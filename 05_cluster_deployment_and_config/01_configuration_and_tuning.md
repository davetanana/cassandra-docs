# Node Configuration, JVM & Operating System Tuning

A Cassandra 5.0 node is tuned at three layers:

1. **`cassandra.yaml`**: database engine settings.
2. **JVM options**: `conf/jvm-server.options` (all JVMs), plus `conf/jvm11-server.options` or `conf/jvm17-server.options` (version-specific), and `conf/cassandra-env.sh`.
3. **Linux**: `sysctl`, resource limits, Transparent Huge Pages, filesystem and mount options.

> [!NOTE]
> **Which template?** `conf/cassandra.yaml` keeps 4.x-compatible defaults (SkipList memtables, BIG SSTables, STCS, legacy secondary indexes, Paxos v1, `storage_compatibility_mode: CASSANDRA_4`). `conf/cassandra_latest.yaml` turns on the 5.0 features (Trie memtables, BTI SSTables, UCS, SAI as default index, Paxos v2, `memtable_allocation_type: offheap_objects`, `storage_compatibility_mode: NONE`). For a **new** cluster with no 4.x nodes, starting from `cassandra_latest.yaml` is reasonable. For a cluster being **upgraded** from 4.x, start from `cassandra.yaml` and move `storage_compatibility_mode` through `CASSANDRA_4` → `UPGRADING` → `NONE` only after every node runs 5.0 (see [04_upgrading_to_5_0.md](04_upgrading_to_5_0.md) and the comments above that setting in `cassandra.yaml`).

---

## 1. Production `cassandra.yaml` Settings

The snippet below shows the settings you will almost always change, plus the important defaults. Values marked *(default)* match what ships in `conf/cassandra.yaml`; anything else is a deliberate change explained in the comment.

> [!IMPORTANT]
> **Use the 5.0 key names.** Since 4.1, durations and sizes carry units (`commitlog_sync_period: 10000ms`, `compaction_throughput: 64MiB/s`, `read_request_timeout: 5000ms`). The old names (`commitlog_sync_period_in_ms`, `compaction_throughput_mb_per_sec`, `read_request_timeout_in_ms`, ...) are still accepted as **deprecated aliases** and log a deprecation warning. Don't mix old and new names for the same setting.

