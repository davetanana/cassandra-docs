# Roadmap

Where this guide stands against the official Apache Cassandra 5.0 documentation, and what to work on next. Pick anything here; open an issue first for larger items (see [CONTRIBUTING.md](CONTRIBUTING.md)).

## 1. How the guide compares with the official docs

This comparison uses the official docs source on the `cassandra-5.0` branch (`doc/modules/cassandra/pages`, about 174,000 words), checked in November 2026. The guide is about 33,000 hand-written words plus the generated references.

| Area | Official 5.0 docs | This guide |
| :--- | :--- | :--- |
| The two config templates | `cassandra_latest.yaml` and `storage_compatibility_mode` are not mentioned | Explained up front; every default names its template |
| Upgrading 4.x → 5.0 | No upgrade procedure | Full runbook, including compatibility-mode stages and rollback limits |
| Restore | The backups page mentions restore once | Node replacement, table restore, dropped-table restore, point-in-time and full-cluster restore, tested |
| Troubleshooting | Organized by tool | Organized by symptom, with the exact log text |
| Cloud and Kubernetes | Snitch names only | AWS, GCP, Azure and Kubernetes pages |
| Paxos v2 | `paxos_variant` not documented | Covered with upgrade steps |
| Drivers | One overview page | Java rules plus a source-checked defaults comparison for Python, Go and Node.js, with tested examples |
| Accuracy | Hand-written; some stub pages and a `//TBD` | Names and defaults checked in CI; behavior tested on a live cluster |
| CQL for newcomers | Grammar-first reference pages; few examples show output | A clause-by-clause querying page on one sample dataset, with real `cqlsh` output and the exact error for each refused query; an error-message table |
| CQL functions | One page; most functions have a syntax line but no example output | One entry per function with argument and return types and a tested example; traps called out (Thursday weeks in `floor`, integer `avg`) |
| cqlsh | One page of options and commands | Scripting (batch-mode exit codes, stdout vs stderr), output formats, reading a trace, environment variables, tested examples |
| **CQL reference depth** | **65 pages** (full DDL grammar, every statement option) | A quick-reference page plus the pages above |
| **Breadth** | Read repair, transient replication, denylisting, compression, bloom filters, plugins, CDC internals | Light or missing |
| **Architecture theory** | Dynamo, storage engine, messaging | Mental-model level only |

The guide aims to complement the official docs, not replace them. It should link to the official pages for theory and the full CQL reference, and own the operational "how do I do this safely" material.

## 2. Conventions borrowed from the ClickHouse docs

The ClickHouse documentation is a good model for query-language docs. This guide now follows three of its conventions, with one change: the examples here are tested.

* **Every function entry has the same shape:** syntax, arguments, returned type, then an example query with its result ([functions reference](09_reference/05_cql_functions.md)).
* **`SELECT` is explained one clause at a time**, each with examples and their output ([Querying with CQL](03_application_development/05_querying_with_cql.md)).
* **The command-line client has its own page** covering interactive and scripted use ([cqlsh](09_reference/06_cqlsh.md)).

Still missing compared with ClickHouse:

* **A reference page per system table.** ClickHouse documents each `system.*` table with its columns. The Cassandra equivalent is `system_views` (virtual tables) plus `system_schema`. A generated page listing every virtual table and column, from a running node or the source, with one tested example query each, would close this.
* **A hosted playground.** ClickHouse runs a public read-only instance. Not possible without hosting costs; the quickstart node and the `examples` dataset are the free equivalent.
* **One page per data type.** The [quick reference](09_reference/04_cql_quick_reference.md#3-data-types) has a size-and-range table; per-type pages with literal formats and `cqlsh` display examples would help.
* **Larger sample datasets.** The [data-modeling tutorial](00_getting_started/02_tutorial_data_modeling.md) and the [operations drill](00_getting_started/03_tutorial_operations.md) use small fixed datasets; a time-series workload loaded with `COPY FROM` would show partition sizing and compaction at scale.

## 3. Content gaps, in priority order

1. **Kubernetes validation.** The [Kubernetes page](04_infrastructure_and_cloud/05_kubernetes.md) was checked against cass-operator's source, not run. Add a scenario that installs cass-operator on a `kind` cluster and applies the page's `CassandraDatacenter`, as an optional CI job.
2. **More driver languages.** C# and Rust, plus Spring Data Cassandra for Java teams. Check each default against the driver's source, as section 7 of the drivers page does.
3. **Operations topics the official docs cover and this guide doesn't:** read repair settings, compression choices, `denylisting_partitions`, CDC operations, bloom filter tuning.
4. **Migration guides** from other databases (PostgreSQL, DynamoDB, MongoDB) to Cassandra concepts.
5. **Glossary.** The official one is a single link; a guide-specific glossary linked from first use of each term would help newcomers.

## 4. Runbooks not yet automated in `test_env`

This list is kept in [test_env/README.md](test_env/README.md#not-yet-automated). Each item there is documented but not yet tested on the cluster.

## 5. Project health

* **More maintainers.** The guide has one maintainer. Regular contributors who review pull requests for a phase (for example, operations or drivers) would reduce that risk.
* **Release cadence.** Run workflow C in [test_env/AGENTS.md](test_env/AGENTS.md) for each Cassandra 5.0.x release, and tag a guide release so the AI bundle is attached.
* **Cassandra 5.1 / 6.0.** When the next major version ships, decide whether to branch the guide per major version or to add version notes to each page.
