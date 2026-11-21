# Monitoring & Observability

Cassandra exposes its internal state in four ways:

1. **Virtual tables** (`system_views`): cluster state queryable with CQL, with no JMX needed.
2. **Dropwizard metrics over JMX** (`org.apache.cassandra.metrics:*`): the source for Prometheus, Datadog and similar tools.
3. **Logs**: `system.log`, `debug.log`, and the slow query log.
4. **Query capture**: full query logging (FQL) and audit logging.

The alert thresholds and remediation steps are in [Housekeeping & Automations](02_housekeeping_and_automations.md). This page explains where each signal comes from.

---

## 1. Virtual Tables (`system_views`)

Virtual tables are **node-local**: a query returns data from the node you are connected to. In `cqlsh`, use `CONNECT`/`--host` to target a specific node, or have the driver pin the query to one host. Unlike regular tables, you don't have to add `ALLOW FILTERING` to a query on a virtual table (`system_views.system_logs` is the exception).

These tables are registered in `SystemViewsKeyspace.java` in the Cassandra source:

| Table | What it shows |
| :--- | :--- |
| `clients` | Connected clients: address, user, driver name and version, protocol version, SSL. |
| `settings` | The node's effective configuration (`cassandra.yaml` values after defaults are applied). |
| `system_properties` | JVM system properties relevant to Cassandra. |
| `thread_pools` | Active, pending, blocked and completed tasks per stage (the same data as `nodetool tpstats`). |
| `caches` | Key, row, counter and chunk cache sizes and hit ratios. |
| `sstable_tasks` | Compactions, cleanups and other SSTable operations in progress. |
| `pending_hints` | Hints waiting to be delivered, per target node. |
| `internode_inbound` / `internode_outbound` | Messaging connection stats per peer. |
| `streaming` | Active and recent streaming sessions (bootstrap, rebuild, repair). |
| `repairs`, `repair_sessions`, `repair_jobs`, `repair_participates`, `repair_validations` | Repair progress on this node. |
| `snapshots` | All snapshots on the node, with sizes and expiry. |
| `gossip_info` | Gossip state per endpoint (the same data as `nodetool gossipinfo`). |
| `queries` | Queries running right now. |
| `cql_metrics`, `batch_metrics` | Prepared-statement and batch statistics. |
| `coordinator_read_latency`, `coordinator_write_latency`, `coordinator_scan_latency`, `local_read_latency`, `local_write_latency`, `local_scan_latency` | Latency per table. |
| `tombstones_per_read`, `rows_per_read`, `max_partition_size`, `disk_usage`, `max_sstable_size`, `max_sstable_duration` | Per-table health. |
| `sai_column_indexes`, `sai_sstable_indexes`, `sai_sstable_index_segments` | SAI index build status and on-disk segments. |
| `credentials_cache_keys`, `roles_cache_keys`, `permissions_cache_keys`, `network_permissions_cache_keys`, `jmx_permissions_cache_keys` | Contents of the auth caches. |
| `cidr_filtering_metrics_counts`, `cidr_filtering_metrics_latencies` | CIDR authorizer activity. |
| `system_logs` | Log messages, **if** the `CQLLOG` appender is uncommented in `conf/logback.xml`. Off by default. |

Some useful queries:

```sql
-- Which apps are connected, with which driver, and over TLS?
SELECT address, username, driver_name, driver_version, protocol_version, ssl_enabled
FROM system_views.clients;

-- Thread pool saturation
SELECT name, active_tasks, pending_tasks, blocked_tasks FROM system_views.thread_pools;

-- Largest partitions and worst tombstone ratios
SELECT * FROM system_views.max_partition_size;
SELECT * FROM system_views.tombstones_per_read;

-- Forgotten snapshots
SELECT * FROM system_views.snapshots;
```

The `system_virtual_schema` keyspace describes the virtual tables themselves.

---

## 2. JMX Metrics

Every metric is a Dropwizard metric registered under the JMX domain `org.apache.cassandra.metrics`, with object names of the form `type=<Type>,[keyspace=..,scope=..,]name=<Name>`. Cassandra does **not** ship a Prometheus endpoint. To scrape these metrics you need an **external** agent:

