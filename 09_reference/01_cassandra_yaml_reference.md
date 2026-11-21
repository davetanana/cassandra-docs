# cassandra.yaml Reference (generated)

> [!NOTE]
> **Generated** from Apache Cassandra **5.0.10** at git commit `47227d98bf` (`conf/cassandra.yaml`, `conf/cassandra_latest.yaml`, `Config.java`). Do not edit by hand.
> Regenerate with: `python3 tools/gen_yaml_reference.py <cassandra-checkout> -o 09_reference/01_cassandra_yaml_reference.md`
>
> Descriptions are the comments from the Apache Cassandra source files, used under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0). Official equivalent: [cassandra.yaml file configuration](https://cassandra.apache.org/doc/5.0/cassandra/managing/configuration/cass_yaml_file.html).

How to read this page:

* **Active**: the key is set in the shipped `cassandra.yaml`. **Commented**: the shipped file contains it only as a `#` example, so Cassandra uses its built-in default (usually, but not always, the value shown).
* **cassandra_latest.yaml**: shown only when the value or block differs from `cassandra.yaml`.
* Keys accepted by `Config.java` but absent from both yaml files are listed at the end.

## Index

**A**: [`allocate_tokens_for_keyspace`](#allocate_tokens_for_keyspace), [`allocate_tokens_for_local_replication_factor`](#allocate_tokens_for_local_replication_factor), [`allow_filtering_enabled`](#allow_filtering_enabled), [`alter_table_enabled`](#alter_table_enabled), [`audit_logging_options`](#audit_logging_options), [`auth_cache_warming_enabled`](#auth_cache_warming_enabled), [`auth_read_consistency_level`](#auth_read_consistency_level), [`auth_write_consistency_level`](#auth_write_consistency_level), [`authenticator`](#authenticator), [`authorizer`](#authorizer), [`auto_hints_cleanup_enabled`](#auto_hints_cleanup_enabled), [`auto_repair`](#auto_repair), [`auto_snapshot`](#auto_snapshot), [`auto_snapshot_ttl`](#auto_snapshot_ttl), [`automatic_sstable_upgrade`](#automatic_sstable_upgrade)

**B**: [`batch_size_fail_threshold`](#batch_size_fail_threshold), [`batch_size_warn_threshold`](#batch_size_warn_threshold), [`batchlog_endpoint_strategy`](#batchlog_endpoint_strategy), [`batchlog_replay_throttle`](#batchlog_replay_throttle), [`broadcast_address`](#broadcast_address), [`broadcast_rpc_address`](#broadcast_rpc_address), [`buffer_pool_use_heap_if_exhausted`](#buffer_pool_use_heap_if_exhausted)

**C**: [`cache_load_timeout`](#cache_load_timeout), [`cas_contention_timeout`](#cas_contention_timeout), [`cdc_block_writes`](#cdc_block_writes), [`cdc_enabled`](#cdc_enabled), [`cdc_free_space_check_interval`](#cdc_free_space_check_interval), [`cdc_on_repair_enabled`](#cdc_on_repair_enabled), [`cdc_raw_directory`](#cdc_raw_directory), [`cdc_total_space`](#cdc_total_space), [`cidr_authorizer`](#cidr_authorizer), [`client_encryption_options`](#client_encryption_options), [`client_error_reporting_exclusions`](#client_error_reporting_exclusions), [`cluster_name`](#cluster_name), [`collection_size_fail_threshold`](#collection_size_fail_threshold), [`collection_size_warn_threshold`](#collection_size_warn_threshold), [`column_index_cache_size`](#column_index_cache_size), [`column_index_size`](#column_index_size), [`column_value_size_fail_threshold`](#column_value_size_fail_threshold), [`column_value_size_warn_threshold`](#column_value_size_warn_threshold), [`columns_per_table_fail_threshold`](#columns_per_table_fail_threshold), [`columns_per_table_warn_threshold`](#columns_per_table_warn_threshold), [`commit_failure_policy`](#commit_failure_policy), [`commitlog_compression`](#commitlog_compression), [`commitlog_directory`](#commitlog_directory), [`commitlog_disk_access_mode`](#commitlog_disk_access_mode), [`commitlog_segment_size`](#commitlog_segment_size), [`commitlog_sync`](#commitlog_sync), [`commitlog_sync_group_window`](#commitlog_sync_group_window), [`commitlog_sync_period`](#commitlog_sync_period), [`commitlog_total_space`](#commitlog_total_space), [`compaction_throughput`](#compaction_throughput), [`concurrent_compactors`](#concurrent_compactors), [`concurrent_counter_writes`](#concurrent_counter_writes), [`concurrent_materialized_view_builders`](#concurrent_materialized_view_builders), [`concurrent_materialized_view_writes`](#concurrent_materialized_view_writes), [`concurrent_merkle_tree_requests`](#concurrent_merkle_tree_requests), [`concurrent_reads`](#concurrent_reads), [`concurrent_validations`](#concurrent_validations), [`concurrent_writes`](#concurrent_writes), [`coordinator_read_size_fail_threshold`](#coordinator_read_size_fail_threshold), [`coordinator_read_size_warn_threshold`](#coordinator_read_size_warn_threshold), [`corrupted_tombstone_strategy`](#corrupted_tombstone_strategy), [`counter_cache_keys_to_save`](#counter_cache_keys_to_save), [`counter_cache_save_period`](#counter_cache_save_period), [`counter_cache_size`](#counter_cache_size), [`counter_write_request_timeout`](#counter_write_request_timeout), [`credentials_cache_active_update`](#credentials_cache_active_update), [`credentials_update_interval`](#credentials_update_interval), [`credentials_validity`](#credentials_validity), [`crypto_provider`](#crypto_provider)

**D**: [`data_disk_usage_max_disk_size`](#data_disk_usage_max_disk_size), [`data_disk_usage_percentage_fail_threshold`](#data_disk_usage_percentage_fail_threshold), [`data_disk_usage_percentage_warn_threshold`](#data_disk_usage_percentage_warn_threshold), [`data_file_directories`](#data_file_directories), [`default_compaction`](#default_compaction), [`default_keyspace_rf`](#default_keyspace_rf), [`default_secondary_index`](#default_secondary_index), [`default_secondary_index_enabled`](#default_secondary_index_enabled), [`denylist_consistency_level`](#denylist_consistency_level), [`denylist_initial_load_retry`](#denylist_initial_load_retry), [`denylist_max_keys_per_table`](#denylist_max_keys_per_table), [`denylist_max_keys_total`](#denylist_max_keys_total), [`denylist_range_reads_enabled`](#denylist_range_reads_enabled), [`denylist_reads_enabled`](#denylist_reads_enabled), [`denylist_refresh`](#denylist_refresh), [`denylist_writes_enabled`](#denylist_writes_enabled), [`diagnostic_events_enabled`](#diagnostic_events_enabled), [`disk_access_mode`](#disk_access_mode), [`disk_failure_policy`](#disk_failure_policy), [`disk_optimization_strategy`](#disk_optimization_strategy), [`drop_compact_storage_enabled`](#drop_compact_storage_enabled), [`drop_keyspace_enabled`](#drop_keyspace_enabled), [`drop_truncate_table_enabled`](#drop_truncate_table_enabled), [`dump_heap_on_uncaught_exception`](#dump_heap_on_uncaught_exception), [`dynamic_data_masking_enabled`](#dynamic_data_masking_enabled), [`dynamic_snitch_badness_threshold`](#dynamic_snitch_badness_threshold), [`dynamic_snitch_reset_interval`](#dynamic_snitch_reset_interval), [`dynamic_snitch_update_interval`](#dynamic_snitch_update_interval)

**E**: [`endpoint_snitch`](#endpoint_snitch), [`entire_sstable_inter_dc_stream_throughput_outbound`](#entire_sstable_inter_dc_stream_throughput_outbound), [`entire_sstable_stream_digest_validation_enabled`](#entire_sstable_stream_digest_validation_enabled), [`entire_sstable_stream_throughput_outbound`](#entire_sstable_stream_throughput_outbound)

**F**: [`fields_per_udt_fail_threshold`](#fields_per_udt_fail_threshold), [`fields_per_udt_warn_threshold`](#fields_per_udt_warn_threshold), [`file_cache_enabled`](#file_cache_enabled), [`file_cache_size`](#file_cache_size), [`flush_compression`](#flush_compression), [`full_query_logging_options`](#full_query_logging_options)

**G**: [`gc_log_threshold`](#gc_log_threshold), [`gc_warn_threshold`](#gc_warn_threshold), [`group_by_enabled`](#group_by_enabled)

**H**: [`heap_dump_path`](#heap_dump_path), [`hint_window_persistent_enabled`](#hint_window_persistent_enabled), [`hinted_handoff_disabled_datacenters`](#hinted_handoff_disabled_datacenters), [`hinted_handoff_enabled`](#hinted_handoff_enabled), [`hinted_handoff_throttle`](#hinted_handoff_throttle), [`hints_compression`](#hints_compression), [`hints_directory`](#hints_directory), [`hints_flush_period`](#hints_flush_period)

**I**: [`ideal_consistency_level`](#ideal_consistency_level), [`in_select_cartesian_product_fail_threshold`](#in_select_cartesian_product_fail_threshold), [`in_select_cartesian_product_warn_threshold`](#in_select_cartesian_product_warn_threshold), [`incremental_backups`](#incremental_backups), [`index_summary_capacity`](#index_summary_capacity), [`index_summary_resize_interval`](#index_summary_resize_interval), [`initial_token`](#initial_token), [`inter_dc_stream_throughput_outbound`](#inter_dc_stream_throughput_outbound), [`inter_dc_tcp_nodelay`](#inter_dc_tcp_nodelay), [`internode_application_receive_queue_capacity`](#internode_application_receive_queue_capacity), [`internode_application_receive_queue_reserve_endpoint_capacity`](#internode_application_receive_queue_reserve_endpoint_capacity), [`internode_application_receive_queue_reserve_global_capacity`](#internode_application_receive_queue_reserve_global_capacity), [`internode_application_send_queue_capacity`](#internode_application_send_queue_capacity), [`internode_application_send_queue_reserve_endpoint_capacity`](#internode_application_send_queue_reserve_endpoint_capacity), [`internode_application_send_queue_reserve_global_capacity`](#internode_application_send_queue_reserve_global_capacity), [`internode_authenticator`](#internode_authenticator), [`internode_compression`](#internode_compression), [`internode_socket_receive_buffer_size`](#internode_socket_receive_buffer_size), [`internode_socket_send_buffer_size`](#internode_socket_send_buffer_size), [`internode_streaming_tcp_user_timeout`](#internode_streaming_tcp_user_timeout), [`internode_tcp_connect_timeout`](#internode_tcp_connect_timeout), [`internode_tcp_user_timeout`](#internode_tcp_user_timeout), [`internode_timeout`](#internode_timeout), [`items_per_collection_fail_threshold`](#items_per_collection_fail_threshold), [`items_per_collection_warn_threshold`](#items_per_collection_warn_threshold)

**K**: [`key_cache_keys_to_save`](#key_cache_keys_to_save), [`key_cache_save_period`](#key_cache_save_period), [`key_cache_size`](#key_cache_size), [`keyspaces_fail_threshold`](#keyspaces_fail_threshold), [`keyspaces_warn_threshold`](#keyspaces_warn_threshold)

**L**: [`listen_address`](#listen_address), [`listen_interface`](#listen_interface), [`listen_interface_prefer_ipv6`](#listen_interface_prefer_ipv6), [`listen_on_broadcast_address`](#listen_on_broadcast_address), [`local_read_size_fail_threshold`](#local_read_size_fail_threshold), [`local_read_size_warn_threshold`](#local_read_size_warn_threshold), [`local_system_data_file_directory`](#local_system_data_file_directory)

**M**: [`materialized_views_enabled`](#materialized_views_enabled), [`materialized_views_on_repair_enabled`](#materialized_views_on_repair_enabled), [`materialized_views_per_table_fail_threshold`](#materialized_views_per_table_fail_threshold), [`materialized_views_per_table_warn_threshold`](#materialized_views_per_table_warn_threshold), [`max_concurrent_automatic_sstable_upgrades`](#max_concurrent_automatic_sstable_upgrades), [`max_hint_window`](#max_hint_window), [`max_hints_delivery_threads`](#max_hints_delivery_threads), [`max_hints_file_size`](#max_hints_file_size), [`max_hints_size_per_host`](#max_hints_size_per_host), [`max_value_size`](#max_value_size), [`maximum_replication_factor_fail_threshold`](#maximum_replication_factor_fail_threshold), [`maximum_replication_factor_warn_threshold`](#maximum_replication_factor_warn_threshold), [`maximum_timestamp_fail_threshold`](#maximum_timestamp_fail_threshold), [`maximum_timestamp_warn_threshold`](#maximum_timestamp_warn_threshold), [`memtable`](#memtable), [`memtable_allocation_type`](#memtable_allocation_type), [`memtable_cleanup_threshold`](#memtable_cleanup_threshold), [`memtable_flush_writers`](#memtable_flush_writers), [`memtable_heap_space`](#memtable_heap_space), [`memtable_offheap_space`](#memtable_offheap_space), [`minimum_replication_factor_fail_threshold`](#minimum_replication_factor_fail_threshold), [`minimum_replication_factor_warn_threshold`](#minimum_replication_factor_warn_threshold), [`minimum_timestamp_fail_threshold`](#minimum_timestamp_fail_threshold), [`minimum_timestamp_warn_threshold`](#minimum_timestamp_warn_threshold)

**N**: [`native_transport_allow_older_protocols`](#native_transport_allow_older_protocols), [`native_transport_flush_in_batches_legacy`](#native_transport_flush_in_batches_legacy), [`native_transport_idle_timeout`](#native_transport_idle_timeout), [`native_transport_max_auth_threads`](#native_transport_max_auth_threads), [`native_transport_max_concurrent_connections`](#native_transport_max_concurrent_connections), [`native_transport_max_concurrent_connections_per_ip`](#native_transport_max_concurrent_connections_per_ip), [`native_transport_max_frame_size`](#native_transport_max_frame_size), [`native_transport_max_requests_per_second`](#native_transport_max_requests_per_second), [`native_transport_max_threads`](#native_transport_max_threads), [`native_transport_port`](#native_transport_port), [`native_transport_port_ssl`](#native_transport_port_ssl), [`native_transport_rate_limiting_enabled`](#native_transport_rate_limiting_enabled), [`network_authorizer`](#network_authorizer), [`networking_cache_size`](#networking_cache_size), [`non_partition_restricted_index_query_enabled`](#non_partition_restricted_index_query_enabled), [`num_tokens`](#num_tokens)

**P**: [`page_size_fail_threshold`](#page_size_fail_threshold), [`page_size_warn_threshold`](#page_size_warn_threshold), [`partition_denylist_enabled`](#partition_denylist_enabled), [`partition_keys_in_select_fail_threshold`](#partition_keys_in_select_fail_threshold), [`partition_keys_in_select_warn_threshold`](#partition_keys_in_select_warn_threshold), [`partition_size_fail_threshold`](#partition_size_fail_threshold), [`partition_size_warn_threshold`](#partition_size_warn_threshold), [`partition_tombstones_fail_threshold`](#partition_tombstones_fail_threshold), [`partition_tombstones_warn_threshold`](#partition_tombstones_warn_threshold), [`partitioner`](#partitioner), [`paxos_variant`](#paxos_variant), [`periodic_commitlog_sync_lag_block`](#periodic_commitlog_sync_lag_block), [`permissions_cache_active_update`](#permissions_cache_active_update), [`permissions_update_interval`](#permissions_update_interval), [`permissions_validity`](#permissions_validity), [`phi_convict_threshold`](#phi_convict_threshold), [`prepared_statements_cache_size`](#prepared_statements_cache_size)

**R**: [`range_request_timeout`](#range_request_timeout), [`read_before_write_list_operations_enabled`](#read_before_write_list_operations_enabled), [`read_consistency_levels_disallowed`](#read_consistency_levels_disallowed), [`read_consistency_levels_warned`](#read_consistency_levels_warned), [`read_request_timeout`](#read_request_timeout), [`read_thresholds_enabled`](#read_thresholds_enabled), [`reject_repair_compaction_threshold`](#reject_repair_compaction_threshold), [`repair`](#repair), [`repair_disk_headroom_reject_ratio`](#repair_disk_headroom_reject_ratio), [`repair_session_space`](#repair_session_space), [`repaired_data_tracking_for_partition_reads_enabled`](#repaired_data_tracking_for_partition_reads_enabled), [`repaired_data_tracking_for_range_reads_enabled`](#repaired_data_tracking_for_range_reads_enabled), [`replica_filtering_protection`](#replica_filtering_protection), [`report_unconfirmed_repaired_data_mismatches`](#report_unconfirmed_repaired_data_mismatches), [`request_timeout`](#request_timeout), [`role_manager`](#role_manager), [`roles_cache_active_update`](#roles_cache_active_update), [`roles_update_interval`](#roles_update_interval), [`roles_validity`](#roles_validity), [`row_cache_class_name`](#row_cache_class_name), [`row_cache_keys_to_save`](#row_cache_keys_to_save), [`row_cache_save_period`](#row_cache_save_period), [`row_cache_size`](#row_cache_size), [`row_index_read_size_fail_threshold`](#row_index_read_size_fail_threshold), [`row_index_read_size_warn_threshold`](#row_index_read_size_warn_threshold), [`rpc_address`](#rpc_address), [`rpc_interface`](#rpc_interface), [`rpc_interface_prefer_ipv6`](#rpc_interface_prefer_ipv6), [`rpc_keepalive`](#rpc_keepalive)

**S**: [`sai_frozen_term_size_fail_threshold`](#sai_frozen_term_size_fail_threshold), [`sai_frozen_term_size_warn_threshold`](#sai_frozen_term_size_warn_threshold), [`sai_options`](#sai_options), [`sai_sstable_indexes_per_query_fail_threshold`](#sai_sstable_indexes_per_query_fail_threshold), [`sai_sstable_indexes_per_query_warn_threshold`](#sai_sstable_indexes_per_query_warn_threshold), [`sai_string_term_size_fail_threshold`](#sai_string_term_size_fail_threshold), [`sai_string_term_size_warn_threshold`](#sai_string_term_size_warn_threshold), [`sai_vector_term_size_fail_threshold`](#sai_vector_term_size_fail_threshold), [`sai_vector_term_size_warn_threshold`](#sai_vector_term_size_warn_threshold), [`sasi_indexes_enabled`](#sasi_indexes_enabled), [`saved_caches_directory`](#saved_caches_directory), [`secondary_indexes_enabled`](#secondary_indexes_enabled), [`secondary_indexes_per_table_fail_threshold`](#secondary_indexes_per_table_fail_threshold), [`secondary_indexes_per_table_warn_threshold`](#secondary_indexes_per_table_warn_threshold), [`seed_provider`](#seed_provider), [`server_encryption_options`](#server_encryption_options), [`simplestrategy_enabled`](#simplestrategy_enabled), [`slow_query_log_timeout`](#slow_query_log_timeout), [`snapshot_before_compaction`](#snapshot_before_compaction), [`snapshot_links_per_second`](#snapshot_links_per_second), [`ssl_storage_port`](#ssl_storage_port), [`sstable`](#sstable), [`sstable_preemptive_open_interval`](#sstable_preemptive_open_interval), [`start_native_transport`](#start_native_transport), [`startup_checks`](#startup_checks), [`storage_compatibility_mode`](#storage_compatibility_mode), [`storage_port`](#storage_port), [`stream_entire_sstables`](#stream_entire_sstables), [`stream_throughput_outbound`](#stream_throughput_outbound), [`streaming_connections_per_host`](#streaming_connections_per_host), [`streaming_keep_alive_period`](#streaming_keep_alive_period), [`streaming_state_expires`](#streaming_state_expires), [`streaming_state_size`](#streaming_state_size), [`streaming_stats_enabled`](#streaming_stats_enabled)

**T**: [`table_properties_disallowed`](#table_properties_disallowed), [`table_properties_ignored`](#table_properties_ignored), [`table_properties_warned`](#table_properties_warned), [`tables_fail_threshold`](#tables_fail_threshold), [`tables_warn_threshold`](#tables_warn_threshold), [`tombstone_failure_threshold`](#tombstone_failure_threshold), [`tombstone_warn_threshold`](#tombstone_warn_threshold), [`trace_type_query_ttl`](#trace_type_query_ttl), [`trace_type_repair_ttl`](#trace_type_repair_ttl), [`transfer_hints_on_decommission`](#transfer_hints_on_decommission), [`transient_replication_enabled`](#transient_replication_enabled), [`transparent_data_encryption_options`](#transparent_data_encryption_options), [`traverse_auth_from_root`](#traverse_auth_from_root), [`trickle_fsync`](#trickle_fsync), [`trickle_fsync_interval`](#trickle_fsync_interval), [`truncate_request_timeout`](#truncate_request_timeout)

**U**: [`uncompressed_tables_enabled`](#uncompressed_tables_enabled), [`unlogged_batch_across_partitions_warn_threshold`](#unlogged_batch_across_partitions_warn_threshold), [`use_statements_enabled`](#use_statements_enabled), [`user_defined_functions_enabled`](#user_defined_functions_enabled), [`user_timestamps_enabled`](#user_timestamps_enabled), [`uuid_sstable_identifiers_enabled`](#uuid_sstable_identifiers_enabled)

**V**: [`vector_dimensions_fail_threshold`](#vector_dimensions_fail_threshold), [`vector_dimensions_warn_threshold`](#vector_dimensions_warn_threshold)

**W**: [`write_consistency_levels_disallowed`](#write_consistency_levels_disallowed), [`write_consistency_levels_warned`](#write_consistency_levels_warned), [`write_request_timeout`](#write_request_timeout)

**Z**: [`zero_ttl_on_twcs_enabled`](#zero_ttl_on_twcs_enabled), [`zero_ttl_on_twcs_warned`](#zero_ttl_on_twcs_warned)

## General

### `cluster_name`

<a id="cluster_name"></a>

*Active* · `conf/cassandra.yaml` line 26

```yaml
cluster_name: 'Test Cluster'
```

> The name of the cluster. This is mainly used to prevent machines in
> one logical cluster from joining another.

### `num_tokens`

<a id="num_tokens"></a>

*Active* · `conf/cassandra.yaml` line 42

```yaml
num_tokens: 16
```

> This defines the number of tokens randomly assigned to this node on the ring
> The more tokens, relative to other nodes, the larger the proportion of data
> that this node will store. You probably want all nodes to have the same number
> of tokens assuming they have equal hardware capability.
>
> If you leave this unspecified, Cassandra will use the default of 1 token for legacy compatibility,
> and will use the initial_token as described below.
>
> Specifying initial_token will override this setting on the node's initial start,
> on subsequent starts, this setting will apply even if initial token is set.
>
> See https://cassandra.apache.org/doc/latest/getting-started/production.html#tokens for
> best practice information about num_tokens.

### `allocate_tokens_for_keyspace`

<a id="allocate_tokens_for_keyspace"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 55

```yaml
allocate_tokens_for_keyspace: KEYSPACE
```

> Replica factor is determined via the replication strategy used by the specified
> keyspace.

### `allocate_tokens_for_local_replication_factor`

<a id="allocate_tokens_for_local_replication_factor"></a>

*Active* · `conf/cassandra.yaml` line 59

```yaml
allocate_tokens_for_local_replication_factor: 3
```

> Replica factor is explicitly set, regardless of keyspace or datacenter.
> This is the replica factor within the datacenter, like NTS.

### `initial_token`

<a id="initial_token"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 65

```yaml
initial_token:
```

> initial_token allows you to specify tokens manually.  While you can use it with
> vnodes (num_tokens > 1, above) -- in which case you should provide a
> comma-separated list -- it's primarily used when adding nodes to legacy clusters
> that do not have vnodes enabled.

### `hinted_handoff_enabled`

<a id="hinted_handoff_enabled"></a>

*Active* · `conf/cassandra.yaml` line 68

```yaml
hinted_handoff_enabled: true
```

> May either be "true" or "false" to enable globally

### `hinted_handoff_disabled_datacenters`

<a id="hinted_handoff_disabled_datacenters"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 72

```yaml
hinted_handoff_disabled_datacenters:
   - DC1
   - DC2
```

> When hinted_handoff_enabled is true, a black list of data centers that will not
> perform hinted handoff

### `max_hint_window`

<a id="max_hint_window"></a>

*Active* · `conf/cassandra.yaml` line 80
 · deprecated old name(s): `max_hint_window_in_ms`

```yaml
max_hint_window: 3h
```

> this defines the maximum amount of time a dead host will have hints
> generated.  After it has been dead this long, new hints for it will not be
> created until it has been seen alive and gone down again.
> Min unit: ms

### `hinted_handoff_throttle`

<a id="hinted_handoff_throttle"></a>

*Active* · `conf/cassandra.yaml` line 88
 · deprecated old name(s): `hinted_handoff_throttle_in_kb`

```yaml
hinted_handoff_throttle: 1024KiB
```

> Maximum throttle in KiBs per second, per delivery thread.  This will be
> reduced proportionally to the number of nodes in the cluster.  (If there
> are two nodes in the cluster, each delivery thread will use the maximum
> rate; if there are three, each will throttle to half of the maximum,
> since we expect two nodes to be delivering hints simultaneously.)
> Min unit: KiB

### `max_hints_delivery_threads`

<a id="max_hints_delivery_threads"></a>

*Active* · `conf/cassandra.yaml` line 93

```yaml
max_hints_delivery_threads: 2
```

> Number of threads with which to deliver hints;
> Consider increasing this number when you have multi-dc deployments, since
> cross-dc handoff tends to be slower

### `hints_directory`

<a id="hints_directory"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 97

```yaml
hints_directory: /var/lib/cassandra/hints
```

> Directory where Cassandra should store hints.
> If not set, the default directory is $CASSANDRA_HOME/data/hints.

### `hints_flush_period`

<a id="hints_flush_period"></a>

*Active* · `conf/cassandra.yaml` line 102
 · deprecated old name(s): `hints_flush_period_in_ms`

```yaml
hints_flush_period: 10000ms
```

> How often hints should be flushed from the internal buffers to disk.
> Will *not* trigger fsync.
> Min unit: ms

### `max_hints_file_size`

<a id="max_hints_file_size"></a>

*Active* · `conf/cassandra.yaml` line 106
 · deprecated old name(s): `max_hints_file_size_in_mb`

```yaml
max_hints_file_size: 128MiB
```

> Maximum size for a single hints file, in mebibytes.
> Min unit: MiB

### `max_hints_size_per_host`

<a id="max_hints_size_per_host"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 111

```yaml
max_hints_size_per_host: 0MiB
```

> The file size limit to store hints for an unreachable host, in mebibytes.
> Once the local hints files have reached the limit, no more new hints will be created.
> Set a non-positive value will disable the size limit.

### `auto_hints_cleanup_enabled`

<a id="auto_hints_cleanup_enabled"></a>

*Active* · `conf/cassandra.yaml` line 115

```yaml
auto_hints_cleanup_enabled: false
```

> Enable / disable automatic cleanup for the expired and orphaned hints file.
> Disable the option in order to preserve those hints on the disk.

### `transfer_hints_on_decommission`

<a id="transfer_hints_on_decommission"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 120

```yaml
transfer_hints_on_decommission: true
```

> Enable/disable transferring hints to a peer during decommission. Even when enabled, this does not guarantee
> consistency for logged batches, and it may delay decommission when coupled with a strict hinted_handoff_throttle.
> Default: true

### `hints_compression`

<a id="hints_compression"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 125

```yaml
hints_compression:
  - class_name: LZ4Compressor
    parameters:
        -
```

> Compression to apply to the hint files. If omitted, hints files
> will be written uncompressed. LZ4, Snappy, and Deflate compressors
> are supported.

### `heap_dump_path`

<a id="heap_dump_path"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 134

```yaml
heap_dump_path: /var/lib/cassandra/heapdump
```

> Directory where Cassandra should store results of a One-Shot troubleshooting heapdump for uncaught exceptions.
> Note: this value can be overridden by the -XX:HeapDumpPath JVM env param with a relative local path for testing if
> so desired.
> If not set, the default directory is $CASSANDRA_HOME/heapdump

### `dump_heap_on_uncaught_exception`

<a id="dump_heap_on_uncaught_exception"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 138

```yaml
dump_heap_on_uncaught_exception: true
```

> Enable / disable automatic dump of heap on first uncaught exception
> If not set, the default value is false

### `hint_window_persistent_enabled`

<a id="hint_window_persistent_enabled"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 152

```yaml
hint_window_persistent_enabled: true
```

> Enable / disable persistent hint windows.
>
> If set to false, a hint will be stored only in case a respective node
> that hint is for is down less than or equal to max_hint_window.
>
> If set to true, a hint will be stored in case there is not any
> hint which was stored earlier than max_hint_window. This is for cases
> when a node keeps to restart and hints are not delivered yet, we would be saving
> hints for that node indefinitely.
>
> Defaults to true.

### `batchlog_replay_throttle`

<a id="batchlog_replay_throttle"></a>

*Active* · `conf/cassandra.yaml` line 157
 · deprecated old name(s): `batchlog_replay_throttle_in_kb`

```yaml
batchlog_replay_throttle: 1024KiB
```

> Maximum throttle in KiBs per second, total. This will be
> reduced proportionally to the number of nodes in the cluster.
> Min unit: KiB

### `batchlog_endpoint_strategy`

<a id="batchlog_endpoint_strategy"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 183

```yaml
batchlog_endpoint_strategy: random_remote
```

**In `cassandra_latest.yaml`**:

```yaml
batchlog_endpoint_strategy: dynamic_remote
```

> Strategy to choose the batchlog storage endpoints.
>
> Available options:
>
> - random_remote
>   Default, purely random, prevents the local rack, if possible.
>
> - prefer_local
>   Similar to random_remote. Random, except that one of the replications will go to the local rack,
>   which mean it offers lower availability guarantee than random_remote or dynamic_remote.
>
> - dynamic_remote
>   Using DynamicEndpointSnitch to select batchlog storage endpoints, prevents the
>   local rack, if possible. This strategy offers the same availability guarantees
>   as random_remote but selects the fastest endpoints according to the DynamicEndpointSnitch.
>   (DynamicEndpointSnitch currently only tracks reads and not writes - i.e. write-only
>   (or mostly-write) workloads might not benefit from this strategy.)
>   Note: this strategy will fall back to random_remote, if dynamic_snitch is not enabled.
>
> - dynamic
>   Mostly the same as dynamic_remote, except that local rack is not excluded, which mean it offers lower
>   availability guarantee than random_remote or dynamic_remote.
>   Note: this strategy will fall back to random_remote, if dynamic_snitch is not enabled.

### `authenticator`

<a id="authenticator"></a>

*Active* · `conf/cassandra.yaml` line 198

```yaml
authenticator: AllowAllAuthenticator
```

**In `cassandra_latest.yaml`**:

```yaml
authenticator:
  class_name: AllowAllAuthenticator
```

> Authentication backend, implementing IAuthenticator; used to identify users
> Out of the box, Cassandra provides org.apache.cassandra.auth.{AllowAllAuthenticator,
> PasswordAuthenticator}.
> Optional parameters can be specified in the form of:
>   parameters:
>    param_key1: param_value1
>    ...
>
> - AllowAllAuthenticator performs no checks - set it to disable authentication.
> - PasswordAuthenticator relies on username/password pairs to authenticate
>   users. It keeps usernames and hashed passwords in system_auth.roles table.
>   Please increase system_auth keyspace replication factor if you use this authenticator.
>   If using PasswordAuthenticator, CassandraRoleManager must also be used (see below)

### `authorizer`

<a id="authorizer"></a>

*Active* · `conf/cassandra.yaml` line 217

```yaml
authorizer: AllowAllAuthorizer
```

**In `cassandra_latest.yaml`**:

```yaml
authorizer:
  class_name: AllowAllAuthorizer
```

> Authorization backend, implementing IAuthorizer; used to limit access/provide permissions
> Out of the box, Cassandra provides org.apache.cassandra.auth.{AllowAllAuthorizer,
> CassandraAuthorizer}.
> Optional parameters can be specified in the form of:
>   parameters:
>    param_key1: param_value1
>    ...
>
> - AllowAllAuthorizer allows any action to any user - set it to disable authorization.
> - CassandraAuthorizer stores permissions in system_auth.role_permissions table. Please
>   increase system_auth keyspace replication factor if you use this authorizer.

### `role_manager`

<a id="role_manager"></a>

*Active* · `conf/cassandra.yaml` line 232

```yaml
role_manager: CassandraRoleManager
```

**In `cassandra_latest.yaml`**:

```yaml
role_manager:
  class_name: CassandraRoleManager
```

> Part of the Authentication & Authorization backend, implementing IRoleManager; used
> to maintain grants and memberships between roles.
> Out of the box, Cassandra provides org.apache.cassandra.auth.CassandraRoleManager,
> which stores role information in the system_auth keyspace. Most functions of the
> IRoleManager require an authenticated login, so unless the configured IAuthenticator
> actually implements authentication, most of this functionality will be unavailable.
> Optional parameters can be specified in the form of:
>   parameters:
>    param_key1: param_value1
>    ...
>
> - CassandraRoleManager stores role data in the system_auth keyspace. Please
>   increase system_auth keyspace replication factor if you use this role manager.

### `network_authorizer`

<a id="network_authorizer"></a>

*Active* · `conf/cassandra.yaml` line 246

```yaml
network_authorizer: AllowAllNetworkAuthorizer
```

**In `cassandra_latest.yaml`**:

```yaml
network_authorizer:
  class_name: AllowAllNetworkAuthorizer
```

> Network authorization backend, implementing INetworkAuthorizer; used to restrict user
> access to certain DCs
> Out of the box, Cassandra provides org.apache.cassandra.auth.{AllowAllNetworkAuthorizer,
> CassandraNetworkAuthorizer}.
> Optional parameters can be specified in the form of:
>   parameters:
>    param_key1: param_value1
>    ...
>
> - AllowAllNetworkAuthorizer allows access to any DC to any user - set it to disable authorization.
> - CassandraNetworkAuthorizer stores permissions in system_auth.network_permissions table. Please
>   increase system_auth keyspace replication factor if you use this authorizer.

### `cidr_authorizer`

<a id="cidr_authorizer"></a>

*Active* · `conf/cassandra.yaml` line 261

```yaml
cidr_authorizer:
  class_name: AllowAllCIDRAuthorizer
  # Below parameters are used only when CIDR authorizer is enabled
  # parameters:
    # CIDR authorizer when enabled, i.e, CassandraCIDRAuthorizer, is applicable for non-superusers only by default.
    # Set this setting to true, to enable CIDR authorization for superusers as well.
    # Note: CIDR checks cannot be performed for JMX calls
    # cidr_checks_for_superusers: true
```

> CIDR authorization backend, implementing ICIDRAuthorizer; used to restrict user
> access from certain CIDRs
> Out of the box, Cassandra provides org.apache.cassandra.auth.{AllowAllCIDRAuthorizer,
> CassandraCIDRAuthorizer}.
> Optional parameters can be specified in the form of:
>   parameters:
>    param_key1: param_value1
>    ...
>
> - AllowAllCIDRAuthorizer allows access from any CIDR to any user - set it to disable CIDR authorization.
> - CassandraCIDRAuthorizer stores user's CIDR permissions in system_auth.cidr_permissions table. Please
>   increase system_auth keyspace replication factor if you use this authorizer, otherwise any changes to
>   system_auth tables being used by this feature may be lost when a host goes down.

### `traverse_auth_from_root`

<a id="traverse_auth_from_root"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 289

```yaml
traverse_auth_from_root: false
```

> Depending on the auth strategy of the cluster, it can be beneficial to iterate
> from root to table (root -> ks -> table) instead of table to root (table -> ks -> root).
> As the auth entries are whitelisting, once a permission is found you know it to be
> valid. We default to false as the legacy behavior is to query at the table level then
> move back up to the root. See CASSANDRA-17016 for details.

### `roles_validity`

<a id="roles_validity"></a>

*Active* · `conf/cassandra.yaml` line 300
 · deprecated old name(s): `roles_validity_in_ms`

```yaml
roles_validity: 2000ms
```

> Validity period for roles cache (fetching granted roles can be an expensive
> operation depending on the role manager, CassandraRoleManager is one example)
> Granted roles are cached for authenticated sessions in AuthenticatedUser and
> after the period specified here, become eligible for (async) reload.
> Defaults to 2000, set to 0 to disable caching entirely.
> Will be disabled automatically for AllowAllAuthenticator.
> For a long-running cache using roles_cache_active_update, consider
> setting to something longer such as a daily validation: 86400000
> Min unit: ms

### `roles_update_interval`

<a id="roles_update_interval"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 312
 · deprecated old name(s): `roles_update_interval_in_ms`

```yaml
roles_update_interval: 2000ms
```

> Refresh interval for roles cache (if enabled).
> After this interval, cache entries become eligible for refresh. Upon next
> access, an async reload is scheduled and the old value returned until it
> completes. If roles_validity is non-zero, then this must be
> also.
> This setting is also used to inform the interval of auto-updating if
> using roles_cache_active_update.
> Defaults to the same value as roles_validity.
> For a long-running cache, consider setting this to 60000 (1 hour) etc.
> Min unit: ms

### `roles_cache_active_update`

<a id="roles_cache_active_update"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 318

```yaml
roles_cache_active_update: false
```

> If true, cache contents are actively updated by a background task at the
> interval set by roles_update_interval. If false, cache entries
> become eligible for refresh after their update interval. Upon next access,
> an async reload is scheduled and the old value returned until it completes.

### `permissions_validity`

<a id="permissions_validity"></a>

*Active* · `conf/cassandra.yaml` line 327
 · deprecated old name(s): `permissions_validity_in_ms`

```yaml
permissions_validity: 2000ms
```

> Validity period for permissions cache (fetching permissions can be an
> expensive operation depending on the authorizer, CassandraAuthorizer is
> one example). Defaults to 2000, set to 0 to disable.
> Will be disabled automatically for AllowAllAuthorizer.
> For a long-running cache using permissions_cache_active_update, consider
> setting to something longer such as a daily validation: 86400000ms
> Min unit: ms

### `permissions_update_interval`

<a id="permissions_update_interval"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 339
 · deprecated old name(s): `permissions_update_interval_in_ms`

```yaml
permissions_update_interval: 2000ms
```

> Refresh interval for permissions cache (if enabled).
> After this interval, cache entries become eligible for refresh. Upon next
> access, an async reload is scheduled and the old value returned until it
> completes. If permissions_validity is non-zero, then this must be
> also.
> This setting is also used to inform the interval of auto-updating if
> using permissions_cache_active_update.
> Defaults to the same value as permissions_validity.
> For a longer-running permissions cache, consider setting to update hourly (60000)
> Min unit: ms

### `permissions_cache_active_update`

<a id="permissions_cache_active_update"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 345

```yaml
permissions_cache_active_update: false
```

> If true, cache contents are actively updated by a background task at the
> interval set by permissions_update_interval. If false, cache entries
> become eligible for refresh after their update interval. Upon next access,
> an async reload is scheduled and the old value returned until it completes.

### `credentials_validity`

<a id="credentials_validity"></a>

*Active* · `conf/cassandra.yaml` line 359
 · deprecated old name(s): `credentials_validity_in_ms`

```yaml
credentials_validity: 2000ms
```

> Validity period for credentials cache. This cache is tightly coupled to
> the provided PasswordAuthenticator implementation of IAuthenticator. If
> another IAuthenticator implementation is configured, this cache will not
> be automatically used and so the following settings will have no effect.
> Please note, credentials are cached in their encrypted form, so while
> activating this cache may reduce the number of queries made to the
> underlying table, it may not  bring a significant reduction in the
> latency of individual authentication attempts.
> Defaults to 2000, set to 0 to disable credentials caching.
> For a long-running cache using credentials_cache_active_update, consider
> setting to something longer such as a daily validation: 86400000
> Min unit: ms

### `credentials_update_interval`

<a id="credentials_update_interval"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 371
 · deprecated old name(s): `credentials_update_interval_in_ms`

```yaml
credentials_update_interval: 2000ms
```

> Refresh interval for credentials cache (if enabled).
> After this interval, cache entries become eligible for refresh. Upon next
> access, an async reload is scheduled and the old value returned until it
> completes. If credentials_validity is non-zero, then this must be
> also.
> This setting is also used to inform the interval of auto-updating if
> using credentials_cache_active_update.
> Defaults to the same value as credentials_validity.
> For a longer-running permissions cache, consider setting to update hourly (60000)
> Min unit: ms

### `credentials_cache_active_update`

<a id="credentials_cache_active_update"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 377

```yaml
credentials_cache_active_update: false
```

> If true, cache contents are actively updated by a background task at the
> interval set by credentials_update_interval. If false (default), cache entries
> become eligible for refresh after their update interval. Upon next access,
> an async reload is scheduled and the old value returned until it completes.

### `partitioner`

<a id="partitioner"></a>

*Active* · `conf/cassandra.yaml` line 389

```yaml
partitioner: org.apache.cassandra.dht.Murmur3Partitioner
```

> The partitioner is responsible for distributing groups of rows (by
> partition key) across nodes in the cluster. The partitioner can NOT be
> changed without reloading all data.  If you are adding nodes or upgrading,
> you should set this to the same partitioner that you are currently using.
>
> The default partitioner is the Murmur3Partitioner. Older partitioners
> such as the RandomPartitioner, ByteOrderedPartitioner, and
> OrderPreservingPartitioner have been included for backward compatibility only.
> For new clusters, you should NOT change this value.

### `data_file_directories`

<a id="data_file_directories"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 395

```yaml
data_file_directories:
    - /var/lib/cassandra/data
```

> Directories where Cassandra should store data on disk. If multiple
> directories are specified, Cassandra will spread data evenly across
> them by partitioning the token ranges.
> If not set, the default directory is $CASSANDRA_HOME/data/data.

### `local_system_data_file_directory`

<a id="local_system_data_file_directory"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 403

```yaml
local_system_data_file_directory:
```

> Directory were Cassandra should store the data of the local system keyspaces.
> By default Cassandra will store the data of the local system keyspaces in the first of the data directories specified
> by data_file_directories.
> This approach ensures that if one of the other disks is lost Cassandra can continue to operate. For extra security
> this setting allows to store those data on a different directory that provides redundancy.

### `commitlog_directory`

<a id="commitlog_directory"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 408

```yaml
commitlog_directory: /var/lib/cassandra/commitlog
```

> commit log.  when running on magnetic HDD, this should be a
> separate spindle than the data directories.
> If not set, the default directory is $CASSANDRA_HOME/data/commitlog.

### `cdc_enabled`

<a id="cdc_enabled"></a>

*Active* · `conf/cassandra.yaml` line 413

```yaml
cdc_enabled: false
```

> Enable / disable CDC functionality on a per-node basis. This modifies the logic used
> for write path allocation rejection (standard: never reject. cdc: reject Mutation
> containing a CDC-enabled table if at space limit in cdc_raw_directory).

### `cdc_block_writes`

<a id="cdc_block_writes"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 418

```yaml
cdc_block_writes: true
```

> Specify whether writes to the CDC-enabled tables should be blocked when CDC data on disk has reached to the limit.
> When setting to false, the writes will not be blocked and the oldest CDC data on disk will be deleted to
> ensure the size constraint. The default is true.

### `cdc_on_repair_enabled`

<a id="cdc_on_repair_enabled"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 425

```yaml
cdc_on_repair_enabled: true
```

> Specify whether CDC mutations are replayed through the write path on streaming, e.g. repair.
> When enabled, CDC data streamed to the destination node will be written into commit log first. When setting to false,
> the streamed CDC data is written into SSTables just the same as normal streaming. The default is true.
> If this is set to false, streaming will be considerably faster however it's possible that, in extreme situations
> (losing > quorum # nodes in a replica set), you may have data in your SSTables that never makes it to the CDC log.

### `cdc_raw_directory`

<a id="cdc_raw_directory"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 431

```yaml
cdc_raw_directory: /var/lib/cassandra/cdc_raw
```

> CommitLogSegments are moved to this directory on flush if cdc_enabled: true and the
> segment contains mutations for a CDC-enabled table. This should be placed on a
> separate spindle than the data directories. If not set, the default directory is
> $CASSANDRA_HOME/data/cdc_raw.

### `disk_access_mode`

<a id="disk_access_mode"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 448

```yaml
disk_access_mode: mmap_index_only
```

> Policy for accessing disk:
>
> auto
>   Enable mmap on both data and index files on a 64-bit JVM.
>
> standard
>   Disable mmap entirely.
>
> mmap
>   Map index and data files. mmap can cause excessive paging if all actively read SSTables do not fit into RAM.
>
> mmap_index_only
>   Similar to mmap but maps only index files. Using this setting might also help if you observe high number of page
>   faults or steals along with increased latencies. This setting is default.

### `disk_failure_policy`

<a id="disk_failure_policy"></a>

*Active* · `conf/cassandra.yaml` line 471

```yaml
disk_failure_policy: stop
```

> Policy for data disk failures:
>
> die
>   shut down gossip and client transports and kill the JVM for any fs errors or
>   single-sstable errors, so the node can be replaced.
>
> stop_paranoid
>   shut down gossip and client transports even for single-sstable errors,
>   kill the JVM for errors during startup.
>
> stop
>   shut down gossip and client transports, leaving the node effectively dead, but
>   can still be inspected via JMX, kill the JVM for errors during startup.
>
> best_effort
>    stop using the failed disk and respond to requests based on
>    remaining available sstables.  This means you WILL see obsolete
>    data at CL.ONE!
>
> ignore
>    ignore fatal errors and let requests fail, as in pre-1.2 Cassandra

### `commit_failure_policy`

<a id="commit_failure_policy"></a>

*Active* · `conf/cassandra.yaml` line 488

```yaml
commit_failure_policy: stop
```

> Policy for commit disk failures:
>
> die
>   shut down the node and kill the JVM, so the node can be replaced.
>
> stop
>   shut down the node, leaving the node effectively dead, but
>   can still be inspected via JMX.
>
> stop_commit
>   shutdown the commit log, letting writes collect but
>   continuing to service reads, as in pre-2.0.5 Cassandra
>
> ignore
>   ignore fatal errors and let the batches fail

### `prepared_statements_cache_size`

<a id="prepared_statements_cache_size"></a>

*Active* · `conf/cassandra.yaml` line 508
 · deprecated old name(s): `prepared_statements_cache_size_mb`

```yaml
prepared_statements_cache_size:
```

> Maximum size of the native protocol prepared statement cache
>
> Valid values are either "auto" (omitting the value) or a value greater 0.
>
> Note that specifying a too large value will result in long running GCs and possibly
> out-of-memory errors. Keep the value at a small fraction of the heap.
>
> If you constantly see "prepared statements discarded in the last minute because
> cache limit reached" messages, the first step is to investigate the root cause
> of these messages and check whether prepared statements are used correctly -
> i.e. use bind markers for variable parts.
>
> Do only change the default value, if you really have more prepared statements than
> fit in the cache. In most cases it is not necessary to change this value.
> Constantly re-preparing statements is a performance penalty.
>
> Default value ("auto") is 1/256th of the heap or 10MiB, whichever is greater
> Min unit: MiB

### `key_cache_size`

<a id="key_cache_size"></a>

*Active* · `conf/cassandra.yaml` line 525
 · deprecated old name(s): `key_cache_size_in_mb`

```yaml
key_cache_size:
```

**In `cassandra_latest.yaml`**:

```yaml
key_cache_size: 0MiB
```

> Maximum size of the key cache in memory.
>
> Each key cache hit saves 1 seek and each row cache hit saves 2 seeks at the
> minimum, sometimes more. The key cache is fairly tiny for the amount of
> time it saves, so it's worthwhile to use it at large numbers.
> The row cache saves even more time, but must contain the entire row,
> so it is extremely space-intensive. It's best to only use the
> row cache if you have hot rows or static rows.
>
> NOTE: if you reduce the size, you may not get you hottest keys loaded on startup.
>
> Default value is empty to make it "auto" (min(5% of Heap (in MiB), 100MiB)). Set to 0 to disable key cache.
>
> This is only relevant to SSTable formats that use key cache, e.g. BIG.
> Min unit: MiB

### `key_cache_save_period`

<a id="key_cache_save_period"></a>

*Active* · `conf/cassandra.yaml` line 538
 · deprecated old name(s): `key_cache_save_period`

```yaml
key_cache_save_period: 4h
```

**In `cassandra_latest.yaml`** (commented):

```yaml
key_cache_save_period: 4h
```

> Duration in seconds after which Cassandra should
> save the key cache. Caches are saved to saved_caches_directory as
> specified in this configuration file.
>
> Saved caches greatly improve cold-start speeds, and is relatively cheap in
> terms of I/O for the key cache. Row cache saving is much more expensive and
> has limited use.
>
> This is only relevant to SSTable formats that use key cache, e.g. BIG.
> Default is 14400 or 4 hours.
> Min unit: s

### `key_cache_keys_to_save`

<a id="key_cache_keys_to_save"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 543

```yaml
key_cache_keys_to_save: 100
```

> Number of keys from the key cache to save
> Disabled by default, meaning all keys are going to be saved
> This is only relevant to SSTable formats that use key cache, e.g. BIG.

### `row_cache_class_name`

<a id="row_cache_class_name"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 553

```yaml
row_cache_class_name: org.apache.cassandra.cache.OHCProvider
```

> Row cache implementation class name. Available implementations:
>
> org.apache.cassandra.cache.OHCProvider
>   Fully off-heap row cache implementation (default).
>
> org.apache.cassandra.cache.SerializingCacheProvider
>   This is the row cache implementation available
>   in previous releases of Cassandra.

### `row_cache_size`

<a id="row_cache_size"></a>

*Active* · `conf/cassandra.yaml` line 564
 · deprecated old name(s): `row_cache_size_in_mb`

```yaml
row_cache_size: 0MiB
```

> Maximum size of the row cache in memory.
> Please note that OHC cache implementation requires some additional off-heap memory to manage
> the map structures and some in-flight memory during operations before/after cache entries can be
> accounted against the cache capacity. This overhead is usually small compared to the whole capacity.
> Do not specify more memory that the system can afford in the worst usual situation and leave some
> headroom for OS block level cache. Do never allow your system to swap.
>
> Default value is 0, to disable row caching.
> Min unit: MiB

### `row_cache_save_period`

<a id="row_cache_save_period"></a>

*Active* · `conf/cassandra.yaml` line 575
 · deprecated old name(s): `row_cache_save_period`

```yaml
row_cache_save_period: 0s
```

> Duration in seconds after which Cassandra should save the row cache.
> Caches are saved to saved_caches_directory as specified in this configuration file.
>
> Saved caches greatly improve cold-start speeds, and is relatively cheap in
> terms of I/O for the key cache. Row cache saving is much more expensive and
> has limited use.
>
> Default is 0 to disable saving the row cache.
> Min unit: s

### `row_cache_keys_to_save`

<a id="row_cache_keys_to_save"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 579

```yaml
row_cache_keys_to_save: 100
```

> Number of keys from the row cache to save.
> Specify 0 (which is the default), meaning all keys are going to be saved

### `counter_cache_size`

<a id="counter_cache_size"></a>

*Active* · `conf/cassandra.yaml` line 595
 · deprecated old name(s): `counter_cache_size_in_mb`

```yaml
counter_cache_size:
```

> Maximum size of the counter cache in memory.
>
> Counter cache helps to reduce counter locks' contention for hot counter cells.
> In case of RF = 1 a counter cache hit will cause Cassandra to skip the read before
> write entirely. With RF > 1 a counter cache hit will still help to reduce the duration
> of the lock hold, helping with hot counter cell updates, but will not allow skipping
> the read entirely. Only the local (clock, count) tuple of a counter cell is kept
> in memory, not the whole counter, so it's relatively cheap.
>
> NOTE: if you reduce the size, you may not get you hottest keys loaded on startup.
>
> Default value is empty to make it "auto" (min(2.5% of Heap (in MiB), 50MiB)). Set to 0 to disable counter cache.
> NOTE: if you perform counter deletes and rely on low gcgs, you should disable the counter cache.
> Min unit: MiB

### `counter_cache_save_period`

<a id="counter_cache_save_period"></a>

*Active* · `conf/cassandra.yaml` line 603
 · deprecated old name(s): `counter_cache_save_period`

```yaml
counter_cache_save_period: 7200s
```

> Duration in seconds after which Cassandra should
> save the counter cache (keys only). Caches are saved to saved_caches_directory as
> specified in this configuration file.
>
> Default is 7200 or 2 hours.
> Min unit: s

### `counter_cache_keys_to_save`

<a id="counter_cache_keys_to_save"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 607

```yaml
counter_cache_keys_to_save: 100
```

> Number of keys from the counter cache to save
> Disabled by default, meaning all keys are going to be saved

### `saved_caches_directory`

<a id="saved_caches_directory"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 611

```yaml
saved_caches_directory: /var/lib/cassandra/saved_caches
```

> saved caches
> If not set, the default directory is $CASSANDRA_HOME/data/saved_caches.

### `cache_load_timeout`

<a id="cache_load_timeout"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 617
 · deprecated old name(s): `cache_load_timeout_seconds`

```yaml
cache_load_timeout: 30s
```

> Number of seconds the server will wait for each cache (row, key, etc ...) to load while starting
> the Cassandra process. Setting this to zero is equivalent to disabling all cache loading on startup
> while still having the cache during runtime.
> Min unit: s

### `commitlog_sync_group_window`

<a id="commitlog_sync_group_window"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 629
 · deprecated old name(s): `commitlog_sync_group_window_in_ms`

```yaml
commitlog_sync_group_window: 1000ms
```

> commitlog_sync may be either "periodic", "group", or "batch."
>
> When in batch mode, Cassandra won't ack writes until the commit log
> has been flushed to disk.  Each incoming write will trigger the flush task.
>
> group mode is similar to batch mode, where Cassandra will not ack writes
> until the commit log has been flushed to disk. The difference is group
> mode will wait up to commitlog_sync_group_window between flushes.
>
> Min unit: ms

### `commitlog_sync`

<a id="commitlog_sync"></a>

*Active* · `conf/cassandra.yaml` line 634

```yaml
commitlog_sync: periodic
```

> the default option is "periodic" where writes may be acked immediately
> and the CommitLog is simply synced every commitlog_sync_period
> milliseconds.

### `commitlog_sync_period`

<a id="commitlog_sync_period"></a>

*Active* · `conf/cassandra.yaml` line 636
 · deprecated old name(s): `commitlog_sync_period_in_ms`

```yaml
commitlog_sync_period: 10000ms
```

> Min unit: ms

See the description of [`commitlog_sync`](#commitlog_sync), which this setting accompanies in the yaml.

### `periodic_commitlog_sync_lag_block`

<a id="periodic_commitlog_sync_lag_block"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 641
 · deprecated old name(s): `periodic_commitlog_sync_lag_block_in_ms`

```yaml
periodic_commitlog_sync_lag_block:
```

> When in periodic commitlog mode, the number of milliseconds to block writes
> while waiting for a slow disk flush to complete.
> Min unit: ms

### `commitlog_segment_size`

<a id="commitlog_segment_size"></a>

*Active* · `conf/cassandra.yaml` line 660
 · deprecated old name(s): `commitlog_segment_size_in_mb`

```yaml
commitlog_segment_size: 32MiB
```

> The size of the individual commitlog file segments.  A commitlog
> segment may be archived, deleted, or recycled once all the data
> in it (potentially from each columnfamily in the system) has been
> flushed to sstables.
>
> The default size is 32, which is almost always fine, but if you are
> archiving commitlog segments (see commitlog_archiving.properties),
> then you probably want a finer granularity of archiving; 8 or 16 MB
> is reasonable.
> Max mutation size is also configurable via max_mutation_size setting in
> cassandra.yaml. The default is half the size commitlog_segment_size in bytes.
> This should be positive and less than 2048.
>
> NOTE: If max_mutation_size is set explicitly then commitlog_segment_size must
> be set to at least twice the size of max_mutation_size
>
> Min unit: MiB

### `commitlog_compression`

<a id="commitlog_compression"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 665

```yaml
commitlog_compression:
  - class_name: LZ4Compressor
    parameters:
        -
```

> Compression to apply to the commit log. If omitted, the commit log
> will be written uncompressed.  LZ4, Snappy, and Deflate compressors
> are supported.

### `commitlog_disk_access_mode`

<a id="commitlog_disk_access_mode"></a>

*Active* · `conf/cassandra.yaml` line 678

```yaml
commitlog_disk_access_mode: legacy
```

**In `cassandra_latest.yaml`**:

```yaml
commitlog_disk_access_mode: auto
```

> Set the disk access mode for writing commitlog segments. The allowed values are:
> - auto: version dependent optimal setting
> - legacy: the default mode as used in Cassandra 4.x and earlier (standard I/O when the commitlog is either
>   compressed or encrypted or mmap otherwise)
> - mmap: use memory mapped I/O - available only when the commitlog is neither compressed nor encrypted
> - direct: use direct I/O - available only when the commitlog is neither compressed nor encrypted
> - standard: use standard I/O - available only when the commitlog is compressed or encrypted
> The default setting is legacy when the storage compatibility is set to 4 or auto otherwise.

### `flush_compression`

<a id="flush_compression"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 693

```yaml
flush_compression: fast
```

> Compression to apply to SSTables as they flush for compressed tables.
> Note that tables without compression enabled do not respect this flag.
>
> As high ratio compressors like LZ4HC, Zstd, and Deflate can potentially
> block flushes for too long, the default is to flush with a known fast
> compressor in those cases. Options are:
>
> none : Flush without compressing blocks but while still doing checksums.
> fast : Flush with a fast compressor. If the table is already using a
>        fast compressor that compressor is used.
> table: Always flush with the same compressor that the table uses. This
>        was the pre 4.0 behavior.

### `seed_provider`

<a id="seed_provider"></a>

*Active* · `conf/cassandra.yaml` line 697

```yaml
seed_provider:
  # Addresses of hosts that are deemed contact points.
  # Cassandra nodes use this list of hosts to find each other and learn
  # the topology of the ring.  You must change this if you are running
  # multiple nodes!
  - class_name: org.apache.cassandra.locator.SimpleSeedProvider
    parameters:
      # seeds is actually a comma-delimited list of addresses.
      # Ex: "<ip1>,<ip2>,<ip3>"
      - seeds: "127.0.0.1:7000"
      # If set to "true", SimpleSeedProvider will return all IP addresses for a DNS name,
      # based on the configured name service on the system. Defaults to "false".
      #  resolve_multiple_ip_addresses_per_dns_record: "false"
```

> any class that implements the SeedProvider interface and has a
> constructor that takes a Map<String, String> of parameters will do.

### `concurrent_reads`

<a id="concurrent_reads"></a>

*Active* · `conf/cassandra.yaml` line 722

```yaml
concurrent_reads: 32
```

> For workloads with more data than can fit in memory, Cassandra's
> bottleneck will be reads that need to fetch data from
> disk. "concurrent_reads" should be set to (16 * number_of_drives) in
> order to allow the operations to enqueue low enough in the stack
> that the OS and drives can reorder them. Same applies to
> "concurrent_counter_writes", since counter writes read the current
> values before incrementing and writing them back.
>
> On the other hand, since writes are almost never IO bound, the ideal
> number of "concurrent_writes" is dependent on the number of cores in
> your system; (8 * number_of_cores) is a good rule of thumb.

### `concurrent_writes`

<a id="concurrent_writes"></a>

*Active* · `conf/cassandra.yaml` line 723

```yaml
concurrent_writes: 32
```

See the description of [`concurrent_reads`](#concurrent_reads), which this setting accompanies in the yaml.

### `concurrent_counter_writes`

<a id="concurrent_counter_writes"></a>

*Active* · `conf/cassandra.yaml` line 724

```yaml
concurrent_counter_writes: 32
```

See the description of [`concurrent_writes`](#concurrent_writes), which this setting accompanies in the yaml.

### `concurrent_materialized_view_writes`

<a id="concurrent_materialized_view_writes"></a>

*Active* · `conf/cassandra.yaml` line 728

```yaml
concurrent_materialized_view_writes: 32
```

> For materialized view writes, as there is a read involved, so this should
> be limited by the less of concurrent reads or concurrent writes.

### `networking_cache_size`

<a id="networking_cache_size"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 738
 · deprecated old name(s): `networking_cache_size_in_mb`

```yaml
networking_cache_size: 128MiB
```

> Maximum memory to use for inter-node and client-server networking buffers.
>
> Defaults to the smaller of 1/16 of heap or 128MB. This pool is allocated off-heap,
> so is in addition to the memory allocated for heap. The cache also has on-heap
> overhead which is roughly 128 bytes per chunk (i.e. 0.2% of the reserved size
> if the default 64k chunk size is used).
> Memory is only allocated when needed.
> Min unit: MiB

### `file_cache_enabled`

<a id="file_cache_enabled"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 742

```yaml
file_cache_enabled: false
```

> Enable the sstable chunk cache.  The chunk cache will store recently accessed
> sections of the sstable in-memory as uncompressed buffers.

### `file_cache_size`

<a id="file_cache_size"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 753
 · deprecated old name(s): `file_cache_size_in_mb`

```yaml
file_cache_size: 512MiB
```

> Maximum memory to use for sstable chunk cache and buffer pooling.
> 32MB of this are reserved for pooling buffers, the rest is used for chunk cache
> that holds uncompressed sstable chunks.
> Defaults to the smaller of 1/4 of heap or 512MB. This pool is allocated off-heap,
> so is in addition to the memory allocated for heap. The cache also has on-heap
> overhead which is roughly 128 bytes per chunk (i.e. 0.2% of the reserved size
> if the default 64k chunk size is used).
> Memory is only allocated when needed.
> Min unit: MiB

### `buffer_pool_use_heap_if_exhausted`

<a id="buffer_pool_use_heap_if_exhausted"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 759

```yaml
buffer_pool_use_heap_if_exhausted: true
```

### `disk_optimization_strategy`

<a id="disk_optimization_strategy"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 765

```yaml
disk_optimization_strategy: ssd
```

> The strategy for optimizing disk read
> Possible values are:
> ssd (for solid state disks, the default)
> spinning (for spinning disks)

### `memtable`

<a id="memtable"></a>

*Active* · `conf/cassandra.yaml` line 783

```yaml
memtable:
  configurations:
    skiplist:
      class_name: SkipListMemtable
    trie:
      class_name: TrieMemtable
    default:
      inherits: skiplist
```

**In `cassandra_latest.yaml`**:

```yaml
memtable:
  configurations:
    skiplist:
      class_name: SkipListMemtable
    trie:
      class_name: TrieMemtable
    default:
      inherits: trie
```

> Supported memtable implementations and selected default.
> Currently Cassandra offers two memtable implementations:
> - SkipListMemtable is the legacy memtable implementation provided by earlier
>   versions of Cassandra.
> - TrieMemtable is a new memtable that utilizes a trie data structure. This
>   implementation significantly reduces garbage collection load by moving
>   more of the sstable metadata off-heap, fits more data in the same allocation
>   and can reliably handle higher write throughput.
>   Because the trie memtable is a sharded single-writer solution, it can perform
>   worse when the load is very unevenly distributed, e.g. when most of the writes
>   access a very small number of partitions or with legacy secondary indexes.
> The memtable implementation can be selected per table by setting memtable
> property in the table definition to one of the configurations specified below.
> If the memtable property is not set, the "default" configuration will be used.
> See src/java/org/apache/cassandra/db/memtable/Memtable_API.md for further
> information.

### `memtable_heap_space`

<a id="memtable_heap_space"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 800
 · deprecated old name(s): `memtable_heap_space_in_mb`

```yaml
memtable_heap_space: 2048MiB
```

> Total permitted memory to use for memtables. Cassandra will stop
> accepting writes when the limit is exceeded until a flush completes,
> and will trigger a flush based on memtable_cleanup_threshold
> If omitted, Cassandra will set both to 1/4 the size of the heap.
> memtable_heap_space must be positive. memtable_offheap_space may be 0
> only for the memtable_allocation_type values that never allocate
> off-heap: heap_buffers and unslabbed_heap_buffers.
> Min unit: MiB

### `memtable_offheap_space`

<a id="memtable_offheap_space"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 802
 · deprecated old name(s): `memtable_offheap_space_in_mb`

```yaml
memtable_offheap_space: 2048MiB
```

> Min unit: MiB

See the description of [`memtable_heap_space`](#memtable_heap_space), which this setting accompanies in the yaml.

### `memtable_cleanup_threshold`

<a id="memtable_cleanup_threshold"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 815

```yaml
memtable_cleanup_threshold: 0.11
```

> memtable_cleanup_threshold is deprecated. The default calculation
> is the only reasonable choice. See the comments on  memtable_flush_writers
> for more information.
>
> Ratio of occupied non-flushing memtable size to total permitted size
> that will trigger a flush of the largest memtable. Larger mct will
> mean larger flushes and hence less compaction, but also less concurrent
> flush activity which can make it difficult to keep your disks fed
> under heavy write load.
>
> memtable_cleanup_threshold defaults to 1 / (memtable_flush_writers + 1)

### `memtable_allocation_type`

<a id="memtable_allocation_type"></a>

*Active* · `conf/cassandra.yaml` line 828

```yaml
memtable_allocation_type: heap_buffers
```

**In `cassandra_latest.yaml`**:

```yaml
memtable_allocation_type: offheap_objects
```

> Specify the way Cassandra allocates and manages memtable memory.
> Options are:
>
> heap_buffers
>   on heap nio buffers
>
> offheap_buffers
>   off heap (direct) nio buffers
>
> offheap_objects
>    off heap objects

### `repair_session_space`

<a id="repair_session_space"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 843
 · deprecated old name(s): `repair_session_space_in_mb`

```yaml
repair_session_space:
```

> Limit memory usage for Merkle tree calculations during repairs of a certain
> table and common token range. Repair commands targeting multiple tables or
> virtual nodes can exceed this limit depending on concurrent_merkle_tree_requests.
>
> The default is 1/16th of the available heap. The main tradeoff is that
> smaller trees have less resolution, which can lead to over-streaming data.
> If you see heap pressure during repairs, consider lowering this, but you
> cannot go below one mebibyte. If you see lots of over-streaming, consider
> raising this or using subrange repair.
>
> For more details see https://issues.apache.org/jira/browse/CASSANDRA-14096.
>
> Min unit: MiB

### `concurrent_merkle_tree_requests`

<a id="concurrent_merkle_tree_requests"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 864

```yaml
concurrent_merkle_tree_requests: 0
```

> The number of simultaneous Merkle tree requests during repairs that can
> be performed by a repair command. The size of each validation request is
> limited by the repair_session_space property, so setting this to 1 will make
> sure that a repair command doesn't exceed that limit, even if the repair
> command is repairing multiple tables or multiple virtual nodes.
>
> There isn't a limit by default for backwards compatibility, but this can
> produce OOM for  commands repairing multiple tables or multiple virtual nodes.
> A limit of just 1 simultaneous Merkle tree request is generally recommended
> with no virtual nodes so repair_session_space, and thereof the Merkle tree
> resolution, can be high. For virtual nodes a value of 1 with the default
> repair_session_space value will produce higher resolution Merkle trees
> at the expense of speed. Alternatively, when working with virtual nodes it
> can make sense to reduce the repair_session_space and increase the value of
> concurrent_merkle_tree_requests because each range will contain fewer data.
>
> For more details see https://issues.apache.org/jira/browse/CASSANDRA-19336.
>
> A zero value means no limit.

### `repair`

<a id="repair"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 866

```yaml
repair:
  # Configure the retries for each of the repair messages that support it.  As of this moment retries use an exponential algorithm where each attempt sleeps longer based off the base_sleep_time and attempt.
  retries:
    max_attempts: 10
    base_sleep_time: 200ms
    max_sleep_time: 1s
    # Increase the timeout of validation responses due to them containing the merkle tree
    merkle_tree_response:
      base_sleep_time: 30s
      max_sleep_time: 1m
```

### `commitlog_total_space`

<a id="commitlog_total_space"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 886
 · deprecated old name(s): `commitlog_total_space_in_mb`

```yaml
commitlog_total_space: 8192MiB
```

> Total space to use for commit logs on disk.
>
> If space gets above this value, Cassandra will flush every dirty CF
> in the oldest segment and remove it.  So a small total commitlog space
> will tend to cause more flush activity on less-active columnfamilies.
>
> The default value is the smaller of 8192, and 1/4 of the total space
> of the commitlog volume.

### `memtable_flush_writers`

<a id="memtable_flush_writers"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 915

```yaml
memtable_flush_writers: 2
```

> This sets the number of memtable flush writer threads per disk
> as well as the total number of memtables that can be flushed concurrently.
> These are generally a combination of compute and IO bound.
>
> Memtable flushing is more CPU efficient than memtable ingest and a single thread
> can keep up with the ingest rate of a whole server on a single fast disk
> until it temporarily becomes IO bound under contention typically with compaction.
> At that point you need multiple flush threads. At some point in the future
> it may become CPU bound all the time.
>
> You can tell if flushing is falling behind using the MemtablePool.BlockedOnAllocation
> metric which should be 0, but will be non-zero if threads are blocked waiting on flushing
> to free memory.
>
> memtable_flush_writers defaults to two for a single data directory.
> This means that two  memtables can be flushed concurrently to the single data directory.
> If you have multiple data directories the default is one memtable flushing at a time
> but the flush will use a thread per data directory so you will get two or more writers.
>
> Two is generally enough to flush on a fast disk [array] mounted as a single data directory.
> Adding more flush writers will result in smaller more frequent flushes that introduce more
> compaction overhead.
>
> There is a direct tradeoff between number of memtables that can be flushed concurrently
> and flush size and frequency. More is not better you just need enough flush writers
> to never stall waiting for flushing to free memory.

### `cdc_total_space`

<a id="cdc_total_space"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 926
 · deprecated old name(s): `cdc_total_space_in_mb`

```yaml
cdc_total_space: 4096MiB
```

> Total space to use for change-data-capture logs on disk.
>
> If space gets above this value, Cassandra will throw WriteTimeoutException
> on Mutations including tables with CDC enabled. A CDCCompactor is responsible
> for parsing the raw CDC logs and deleting them when parsing is completed.
>
> The default value is the min of 4096 MiB and 1/8th of the total space
> of the drive where cdc_raw_directory resides.
> Min unit: MiB

### `cdc_free_space_check_interval`

<a id="cdc_free_space_check_interval"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 932
 · deprecated old name(s): `cdc_free_space_check_interval_ms`

```yaml
cdc_free_space_check_interval: 250ms
```

> When we hit our cdc_raw limit and the CDCCompactor is either running behind
> or experiencing backpressure, we check at the following interval to see if any
> new space for cdc-tracked tables has been made available. Default to 250ms
> Min unit: ms

### `index_summary_capacity`

<a id="index_summary_capacity"></a>

*Active* · `conf/cassandra.yaml` line 942
 · deprecated old name(s): `index_summary_capacity_in_mb`

```yaml
index_summary_capacity:
```

> A fixed memory pool size in MB for SSTable index summaries. If left
> empty, this will default to 5% of the heap size. If the memory usage of
> all index summaries exceeds this limit, SSTables with low read rates will
> shrink their index summaries in order to meet this limit.  However, this
> is a best-effort process. In extreme conditions Cassandra may need to use
> more than this amount of memory.
> Only relevant to formats that use an index summary, e.g. BIG.
> Min unit: KiB

### `index_summary_resize_interval`

<a id="index_summary_resize_interval"></a>

*Active* · `conf/cassandra.yaml` line 950
 · deprecated old name(s): `index_summary_resize_interval_in_minutes`

```yaml
index_summary_resize_interval: 60m
```

> How frequently index summaries should be resampled.  This is done
> periodically to redistribute memory from the fixed-size pool to sstables
> proportional their recent read rates.  Setting to null value will disable this
> process, leaving existing index summaries at their current sampling level.
> Only relevant to formats that use an index summary, e.g. BIG.
> Min unit: m

### `trickle_fsync`

<a id="trickle_fsync"></a>

*Active* · `conf/cassandra.yaml` line 957

```yaml
trickle_fsync: false
```

**In `cassandra_latest.yaml`**:

```yaml
trickle_fsync: true
```

> Whether to, when doing sequential writing, fsync() at intervals in
> order to force the operating system to flush the dirty
> buffers. Enable this to avoid sudden dirty buffer flushing from
> impacting read latencies. Almost always a good idea on SSDs; not
> necessarily on platters.

### `trickle_fsync_interval`

<a id="trickle_fsync_interval"></a>

*Active* · `conf/cassandra.yaml` line 961
 · deprecated old name(s): `trickle_fsync_interval_in_kb`

```yaml
trickle_fsync_interval: 10240KiB
```

> The interval is counted in uncompressed bytes, so for compressed SSTables
> (the default) an fsync fires after fewer bytes than this reach the disk.
> Min unit: KiB

### `storage_port`

<a id="storage_port"></a>

*Active* · `conf/cassandra.yaml` line 965

```yaml
storage_port: 7000
```

> TCP port, for commands and data
> For security reasons, you should not expose this port to the internet.  Firewall it if needed.

### `ssl_storage_port`

<a id="ssl_storage_port"></a>

*Active* · `conf/cassandra.yaml` line 971

```yaml
ssl_storage_port: 7001
```

> SSL port, for legacy encrypted communication. This property is unused unless enabled in
> server_encryption_options (see below). As of cassandra 4.0, this property is deprecated
> as a single port can be used for either/both secure and insecure connections.
> For security reasons, you should not expose this port to the internet. Firewall it if needed.

### `listen_address`

<a id="listen_address"></a>

*Active* · `conf/cassandra.yaml` line 986

```yaml
listen_address: localhost
```

> Address or interface to bind to and tell other Cassandra nodes to connect to.
> You _must_ change this if you want multiple nodes to be able to communicate!
>
> Set listen_address OR listen_interface, not both.
>
> Leaving it blank leaves it up to InetAddress.getLocalHost(). This
> will always do the Right Thing _if_ the node is properly configured
> (hostname, name resolution, etc), and the Right Thing is to use the
> address associated with the hostname (it might not be). If unresolvable
> it will fall back to InetAddress.getLoopbackAddress(), which is wrong for production systems.
>
> Setting listen_address to 0.0.0.0 is always wrong.

### `listen_interface`

<a id="listen_interface"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 990

```yaml
listen_interface: eth0
```

> Set listen_address OR listen_interface, not both. Interfaces must correspond
> to a single address, IP aliasing is not supported.

### `listen_interface_prefer_ipv6`

<a id="listen_interface_prefer_ipv6"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 996

```yaml
listen_interface_prefer_ipv6: false
```

> If you choose to specify the interface by name and the interface has an ipv4 and an ipv6 address
> you can specify which should be chosen using listen_interface_prefer_ipv6. If false the first ipv4
> address will be used. If true the first ipv6 address will be used. Defaults to false preferring
> ipv4. If there is only one address it will be selected regardless of ipv4/ipv6.

### `broadcast_address`

<a id="broadcast_address"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1000

```yaml
broadcast_address: 1.2.3.4
```

> Address to broadcast to other Cassandra nodes
> Leaving this blank will set it to the same value as listen_address

### `listen_on_broadcast_address`

<a id="listen_on_broadcast_address"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1008

```yaml
listen_on_broadcast_address: false
```

> When using multiple physical network interfaces, set this
> to true to listen on broadcast_address in addition to
> the listen_address, allowing nodes to communicate in both
> interfaces.
> Ignore this property if the network configuration automatically
> routes  between the public and private networks such as EC2.

### `internode_authenticator`

<a id="internode_authenticator"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1012

```yaml
internode_authenticator:
 class_name: org.apache.cassandra.auth.AllowAllInternodeAuthenticator
 parameters:
```

> Internode authentication backend, implementing IInternodeAuthenticator;
> used to allow/disallow connections from peer nodes.

### `start_native_transport`

<a id="start_native_transport"></a>

*Active* · `conf/cassandra.yaml` line 1025

```yaml
start_native_transport: true
```

>  class_name: org.apache.cassandra.auth.AllowAllInternodeAuthenticator
>  parameters:
> MutualTlsInternodeAuthenticator can be configured using the following configuration.One can add their own validator
> which implements MutualTlsCertificateValidator class and provide logic for extracting identity out of certificates
> and validating certificates.
>  class_name: org.apache.cassandra.auth.MutualTlsInternodeAuthenticator
>  parameters:
>    validator_class_name: org.apache.cassandra.auth.SpiffeCertificateValidator
>    trusted_peer_identities: "spiffe1,spiffe2"
>    node_identity: "spiffe1"
> Whether to start the native transport server.
> The address on which the native transport is bound is defined by rpc_address.

### `native_transport_port`

<a id="native_transport_port"></a>

*Active* · `conf/cassandra.yaml` line 1028

```yaml
native_transport_port: 9042
```

> port for the CQL native transport to listen for clients on
> For security reasons, you should not expose this port to the internet.  Firewall it if needed.

### `native_transport_port_ssl`

<a id="native_transport_port_ssl"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1037

```yaml
native_transport_port_ssl: 9142
```

> Enabling native transport encryption in client_encryption_options allows you to either use
> encryption for the standard port or to use a dedicated, additional port along with the unencrypted
> standard native_transport_port.
> Enabling client encryption and keeping native_transport_port_ssl disabled will use encryption
> for native_transport_port. Setting native_transport_port_ssl to a different value
> from native_transport_port will use encryption for native_transport_port_ssl while
> keeping native_transport_port unencrypted.
> This feature is deprecated since Cassandra 5.0 and will be removed. Please consult deprecation section in NEWS.txt.

### `native_transport_max_threads`

<a id="native_transport_max_threads"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1040

```yaml
native_transport_max_threads: 128
```

> The maximum threads for handling requests (note that idle threads are stopped
> after 30 seconds so there is not corresponding minimum setting).

### `native_transport_max_auth_threads`

<a id="native_transport_max_auth_threads"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1043

```yaml
native_transport_max_auth_threads: 4
```

> The maximum threads for handling auth requests in a separate executor from main request executor.
> When set to 0, main executor for requests is used.

### `native_transport_max_frame_size`

<a id="native_transport_max_frame_size"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1049
 · deprecated old name(s): `native_transport_max_frame_size_in_mb`

```yaml
native_transport_max_frame_size: 16MiB
```

> The maximum size of allowed frame. Frame (requests) larger than this will
> be rejected as invalid. The default is 16MiB. If you're changing this parameter,
> you may want to adjust max_value_size accordingly. This should be positive and less than 2048.
> Min unit: MiB

### `native_transport_max_concurrent_connections`

<a id="native_transport_max_concurrent_connections"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1053

```yaml
native_transport_max_concurrent_connections: -1
```

> The maximum number of concurrent client connections.
> The default is -1, which means unlimited.

### `native_transport_max_concurrent_connections_per_ip`

<a id="native_transport_max_concurrent_connections_per_ip"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1057

```yaml
native_transport_max_concurrent_connections_per_ip: -1
```

> The maximum number of concurrent client connections per source ip.
> The default is -1, which means unlimited.

### `native_transport_allow_older_protocols`

<a id="native_transport_allow_older_protocols"></a>

*Active* · `conf/cassandra.yaml` line 1061

```yaml
native_transport_allow_older_protocols: true
```

> Controls whether Cassandra honors older, yet currently supported, protocol versions.
> The default is true, which means all supported protocols will be honored.

### `native_transport_idle_timeout`

<a id="native_transport_idle_timeout"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1072
 · deprecated old name(s): `native_transport_idle_timeout_in_ms`

```yaml
native_transport_idle_timeout: 60000ms
```

> Controls when idle client connections are closed. Idle connections are ones that had neither reads
> nor writes for a time period.
>
> Clients may implement heartbeats by sending OPTIONS native protocol message after a timeout, which
> will reset idle timeout timer on the server side. To close idle client connections, corresponding
> values for heartbeat intervals have to be set on the client side.
>
> Idle connection timeouts are disabled by default.
> Min unit: ms

### `native_transport_rate_limiting_enabled`

<a id="native_transport_rate_limiting_enabled"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1081

```yaml
native_transport_rate_limiting_enabled: false
```

> When enabled, limits the number of native transport requests dispatched for processing per second.
> Behavior once the limit has been breached depends on the value of THROW_ON_OVERLOAD specified in
> the STARTUP message sent by the client during connection establishment. (See section "4.1.1. STARTUP"
> in "CQL BINARY PROTOCOL v5".) With the THROW_ON_OVERLOAD flag enabled, messages that breach the limit
> are dropped, and an OverloadedException is thrown for the client to handle. When the flag is not
> enabled, the server will stop consuming messages from the channel/socket, putting backpressure on
> the client while already dispatched messages are processed.

### `native_transport_max_requests_per_second`

<a id="native_transport_max_requests_per_second"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1082

```yaml
native_transport_max_requests_per_second: 1000000
```

See the description of [`native_transport_rate_limiting_enabled`](#native_transport_rate_limiting_enabled), which this setting accompanies in the yaml.

### `rpc_address`

<a id="rpc_address"></a>

*Active* · `conf/cassandra.yaml` line 1095

```yaml
rpc_address: localhost
```

> The address or interface to bind the native transport server to.
>
> Set rpc_address OR rpc_interface, not both.
>
> Leaving rpc_address blank has the same effect as on listen_address
> (i.e. it will be based on the configured hostname of the node).
>
> Note that unlike listen_address, you can specify 0.0.0.0, but you must also
> set broadcast_rpc_address to a value other than 0.0.0.0.
>
> For security reasons, you should not expose this port to the internet.  Firewall it if needed.

### `rpc_interface`

<a id="rpc_interface"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1099

```yaml
rpc_interface: eth1
```

> Set rpc_address OR rpc_interface, not both. Interfaces must correspond
> to a single address, IP aliasing is not supported.

### `rpc_interface_prefer_ipv6`

<a id="rpc_interface_prefer_ipv6"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1105

```yaml
rpc_interface_prefer_ipv6: false
```

> If you choose to specify the interface by name and the interface has an ipv4 and an ipv6 address
> you can specify which should be chosen using rpc_interface_prefer_ipv6. If false the first ipv4
> address will be used. If true the first ipv6 address will be used. Defaults to false preferring
> ipv4. If there is only one address it will be selected regardless of ipv4/ipv6.

### `broadcast_rpc_address`

<a id="broadcast_rpc_address"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1111

```yaml
broadcast_rpc_address: 1.2.3.4
```

> RPC address to broadcast to drivers and other Cassandra nodes. This cannot
> be set to 0.0.0.0. If left blank, this will be set to the value of
> rpc_address. If rpc_address is set to 0.0.0.0, broadcast_rpc_address must
> be set.

### `rpc_keepalive`

<a id="rpc_keepalive"></a>

*Active* · `conf/cassandra.yaml` line 1114

```yaml
rpc_keepalive: true
```

> enable or disable keepalive on rpc/native connections

### `internode_socket_send_buffer_size`

<a id="internode_socket_send_buffer_size"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1126
 · deprecated old name(s): `internode_send_buff_size_in_bytes`, `internode_socket_send_buffer_size_in_bytes`

```yaml
internode_socket_send_buffer_size:
```

> Uncomment to set socket buffer size for internode communication
> Note that when setting this, the buffer size is limited by net.core.wmem_max
> and when not setting it it is defined by net.ipv4.tcp_wmem
> See also:
> /proc/sys/net/core/wmem_max
> /proc/sys/net/core/rmem_max
> /proc/sys/net/ipv4/tcp_wmem
> /proc/sys/net/ipv4/tcp_wmem
> and 'man tcp'
> Min unit: B

### `internode_socket_receive_buffer_size`

<a id="internode_socket_receive_buffer_size"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1132
 · deprecated old name(s): `internode_recv_buff_size_in_bytes`, `internode_socket_receive_buffer_size_in_bytes`

```yaml
internode_socket_receive_buffer_size:
```

> Uncomment to set socket buffer size for internode communication
> Note that when setting this, the buffer size is limited by net.core.wmem_max
> and when not setting it it is defined by net.ipv4.tcp_wmem
> Min unit: B

### `incremental_backups`

<a id="incremental_backups"></a>

*Active* · `conf/cassandra.yaml` line 1140

```yaml
incremental_backups: false
```

> Set to true to have Cassandra create a hard link to each sstable
> flushed or streamed locally in a backups/ subdirectory of all the
> keyspace data in this node.  Removing these links is the operator's
> responsibility. The operator can also turn off incremental backups
> for specified table by setting table parameter incremental_backups to
> false, which is set to true by default. See CASSANDRA-15402

### `snapshot_before_compaction`

<a id="snapshot_before_compaction"></a>

*Active* · `conf/cassandra.yaml` line 1146

```yaml
snapshot_before_compaction: false
```

> Whether or not to take a snapshot before each compaction.  Be
> careful using this option, since Cassandra won't clean up the
> snapshots for you.  Mostly useful if you're paranoid when there
> is a data format change.

### `auto_snapshot`

<a id="auto_snapshot"></a>

*Active* · `conf/cassandra.yaml` line 1152

```yaml
auto_snapshot: true
```

> Whether or not a snapshot is taken of the data before keyspace truncation
> or dropping of column families. The STRONGLY advised default of true
> should be used to provide data safety. If you set this flag to false, you will
> lose data on truncation or drop.

### `auto_snapshot_ttl`

<a id="auto_snapshot_ttl"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1160

```yaml
auto_snapshot_ttl: 30d
```

> Adds a time-to-live (TTL) to auto snapshots generated by table
> truncation or drop (when enabled).
> After the TTL is elapsed, the snapshot is automatically cleared.
> By default, auto snapshots *do not* have TTL, uncomment the property below
> to enable TTL on auto snapshots.
> Accepted units: d (days), h (hours) or m (minutes)

### `snapshot_links_per_second`

<a id="snapshot_links_per_second"></a>

*Active* · `conf/cassandra.yaml` line 1167

```yaml
snapshot_links_per_second: 0
```

> The act of creating or clearing a snapshot involves creating or removing
> potentially tens of thousands of links, which can cause significant performance
> impact, especially on consumer grade SSDs. A non-zero value here can
> be used to throttle these links to avoid negative performance impact of
> taking and clearing snapshots

### `sstable`

<a id="sstable"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1176

```yaml
sstable:
 selected_format: big
```

**In `cassandra_latest.yaml`**:

```yaml
sstable:
  selected_format: bti
```

> The sstable formats configuration. SSTable formats implementations are
> loaded using the service loader mechanism. In this section, one can select
> the format for created sstables and pass additional parameters for the formats
> available on the classpath.
> The default format is "big", the legacy SSTable format in use since Cassandra 3.0.
> Cassandra versions 5.0 and later also support the trie-indexed "bti" format,
> which offers better performance.

### `column_index_size`

<a id="column_index_size"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1193
 · deprecated old name(s): `column_index_size_in_kb`

```yaml
column_index_size: 4KiB
```

**In `cassandra_latest.yaml`**:

```yaml
column_index_size: 4KiB
```

> Granularity of the collation index of rows within a partition.
> Applies to both BIG and BTI SSTable formats. In both formats,
> a smaller granularity results in faster lookup of rows within
> a partition, but a bigger index file size.
> Using smaller granularities with the BIG format is not recommended
> because bigger collation indexes cannot be cached efficiently
> or at all if they become sufficiently large. Further, if
> large rows, or a very large number of rows per partition are
> present, it is recommended to increase the index granularity
> or switch to the BTI SSTable format.
>
> Leave undefined to use a default suitable for the SSTable format
> in use (64 KiB for BIG, 16KiB for BTI).
> Min unit: KiB

### `column_index_cache_size`

<a id="column_index_cache_size"></a>

*Active* · `conf/cassandra.yaml` line 1205
 · deprecated old name(s): `column_index_cache_size_in_kb`

```yaml
column_index_cache_size: 2KiB
```

> Per sstable indexed key cache entries (the collation index in memory
> mentioned above) exceeding this size will not be held on heap.
> This means that only partition information is held on heap and the
> index entries are read from disk.
>
> Note that this size refers to the size of the
> serialized index information and not the size of the partition.
>
> This is only relevant to SSTable formats that use key cache, e.g. BIG.
> Min unit: KiB

### `default_compaction`

<a id="default_compaction"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1214

```yaml
default_compaction:
  class_name: SizeTieredCompactionStrategy
  parameters:
    min_threshold: 4
    max_threshold: 32
```

**In `cassandra_latest.yaml`**:

```yaml
default_compaction:
  class_name: UnifiedCompactionStrategy
  parameters:
    scaling_parameters: T4
    max_sstables_to_compact: 64
    target_sstable_size: 1GiB
    sstable_growth: 0.3333333333333333
    min_sstable_size: 100MiB
```

> Default compaction strategy, applied when a table's parameters do not
> specify compaction.
> The selected compaction strategy will also apply to system tables.
>
> If no value is specified, the default is to use SizeTieredCompactionStrategy,
> with its default compaction parameters.

### `concurrent_compactors`

<a id="concurrent_compactors"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1235

```yaml
concurrent_compactors: 1
```

**In `cassandra_latest.yaml`**:

```yaml
concurrent_compactors: 8
```

> Number of simultaneous compactions to allow, NOT including
> validation "compactions" for anti-entropy repair.  Simultaneous
> compactions can help preserve read performance in a mixed read/write
> workload, by mitigating the tendency of small sstables to accumulate
> during a single long running compactions. The default is usually
> fine and if you experience problems with compaction running too
> slowly or too fast, you should look at
> compaction_throughput first.
>
> concurrent_compactors defaults to the smaller of (number of disks,
> number of cores), with a minimum of 2 and a maximum of 8.
>
> If your data directories are backed by SSD, you should increase this
> to the number of cores.

### `concurrent_validations`

<a id="concurrent_validations"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1244

```yaml
concurrent_validations: 0
```

> Number of simultaneous repair validations to allow. If not set or set to
> a value less than 1, it defaults to the value of concurrent_compactors.
> To set a value greater than concurrent_compactors at startup, the system
> property cassandra.allow_unlimited_concurrent_validations must be set to
> true. To dynamically resize to a value > concurrent_compactors on a running
> node, first call the bypassConcurrentValidatorsLimit method on the
> org.apache.cassandra.db:type=StorageService mbean

### `concurrent_materialized_view_builders`

<a id="concurrent_materialized_view_builders"></a>

*Active* · `conf/cassandra.yaml` line 1247

```yaml
concurrent_materialized_view_builders: 1
```

> Number of simultaneous materialized view builder tasks to allow.

### `compaction_throughput`

<a id="compaction_throughput"></a>

*Active* · `conf/cassandra.yaml` line 1256
 · deprecated old name(s): `compaction_throughput_mb_per_sec`

```yaml
compaction_throughput: 64MiB/s
```

> Throttles compaction to the given total throughput across the entire
> system. The faster you insert data, the faster you need to compact in
> order to keep the sstable count down, but in general, setting this to
> 16 to 32 times the rate you are inserting data is more than sufficient.
> Setting this to 0 disables throttling. Note that this accounts for all types
> of compaction, including validation compaction (building Merkle trees
> for repairs).

### `sstable_preemptive_open_interval`

<a id="sstable_preemptive_open_interval"></a>

*Active* · `conf/cassandra.yaml` line 1265
 · deprecated old name(s): `sstable_preemptive_open_interval_in_mb`

```yaml
sstable_preemptive_open_interval: 50MiB
```

> When compacting, the replacement sstable(s) can be opened before they
> are completely written, and used in place of the prior sstables for
> any range that has been written. This helps to smoothly transfer reads
> between the sstables, reducing page cache churn and keeping hot rows hot
> Set sstable_preemptive_open_interval to null for disabled which is equivalent to
> sstable_preemptive_open_interval_in_mb being negative
> Min unit: MiB

### `uuid_sstable_identifiers_enabled`

<a id="uuid_sstable_identifiers_enabled"></a>

*Active* · `conf/cassandra.yaml` line 1272

```yaml
uuid_sstable_identifiers_enabled: false
```

**In `cassandra_latest.yaml`**:

```yaml
uuid_sstable_identifiers_enabled: true
```

> Starting from 4.1 sstables support UUID based generation identifiers. They are disabled by default
> because once enabled, there is no easy way to downgrade. When the node is restarted with this option
> set to true, each newly created sstable will have a UUID based generation identifier and such files are
> not readable by previous Cassandra versions. At some point, this option will become true by default
> and eventually get removed from the configuration.

### `stream_entire_sstables`

<a id="stream_entire_sstables"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1284

```yaml
stream_entire_sstables: true
```

**In `cassandra_latest.yaml`**:

```yaml
stream_entire_sstables: true
```

> When enabled, permits Cassandra to zero-copy stream entire eligible
> SSTables between nodes, including every component.
> This speeds up the network transfer significantly subject to
> throttling specified by entire_sstable_stream_throughput_outbound,
> and entire_sstable_inter_dc_stream_throughput_outbound
> for inter-DC transfers.
> Enabling this will reduce the GC pressure on sending and receiving node.
> When unset, the default is enabled. While this feature tries to keep the
> disks balanced, it cannot guarantee it. This feature will be automatically
> disabled if internode encryption is enabled.

### `entire_sstable_stream_digest_validation_enabled`

<a id="entire_sstable_stream_digest_validation_enabled"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1292

```yaml
entire_sstable_stream_digest_validation_enabled: false
```

> When an entire SSTable is received via zero-copy streaming, validate the Digest.crc32 that was streamed with it
> against the received Data.db before the SSTable is added to the table. This detects corruption introduced in
> transit as well as pre-existing corruption on the sending node's disk, neither of which is otherwise noticed by
> this path, since it writes component bytes to disk without parsing them.
> If there's no Digest.crc32, this check passes.
> When unset, the default is not validating Digest.crc32.

### `entire_sstable_stream_throughput_outbound`

<a id="entire_sstable_stream_throughput_outbound"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1298

```yaml
entire_sstable_stream_throughput_outbound: 24MiB/s
```

> Throttles entire SSTable outbound streaming file transfers on
> this node to the given total throughput in Mbps.
> Setting this value to 0 it disables throttling.
> When unset, the default is 200 Mbps or 24 MiB/s.

### `entire_sstable_inter_dc_stream_throughput_outbound`

<a id="entire_sstable_inter_dc_stream_throughput_outbound"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1303

```yaml
entire_sstable_inter_dc_stream_throughput_outbound: 24MiB/s
```

> Throttles entire SSTable file streaming between datacenters.
> Setting this value to 0 disables throttling for entire SSTable inter-DC file streaming.
> When unset, the default is 200 Mbps or 24 MiB/s.

### `stream_throughput_outbound`

<a id="stream_throughput_outbound"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1310
 · deprecated old name(s): `stream_throughput_outbound_megabits_per_sec`

```yaml
stream_throughput_outbound: 24MiB/s
```

> Throttles all outbound streaming file transfers on this node to the
> given total throughput in Mbps. This is necessary because Cassandra does
> mostly sequential IO when streaming data during bootstrap or repair, which
> can lead to saturating the network connection and degrading rpc performance.
> When unset, the default is 200 Mbps or 24 MiB/s.

### `inter_dc_stream_throughput_outbound`

<a id="inter_dc_stream_throughput_outbound"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1317
 · deprecated old name(s): `inter_dc_stream_throughput_outbound_megabits_per_sec`

```yaml
inter_dc_stream_throughput_outbound: 24MiB/s
```

> Throttles all streaming file transfer between the datacenters,
> this setting allows users to throttle inter dc stream throughput in addition
> to throttling all network stream traffic as configured with
> stream_throughput_outbound_megabits_per_sec
> When unset, the default is 200 Mbps or 24 MiB/s.

### `read_request_timeout`

<a id="read_request_timeout"></a>

*Active* · `conf/cassandra.yaml` line 1335
 · deprecated old name(s): `read_request_timeout_in_ms`

```yaml
read_request_timeout: 5000ms
```

> How long the coordinator should wait for read operations to complete.
> Lowest acceptable value is 10 ms.
> Min unit: ms

### `range_request_timeout`

<a id="range_request_timeout"></a>

*Active* · `conf/cassandra.yaml` line 1339
 · deprecated old name(s): `range_request_timeout_in_ms`

```yaml
range_request_timeout: 10000ms
```

> How long the coordinator should wait for seq or index scans to complete.
> Lowest acceptable value is 10 ms.
> Min unit: ms

### `write_request_timeout`

<a id="write_request_timeout"></a>

*Active* · `conf/cassandra.yaml` line 1343
 · deprecated old name(s): `write_request_timeout_in_ms`

```yaml
write_request_timeout: 2000ms
```

> How long the coordinator should wait for writes to complete.
> Lowest acceptable value is 10 ms.
> Min unit: ms

### `counter_write_request_timeout`

<a id="counter_write_request_timeout"></a>

*Active* · `conf/cassandra.yaml` line 1347
 · deprecated old name(s): `counter_write_request_timeout_in_ms`

```yaml
counter_write_request_timeout: 5000ms
```

> How long the coordinator should wait for counter writes to complete.
> Lowest acceptable value is 10 ms.
> Min unit: ms

### `cas_contention_timeout`

<a id="cas_contention_timeout"></a>

*Active* · `conf/cassandra.yaml` line 1352
 · deprecated old name(s): `cas_contention_timeout_in_ms`

```yaml
cas_contention_timeout: 1000ms
```

> How long a coordinator should continue to retry a CAS operation
> that contends with other proposals for the same row.
> Lowest acceptable value is 10 ms.
> Min unit: ms

### `truncate_request_timeout`

<a id="truncate_request_timeout"></a>

*Active* · `conf/cassandra.yaml` line 1358
 · deprecated old name(s): `truncate_request_timeout_in_ms`

```yaml
truncate_request_timeout: 60000ms
```

> How long the coordinator should wait for truncates to complete
> (This can be much longer, because unless auto_snapshot is disabled
> we need to flush first so we can snapshot before removing the data.)
> Lowest acceptable value is 10 ms.
> Min unit: ms

### `request_timeout`

<a id="request_timeout"></a>

*Active* · `conf/cassandra.yaml` line 1362
 · deprecated old name(s): `request_timeout_in_ms`

```yaml
request_timeout: 10000ms
```

> The default timeout for other, miscellaneous operations.
> Lowest acceptable value is 10 ms.
> Min unit: ms

### `internode_tcp_connect_timeout`

<a id="internode_tcp_connect_timeout"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1369
 · deprecated old name(s): `internode_tcp_connect_timeout_in_ms`

```yaml
internode_tcp_connect_timeout: 2000ms
```

> Defensive settings for protecting Cassandra from true network partitions.
> See (CASSANDRA-14358) for details.
>
> The amount of time to wait for internode tcp connections to establish.
> Min unit: ms

### `internode_tcp_user_timeout`

<a id="internode_tcp_user_timeout"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1376
 · deprecated old name(s): `internode_tcp_user_timeout_in_ms`

```yaml
internode_tcp_user_timeout: 30000ms
```

> The amount of time unacknowledged data is allowed on a connection before we throw out the connection
> Note this is only supported on Linux + epoll, and it appears to behave oddly above a setting of 30000
> (it takes much longer than 30s) as of Linux 4.12. If you want something that high set this to 0
> which picks up the OS default and configure the net.ipv4.tcp_retries2 sysctl to be ~8.
> Min unit: ms

### `internode_streaming_tcp_user_timeout`

<a id="internode_streaming_tcp_user_timeout"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1381
 · deprecated old name(s): `internode_streaming_tcp_user_timeout_in_ms`

```yaml
internode_streaming_tcp_user_timeout: 300000ms
```

> The amount of time unacknowledged data is allowed on a streaming connection.
> The default is 5 minutes. Increase it or set it to 0 in order to increase the timeout.
> Min unit: ms

### `internode_application_send_queue_capacity`

<a id="internode_application_send_queue_capacity"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1399
 · deprecated old name(s): `internode_application_send_queue_capacity_in_bytes`

```yaml
internode_application_send_queue_capacity: 4MiB
```

> Global, per-endpoint and per-connection limits imposed on messages queued for delivery to other nodes
> and waiting to be processed on arrival from other nodes in the cluster.  These limits are applied to the on-wire
> size of the message being sent or received.
>
> The basic per-link limit is consumed in isolation before any endpoint or global limit is imposed.
> Each node-pair has three links: urgent, small and large.  So any given node may have a maximum of
> N*3*(internode_application_send_queue_capacity+internode_application_receive_queue_capacity)
> messages queued without any coordination between them although in practice, with token-aware routing, only RF*tokens
> nodes should need to communicate with significant bandwidth.
>
> The per-endpoint limit is imposed on all messages exceeding the per-link limit, simultaneously with the global limit,
> on all links to or from a single node in the cluster.
> The global limit is imposed on all messages exceeding the per-link limit, simultaneously with the per-endpoint limit,
> on all links to or from any node in the cluster.
>
> Min unit: B

### `internode_application_send_queue_reserve_endpoint_capacity`

<a id="internode_application_send_queue_reserve_endpoint_capacity"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1400
 · deprecated old name(s): `internode_application_send_queue_reserve_endpoint_capacity_in_bytes`

```yaml
internode_application_send_queue_reserve_endpoint_capacity: 128MiB
```

See the description of [`internode_application_send_queue_capacity`](#internode_application_send_queue_capacity), which this setting accompanies in the yaml.

### `internode_application_send_queue_reserve_global_capacity`

<a id="internode_application_send_queue_reserve_global_capacity"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1401
 · deprecated old name(s): `internode_application_send_queue_reserve_global_capacity_in_bytes`

```yaml
internode_application_send_queue_reserve_global_capacity: 512MiB
```

See the description of [`internode_application_send_queue_reserve_endpoint_capacity`](#internode_application_send_queue_reserve_endpoint_capacity), which this setting accompanies in the yaml.

### `internode_application_receive_queue_capacity`

<a id="internode_application_receive_queue_capacity"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1402
 · deprecated old name(s): `internode_application_receive_queue_capacity_in_bytes`

```yaml
internode_application_receive_queue_capacity: 4MiB
```

See the description of [`internode_application_send_queue_reserve_global_capacity`](#internode_application_send_queue_reserve_global_capacity), which this setting accompanies in the yaml.

### `internode_application_receive_queue_reserve_endpoint_capacity`

<a id="internode_application_receive_queue_reserve_endpoint_capacity"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1403
 · deprecated old name(s): `internode_application_receive_queue_reserve_endpoint_capacity_in_bytes`

```yaml
internode_application_receive_queue_reserve_endpoint_capacity: 128MiB
```

See the description of [`internode_application_receive_queue_capacity`](#internode_application_receive_queue_capacity), which this setting accompanies in the yaml.

### `internode_application_receive_queue_reserve_global_capacity`

<a id="internode_application_receive_queue_reserve_global_capacity"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1404
 · deprecated old name(s): `internode_application_receive_queue_reserve_global_capacity_in_bytes`

```yaml
internode_application_receive_queue_reserve_global_capacity: 512MiB
```

See the description of [`internode_application_receive_queue_reserve_endpoint_capacity`](#internode_application_receive_queue_reserve_endpoint_capacity), which this setting accompanies in the yaml.

### `slow_query_log_timeout`

<a id="slow_query_log_timeout"></a>

*Active* · `conf/cassandra.yaml` line 1411
 · deprecated old name(s): `slow_query_log_timeout_in_ms`

```yaml
slow_query_log_timeout: 500ms
```

> How long before a node logs slow queries. Select queries that take longer than
> this timeout to execute, will generate an aggregated log message, so that slow queries
> can be identified. Set this value to zero to disable slow query logging.
> Min unit: ms

### `internode_timeout`

<a id="internode_timeout"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1421
 · deprecated old name(s): `cross_node_timeout`

```yaml
internode_timeout: true
```

> Enable operation timeout information exchange between nodes to accurately
> measure request timeouts.  If disabled, replicas will assume that requests
> were forwarded to them instantly by the coordinator, which means that
> under overload conditions we will waste that much extra time processing
> already-timed-out requests.
>
> Warning: It is generally assumed that users have setup NTP on their clusters, and that clocks are modestly in sync,
> since this is a requirement for general correctness of last write wins.

### `streaming_keep_alive_period`

<a id="streaming_keep_alive_period"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1432
 · deprecated old name(s): `streaming_keep_alive_period_in_secs`

```yaml
streaming_keep_alive_period: 300s
```

> Set period for idle state control messages for earlier detection of failed streams
> This node will send a keep-alive message periodically on the streaming's control channel.
> This ensures that any eventual SocketTimeoutException will occur within 2 keep-alive cycles
> If the node cannot send, or timeouts sending, the keep-alive message on the netty control channel
> the stream session is closed.
> Default value is 300s (5 minutes), which means stalled streams
> are detected within 10 minutes
> Specify 0 to disable.
> Min unit: s

### `streaming_connections_per_host`

<a id="streaming_connections_per_host"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1437

```yaml
streaming_connections_per_host: 1
```

> Limit number of connections per host for streaming
> Increase this when you notice that joins are CPU-bound rather that network
> bound (for example a few nodes with big files).

### `streaming_state_expires`

<a id="streaming_state_expires"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1442

```yaml
streaming_state_expires: 3d
```

> Settings for stream stats tracking; used by system_views.streaming table
> How long before a stream is evicted from tracking; this impacts both historic and currently running
> streams.

### `streaming_state_size`

<a id="streaming_state_size"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1445

```yaml
streaming_state_size: 40MiB
```

> How much memory may be used for tracking before evicting session from tracking; once crossed
> historic and currently running streams maybe impacted.

### `streaming_stats_enabled`

<a id="streaming_stats_enabled"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1447

```yaml
streaming_stats_enabled: true
```

> Enable/Disable tracking of streaming stats

### `partition_denylist_enabled`

<a id="partition_denylist_enabled"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1451

```yaml
partition_denylist_enabled: false
```

> Allows denying configurable access (rw/rr) to operations on configured ks, table, and partitions, intended for use by
> operators to manage cluster health vs application access. See CASSANDRA-12106 and CEP-13 for more details.

### `denylist_writes_enabled`

<a id="denylist_writes_enabled"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1453

```yaml
denylist_writes_enabled: true
```

### `denylist_reads_enabled`

<a id="denylist_reads_enabled"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1454

```yaml
denylist_reads_enabled: true
```

See the description of [`denylist_writes_enabled`](#denylist_writes_enabled), which this setting accompanies in the yaml.

### `denylist_range_reads_enabled`

<a id="denylist_range_reads_enabled"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1455

```yaml
denylist_range_reads_enabled: true
```

See the description of [`denylist_reads_enabled`](#denylist_reads_enabled), which this setting accompanies in the yaml.

### `denylist_refresh`

<a id="denylist_refresh"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1461

```yaml
denylist_refresh: 600s
```

> The interval at which keys in the cache for denylisting will "expire" and async refresh from the backing DB.
> Note: this serves only as a fail-safe, as the usage pattern is expected to be "mutate state, refresh cache" on any
> changes to the underlying denylist entries. See documentation for details.
> Min unit: s

### `denylist_initial_load_retry`

<a id="denylist_initial_load_retry"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1465

```yaml
denylist_initial_load_retry: 5s
```

> In the event of errors on attempting to load the denylist cache, retry on this interval.
> Min unit: s

### `denylist_max_keys_per_table`

<a id="denylist_max_keys_per_table"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1470

```yaml
denylist_max_keys_per_table: 1000
```

> We cap the number of denylisted keys allowed per table to keep things from growing unbounded. Nodes will warn above
> this limit while allowing new denylisted keys to be inserted. Denied keys are loaded in natural query / clustering
> ordering by partition key in case of overflow.

### `denylist_max_keys_total`

<a id="denylist_max_keys_total"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1475

```yaml
denylist_max_keys_total: 10000
```

> We cap the total number of denylisted keys allowed in the cluster to keep things from growing unbounded.
> Nodes will warn on initial cache load that there are too many keys and be direct the operator to trim down excess
> entries to within the configured limits.

### `denylist_consistency_level`

<a id="denylist_consistency_level"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1480

```yaml
denylist_consistency_level: QUORUM
```

> Since the denylist in many ways serves to protect the health of the cluster from partitions operators have identified
> as being in a bad state, we usually want more robustness than just CL.ONE on operations to/from these tables to
> ensure that these safeguards are in place. That said, we allow users to configure this if they're so inclined.

### `phi_convict_threshold`

<a id="phi_convict_threshold"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1484

```yaml
phi_convict_threshold: 8
```

> phi value that must be reached for a host to be marked down.
> most users should never need to adjust this.

### `endpoint_snitch`

<a id="endpoint_snitch"></a>

*Active* · `conf/cassandra.yaml` line 1569

```yaml
endpoint_snitch: SimpleSnitch
```

> endpoint_snitch -- Set this to a class that implements
> IEndpointSnitch.  The snitch has two functions:
>
> - it teaches Cassandra enough about your network topology to route
>   requests efficiently
> - it allows Cassandra to spread replicas around your cluster to avoid
>   correlated failures. It does this by grouping machines into
>   "datacenters" and "racks."  Cassandra will do its best not to have
>   more than one replica on the same "rack" (which may not actually
>   be a physical location)
>
> CASSANDRA WILL NOT ALLOW YOU TO SWITCH TO AN INCOMPATIBLE SNITCH
> ONCE DATA IS INSERTED INTO THE CLUSTER.  This would cause data loss.
> This means that if you start with the default SimpleSnitch, which
> locates every node on "rack1" in "datacenter1", your only options
> if you need to add another datacenter are GossipingPropertyFileSnitch
> (and the older PFS).  From there, if you want to migrate to an
> incompatible snitch like Ec2Snitch you can do it by adding new nodes
> under Ec2Snitch (which will locate them in a new "datacenter") and
> decommissioning the old ones.
>
> Out of the box, Cassandra provides:
>
> SimpleSnitch:
>    Treats Strategy order as proximity. This can improve cache
>    locality when disabling read repair.  Only appropriate for
>    single-datacenter deployments.
>
> GossipingPropertyFileSnitch
>    This should be your go-to snitch for production use.  The rack
>    and datacenter for the local node are defined in
>    cassandra-rackdc.properties and propagated to other nodes via
>    gossip.  If cassandra-topology.properties exists, it is used as a
>    fallback, allowing migration from the PropertyFileSnitch.
>
> PropertyFileSnitch:
>    Proximity is determined by rack and data center, which are
>    explicitly configured in cassandra-topology.properties.
>
> AlibabaCloudSnitch:
>    Snitch for getting dc and rack of a node from metadata service of Alibaba cloud.
>    This snitch that assumes an ECS region is a DC and an ECS availability_zone is a rack.
>
> AzureSnitch:
>    Gets datacenter from 'location' and rack from 'zone' fields of 'compute' object
>    from instance metadata service. If the availability zone is not enabled, it will use the fault
>    domain and get its respective value.
>
> CloudstackSnitch:
>    A snitch that assumes a Cloudstack Zone follows the typical convention
>    country-location-az and uses a country/location tuple as a datacenter
>    and the availability zone as a rack.
>    WARNING: This snitch is deprecated and it is scheduled to be removed
>    in the next major version of Cassandra.
>
> Ec2Snitch:
>    Appropriate for EC2 deployments in a single Region. Loads Region
>    and Availability Zone information from the EC2 API. The Region is
>    treated as the datacenter, and the Availability Zone as the rack.
>    Only private IPs are used, so this will not work across multiple
>    Regions.
>
> Ec2MultiRegionSnitch:
>    Uses public IPs as broadcast_address to allow cross-region
>    connectivity.  (Thus, you should set seed addresses to the public
>    IP as well.) You will need to open the storage_port or
>    ssl_storage_port on the public IP firewall.  (For intra-Region
>    traffic, Cassandra will switch to the private IP after
>    establishing a connection.)
>
> GoogleCloudSnitch:
>    Snitch for getting dc and rack of a node from metadata service of Google cloud.
>    This snitch that assumes an GCE region is a DC and an GCE availability_zone is a rack.
>
> RackInferringSnitch:
>    Proximity is determined by rack and data center, which are
>    assumed to correspond to the 3rd and 2nd octet of each node's IP
>    address, respectively.  Unless this happens to match your
>    deployment conventions, this is best used as an example of
>    writing a custom Snitch class and is provided in that spirit.
>
> You can use a custom Snitch by setting this to the full class name
> of the snitch, which will be assumed to be on your classpath.

### `dynamic_snitch_update_interval`

<a id="dynamic_snitch_update_interval"></a>

*Active* · `conf/cassandra.yaml` line 1574
 · deprecated old name(s): `dynamic_snitch_update_interval_in_ms`

```yaml
dynamic_snitch_update_interval: 100ms
```

> controls how often to perform the more expensive part of host score
> calculation
> Min unit: ms

### `dynamic_snitch_reset_interval`

<a id="dynamic_snitch_reset_interval"></a>

*Active* · `conf/cassandra.yaml` line 1578
 · deprecated old name(s): `dynamic_snitch_reset_interval_in_ms`

```yaml
dynamic_snitch_reset_interval: 600000ms
```

> controls how often to reset all host scores, allowing a bad host to
> possibly recover
> Min unit: ms

### `dynamic_snitch_badness_threshold`

<a id="dynamic_snitch_badness_threshold"></a>

*Active* · `conf/cassandra.yaml` line 1586

```yaml
dynamic_snitch_badness_threshold: 1.0
```

> if set greater than zero, this will allow
> 'pinning' of replicas to hosts in order to increase cache capacity.
> The badness threshold will control how much worse the pinned host has to be
> before the dynamic snitch will prefer other replicas over it.  This is
> expressed as a double which represents a percentage.  Thus, a value of
> 0.2 means Cassandra would continue to prefer the static snitch values
> until the pinned host was 20% worse than the fastest.

### `paxos_variant`

<a id="paxos_variant"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1615

```yaml
paxos_variant: v1
```

**In `cassandra_latest.yaml`**:

```yaml
paxos_variant: v2
```

> Paxos variant for lightweight transactions (LWTs)
> Options:
>   v1
>          - Legacy Paxos. Expect 4RTs for a write and 3RTs for a read. (default)
>
>   v1_without_linearizable_reads_or_rejected_writes
>          - Legacy Paxos. Expect 4RTs for a write and 2RTs for a read.
>            With legacy semantics for read/read and rejected write linearizability, i.e. not guaranteed.
>
>   v2
>          - Optimized Paxos. Expect 2RTs for a write, and either 1RT or 2RT for a read. (recommended)
>
>   v2_without_linearizable_reads
>          - Optimized Paxos. Expect 2RTs for a write and 1RT for a read.
>
>   v2_without_linearizable_reads_or_rejected_writes
>          - Optimized Paxos. Expect 2RTs for a write and 1RT for a read.
>            With legacy semantics for read/read and rejected write linearizability, i.e. not guaranteed.
>
> To upgrade from v1:
>   1. Ensure all nodes are on same Cassandra version 4.1+.
>   2. Run `nodetool repair --full -pr` on each node.
>   3. Set paxos_variant: v2 on each node and rolling restart.
>   Rollback is safe: revert to v1 and rolling restart. No data migration needed.
>
> With any v2 variant and `paxos_state_purging: repaired` it is safe to use ANY Commit consistency.

### `crypto_provider`

<a id="crypto_provider"></a>

*Active* · `conf/cassandra.yaml` line 1627

```yaml
crypto_provider:
  - class_name: org.apache.cassandra.security.DefaultCryptoProvider
    parameters:
      - fail_on_missing_provider: "false"
```

> Configures Java crypto provider. By default, it will use DefaultCryptoProvider
> which will install Amazon Correto Crypto Provider.
>
> Amazon Correto Crypto Provider works currently for x86_64 and aarch_64 platforms.
> If this provider fails it will fall back to the default crypto provider in the JRE.
>
> To force failure when the provider was not installed properly, set the property "fail_on_missing_provider" to "true".
>
> To bypass the installation of a crypto provider use class 'org.apache.cassandra.security.JREProvider'

### `server_encryption_options`

<a id="server_encryption_options"></a>

*Active* · `conf/cassandra.yaml` line 1654

```yaml
server_encryption_options:
  # On outbound connections, determine which type of peers to securely connect to.
  #   The available options are :
  #     none : Do not encrypt outgoing connections
  #     dc   : Encrypt connections to peers in other datacenters but not within datacenters
  #     rack : Encrypt connections to peers in other racks but not within racks
  #     all  : Always use encrypted connections
  internode_encryption: none
  # When set to true, encrypted and unencrypted connections are allowed on the storage_port
  # This should _only be true_ while in unencrypted or transitional operation
  # optional defaults to true if internode_encryption is none
  # optional: true
  # If enabled, will open up an encrypted listening socket on ssl_storage_port. Should only be used
  # during upgrade to 4.0; otherwise, set to false.
  legacy_ssl_storage_port_enabled: false
  # Set to a valid keystore if internode_encryption is dc, rack or all
  keystore: conf/.keystore
  #keystore_password: cassandra
  # Configure the way Cassandra creates SSL contexts.
  # To use PEM-based key material, see org.apache.cassandra.security.PEMBasedSslContextFactory
  # ssl_context_factory:
  #     # Must be an instance of org.apache.cassandra.security.ISslContextFactory
  #     class_name: org.apache.cassandra.security.DefaultSslContextFactory
  # During internode mTLS authentication, inbound connections (acting as servers) use keystore, keystore_password
  # containing server certificate to create SSLContext and
  # outbound connections (acting as clients) use outbound_keystore & outbound_keystore_password with client certificates
  # to create SSLContext. By default, outbound_keystore is the same as keystore indicating mTLS is not enabled.
  # Verify peer server certificates
  require_client_auth: false
  # Set to a valid truststore if require_client_auth is true
  truststore: conf/.truststore
  #truststore_password: cassandra
  # Verify that the host name in the certificate matches the connected host
  require_endpoint_verification: false
  # More advanced defaults:
  # protocol: TLS
  # store_type: JKS
  # cipher_suites: [
  #   TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384, TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256,
  #   TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256, TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA,
  #   TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA, TLS_RSA_WITH_AES_128_GCM_SHA256, TLS_RSA_WITH_AES_128_CBC_SHA,
  #   TLS_RSA_WITH_AES_256_CBC_SHA
  # ]
```

> Configure server-to-server internode encryption
>
> JVM and netty defaults for supported SSL socket protocols and cipher suites can
> be replaced using custom encryption options. This is not recommended
> unless you have policies in place that dictate certain settings, or
> need to disable vulnerable ciphers or protocols in case the JVM cannot
> be updated.
>
> FIPS compliant settings can be configured at JVM level and should not
> involve changing encryption settings here:
> https://docs.oracle.com/javase/8/docs/technotes/guides/security/jsse/FIPS.html
>
> **NOTE** this default configuration is an insecure configuration. If you need to
> enable server-to-server encryption generate server keystores (and truststores for mutual
> authentication) per:
> http://download.oracle.com/javase/8/docs/technotes/guides/security/jsse/JSSERefGuide.html#CreateKeystore
> Then perform the following configuration changes:
>
> Step 1: Set internode_encryption=<dc\|rack\|all> and explicitly set optional=true. Restart all nodes
>
> Step 2: Set optional=false (or remove it) and if you generated truststores and want to use mutual
> auth set require_client_auth=true. Restart all nodes

### `client_encryption_options`

<a id="client_encryption_options"></a>

*Active* · `conf/cassandra.yaml` line 1712

```yaml
client_encryption_options:
  # Enable client-to-server encryption
  enabled: false
  # When set to true, encrypted and unencrypted connections are allowed on the native_transport_port
  # This should _only be true_ while in unencrypted or transitional operation
  # optional defaults to true when enabled is false, and false when enabled is true.
  # optional: true
  # Set keystore and keystore_password to valid keystores if enabled is true
  keystore: conf/.keystore
  #keystore_password: cassandra
  # Configure the way Cassandra creates SSL contexts.
  # To use PEM-based key material, see org.apache.cassandra.security.PEMBasedSslContextFactory
  # ssl_context_factory:
  #     # Must be an instance of org.apache.cassandra.security.ISslContextFactory
  #     class_name: org.apache.cassandra.security.DefaultSslContextFactory
  # Verify client certificates
  require_client_auth: false
  # require_endpoint_verification: false
  # Set truststore and truststore_password if require_client_auth is true
  # truststore: conf/.truststore
  # truststore_password: cassandra
  # More advanced defaults:
  # protocol: TLS
  # store_type: JKS
  # cipher_suites: [
  #   TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384, TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256,
  #   TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256, TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA,
  #   TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA, TLS_RSA_WITH_AES_128_GCM_SHA256, TLS_RSA_WITH_AES_128_CBC_SHA,
  #   TLS_RSA_WITH_AES_256_CBC_SHA
  # ]
```

> Configure client-to-server encryption.
>
> **NOTE** this default configuration is an insecure configuration. If you need to
> enable client-to-server encryption generate server keystores (and truststores for mutual
> authentication) per:
> http://download.oracle.com/javase/8/docs/technotes/guides/security/jsse/JSSERefGuide.html#CreateKeystore
> Then perform the following configuration changes:
>
> Step 1: Set enabled=true and explicitly set optional=true. Restart all nodes
>
> Step 2: Set optional=false (or remove it) and if you generated truststores and want to use mutual
> auth set require_client_auth=true. Restart all nodes

### `internode_compression`

<a id="internode_compression"></a>

*Active* · `conf/cassandra.yaml` line 1755

```yaml
internode_compression: dc
```

> internode_compression controls whether traffic between nodes is
> compressed.
> Can be:
>
> all
>   all traffic is compressed
>
> dc
>   traffic between different datacenters is compressed
>
> none
>   nothing is compressed.

### `inter_dc_tcp_nodelay`

<a id="inter_dc_tcp_nodelay"></a>

*Active* · `conf/cassandra.yaml` line 1761

```yaml
inter_dc_tcp_nodelay: false
```

> Enable or disable tcp_nodelay for inter-dc communication.
> Disabling it will result in larger (but fewer) network packets being sent,
> reducing overhead from the TCP protocol itself, at the cost of increasing
> latency if you block for cross-datacenter responses.

### `trace_type_query_ttl`

<a id="trace_type_query_ttl"></a>

*Active* · `conf/cassandra.yaml` line 1765
 · deprecated old name(s): `tracetype_query_ttl`

```yaml
trace_type_query_ttl: 1d
```

> TTL for different trace types used during logging of the repair process.
> Min unit: s

### `trace_type_repair_ttl`

<a id="trace_type_repair_ttl"></a>

*Active* · `conf/cassandra.yaml` line 1767
 · deprecated old name(s): `tracetype_repair_ttl`

```yaml
trace_type_repair_ttl: 7d
```

> Min unit: s

See the description of [`trace_type_query_ttl`](#trace_type_query_ttl), which this setting accompanies in the yaml.

### `user_defined_functions_enabled`

<a id="user_defined_functions_enabled"></a>

*Active* · `conf/cassandra.yaml` line 1773
 · deprecated old name(s): `enable_user_defined_functions`

```yaml
user_defined_functions_enabled: false
```

> If unset, all GC Pauses greater than gc_log_threshold will log at
> INFO level
> UDFs (user defined functions) are disabled by default.
> As of Cassandra 3.0 there is a sandbox in place that should prevent execution of evil code.

### `transparent_data_encryption_options`

<a id="transparent_data_encryption_options"></a>

*Active* · `conf/cassandra.yaml` line 1787

```yaml
transparent_data_encryption_options:
  enabled: false
  chunk_length_kb: 64
  cipher: AES/CBC/PKCS5Padding
  key_alias: testing:1
  # CBC IV length for AES needs to be 16 bytes (which is also the default size)
  # iv_length: 16
  key_provider:
    - class_name: org.apache.cassandra.security.JKSKeyProvider
      parameters:
        - keystore: conf/.keystore
          keystore_password: cassandra
          store_type: JCEKS
          key_password: cassandra
```

> Enables encrypting data at-rest (on disk). Different key providers can be plugged in, but the default reads from
> a JCE-style keystore. A single keystore can hold multiple keys, but the one referenced by
> the "key_alias" is the only key that will be used for encrypt operations; previously used keys
> can still (and should!) be in the keystore and will be used on decrypt operations
> (to handle the case of key rotation).
>
> It is strongly recommended to download and install Java Cryptography Extension (JCE)
> Unlimited Strength Jurisdiction Policy Files for your version of the JDK.
> (current link: http://www.oracle.com/technetwork/java/javase/downloads/jce8-download-2133166.html)
>
> Currently, only the following file types are supported for transparent data encryption, although
> more are coming in future cassandra releases: commitlog, hints

### `sai_options`

<a id="sai_options"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1803

```yaml
sai_options:
```

> Storage Attached Indexing options.

## Safety Thresholds

### `tombstone_warn_threshold`

<a id="tombstone_warn_threshold"></a>

*Active* · `conf/cassandra.yaml` line 1827

```yaml
tombstone_warn_threshold: 1000
```

> When executing a scan, within or across a partition, we need to keep the
> tombstones seen in memory so we can return them to the coordinator, which
> will use them to make sure other replicas also know about the deleted rows.
> With workloads that generate a lot of tombstones, this can cause performance
> problems and even exhaust the server heap.
> (http://www.datastax.com/dev/blog/cassandra-anti-patterns-queues-and-queue-like-datasets)
> Adjust the thresholds here if you understand the dangers and want to
> scan more tombstones anyway.  These thresholds may also be adjusted at runtime
> using the StorageService mbean.

### `tombstone_failure_threshold`

<a id="tombstone_failure_threshold"></a>

*Active* · `conf/cassandra.yaml` line 1828

```yaml
tombstone_failure_threshold: 100000
```

See the description of [`tombstone_warn_threshold`](#tombstone_warn_threshold), which this setting accompanies in the yaml.

### `replica_filtering_protection`

<a id="replica_filtering_protection"></a>

*Active* · `conf/cassandra.yaml` line 1835

```yaml
replica_filtering_protection:
    # These thresholds exist to limit the damage severely out-of-date replicas can cause during these
    # queries. They limit the number of rows from all replicas individual index and filtering queries
    # can materialize on-heap to return correct results at the desired read consistency level.
    #
    # "cached_replica_rows_warn_threshold" is the per-query threshold at which a warning will be logged.
    # "cached_replica_rows_fail_threshold" is the per-query threshold at which the query will fail.
    #
    # These thresholds may also be adjusted at runtime using the StorageService mbean.
    #
    # If the failure threshold is breached, it is likely that either the current page/fetch size
    # is too large or one or more replicas is severely out-of-sync and in need of repair.
    cached_rows_warn_threshold: 2000
    cached_rows_fail_threshold: 32000
```

> Filtering and secondary index queries at read consistency levels above ONE/LOCAL_ONE use a
> mechanism called replica filtering protection to ensure that results from stale replicas do
> not violate consistency. (See CASSANDRA-8272 and CASSANDRA-15907 for more details.) This
> mechanism materializes replica results by partition on-heap at the coordinator. The more possibly
> stale results returned by the replicas, the more rows materialized during the query.

### `batch_size_warn_threshold`

<a id="batch_size_warn_threshold"></a>

*Active* · `conf/cassandra.yaml` line 1853
 · deprecated old name(s): `batch_size_warn_threshold_in_kb`

```yaml
batch_size_warn_threshold: 5KiB
```

> Log WARN on any multiple-partition batch size exceeding this value. 5KiB per batch by default.
> Caution should be taken on increasing the size of this threshold as it can lead to node instability.
> Min unit: KiB

### `batch_size_fail_threshold`

<a id="batch_size_fail_threshold"></a>

*Active* · `conf/cassandra.yaml` line 1857
 · deprecated old name(s): `batch_size_fail_threshold_in_kb`

```yaml
batch_size_fail_threshold: 50KiB
```

> Fail any multiple-partition batch exceeding this value. 50KiB (10x warn threshold) by default.
> Min unit: KiB

### `unlogged_batch_across_partitions_warn_threshold`

<a id="unlogged_batch_across_partitions_warn_threshold"></a>

*Active* · `conf/cassandra.yaml` line 1860

```yaml
unlogged_batch_across_partitions_warn_threshold: 10
```

> Log WARN on any batches not of type LOGGED than span across more partitions than this limit

### `gc_log_threshold`

<a id="gc_log_threshold"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1865
 · deprecated old name(s): `gc_log_threshold_in_ms`

```yaml
gc_log_threshold: 200ms
```

> GC Pauses greater than 200 ms will be logged at INFO level
> This threshold can be adjusted to minimize logging if necessary
> Min unit: ms

### `gc_warn_threshold`

<a id="gc_warn_threshold"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1871
 · deprecated old name(s): `gc_warn_threshold_in_ms`

```yaml
gc_warn_threshold: 1000ms
```

> GC Pauses greater than gc_warn_threshold will be logged at WARN level
> Adjust the threshold based on your application throughput requirement. Setting to 0
> will deactivate the feature.
> Min unit: ms

### `max_value_size`

<a id="max_value_size"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1877
 · deprecated old name(s): `max_value_size_in_mb`

```yaml
max_value_size: 256MiB
```

> Maximum size of any value in SSTables. Safety measure to detect SSTable corruption
> early. Any value size larger than this threshold will result into marking an SSTable
> as corrupted. This should be positive and less than 2GiB.
> Min unit: MiB

### `default_keyspace_rf`

<a id="default_keyspace_rf"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1891

```yaml
default_keyspace_rf: 1
```

> ** Impact on keyspace creation **
> If replication factor is not mentioned as part of keyspace creation, default_keyspace_rf would apply.
> Changing this configuration would only take effect for keyspaces created after the change, but does not impact
> existing keyspaces created prior to the change.
> ** Impact on keyspace alter **
> When altering a keyspace from NetworkTopologyStrategy to SimpleStrategy, default_keyspace_rf is applied if rf is not
> explicitly mentioned.
> ** Impact on system keyspaces **
> This would also apply for any system keyspaces that need replication factor.
> A further note about system keyspaces - system_traces and system_distributed keyspaces take RF of 2 or default,
> whichever is higher, and system_auth keyspace takes RF of 1 or default, whichever is higher.
> Suggested value for use in production: 3

### `ideal_consistency_level`

<a id="ideal_consistency_level"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1896

```yaml
ideal_consistency_level: EACH_QUORUM
```

> Track a metric per keyspace indicating whether replication achieved the ideal consistency
> level for writes without timing out. This is different from the consistency level requested by
> each write which may be lower in order to facilitate availability.

### `automatic_sstable_upgrade`

<a id="automatic_sstable_upgrade"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1900

```yaml
automatic_sstable_upgrade: false
```

> Automatically upgrade sstables after upgrade - if there is no ordinary compaction to do, the
> oldest non-upgraded sstable will get upgraded to the latest version

### `max_concurrent_automatic_sstable_upgrades`

<a id="max_concurrent_automatic_sstable_upgrades"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1902

```yaml
max_concurrent_automatic_sstable_upgrades: 1
```

> Limit the number of concurrent sstable upgrades

### `audit_logging_options`

<a id="audit_logging_options"></a>

*Active* · `conf/cassandra.yaml` line 1906

```yaml
audit_logging_options:
  enabled: false
  logger:
    - class_name: BinAuditLogger
  # audit_logs_dir:
  # included_keyspaces:
  # excluded_keyspaces: system, system_schema, system_virtual_schema
  # included_categories:
  # excluded_categories:
  # included_users:
  # excluded_users:
  # roll_cycle: HOURLY
  # block: true
  # max_queue_weight: 268435456 # 256 MiB
  # max_log_size: 17179869184 # 16 GiB
  #
  ## If archive_command is empty or unset, Cassandra uses a built-in DeletingArchiver that deletes the oldest files if ``max_log_size`` is reached.
  ## If archive_command is set, Cassandra does not use DeletingArchiver, so it is the responsibility of the script to make any required cleanup.
  ## Example: "/path/to/script.sh %path" where %path is replaced with the file being rolled.
  # archive_command:
  # max_archive_retries: 10
```

> Audit logging - Logs every incoming CQL command request, authentication to a node. See the docs
> on audit_logging for full details about the various configuration options and production tips.

### `full_query_logging_options`

<a id="full_query_logging_options"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1930

```yaml
full_query_logging_options:
```

> default options for full query logging - these can be overridden from command line when executing
> nodetool enablefullquerylog

### `corrupted_tombstone_strategy`

<a id="corrupted_tombstone_strategy"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1944

```yaml
corrupted_tombstone_strategy: disabled
```

> validate tombstones on reads and compaction
> can be either "disabled", "warn" or "exception"

### `diagnostic_events_enabled`

<a id="diagnostic_events_enabled"></a>

*Active* · `conf/cassandra.yaml` line 1949

```yaml
diagnostic_events_enabled: false
```

> Diagnostic Events #
> If enabled, diagnostic events can be helpful for troubleshooting operational issues. Emitted events contain details
> on internal state and temporal relationships across events, accessible by clients via JMX.

### `native_transport_flush_in_batches_legacy`

<a id="native_transport_flush_in_batches_legacy"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1953

```yaml
native_transport_flush_in_batches_legacy: false
```

> Use native transport TCP message coalescing. If on upgrade to 4.0 you found your throughput decreasing, and in
> particular you run an old kernel or have very fewer client connections, this option might be worth evaluating.

### `repaired_data_tracking_for_range_reads_enabled`

<a id="repaired_data_tracking_for_range_reads_enabled"></a>

*Active* · `conf/cassandra.yaml` line 1965

```yaml
repaired_data_tracking_for_range_reads_enabled: false
```

> Enable tracking of repaired state of data during reads and comparison between replicas
> Mismatches between the repaired sets of replicas can be characterized as either confirmed
> or unconfirmed. In this context, unconfirmed indicates that the presence of pending repair
> sessions, unrepaired partition tombstones, or some other condition means that the disparity
> cannot be considered conclusive. Confirmed mismatches should be a trigger for investigation
> as they may be indicative of corruption or data loss.
> There are separate flags for range vs partition reads as single partition reads are only tracked
> when CL > 1 and a digest mismatch occurs. Currently, range queries don't use digests so if
> enabled for range reads, all range reads will include repaired data tracking. As this adds
> some overhead, operators may wish to disable it whilst still enabling it for partition reads

### `repaired_data_tracking_for_partition_reads_enabled`

<a id="repaired_data_tracking_for_partition_reads_enabled"></a>

*Active* · `conf/cassandra.yaml` line 1966

```yaml
repaired_data_tracking_for_partition_reads_enabled: false
```

See the description of [`repaired_data_tracking_for_range_reads_enabled`](#repaired_data_tracking_for_range_reads_enabled), which this setting accompanies in the yaml.

### `report_unconfirmed_repaired_data_mismatches`

<a id="report_unconfirmed_repaired_data_mismatches"></a>

*Active* · `conf/cassandra.yaml` line 1970

```yaml
report_unconfirmed_repaired_data_mismatches: false
```

> If false, only confirmed mismatches will be reported. If true, a separate metric for unconfirmed
> mismatches will also be recorded. This is to avoid potential signal:noise issues are unconfirmed
> mismatches are less actionable than confirmed ones.

### `auth_read_consistency_level`

<a id="auth_read_consistency_level"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1973

```yaml
auth_read_consistency_level: LOCAL_QUORUM
```

> configure the read and write consistency levels for modifications to auth tables

### `auth_write_consistency_level`

<a id="auth_write_consistency_level"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1974

```yaml
auth_write_consistency_level: EACH_QUORUM
```

See the description of [`auth_read_consistency_level`](#auth_read_consistency_level), which this setting accompanies in the yaml.

### `auth_cache_warming_enabled`

<a id="auth_cache_warming_enabled"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1978

```yaml
auth_cache_warming_enabled: false
```

> Delays on auth resolution can lead to a thundering herd problem on reconnects; this option will enable
> warming of auth caches prior to node completing startup. See CASSANDRA-16958

### `dynamic_data_masking_enabled`

<a id="dynamic_data_masking_enabled"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 1986

```yaml
dynamic_data_masking_enabled: false
```

> If enabled, dynamic data masking allows to attach CQL masking functions to the columns of a table.
> Users without the UNMASK permission will see an obscured version of the values of the columns with an attached mask.
> If dynamic data masking is disabled it won't be allowed to create new column masks, although it will still be possible
> to drop any previously existing masks. Also, any existing mask will be ignored at query time, so all users will see
> the clear values of the masked columns.
> Defaults to false to disable dynamic data masking.

## Experimental Features

### `materialized_views_enabled`

<a id="materialized_views_enabled"></a>

*Active* · `conf/cassandra.yaml` line 1994
 · deprecated old name(s): `enable_materialized_views`

```yaml
materialized_views_enabled: false
```

> Enables materialized view creation on this node.
> Materialized views are considered experimental and are not recommended for production use.

### `materialized_views_on_repair_enabled`

<a id="materialized_views_on_repair_enabled"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2001

```yaml
materialized_views_on_repair_enabled: true
```

> Specify whether Materialized View mutations are replayed through the write path on streaming, e.g. repair.
> When enabled, Materialized View data streamed to the destination node will be written into commit log first. When setting to false,
> the streamed Materialized View data is written into SSTables just the same as normal streaming. The default is true.
> If this is set to false, streaming will be considerably faster however it's possible that, in extreme situations
> (losing > quorum # nodes in a replica set), you may have data in your SSTables that never makes it to the Materialized View.

### `sasi_indexes_enabled`

<a id="sasi_indexes_enabled"></a>

*Active* · `conf/cassandra.yaml` line 2005
 · deprecated old name(s): `enable_sasi_indexes`

```yaml
sasi_indexes_enabled: false
```

> Enables SASI index creation on this node.
> SASI indexes are considered experimental and are not recommended for production use.

### `transient_replication_enabled`

<a id="transient_replication_enabled"></a>

*Active* · `conf/cassandra.yaml` line 2009
 · deprecated old name(s): `enable_transient_replication`

```yaml
transient_replication_enabled: false
```

> Enables creation of transiently replicated keyspaces on this node.
> Transient replication is experimental and is not recommended for production use.

### `drop_compact_storage_enabled`

<a id="drop_compact_storage_enabled"></a>

*Active* · `conf/cassandra.yaml` line 2013
 · deprecated old name(s): `enable_drop_compact_storage`

```yaml
drop_compact_storage_enabled: false
```

> Enables the used of 'ALTER ... DROP COMPACT STORAGE' statements on this node.
> 'ALTER ... DROP COMPACT STORAGE' is considered experimental and is not recommended for production use.

### `use_statements_enabled`

<a id="use_statements_enabled"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2016

```yaml
use_statements_enabled: true
```

> Whether or not USE <keyspace> is allowed. This is enabled by default to avoid failure on upgrade.

### `client_error_reporting_exclusions`

<a id="client_error_reporting_exclusions"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2021

```yaml
client_error_reporting_exclusions:
 subnets:
   - 127.0.0.1
   - 127.0.0.0/31
```

> When the client triggers a protocol exception or unknown issue (Cassandra bug) we increment
> a client metric showing this; this logic will exclude specific subnets from updating these
> metrics

### `read_thresholds_enabled`

<a id="read_thresholds_enabled"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2028

```yaml
read_thresholds_enabled: false # scheduled to be set true in 4.2
```

> Enables read thresholds (warn/fail) across all replicas for reporting back to the client.
> See: CASSANDRA-16850

### `coordinator_read_size_warn_threshold`

<a id="coordinator_read_size_warn_threshold"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2034

```yaml
coordinator_read_size_warn_threshold:
```

> When read_thresholds_enabled: true, this tracks the materialized size of a query on the
> coordinator. If coordinator_read_size_warn_threshold is defined, this will emit a warning
> to clients with details on what query triggered this as well as the size of the result set; if
> coordinator_read_size_fail_threshold is defined, this will fail the query after it
> has exceeded this threshold, returning a read error to the user.

### `coordinator_read_size_fail_threshold`

<a id="coordinator_read_size_fail_threshold"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2035

```yaml
coordinator_read_size_fail_threshold:
```

See the description of [`coordinator_read_size_warn_threshold`](#coordinator_read_size_warn_threshold), which this setting accompanies in the yaml.

### `local_read_size_warn_threshold`

<a id="local_read_size_warn_threshold"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2038

```yaml
local_read_size_warn_threshold:
```

> When read_thresholds_enabled: true, this tracks the size of the local read (as defined by
> heap size), and will warn/fail based off these thresholds; undefined disables these checks.

### `local_read_size_fail_threshold`

<a id="local_read_size_fail_threshold"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2039

```yaml
local_read_size_fail_threshold:
```

See the description of [`local_read_size_warn_threshold`](#local_read_size_warn_threshold), which this setting accompanies in the yaml.

### `row_index_read_size_warn_threshold`

<a id="row_index_read_size_warn_threshold"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2042

```yaml
row_index_read_size_warn_threshold:
```

> When read_thresholds_enabled: true, this tracks the expected memory size of the RowIndexEntry
> and will warn/fail based off these thresholds; undefined disables these checks

### `row_index_read_size_fail_threshold`

<a id="row_index_read_size_fail_threshold"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2043

```yaml
row_index_read_size_fail_threshold:
```

See the description of [`row_index_read_size_warn_threshold`](#row_index_read_size_warn_threshold), which this setting accompanies in the yaml.

### `keyspaces_warn_threshold`

<a id="keyspaces_warn_threshold"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2047
 · deprecated old name(s): `keyspace_count_warn_threshold`

```yaml
keyspaces_warn_threshold: -1
```

> Guardrail to warn or fail when creating more user keyspaces than threshold.
> The two thresholds default to -1 to disable.

### `keyspaces_fail_threshold`

<a id="keyspaces_fail_threshold"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2048

```yaml
keyspaces_fail_threshold: -1
```

See the description of [`keyspaces_warn_threshold`](#keyspaces_warn_threshold), which this setting accompanies in the yaml.

### `tables_warn_threshold`

<a id="tables_warn_threshold"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2052
 · deprecated old name(s): `table_count_warn_threshold`

```yaml
tables_warn_threshold: -1
```

> Guardrail to warn or fail when creating more user tables than threshold.
> The two thresholds default to -1 to disable.

### `tables_fail_threshold`

<a id="tables_fail_threshold"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2053

```yaml
tables_fail_threshold: -1
```

See the description of [`tables_warn_threshold`](#tables_warn_threshold), which this setting accompanies in the yaml.

### `uncompressed_tables_enabled`

<a id="uncompressed_tables_enabled"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2056

```yaml
uncompressed_tables_enabled: true
```

> Guardrail to enable or disable the ability to create uncompressed tables

### `columns_per_table_warn_threshold`

<a id="columns_per_table_warn_threshold"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2060

```yaml
columns_per_table_warn_threshold: -1
```

> Guardrail to warn or fail when creating/altering a table with more columns per table than threshold.
> The two thresholds default to -1 to disable.

### `columns_per_table_fail_threshold`

<a id="columns_per_table_fail_threshold"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2061

```yaml
columns_per_table_fail_threshold: -1
```

See the description of [`columns_per_table_warn_threshold`](#columns_per_table_warn_threshold), which this setting accompanies in the yaml.

### `secondary_indexes_per_table_warn_threshold`

<a id="secondary_indexes_per_table_warn_threshold"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2065

```yaml
secondary_indexes_per_table_warn_threshold: -1
```

> Guardrail to warn or fail when creating more secondary indexes per table than threshold.
> The two thresholds default to -1 to disable.

### `secondary_indexes_per_table_fail_threshold`

<a id="secondary_indexes_per_table_fail_threshold"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2066

```yaml
secondary_indexes_per_table_fail_threshold: -1
```

See the description of [`secondary_indexes_per_table_warn_threshold`](#secondary_indexes_per_table_warn_threshold), which this setting accompanies in the yaml.

### `secondary_indexes_enabled`

<a id="secondary_indexes_enabled"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2069

```yaml
secondary_indexes_enabled: true
```

> Guardrail to enable or disable the creation of secondary indexes

### `materialized_views_per_table_warn_threshold`

<a id="materialized_views_per_table_warn_threshold"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2073

```yaml
materialized_views_per_table_warn_threshold: -1
```

> Guardrail to warn or fail when creating more materialized views per table than threshold.
> The two thresholds default to -1 to disable.

### `materialized_views_per_table_fail_threshold`

<a id="materialized_views_per_table_fail_threshold"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2074

```yaml
materialized_views_per_table_fail_threshold: -1
```

See the description of [`materialized_views_per_table_warn_threshold`](#materialized_views_per_table_warn_threshold), which this setting accompanies in the yaml.

### `table_properties_warned`

<a id="table_properties_warned"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2077

```yaml
table_properties_warned: []
```

> Guardrail to warn about, ignore or reject properties when creating tables. By default all properties are allowed.

### `table_properties_ignored`

<a id="table_properties_ignored"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2078

```yaml
table_properties_ignored: []
```

See the description of [`table_properties_warned`](#table_properties_warned), which this setting accompanies in the yaml.

### `table_properties_disallowed`

<a id="table_properties_disallowed"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2079

```yaml
table_properties_disallowed: []
```

See the description of [`table_properties_ignored`](#table_properties_ignored), which this setting accompanies in the yaml.

### `user_timestamps_enabled`

<a id="user_timestamps_enabled"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2082

```yaml
user_timestamps_enabled: true
```

> Guardrail to allow/disallow user-provided timestamps. Defaults to true.

### `maximum_timestamp_warn_threshold`

<a id="maximum_timestamp_warn_threshold"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2086

```yaml
maximum_timestamp_warn_threshold:
```

> Guardrail to bound user-provided timestamps within a given range. Default is infinite (denoted by null).
> Accepted values are durations of the form 12h, 24h, etc.

### `maximum_timestamp_fail_threshold`

<a id="maximum_timestamp_fail_threshold"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2087

```yaml
maximum_timestamp_fail_threshold:
```

See the description of [`maximum_timestamp_warn_threshold`](#maximum_timestamp_warn_threshold), which this setting accompanies in the yaml.

### `minimum_timestamp_warn_threshold`

<a id="minimum_timestamp_warn_threshold"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2088

```yaml
minimum_timestamp_warn_threshold:
```

See the description of [`maximum_timestamp_fail_threshold`](#maximum_timestamp_fail_threshold), which this setting accompanies in the yaml.

### `minimum_timestamp_fail_threshold`

<a id="minimum_timestamp_fail_threshold"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2089

```yaml
minimum_timestamp_fail_threshold:
```

See the description of [`minimum_timestamp_warn_threshold`](#minimum_timestamp_warn_threshold), which this setting accompanies in the yaml.

### `group_by_enabled`

<a id="group_by_enabled"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2092

```yaml
group_by_enabled: true
```

> Guardrail to allow/disallow GROUP BY functionality.

### `drop_truncate_table_enabled`

<a id="drop_truncate_table_enabled"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2095

```yaml
drop_truncate_table_enabled: true
```

> Guardrail to allow/disallow TRUNCATE and DROP TABLE statements

### `drop_keyspace_enabled`

<a id="drop_keyspace_enabled"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2098

```yaml
drop_keyspace_enabled: true
```

> Guardrail to allow/disallow DROP KEYSPACE statements

### `page_size_warn_threshold`

<a id="page_size_warn_threshold"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2102

```yaml
page_size_warn_threshold: -1
```

> Guardrail to warn or fail when using a page size greater than threshold.
> The two thresholds default to -1 to disable.

### `page_size_fail_threshold`

<a id="page_size_fail_threshold"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2103

```yaml
page_size_fail_threshold: -1
```

See the description of [`page_size_warn_threshold`](#page_size_warn_threshold), which this setting accompanies in the yaml.

### `read_before_write_list_operations_enabled`

<a id="read_before_write_list_operations_enabled"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2107

```yaml
read_before_write_list_operations_enabled: true
```

> Guardrail to allow/disallow list operations that require read before write, i.e. setting list element by index and
> removing list elements by either index or value. Defaults to true.

### `partition_keys_in_select_warn_threshold`

<a id="partition_keys_in_select_warn_threshold"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2111

```yaml
partition_keys_in_select_warn_threshold: -1
```

> Guardrail to warn or fail when querying with an IN restriction selecting more partition keys than threshold.
> The two thresholds default to -1 to disable.

### `partition_keys_in_select_fail_threshold`

<a id="partition_keys_in_select_fail_threshold"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2112

```yaml
partition_keys_in_select_fail_threshold: -1
```

See the description of [`partition_keys_in_select_warn_threshold`](#partition_keys_in_select_warn_threshold), which this setting accompanies in the yaml.

### `in_select_cartesian_product_warn_threshold`

<a id="in_select_cartesian_product_warn_threshold"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2117

```yaml
in_select_cartesian_product_warn_threshold: -1
```

> Guardrail to warn or fail when an IN query creates a cartesian product with a size exceeding threshold,
> eg. "a in (1,2,...10) and b in (1,2...10)" results in cartesian product of 100.
> The two thresholds default to -1 to disable.

### `in_select_cartesian_product_fail_threshold`

<a id="in_select_cartesian_product_fail_threshold"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2118

```yaml
in_select_cartesian_product_fail_threshold: -1
```

See the description of [`in_select_cartesian_product_warn_threshold`](#in_select_cartesian_product_warn_threshold), which this setting accompanies in the yaml.

### `read_consistency_levels_warned`

<a id="read_consistency_levels_warned"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2121

```yaml
read_consistency_levels_warned: []
```

> Guardrail to warn about or reject read consistency levels. By default, all consistency levels are allowed.

### `read_consistency_levels_disallowed`

<a id="read_consistency_levels_disallowed"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2122

```yaml
read_consistency_levels_disallowed: []
```

See the description of [`read_consistency_levels_warned`](#read_consistency_levels_warned), which this setting accompanies in the yaml.

### `write_consistency_levels_warned`

<a id="write_consistency_levels_warned"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2125

```yaml
write_consistency_levels_warned: []
```

> Guardrail to warn about or reject write consistency levels. By default, all consistency levels are allowed.

### `write_consistency_levels_disallowed`

<a id="write_consistency_levels_disallowed"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2126

```yaml
write_consistency_levels_disallowed: []
```

See the description of [`write_consistency_levels_warned`](#write_consistency_levels_warned), which this setting accompanies in the yaml.

### `partition_size_warn_threshold`

<a id="partition_size_warn_threshold"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2134
 · deprecated old name(s): `compaction_large_partition_warning_threshold`, `compaction_large_partition_warning_threshold_mb`

```yaml
partition_size_warn_threshold:
```

> Guardrail to warn or fail when writing partitions larger than threshold, expressed as 100MiB, 1GiB, etc.
> The guardrail is only checked when writing sstables (flush and compaction), and exceeding the fail threshold on that
> moment will only log an error message, without interrupting the operation.
> This operates on a per-sstable basis, so it won't detect a large partition if it is spread across multiple sstables.
> The warning threshold replaces the deprecated config property compaction_large_partition_warning_threshold.
> The two thresholds default to null to disable.

### `partition_size_fail_threshold`

<a id="partition_size_fail_threshold"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2135

```yaml
partition_size_fail_threshold:
```

See the description of [`partition_size_warn_threshold`](#partition_size_warn_threshold), which this setting accompanies in the yaml.

### `partition_tombstones_warn_threshold`

<a id="partition_tombstones_warn_threshold"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2143
 · deprecated old name(s): `compaction_tombstone_warning_threshold`

```yaml
partition_tombstones_warn_threshold: -1
```

> Guardrail to warn or fail when writing partitions with more tombstones than threshold.
> The guardrail is only checked when writing sstables (flush and compaction), and exceeding the fail threshold on that
> moment will only log an error message, without interrupting the operation.
> This operates on a per-sstable basis, so it won't detect a large partition if it is spread across multiple sstables.
> The warning threshold replaces the deprecated config property compaction_tombstone_warning_threshold.
> The two thresholds default to -1 to disable.

### `partition_tombstones_fail_threshold`

<a id="partition_tombstones_fail_threshold"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2144

```yaml
partition_tombstones_fail_threshold: -1
```

See the description of [`partition_tombstones_warn_threshold`](#partition_tombstones_warn_threshold), which this setting accompanies in the yaml.

### `column_value_size_warn_threshold`

<a id="column_value_size_warn_threshold"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2161

```yaml
column_value_size_warn_threshold:
```

> Guardrail to warn or fail when writing column values larger than threshold.
> This guardrail is only applied to the values of regular columns because both the serialized partitions keys and the
> values of the components of the clustering key already have a fixed, relatively small size limit of 65535 bytes, which
> is probably lesser than the thresholds defined here.
> Deleting individual elements of non-frozen sets and maps involves creating tombstones that contain the value of the
> deleted element, independently on whether the element existed or not. That tombstone value is also guarded by this
> guardrail, to prevent the insertion of tombstones over the threshold. The downside is that enabling or raising this
> threshold can prevent users from deleting set/map elements that were written when the guardrail was disabled or with a
> lower value. Deleting the entire column, row or partition is always allowed, since the tombstones created for those
> operations don't contain the CQL column values.
> This guardrail is different to max_value_size. max_value_size is checked when deserializing any value to detect
> sstable corruption, whereas this guardrail is checked on the CQL layer at write time to reject regular user queries
> inserting too large columns.
> The two thresholds default to null to disable.
> Min unit: B

### `column_value_size_fail_threshold`

<a id="column_value_size_fail_threshold"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2162

```yaml
column_value_size_fail_threshold:
```

See the description of [`column_value_size_warn_threshold`](#column_value_size_warn_threshold), which this setting accompanies in the yaml.

### `collection_size_warn_threshold`

<a id="collection_size_warn_threshold"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2171

```yaml
collection_size_warn_threshold:
```

> Guardrail to warn or fail when encountering larger size of collection data than threshold.
> At query time this guardrail is applied only to the collection fragment that is being written, even though in the case
> of non-frozen collections there could be unaccounted parts of the collection on the sstables. This is done this way to
> prevent read-before-write. The guardrail is also checked at sstable write time to detect large non-frozen collections,
> although in that case exceeding the fail threshold will only log an error message, without interrupting the operation.
> The two thresholds default to null to disable.
> Min unit: B

### `collection_size_fail_threshold`

<a id="collection_size_fail_threshold"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2173

```yaml
collection_size_fail_threshold:
```

> Min unit: B

See the description of [`collection_size_warn_threshold`](#collection_size_warn_threshold), which this setting accompanies in the yaml.

### `items_per_collection_warn_threshold`

<a id="items_per_collection_warn_threshold"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2181

```yaml
items_per_collection_warn_threshold: -1
```

> Guardrail to warn or fail when encountering more elements in collection than threshold.
> At query time this guardrail is applied only to the collection fragment that is being written, even though in the case
> of non-frozen collections there could be unaccounted parts of the collection on the sstables. This is done this way to
> prevent read-before-write. The guardrail is also checked at sstable write time to detect large non-frozen collections,
> although in that case exceeding the fail threshold will only log an error message, without interrupting the operation.
> The two thresholds default to -1 to disable.

### `items_per_collection_fail_threshold`

<a id="items_per_collection_fail_threshold"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2182

```yaml
items_per_collection_fail_threshold: -1
```

See the description of [`items_per_collection_warn_threshold`](#items_per_collection_warn_threshold), which this setting accompanies in the yaml.

### `allow_filtering_enabled`

<a id="allow_filtering_enabled"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2186

```yaml
allow_filtering_enabled: true
```

> Guardrail to allow/disallow querying with ALLOW FILTERING. Defaults to true.
> ALLOW FILTERING can potentially visit all the data in the table and have unpredictable performance.

### `simplestrategy_enabled`

<a id="simplestrategy_enabled"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2189

```yaml
simplestrategy_enabled: true
```

> Guardrail to allow/disallow setting SimpleStrategy via keyspace creation or alteration. Defaults to true.

### `fields_per_udt_warn_threshold`

<a id="fields_per_udt_warn_threshold"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2193

```yaml
fields_per_udt_warn_threshold: -1
```

> Guardrail to warn or fail when creating a user-defined-type with more fields in than threshold.
> Default -1 to disable.

### `fields_per_udt_fail_threshold`

<a id="fields_per_udt_fail_threshold"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2194

```yaml
fields_per_udt_fail_threshold: -1
```

See the description of [`fields_per_udt_warn_threshold`](#fields_per_udt_warn_threshold), which this setting accompanies in the yaml.

### `vector_dimensions_warn_threshold`

<a id="vector_dimensions_warn_threshold"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2198

```yaml
vector_dimensions_warn_threshold: -1
```

> Guardrail to warn or fail when creating a vector column with more dimensions than threshold.
> Default -1 to disable.

### `vector_dimensions_fail_threshold`

<a id="vector_dimensions_fail_threshold"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2199

```yaml
vector_dimensions_fail_threshold: -1
```

See the description of [`vector_dimensions_warn_threshold`](#vector_dimensions_warn_threshold), which this setting accompanies in the yaml.

### `alter_table_enabled`

<a id="alter_table_enabled"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2202

```yaml
alter_table_enabled: true
```

> Guardrail to indicate whether or not users are allowed to use ALTER TABLE commands to make column changes to tables

### `data_disk_usage_percentage_warn_threshold`

<a id="data_disk_usage_percentage_warn_threshold"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2213

```yaml
data_disk_usage_percentage_warn_threshold: -1
```

> Guardrail to warn or fail when local data disk usage percentage exceeds threshold. Valid values are in [1, 100].
> This is only used for the disks storing data directories, so it won't count any separate disks used for storing
> the commitlog, hints nor saved caches. The disk usage is the ratio between the amount of space used by the data
> directories and the addition of that same space and the remaining free space on disk. The main purpose of this
> guardrail is rejecting user writes when the disks are over the defined usage percentage, so the writes done by
> background processes such as compaction and streaming don't fail due to a full disk. The limits should be defined
> accordingly to the expected data growth due to those background processes, so for example a compaction strategy
> doubling the size of the data would require to keep the disk usage under 50%.
> The two thresholds default to -1 to disable.

### `data_disk_usage_percentage_fail_threshold`

<a id="data_disk_usage_percentage_fail_threshold"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2214

```yaml
data_disk_usage_percentage_fail_threshold: -1
```

See the description of [`data_disk_usage_percentage_warn_threshold`](#data_disk_usage_percentage_warn_threshold), which this setting accompanies in the yaml.

### `data_disk_usage_max_disk_size`

<a id="data_disk_usage_max_disk_size"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2223

```yaml
data_disk_usage_max_disk_size:
```

> Guardrail that allows users to define the max disk size of the data directories when calculating thresholds for
> disk_usage_percentage_warn_threshold and disk_usage_percentage_fail_threshold, so if this is greater than zero they
> become percentages of a fixed size on disk instead of percentages of the physically available disk size. This should
> be useful when we have a large disk and we only want to use a part of it for Cassandra's data directories.
> Valid values are in [1, max available disk size of all data directories].
> Defaults to null to disable and use the physically available disk size of data directories during calculations.
> Min unit: B

### `minimum_replication_factor_warn_threshold`

<a id="minimum_replication_factor_warn_threshold"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2228

```yaml
minimum_replication_factor_warn_threshold: -1
```

> Guardrail to warn or fail when the minimum replication factor is lesser than threshold.
> This would also apply to system keyspaces.
> Suggested value for use in production: 2 or higher

### `minimum_replication_factor_fail_threshold`

<a id="minimum_replication_factor_fail_threshold"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2229

```yaml
minimum_replication_factor_fail_threshold: -1
```

See the description of [`minimum_replication_factor_warn_threshold`](#minimum_replication_factor_warn_threshold), which this setting accompanies in the yaml.

### `maximum_replication_factor_warn_threshold`

<a id="maximum_replication_factor_warn_threshold"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2233

```yaml
maximum_replication_factor_warn_threshold: -1
```

> Guardrail to warn or fail when the maximum replication factor is greater than threshold.
> This would also apply to system keyspaces.

### `maximum_replication_factor_fail_threshold`

<a id="maximum_replication_factor_fail_threshold"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2234

```yaml
maximum_replication_factor_fail_threshold: -1
```

See the description of [`maximum_replication_factor_warn_threshold`](#maximum_replication_factor_warn_threshold), which this setting accompanies in the yaml.

### `zero_ttl_on_twcs_enabled`

<a id="zero_ttl_on_twcs_enabled"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2243

```yaml
zero_ttl_on_twcs_enabled: true
```

> Guardrail to enable a CREATE or ALTER TABLE statement when default_time_to_live is set to 0
> and the table is using TimeWindowCompactionStrategy compaction or a subclass of it.
> It is suspicious to use default_time_to_live set to 0 with such compaction strategy.
> Please keep in mind that data will not start to automatically expire after they are older than
> a respective compaction window unit of a certain size. Please set TTL for your INSERT or UPDATE
> statements if you expect data to be expired as table settings will not do it.
> Defaults to true. If set to false, such statements fail and zero_ttl_on_twcs_warned flag is irrelevant.

### `zero_ttl_on_twcs_warned`

<a id="zero_ttl_on_twcs_warned"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2247

```yaml
zero_ttl_on_twcs_warned: true
```

> Guardrail to warn a user upon executing CREATE or ALTER TABLE statement when default_time_to_live is set to 0
> and the table is using TimeWindowCompactionStrategy compaction or a subclass of it. Defaults to true.
> if zero_ttl_on_twcs_enabled is set to false, this property is irrelevant as such statements will fail.

### `non_partition_restricted_index_query_enabled`

<a id="non_partition_restricted_index_query_enabled"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2250

```yaml
non_partition_restricted_index_query_enabled: true
```

> Guardrail enabling secondary index queries that do not restrict on partition key (defaults to true)

### `sai_sstable_indexes_per_query_warn_threshold`

<a id="sai_sstable_indexes_per_query_warn_threshold"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2253

```yaml
sai_sstable_indexes_per_query_warn_threshold: 32
```

> Maximum number of referenced SAI indexes on a replica when executing a SELECT query
> before emitting a warning (defaults to 32)

### `sai_sstable_indexes_per_query_fail_threshold`

<a id="sai_sstable_indexes_per_query_fail_threshold"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2256

```yaml
sai_sstable_indexes_per_query_fail_threshold: -1
```

> Maximum number of referenced SAI indexes on a replica when executing a SELECT query
> before emitting a failure (defaults to -1 to disable)

### `sai_string_term_size_warn_threshold`

<a id="sai_string_term_size_warn_threshold"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2259

```yaml
sai_string_term_size_warn_threshold: 1KiB
```

> Guardrail specifying warn/fail thresholds for the size of string terms written to an SAI index

### `sai_string_term_size_fail_threshold`

<a id="sai_string_term_size_fail_threshold"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2260

```yaml
sai_string_term_size_fail_threshold: 8KiB
```

See the description of [`sai_string_term_size_warn_threshold`](#sai_string_term_size_warn_threshold), which this setting accompanies in the yaml.

### `sai_frozen_term_size_warn_threshold`

<a id="sai_frozen_term_size_warn_threshold"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2263

```yaml
sai_frozen_term_size_warn_threshold: 1KiB
```

> Guardrail specifying warn/fail thresholds for the size of frozen terms written to an SAI index

### `sai_frozen_term_size_fail_threshold`

<a id="sai_frozen_term_size_fail_threshold"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2264

```yaml
sai_frozen_term_size_fail_threshold: 8KiB
```

See the description of [`sai_frozen_term_size_warn_threshold`](#sai_frozen_term_size_warn_threshold), which this setting accompanies in the yaml.

### `sai_vector_term_size_warn_threshold`

<a id="sai_vector_term_size_warn_threshold"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2267

```yaml
sai_vector_term_size_warn_threshold: 16KiB
```

> Guardrail specifying warn/fail thresholds for the size of vector terms written to an SAI index

### `sai_vector_term_size_fail_threshold`

<a id="sai_vector_term_size_fail_threshold"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2268

```yaml
sai_vector_term_size_fail_threshold: 32KiB
```

See the description of [`sai_vector_term_size_warn_threshold`](#sai_vector_term_size_warn_threshold), which this setting accompanies in the yaml.

### `default_secondary_index`

<a id="default_secondary_index"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2273

```yaml
default_secondary_index: legacy_local_table
```

**In `cassandra_latest.yaml`**:

```yaml
default_secondary_index: sai
```

> The default secondary index implementation when CREATE INDEX does not specify one via USING.
> ex. "legacy_local_table" - (default) legacy secondary index, implemented as a hidden table
> ex. "sai" - "storage-attached" index, implemented via optimized SSTable/Memtable-attached indexes

### `default_secondary_index_enabled`

<a id="default_secondary_index_enabled"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2277

```yaml
default_secondary_index_enabled: true
```

**In `cassandra_latest.yaml`**:

```yaml
default_secondary_index_enabled: true
```

> Whether a default secondary index implementation is allowed. If this is "false", CREATE INDEX must
> specify an index implementation via USING.

### `startup_checks`

<a id="startup_checks"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2283

```yaml
startup_checks:
```

> Startup Checks are executed as part of Cassandra startup process, not all of them
> are configurable (so you can disable them) but these which are enumerated below.
> Uncomment the startup checks and configure them appropriately to cover your needs.

### `storage_compatibility_mode`

<a id="storage_compatibility_mode"></a>

*Active* · `conf/cassandra.yaml` line 2333

```yaml
storage_compatibility_mode: CASSANDRA_4
```

**In `cassandra_latest.yaml`**:

```yaml
storage_compatibility_mode: NONE
```

> This property indicates with what Cassandra major version the storage format will be compatible with.
>
> The chosen storage compatibility mode will determine the versions of the written sstables, commitlogs, hints, etc.
> For example, if we're going to remain compatible with Cassandra 4.x, the value of this property should be 4, which
> will make us use sstables in the latest N version of the BIG format.
>
> This will also determine if certain features that depend on newer formats are available. For example, extended TTL
> (up to 2106) depends on the sstable, commit-log, hints, and messaging versions introduced by Cassandra 5.0, so that
> feature won't be available if this property is set to CASSANDRA_4. See the upgrade guide for more details.
>
> Possible values are:
>
> ** CASSANDRA_4: Stays compatible with the 4.x line in features, formats and component versions.
> ** UPGRADING:   The cluster monitors the version of each node during this interim stage. This has a cost but ensures
>                all new features, formats, versions, etc. are enabled safely.
> ** NONE:        Start with all the new features and formats enabled.
>
> A typical upgrade would be:
>
> . Do a rolling upgrade, starting all nodes in CASSANDRA_X compatibility mode.
> . Once the new binary is rendered stable, do a rolling restart with the UPGRADING mode. The cluster will keep new
>   features disabled until all nodes are started in the UPGRADING mode; when that happens, new features controlled by
>   the storage compatibility mode are enabled.
> . Do a rolling restart with all nodes starting with the NONE mode. This eliminates the cost of checking node versions
>   and ensures stability. If Cassandra was started at the previous version by accident, a node with disabled
>   compatibility mode would no longer toggle behaviors as when it was running in the UPGRADING mode.

### `reject_repair_compaction_threshold`

<a id="reject_repair_compaction_threshold"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2338

```yaml
reject_repair_compaction_threshold: 1024
```

> Prevents preparing a repair session or beginning a repair streaming session if pending compactions is over
> the given value.  Defaults to disabled.

### `repair_disk_headroom_reject_ratio`

<a id="repair_disk_headroom_reject_ratio"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2344

```yaml
repair_disk_headroom_reject_ratio: 0.0
```

> Ratio of disk that must be unused to run repair. It is useful to avoid disks filling up during
> repair as anti-compaction during repair may contribute to additional space temporarily.
> For example, setting this to 0.2 means at least 20% of disk must be unused.
> Set to 0.0 to disable this check. Defaults to 0.0 (disabled) on 5.0 for backward-compatibility.

### `auto_repair`

<a id="auto_repair"></a>

*Commented (built-in default applies)* · `conf/cassandra.yaml` line 2355

```yaml
auto_repair:
  # Enable/Disable the auto-repair scheduler.
  # If set to false, the scheduler thread will not be started.
  # If set to true, the repair scheduler thread will be created. The thread will
  # check for secondary configuration available for each repair type (full, incremental,
  # and preview_repaired), and based on that, it will schedule repairs.
  enabled: true
  repair_type_overrides:
    full:
      # Enable/Disable full auto-repair
      enabled: true
      # Minimum duration between repairing the same node again. This is useful for tiny clusters,
      # such as clusters with 5 nodes that finish repairs quickly. This means that if the scheduler completes one
      # round on all nodes in less than this duration, it will not start a new repair round on a given node until
      # this much time has passed since the last repair completed. Consider increasing to a larger value to reduce
      # the impact of repairs, however note that one should attempt to run repairs at a smaller interval than
      # gc_grace_seconds to avoid potential data resurrection.
      min_repair_interval: 24h
      token_range_splitter:
        # Implementation of IAutoRepairTokenRangeSplitter; responsible for splitting token ranges
        # for repair assignments.
        #
        # Out of the box, Cassandra provides org.apache.cassandra.repair.autorepair.{RepairTokenRangeSplitter,
        # FixedTokenRangeSplitter}.
        #
        # - RepairTokenRangeSplitter (default) attempts to intelligently split ranges based on data size and partition
        #   count.
        # - FixedTokenRangeSplitter splits into fixed ranges based on the 'number_of_subranges' option.
        # class_name: org.apache.cassandra.repair.autorepair.RepairTokenRangeSplitter
        # Optional parameters can be specified in the form of:
        #   parameters:
        #    param_key1: param_value1
        parameters:
          # The target and maximum amount of compressed bytes that should be included in a repair assignment.
          # This scopes the amount of work involved in a repair and includes the data covering the range being
          # repaired.
          bytes_per_assignment: 50GiB
          # The maximum number of bytes to cover in an individual schedule. This serves as
          # a mechanism to throttle the work done in each repair cycle. You may reduce this
          # value if the impact of repairs is causing too much load on the cluster or increase it
          # if writes outpace the amount of data being repaired. Alternatively, adjust the
          # min_repair_interval.
          # This is set to a large value for full repair to attempt to repair all data per repair schedule.
          max_bytes_per_schedule: 100000GiB
    incremental:
      enabled: false
      # Incremental repairs operate over unrepaired data and should finish quickly. Running incremental repair
      # frequently keeps the unrepaired set smaller and thus causes repairs to operate over a smaller set of data,
      # so a more frequent schedule such as 1h is recommended.
      # NOTE: Please consult
      # https://cassandra.apache.org/doc/latest/cassandra/managing/operating/auto_repair.html#enabling-ir
      # for guidance on enabling incremental repair on an existing cluster.
      min_repair_interval: 24h
      token_range_splitter:
        parameters:
          # Configured to attempt repairing 50GiB of compressed data per repair.
          # This throttles the amount of incremental repair and anticompaction done per schedule after incremental
          # repairs are turned on.
          bytes_per_assignment: 50GiB
          # Restricts the maximum number of bytes to cover in an individual schedule to the configured
          # max_bytes_per_schedule value (defaults to 100GiB for incremental).
          # Consider increasing this value if more data is written than this limit within the min_repair_interval.
          max_bytes_per_schedule: 100GiB
    preview_repaired:
      # Performs preview repair over repaired SSTables, useful to detect possible inconsistencies in the repaired
      # data set.
      enabled: false
      min_repair_interval: 24h
      token_range_splitter:
        parameters:
          bytes_per_assignment: 50GiB
          max_bytes_per_schedule: 100000GiB
  # Time interval between successive checks to see if ongoing repairs are complete or if it is time to schedule
  # repairs.
  repair_check_interval: 5m
  # Minimum duration for the execution of a single repair task. This prevents the scheduler from overwhelming
  # the node by scheduling too many repair tasks in a short period of time.
  repair_task_min_duration: 5s
  # The scheduler needs to adjust its order when nodes leave the ring. Deleted hosts are tracked in metadata
  # for a specified duration to ensure they are indeed removed before adjustments are made to the schedule.
  history_clear_delete_hosts_buffer_interval: 2h
  # By default repair is disabled if there are mixed major versions detected - which would happen
  # if a major version upgrade is being performed on the cluster, but a user can enable it using this flag
  mixed_major_version_repair_enabled: false
  # NOTE: Each of the below settings can be overridden per repair type under repair_type_overrides
  global_settings:
    # If true, attempts to group tables in the same keyspace into one repair; otherwise, each table is repaired
    # individually.
    repair_by_keyspace: true
    # Number of threads to use for each repair job scheduled by the scheduler. Similar to the -j option in nodetool
    # repair.
    number_of_repair_threads: 1
    # Number of nodes running repair in parallel. If parallel_repair_percentage is set, the larger value is used.
    parallel_repair_count: 3
    # Percentage of nodes in the cluster running repair in parallel. If parallel_repair_count is set, the larger value
    # is used.
    parallel_repair_percentage: 3
    # Whether to allow a node to take its turn running repair while one or more of its replicas are running repair.
    # Defaults to false, as running repairs concurrently on replicas can increase load and also cause anticompaction
    # conflicts while running incremental repair.
    allow_parallel_replica_repair: false
    # An addition to allow_parallel_replica_repair that also blocks repairs when replicas (including this node itself)
    # are repairing in any schedule. For example, if a replica is executing full repairs, a value of false will
    # prevent starting incremental repairs for this node. Defaults to true and is only evaluated when
    # allow_parallel_replica_repair is false.
    allow_parallel_replica_repair_across_schedules: true
    # Repairs materialized views if true.
    materialized_view_repair_enabled: false
    # Delay before starting repairs after a node restarts to avoid repairs starting immediately after a restart.
    initial_scheduler_delay: 5m
    # Timeout for retrying stuck repair sessions.
    repair_session_timeout: 3h
    # Force immediate repair on new nodes after they join the ring.
    force_repair_new_node: false
    # Threshold to skip repairing tables with too many SSTables. Defaults to 10,000 SSTables to avoid penalizing good
    # tables.
    sstable_upper_threshold: 50000
    # Maximum time allowed for repairing one table on a given node. If exceeded, the repair proceeds to the
    # next table.
    table_max_repair_time: 6h
    # Avoid running repairs in specific data centers. By default, repairs run in all data centers. Specify data
    # centers to exclude in this list. Note that repair sessions will still consider all replicas from excluded
    # data centers. Useful if you have keyspaces that are not replicated in certain data centers, and you want to
    # not run repair schedule in certain data centers.
    ignore_dcs: []
    # Repair only the primary ranges owned by a node. Equivalent to the -pr option in nodetool repair. Defaults
    # to true. General advice is to keep this true.
    repair_primary_token_range_only: true
    # Maximum number of retries for a repair session.
    repair_max_retries: 3
    # Backoff time before retrying a repair session.
    repair_retry_backoff: 30s
    token_range_splitter:
      # Splitter implementation to generate repair assignments. Defaults to RepairTokenRangeSplitter.
      class_name: org.apache.cassandra.repair.autorepair.RepairTokenRangeSplitter
      parameters:
        # Maximum number of partitions to include in a repair assignment. Used to reduce number of partitions
        # present in merkle tree leaf nodes to avoid overstreaming.
        partitions_per_assignment: 1048576
        # Maximum number of tables to include in a repair assignment. This reduces the number of repairs,
        # especially in keyspaces with many tables. The splitter avoids batching tables together if they
        # exceed other configuration parameters like bytes_per_assignment or partitions_per_assignment.
        max_tables_per_assignment: 64
```

**In `cassandra_latest.yaml`** (commented):

```yaml
auto_repair:
  # Enable/Disable the auto-repair scheduler.
  # If set to false, the scheduler thread will not be started.
  # If set to true, the repair scheduler thread will be created. The thread will
  # check for secondary configuration available for each repair type (full, incremental,
  # and preview_repaired), and based on that, it will schedule repairs.
  enabled: true
  repair_type_overrides:
    full:
      # Enable/Disable full auto-repair
      enabled: true
      # Minimum duration between repairing the same node again. This is useful for tiny clusters,
      # such as clusters with 5 nodes that finish repairs quickly. This means that if the scheduler completes one
      # round on all nodes in less than this duration, it will not start a new repair round on a given node until
      # this much time has passed since the last repair completed. Consider increasing to a larger value to reduce
      # the impact of repairs, however note that one should attempt to run repairs at a smaller interval than
      # gc_grace_seconds to avoid potential data resurrection.
      min_repair_interval: 24h
      token_range_splitter:
        # Implementation of IAutoRepairTokenRangeSplitter; responsible for splitting token ranges
        # for repair assignments.
        #
        # Out of the box, Cassandra provides org.apache.cassandra.repair.autorepair.{RepairTokenRangeSplitter,
        # FixedTokenRangeSplitter}.
        #
        # - RepairTokenRangeSplitter (default) attempts to intelligently split ranges based on data size and partition
        #   count.
        # - FixedTokenRangeSplitter splits into fixed ranges based on the 'number_of_subranges' option.
        # class_name: org.apache.cassandra.repair.autorepair.RepairTokenRangeSplitter
        # Optional parameters can be specified in the form of:
        #   parameters:
        #    param_key1: param_value1
        parameters:
          # The target and maximum amount of compressed bytes that should be included in a repair assignment.
          # This scopes the amount of work involved in a repair and includes the data covering the range being
          # repaired.
          bytes_per_assignment: 50GiB
          # The maximum number of bytes to cover in an individual schedule. This serves as
          # a mechanism to throttle the work done in each repair cycle. You may reduce this
          # value if the impact of repairs is causing too much load on the cluster or increase it
          # if writes outpace the amount of data being repaired. Alternatively, adjust the
          # min_repair_interval.
          # This is set to a large value for full repair to attempt to repair all data per repair schedule.
          max_bytes_per_schedule: 100000GiB
    incremental:
      enabled: false
      # Incremental repairs operate over unrepaired data and should finish quickly. Running incremental repair
      # frequently keeps the unrepaired set smaller and thus causes repairs to operate over a smaller set of data,
      # so a more frequent schedule such as 1h is recommended.
      # NOTE: Please consult
      # https://cassandra.apache.org/doc/latest/cassandra/managing/operating/auto_repair.html#enabling-ir
      # for guidance on enabling incremental repair on ane exiting cluster.
      min_repair_interval: 24h
      token_range_splitter:
        parameters:
          # Configured to attempt repairing 50GiB of compressed data per repair.
          # This throttles the amount of incremental repair and anticompaction done per schedule after incremental
          # repairs are turned on.
          bytes_per_assignment: 50GiB
          # Restricts the maximum number of bytes to cover in an individual schedule to the configured
          # max_bytes_per_schedule value (defaults to 100GiB for incremental).
          # Consider increasing this value if more data is written than this limit within the min_repair_interval.
          max_bytes_per_schedule: 100GiB
    preview_repaired:
      # Performs preview repair over repaired SSTables, useful to detect possible inconsistencies in the repaired
      # data set.
      enabled: false
      min_repair_interval: 24h
      token_range_splitter:
        parameters:
          bytes_per_assignment: 50GiB
          max_bytes_per_schedule: 100000GiB
  # Time interval between successive checks to see if ongoing repairs are complete or if it is time to schedule
  # repairs.
  repair_check_interval: 5m
  # Minimum duration for the execution of a single repair task. This prevents the scheduler from overwhelming
  # the node by scheduling too many repair tasks in a short period of time.
  repair_task_min_duration: 5s
  # The scheduler needs to adjust its order when nodes leave the ring. Deleted hosts are tracked in metadata
  # for a specified duration to ensure they are indeed removed before adjustments are made to the schedule.
  history_clear_delete_hosts_buffer_interval: 2h
  # By default repair is disabled if there are mixed major versions detected - which would happen
  # if a major version upgrade is being performed on the cluster, but a user can enable it using this flag
  mixed_major_version_repair_enabled: false
  # NOTE: Each of the below settings can be overridden per repair type under repair_type_overrides
  global_settings:
    # If true, attempts to group tables in the same keyspace into one repair; otherwise, each table is repaired
    # individually.
    repair_by_keyspace: true
    # Number of threads to use for each repair job scheduled by the scheduler. Similar to the -j option in nodetool
    # repair.
    number_of_repair_threads: 1
    # Number of nodes running repair in parallel. If parallel_repair_percentage is set, the larger value is used.
    parallel_repair_count: 3
    # Percentage of nodes in the cluster running repair in parallel. If parallel_repair_count is set, the larger value
    # is used.
    parallel_repair_percentage: 3
    # Whether to allow a node to take its turn running repair while one or more of its replicas are running repair.
    # Defaults to false, as running repairs concurrently on replicas can increase load and also cause anticompaction
    # conflicts while running incremental repair.
    allow_parallel_replica_repair: false
    # An addition to allow_parallel_replica_repair that also blocks repairs when replicas (including this node itself)
    # are repairing in any schedule. For example, if a replica is executing full repairs, a value of false will
    # prevent starting incremental repairs for this node. Defaults to true and is only evaluated when
    # allow_parallel_replica_repair is false.
    allow_parallel_replica_repair_across_schedules: true
    # Repairs materialized views if true.
    materialized_view_repair_enabled: false
    # Delay before starting repairs after a node restarts to avoid repairs starting immediately after a restart.
    initial_scheduler_delay: 5m
    # Timeout for retrying stuck repair sessions.
    repair_session_timeout: 3h
    # Force immediate repair on new nodes after they join the ring.
    force_repair_new_node: false
    # Threshold to skip repairing tables with too many SSTables. Defaults to 10,000 SSTables to avoid penalizing good
    # tables.
    sstable_upper_threshold: 50000
    # Maximum time allowed for repairing one table on a given node. If exceeded, the repair proceeds to the
    # next table.
    table_max_repair_time: 6h
    # Avoid running repairs in specific data centers. By default, repairs run in all data centers. Specify data
    # centers to exclude in this list. Note that repair sessions will still consider all replicas from excluded
    # data centers. Useful if you have keyspaces that are not replicated in certain data centers, and you want to
    # not run repair schedule in certain data centers.
    ignore_dcs: []
    # Repair only the primary ranges owned by a node. Equivalent to the -pr option in nodetool repair. Defaults
    # to true. General advice is to keep this true.
    repair_primary_token_range_only: true
    # Maximum number of retries for a repair session.
    repair_max_retries: 3
    # Backoff time before retrying a repair session.
    repair_retry_backoff: 30s
    token_range_splitter:
      # Splitter implementation to generate repair assignments. Defaults to RepairTokenRangeSplitter.
      class_name: org.apache.cassandra.repair.autorepair.RepairTokenRangeSplitter
      parameters:
        # Maximum number of partitions to include in a repair assignment. Used to reduce number of partitions
        # present in merkle tree leaf nodes to avoid overstreaming.
        partitions_per_assignment: 1048576
        # Maximum number of tables to include in a repair assignment. This reduces the number of repairs,
        # especially in keyspaces with many tables. The splitter avoids batching tables together if they
        # exceed other configuration parameters like bytes_per_assignment or partitions_per_assignment.
        max_tables_per_assignment: 64
```

> Configuration for Auto Repair Scheduler.
>
> This feature is disabled by default.
>
> NOTE: The auto-repair feature requires enabling the JVM property `cassandra.autorepair.enable=true`.
>
> See: https://cassandra.apache.org/doc/latest/cassandra/managing/operating/auto_repair.html for an overview of this
> feature.

## Accepted by Config.java but not present in either yaml file

These keys are valid but undocumented in the shipped files. Check `Config.java` and `NEWS.txt` before using them.

`allow_extra_insecure_udfs`, `allow_insecure_udfs`, `auto_bootstrap`, `auto_optimise_full_repair_streams`, `auto_optimise_inc_repair_streams`, `auto_optimise_preview_repair_streams`, `autocompaction_on_startup_enabled`, `available_processors`, `back_pressure_enabled`, `back_pressure_strategy`, `block_for_peers_in_remote_dcs`, `block_for_peers_timeout_in_secs`, `check_for_duplicate_rows_during_compaction`, `check_for_duplicate_rows_during_reads`, `client_request_size_metrics_enabled`, `commitlog_max_compression_buffers_in_pool`, `compact_tables_enabled`, `compressed_read_ahead_buffer_size`, `concurrent_index_builders`, `consecutive_message_errors_threshold`, `cql_start_time`, `credentials_cache_max_entries`, `disk_optimization_estimate_percentile`, `disk_optimization_page_cross_chance`, `dynamic_snitch`, `enforce_native_deadline_for_hints`, `failure_detector`, `file_cache_round_up`, `force_new_prepared_statement_behaviour`, `force_optimized_index_status_format`, `initial_range_tombstone_list_allocation_size`, `internode_error_reporting_exclusions`, `internode_max_message_size`, `intersect_filtering_query_enabled`, `intersect_filtering_query_warned`, `invalid_legacy_protocol_magic_no_spam_enabled`, `key_cache_invalidate_after_sstable_deletion`, `key_cache_migrate_during_compaction`, `log_out_of_token_range_requests`, `max_mutation_size`, `max_space_usable_for_compactions_in_percentage`, `max_streaming_retries`, `max_top_size_partition_count`, `max_top_tombstone_partition_count`, `min_free_space_per_drive`, `min_tracked_partition_size`, `min_tracked_partition_tombstone_count`, `native_transport_max_backoff_on_queue_overload`, `native_transport_max_message_size`, `native_transport_max_request_data_in_flight`, `native_transport_max_request_data_in_flight_per_ip`, `native_transport_min_backoff_on_queue_overload`, `native_transport_queue_max_item_age_threshold`, `native_transport_receive_queue_capacity`, `native_transport_throw_on_overload`, `native_transport_timeout`, `otc_backlog_expiration_interval_ms`, `otc_coalescing_enough_coalesced_messages`, `otc_coalescing_strategy`, `otc_coalescing_window_us`, `paxos_cache_size`, `paxos_contention_max_wait`, `paxos_contention_min_delta`, `paxos_contention_min_wait`, `paxos_contention_wait_randomizer`, `paxos_on_linearizability_violations`, `paxos_purge_grace_period`, `paxos_repair_enabled`, `paxos_repair_parallelism`, `paxos_repair_race_wait`, `paxos_state_purging`, `paxos_topology_repair_no_dc_checks`, `paxos_topology_repair_strict_each_quorum`, `permissions_cache_max_entries`, `range_tombstone_list_growth_factor`, `reject_out_of_token_range_requests`, `repair_command_pool_full_strategy`, `repair_command_pool_size`, `repair_request_timeout`, `repair_session_max_tree_depth`, `repair_state_expires`, `repair_state_size`, `roles_cache_max_entries`, `scripted_user_defined_functions_enabled`, `severity_during_decommission`, `skip_paxos_repair_on_topology_change`, `skip_paxos_repair_on_topology_change_keyspaces`, `skip_stream_disk_space_check`, `snapshot_on_duplicate_row_detection`, `snapshot_on_repaired_data_mismatch`, `sstable_read_rate_persistence_enabled`, `stream_transfer_task_timeout`, `streaming_slow_events_log_timeout`, `top_partitions_enabled`, `use_creation_time_for_hint_ttl`, `use_deterministic_table_id`, `use_offheap_merkle_trees`, `user_defined_functions_fail_timeout`, `user_defined_functions_threads_enabled`, `user_defined_functions_warn_timeout`, `user_function_timeout_policy`, `validation_preview_purge_head_start`, `vector_type_enabled`, `windows_timer_interval`

## Deprecated key names still accepted

| Old name | Current name |
| :--- | :--- |
| `batch_size_fail_threshold_in_kb` | `batch_size_fail_threshold` |
| `batch_size_warn_threshold_in_kb` | `batch_size_warn_threshold` |
| `batchlog_replay_throttle_in_kb` | `batchlog_replay_throttle` |
| `cache_load_timeout_seconds` | `cache_load_timeout` |
| `cas_contention_timeout_in_ms` | `cas_contention_timeout` |
| `cdc_free_space_check_interval_ms` | `cdc_free_space_check_interval` |
| `cdc_total_space_in_mb` | `cdc_total_space` |
| `column_index_cache_size_in_kb` | `column_index_cache_size` |
| `column_index_size_in_kb` | `column_index_size` |
| `commitlog_segment_size_in_mb` | `commitlog_segment_size` |
| `commitlog_sync_group_window_in_ms` | `commitlog_sync_group_window` |
| `commitlog_sync_period_in_ms` | `commitlog_sync_period` |
| `commitlog_total_space_in_mb` | `commitlog_total_space` |
| `compaction_large_partition_warning_threshold` | `partition_size_warn_threshold` |
| `compaction_large_partition_warning_threshold_mb` | `partition_size_warn_threshold` |
| `compaction_throughput_mb_per_sec` | `compaction_throughput` |
| `compaction_tombstone_warning_threshold` | `partition_tombstones_warn_threshold` |
| `counter_cache_save_period` | `counter_cache_save_period` |
| `counter_cache_size_in_mb` | `counter_cache_size` |
| `counter_write_request_timeout_in_ms` | `counter_write_request_timeout` |
| `credentials_update_interval_in_ms` | `credentials_update_interval` |
| `credentials_validity_in_ms` | `credentials_validity` |
| `cross_node_timeout` | `internode_timeout` |
| `dynamic_snitch_reset_interval_in_ms` | `dynamic_snitch_reset_interval` |
| `dynamic_snitch_update_interval_in_ms` | `dynamic_snitch_update_interval` |
| `enable_drop_compact_storage` | `drop_compact_storage_enabled` |
| `enable_materialized_views` | `materialized_views_enabled` |
| `enable_sasi_indexes` | `sasi_indexes_enabled` |
| `enable_scripted_user_defined_functions` | `scripted_user_defined_functions_enabled` |
| `enable_transient_replication` | `transient_replication_enabled` |
| `enable_user_defined_functions` | `user_defined_functions_enabled` |
| `enable_user_defined_functions_threads` | `user_defined_functions_threads_enabled` |
| `file_cache_size_in_mb` | `file_cache_size` |
| `gc_log_threshold_in_ms` | `gc_log_threshold` |
| `gc_warn_threshold_in_ms` | `gc_warn_threshold` |
| `hinted_handoff_throttle_in_kb` | `hinted_handoff_throttle` |
| `hints_flush_period_in_ms` | `hints_flush_period` |
| `index_summary_capacity_in_mb` | `index_summary_capacity` |
| `index_summary_resize_interval_in_minutes` | `index_summary_resize_interval` |
| `inter_dc_stream_throughput_outbound_megabits_per_sec` | `inter_dc_stream_throughput_outbound` |
| `internode_application_receive_queue_capacity_in_bytes` | `internode_application_receive_queue_capacity` |
| `internode_application_receive_queue_reserve_endpoint_capacity_in_bytes` | `internode_application_receive_queue_reserve_endpoint_capacity` |
| `internode_application_receive_queue_reserve_global_capacity_in_bytes` | `internode_application_receive_queue_reserve_global_capacity` |
| `internode_application_send_queue_capacity_in_bytes` | `internode_application_send_queue_capacity` |
| `internode_application_send_queue_reserve_endpoint_capacity_in_bytes` | `internode_application_send_queue_reserve_endpoint_capacity` |
| `internode_application_send_queue_reserve_global_capacity_in_bytes` | `internode_application_send_queue_reserve_global_capacity` |
| `internode_max_message_size_in_bytes` | `internode_max_message_size` |
| `internode_recv_buff_size_in_bytes` | `internode_socket_receive_buffer_size` |
| `internode_send_buff_size_in_bytes` | `internode_socket_send_buffer_size` |
| `internode_socket_receive_buffer_size_in_bytes` | `internode_socket_receive_buffer_size` |
| `internode_socket_send_buffer_size_in_bytes` | `internode_socket_send_buffer_size` |
| `internode_streaming_tcp_user_timeout_in_ms` | `internode_streaming_tcp_user_timeout` |
| `internode_tcp_connect_timeout_in_ms` | `internode_tcp_connect_timeout` |
| `internode_tcp_user_timeout_in_ms` | `internode_tcp_user_timeout` |
| `key_cache_save_period` | `key_cache_save_period` |
| `key_cache_size_in_mb` | `key_cache_size` |
| `keyspace_count_warn_threshold` | `keyspaces_warn_threshold` |
| `max_hint_window_in_ms` | `max_hint_window` |
| `max_hints_file_size_in_mb` | `max_hints_file_size` |
| `max_mutation_size_in_kb` | `max_mutation_size` |
| `max_value_size_in_mb` | `max_value_size` |
| `memtable_heap_space_in_mb` | `memtable_heap_space` |
| `memtable_offheap_space_in_mb` | `memtable_offheap_space` |
| `min_free_space_per_drive_in_mb` | `min_free_space_per_drive` |
| `native_transport_idle_timeout_in_ms` | `native_transport_idle_timeout` |
| `native_transport_max_concurrent_requests_in_bytes` | `native_transport_max_request_data_in_flight` |
| `native_transport_max_concurrent_requests_in_bytes_per_ip` | `native_transport_max_request_data_in_flight_per_ip` |
| `native_transport_max_frame_size_in_mb` | `native_transport_max_frame_size` |
| `native_transport_receive_queue_capacity_in_bytes` | `native_transport_receive_queue_capacity` |
| `networking_cache_size_in_mb` | `networking_cache_size` |
| `periodic_commitlog_sync_lag_block_in_ms` | `periodic_commitlog_sync_lag_block` |
| `permissions_update_interval_in_ms` | `permissions_update_interval` |
| `permissions_validity_in_ms` | `permissions_validity` |
| `prepared_statements_cache_size_mb` | `prepared_statements_cache_size` |
| `range_request_timeout_in_ms` | `range_request_timeout` |
| `read_request_timeout_in_ms` | `read_request_timeout` |
| `repair_request_timeout_in_ms` | `repair_request_timeout` |
| `repair_session_space_in_mb` | `repair_session_space` |
| `request_timeout_in_ms` | `request_timeout` |
| `roles_update_interval_in_ms` | `roles_update_interval` |
| `roles_validity_in_ms` | `roles_validity` |
| `row_cache_save_period` | `row_cache_save_period` |
| `row_cache_size_in_mb` | `row_cache_size` |
| `slow_query_log_timeout_in_ms` | `slow_query_log_timeout` |
| `sstable_preemptive_open_interval_in_mb` | `sstable_preemptive_open_interval` |
| `stream_throughput_outbound_megabits_per_sec` | `stream_throughput_outbound` |
| `streaming_keep_alive_period_in_secs` | `streaming_keep_alive_period` |
| `table_count_warn_threshold` | `tables_warn_threshold` |
| `tracetype_query_ttl` | `trace_type_query_ttl` |
| `tracetype_repair_ttl` | `trace_type_repair_ttl` |
| `trickle_fsync_interval_in_kb` | `trickle_fsync_interval` |
| `truncate_request_timeout_in_ms` | `truncate_request_timeout` |
| `user_defined_function_fail_timeout` | `user_defined_functions_fail_timeout` |
| `user_defined_function_warn_timeout` | `user_defined_functions_warn_timeout` |
| `validation_preview_purge_head_start_in_sec` | `validation_preview_purge_head_start` |
| `write_request_timeout_in_ms` | `write_request_timeout` |
