#!/usr/bin/env bash
# DOC: 01_architecture_and_mental_model/01_mental_model.md, 05_cluster_deployment_and_config/01_configuration_and_tuning.md,
#      03_application_development/*.md, 09_reference/01_cassandra_yaml_reference.md
# CLAIMS: the runtime defaults the docs quote for the shipped cassandra.yaml (read from system_views.settings).
#         A setting the table doesn't expose is a WARN (the claim couldn't be checked), not a FAIL.
set -uo pipefail
source "$(dirname "$0")/../scripts/lib.sh"
require_nodes cass1

# doc_ref | setting name | expected substring of value
while IFS='|' read -r ref name want; do
  [ -z "$name" ] && continue
  got=$(cq_val $SEED "SELECT value FROM system_views.settings WHERE name='$name';")
  if [ -z "$got" ]; then warn "$ref" "setting $name = $want" "not exposed in system_views.settings"
  elif grep -qiF -- "$want" <<<"$got"; then pass "$ref" "setting $name = $want"
  else fail "$ref" "setting $name = $want" "actual value: $got"; fi
done <<'EOF'
01_architecture_and_mental_model/01_mental_model.md|num_tokens|16
01_architecture_and_mental_model/01_mental_model.md|commitlog_sync|periodic
01_architecture_and_mental_model/01_mental_model.md|commitlog_sync_period|10
01_architecture_and_mental_model/01_mental_model.md|storage_compatibility_mode|CASSANDRA_4
01_architecture_and_mental_model/01_mental_model.md|memtable_allocation_type|heap_buffers
01_architecture_and_mental_model/01_mental_model.md|row_cache_size|0
02_data_modeling_and_indexing/02_indexing_and_vector_search.md|default_secondary_index|legacy_local_table
03_application_development/04_consistency_and_transactions.md|paxos_variant|v1
03_application_development/04_consistency_and_transactions.md|dynamic_data_masking_enabled|false
02_data_modeling_and_indexing/01_schema_design_patterns.md|materialized_views_enabled|false
03_application_development/01_performant_writes.md|batch_size_warn_threshold|5
03_application_development/01_performant_writes.md|batch_size_fail_threshold|50
03_application_development/01_performant_writes.md|unlogged_batch_across_partitions_warn_threshold|10
03_application_development/01_performant_writes.md|tombstone_warn_threshold|1000
03_application_development/01_performant_writes.md|tombstone_failure_threshold|100000
05_cluster_deployment_and_config/01_configuration_and_tuning.md|concurrent_reads|32
05_cluster_deployment_and_config/01_configuration_and_tuning.md|concurrent_writes|32
05_cluster_deployment_and_config/01_configuration_and_tuning.md|compaction_throughput|64
05_cluster_deployment_and_config/01_configuration_and_tuning.md|max_hint_window|3h
05_cluster_deployment_and_config/01_configuration_and_tuning.md|auto_snapshot|true
05_cluster_deployment_and_config/01_configuration_and_tuning.md|read_request_timeout|5000
05_cluster_deployment_and_config/01_configuration_and_tuning.md|write_request_timeout|2000
06_operations_and_housekeeping/03_monitoring_and_observability.md|slow_query_log_timeout|500
EOF