```yaml
# ==============================================================================
# CLUSTER IDENTIFICATION & TOKENS
# ==============================================================================
cluster_name: 'ProductionCluster'      # Must be identical on every node. Cannot be changed later without downtime.
num_tokens: 16                         # (default) vnodes per node
allocate_tokens_for_local_replication_factor: 3   # (default) token allocator optimises balance for RF=3 per DC.
                                       # Set it to your actual per-DC RF before a node first starts.

# ==============================================================================
# NETWORKING
# ==============================================================================
listen_address: 10.0.1.10              # This node's private IP (default: localhost, which is never right in production)
# broadcast_address: 203.0.113.10      # Only when peers must reach this node on a different (e.g. public/NAT) address
rpc_address: 0.0.0.0                   # Listen for CQL on all interfaces...
broadcast_rpc_address: 10.0.1.10       # ...which then REQUIRES broadcast_rpc_address (address advertised to drivers)
storage_port: 7000                     # (default) internode, plaintext AND TLS (since 4.0)
native_transport_port: 9042            # (default) CQL, plaintext or TLS

seed_provider:
  - class_name: org.apache.cassandra.locator.SimpleSeedProvider
    parameters:
      # 2-3 stable nodes per datacenter. Same list on every node.
      - seeds: "10.0.1.10,10.0.1.11,10.0.2.10,10.0.2.11"

endpoint_snitch: GossipingPropertyFileSnitch   # default is SimpleSnitch, which is single-DC only.
                                               # See the deployment runbook and cloud guides for cloud snitches.

# ==============================================================================
# STORAGE DIRECTORIES
# ==============================================================================
# Tarball default is $CASSANDRA_HOME/data/...; deb/rpm packages use /var/lib/cassandra/...
data_file_directories:
  - /mnt/cassandra/data
commitlog_directory: /mnt/cassandra/commitlog   # Separate device helps on spinning disks; optional on NVMe
saved_caches_directory: /mnt/cassandra/saved_caches
hints_directory: /mnt/cassandra/hints

# ==============================================================================
# COMMIT LOG
# ==============================================================================
commitlog_sync: periodic               # (default)
commitlog_sync_period: 10000ms         # (default) acknowledged writes may be up to 10s from an fsync
commitlog_segment_size: 32MiB          # (default)
# commitlog_total_space: 8192MiB       # default: smaller of 8192MiB and 1/4 of the commitlog volume

# ==============================================================================
# MEMTABLES
# ==============================================================================
# Same shape as cassandra_latest.yaml. Define both implementations and point
# "default" at one; tables can still pick another with WITH memtable = 'skiplist'.
memtable:
  configurations:
    skiplist:
      class_name: SkipListMemtable
    trie:
      class_name: TrieMemtable
    default:
      inherits: trie                   # cassandra.yaml ships "inherits: skiplist"
# memtable_allocation_type: heap_buffers   # (default in cassandra.yaml)
# cassandra_latest.yaml uses offheap_objects, which pairs well with TrieMemtable.

# ==============================================================================
# CONCURRENCY & COMPACTION
# ==============================================================================
concurrent_reads: 32                   # (default) yaml guidance: 16 x number_of_drives
concurrent_writes: 32                  # (default) yaml guidance: 8 x number_of_cores
concurrent_counter_writes: 32          # (default)
# concurrent_compactors:               # default: min(#disks, #cores), clamped to 2..8.
                                       # The yaml suggests raising it to #cores on SSD.
compaction_throughput: 64MiB/s         # (default) 0 disables throttling

# ==============================================================================
# TIMEOUTS (all defaults)
# ==============================================================================
read_request_timeout: 5000ms
range_request_timeout: 10000ms
write_request_timeout: 2000ms
cas_contention_timeout: 1000ms

# ==============================================================================
# HINTS
# ==============================================================================
hinted_handoff_enabled: true           # (default)
max_hint_window: 3h                    # (default) a node down longer than this gets no new hints;
                                       # it MUST be repaired after it returns.
hinted_handoff_throttle: 1024KiB       # (default) per delivery thread
max_hints_delivery_threads: 2          # (default)

# ==============================================================================
# SNAPSHOTS
# ==============================================================================
auto_snapshot: true                    # (default) DROP/TRUNCATE takes a snapshot first. Keep it on.
# auto_snapshot_ttl: 30d               # Off by default. Set it so auto-snapshots don't accumulate forever.
incremental_backups: false             # (default)
```

### Concurrency: when to change the defaults

The shipped `concurrent_reads: 32` / `concurrent_writes: 32` are conservative. The `cassandra.yaml` comments give the rules of thumb: reads ≈ 16 × data drives (disk-bound), writes ≈ 8 × cores (CPU-bound). On an 8-core node with one NVMe drive, the defaults are already close. Raise them only if `nodetool tpstats` shows sustained `Pending` on `ReadStage` / `MutationStage` while CPU and disk still have headroom. Both can also be changed at runtime with `nodetool setconcurrency ReadStage <n>` / `MutationStage <n>`.

### Table-level settings that matter for operations

These are set per table (`CREATE/ALTER TABLE ... WITH`), not in `cassandra.yaml`:

| Option | Default | Why it matters |
| :--- | :--- | :--- |
| `gc_grace_seconds` | `864000` (10 days) | Tombstones are kept at least this long. **Every replica must be repaired within this window** or deleted data can come back. Shorten it only if repairs reliably finish more often; never set it below `max_hint_window`. |
| `default_time_to_live` | `0` (none) | Table-wide TTL. |
| `compaction` | `SizeTieredCompactionStrategy` (`cassandra.yaml`), `UnifiedCompactionStrategy` (`cassandra_latest.yaml` `default_compaction`) | Choose per workload; TWCS for TTL'd time series. |

---

## 2. Guardrails

Cassandra 5.0 guardrails let operators warn on or reject risky schema and queries. They are all set in `cassandra.yaml`; most are **disabled (`-1`) or permissive by default**, so you have to turn them on. Superusers bypass most guardrails.

