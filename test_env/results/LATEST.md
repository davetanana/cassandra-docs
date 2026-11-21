# Validation results (20261121-114345)

- Image: `cassandra:5.0`  Cassandra: `5.0.9` (recorded by hand for this run; `run.sh` now captures it automatically)
- Docs commit: n/a (run before the guide had its own repository; `47227d98bf` was the enclosing Cassandra checkout)

| Scenario | PASS | FAIL | WARN | SKIP |
|---|---|---|---|---|
| 00_docs_static | 7 | 0 | 0 | 2 |
| 01_bootstrap_and_topology | 17 | 0 | 0 | 0 |
| 02_config_defaults | 23 | 0 | 0 | 0 |
| 03_cql_claims | 35 | 0 | 0 | 0 |
| 04_nodetool_claims | 20 | 0 | 0 | 0 |
| 05_restore_import | 9 | 0 | 0 | 0 |
| 06_dropped_table_restore | 8 | 0 | 0 | 0 |
| 07_s3_backup_include_pattern | 5 | 0 | 0 | 0 |
| 08_rolling_restart | 14 | 0 | 0 | 0 |
| 09_node_replacement | 9 | 0 | 0 | 0 |
| 10_add_datacenter | 9 | 0 | 0 | 0 |
| 11_auto_repair | 16 | 0 | 0 | 0 |

## Failures and warnings (fix the doc or the test; see test_env/AGENTS.md)

