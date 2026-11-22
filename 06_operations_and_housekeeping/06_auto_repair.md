# Built-in Auto Repair (CEP-37)

> [!CAUTION]
> Commands on this page can change or delete data and affect running clusters. Try them on a test or staging cluster first, and read the [disclaimer](../README.md#disclaimer). The guide is provided "as is", without warranty.

Cassandra 5.0.8 and later includes a repair scheduler that runs inside every node. It decides which nodes repair next, splits each node's token ranges into bounded assignments, retries failures, and records its progress in replicated tables. It replaces external schedulers such as Reaper or cron scripts. This branch (5.0.10) includes it.

This page goes further than the [official auto repair page](https://cassandra.apache.org/doc/5.0/cassandra/managing/operating/auto_repair.html). It adds a rollout runbook and alerting, notes where the official page and the shipped yaml comments differ from the code, and verifies every default against `AutoRepairConfig.java` and `RepairTokenRangeSplitter.java`.

> [!IMPORTANT]
> Repair exists to keep deleted data from coming back. Every token range must be repaired more often than the smallest `gc_grace_seconds` in the cluster (default 10 days). See [Housekeeping](02_housekeeping_and_automations.md#2-scheduled-repairs-preventing-resurrected-data).

---

## 1. How It Works

* A scheduler thread on each node wakes every `repair_check_interval` (5m). It checks whether it is this node's turn, whether its replicas are busy, and whether `min_repair_interval` has passed since this node last repaired.
* Turn order and history are stored in `system_distributed.auto_repair_history`. Operator overrides (priority and forced hosts) are stored in `system_distributed.auto_repair_priority`.
* Each of the three **repair types** has its own schedule and settings:

| Repair type | What it repairs | Typical cadence |
| :--- | :--- | :--- |
| `full` | All data in the range (classic `nodetool repair -full -pr`) | Days, well inside `gc_grace_seconds` |
| `incremental` | Only unrepaired SSTables; anticompacts them into repaired and unrepaired sets | Hourly once enabled |
| `preview_repaired` | Compares the **repaired** set across replicas without streaming anything (detects incremental-repair bugs) | Daily, optional |

* A token range splitter breaks each node's primary ranges into **assignments** that are bounded by bytes, partitions and table count. Assignments that fail are retried (`repair_max_retries`, `repair_retry_backoff`).

---

## 2. Enabling It: Two Switches

### Switch 1: the JVM property (permanent)
Add the property to `conf/jvm-server.options` on **every** node:
```bash
-Dcassandra.autorepair.enable=true
```
This adds an `auto_repair` column to `system_schema.tables` and `system_schema.views`, and creates the `auto_repair_history` and `auto_repair_priority` tables. From NEWS.txt (5.0.8):

> [!WARNING]
> * **Non-reversible.** If a node that once started with the property later starts with `cassandra.autorepair.enable=false`, it fails during initialization because of the schema mismatch. To stop auto repair afterwards, use the yaml or JMX, **not** the JVM property.
> * **All nodes or none.** If only some nodes have it, `system_distributed` is at schema generation 7 on some nodes and 6 on others. Schema then disagrees and **any DDL times out** until every node matches.
> * Leave it off while a rolling upgrade from a version older than 5.0.8 is in progress.

Without the property, the auto-repair MBean doesn't exist, and nodetool reports this inconsistently:
* `nodetool setautorepairconfig ...` prints `Auto-repair is not supported or not enabled via -Dcassandra.autorepair.enable=true on the server.` and exits 0.
* `nodetool getautorepairconfig` and `nodetool autorepairstatus` fail with the **misleading** `Server is not initialized yet, cannot run nodetool.`, even on a healthy node.

If you see that message on a node that is otherwise up, check for the JVM property before you suspect the node. Verified on 5.0.9 by `test_env` scenario 11.

### Switch 2: scheduling (reversible)
Scheduling is turned on in `cassandra.yaml` (the top-level `enabled` and each type's `enabled`). It can also be started at runtime with `nodetool setautorepairconfig start_scheduler true`. Turning it off later through the yaml or JMX is safe.

> [!IMPORTANT]
> Until switch 2 is on, `getautorepairconfig`, `autorepairstatus` and every `setautorepairconfig` parameter **except `start_scheduler`** print `Auto-repair is not enabled` and **exit with status 0, without applying anything**. Scripts must check the output, not just the exit code. Run `start_scheduler true` (or enable it in the yaml) first. `getautorepairconfig` prints a repair type's settings (`min_repair_interval`, splitter and so on) only once that type is enabled: `nodetool setautorepairconfig -t full enabled true`. Verified on 5.0.9 by `test_env` scenario 11.

---

## 3. Configuration Reference (5.0.10 code defaults)

```yaml
auto_repair:
  enabled: true                       # scheduler thread on/off (default false)
  repair_check_interval: 5m
  history_clear_delete_hosts_buffer_interval: 2h
  repair_task_min_duration: 5s
  mixed_major_version_repair_enabled: false
  global_settings:                    # defaults for all repair types
    repair_by_keyspace: true
  repair_type_overrides:              # per type: full, incremental, preview_repaired
    full:
      enabled: true
      min_repair_interval: 5d
    incremental:
      enabled: false
```

### Top-level settings
| Setting | Default | Meaning |
| :--- | :--- | :--- |
| `enabled` | `false` | Starts the scheduler thread. It also needs the JVM property; the scheduler runs only when both are on. |
| `repair_check_interval` | `5m` | How often the scheduler checks for work. |
| `history_clear_delete_hosts_buffer_interval` | `2h` | How long a departed host is kept in history before the turn order is recomputed. |
| `repair_task_min_duration` | `5s` | Minimum time per repair task, so the scheduler doesn't flood the node with tiny tasks. |
| `mixed_major_version_repair_enabled` | `false` | Whether to repair while major versions are mixed, as during an upgrade. Leave it `false`. |

### Per-repair-type settings
Set these under `global_settings` or `repair_type_overrides.<type>`. Code defaults (`AutoRepairConfig.Options.getDefaultOptions`):

| Setting | Default | Meaning |
| :--- | :--- | :--- |
| `enabled` | `false` | Whether this repair type runs. |
| `min_repair_interval` | `24h` | Minimum time between two repairs of the same node. |
| `repair_by_keyspace` | `true` | Groups the tables of a keyspace into one repair. |
| `number_of_repair_threads` | `1` | Like `nodetool repair -j`. |
| `parallel_repair_count` | `3` | Number of nodes that repair at once. The larger of this and the percentage applies. |
| `parallel_repair_percentage` | `3` | Percentage of the cluster that repairs at once. |
| `allow_parallel_replica_repair` | `false` | Whether a node may repair while one of its replicas is repairing. Keep it `false`, especially with incremental repair, to avoid anticompaction conflicts. |
| `allow_parallel_replica_repair_across_schedules` | `true` | Only checked when the previous setting is `false`. If `false`, a node also waits for replicas busy with *another* repair type. |
| `repair_primary_token_range_only` | `true` | Like `-pr`. Keep it `true`. |
| `sstable_upper_threshold` | `50000` | Tables with more SSTables than this are skipped. |
| `table_max_repair_time` | `6h` | After this, the node moves on to the next table. |
| `ignore_dcs` | `[]` | DCs whose nodes do not take turns. Their replicas still take part in other nodes' sessions. |
| `materialized_view_repair_enabled` | `false` | Whether to repair materialized views. |
| `initial_scheduler_delay` | `5m` | Wait after startup before the first repair. |
| `repair_session_timeout` | `3h` | When a stuck session is considered failed. |
| `force_repair_new_node` | `false` | Whether a node that just joined repairs immediately. |
| `repair_max_retries` | `3` | Retries per assignment. In 5.0.10 the global value is honored (fix CASSANDRA-21748). |
| `repair_retry_backoff` | `30s` | Delay between retries. |
| `token_range_splitter` | `RepairTokenRangeSplitter` | See below. |

> [!NOTE]
> **Discrepancies in the shipped text (5.0.10):**
> * The in-repo `auto_repair.adoc` lists `repair_max_retries` as a top-level setting. In the code it is a per-type option.
> * The `.adoc` page says repairs are rejected when less than 20% of the disk is free. In 5.0, `repair_disk_headroom_reject_ratio` defaults to **0.0 (disabled)**; see section 6.
> * The yaml comment calls the fixed splitter `FixedTokenRangeSplitter`. The class is actually `org.apache.cassandra.repair.autorepair.FixedSplitTokenRangeSplitter`.

### Token range splitters
**`RepairTokenRangeSplitter`** (default) estimates bytes and partitions from SSTable metadata and caps each assignment:

| Parameter | `full` / `preview_repaired` | `incremental` |
| :--- | :--- | :--- |
| `bytes_per_assignment` | `50GiB` (only the part of each SSTable inside the range) | `50GiB` (the **whole** size of each unrepaired SSTable, because all of it gets anticompacted) |
| `partitions_per_assignment` | `1048576` (2^20, roughly one partition per Merkle leaf) | `1048576` |
| `max_tables_per_assignment` | `64` | `64` |
| `max_bytes_per_schedule` | `100000GiB` (effectively unlimited) | `100GiB` (caps anticompaction per round) |

**`FixedSplitTokenRangeSplitter`** has one parameter, `number_of_subranges` (default `32`). It splits each node's ranges evenly. With `num_tokens: 16`, that gives 2 subranges per vnode range.

```yaml
    full:
      token_range_splitter:
        class_name: org.apache.cassandra.repair.autorepair.FixedSplitTokenRangeSplitter
        parameters:
          number_of_subranges: 64
```

---

## 4. Table-Level Control

The `auto_repair` table property is only available once the JVM property is set:
```sql
-- Skip incremental repair for a table, but keep full repair
ALTER TABLE ks.events WITH auto_repair = {'incremental_enabled': 'false'};

-- Repair this table before others (higher number = sooner)
ALTER TABLE ks.accounts WITH auto_repair = {'priority': '3'};
```
| Option | Default |
| :--- | :--- |
| `full_enabled` | `true` |
| `incremental_enabled` | `true` |
| `preview_repaired_enabled` | `true` |
| `priority` | `0` |

Unknown keys are rejected (`Unknown property '...'`), and so are non-boolean or non-integer values. A table-level `true` has no effect when that repair type is disabled in `cassandra.yaml`.

---

## 5. Operating It with nodetool

```bash
# Effective configuration on this node, per repair type
nodetool getautorepairconfig

# What is running now (-t / --repair-type: full | incremental | preview_repaired)
nodetool autorepairstatus -t full

# Runtime changes. Most apply to this node only and are LOST ON RESTART.
nodetool setautorepairconfig -t full min_repair_interval 5d
nodetool setautorepairconfig -t incremental enabled false
nodetool setautorepairconfig -t incremental token_range_splitter.bytes_per_assignment 10GiB

# These need no -t
nodetool setautorepairconfig start_scheduler true
nodetool setautorepairconfig min_repair_task_duration 10s
nodetool setautorepairconfig history_clear_delete_hosts_buffer_interval 4h

# Cluster-level overrides, stored in system_distributed.auto_repair_priority
nodetool setautorepairconfig -t full priority_hosts 10.0.1.12,10.0.1.15
nodetool setautorepairconfig -t full forcerepair_hosts 10.0.1.18
```
Note that the nodetool key `min_repair_task_duration` corresponds to the yaml key `repair_task_min_duration`. To make a runtime change permanent, also put it in `cassandra.yaml`.

---

## 6. Guard Rails That Protect the Node

These top-level `cassandra.yaml` settings apply to **every** repair, manual or automatic. They are checked on each participant when a repair is prepared (`ActiveRepairService`):

| Setting | 5.0 default | Effect |
| :--- | :--- | :--- |
| `repair_disk_headroom_reject_ratio` | `0.0` (disabled) | When set to, for example, `0.2`, a repair is rejected if data-disk usage is above 80%. Log line: `Rejecting incoming repair, disk usage (…%) above threshold (…%)`. |
| `reject_repair_compaction_threshold` | disabled (`Integer.MAX_VALUE`) | Rejects repair when pending compactions exceed this value. Log line: `Rejecting incoming repair, pending compactions (…) above threshold (…)`. |

Disk usage here is measured against the data directories, capped by the `data_disk_usage_max_disk_size` guardrail if that is set. **Set both settings before you turn on auto repair**, for example `0.2` and `1024`.

---

## 7. Enabling Incremental Repair on an Existing Cluster

The first incremental repair must anticompact every SSTable it touches, splitting repaired from unrepaired data. On large STCS SSTables, or tables with many overlapping SSTables, that is a lot of I/O. Use this order:

1. Run at least one **full** auto-repair cycle across the whole cluster. This reduces how much data the first incremental pass has to stream.
2. Choose how to treat existing data:
   * **Strict consistency:** keep everything unrepaired and let the default incremental throttle work through it (`max_bytes_per_schedule: 100GiB` per node per `min_repair_interval`).
   * **Relaxed consistency:** stop the node, mark its existing SSTables as repaired with the offline tool `tools/bin/sstablerepairedset --really-set --is-repaired`, and start it again. Do this one node at a time. Incremental repair then only covers new writes. The official page mistakenly calls this tool `nodetool sstablerepairedset`.
3. Enable incremental repair with a long interval first (`min_repair_interval: 24h`), and watch anticompaction (`nodetool compactionstats`) and disk usage.
4. Shorten the interval to `1h` once a full round finishes comfortably.
5. Keep full repair enabled at a low cadence (for example `5d`–`7d`).
6. Optionally enable `preview_repaired` daily. Desynchronised repaired data appears in the table metrics `BytesPreviewedDesynchronized` and `TokenRangesPreviewedDesynchronized`. It should always be zero. It is also a precondition before you consider `only_purge_repaired_tombstones`.

> [!CAUTION]
> Once incremental repair has run on a table, keep running it. Repaired and unrepaired SSTables are never compacted together, so stopping incremental repair leaves data stuck in the unrepaired set and can stop tombstones from being purged.

---

## 8. Rollout Runbook

1. **Choose one repair tool.** Disable Reaper schedules and cron repair jobs first. Two schedulers running anticompaction or validation on the same replicas just compete for the same resources.
2. **Set the guard rails** from section 6 and do a rolling restart to apply them.
3. **Add the JVM property on all nodes** with scheduling still off (no `auto_repair.enabled`), then do a rolling restart. Confirm `nodetool describecluster` shows **one** schema version before you run any DDL.
4. **Enable full repair only**, with `min_repair_interval` set to a value that finishes a cluster-wide round inside `gc_grace_seconds` with room to spare. Keep `parallel_repair_count` at its default or lower. Rolling restart, or `nodetool setautorepairconfig start_scheduler true` plus per-type `enabled true` on each node.
5. **Watch the first full round** using the metrics below. Tune `bytes_per_assignment` downwards if individual sessions run for hours.
6. **(Optional)** Turn on incremental repair following section 7.
7. Put the final settings in `cassandra.yaml` everywhere, so a restart doesn't undo runtime changes.

---

## 9. Monitoring & Alerts

MBean: `org.apache.cassandra.metrics:type=AutoRepair,name=<Metric>,repairType=<full|incremental|preview_repaired>`

| Metric | Meaning | Suggested alert |
| :--- | :--- | :--- |
| `LongestUnrepairedSec` | Age of the least recently repaired data on this node | **Warn above 50% of the minimum `gc_grace_seconds`, critical above 80%.** This is the one alert that prevents deleted data from coming back. |
| `ClusterRepairTimeInSec` / `NodeRepairTimeInSec` | Duration of the last cluster-wide round and of this node's last turn | Warn if a round approaches `gc_grace_seconds`. |
| `RepairsInProgress` | Repairs running on this node | Stuck at 1 for longer than `repair_session_timeout` |
| `FailedTokenRangesCount` / `SucceededTokenRangesCount` / `SkippedTokenRangesCount` | Results of the last turn | Any `Failed` greater than 0 over several rounds |
| `SkippedTablesCount` | Tables skipped, for example by `sstable_upper_threshold` or `table_max_repair_time` | Greater than 0 means some tables are not being repaired |
| `RepairStartLagSec` | How long a due repair waited to start | Rising steadily: the cluster is not keeping up |
| `RepairDelayedByReplica` / `RepairDelayedBySchedule` | Turns postponed because replicas were busy or another schedule was running | Sustained growth means too little parallelism, or repairs are too slow |
| `TotalBytesToRepair` / `BytesAlreadyRepaired` | Progress through the current schedule | Useful on dashboards |
| `TotalDisabledRepairTables` | Tables with that repair type disabled | Check after schema changes |

Also check `nodetool autorepairstatus`, `system_views.repairs`, and `system.log` for `Rejecting incoming repair` lines (section 6).

---

## Sources

* Code (cassandra-5.0 branch):
  * [`AutoRepairConfig.java`](https://github.com/apache/cassandra/blob/cassandra-5.0/src/java/org/apache/cassandra/repair/autorepair/AutoRepairConfig.java)
  * [`RepairTokenRangeSplitter.java`](https://github.com/apache/cassandra/blob/cassandra-5.0/src/java/org/apache/cassandra/repair/autorepair/RepairTokenRangeSplitter.java)
  * [`FixedSplitTokenRangeSplitter.java`](https://github.com/apache/cassandra/blob/cassandra-5.0/src/java/org/apache/cassandra/repair/autorepair/FixedSplitTokenRangeSplitter.java)
  * [`AutoRepairParams.java`](https://github.com/apache/cassandra/blob/cassandra-5.0/src/java/org/apache/cassandra/schema/AutoRepairParams.java)
  * [`AutoRepairMetrics.java`](https://github.com/apache/cassandra/blob/cassandra-5.0/src/java/org/apache/cassandra/metrics/AutoRepairMetrics.java)
  * [`AutoRepairService.java`](https://github.com/apache/cassandra/blob/cassandra-5.0/src/java/org/apache/cassandra/service/AutoRepairService.java)
  * [`SetAutoRepairConfig.java`](https://github.com/apache/cassandra/blob/cassandra-5.0/src/java/org/apache/cassandra/tools/nodetool/SetAutoRepairConfig.java)
  * [`ActiveRepairService.java`](https://github.com/apache/cassandra/blob/cassandra-5.0/src/java/org/apache/cassandra/service/ActiveRepairService.java)
  * [`Config.java`](https://github.com/apache/cassandra/blob/cassandra-5.0/src/java/org/apache/cassandra/config/Config.java)
* Config and release notes:
  * [`conf/cassandra.yaml`](https://github.com/apache/cassandra/blob/cassandra-5.0/conf/cassandra.yaml)
  * [`NEWS.txt`](https://github.com/apache/cassandra/blob/cassandra-5.0/NEWS.txt) (5.0.8 section)
  * [`CHANGES.txt`](https://github.com/apache/cassandra/blob/cassandra-5.0/CHANGES.txt) (CASSANDRA-21748, CASSANDRA-20045, CASSANDRA-20046)
* In-repo doc: [`doc/modules/cassandra/pages/managing/operating/auto_repair.adoc`](https://github.com/apache/cassandra/blob/cassandra-5.0/doc/modules/cassandra/pages/managing/operating/auto_repair.adoc)
* Official docs: https://cassandra.apache.org/doc/5.0/cassandra/managing/operating/auto_repair.html
* Design: [CEP-37](https://cwiki.apache.org/confluence/display/CASSANDRA/CEP-37+Apache+Cassandra+Unified+Repair+Solution)