| Guardrail | Default | Suggested production starting point |
| :--- | :--- | :--- |
| `tombstone_warn_threshold` / `tombstone_failure_threshold` | `1000` / `100000` | Keep. |
| `batch_size_warn_threshold` / `batch_size_fail_threshold` | `5KiB` / `50KiB` | Keep. |
| `unlogged_batch_across_partitions_warn_threshold` | `10` | Keep. |
| `allow_filtering_enabled` | `true` | `false` for application roles. |
| `partition_size_warn_threshold` / `_fail_threshold` | unset | e.g. warn `100MiB`. |
| `collection_size_warn_threshold`, `items_per_collection_warn_threshold` | unset / `-1` | Set warn levels. |
| `tables_warn_threshold` / `tables_fail_threshold` | `-1` | e.g. warn 150, fail 200 (each table costs heap). |
| `secondary_indexes_per_table_warn/fail_threshold` | `-1` | Set if many teams create indexes. |
| `page_size_warn/fail_threshold` | `-1` | Optional. |
| `read_before_write_list_operations_enabled` | `true` | `false` blocks list set-by-index / remove-by-value. |
| `drop_truncate_table_enabled`, `drop_keyspace_enabled` | `true` | Consider `false` in production. |
| `simplestrategy_enabled` | `true` | `false` (force `NetworkTopologyStrategy`). |
| `minimum_replication_factor_warn/fail_threshold` | `-1` | e.g. fail below 2. |
| `data_disk_usage_percentage_warn/fail_threshold` | `-1` | e.g. warn 70, fail 85. Writes are rejected over the fail threshold. |
| `vector_dimensions_warn/fail_threshold` | `-1` | Optional. |

See the `# Guardrails` section of `conf/cassandra.yaml` for the full list.

---

## 3. JVM Configuration

Cassandra 5.0 supports **Java 11 and Java 17 only**. Java 21 is not supported. See [01_java_and_jvm_flavors.md](../04_infrastructure_and_cloud/01_java_and_jvm_flavors.md) for runtimes and collectors.

### Where settings go

| File | Contents |
| :--- | :--- |
| `conf/jvm-server.options` | Options for every Java version: **heap (`-Xms`/`-Xmx`)**, `-XX:MaxDirectMemorySize`, system properties (`-Dcassandra.*`). Already ships `-XX:+AlwaysPreTouch`, `-XX:+UseNUMA`, `-XX:+UseThreadPriorities`, `-XX:+HeapDumpOnOutOfMemoryError`, `-XX:+PerfDisableSharedMem`. |
| `conf/jvm17-server.options` / `conf/jvm11-server.options` | Version-specific flags, including the **G1 GC settings**. |
| `conf/cassandra-env.sh` | Heap auto-sizing, or `MAX_HEAP_SIZE` if you prefer environment variables. |

Set heap **either** with `-Xms`/`-Xmx` in `jvm-server.options` **or** `MAX_HEAP_SIZE` in `cassandra-env.sh`, not both. Always set `-Xms` and `-Xmx` as a pair, to the same value.

### Heap auto-sizing (`cassandra-env.sh`)

If you set nothing, `cassandra-env.sh` calculates:

* **Heap** = min(½ of RAM, **31744 MiB**) with G1 (the CMS limit is 15872 MiB, Java 11 only).
* **`MaxDirectMemorySize`**: ½ of that heap limit when ½ RAM exceeds the limit (hosts above ~62 GB RAM), otherwise ¼ of RAM.

Auto-sizing is fine for most hosts. On a 64 GB host it gives a ~31 GB heap, which is more than most workloads need; many operators pin 16–24 GB to leave more RAM for the page cache.

### The Compressed OOPs boundary

Below roughly 32 GB of heap, HotSpot uses 32-bit compressed object pointers. Just above it, every reference doubles to 64 bits, so a heap of 32–~40 GB holds **less** than a 31 GB heap. Stay at or below 31 GB (the auto-sizing limit exists for this reason). The exact boundary depends on the JVM; check it with `java -Xmx31g -XX:+PrintFlagsFinal -version | grep UseCompressedOops`.

