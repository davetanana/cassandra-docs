# Tools Reference: cqlsh, SSTable Tools, Bulk Loading, Logs & Stress

This page covers every command-line tool that ships with Cassandra 5.0 except `nodetool`, which has its own [operations guide](../06_operations_and_housekeeping/01_nodetool_operations_guide.md). Options and defaults were taken from the 5.0 source (see [Sources](#sources)). Run any tool with `-h` / `--help` to see the full list for your build.

| Location | Tools |
| :--- | :--- |
| `bin/` (all installs) | `cqlsh`, `nodetool`, `sstableloader`, `sstablescrub`, `sstableupgrade`, `sstableutil`, `sstableverify` |
| `tools/bin/` (tarball; deb/rpm put them in the `cassandra-tools` package) | `sstabledump`, `sstablemetadata`, `sstablepartitions`, `sstableexpiredblockers`, `sstablelevelreset`, `sstableofflinerelevel`, `sstablerepairedset`, `sstablesplit`, `fqltool`, `auditlogviewer`, `cassandra-stress`, `compaction-stress`, `generatetokens`, `hash_password`, `jmxtool` |

> [!CAUTION]
> **Offline tools must run with the node stopped.** Running a tool that rewrites or re-labels SSTables against a live node's data directory can corrupt data or produce "very strange behavior" (the tools' own wording). This covers `sstablescrub`, `sstableupgrade`, `sstableverify`, `sstablesplit`, `sstablelevelreset`, `sstableofflinerelevel`, `sstablerepairedset` and `sstableutil --cleanup`.
> Where an online equivalent exists, use it instead: `nodetool scrub`, `nodetool upgradesstables`, `nodetool verify`, `nodetool garbagecollect`.
> The read-only tools (`sstabledump`, `sstablemetadata`, `sstablepartitions`, `sstableexpiredblockers`) can run against a live node, but compaction may delete the files they are reading. Point them at a snapshot when you can.

---

## 1. `cqlsh`: The CQL Shell

`cqlsh` is a Python program (`bin/cqlsh.py` + `pylib/cqlshlib`) that uses the bundled Python driver. `bin/cqlsh` lists Python 3.8–3.11 as supported and accepts up to 3.13 (3.6–3.7 are deprecated).

### Command-Line Options

| Option | Purpose |
| :--- | :--- |
| `cqlsh [host [port]]` | Connect to a host (default `127.0.0.1` `9042`, or `$CQLSH_HOST` / `$CQLSH_PORT`) |
| `-u`, `--username` / `-p`, `--password` | Authenticate. Passing `-p` on the command line prints a warning; use a credentials file instead (below). |
| `-k`, `--keyspace` | Start in this keyspace |
| `-f`, `--file FILE` | Run the statements in FILE, then exit |
| `-e`, `--execute "STMT"` | Run one statement, then exit |
| `--ssl` | Connect with TLS (configure `[ssl]` in cqlshrc) |
| `--connect-timeout SECS` | Default **5** |
| `--request-timeout SECS` | Default **10**. Raise it for long `SELECT`s or schema changes. |
| `--protocol-version N` | Force a native protocol version |
| `--cqlshrc PATH`, `--credentials PATH` | Alternative config and credentials files |
| `--encoding`, `-C`/`--color`, `--no-color`, `-t`/`--tty`, `--disable-history`, `--debug` | Output and terminal behavior |

### `~/.cassandra/cqlshrc` and `~/.cassandra/credentials`

A fully commented sample ships as `conf/cqlshrc.sample`. The sections you will use most:

```ini
[authentication]
credentials = ~/.cassandra/credentials   ; keeps passwords off the command line
keyspace = my_ks

[connection]
hostname = 10.0.1.10
port = 9042
ssl = true
timeout = 10            ; connect timeout, seconds
request_timeout = 30

[ssl]
certfile = ~/keys/ca.pem      ; CA used to validate the server
validate = true
; userkey / usercert only when client_encryption_options.require_client_auth is true
userkey = ~/keys/client.key
usercert = ~/keys/client.pem

[ui]
time_format = %Y-%m-%d %H:%M:%S%z
timezone = Etc/UTC
float_precision = 5
double_precision = 12

[copy]                         ; defaults for COPY TO and COPY FROM
numprocesses = 4
[copy-from:my_ks.my_table]     ; per-table overrides: [copy:ks.t], [copy-from:ks.t], [copy-to:ks.t]
ingestrate = 20000
```

```ini
; ~/.cassandra/credentials  (chmod 600: cqlsh ignores the file, with a warning, if it is group/world-readable or not owned by you)
[PlainTextAuthProvider]
username = app_admin
password = s3cret
```

### Shell Commands (cqlsh-only, not CQL)

| Command | What it does |
| :--- | :--- |
| `CONSISTENCY [level]` | Show or set the CL for later statements. The cqlsh default is `ONE`. |
| `SERIAL CONSISTENCY [SERIAL\|LOCAL_SERIAL]` | Serial CL for LWTs |
| `TRACING ON\|OFF` | Print the server-side trace for each statement. Traces are written to `system_traces` (`trace_type_query_ttl`, default 1 day). |
| `PAGING [ON\|OFF\|<n>]` | Interactive paging. The default page size is **100** rows; `PAGING 500` sets it. |
| `EXPAND ON\|OFF` | Vertical (one column per line) output, useful for wide rows |
| `CAPTURE 'file'` / `CAPTURE OFF` | Also send query output to a file |
| `SOURCE 'file.cql'` | Run statements from a file |
| `DESCRIBE ...` / `DESC ...` | Show schema. Since 4.0 this runs on the server; see the [CQL reference](04_cql_quick_reference.md#10-describe). |
| `SHOW VERSION` / `SHOW HOST` / `SHOW SESSION <trace-id>` / `SHOW REPLICAS <token> [keyspace]` | Session info, a past trace, or the replicas for a token |
| `LOGIN user ['pass']` | Re-authenticate as another role |
| `COPY ...` | CSV import/export (below) |
| `CLEAR` / `CLS`, `HISTORY`, `HELP [topic]`, `EXIT` / `QUIT` | Housekeeping |

### `COPY TO` / `COPY FROM`: CSV Export and Import

```sql
COPY my_ks.users (user_id, email, created_at) TO '/tmp/users.csv' WITH HEADER = true;
COPY my_ks.users (user_id, email, created_at) FROM '/tmp/users.csv' WITH HEADER = true AND MAXINSERTERRORS = 100;
```

| Option (applies to) | Default (from `copyutil.py`) | Notes |
| :--- | :--- | :--- |
| `DELIMITER`, `QUOTE`, `ESCAPE` (both) | `,` `"` `\` | |
| `HEADER` (both) | `false` | |
| `NULL` (both) | empty string | The string that represents null |
| `DATETIMEFORMAT` (both) | the cqlshrc `time_format` | |
| `NUMPROCESSES` (both) | cores − 1, capped at **16** | Worker processes |
| `MAXATTEMPTS` (both) | 5 | Retries per batch or page |
| `REPORTFREQUENCY`, `RATEFILE`, `CONFIGFILE`, `DECIMALSEP`, `THOUSANDSSEP`, `BOOLSTYLE` (both) | | Progress, rate log, alternative config file, number/boolean formats |
| `INGESTRATE` (FROM) | 100000 rows/s | An approximate cap; lower it to protect a busy cluster |
| `CHUNKSIZE` (FROM) | 5000 | Rows sent to each worker at a time |
| `MINBATCHSIZE` / `MAXBATCHSIZE` (FROM) | 10 / 20 | Rows per **single-partition** unlogged batch |
| `MAXROWS`, `SKIPROWS`, `SKIPCOLS` (FROM) | -1 (all), 0, none | |
| `MAXPARSEERRORS` / `MAXINSERTERRORS` (FROM) | -1 (unlimited) / 1000 | Failed rows are written to `ERRFILE` |
| `PREPAREDSTATEMENTS` (FROM) | true | |
| `TTL` (FROM) | -1 (none) | Applies a TTL to every imported row |
| `PAGESIZE` / `PAGETIMEOUT` (TO) | 1000 / 10 s (scaled up with page size) | |
| `MAXREQUESTS` (TO) | 6 | Concurrent page requests per worker |
| `BEGINTOKEN` / `ENDTOKEN` (TO) | full ring | Export a slice of the ring |
| `MAXOUTPUTSIZE` (TO) | -1 | Split the output into files of N rows |
| `ENCODING`, `FLOATPRECISION`, `DOUBLEPRECISION` (TO) | `utf8`, 5, 12 | |

> [!NOTE]
> `COPY` is meant for small to medium data sets (up to a few million rows) and for moving data between environments. It is not a backup tool. For bulk loads use `sstableloader` or a Spark job; for backups use snapshots ([DR runbook](../07_disaster_recovery/01_backup_and_disaster_recovery.md)). The sample `conf/cqlshrc.sample` comments show `chunksize = 1000` and `minbatchsize = 2`; the code defaults above are what actually applies when you set nothing.

---

## 2. `sstableloader`: Streaming SSTables into a Live Cluster

`sstableloader` reads SSTables from a local directory and streams each partition to the nodes that own it in the **target** cluster. Topology, token layout and RF can all differ from the source.

```bash
sstableloader -d 10.0.1.10,10.0.1.11 [options] /path/to/<keyspace>/<table>/
```

The **last two path components must be `<keyspace>/<table>`**; snapshot layouts (`<table>-<id>/snapshots/<tag>/`) have to be rearranged first, or use `-k`/`-tb` to override the target. The table must already exist in the target cluster.

| Option | Purpose |
| :--- | :--- |
| `-d`, `--nodes` **(required)** | Initial hosts used to discover the ring |
| `-p`, `--port` / `-sp`, `--storage-port` | Native port (default 9042) / storage port (default 7000) |
| `-u`, `--username` / `-pw`, `--password` / `-ap`, `--auth-provider` | Authentication |
| `-k`, `--target-keyspace` / `-tb`, `--target-table` | Load into a different keyspace or table than the directory names say |
| `-i`, `--ignore` | Do not stream to these nodes |
| `-cph`, `--connections-per-host` | Concurrent connections per host |
| `--throttle-mib` / `--inter-dc-throttle-mib` | Throughput caps in MiB/s (0 = unlimited). `-t` / `-idct` (Mbit/s) are deprecated. |
| `--entire-sstable-throttle-mib`, `--entire-sstable-inter-dc-throttle-mib` | Caps for zero-copy entire-SSTable streaming |
| `-f`, `--conf-path` | A `cassandra.yaml` to read streaming and SSL settings from |
| `-ts`/`-tspw`, `-ks`/`-kspw`, `-prtcl`, `-alg`, `-st`, `-ciphers` | Client TLS truststore/keystore, protocol, algorithm, store type, cipher suites |
| `-v`, `--verbose` / `--no-progress` | Output control |

Each SSTable is streamed to **every** replica, so loading the snapshots of all N nodes of an RF=3 cluster sends roughly 3× the data the cluster will keep. Compaction collapses the duplicates afterwards. For loading files that are already on the right node, prefer `nodetool import`.

---

## 3. SSTable Inspection Tools (Read-Only)

### `sstablemetadata`: what's inside an SSTable
```bash
sstablemetadata [-g <gc_grace_seconds>] [-s] [-t <timestamp_unit>] [-u] [-c] <sstable-Data.db>...
```
Prints the format and version, min/max timestamps and local deletion times, the estimated droppable tombstone ratio, TTL ranges, the repaired-at / pending-repair state, the partition-size and cell-count histograms, compression ratio and the key range.
* `-g`, `--gc_grace_seconds`: the GC grace to use when computing droppable tombstones.
* `-s`, `--scan`: read the whole file for exact partition statistics (slow).
* `-t`, `--timestamp_unit`: the unit cell timestamps were written in.
* `-u`, `--unicode` / `-c`, `--colors`: output style.

Use it to answer "why isn't this SSTable compacting away?" and "is this file repaired?".

### `sstabledump`: SSTable to JSON
```bash
sstabledump <sstable-Data.db> [-k <key>...] [-x <key>...] [-e] [-d] [-l] [-t]
```
* `-k` / `-x`: include or exclude partition keys (repeatable).
* `-e`: list the partition keys only.
* `-d`: one CQL row per line, in internal debug form.
* `-l`: JSON lines, one per partition.
* `-t`: raw microsecond timestamps instead of ISO-8601.

Good for inspecting tombstones (`deletion_info`) and TTL'd cells.

### `sstablepartitions` (new in 5.0, CASSANDRA-8720): find large or tombstone-heavy partitions
```bash
# Partitions >= 100 MiB, or with >= 100k tombstones, in a whole table directory
sstablepartitions -t 100MiB -o 100000 /var/lib/cassandra/data/my_ks/events-*/
sstablepartitions -r -s -m /var/lib/cassandra/data/my_ks/   # recursive, include snapshots, CSV output
```
| Option | Meaning |
| :--- | :--- |
| `-t`, `--min-size` | Partition size threshold (e.g. `100MiB`) |
| `-o`, `--min-tombstones` / `-c`, `--min-cells` / `-w`, `--min-rows` | Count thresholds |
| `-k`, `--key` / `-x`, `--exclude-key` | Include or exclude specific keys |
| `-r`, `--recursive` / `-s`, `--snapshots` / `-b`, `--backups` | Directory scanning scope |
| `-y`, `--partitions-only` | Print only the partition keys |
| `-m`, `--csv` | Machine-readable output |
| `-u`, `--current-timestamp` | Treat this time as "now" when deciding whether tombstones are droppable |

This is the offline counterpart to the "Compacted partition maximum bytes" figure in `nodetool tablestats`, and it names the offending keys.

### `sstableexpiredblockers`: why fully expired SSTables are not being dropped
```bash
sstableexpiredblockers <keyspace> <table>
```
Lists the SSTables whose overlapping data blocks fully expired SSTables from being dropped. This usually explains TWCS tables whose disk usage keeps growing.

### `sstableutil`: list a table's files
```bash
sstableutil [-t all|tmp|final] [-o] [-c] [-v] <keyspace> <table>
```
`-t` filters by file type and `-o` includes operation logs. `-c`, `--cleanup` removes leftovers from interrupted transactions; it **modifies data, so run it offline only**.

---

## 4. SSTable Maintenance Tools (Offline Only)

| Tool | Usage | Notes |
| :--- | :--- | :--- |
| `sstablescrub` | `sstablescrub [-m] [-s] [-n] [-r] [-e <mode>] [-v] <ks> <table>` | Rewrites SSTables and drops unreadable rows. `-s` skips corrupt counter rows, `-n` skips column validation, `-m` only checks/repairs the LCS manifest, `-r` re-inserts cells whose TTL overflowed the 2038 limit, `-e` controls the serialization-header fix. A snapshot is taken first. Run `repair` afterwards. |
| `sstableverify` | `sstableverify -f [-e] [-c] [-q] [-r] [-v] <ks> <table>` | **Refuses to run without `-f`/`--force`** (CASSANDRA-17017). `-e` extended (reads every cell), `-q` quick, `-c` fails on old-version SSTables, `-r` leaves the repair status untouched. On a live node use `nodetool verify`. |
| `sstableupgrade` | `sstableupgrade [-k] <ks> <table> [snapshot]` | Rewrites to the current format. `-k` keeps the source files. Online: `nodetool upgradesstables`. |
| `sstablesplit` | `sstablesplit [-s <MB>] [--no-snapshot] <Data.db>...` | Splits large SSTables (default 50 MB pieces), e.g. after an accidental STCS major compaction. |
| `sstablelevelreset` | `sstablelevelreset --really-reset <ks> <table>` | Moves every LCS SSTable back to L0. |
| `sstableofflinerelevel` | `sstableofflinerelevel [--dry-run] <ks> <table>` | Rebuilds a sensible LCS leveling; use `--dry-run` first. |
| `sstablerepairedset` | `sstablerepairedset --really-set --is-repaired\|--is-unrepaired [-f <list-file> \| <sstables>]` | Changes the repaired-at flag. Mainly for migrating to or away from incremental repair. |

---

## 5. Log Tools: `fqltool` and `auditlogviewer`

Both read Chronicle Queue binary logs written by full query logging (`nodetool enablefullquerylog`) and audit logging. See [Monitoring](../06_operations_and_housekeeping/03_monitoring_and_observability.md) and [Security](../05_cluster_deployment_and_config/03_security_hardening.md).

```bash
# Print FQL entries (optionally follow a live log)
fqltool dump [--roll-cycle HOURLY] [--follow] /var/log/cassandra/fql

# Replay captured traffic against another cluster, saving results for comparison
fqltool replay --target 10.0.9.10 --keyspace my_ks --results /tmp/res_new \
               [--store-queries /tmp/queries] [--replay-ddl-statements] /var/log/cassandra/fql
fqltool compare --queries /tmp/queries /tmp/res_old /tmp/res_new

# Print audit log entries
auditlogviewer /var/log/cassandra/audit [-r HOURLY] [-f] [-i]
```
`-r`/`--roll-cycle` must match the roll cycle the log was written with. `-f`/`--follow` tails the log. `auditlogviewer -i` ignores unsupported records. DDL statements are **not** replayed unless you pass `--replay-ddl-statements`.

---

## 6. `cassandra-stress`: Load Generation

`tools/bin/cassandra-stress <command> [command options] [-option ...]`

| Command | What it does |
| :--- | :--- |
| `write`, `read` | Built-in `keyspace1.standard1` table (create it with `write` first) |
| `mixed ratio\(write=1,read=3\)` | Mixed workload on the built-in table |
| `counter_write`, `counter_read` | Built-in `counter1` table |
| `user profile=<yaml> ops\(insert=1,<query>=N\)` | Your own schema and queries, from a YAML profile |
| `help`, `print`, `version` | `cassandra-stress help -rate` shows the help for one option group |

Common command options: `n=<ops>` or `duration=<N>[smhd]`; `cl=<LEVEL>` (default `LOCAL_ONE`); `no-warmup`; `truncate=never|once|always`.

Common option groups:
* `-node <h1,h2> [datacenter=<dc>]`
* `-rate threads=<N> | threads>=4 threads<=1000 | throttle=<N>/s | fixed=<N>/s`
* `-mode native cql3 [prepared] [user=… password=…] [protocolVersion=…]`
* `-schema keyspace=<ks> "replication(strategy=NetworkTopologyStrategy, <dc>=3)"`
* `-pop seq=1..1000000`
* `-col size=fixed(256)`
* `-log file=out.log hdrfile=out.hdr interval=1s`
* `-graph file=report.html`
* `-port native=9042`

```bash
# 1. Load 1M rows, then read them back at QUORUM with 64 client threads for 10 minutes
cassandra-stress write n=1000000 cl=LOCAL_QUORUM -node 10.0.1.10 -rate threads=64 \
    -schema "replication(strategy=NetworkTopologyStrategy, us-east-1=3)"
cassandra-stress read duration=10m cl=LOCAL_QUORUM -node 10.0.1.10 -rate threads=64

# 2. Your own data model (sample profiles: tools/cqlstress-example.yaml, cqlstress-lwt-example.yaml)
cassandra-stress user profile=./my_profile.yaml ops\(insert=1,by_user=4\) duration=15m \
    cl=LOCAL_QUORUM -node 10.0.1.10 -rate threads=128 -graph file=my_profile.html
```

A user profile sets `keyspace`/`keyspace_definition`, `table`/`table_definition`, `columnspec` (size and population distributions per column), `insert` (`partitions`, `batchtype`, `select`) and named `queries`.

> [!TIP]
> Benchmark with a schema, row size and read/write mix that match production, at the consistency level you will use, on hardware like production's, for long enough that compaction kicks in (≥ 30 min). Results from a few minutes on the built-in `standard1` table say little about your workload. For a modern, scriptable alternative, NoSQLBench (external) is widely used.

`compaction-stress` (in `tools/bin`) generates SSTables and benchmarks compaction offline using the same YAML profiles. It is useful when comparing compaction strategies.

---

## 7. Other Helpers

| Tool | Usage |
| :--- | :--- |
| `generatetokens` | `generatetokens -n <nodes> -t <tokens-per-node> --rf <rf> [--racks 3,3,3] [-p Murmur3Partitioner]`: prints balanced `initial_token` lists for planned clusters |
| `hash_password` | `hash_password [-r <logrounds, default 10>] (-p <plain> \| -e <ENV_VAR> \| -i <file\|->)`: produces a bcrypt hash for `CREATE ROLE ... WITH HASHED PASSWORD` |
| `jmxtool` | Dumps and diffs MBean metadata. Mostly used to compare metrics between versions during upgrades. |
| `debug-cql` (`bin/`) | Developer tool for low-level protocol debugging |

---

## Sources

Repository files (branch `cassandra-5.0`):
* [pylib/cqlshlib/cqlshmain.py](https://github.com/apache/cassandra/blob/cassandra-5.0/pylib/cqlshlib/cqlshmain.py), [pylib/cqlshlib/cqlshhandling.py](https://github.com/apache/cassandra/blob/cassandra-5.0/pylib/cqlshlib/cqlshhandling.py), [pylib/cqlshlib/copyutil.py](https://github.com/apache/cassandra/blob/cassandra-5.0/pylib/cqlshlib/copyutil.py), [conf/cqlshrc.sample](https://github.com/apache/cassandra/blob/cassandra-5.0/conf/cqlshrc.sample), [conf/credentials.sample](https://github.com/apache/cassandra/blob/cassandra-5.0/conf/credentials.sample)
* [src/java/org/apache/cassandra/tools/LoaderOptions.java](https://github.com/apache/cassandra/blob/cassandra-5.0/src/java/org/apache/cassandra/tools/LoaderOptions.java), [SSTableExport.java](https://github.com/apache/cassandra/blob/cassandra-5.0/src/java/org/apache/cassandra/tools/SSTableExport.java), [SSTableMetadataViewer.java](https://github.com/apache/cassandra/blob/cassandra-5.0/src/java/org/apache/cassandra/tools/SSTableMetadataViewer.java), [SSTablePartitions.java](https://github.com/apache/cassandra/blob/cassandra-5.0/src/java/org/apache/cassandra/tools/SSTablePartitions.java), [StandaloneScrubber.java](https://github.com/apache/cassandra/blob/cassandra-5.0/src/java/org/apache/cassandra/tools/StandaloneScrubber.java), [StandaloneVerifier.java](https://github.com/apache/cassandra/blob/cassandra-5.0/src/java/org/apache/cassandra/tools/StandaloneVerifier.java), [StandaloneUpgrader.java](https://github.com/apache/cassandra/blob/cassandra-5.0/src/java/org/apache/cassandra/tools/StandaloneUpgrader.java), [StandaloneSplitter.java](https://github.com/apache/cassandra/blob/cassandra-5.0/src/java/org/apache/cassandra/tools/StandaloneSplitter.java), [StandaloneSSTableUtil.java](https://github.com/apache/cassandra/blob/cassandra-5.0/src/java/org/apache/cassandra/tools/StandaloneSSTableUtil.java), [SSTableLevelResetter.java](https://github.com/apache/cassandra/blob/cassandra-5.0/src/java/org/apache/cassandra/tools/SSTableLevelResetter.java), [SSTableOfflineRelevel.java](https://github.com/apache/cassandra/blob/cassandra-5.0/src/java/org/apache/cassandra/tools/SSTableOfflineRelevel.java), [SSTableRepairedAtSetter.java](https://github.com/apache/cassandra/blob/cassandra-5.0/src/java/org/apache/cassandra/tools/SSTableRepairedAtSetter.java), [SSTableExpiredBlockers.java](https://github.com/apache/cassandra/blob/cassandra-5.0/src/java/org/apache/cassandra/tools/SSTableExpiredBlockers.java), [AuditLogViewer.java](https://github.com/apache/cassandra/blob/cassandra-5.0/src/java/org/apache/cassandra/tools/AuditLogViewer.java), [GenerateTokens.java](https://github.com/apache/cassandra/blob/cassandra-5.0/src/java/org/apache/cassandra/tools/GenerateTokens.java), [HashPassword.java](https://github.com/apache/cassandra/blob/cassandra-5.0/src/java/org/apache/cassandra/tools/HashPassword.java)
* [tools/fqltool](https://github.com/apache/cassandra/tree/cassandra-5.0/tools/fqltool/src/org/apache/cassandra/fqltool/commands), [tools/stress settings](https://github.com/apache/cassandra/tree/cassandra-5.0/tools/stress/src/org/apache/cassandra/stress/settings), [tools/cqlstress-example.yaml](https://github.com/apache/cassandra/blob/cassandra-5.0/tools/cqlstress-example.yaml)
* [CHANGES.txt](https://github.com/apache/cassandra/blob/cassandra-5.0/CHANGES.txt) (CASSANDRA-8720 `sstablepartitions`, CASSANDRA-17577 `SHOW REPLICAS`)

Official documentation:
* cqlsh: https://cassandra.apache.org/doc/5.0/cassandra/managing/tools/cqlsh.html
* SSTable tools: https://cassandra.apache.org/doc/5.0/cassandra/managing/tools/sstable/index.html
* sstableloader: https://cassandra.apache.org/doc/5.0/cassandra/managing/tools/sstable/sstableloader.html
* cassandra-stress: https://cassandra.apache.org/doc/5.0/cassandra/tooling/cassandra-stress.html
* Full query logging: https://cassandra.apache.org/doc/5.0/cassandra/managing/operating/fqllogging.html
* Audit logging: https://cassandra.apache.org/doc/5.0/cassandra/managing/operating/audit_logging.html
