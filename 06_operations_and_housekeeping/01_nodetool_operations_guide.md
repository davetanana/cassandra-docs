# Nodetool Operations Manual: Commands, Diagnostics & Administration

`nodetool` is the command-line administration tool for a Cassandra node. It talks to the node over JMX (port 7199, bound to localhost by default). Run `nodetool help <command>` for the full option list of any command. The sample outputs below are abridged.

---

## 1. Cluster Status & Topology Commands

### `nodetool status [keyspace]`
Shows the state, load and token ownership of every node. Pass a keyspace to get **effective** ownership for that keyspace's replication settings.

```bash
$ nodetool status production_keyspace
Datacenter: us-east-1
=====================
Status=Up/Down
|/ State=Normal/Leaving/Joining/Moving
--  Address        Load        Tokens  Owns (effective)  Host ID                               Rack
UN  10.0.1.12      142.34 GiB  16      100.0%            a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d  us-east-1a
UN  10.0.1.15      138.81 GiB  16      100.0%            b2c3d4e5-f6a7-8b9c-0d1e-2f3a4b5c6d7e  us-east-1b
DN  10.0.1.18      140.12 GiB  16      100.0%            c3d4e5f6-a7b8-9c0d-1e2f-3a4b5c6d7e8f  us-east-1c
```
(With three nodes and RF=3, each node owns 100% effectively. `Tokens` is `num_tokens`, 16 by default in 5.0.)

#### Status & State Legend:
* **`UN` (Up / Normal)**: Healthy and serving traffic.
* **`DN` (Down / Normal)**: Marked down by gossip; it still owns its tokens.
* **`UJ` (Up / Joining)**: Bootstrapping and streaming data in.
* **`UL` (Up / Leaving)**: Decommissioning and streaming data out.
* **`UM` (Up / Moving)**: Moving to a new token.

### `nodetool ring [keyspace]`
Lists every token and the node that owns it. Use it to record a node's tokens for restores, or to check the token distribution. `nodetool info -T` prints only the local node's tokens.

---

### `nodetool describecluster`
Shows the cluster name, snitch, partitioner and schema versions:

```bash
$ nodetool describecluster
Cluster Information:
    Name: ProductionCluster
    Snitch: org.apache.cassandra.locator.Ec2Snitch
    DynamicEndPointSnitch: enabled
    Partitioner: org.apache.cassandra.dht.Murmur3Partitioner
    Schema versions:
        9a8b7c6d-5e4f-3a2b-1c0d-e9f8a7b6c5d4: [10.0.1.12, 10.0.1.15]
        UNREACHABLE: [10.0.1.18]
```
> [!WARNING]
> If `Schema versions` lists more than one UUID (excluding UNREACHABLE) for more than a short time, the cluster has a **schema disagreement**. Do not run more DDL until the nodes converge.

---

### `nodetool info`
Node-level details: uptime, heap and off-heap usage, generation number, datacenter, rack, cache sizes and exception count. `-T` adds the node's tokens.

---

## 2. Diagnostics, Thread Pools & Metrics

### `nodetool tpstats`
The first command to run when investigating latency or dropped requests:

```bash
$ nodetool tpstats
Pool Name                         Active   Pending      Completed   Blocked  All time blocked
ReadStage                              4         0       14298104         0                 0
MutationStage                         12         2       98102394         0                 0
CompactionExecutor                     2         4          48102         0                 0
...
Latencies waiting in queue (micros) per dropped message types
Message type           Dropped     50%      95%      99%      Max
READ_REQ                     0      ...
MUTATION_REQ               142      ...   <-- writes dropped
HINT_REQ                     0      ...
```

#### What to Look For:
* **`Pending` continually > 0**: The pool is saturated and requests are queuing.
* **`Dropped` > 0**: The node discarded messages that had already waited longer than their timeout (`write_request_timeout`, `read_request_timeout`, ...). This usually points to saturated disk I/O, GC pauses or an overloaded node. A dropped mutation is a missed write on that replica, recovered later by hints or repair.

---

### `nodetool tablestats <keyspace>.<table>`
Per-table metrics. The fields to check first:
```bash
$ nodetool tablestats production_keyspace.user_events
	Table: user_events
	SSTable count: 8
	Space used (live): 45291847680
	Space used by snapshots (total): 0
	Number of partitions (estimate): 1420930
	Percent repaired: 87.5
	Compacted partition maximum bytes: 51286138      <-- largest partition seen by compaction
	Compacted partition mean bytes: 31766
	Average tombstones per slice (last five minutes): 1.2
	Maximum tombstones per slice (last five minutes): 840   <-- compare with tombstone_warn_threshold (1000)
```
Add `-H` for human-readable sizes. Tables with SAI indexes also report `SAI ...` lines (query latency, space used, rows filtered).

---