### Example memory plan (64 GB host)

```
├── JVM heap (-Xms24G -Xmx24G)                 : 24 GB
├── Direct memory (-XX:MaxDirectMemorySize)    : up to 8–12 GB (chunk cache, network buffers)
├── Other native memory (bloom filters, index summaries,
│   off-heap memtables if offheap_*)           : a few GB, workload dependent
└── OS page cache + kernel                     : the rest (it matters for reads)
```

```bash
# conf/jvm-server.options
-Xms24G
-Xmx24G
-XX:MaxDirectMemorySize=12G   # optional; otherwise derived by cassandra-env.sh
```

### G1 settings

Keep the G1 block shipped in `conf/jvm17-server.options` (identical in `jvm11-server.options`):

```bash
-XX:+UseG1GC
-XX:+ParallelRefProcEnabled
-XX:MaxTenuringThreshold=2
-XX:G1HeapRegionSize=16m
-XX:+UnlockExperimentalVMOptions
-XX:G1NewSizePercent=50
-XX:G1RSetUpdatingPauseTimePercent=5
-XX:MaxGCPauseMillis=300
-XX:InitiatingHeapOccupancyPercent=70
```

These are the tested defaults. Change them only from GC log evidence (`logs/gc.log`), one flag at a time. For example, lower `MaxGCPauseMillis` only if long pauses correlate with latency spikes and you can absorb the extra GC CPU.

---

## 4. Linux Operating System Tuning

The deb package installs `/etc/sysctl.d/cassandra.conf` with `vm.max_map_count = 1048575` and `net.ipv4.tcp_keepalive_time=300`, and `/etc/security/limits.d/cassandra.conf` with `nofile 100000`, `memlock unlimited`, `as unlimited`, `nproc 8096`. Tarball installs get nothing, so apply the settings below yourself.

### Kernel sysctl (`/etc/sysctl.d/99-cassandra.conf`)
```ini
vm.max_map_count = 1048575           # Cassandra memory-maps SSTable index/data files
vm.swappiness = 1                    # Prefer not to swap; better still, disable swap entirely
net.ipv4.tcp_keepalive_time = 300    # Same as the deb package; detects dead peers faster
net.core.somaxconn = 4096
net.ipv4.tcp_max_syn_backlog = 8192
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
net.ipv4.tcp_rmem = 4096 87380 16777216
net.ipv4.tcp_wmem = 4096 65536 16777216
```
Apply with `sudo sysctl -p /etc/sysctl.d/99-cassandra.conf`. Disable swap with `sudo swapoff -a` and remove swap entries from `/etc/fstab`.

### Resource limits (`/etc/security/limits.d/cassandra.conf`)
```ini
cassandra - nofile 1048576
cassandra - memlock unlimited
cassandra - as unlimited
cassandra - nproc 32768
```
If Cassandra runs under systemd, `limits.d` is **not** applied; set `LimitNOFILE=`, `LimitMEMLOCK=infinity`, `LimitAS=infinity`, `LimitNPROC=` in the unit file or a drop-in instead. Check the effective values with `cat /proc/$(pgrep -f CassandraDaemon)/limits`.

### Transparent Huge Pages
```bash
echo never | sudo tee /sys/kernel/mm/transparent_hugepage/enabled
echo never | sudo tee /sys/kernel/mm/transparent_hugepage/defrag
```
This doesn't survive a reboot; persist it with a systemd unit, tuned profile, or the kernel parameter `transparent_hugepage=never`.

### Filesystem
* XFS or ext4 on SSD/NVMe. Mount data and commit log volumes with `noatime`.
* For SSDs, use the `none` (NVMe) or `mq-deadline` I/O scheduler and a small read-ahead (e.g. `blockdev --setra 8 /dev/<dev>`). Large read-ahead wastes page cache on random reads.

```bash
# /etc/fstab
UUID=<uuid>  /mnt/cassandra  xfs  defaults,noatime  0  2
```

---

## 5. Security

The shipped configuration has **no authentication, no authorization and no encryption** (`authenticator: AllowAllAuthenticator`). Before production traffic, follow [03_security_hardening.md](03_security_hardening.md).