* the Prometheus [JMX exporter](https://github.com/prometheus/jmx_exporter) as a `-javaagent` (add it through `JVM_EXTRA_OPTS` or `jvm-server.options`, and choose its HTTP port yourself), or
* your vendor's agent (Datadog, New Relic, and others), or
* a Dropwizard reporter. The old `metrics-reporter-config` integration was **removed** in 5.0.

### The metrics that matter most

| Area | Object name | Watch for |
| :--- | :--- | :--- |
| Client latency | `type=ClientRequest,scope=Read\|Write\|RangeSlice\|CASWrite\|CASRead,name=Latency` | p99 trends. |
| Client errors | `type=ClientRequest,scope=Read\|Write,name=Timeouts\|Unavailables\|Failures` | Any sustained rate. |
| Dropped messages | `type=DroppedMessage,scope=<VERB>,name=Dropped` | Any dropped `MUTATION_REQ` or `READ_REQ`. |
| Thread pools | `type=ThreadPools,path=request,scope=<Stage>,name=PendingTasks\|CurrentlyBlockedTasks` | Pending tasks that never drain. |
| Compaction | `type=Compaction,name=PendingTasks` | A backlog that keeps growing. |
| Per table | `type=Table,keyspace=..,scope=..,name=SSTablesPerReadHistogram\|TombstoneScannedHistogram\|LiveSSTableCount\|MaxPartitionSize\|PendingCompactions\|LiveDiskSpaceUsed\|SnapshotsSize` | Read amplification, tombstones, partition growth, snapshot bloat. |
| Repair state | `type=Table,...,name=PercentRepaired\|BytesUnrepaired` | When incremental repair is used. |
| Storage | `type=Storage,name=Load\|Exceptions\|TotalHints` | Disk growth and unhandled exceptions. |
| Hints | `type=HintsService,name=HintsSucceeded\|HintsFailed\|HintsTimedOut` | Hint delivery failing. |
| Guardrail-style signals | `type=Table,...,name=TombstoneWarnings\|TombstoneFailures\|ClientTombstoneAborts\|CoordinatorReadSizeAborts` | Queries close to their limits. |
| CQL | `type=CQL,name=PreparedStatementsEvicted\|RegularStatementsExecuted` | Evictions mean statements are being prepared per request. |

For a quick look without a metrics stack, use `nodetool tpstats`, `tablestats`, `tablehistograms`, `proxyhistograms` and `compactionstats`. `tools/bin/jmxtool` can dump all MBeans.

JVM-level signals (heap, GC pause times, direct memory) come from the standard `java.lang` MBeans and from the GC log that `cassandra-env.sh` writes to `${CASSANDRA_LOG_DIR}/gc.log`.

---

## 3. Logs

| File | Contents |
| :--- | :--- |
| `system.log` | INFO and above: startup, schema changes, compaction summaries, warnings. **Alert on `ERROR` and `WARN`.** |
| `debug.log` | DEBUG output, including the slow query details below. |
| `gc.log` | GC pauses. |

Logs go to `$CASSANDRA_LOG_DIR`, which defaults to `$CASSANDRA_HOME/logs` for tarball installs. Packages set it to `/var/log/cassandra`. The rotation settings in the shipped `conf/logback.xml` are 50 MB files, `maxHistory` 7, and `totalSizeCap` 5 GB per file family.

### Slow query log
Any operation that runs longer than `slow_query_log_timeout` (default **500ms**) is recorded. `system.log` gets a rate-limited INFO line, *"Some operations were slow, details available at debug level (debug.log)"*, and `debug.log` gets the full text of the slow operations. Lower the threshold temporarily if you are hunting a latency problem.

---

## 4. Full Query Logging (FQL)

FQL records **every** CQL query, with its bound values and timestamps, to a binary log. Use it to capture production traffic for replay or comparison testing, for example before an upgrade.

```bash
nodetool enablefullquerylog --path /var/lib/cassandra/fql --roll-cycle HOURLY --max-log-size 17179869184
nodetool getfullquerylog
nodetool disablefullquerylog
```

> [!WARNING]
> The `--path` directory is **wiped recursively** when FQL is enabled. Give FQL its own dedicated directory.

Defaults can also be set in `full_query_logging_options` in `cassandra.yaml`. Use the `fqltool` command (`tools/bin/fqltool`) to read the logs:
* `fqltool dump <dir>`: print the logged queries.
* `fqltool replay`: replay them against another cluster.
* `fqltool compare`: compare the results of two replays.

FQL adds overhead and can capture sensitive bound values. Enable it for a limited time.

---

## 5. Audit Logging

Audit logging is covered in [Security Hardening](../05_cluster_deployment_and_config/03_security_hardening.md#8-audit-logging). It records *who* did *what* (the `AUTH`, `DDL`, `DCL`, `DML`, `QUERY` and other categories), while FQL captures queries for replay. Read binary audit logs with `tools/bin/auditlogviewer`.

---

## 6. Minimum Monitoring Baseline

- [ ] Scrape JMX metrics from every node with an external exporter.
- [ ] Alert on: node down (gossip), dropped mutations and reads, client timeouts and unavailables, pending compactions, disk usage, GC pauses, `ERROR` lines in `system.log`, and schema disagreement (`nodetool describecluster`).
- [ ] Dashboard p50/p99 client latency per operation type, and per table for your hot tables.
- [ ] Check `system_views.snapshots` and `SnapshotsSize` for forgotten snapshots.
- [ ] Track repair completion, using `system_views.repairs` or your repair tool, so you know every range is repaired within `gc_grace_seconds`.