### `nodetool tablehistograms <keyspace> <table>`
Percentile histograms (50%, 75%, 95%, 98%, 99%, Min, Max) for:
* **SSTables read per query**. Low single digits is healthy. A steadily rising number suggests compaction is falling behind or the compaction strategy does not fit the workload.
* **Read / write latency** (microseconds).
* **Partition size** and **cell count**.

---

### `nodetool toppartitions <keyspace> <table> <duration_ms>` and `nodetool profileload`
`toppartitions` samples one table for the given time and reports its hottest partitions:

```bash
$ nodetool toppartitions production_keyspace user_events 5000
```
`profileload [<keyspace> <table> <duration_ms>]` is the broader version: it samples all tables (or one) and reports top partitions by reads, writes, CAS contention and more. `-k` sets the number of results, and `-i/--interval` schedules continuous background sampling.

---

### `nodetool compactionstats` and `nodetool netstats`
* `compactionstats` (`-H` for human-readable): running compactions and the number of **pending tasks**. A pending count that keeps rising means compaction cannot keep up.
* `netstats`: active streaming sessions (bootstrap, repair, rebuild, decommission), and pending/completed internode messages.

---

## 3. Maintenance, Compaction & Disk Operations

### `nodetool flush [keyspace] [table...]`
Writes memtables to new SSTables on disk, so the corresponding commit log segments can be recycled. The memtable implementation depends on configuration: `SkipListMemtable` with the default `cassandra.yaml`, `TrieMemtable` with `cassandra_latest.yaml`.
* You don't need to flush before a snapshot (`nodetool snapshot` flushes unless you pass `-sf`) or before a shutdown (`nodetool drain` flushes).

---

### `nodetool compact [keyspace] [table...]`
> [!CAUTION]
> **`nodetool compact` without flags performs a MAJOR compaction** of the named tables (every table in the node, if you pass nothing). With `SizeTieredCompactionStrategy` this merges each table into one very large SSTable that is unlikely to be compacted again soon, and the operation temporarily needs free space roughly equal to the table's size. Avoid it in production unless you understand the consequences.

* **`-s` / `--split-output`**: for STCS major compactions, writes several SSTables of decreasing size instead of one huge file. It cannot be combined with `--user-defined` or a token range.
* **`--user-defined <SSTable files>`**: compacts only the listed SSTables.
* **`-st` / `-et`**: compacts only a token range. **`--partition <key>`** compacts one partition.

---

### `nodetool cleanup [keyspace] [table...]`
Removes data for token ranges the node no longer owns, after new nodes have joined. It rewrites SSTables, so it needs disk headroom.
* Run it on each **existing** node, **one node at a time**, after the new node is `UN`. `-j` sets how many SSTables are cleaned in parallel (default 2).

---

### `nodetool garbagecollect [keyspace] [table...]`
Available since Cassandra 3.10 (not new in 5.0). Rewrites each SSTable on its own, dropping data that is shadowed by newer tombstones or overwrites found in other SSTables. It does not merge SSTables, so it is less disruptive than a major compaction.
* `-g ROW` (default) removes deleted partitions and rows; `-g CELL` also removes overwritten or deleted cells.
* It **rewrites SSTables**, so it needs free disk space and uses compaction I/O. It is not an emergency tool for a full disk.

---

### `nodetool scrub [keyspace] [table...]` and `nodetool verify`
* `verify` checks SSTable checksums and reports corruption without changing anything. Run it first.
* `scrub` rewrites SSTables and skips rows it cannot read. It takes a snapshot first unless you pass `--no-snapshot`. After scrubbing, run a repair of the table so the dropped rows are restored from other replicas.

---

## 4. Anti-Entropy Repair

Repair compares replicas and streams the differences between them. It must complete for all data within every table's `gc_grace_seconds` (default 864,000 s = 10 days), or deleted data can come back (see the housekeeping guide).

### Incremental vs. Full
* **`nodetool repair` with no flags runs an INCREMENTAL repair.** It only compares SSTables not yet marked repaired, then marks them repaired (anti-compaction). Run it frequently so each run stays small.
* **`--full` (`-full`)** compares all data, whether or not it is marked repaired. Use it for regular full repairs, after replacing a node, and after restoring data.
* If a cluster has never run incremental repair, read the incremental-repair migration guidance before switching on a large existing data set: the first incremental run anti-compacts everything.

