# Upgrading to Cassandra 5.0

This page covers rolling upgrades from **4.0.x / 4.1.x** to 5.0.x, and how to turn on 5.0-only features (BTI, UCS, SAI, trie memtables, Paxos v2) on an existing cluster. The authoritative source is [`NEWS.txt`](https://github.com/apache/cassandra/blob/cassandra-5.0/NEWS.txt) in the Apache Cassandra source. Read its "Upgrading" sections for 5.0 and for **every 5.0.x release up to your target**.

---

## 1. Supported Upgrade Paths

| From | To 5.0? | Why |
| :--- | :--- | :--- |
| 4.0.x, 4.1.x | **Yes**, as a rolling upgrade | 5.0 still talks to 4.0 nodes (`MessagingService.minimum_version = VERSION_40`). |
| 3.0.x, 3.11.x | **No**, not directly | 5.0 cannot exchange messages with 3.x nodes. Upgrade to 4.0 or 4.1 first and run `upgradesstables`, then upgrade to 5.0. |

5.0 reads SSTables back to version `ma` (3.0), but you should still upgrade SSTables at every hop.

---

## 2. Pre-Upgrade Checklist

Work through these items **on the old version**, before touching any binaries:

- [ ] **Java**: 5.0 needs Java 11 or 17. Java 8 is no longer supported. Java 17 is fully supported from **5.0.5**; earlier 5.0.x releases treat it as experimental.
- [ ] **Python for cqlsh**: 3.8 or later (`bin/cqlsh` accepts 3.8–3.13).
- [ ] **No `DateTieredCompactionStrategy`**: DTCS was removed. Switch those tables to `TimeWindowCompactionStrategy` **before** upgrading.
- [ ] **No removed CQL functions**: `dateOf` and `unixTimestampOf` were removed. Use `toTimestamp` and `toUnixTimestamp`.
- [ ] **No removed table compression options**: `sstable_compression` and `chunk_length_kb` were removed. Use `class` and `chunk_length_in_kb`.
- [ ] **Keystore and truststore passwords set explicitly**: 5.0 removed the code default of `cassandra`. A node that relied on that default fails at startup.
- [ ] **`commitlog_sync_batch_window_in_ms` removed** from the yaml.
- [ ] **Hadoop integration is gone**: use the Spark Cassandra Connector instead.
- [ ] **UDTs on clusters upgraded from 3.x**: the UDT migration logic was removed. See CASSANDRA-18504.
- [ ] **Drivers on protocol v4 or later**, if you are upgrading from 4.1.0 or 4.0.0–4.0.7 (paging bug with protocol v3, CASSANDRA-17507).
- [ ] **Cluster is healthy**: all nodes `UN`, a single schema version (`nodetool describecluster`), no streaming, and a recent repair has completed.
- [ ] **Snapshot every node** (`nodetool snapshot -t pre_5_0_upgrade`). Snapshots are cheap and are your rollback path for data files.
- [ ] **Merge your config into the new yaml**: start from the 5.0 `conf/cassandra.yaml` and copy your settings in. Do not reuse the old file as-is. Old key names (`*_in_ms`, `*_in_kb`, `*_mb_per_sec`) are still accepted as deprecated aliases, but should be moved to the new names (`read_request_timeout: 5000ms`, `compaction_throughput: 64MiB/s`).
- [ ] **Add the `crypto_provider` section to the yaml.** If you keep an old yaml without it, the bundled Amazon Corretto Crypto Provider is **not** installed.
- [ ] **Avoid schema changes** for the whole duration of the mixed-version window.

---

## 3. Behavior Changes to Expect

* `disk_access_mode` now defaults to `mmap_index_only` instead of `auto`. Set `disk_access_mode: auto` to keep the old behavior.
* `-XX:MaxDirectMemorySize` is now explicitly half of `-Xmx` (since 5.0.4).
* New table properties (`allow_auto_snapshot`, `incremental_backups`) give upgraded nodes a new schema version. The versions converge once every node has been upgraded.
* Since 5.0.1, `reject_out_of_token_range_requests` and `log_out_of_token_range_requests` are on by default.
* If you use `Ec2Snitch` or `Ec2MultiRegionSnitch`, Cassandra now talks to AWS IMDSv2 by default.
* The `BufferPool` MBean without a scope has been removed. Use `type=BufferPool,scope=chunk-cache`.
* The `metrics-reporter-config` pluggable reporter has been removed.
* Since 5.0.10, the `hostname` column in `system_views.clients` no longer does a reverse DNS lookup.

---

## 4. The Rolling Upgrade Procedure

Upgrade **one node at a time**:

```bash
# 1. Stop client traffic and flush. drain also stops gossip and the native transport.
nodetool drain

# 2. Stop the process
sudo systemctl stop cassandra      # or your service manager / bin/stop-server

# 3. Install the 5.0.x binaries and the merged config.
#    Keep storage_compatibility_mode: CASSANDRA_4 (the default) for now.

# 4. Start, then wait for UN and for the node to show up in nodetool describecluster
sudo systemctl start cassandra
nodetool status
```

Check `system.log` for errors before you move on to the next node. Once **every** node runs 5.0, rewrite the old-format SSTables. Throttle with `nodetool setcompactionthroughput` if needed:

```bash
nodetool upgradesstables        # rewrites only SSTables that are not on the current version
```

Do not run repairs, bootstraps or decommissions while the cluster is on mixed versions.

---

## 5. `storage_compatibility_mode`: The Three-Step Finish

This setting controls which on-disk and messaging formats the node writes, and therefore **whether you can still roll back**:

| Mode | What it means (from `StorageCompatibilityMode.java` and the yaml comments) |
| :--- | :--- |
| `CASSANDRA_4` (the default in `cassandra.yaml`) | Stays compatible with 4.x. SSTables are written as BIG version `nb`. TTL expiration is capped at **2038-01-19**. **BTI cannot be selected**: the node refuses to start with "Selected sstable format 'bti' is not available when in storage compatibility mode 'CASSANDRA_4'". Rolling back to 4.x is still possible. |
| `UPGRADING` | Writes the 5.0 formats (BIG `oa`), but keeps the features that need all nodes on 5.0 turned off until every node runs in this mode. Checking node versions has a small runtime cost. |
| `NONE` (the default in `cassandra_latest.yaml`) | Assumes every node is on 5.0. All new formats and features are enabled, including TTLs up to **2106-02-07**. |

The procedure:

1. Do the rolling upgrade to 5.0 with `storage_compatibility_mode: CASSANDRA_4`, and let it run stably.
2. Do a rolling restart with `storage_compatibility_mode: UPGRADING`. The new features turn on once every node is in this mode.
3. Do a rolling restart with `storage_compatibility_mode: NONE`. Mixed 2038/2106 nodes are no longer possible.

> [!CAUTION]
> **Step 2 is the point of no return.** Once a node writes 5.0-format SSTables, commit logs and hints, 4.x can no longer read them, so a binary rollback is no longer possible. Roll back after that point only by restoring the pre-upgrade snapshots, which loses any writes made since.
>
> The property has to be set consistently for **every executable and tool**, including the offline `sstable*` tools that read `cassandra.yaml`.

---

## 6. Adopting 5.0 Features on Existing Data

| Feature | How to enable | Safe when | Existing data |
| :--- | :--- | :--- | :--- |
| **BTI SSTables** | `sstable:` / `selected_format: bti` in the yaml, then a rolling restart | `storage_compatibility_mode` is `UPGRADING` or `NONE`; `NONE` is recommended | Only new SSTables are written as BTI. Run `nodetool upgradesstables -a` to rewrite old ones. BIG and BTI SSTables can coexist. |
| **Trie memtable** | Per table: `ALTER TABLE ks.t WITH memtable = 'trie';` (the `trie` configuration is defined in the shipped `memtable.configurations`), or change `default: inherits: trie` in the yaml | After every node is on 5.0 (it is a schema change) | Takes effect at the next memtable flush. |
| **UCS** | `ALTER TABLE ks.t WITH compaction = {'class': 'UnifiedCompactionStrategy', 'scaling_parameters': 'T4'};` | After every node is on 5.0 | Existing SSTables are reorganized gradually by normal compaction. See [Compaction Strategies](../06_operations_and_housekeeping/04_compaction_strategies.md). |
| **SAI** | `CREATE INDEX ... USING 'sai'` | After every node is on 5.0 | The index is built from existing SSTables in the background. |
| **Paxos v2** | Section 7 | 4.1 or later on every node | No data migration. |
| **Auto-repair (5.0.8+)** | `-Dcassandra.autorepair.enable=true` on **every** node, then the `auto_repair:` yaml section | Every node is on 5.0.8 or later | See the warning below. |

### Migrating legacy 2i indexes to SAI
Since 5.0.4, if a column has **both** a legacy index and an SAI index, the legacy index is preferred (`sai_options.prioritize_over_legacy_index: false`). That makes the migration safe:

1. `CREATE INDEX new_idx ON ks.t (col) USING 'sai';` and wait for the build to finish.
2. Set `sai_options.prioritize_over_legacy_index: true` (or use the JMX setter `setPrioritizeSAIOverLegacyIndex`) and test your queries.
3. `DROP INDEX old_legacy_idx;`

> [!WARNING]
> **`cassandra.autorepair.enable=true` is not reversible.** It adds auto-repair columns to the schema. A node later started with the property set to `false` fails to initialize.
>
> If the property differs between nodes, the `system_distributed` schema differs between them and schema changes time out. Set it identically everywhere, before any schema change. Turn the scheduler on and off with yaml or JMX, never by flipping the JVM property.

---

## 7. Enabling Paxos v2 (LWT)

Paxos v2 was added in **4.1** and is opt-in. The default is `paxos_variant: v1`; `cassandra_latest.yaml` sets `v2`. From the shipped `cassandra.yaml`:

| Variant | Write LWT | Read (SERIAL) |
| :--- | :--- | :--- |
| `v1` (default) | 4 round-trips | 3 round-trips |
| `v2` (recommended) | 2 round-trips | 1–2 round-trips |

Steps:
1. Every node is on 4.1 or later.
2. Run `nodetool repair --full -pr` on every node.
3. Set `paxos_variant: v2` on every node and do a rolling restart. To roll back, set `v1` again and do a rolling restart; no data migration is involved.
4. Optional, for one more round-trip saved: once Paxos repairs run regularly (they run as part of normal repair under v2), set `paxos_state_purging: repaired` on every node. Applications may then send LWT writes with a commit consistency level of `ANY`.
   > [!CAUTION]
   > Once `paxos_state_purging: repaired` is set, never go back to `legacy`. If Paxos repairs have to stop for a long time, use `gc_grace` instead, and set applications back to the default commit consistency.

---

## 8. Rollback Summary

| Point in the upgrade | Rollback option |
| :--- | :--- |
| Some nodes are on 5.0 with `CASSANDRA_4` | Drain, reinstall the 4.x binaries, and restart. The data is still in 4.x format. |
| `UPGRADING` or `NONE` has been set on any node | No binary rollback. Restore the pre-upgrade snapshots on every node; writes made since are lost. |
| BTI, UCS, or trie memtables are in use | Revert them first: set `selected_format: big` and run `upgradesstables -a`; change the compaction class back. Then follow the rows above. |
| UCS `max_sstables_per_shard_factor` is set (5.0.10+) | Remove the option from those tables before downgrading below 5.0.10. Older nodes reject any table that has it. |
| Auto-repair JVM property enabled | Cannot be reverted. |
