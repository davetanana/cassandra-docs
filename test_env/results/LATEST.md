# Validation results (20261122-052858)

- Image: `cassandra:5.0`  Cassandra: `5.0.9` (recorded by hand for this run: the runner read the version after scenarios 12 and 13 had stopped the cluster; fixed in `run.sh`. Scenario 12 ran the same image and its node reported `ReleaseVersion: 5.0.9`)
- Docs commit: `98a005c`

| Scenario | PASS | FAIL | WARN | SKIP |
|---|---|---|---|---|
| 00_docs_static | 21 | 0 | 0 | 2 |
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
| 12_quickstart | 16 | 0 | 0 | 0 |
| 13_client_drivers | 3 | 0 | 0 | 0 |

## Failures and warnings (fix the doc or the test; see test_env/AGENTS.md)