### Scope flags
| Flag | Effect | Notes |
| :--- | :--- | :--- |
| `-pr` / `--partitioner-range` | Repairs only the ranges for which this node is the primary replica. | Must be run on **every node in every datacenter** to cover the whole ring. Cannot be combined with `-dc` or `-hosts` (nodetool refuses: "Primary range repair should be performed on all nodes in the cluster."). |
| `-dc <dc>` / `--in-dc` | Repairs with replicas in the named datacenter(s) only. | Not combinable with `-pr`. |
| `-local` / `--in-local-dc` | Repairs only with replicas in the local datacenter, avoiding cross-DC traffic. | Allowed with `-pr`, but then every DC must run its own `-pr -local` pass for full coverage. |
| `-st` / `-et` | Repairs a token sub-range. | Used by repair schedulers to split work. |
| `-seq` | Sequential repair (one replica at a time builds its Merkle tree). | Lower impact, slower. |
| `-j <n>` | Repair job threads (1–4). | |
| `-prv` / `-vd` | Preview what would be streamed / validate already-repaired data. | Do not change data. |

```bash
# Full repair of this node's primary ranges for one keyspace.
# Repeat on every node in every DC, one node at a time.
nodetool repair --full -pr production_keyspace
```

For anything beyond a small cluster, use a scheduler: Cassandra 5.0.8+ has a built-in automated repair scheduler, and Cassandra Reaper is a widely used external one (see the housekeeping guide).

---

## 5. Backups & Snapshots

Snapshots are **hard links** to existing SSTable files, so taking one is fast and uses almost no extra space at first. As compaction replaces the original SSTables, the snapshot keeps the old files alive, and its disk usage grows towards the full size of the data.

```bash
# Take a snapshot of one keyspace (flushes first unless -sf is given).
nodetool snapshot -t backup_20261121 production_keyspace

# Snapshot with an automatic expiry (cleared by Cassandra after the TTL).
nodetool snapshot -t backup_20261121 --ttl 3d production_keyspace

# List snapshots, their size on disk and their true size.
nodetool listsnapshots

# Remove one snapshot by name.
nodetool clearsnapshot -t backup_20261121 production_keyspace

# Remove every snapshot older than 7 days, in all keyspaces.
nodetool clearsnapshot --all --older-than 7d
```
`clearsnapshot` requires either `-t <name>` or `--all`; with neither it fails with "Specify snapshot name or --all". `--older-than` and `--older-than-timestamp` cannot be combined with `-t`.

Each table's snapshot directory also contains `manifest.json` (the SSTables in the snapshot) and `schema.cql` (the CQL to re-create the table). See the disaster recovery runbook for restores using `nodetool import`.

### `nodetool import <keyspace> <table> <directory>...`
Loads SSTables from a directory into a live table without a restart. It verifies the files and places them in the correct data directory. It replaces `nodetool refresh`, which is deprecated in 5.0.

---

## 6. Node Lifecycle & Topology Operations

### `nodetool drain` (before every stop or restart)
```bash
nodetool drain && sudo systemctl stop cassandra
```
`drain` on its own is enough. It:
1. Stops the native transport (CQL) and gossip, so clients and peers stop sending requests to the node.
2. Stops internode messaging and waits for in-flight mutations to finish.
3. Flushes all memtables, so the commit log does not need to be replayed at the next start.

After a drain the node no longer accepts writes; stop the process next. You don't need `disablebinary`, `disablegossip` or `flush` beforehand.

---

### `nodetool decommission`
Retires a live node: it streams the node's data to the nodes that take over its ranges, then leaves the ring. No `cleanup` is needed afterwards. Make sure the remaining nodes have room for the extra data.

---

### `nodetool removenode <HostID>`
Removes a dead node that will never return. The remaining replicas re-stream its data among themselves:
```bash
$ nodetool status | grep DN
DN  10.0.1.18  140.12 GiB  16  33.4%  c3d4e5f6-a7b8-9c0d-1e2f-3a4b5c6d7e8f  us-east-1c

$ nodetool removenode c3d4e5f6-a7b8-9c0d-1e2f-3a4b5c6d7e8f
$ nodetool removenode status
```
If you are going to put a new machine in the same place, replace the node instead (`replace_address_first_boot`), which streams the data once rather than twice.

---

## 7. Runtime Tuning (No Restart)

These settings change only the running process. They are lost on restart unless you also change `cassandra.yaml`.

| Command | Purpose |
| :--- | :--- |
| `nodetool setcompactionthroughput 64` | Caps compaction I/O at 64 MiB/s (`0` disables the cap). `getcompactionthroughput` shows the current value. |
| `nodetool setconcurrentcompactors 4` | Changes the number of concurrent compaction threads. |
| `nodetool setconcurrency ReadStage 64` | Changes a stage's maximum concurrency (for example `ReadStage`, `MutationStage`). `getconcurrency` lists current values. |
| `nodetool setstreamthroughput <MiB/s>` | Caps streaming throughput for bootstrap, repair and rebuild. |
| `nodetool settimeout read 5000` | Changes a timeout in ms. Types: `read, range, write, counterwrite, cascontention, truncate, internodeconnect, internodeuser, internodestreaminguser, misc`. |
| `nodetool reloadssl` | Reloads TLS keystores and truststores, for certificate rotation without a restart. |
