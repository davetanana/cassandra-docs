# nodetool Reference (generated)

> [!NOTE]
> **Generated** from Apache Cassandra **5.0.10** at git commit `47227d98bf` (`src/java/org/apache/cassandra/tools/NodeTool.java` and `tools/nodetool/*.java`). Do not edit by hand.
> Regenerate with: `python3 tools/gen_nodetool_reference.py <cassandra-checkout> -o 09_reference/02_nodetool_reference.md`
>
> Descriptions are taken from the Apache Cassandra source, used under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0). Official equivalent: [nodetool](https://cassandra.apache.org/doc/5.0/cassandra/managing/tools/nodetool/nodetool.html).

147 top-level commands and 6 grouped subcommands. Run `nodetool help <command>` on a node for the authoritative help text of the version you run.

## Global options

These connection options apply to every command and go before the command name, for example `nodetool -h 10.0.1.10 -p 7199 status`.

| Option | Description |
| :--- | :--- |
| `-h`, `--host` | Node hostname or ip address |
| `-p`, `--port` | Remote jmx agent port number |
| `-u`, `--username` | Remote jmx agent username |
| `-pw`, `--password` | Remote jmx agent password |
| `-pwf`, `--password-file` | Path to the JMX password file |
| `-pp`, `--print-port` | Operate in 4.0 mode with hosts disambiguated by port number |

## Index

| Command | Description |
| :--- | :--- |
| [`assassinate`](#assassinate) | Forcefully remove a dead node without re-replicating any data. Use as a last resort if you cannot removenode |
| [`autorepairstatus`](#autorepairstatus) | Print autorepair status |
| [`bootstrap resume`](#bootstrap-resume) | Resume bootstrap streaming |
| [`checktokenmetadata`](#checktokenmetadata) | compares the Gossip endpointState and TokenMetadata cache; printing any mismatches found |
| [`cidrfilteringstats`](#cidrfilteringstats) | Print statistics on CIDR filtering |
| [`cleanup`](#cleanup) | Triggers the immediate cleanup of keys no longer belonging to a node. By default, clean all keyspaces |
| [`clearsnapshot`](#clearsnapshot) | Remove the snapshot with the given name from the given keyspaces |
| [`clientstats`](#clientstats) | Print information about connected clients |
| [`compact`](#compact) | Force a (major) compaction on one or more tables or user-defined compaction on given SSTables |
| [`compactionhistory`](#compactionhistory) | Print history of compaction |
| [`compactionstats`](#compactionstats) | Print statistics on compactions |
| [`datapaths`](#datapaths) | Print all directories where data of tables are stored |
| [`decommission`](#decommission) | Decommission the *node I am connecting to* |
| [`describecluster`](#describecluster) | Print the name, snitch, partitioner and schema version of a cluster |
| [`describering`](#describering) | Shows the token ranges info of a given keyspace |
| [`disableauditlog`](#disableauditlog) | Disable the audit log |
| [`disableautocompaction`](#disableautocompaction) | Disable autocompaction for the given keyspace and table |
| [`disablebackup`](#disablebackup) | Disable incremental backup |
| [`disablebinary`](#disablebinary) | Disable native transport (binary protocol) |
| [`disablefullquerylog`](#disablefullquerylog) | Disable the full query log |
| [`disablegossip`](#disablegossip) | Disable gossip (effectively marking the node down) |
| [`disablehandoff`](#disablehandoff) | Disable storing hinted handoffs |
| [`disablehintsfordc`](#disablehintsfordc) | Disable hints for a data center |
| [`disableoldprotocolversions`](#disableoldprotocolversions) | Disable old protocol versions |
| [`drain`](#drain) | Drain the node (stop accepting writes and flush all tables) |
| [`dropcidrgroup`](#dropcidrgroup) | Drop an existing cidr group |
| [`enableauditlog`](#enableauditlog) | Enable the audit log |
| [`enableautocompaction`](#enableautocompaction) | Enable autocompaction for the given keyspace and table |
| [`enablebackup`](#enablebackup) | Enable incremental backup |
| [`enablebinary`](#enablebinary) | Reenable native transport (binary protocol) |
| [`enablefullquerylog`](#enablefullquerylog) | Enable full query logging, defaults for the options are configured in cassandra.yaml |
| [`enablegossip`](#enablegossip) | Reenable gossip |
| [`enablehandoff`](#enablehandoff) | Reenable future hints storing on the current node |
| [`enablehintsfordc`](#enablehintsfordc) | Enable hints for a data center that was previsouly disabled |
| [`enableoldprotocolversions`](#enableoldprotocolversions) | Enable old protocol versions |
| [`failuredetector`](#failuredetector) | Shows the failure detector information for the cluster |
| [`flush`](#flush) | Flush one or more tables |
| [`forcecompact`](#forcecompact) | Force a (major) compaction on a table |
| [`garbagecollect`](#garbagecollect) | Remove deleted data from one or more tables |
| [`gcstats`](#gcstats) | Print GC Statistics |
| [`getauditlog`](#getauditlog) | Print configuration of audit log if enabled, otherwise the configuration reflected in cassandra.yaml |
| [`getauthcacheconfig`](#getauthcacheconfig) | Get configuration of Auth cache |
| [`getautorepairconfig`](#getautorepairconfig) | Print autorepair configurations |
| [`getbatchlogreplaythrottle`](#getbatchlogreplaythrottle) | Print batchlog replay throttle in KB/s. This is reduced proportionally to the number of nodes in the cluster. |
| [`getcidrgroupsofip`](#getcidrgroupsofip) | Print CIDR groups associated with given IP |
| [`getcolumnindexsize`](#getcolumnindexsize) | Print the granularity of the collation index of rows within a partition in KiB |
| [`getcompactionthreshold`](#getcompactionthreshold) | Print min and max compaction thresholds for a given table |
| [`getcompactionthroughput`](#getcompactionthroughput) | Print the MiB/s throughput cap for compaction in the system as a rounded number |
| [`getconcurrency`](#getconcurrency) | Get maximum concurrency for processing stages |
| [`getconcurrentcompactors`](#getconcurrentcompactors) | Get the number of concurrent compactors in the system. |
| [`getconcurrentviewbuilders`](#getconcurrentviewbuilders) | Get the number of concurrent view builders in the system |
| [`getdefaultrf`](#getdefaultrf) | Gets default keyspace replication factor. |
| [`getendpoints`](#getendpoints) | Print the end points that owns the key |
| [`getfullquerylog`](#getfullquerylog) | Print configuration of fql if enabled, otherwise the configuration reflected in cassandra.yaml |
| [`getguardrailsconfig`](#getguardrailsconfig) | Print runtime configuration of guardrails. |
| [`getinterdcstreamthroughput`](#getinterdcstreamthroughput) | Print the throughput cap for inter-datacenter streaming and entire SSTable inter-datacenter streaming in the systemin rounded megabits. For precise number, please, use option -d |
| [`getlogginglevels`](#getlogginglevels) | Get the runtime logging levels |
| [`getmaxhintwindow`](#getmaxhintwindow) | Print the max hint window in ms |
| [`getseeds`](#getseeds) | Get the currently in use seed node IP list excluding the node IP |
| [`getsnapshotthrottle`](#getsnapshotthrottle) | Print the snapshot_links_per_second throttle for snapshot/clearsnapshot |
| [`getsstables`](#getsstables) | Print the sstable filenames that own the key |
| [`getstreamthroughput`](#getstreamthroughput) | Print the throughput cap for streaming and entire SSTable streaming in the system in rounded megabits. For precise number, please, use option -d |
| [`gettimeout`](#gettimeout) | Print the timeout of the given type in ms |
| [`gettraceprobability`](#gettraceprobability) | Print the current trace probability value |
| [`gossipinfo`](#gossipinfo) | Shows the gossip information for the cluster |
| [`help`](#help) | Display help information (nodetool help <command>) |
| [`import`](#import) | Import new SSTables to the system |
| [`info`](#info) | Print node information (uptime, load, ...) |
| [`invalidatecidrpermissionscache`](#invalidatecidrpermissionscache) | Invalidate the cidr permissions cache |
| [`invalidatecountercache`](#invalidatecountercache) | Invalidate the counter cache |
| [`invalidatecredentialscache`](#invalidatecredentialscache) | Invalidate the credentials cache |
| [`invalidatejmxpermissionscache`](#invalidatejmxpermissionscache) | Invalidate the JMX permissions cache |
| [`invalidatekeycache`](#invalidatekeycache) | Invalidate the key cache |
| [`invalidatenetworkpermissionscache`](#invalidatenetworkpermissionscache) | Invalidate the network permissions cache |
| [`invalidatepermissionscache`](#invalidatepermissionscache) | Invalidate the permissions cache |
| [`invalidaterolescache`](#invalidaterolescache) | Invalidate the roles cache |
| [`invalidaterowcache`](#invalidaterowcache) | Invalidate the row cache |
| [`join`](#join) | Join the ring |
| [`listcidrgroups`](#listcidrgroups) | List existing cidr groups |
| [`listpendinghints`](#listpendinghints) | Print all pending hints that this node has |
| [`listsnapshots`](#listsnapshots) | Lists all the snapshots along with the size on disk and true size. True size is the total size of all SSTables which are not backed up to disk. Size on disk is total size of the snapshot on disk. Total TrueDiskSpaceUsed does not make any SSTable deduplication. |
| [`move`](#move) | Move node on the token ring to a new token |
| [`netstats`](#netstats) | Print network information on provided host (connecting node by default) |
| [`pausehandoff`](#pausehandoff) | Pause hints delivery process |
| [`profileload`](#profileload) | Low footprint profiling of activity for a period of time |
| [`proxyhistograms`](#proxyhistograms) | Print statistic histograms for network operations |
| [`rangekeysample`](#rangekeysample) | Shows the sampled keys held across all keyspaces |
| [`rebuild`](#rebuild) | Rebuild data by streaming from other nodes (similarly to bootstrap) |
| [`rebuild_index`](#rebuild_index) | A full rebuild of native secondary indexes for a given table |
| [`recompress_sstables`](#recompress_sstables) | Rewrite sstables (for the requested tables) that have compression configuration different from the current |
| [`refresh`](#refresh) | Load newly placed SSTables to the system without restart **(deprecated)** |
| [`refreshsizeestimates`](#refreshsizeestimates) | Refresh system.size_estimates |
| [`reloadcidrgroupscache`](#reloadcidrgroupscache) | Reload CIDR groups cache with latest entries in cidr_groups table, when CIDR authorizer is enabled |
| [`reloadlocalschema`](#reloadlocalschema) | Reload local node schema from system tables |
| [`reloadseeds`](#reloadseeds) | Reload the seed node list from the seed node provider |
| [`reloadssl`](#reloadssl) | Signals Cassandra to reload SSL certificates |
| [`reloadtriggers`](#reloadtriggers) | Reload trigger classes |
| [`relocatesstables`](#relocatesstables) | Relocates sstables to the correct disk |
| [`removenode`](#removenode) | Show status of current node removal, force completion of pending removal or remove provided ID |
| [`repair`](#repair) | Repair one or more tables |
| [`repair_admin cancel`](#repair_admin-cancel) | cancel an incremental repair session. Use --force to cancel from a node other than the repair coordinator Attempting to cancel FINALIZED or FAILED sessions is an error. |
| [`repair_admin cleanup`](#repair_admin-cleanup) | cleans up pending data from completed sessions. This happens automatically, but the command is provided for situations where it needs to be expedited. Use --force to cancel compactions that are preventing promotion |
| [`repair_admin list`](#repair_admin-list) | list repair sessions |
| [`repair_admin summarize-pending`](#repair_admin-summarize-pending) | report the amount of data marked pending repair for the given token range (or all replicated range if no tokens are provided |
| [`repair_admin summarize-repaired`](#repair_admin-summarize-repaired) | return the most recent repairedAt timestamp for the given token range (or all replicated ranges if no tokens are provided) |
| [`replaybatchlog`](#replaybatchlog) | Kick off batchlog replay and wait for finish |
| [`resetfullquerylog`](#resetfullquerylog) | Stop the full query log and clean files in the configured full query log directory from cassandra.yaml as well as JMX |
| [`resetlocalschema`](#resetlocalschema) | Reset node's local schema and resync |
| [`resumehandoff`](#resumehandoff) | Resume hints delivery process |
| [`ring`](#ring) | Print information about the token ring |
| [`scrub`](#scrub) | Scrub (rebuild sstables for) one or more tables |
| [`setauthcacheconfig`](#setauthcacheconfig) | Set configuration for Auth cache |
| [`setautorepairconfig`](#setautorepairconfig) | sets the autorepair configuration |
| [`setbatchlogreplaythrottle`](#setbatchlogreplaythrottle) | Set batchlog replay throttle in KB per second, or 0 to disable throttling. This will be reduced proportionally to the number of nodes in the cluster. |
| [`setcachecapacity`](#setcachecapacity) | Set global key, row, and counter cache capacities (in MB units) |
| [`setcachekeystosave`](#setcachekeystosave) | Set number of keys saved by each cache for faster post-restart warmup. 0 to disable |
| [`setcolumnindexsize`](#setcolumnindexsize) | Set the granularity of the collation index of rows within a partition in KiB |
| [`setcompactionthreshold`](#setcompactionthreshold) | Set min and max compaction thresholds for a given table |
| [`setcompactionthroughput`](#setcompactionthroughput) | Set the MiB/s throughput cap for compaction in the system, or 0 to disable throttling |
| [`setconcurrency`](#setconcurrency) | Set maximum concurrency for processing stage |
| [`setconcurrentcompactors`](#setconcurrentcompactors) | Set number of concurrent compactors in the system. |
| [`setconcurrentviewbuilders`](#setconcurrentviewbuilders) | Set the number of concurrent view builders in the system |
| [`setdefaultrf`](#setdefaultrf) | Sets default keyspace replication factor. |
| [`setguardrailsconfig`](#setguardrailsconfig) | Modify runtime configuration of guardrails. |
| [`sethintedhandoffthrottlekb`](#sethintedhandoffthrottlekb) | Set hinted handoff throttle in KiB per second, per delivery thread. |
| [`setinterdcstreamthroughput`](#setinterdcstreamthroughput) | Set the throughput cap for inter-datacenter streaming and entire SSTable inter-datacenter streaming in the system, or 0 to disable throttling |
| [`setlogginglevel`](#setlogginglevel) | Set the log level threshold for a given component or class. Will reset to the initial configuration if called with no parameters. |
| [`setmaxhintwindow`](#setmaxhintwindow) | Set the specified max hint window in ms |
| [`setsnapshotthrottle`](#setsnapshotthrottle) | Set the snapshot_links_per_second cap for snapshot and clearsnapshot throttling |
| [`setstreamthroughput`](#setstreamthroughput) | Set throughput cap for streaming and entire SSTable streaming in the system, or 0 to disable throttling |
| [`settimeout`](#settimeout) | Set the specified timeout in ms, or 0 to disable timeout |
| [`settraceprobability`](#settraceprobability) | Sets the probability for tracing any given request to value. 0 disables, 1 enables for all requests, 0 is the default |
| [`sjk`](#sjk) | Run commands of 'Swiss Java Knife'. Run 'nodetool sjk --help' for more information. |
| [`snapshot`](#snapshot) | Take a snapshot of specified keyspaces or a snapshot of the specified table |
| [`sstablerepairedset`](#sstablerepairedset) | Set the repaired state of SSTables for given keyspace/tables |
| [`status`](#status) | Print cluster information (state, load, IDs, ...) |
| [`statusautocompaction`](#statusautocompaction) | status of autocompaction of the given keyspace and table |
| [`statusbackup`](#statusbackup) | Status of incremental backup |
| [`statusbinary`](#statusbinary) | Status of native transport (binary protocol) |
| [`statusgossip`](#statusgossip) | Status of gossip |
| [`statushandoff`](#statushandoff) | Status of storing future hints on the current node |
| [`stop`](#stop) | Stop compaction |
| [`stopdaemon`](#stopdaemon) | Stop cassandra daemon |
| [`tablehistograms`](#tablehistograms) | Print statistic histograms for a given table |
| [`tablestats`](#tablestats) | Print statistics on tables |
| [`toppartitions`](#toppartitions) | Sample and print the most active partitions |
| [`tpstats`](#tpstats) | Print usage statistics of thread pools |
| [`truncatehints`](#truncatehints) | Truncate all hints on the local node, or truncate hints for the endpoint(s) specified. |
| [`updatecidrgroup`](#updatecidrgroup) | Insert/Update a cidr group |
| [`upgradesstables`](#upgradesstables) | Rewrite sstables (for the requested tables) that are not on the current version (thus upgrading them to said current version) |
| [`verify`](#verify) | Verify (check data checksum for) one or more tables |
| [`version`](#version) | Print cassandra version |
| [`viewbuildstatus`](#viewbuildstatus) | Show progress of a materialized view build |

Command groups: `bootstrap` (Monitor/manage node's bootstrap process); `repair_admin` (list and fail incremental repair sessions).

## Commands

<a id="assassinate"></a>

### `assassinate`

Forcefully remove a dead node without re-replicating any data. Use as a last resort if you cannot removenode

```
nodetool [global options] assassinate <ip_address>
```

* **Arguments** `<ip_address>`: IP address of the endpoint to assassinate

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/Assassinate.java` (class `Assassinate`)</sub>

<a id="autorepairstatus"></a>

### `autorepairstatus`

Print autorepair status

```
nodetool [global options] autorepairstatus [options]
```

| Option | Description |
| :--- | :--- |
| `-t`, `--repair-type` | Repair type |

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/AutoRepairStatus.java` (class `AutoRepairStatus`)</sub>

<a id="bootstrap-resume"></a>

### `bootstrap resume`

Resume bootstrap streaming

```
nodetool [global options] bootstrap resume [options]
```

| Option | Description |
| :--- | :--- |
| `-f`, `--force` | Use --force to resume bootstrap regardless of cassandra.reset_bootstrap_progress environment variable. WARNING: This is potentially dangerous, see CASSANDRA-17679 |

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/BootstrapResume.java` (class `BootstrapResume`)</sub>

<a id="checktokenmetadata"></a>

### `checktokenmetadata`

compares the Gossip endpointState and TokenMetadata cache; printing any mismatches found

```
nodetool [global options] checktokenmetadata
```

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/CheckTokenMetadata.java` (class `CheckTokenMetadata`)</sub>

<a id="cidrfilteringstats"></a>

### `cidrfilteringstats`

Print statistics on CIDR filtering

```
nodetool [global options] cidrfilteringstats
```

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/CIDRFilteringStats.java` (class `CIDRFilteringStats`)</sub>

<a id="cleanup"></a>

### `cleanup`

Triggers the immediate cleanup of keys no longer belonging to a node. By default, clean all keyspaces

```
nodetool [global options] cleanup [options] [<keyspace> <tables>...]
```

* **Arguments** `[<keyspace> <tables>...]`: The keyspace followed by one or many tables

| Option | Description |
| :--- | :--- |
| `-j`, `--jobs` | Number of sstables to cleanup simultanously, set to 0 to use all available compaction threads |

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/Cleanup.java` (class `Cleanup`)</sub>

<a id="clearsnapshot"></a>

### `clearsnapshot`

Remove the snapshot with the given name from the given keyspaces

```
nodetool [global options] clearsnapshot [options] [<keyspaces>...] 
```

* **Arguments** `[<keyspaces>...]`: Remove snapshots from the given keyspaces

| Option | Description |
| :--- | :--- |
| `-t` | Remove the snapshot with a given name |
| `--all` | Removes all snapshots |
| `--older-than` | Clear snapshots older than specified time period. |
| `--older-than-timestamp` | Clear snapshots older than specified timestamp. It has to be a string in ISO format, for example '2022-12-03T10:15:30Z' |

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/ClearSnapshot.java` (class `ClearSnapshot`)</sub>

<a id="clientstats"></a>

### `clientstats`

Print information about connected clients

```
nodetool [global options] clientstats [options]
```

| Option | Description |
| :--- | :--- |
| `--all` | Lists all connections |
| `--by-protocol` | Lists most recent client connections by protocol version |
| `--clear-history` | Clear the history of connected clients |
| `--client-options` | Lists all connections and the client options |

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/ClientStats.java` (class `ClientStats`)</sub>

<a id="compact"></a>

### `compact`

Force a (major) compaction on one or more tables or user-defined compaction on given SSTables

```
nodetool [global options] compact [options] [<keyspace> <tables>...] or <SSTable file>...
```

* **Arguments** `[<keyspace> <tables>...] or <SSTable file>...`: The keyspace followed by one or many tables or list of SSTable data files when using --user-defined

| Option | Description |
| :--- | :--- |
| `-s`, `--split-output` | Use -s to not create a single big file |
| `--user-defined` | Use --user-defined to submit listed files for user-defined compaction |
| `-st`, `--start-token` | Use -st to specify a token at which the compaction range starts (inclusive) |
| `-et`, `--end-token` | Use -et to specify a token at which compaction range ends (inclusive) |
| `--partition` | String representation of the partition key |

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/Compact.java` (class `Compact`)</sub>

<a id="compactionhistory"></a>

### `compactionhistory`

Print history of compaction

```
nodetool [global options] compactionhistory [options]
```

| Option | Description |
| :--- | :--- |
| `-F`, `--format` | Output format (json, yaml) |

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/CompactionHistory.java` (class `CompactionHistory`)</sub>

<a id="compactionstats"></a>

### `compactionstats`

Print statistics on compactions

```
nodetool [global options] compactionstats [options]
```

| Option | Description |
| :--- | :--- |
| `-H`, `--human-readable` | Display bytes in human readable form, i.e. KiB, MiB, GiB, TiB |
| `-V`, `--vtable` | Display fields matching vtable output |

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/CompactionStats.java` (class `CompactionStats`)</sub>

<a id="datapaths"></a>

### `datapaths`

Print all directories where data of tables are stored

```
nodetool [global options] datapaths [options] [<keyspace.table>...]
```

* **Arguments** `[<keyspace.table>...]`: List of table (or keyspace) names

| Option | Description |
| :--- | :--- |
| `-F`, `--format` | Output format (json, yaml) |

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/DataPaths.java` (class `DataPaths`)</sub>

<a id="decommission"></a>

### `decommission`

Decommission the *node I am connecting to*

```
nodetool [global options] decommission [options]
```

| Option | Description |
| :--- | :--- |
| `-f`, `--force` | Force decommission of this node even when it reduces the number of replicas to below configured RF |

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/Decommission.java` (class `Decommission`)</sub>

<a id="describecluster"></a>

### `describecluster`

Print the name, snitch, partitioner and schema version of a cluster

```
nodetool [global options] describecluster
```

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/DescribeCluster.java` (class `DescribeCluster`)</sub>

<a id="describering"></a>

### `describering`

Shows the token ranges info of a given keyspace

```
nodetool [global options] describering
```

* **Arguments** ``: The keyspace name

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/DescribeRing.java` (class `DescribeRing`)</sub>

<a id="disableauditlog"></a>

### `disableauditlog`

Disable the audit log

```
nodetool [global options] disableauditlog
```

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/DisableAuditLog.java` (class `DisableAuditLog`)</sub>

<a id="disableautocompaction"></a>

### `disableautocompaction`

Disable autocompaction for the given keyspace and table

```
nodetool [global options] disableautocompaction [<keyspace> <tables>...]
```

* **Arguments** `[<keyspace> <tables>...]`: The keyspace followed by one or many tables

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/DisableAutoCompaction.java` (class `DisableAutoCompaction`)</sub>

<a id="disablebackup"></a>

### `disablebackup`

Disable incremental backup

```
nodetool [global options] disablebackup
```

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/DisableBackup.java` (class `DisableBackup`)</sub>

<a id="disablebinary"></a>

### `disablebinary`

Disable native transport (binary protocol)

```
nodetool [global options] disablebinary [options]
```

| Option | Description |
| :--- | :--- |
| `-f`, `--force` | Use -f to interrupt client requests that have already started |

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/DisableBinary.java` (class `DisableBinary`)</sub>

<a id="disablefullquerylog"></a>

### `disablefullquerylog`

Disable the full query log

```
nodetool [global options] disablefullquerylog
```

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/DisableFullQueryLog.java` (class `DisableFullQueryLog`)</sub>

<a id="disablegossip"></a>

### `disablegossip`

Disable gossip (effectively marking the node down)

```
nodetool [global options] disablegossip
```

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/DisableGossip.java` (class `DisableGossip`)</sub>

<a id="disablehandoff"></a>

### `disablehandoff`

Disable storing hinted handoffs

```
nodetool [global options] disablehandoff
```

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/DisableHandoff.java` (class `DisableHandoff`)</sub>

<a id="disablehintsfordc"></a>

### `disablehintsfordc`

Disable hints for a data center

```
nodetool [global options] disablehintsfordc <datacenter>
```

* **Arguments** `<datacenter>`: The data center to disable

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/DisableHintsForDC.java` (class `DisableHintsForDC`)</sub>

<a id="disableoldprotocolversions"></a>

### `disableoldprotocolversions`

Disable old protocol versions

```
nodetool [global options] disableoldprotocolversions
```

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/DisableOldProtocolVersions.java` (class `DisableOldProtocolVersions`)</sub>

<a id="drain"></a>

### `drain`

Drain the node (stop accepting writes and flush all tables)

```
nodetool [global options] drain
```

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/Drain.java` (class `Drain`)</sub>

<a id="dropcidrgroup"></a>

### `dropcidrgroup`

Drop an existing cidr group

```
nodetool [global options] dropcidrgroup <cidrGroup>
```

* **Arguments** `<cidrGroup>`: Requires a cidr group name

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/DropCIDRGroup.java` (class `DropCIDRGroup`)</sub>

<a id="enableauditlog"></a>

### `enableauditlog`

Enable the audit log

```
nodetool [global options] enableauditlog [options]
```

| Option | Description |
| :--- | :--- |
| `--logger` | Logger name to be used for AuditLogging. Default BinAuditLogger. If not set the value from cassandra.yaml will be used |
| `--included-keyspaces` | Comma separated list of keyspaces to be included for audit log. If not set the value from cassandra.yaml will be used |
| `--excluded-keyspaces` | Comma separated list of keyspaces to be excluded for audit log. If not set the value from cassandra.yaml will be used |
| `--included-categories` | Comma separated list of Audit Log Categories to be included for audit log. If not set the value from cassandra.yaml will be used |
| `--excluded-categories` | Comma separated list of Audit Log Categories to be excluded for audit log. If not set the value from cassandra.yaml will be used |
| `--included-users` | Comma separated list of users to be included for audit log. If not set the value from cassandra.yaml will be used |
| `--excluded-users` | Comma separated list of users to be excluded for audit log. If not set the value from cassandra.yaml will be used |
| `--roll-cycle` | How often to roll the log file (MINUTELY, HOURLY, DAILY). |
| `--blocking` | If the queue is full whether to block producers or drop samples [true\|false]. |
| `--max-queue-weight` | Maximum number of bytes of query data to queue to disk before blocking or dropping samples. |
| `--max-log-size` | How many bytes of log data to store before dropping segments. Might not be respected if a log file hasn't rolled so it can be deleted. |
| `--archive-command` | Command that will handle archiving rolled audit log files. Format is "/path/to/script.sh %path" where %path will be replaced with the file to archive Enable this by setting the audit_logging_options.allow_nodetool_archive_command: true in the config. |
| `--max-archive-retries` | Max number of archive retries. |

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/EnableAuditLog.java` (class `EnableAuditLog`)</sub>

<a id="enableautocompaction"></a>

### `enableautocompaction`

Enable autocompaction for the given keyspace and table

```
nodetool [global options] enableautocompaction [<keyspace> <tables>...]
```

* **Arguments** `[<keyspace> <tables>...]`: The keyspace followed by one or many tables

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/EnableAutoCompaction.java` (class `EnableAutoCompaction`)</sub>

<a id="enablebackup"></a>

### `enablebackup`

Enable incremental backup

```
nodetool [global options] enablebackup
```

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/EnableBackup.java` (class `EnableBackup`)</sub>

<a id="enablebinary"></a>

### `enablebinary`

Reenable native transport (binary protocol)

```
nodetool [global options] enablebinary
```

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/EnableBinary.java` (class `EnableBinary`)</sub>

<a id="enablefullquerylog"></a>

### `enablefullquerylog`

Enable full query logging, defaults for the options are configured in cassandra.yaml

```
nodetool [global options] enablefullquerylog [options]
```

| Option | Description |
| :--- | :--- |
| `--roll-cycle` | How often to roll the log file (MINUTELY, HOURLY, DAILY). |
| `--blocking` | If the queue is full whether to block producers or drop samples [true\|false]. |
| `--max-queue-weight` | Maximum number of bytes of query data to queue to disk before blocking or dropping samples. |
| `--max-log-size` | How many bytes of log data to store before dropping segments. Might not be respected if a log file hasn't rolled so it can be deleted. |
| `--path` | Path to store the full query log at. Will have it's contents recursively deleted. |
| `--archive-command` | Command that will handle archiving rolled full query log files. Format is "/path/to/script.sh %path" where %path will be replaced with the file to archive Enable this by setting the full_query_logging_options.allow_nodetool_archive_command: true in the config. |
| `--max-archive-retries` | Max number of archive retries. |

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/EnableFullQueryLog.java` (class `EnableFullQueryLog`)</sub>

<a id="enablegossip"></a>

### `enablegossip`

Reenable gossip

```
nodetool [global options] enablegossip
```

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/EnableGossip.java` (class `EnableGossip`)</sub>

<a id="enablehandoff"></a>

### `enablehandoff`

Reenable future hints storing on the current node

```
nodetool [global options] enablehandoff
```

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/EnableHandoff.java` (class `EnableHandoff`)</sub>

<a id="enablehintsfordc"></a>

### `enablehintsfordc`

Enable hints for a data center that was previsouly disabled

```
nodetool [global options] enablehintsfordc <datacenter>
```

* **Arguments** `<datacenter>`: The data center to enable

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/EnableHintsForDC.java` (class `EnableHintsForDC`)</sub>

<a id="enableoldprotocolversions"></a>

### `enableoldprotocolversions`

Enable old protocol versions

```
nodetool [global options] enableoldprotocolversions
```

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/EnableOldProtocolVersions.java` (class `EnableOldProtocolVersions`)</sub>

<a id="failuredetector"></a>

### `failuredetector`

Shows the failure detector information for the cluster

```
nodetool [global options] failuredetector
```

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/FailureDetectorInfo.java` (class `FailureDetectorInfo`)</sub>

<a id="flush"></a>

### `flush`

Flush one or more tables

```
nodetool [global options] flush [<keyspace> <tables>...]
```

* **Arguments** `[<keyspace> <tables>...]`: The keyspace followed by one or many tables

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/Flush.java` (class `Flush`)</sub>

<a id="forcecompact"></a>

### `forcecompact`

Force a (major) compaction on a table

```
nodetool [global options] forcecompact [<keyspace> <table> <keys>]
```

* **Arguments** `[<keyspace> <table> <keys>]`: The keyspace, table, and a list of partition keys ignoring the gc_grace_seconds

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/ForceCompact.java` (class `ForceCompact`)</sub>

<a id="garbagecollect"></a>

### `garbagecollect`

Remove deleted data from one or more tables

```
nodetool [global options] garbagecollect [options] [<keyspace> <tables>...]
```

* **Arguments** `[<keyspace> <tables>...]`: The keyspace followed by one or many tables

| Option | Description |
| :--- | :--- |
| `-g`, `--granularity` | Granularity of garbage removal. ROW (default) removes deleted partitions and rows, CELL also removes overwritten or deleted cells. |
| `-j`, `--jobs` | Number of sstables to cleanup simultanously, set to 0 to use all available compaction threads. Defaults to 1 so that collections of newer tables can see the data is deleted and also remove tombstones. |

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/GarbageCollect.java` (class `GarbageCollect`)</sub>

<a id="gcstats"></a>

### `gcstats`

Print GC Statistics

```
nodetool [global options] gcstats
```

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/GcStats.java` (class `GcStats`)</sub>

<a id="getauditlog"></a>

### `getauditlog`

Print configuration of audit log if enabled, otherwise the configuration reflected in cassandra.yaml

```
nodetool [global options] getauditlog
```

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/GetAuditLog.java` (class `GetAuditLog`)</sub>

<a id="getauthcacheconfig"></a>

### `getauthcacheconfig`

Get configuration of Auth cache

```
nodetool [global options] getauthcacheconfig [options]
```

| Option | Description |
| :--- | :--- |
| `--cache-name` | Name of Auth cache (required) **(required)** |

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/GetAuthCacheConfig.java` (class `GetAuthCacheConfig`)</sub>

<a id="getautorepairconfig"></a>

### `getautorepairconfig`

Print autorepair configurations

```
nodetool [global options] getautorepairconfig
```

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/GetAutoRepairConfig.java` (class `GetAutoRepairConfig`)</sub>

<a id="getbatchlogreplaythrottle"></a>

### `getbatchlogreplaythrottle`

Print batchlog replay throttle in KB/s. This is reduced proportionally to the number of nodes in the cluster.

```
nodetool [global options] getbatchlogreplaythrottle
```

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/GetBatchlogReplayTrottle.java` (class `GetBatchlogReplayTrottle`)</sub>

<a id="getcidrgroupsofip"></a>

### `getcidrgroupsofip`

Print CIDR groups associated with given IP

```
nodetool [global options] getcidrgroupsofip <IP address>
```

* **Arguments** `<IP address>`: Requires IP address as a string

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/GetCIDRGroupsOfIP.java` (class `GetCIDRGroupsOfIP`)</sub>

<a id="getcolumnindexsize"></a>

### `getcolumnindexsize`

Print the granularity of the collation index of rows within a partition in KiB

```
nodetool [global options] getcolumnindexsize
```

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/GetColumnIndexSize.java` (class `GetColumnIndexSize`)</sub>

<a id="getcompactionthreshold"></a>

### `getcompactionthreshold`

Print min and max compaction thresholds for a given table

```
nodetool [global options] getcompactionthreshold <keyspace> <table>
```

* **Arguments** `<keyspace> <table>`: The keyspace with a table

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/GetCompactionThreshold.java` (class `GetCompactionThreshold`)</sub>

<a id="getcompactionthroughput"></a>

### `getcompactionthroughput`

Print the MiB/s throughput cap for compaction in the system as a rounded number

```
nodetool [global options] getcompactionthroughput [options]
```

| Option | Description |
| :--- | :--- |
| `-d`, `--precise-mib` | Print the MiB/s throughput cap for compaction in the system as a precise number (double) |

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/GetCompactionThroughput.java` (class `GetCompactionThroughput`)</sub>

<a id="getconcurrency"></a>

### `getconcurrency`

Get maximum concurrency for processing stages

```
nodetool [global options] getconcurrency [stage-names]
```

* **Arguments** `[stage-names]`: optional list of stage names, otherwise display all stages

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/GetConcurrency.java` (class `GetConcurrency`)</sub>

<a id="getconcurrentcompactors"></a>

### `getconcurrentcompactors`

Get the number of concurrent compactors in the system.

```
nodetool [global options] getconcurrentcompactors
```

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/GetConcurrentCompactors.java` (class `GetConcurrentCompactors`)</sub>

<a id="getconcurrentviewbuilders"></a>

### `getconcurrentviewbuilders`

Get the number of concurrent view builders in the system

```
nodetool [global options] getconcurrentviewbuilders
```

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/GetConcurrentViewBuilders.java` (class `GetConcurrentViewBuilders`)</sub>

<a id="getdefaultrf"></a>

### `getdefaultrf`

Gets default keyspace replication factor.

```
nodetool [global options] getdefaultrf
```

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/GetDefaultKeyspaceRF.java` (class `GetDefaultKeyspaceRF`)</sub>

<a id="getendpoints"></a>

### `getendpoints`

Print the end points that owns the key

```
nodetool [global options] getendpoints <keyspace> <table> <key>
```

* **Arguments** `<keyspace> <table> <key>`: The keyspace, the table, and the partition key for which we need to find the endpoint

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/GetEndpoints.java` (class `GetEndpoints`)</sub>

<a id="getfullquerylog"></a>

### `getfullquerylog`

Print configuration of fql if enabled, otherwise the configuration reflected in cassandra.yaml

```
nodetool [global options] getfullquerylog
```

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/GetFullQueryLog.java` (class `GetFullQueryLog`)</sub>

<a id="getguardrailsconfig"></a>

### `getguardrailsconfig`

Print runtime configuration of guardrails.

```
nodetool [global options] getguardrailsconfig [options]
```

* **Arguments** ``: Specific name of a guardrail to get configuration of.

| Option | Description |
| :--- | :--- |
| `--category`, `-c` | Category of guardrails to filter, can be one of 'values', 'thresholds', 'flags', 'others'. |
| `--expand` | Expand all guardrail names so they reflect their counterparts in cassandra.yaml |

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/GuardrailsConfigCommand.java` (class `GetGuardrailsConfig`)</sub>

<a id="getinterdcstreamthroughput"></a>

### `getinterdcstreamthroughput`

Print the throughput cap for inter-datacenter streaming and entire SSTable inter-datacenter streaming in the systemin rounded megabits. For precise number, please, use option -d

```
nodetool [global options] getinterdcstreamthroughput [options]
```

| Option | Description |
| :--- | :--- |
| `-e`, `--entire-sstable-throughput` | Print entire SSTable streaming throughput in MiB/s |
| `-m`, `--mib` | Print the throughput cap for inter-datacenter streaming in MiB/s |
| `-d`, `--precise-mbit` | Print the throughput cap for inter-datacenter streaming in precise Mbits (double) |

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/GetInterDCStreamThroughput.java` (class `GetInterDCStreamThroughput`)</sub>

<a id="getlogginglevels"></a>

### `getlogginglevels`

Get the runtime logging levels

```
nodetool [global options] getlogginglevels
```

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/GetLoggingLevels.java` (class `GetLoggingLevels`)</sub>

<a id="getmaxhintwindow"></a>

### `getmaxhintwindow`

Print the max hint window in ms

```
nodetool [global options] getmaxhintwindow
```

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/GetMaxHintWindow.java` (class `GetMaxHintWindow`)</sub>

<a id="getseeds"></a>

### `getseeds`

Get the currently in use seed node IP list excluding the node IP

```
nodetool [global options] getseeds
```

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/GetSeeds.java` (class `GetSeeds`)</sub>

<a id="getsnapshotthrottle"></a>

### `getsnapshotthrottle`

Print the snapshot_links_per_second throttle for snapshot/clearsnapshot

```
nodetool [global options] getsnapshotthrottle
```

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/GetSnapshotThrottle.java` (class `GetSnapshotThrottle`)</sub>

<a id="getsstables"></a>

### `getsstables`

Print the sstable filenames that own the key

```
nodetool [global options] getsstables [options] <keyspace> <cfname> <key>
```

* **Arguments** `<keyspace> <cfname> <key>`: The keyspace, the column family, and the key

| Option | Description |
| :--- | :--- |
| `-hf`, `--hex-format` | Specify the key in hexadecimal string format |
| `-l`, `--show-levels` | If the table is using leveled compaction the level of each sstable will be included in the output (Default: false) |

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/GetSSTables.java` (class `GetSSTables`)</sub>

<a id="getstreamthroughput"></a>

### `getstreamthroughput`

Print the throughput cap for streaming and entire SSTable streaming in the system in rounded megabits. For precise number, please, use option -d

```
nodetool [global options] getstreamthroughput [options]
```

| Option | Description |
| :--- | :--- |
| `-e`, `--entire-sstable-throughput` | Print entire SSTable streaming throughput in MiB/s |
| `-m`, `--mib` | Print the throughput cap for streaming in MiB/s |
| `-d`, `--precise-mbit` | Print the throughput cap for streaming in precise Mbits (double) |

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/GetStreamThroughput.java` (class `GetStreamThroughput`)</sub>

<a id="gettimeout"></a>

### `gettimeout`

Print the timeout of the given type in ms

```
nodetool [global options] gettimeout <timeout_type>
```

* **Arguments** `<timeout_type>`: The timeout type, one of ()

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/GetTimeout.java` (class `GetTimeout`)</sub>

<a id="gettraceprobability"></a>

### `gettraceprobability`

Print the current trace probability value

```
nodetool [global options] gettraceprobability
```

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/GetTraceProbability.java` (class `GetTraceProbability`)</sub>

<a id="gossipinfo"></a>

### `gossipinfo`

Shows the gossip information for the cluster

```
nodetool [global options] gossipinfo [options]
```

| Option | Description |
| :--- | :--- |
| `-r`, `--resolve-ip` | Show node domain names instead of IPs |

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/GossipInfo.java` (class `GossipInfo`)</sub>

<a id="help"></a>

### `help`

Display help information (nodetool help <command>)

```
nodetool [global options] help
```

<sub>Source: `src/java/org/apache/cassandra/tools/NodeTool.java` (class `CassHelp`)</sub>

<a id="import"></a>

### `import`

Import new SSTables to the system

```
nodetool [global options] import [options] <keyspace> <table> <directory> ...
```

* **Arguments** `<keyspace> <table> <directory> ...`: The keyspace, table name and directories to import sstables from

| Option | Description |
| :--- | :--- |
| `-l`, `--keep-level` | Keep the level on the new sstables |
| `-r`, `--keep-repaired` | Keep any repaired information from the sstables |
| `-v`, `--no-verify` | Don't verify new sstables |
| `-t`, `--no-tokens` | Don't verify that all tokens in the new sstable are owned by the current node |
| `-c`, `--no-invalidate-caches` | Don't invalidate the row cache when importing |
| `-q`, `--quick` | Do a quick import without verifying sstables, clearing row cache or checking in which data directory to put the file |
| `-e`, `--extended-verify` | Run an extended verify, verifying all values in the new sstables |
| `-cd`, `--copy-data` | Copy data from source directories instead of moving them |
| `-ri`, `--require-index-components` | Require existing index components for SSTables with attached indexes |
| `-niv`, `--no-index-validation` | Skip SSTable-attached index checksum validation |

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/Import.java` (class `Import`)</sub>

<a id="info"></a>

### `info`

Print node information (uptime, load, ...)

```
nodetool [global options] info [options]
```

| Option | Description |
| :--- | :--- |
| `-T`, `--tokens` | Display all tokens |
| `-O`, `--out-of-range-ops` | Display per-keyspace counts of operations for invalid tokens |

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/Info.java` (class `Info`)</sub>

<a id="invalidatecidrpermissionscache"></a>

### `invalidatecidrpermissionscache`

Invalidate the cidr permissions cache

```
nodetool [global options] invalidatecidrpermissionscache [<role>...]
```

* **Arguments** `[<role>...]`: List of roles to invalidate. By default, all roles

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/InvalidateCIDRPermissionsCache.java` (class `InvalidateCIDRPermissionsCache`)</sub>

<a id="invalidatecountercache"></a>

### `invalidatecountercache`

Invalidate the counter cache

```
nodetool [global options] invalidatecountercache
```

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/InvalidateCounterCache.java` (class `InvalidateCounterCache`)</sub>

<a id="invalidatecredentialscache"></a>

### `invalidatecredentialscache`

Invalidate the credentials cache

```
nodetool [global options] invalidatecredentialscache [<role>...]
```

* **Arguments** `[<role>...]`: List of roles to invalidate. By default, all roles

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/InvalidateCredentialsCache.java` (class `InvalidateCredentialsCache`)</sub>

<a id="invalidatejmxpermissionscache"></a>

### `invalidatejmxpermissionscache`

Invalidate the JMX permissions cache

```
nodetool [global options] invalidatejmxpermissionscache [<role>...]
```

* **Arguments** `[<role>...]`: List of roles to invalidate. By default, all roles

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/InvalidateJmxPermissionsCache.java` (class `InvalidateJmxPermissionsCache`)</sub>

<a id="invalidatekeycache"></a>

### `invalidatekeycache`

Invalidate the key cache

```
nodetool [global options] invalidatekeycache
```

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/InvalidateKeyCache.java` (class `InvalidateKeyCache`)</sub>

<a id="invalidatenetworkpermissionscache"></a>

### `invalidatenetworkpermissionscache`

Invalidate the network permissions cache

```
nodetool [global options] invalidatenetworkpermissionscache [<role>...]
```

* **Arguments** `[<role>...]`: List of roles to invalidate. By default, all roles

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/InvalidateNetworkPermissionsCache.java` (class `InvalidateNetworkPermissionsCache`)</sub>

<a id="invalidatepermissionscache"></a>

### `invalidatepermissionscache`

Invalidate the permissions cache

```
nodetool [global options] invalidatepermissionscache [options] [<role>]
```

* **Arguments** `[<role>]`: A role for which permissions to specified resources need to be invalidated

| Option | Description |
| :--- | :--- |
| `--all-keyspaces` | Invalidate permissions for 'ALL KEYSPACES' |
| `--keyspace` | Keyspace to invalidate permissions for |
| `--all-tables` | Invalidate permissions for 'ALL TABLES' |
| `--table` | Table to invalidate permissions for (you must specify --keyspace for using this option) |
| `--all-roles` | Invalidate permissions for 'ALL ROLES' |
| `--role` | Role to invalidate permissions for |
| `--all-functions` | Invalidate permissions for 'ALL FUNCTIONS' |
| `--functions-in-keyspace` | Keyspace to invalidate permissions for |
| `--function` | Function to invalidate permissions for (you must specify --functions-in-keyspace for using this option; function format: name[arg1^..^agrN], for example: foo[Int32Type^DoubleType]) |
| `--all-mbeans` | Invalidate permissions for 'ALL MBEANS' |
| `--mbean` | MBean to invalidate permissions for |

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/InvalidatePermissionsCache.java` (class `InvalidatePermissionsCache`)</sub>

<a id="invalidaterolescache"></a>

### `invalidaterolescache`

Invalidate the roles cache

```
nodetool [global options] invalidaterolescache [<role>...]
```

* **Arguments** `[<role>...]`: List of roles to invalidate. By default, all roles

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/InvalidateRolesCache.java` (class `InvalidateRolesCache`)</sub>

<a id="invalidaterowcache"></a>

### `invalidaterowcache`

Invalidate the row cache

```
nodetool [global options] invalidaterowcache
```

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/InvalidateRowCache.java` (class `InvalidateRowCache`)</sub>

<a id="join"></a>

### `join`

Join the ring

```
nodetool [global options] join
```

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/Join.java` (class `Join`)</sub>

<a id="listcidrgroups"></a>

### `listcidrgroups`

List existing cidr groups

```
nodetool [global options] listcidrgroups [<cidrGroup>]
```

* **Arguments** `[<cidrGroup>]`: LIST operation can be invoked with or without cidr group name

<sub>Source: `src/java/org/apache/cassandra/tools/ListCIDRGroups.java` (class `ListCIDRGroups`)</sub>

<a id="listpendinghints"></a>

### `listpendinghints`

Print all pending hints that this node has

```
nodetool [global options] listpendinghints
```

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/ListPendingHints.java` (class `ListPendingHints`)</sub>

<a id="listsnapshots"></a>

### `listsnapshots`

Lists all the snapshots along with the size on disk and true size. True size is the total size of all SSTables which are not backed up to disk. Size on disk is total size of the snapshot on disk. Total TrueDiskSpaceUsed does not make any SSTable deduplication.

```
nodetool [global options] listsnapshots [options]
```

| Option | Description |
| :--- | :--- |
| `-nt`, `--no-ttl` | Skip snapshots with TTL |
| `-e`, `--ephemeral` | Include ephememeral snapshots |

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/ListSnapshots.java` (class `ListSnapshots`)</sub>

<a id="move"></a>

### `move`

Move node on the token ring to a new token

```
nodetool [global options] move <new token>
```

* **Arguments** `<new token>`: The new token.

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/Move.java` (class `Move`)</sub>

<a id="netstats"></a>

### `netstats`

Print network information on provided host (connecting node by default)

```
nodetool [global options] netstats [options]
```

| Option | Description |
| :--- | :--- |
| `-H`, `--human-readable` | Display bytes in human readable form, i.e. KiB, MiB, GiB, TiB |

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/NetStats.java` (class `NetStats`)</sub>

<a id="pausehandoff"></a>

### `pausehandoff`

Pause hints delivery process

```
nodetool [global options] pausehandoff
```

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/PauseHandoff.java` (class `PauseHandoff`)</sub>

<a id="profileload"></a>

### `profileload`

Low footprint profiling of activity for a period of time

```
nodetool [global options] profileload [options] <keyspace> <cfname> <duration>
```

* **Arguments** `<keyspace> <cfname> <duration>`: The keyspace, column family name, and duration in milliseconds (Default: 10000)

| Option | Description |
| :--- | :--- |
| `-s` | Capacity of the sampler, higher for more accuracy (Default: 256) |
| `-k` | Number of the top samples to list (Default: 10) |
| `-a` | Comma separated list of samplers to use (Default: all) |
| `-i`, `--interval` | Schedule a new job that samples every interval milliseconds (Default: disabled) in the background |
| `-t`, `--stop` | Stop the scheduled sampling job identified by <keyspace> and <cfname>. Jobs are stopped until the last schedules complete. |
| `-l`, `--list` | List the scheduled sampling jobs |

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/ProfileLoad.java` (class `ProfileLoad`)</sub>

<a id="proxyhistograms"></a>

### `proxyhistograms`

Print statistic histograms for network operations

```
nodetool [global options] proxyhistograms
```

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/ProxyHistograms.java` (class `ProxyHistograms`)</sub>

<a id="rangekeysample"></a>

### `rangekeysample`

Shows the sampled keys held across all keyspaces

```
nodetool [global options] rangekeysample
```

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/RangeKeySample.java` (class `RangeKeySample`)</sub>

<a id="rebuild"></a>

### `rebuild`

Rebuild data by streaming from other nodes (similarly to bootstrap)

```
nodetool [global options] rebuild [options] <src-dc-name>
```

* **Arguments** `<src-dc-name>`: Name of DC from which to select sources for streaming. By default, pick any DC (except local DC when --exclude-local-dc is set)

| Option | Description |
| :--- | :--- |
| `-ks`, `--keyspace` | Use -ks to rebuild specific keyspace. |
| `-ts`, `--tokens` | Use -ts to rebuild specific token ranges, in the format of "(start_token_1,end_token_1],(start_token_2,end_token_2],...(start_token_n,end_token_n]". |
| `-s`, `--sources` | Use -s to specify hosts that this node should stream from when -ts is used. Multiple hosts should be separated using commas (e.g. 127.0.0.1,127.0.0.2,...) |
| `--exclude-local-dc` | Use --exclude-local-dc to exclude nodes in local data center as source for streaming. |

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/Rebuild.java` (class `Rebuild`)</sub>

<a id="rebuild_index"></a>

### `rebuild_index`

A full rebuild of native secondary indexes for a given table

```
nodetool [global options] rebuild_index <keyspace> <table> <indexName...>
```

* **Arguments** `<keyspace> <table> <indexName...>`: The keyspace and table name followed by a list of index names

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/RebuildIndex.java` (class `RebuildIndex`)</sub>

<a id="recompress_sstables"></a>

### `recompress_sstables`

Rewrite sstables (for the requested tables) that have compression configuration different from the current

```
nodetool [global options] recompress_sstables [options] [<keyspace> <tables>...]
```

* **Arguments** `[<keyspace> <tables>...]`: The keyspace followed by one or many tables

| Option | Description |
| :--- | :--- |
| `-j`, `--jobs` | Number of sstables to upgrade simultanously, set to 0 to use all available compaction threads |

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/RecompressSSTables.java` (class `RecompressSSTables`)</sub>

<a id="refresh"></a>

### `refresh`

> [!WARNING]
> The source marks this command as deprecated.

Load newly placed SSTables to the system without restart

```
nodetool [global options] refresh <keyspace> <table>
```

* **Arguments** `<keyspace> <table>`: The keyspace and table name

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/Refresh.java` (class `Refresh`)</sub>

<a id="refreshsizeestimates"></a>

### `refreshsizeestimates`

Refresh system.size_estimates

```
nodetool [global options] refreshsizeestimates
```

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/RefreshSizeEstimates.java` (class `RefreshSizeEstimates`)</sub>

<a id="reloadcidrgroupscache"></a>

### `reloadcidrgroupscache`

Reload CIDR groups cache with latest entries in cidr_groups table, when CIDR authorizer is enabled

```
nodetool [global options] reloadcidrgroupscache
```

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/ReloadCIDRGroupsCache.java` (class `ReloadCIDRGroupsCache`)</sub>

<a id="reloadlocalschema"></a>

### `reloadlocalschema`

Reload local node schema from system tables

```
nodetool [global options] reloadlocalschema
```

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/ReloadLocalSchema.java` (class `ReloadLocalSchema`)</sub>

<a id="reloadseeds"></a>

### `reloadseeds`

Reload the seed node list from the seed node provider

```
nodetool [global options] reloadseeds
```

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/ReloadSeeds.java` (class `ReloadSeeds`)</sub>

<a id="reloadssl"></a>

### `reloadssl`

Signals Cassandra to reload SSL certificates

```
nodetool [global options] reloadssl
```

<sub>Source: `src/java/org/apache/cassandra/tools/ReloadSslCertificates.java` (class `ReloadSslCertificates`)</sub>

<a id="reloadtriggers"></a>

### `reloadtriggers`

Reload trigger classes

```
nodetool [global options] reloadtriggers
```

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/ReloadTriggers.java` (class `ReloadTriggers`)</sub>

<a id="relocatesstables"></a>

### `relocatesstables`

Relocates sstables to the correct disk

```
nodetool [global options] relocatesstables [options] <keyspace> <table>
```

* **Arguments** `<keyspace> <table>`: The keyspace and table name

| Option | Description |
| :--- | :--- |
| `-j`, `--jobs` | Number of sstables to relocate simultanously, set to 0 to use all available compaction threads |

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/RelocateSSTables.java` (class `RelocateSSTables`)</sub>

<a id="removenode"></a>

### `removenode`

Show status of current node removal, force completion of pending removal or remove provided ID

```
nodetool [global options] removenode <status>|<force>|<ID>
```

* **Arguments** `<status>\|<force>\|<ID>`: Show status of current node removal, force completion of pending removal, or remove provided ID

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/RemoveNode.java` (class `RemoveNode`)</sub>

<a id="repair"></a>

### `repair`

Repair one or more tables

```
nodetool [global options] repair [options] [<keyspace> <tables>...]
```

* **Arguments** `[<keyspace> <tables>...]`: The keyspace followed by one or many tables

| Option | Description |
| :--- | :--- |
| `-seq`, `--sequential` | Use -seq to carry out a sequential repair |
| `-dcpar`, `--dc-parallel` | Use -dcpar to repair data centers in parallel. |
| `-local`, `--in-local-dc` | Use -local to only repair against nodes in the same datacenter |
| `-dc`, `--in-dc` | Use -dc to repair specific datacenters |
| `-hosts`, `--in-hosts` | Use -hosts to repair specific hosts |
| `-st`, `--start-token` | Use -st to specify a token at which the repair range starts (exclusive) |
| `-et`, `--end-token` | Use -et to specify a token at which repair range ends (inclusive) |
| `-pr`, `--partitioner-range` | Use -pr to repair only the first range returned by the partitioner |
| `-full`, `--full` | Use -full to issue a full repair. |
| `-force`, `--force` | Use -force to filter out down endpoints |
| `-prv`, `--preview` | Determine ranges and amount of data to be streamed, but don't actually perform repair |
| `-vd`, `--validate` | Checks that repaired data is in sync between nodes. Out of sync repaired data indicates a full repair should be run. |
| `-j`, `--job-threads` | Number of threads to run repair jobs. Usually this means number of CFs to repair concurrently. WARNING: increasing this puts more load on repairing nodes, so be careful. (default: 1, max: 4) |
| `-tr`, `--trace` | Use -tr to trace the repair. Traces are logged to system_traces.events. |
| `-pl`, `--pull` | Use --pull to perform a one way repair where data is only streamed from a remote node to this node. |
| `-os`, `--optimise-streams` | Use --optimise-streams to try to reduce the number of streams we do (EXPERIMENTAL, see CASSANDRA-3200). |
| `-skip-paxos`, `--skip-paxos` | If the --skip-paxos flag is included, the paxos repair step is skipped. Paxos repair is also skipped for preview repairs. |
| `-paxos-only`, `--paxos-only` | If the --paxos-only flag is included, no table data is repaired, only paxos operations.. |
| `-iuk`, `--ignore-unreplicated-keyspaces` | Use --ignore-unreplicated-keyspaces to ignore keyspaces which are not replicated, otherwise the repair will fail |

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/Repair.java` (class `Repair`)</sub>

<a id="repair_admin-cancel"></a>

### `repair_admin cancel`

cancel an incremental repair session. Use --force to cancel from a node other than the repair coordinator Attempting to cancel FINALIZED or FAILED sessions is an error.

```
nodetool [global options] repair_admin cancel [options]
```

| Option | Description |
| :--- | :--- |
| `-f`, `--force` | Force a cancellation. |
| `-s`, `--session` | The session to cancel **(required)** |

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/RepairAdmin.java` (class `CancelCmd`)</sub>

<a id="repair_admin-cleanup"></a>

### `repair_admin cleanup`

cleans up pending data from completed sessions. This happens automatically, but the command is provided for situations where it needs to be expedited. Use --force to cancel compactions that are preventing promotion

```
nodetool [global options] repair_admin cleanup [options] [<keyspace> <tables>...]
```

* **Arguments** `[<keyspace> <tables>...]`: The keyspace followed by one or many tables

| Option | Description |
| :--- | :--- |
| `-f`, `--force` | Force a cleanup. |
| `-st`, `--start-token` | Use -st to specify a token at which the repair range starts |
| `-et`, `--end-token` | Use -et to specify a token at which repair range ends |

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/RepairAdmin.java` (class `CleanupDataCmd`)</sub>

<a id="repair_admin-list"></a>

### `repair_admin list`

list repair sessions

```
nodetool [global options] repair_admin list [options]
```

| Option | Description |
| :--- | :--- |
| `-a`, `--all` | include completed and failed sessions |
| `-st`, `--start-token` | Use -st to specify a token at which the repair range starts |
| `-et`, `--end-token` | Use -et to specify a token at which repair range ends |

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/RepairAdmin.java` (class `ListCmd`)</sub>

<a id="repair_admin-summarize-pending"></a>

### `repair_admin summarize-pending`

report the amount of data marked pending repair for the given token range (or all replicated range if no tokens are provided

```
nodetool [global options] repair_admin summarize-pending [options] [<keyspace> <tables>...]
```

* **Arguments** `[<keyspace> <tables>...]`: The keyspace followed by one or many tables

| Option | Description |
| :--- | :--- |
| `-v`, `--verbose` | print additional info |
| `-st`, `--start-token` | Use -st to specify a token at which the repair range starts |
| `-et`, `--end-token` | Use -et to specify a token at which repair range ends |

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/RepairAdmin.java` (class `SummarizePendingCmd`)</sub>

<a id="repair_admin-summarize-repaired"></a>

### `repair_admin summarize-repaired`

return the most recent repairedAt timestamp for the given token range (or all replicated ranges if no tokens are provided)

```
nodetool [global options] repair_admin summarize-repaired [options] [<keyspace> <tables>...]
```

* **Arguments** `[<keyspace> <tables>...]`: The keyspace followed by one or many tables

| Option | Description |
| :--- | :--- |
| `-v`, `--verbose` | print additional info |
| `-st`, `--start-token` | Use -st to specify a token at which the repair range starts |
| `-et`, `--end-token` | Use -et to specify a token at which repair range ends |

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/RepairAdmin.java` (class `SummarizeRepairedCmd`)</sub>

<a id="replaybatchlog"></a>

### `replaybatchlog`

Kick off batchlog replay and wait for finish

```
nodetool [global options] replaybatchlog
```

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/ReplayBatchlog.java` (class `ReplayBatchlog`)</sub>

<a id="resetfullquerylog"></a>

### `resetfullquerylog`

Stop the full query log and clean files in the configured full query log directory from cassandra.yaml as well as JMX

```
nodetool [global options] resetfullquerylog
```

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/ResetFullQueryLog.java` (class `ResetFullQueryLog`)</sub>

<a id="resetlocalschema"></a>

### `resetlocalschema`

Reset node's local schema and resync

```
nodetool [global options] resetlocalschema
```

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/ResetLocalSchema.java` (class `ResetLocalSchema`)</sub>

<a id="resumehandoff"></a>

### `resumehandoff`

Resume hints delivery process

```
nodetool [global options] resumehandoff
```

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/ResumeHandoff.java` (class `ResumeHandoff`)</sub>

<a id="ring"></a>

### `ring`

Print information about the token ring

```
nodetool [global options] ring [options]
```

* **Arguments** ``: Specify a keyspace for accurate ownership information (topology awareness)

| Option | Description |
| :--- | :--- |
| `-r`, `--resolve-ip` | Show node domain names instead of IPs |

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/Ring.java` (class `Ring`)</sub>

<a id="scrub"></a>

### `scrub`

Scrub (rebuild sstables for) one or more tables

```
nodetool [global options] scrub [options] [<keyspace> <tables>...]
```

* **Arguments** `[<keyspace> <tables>...]`: The keyspace followed by one or many tables

| Option | Description |
| :--- | :--- |
| `-ns`, `--no-snapshot` | Scrubbed CFs will be snapshotted first, if disableSnapshot is false. (default false) |
| `-s`, `--skip-corrupted` | Skip corrupted partitions even when scrubbing counter tables. (default false) |
| `-n`, `--no-validate` | Do not validate columns using column validator |
| `-r`, `--reinsert-overflowed-ttl` | StandaloneScrubber.REINSERT_OVERFLOWED_TTL_OPTION_DESCRIPTION |
| `-j`, `--jobs` | Number of sstables to scrub simultanously, set to 0 to use all available compaction threads |

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/Scrub.java` (class `Scrub`)</sub>

<a id="setauthcacheconfig"></a>

### `setauthcacheconfig`

Set configuration for Auth cache

```
nodetool [global options] setauthcacheconfig [options]
```

| Option | Description |
| :--- | :--- |
| `--cache-name` | Name of Auth cache (required) **(required)** |
| `--validity-period` | Validity period in milliseconds |
| `--update-interval` | Update interval in milliseconds |
| `--max-entries` | Max entries |
| `--enable-active-update` | Enable active update |
| `--disable-active-update` | Disable active update |

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/SetAuthCacheConfig.java` (class `SetAuthCacheConfig`)</sub>

<a id="setautorepairconfig"></a>

### `setautorepairconfig`

sets the autorepair configuration

```
nodetool [global options] setautorepairconfig [options] <autorepairparam> <value>
```

* **Arguments** `<autorepairparam> <value>`: autorepair param and value. Possible autorepair parameters are as following: [start_scheduler\|number_of_repair_threads\|min_repair_interval\|sstable_upper_threshold\|enabled\|table_max_repair_time\|priority_hosts\|forcerepair_hosts\|ignore_dcs\|history_clear_delete_hosts_buffer_interval\|repair_primary_token_range_only\|parallel_repair_count\|parallel_repair_percentage\|allow_parallel_replica_repair\|allow_parallel_repair_across_schedules\|materialized_view_repair_enabled\|repair_max_retries\|repair_retry_backoff\|repair_session_timeout\|min_repair_task_duration\|repair_by_keyspace\|mixed_major_version_repair_enabled\|token_range_splitter.<property>]

| Option | Description |
| :--- | :--- |
| `-t`, `--repair-type` | Repair type |

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/SetAutoRepairConfig.java` (class `SetAutoRepairConfig`)</sub>

<a id="setbatchlogreplaythrottle"></a>

### `setbatchlogreplaythrottle`

Set batchlog replay throttle in KB per second, or 0 to disable throttling. This will be reduced proportionally to the number of nodes in the cluster.

```
nodetool [global options] setbatchlogreplaythrottle <value_in_kb_per_sec>
```

* **Arguments** `<value_in_kb_per_sec>`: Value in KiB per second, 0 to disable throttling

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/SetBatchlogReplayThrottle.java` (class `SetBatchlogReplayThrottle`)</sub>

<a id="setcachecapacity"></a>

### `setcachecapacity`

Set global key, row, and counter cache capacities (in MB units)

```
nodetool [global options] setcachecapacity <key-cache-capacity> <row-cache-capacity> <counter-cache-capacity>
```

* **Arguments** `<key-cache-capacity> <row-cache-capacity> <counter-cache-capacity>`: Key cache, row cache, and counter cache (in MB)

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/SetCacheCapacity.java` (class `SetCacheCapacity`)</sub>

<a id="setcachekeystosave"></a>

### `setcachekeystosave`

Set number of keys saved by each cache for faster post-restart warmup. 0 to disable

```
nodetool [global options] setcachekeystosave <key-cache-keys-to-save> <row-cache-keys-to-save> <counter-cache-keys-to-save>
```

* **Arguments** `<key-cache-keys-to-save> <row-cache-keys-to-save> <counter-cache-keys-to-save>`: The number of keys saved by each cache. 0 to disable

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/SetCacheKeysToSave.java` (class `SetCacheKeysToSave`)</sub>

<a id="setcolumnindexsize"></a>

### `setcolumnindexsize`

Set the granularity of the collation index of rows within a partition in KiB

```
nodetool [global options] setcolumnindexsize <value_in_kib>
```

* **Arguments** `<value_in_kib>`: Value in KiB

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/SetColumnIndexSize.java` (class `SetColumnIndexSize`)</sub>

<a id="setcompactionthreshold"></a>

### `setcompactionthreshold`

Set min and max compaction thresholds for a given table

```
nodetool [global options] setcompactionthreshold <keyspace> <table> <minthreshold> <maxthreshold>
```

* **Arguments** `<keyspace> <table> <minthreshold> <maxthreshold>`: The keyspace, the table, min and max threshold

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/SetCompactionThreshold.java` (class `SetCompactionThreshold`)</sub>

<a id="setcompactionthroughput"></a>

### `setcompactionthroughput`

Set the MiB/s throughput cap for compaction in the system, or 0 to disable throttling

```
nodetool [global options] setcompactionthroughput <value_in_mb>
```

* **Arguments** `<value_in_mb>`: Value in MiB, 0 to disable throttling

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/SetCompactionThroughput.java` (class `SetCompactionThroughput`)</sub>

<a id="setconcurrency"></a>

### `setconcurrency`

Set maximum concurrency for processing stage

```
nodetool [global options] setconcurrency <stage-name> <maximum-concurrency> | <stage-name> <core-pool> <maximum-concurrency>
```

* **Arguments** `<stage-name> <maximum-concurrency> \| <stage-name> <core-pool> <maximum-concurrency>`: Set concurrency for processing stage

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/SetConcurrency.java` (class `SetConcurrency`)</sub>

<a id="setconcurrentcompactors"></a>

### `setconcurrentcompactors`

Set number of concurrent compactors in the system.

```
nodetool [global options] setconcurrentcompactors <value>
```

* **Arguments** `<value>`: Number of concurrent compactors, greater than 0.

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/SetConcurrentCompactors.java` (class `SetConcurrentCompactors`)</sub>

<a id="setconcurrentviewbuilders"></a>

### `setconcurrentviewbuilders`

Set the number of concurrent view builders in the system

```
nodetool [global options] setconcurrentviewbuilders <value>
```

* **Arguments** `<value>`: Number of concurrent view builders, greater than 0.

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/SetConcurrentViewBuilders.java` (class `SetConcurrentViewBuilders`)</sub>

<a id="setdefaultrf"></a>

### `setdefaultrf`

Sets default keyspace replication factor.

```
nodetool [global options] setdefaultrf <value>
```

* **Arguments** `<value>`: Default replication factor

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/SetDefaultKeyspaceRF.java` (class `SetDefaultKeyspaceRF`)</sub>

<a id="setguardrailsconfig"></a>

### `setguardrailsconfig`

Modify runtime configuration of guardrails.

```
nodetool [global options] setguardrailsconfig [<setter> <value1> ...]
```

* **Arguments** `[<setter> <value1> ...]`: For flags, possible values are 'true' or 'false'. For thresholds, two values are expected, first for failure, second for warning. For values, enumeration of values expected or one value where multiple items are separated by comma. Setting for thresholds accepting strings and value guardrails are reset by specifying 'null' or '[]' value. For thresholds accepting integers, the reset value is -1.

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/GuardrailsConfigCommand.java` (class `SetGuardrailsConfig`)</sub>

<a id="sethintedhandoffthrottlekb"></a>

### `sethintedhandoffthrottlekb`

Set hinted handoff throttle in KiB per second, per delivery thread.

```
nodetool [global options] sethintedhandoffthrottlekb <value_in_kb_per_sec>
```

* **Arguments** `<value_in_kb_per_sec>`: Value in KiB per second

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/SetHintedHandoffThrottleInKB.java` (class `SetHintedHandoffThrottleInKB`)</sub>

<a id="setinterdcstreamthroughput"></a>

### `setinterdcstreamthroughput`

Set the throughput cap for inter-datacenter streaming and entire SSTable inter-datacenter streaming in the system, or 0 to disable throttling

```
nodetool [global options] setinterdcstreamthroughput [options] <value_in_mb>
```

* **Arguments** `<value_in_mb>`: Value in megabits, 0 to disable throttling

| Option | Description |
| :--- | :--- |
| `-e`, `--entire-sstable-throughput` | Set entire SSTable streaming throughput in MiB/s |
| `-m`, `--mib` | Set streaming throughput in MiB/s |

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/SetInterDCStreamThroughput.java` (class `SetInterDCStreamThroughput`)</sub>

<a id="setlogginglevel"></a>

### `setlogginglevel`

Set the log level threshold for a given component or class. Will reset to the initial configuration if called with no parameters.

```
nodetool [global options] setlogginglevel <component|class> <level>
```

* **Arguments** `<component\|class> <level>`: The component or class to change the level for and the log level threshold to set. Will reset to initial level if omitted. Available components: bootstrap, compaction, repair, streaming, cql, ring

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/SetLoggingLevel.java` (class `SetLoggingLevel`)</sub>

<a id="setmaxhintwindow"></a>

### `setmaxhintwindow`

Set the specified max hint window in ms

```
nodetool [global options] setmaxhintwindow <value_in_ms>
```

* **Arguments** `<value_in_ms>`: Value of maxhintwindow in ms

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/SetMaxHintWindow.java` (class `SetMaxHintWindow`)</sub>

<a id="setsnapshotthrottle"></a>

### `setsnapshotthrottle`

Set the snapshot_links_per_second cap for snapshot and clearsnapshot throttling

```
nodetool [global options] setsnapshotthrottle <throttle>
```

* **Arguments** `<throttle>`: Value represents hardlinks per second ( snapshot_links_per_second ) , 0 to disable throttling

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/SetSnapshotThrottle.java` (class `SetSnapshotThrottle`)</sub>

<a id="setstreamthroughput"></a>

### `setstreamthroughput`

Set throughput cap for streaming and entire SSTable streaming in the system, or 0 to disable throttling

```
nodetool [global options] setstreamthroughput [options] <value_in_mb>
```

* **Arguments** `<value_in_mb>`: Value in megabits, 0 to disable throttling

| Option | Description |
| :--- | :--- |
| `-e`, `--entire-sstable-throughput` | Set entire SSTable streaming throughput in MiB/s |
| `-m`, `--mib` | Set streaming throughput in MiB/s |

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/SetStreamThroughput.java` (class `SetStreamThroughput`)</sub>

<a id="settimeout"></a>

### `settimeout`

Set the specified timeout in ms, or 0 to disable timeout

```
nodetool [global options] settimeout <timeout_type> <timeout_in_ms>
```

* **Arguments** `<timeout_type> <timeout_in_ms>`: Timeout type followed by value in ms (0 disables socket streaming timeout). Type should be one of ()

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/SetTimeout.java` (class `SetTimeout`)</sub>

<a id="settraceprobability"></a>

### `settraceprobability`

Sets the probability for tracing any given request to value. 0 disables, 1 enables for all requests, 0 is the default

```
nodetool [global options] settraceprobability <value>
```

* **Arguments** `<value>`: Trace probability between 0 and 1 (ex: 0.2)

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/SetTraceProbability.java` (class `SetTraceProbability`)</sub>

<a id="sjk"></a>

### `sjk`

Run commands of 'Swiss Java Knife'. Run 'nodetool sjk --help' for more information.

```
nodetool [global options] sjk
```

* **Arguments** ``: Arguments passed as is to 'Swiss Java Knife'.

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/Sjk.java` (class `Sjk`)</sub>

<a id="snapshot"></a>

### `snapshot`

Take a snapshot of specified keyspaces or a snapshot of the specified table

```
nodetool [global options] snapshot [options] [<keyspaces...>]
```

* **Arguments** `[<keyspaces...>]`: List of keyspaces. By default, all keyspaces

| Option | Description |
| :--- | :--- |
| `-cf`, `--column-family`, `--table` | The table name (you must specify one and only one keyspace for using this option) |
| `-t`, `--tag` | The name of the snapshot |
| `-kt`, `--kt-list`, `-kc`, `--kc.list` | The list of Keyspace.table to take snapshot.(you must not specify only keyspace) |
| `-sf`, `--skip-flush` | Do not flush memtables before snapshotting (snapshot will not contain unflushed data) |
| `--ttl` | Specify a TTL of created snapshot |

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/Snapshot.java` (class `Snapshot`)</sub>

<a id="sstablerepairedset"></a>

### `sstablerepairedset`

Set the repaired state of SSTables for given keyspace/tables

```
nodetool [global options] sstablerepairedset [options] [<keyspace> <table...>]
```

* **Arguments** `[<keyspace> <table...>]`: Optional keyspace followed by zero or more tables

| Option | Description |
| :--- | :--- |
| `--really-set` | Really set the repaired state of SSTables. If not set, only print SSTables that would be affected. |
| `--is-repaired` | Set SSTables to repaired state. |
| `--is-unrepaired` | Set SSTables to unrepaired state. |

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/SSTableRepairedSet.java` (class `SSTableRepairedSet`)</sub>

<a id="status"></a>

### `status`

Print cluster information (state, load, IDs, ...)

```
nodetool [global options] status [options] [<keyspace>]
```

* **Arguments** `[<keyspace>]`: The keyspace name

| Option | Description |
| :--- | :--- |
| `-r`, `--resolve-ip` | Show node domain names instead of IPs |

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/Status.java` (class `Status`)</sub>

<a id="statusautocompaction"></a>

### `statusautocompaction`

status of autocompaction of the given keyspace and table

```
nodetool [global options] statusautocompaction [options] [<keyspace> <tables>...]
```

* **Arguments** `[<keyspace> <tables>...]`: The keyspace followed by one or many tables

| Option | Description |
| :--- | :--- |
| `-a`, `--all` | Show auto compaction status for each keyspace/table |

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/StatusAutoCompaction.java` (class `StatusAutoCompaction`)</sub>

<a id="statusbackup"></a>

### `statusbackup`

Status of incremental backup

```
nodetool [global options] statusbackup
```

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/StatusBackup.java` (class `StatusBackup`)</sub>

<a id="statusbinary"></a>

### `statusbinary`

Status of native transport (binary protocol)

```
nodetool [global options] statusbinary
```

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/StatusBinary.java` (class `StatusBinary`)</sub>

<a id="statusgossip"></a>

### `statusgossip`

Status of gossip

```
nodetool [global options] statusgossip
```

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/StatusGossip.java` (class `StatusGossip`)</sub>

<a id="statushandoff"></a>

### `statushandoff`

Status of storing future hints on the current node

```
nodetool [global options] statushandoff
```

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/StatusHandoff.java` (class `StatusHandoff`)</sub>

<a id="stop"></a>

### `stop`

Stop compaction

```
nodetool [global options] stop [options] <compaction type>
```

* **Arguments** `<compaction type>`: Supported types are COMPACTION, VALIDATION, CLEANUP, SCRUB, UPGRADE_SSTABLES, INDEX_BUILD, TOMBSTONE_COMPACTION, ANTICOMPACTION, VERIFY, VIEW_BUILD, INDEX_SUMMARY, RELOCATE, GARBAGE_COLLECT

| Option | Description |
| :--- | :--- |
| `-id`, `--compaction-id` | Use -id to stop a compaction by the specified id. Ids can be found in the transaction log files whose name starts with compaction_, located in the table transactions folder. |

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/Stop.java` (class `Stop`)</sub>

<a id="stopdaemon"></a>

### `stopdaemon`

Stop cassandra daemon

```
nodetool [global options] stopdaemon
```

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/StopDaemon.java` (class `StopDaemon`)</sub>

<a id="tablehistograms"></a>

### `tablehistograms`

Print statistic histograms for a given table

```
nodetool [global options] tablehistograms [<keyspace> <table> | <keyspace.table>]
```

* **Arguments** `[<keyspace> <table> \| <keyspace.table>]`: The keyspace and table name

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/TableHistograms.java` (class `TableHistograms`)</sub>

<a id="tablestats"></a>

### `tablestats`

Print statistics on tables

```
nodetool [global options] tablestats [options] [<keyspace.table>...]
```

* **Arguments** `[<keyspace.table>...]`: List of tables (or keyspace) names

| Option | Description |
| :--- | :--- |
| `-i` | Ignore the list of tables and display the remaining tables |
| `-H`, `--human-readable` | Display bytes in human readable form, i.e. KiB, MiB, GiB, TiB |
| `-F`, `--format` | Output format (json, yaml) |
| `-s`, `--sort` | Sort tables by specified sort key (average_live_cells_per_slice_last_five_minutes, average_tombstones_per_slice_last_five_minutes, bloom_filter_false_positives, bloom_filter_false_ratio, bloom_filter_off_heap_memory_used, bloom_filter_space_used, compacted_partition_maximum_bytes, compacted_partition_mean_bytes, compacted_partition_minimum_bytes, compression_metadata_off_heap_memory_used, full_name, index_summary_off_heap_memory_used, local_read_count, local_read_latency_ms, local_write_latency_ms, maximum_live_cells_per_slice_last_five_minutes, maximum_tombstones_per_slice_last_five_minutes, memtable_cell_count, memtable_data_size, memtable_off_heap_memory_used, memtable_switch_count, number_of_partitions_estimate, off_heap_memory_used_total, pending_flushes, percent_repaired, read_latency, reads, space_used_by_snapshots_total, space_used_live, space_used_total, sstable_compression_ratio, sstable_count, table_name, write_latency, writes, max_sstable_size, local_read_write_ratio, twcs_max_duration, sai_local_query_latency_ms,sai_post_filtering_read_latency, sai_disk_used_bytes, sai_sstable_indexes_hit, sai_index_segments_hit sai_rows_filtered, sai_total_query_timeouts, sai_total_queryable_index_ratio) |
| `-t`, `--top` | Show only the top K tables for the sort key (specify the number K of tables to be shown |
| `-l`, `--sstable-location-check` | Check whether or not the SSTables are in the correct location. |

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/TableStats.java` (class `TableStats`)</sub>

<a id="toppartitions"></a>

### `toppartitions`

Sample and print the most active partitions

```
nodetool [global options] toppartitions [options] <keyspace> <cfname> <duration>
```

* **Arguments** `<keyspace> <cfname> <duration>`: The keyspace, column family name, and duration in milliseconds (Default: 10000)

| Option | Description |
| :--- | :--- |
| `-s` | Capacity of the sampler, higher for more accuracy (Default: 256) |
| `-k` | Number of the top samples to list (Default: 10) |
| `-a` | Comma separated list of samplers to use (Default: all) |
| `-i`, `--interval` | Schedule a new job that samples every interval milliseconds (Default: disabled) in the background |
| `-t`, `--stop` | Stop the scheduled sampling job identified by <keyspace> and <cfname>. Jobs are stopped until the last schedules complete. |
| `-l`, `--list` | List the scheduled sampling jobs |

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/TopPartitions.java` (class `TopPartitions`)</sub>

<a id="tpstats"></a>

### `tpstats`

Print usage statistics of thread pools

```
nodetool [global options] tpstats [options]
```

| Option | Description |
| :--- | :--- |
| `-F`, `--format` | Output format (json, yaml) |

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/TpStats.java` (class `TpStats`)</sub>

<a id="truncatehints"></a>

### `truncatehints`

Truncate all hints on the local node, or truncate hints for the endpoint(s) specified.

```
nodetool [global options] truncatehints [endpoint ... ]
```

* **Arguments** `[endpoint ... ]`: Endpoint address(es) to delete hints for, either ip address ("127.0.0.1") or hostname

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/TruncateHints.java` (class `TruncateHints`)</sub>

<a id="updatecidrgroup"></a>

### `updatecidrgroup`

Insert/Update a cidr group

```
nodetool [global options] updatecidrgroup [<cidrGroup> <cidr> ...]
```

* **Arguments** `[<cidrGroup> <cidr> ...]`: Requires a cidr group name, followed by one or more CIDRs separated by space

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/UpdateCIDRGroup.java` (class `UpdateCIDRGroup`)</sub>

<a id="upgradesstables"></a>

### `upgradesstables`

Rewrite sstables (for the requested tables) that are not on the current version (thus upgrading them to said current version)

```
nodetool [global options] upgradesstables [options] [<keyspace> <tables>...]
```

* **Arguments** `[<keyspace> <tables>...]`: The keyspace followed by one or many tables

| Option | Description |
| :--- | :--- |
| `-a`, `--include-all-sstables` | Use -a to include all sstables, even those already on the current version |
| `-t`, `--max-timestamp` | Use -t to compact only SSTables that have local creation time _older_ than the given timestamp |
| `-j`, `--jobs` | Number of sstables to upgrade simultanously, set to 0 to use all available compaction threads |

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/UpgradeSSTable.java` (class `UpgradeSSTable`)</sub>

<a id="verify"></a>

### `verify`

Verify (check data checksum for) one or more tables

```
nodetool [global options] verify [options] [<keyspace> <tables>...]
```

* **Arguments** `[<keyspace> <tables>...]`: The keyspace followed by one or many tables

| Option | Description |
| :--- | :--- |
| `-e`, `--extended-verify` | Verify each cell data, beyond simply checking sstable checksums |
| `-c`, `--check-version` | Also check that all sstables are the latest version |
| `-f`, `--force` | Override disabling of verify tool - see CASSANDRA-9947 for caveats |
| `-d`, `--dfp` | Invoke the disk failure policy if a corrupt sstable is found |
| `-r`, `--rsc` | Mutate the repair status on corrupt sstables |
| `-t`, `--check-tokens` | Verify that all tokens in sstables are owned by this node |
| `-q`, `--quick` | Do a quick check - avoid reading all data to verify checksums |

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/Verify.java` (class `Verify`)</sub>

<a id="version"></a>

### `version`

Print cassandra version

```
nodetool [global options] version [options]
```

| Option | Description |
| :--- | :--- |
| `-v`, `--verbose` | Include additional information |

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/Version.java` (class `Version`)</sub>

<a id="viewbuildstatus"></a>

### `viewbuildstatus`

Show progress of a materialized view build

```
nodetool [global options] viewbuildstatus <keyspace> <view> | <keyspace.view>
```

* **Arguments** `<keyspace> <view> \| <keyspace.view>`: The keyspace and view name

<sub>Source: `src/java/org/apache/cassandra/tools/nodetool/ViewBuildStatus.java` (class `ViewBuildStatus`)</sub>
