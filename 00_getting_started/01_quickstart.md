# Quickstart: Your First 15 Minutes with Cassandra 5.0

This page takes you from nothing to a running Cassandra 5.0 node, a table designed the Cassandra way, an index, and a small application that reads and writes it. Each step says which idea it shows and links to the page that explains it.

> [!WARNING]
> This is a **development** setup: one node, replication factor 1, no authentication, no TLS. Don't use it for anything you want to keep. For a real cluster, follow the [deployment runbook](../05_cluster_deployment_and_config/02_cluster_deployment_runbook.md) and [security hardening](../05_cluster_deployment_and_config/03_security_hardening.md).

---

## 1. What you need

* Docker (Docker Desktop on macOS or Windows, or Docker Engine on Linux).
* About 2 GB of free memory for Docker. The command below caps the Java heap at 1 GB.
* Port 9042 free on your machine. That is the CQL port that drivers connect to.
* Python 3.9 or later for step 6. You can skip step 6 if you only want to try CQL.

---

## 2. Start one node

<!-- test: start -->
```bash
docker run --name cass-quickstart -d -p 9042:9042 -e MAX_HEAP_SIZE=1G cassandra:5.0
```

`cassandra:5.0` is the official image. It always points to the newest 5.0.x release. `MAX_HEAP_SIZE` caps the Java heap. Without it, Cassandra sizes the heap from the memory it can see, which on a laptop is more than you want. Set only `MAX_HEAP_SIZE`: 5.0 uses the G1 garbage collector, and it ignores `HEAP_NEWSIZE` (with a warning in the log). See [Java & JVM flavors](../04_infrastructure_and_cloud/01_java_and_jvm_flavors.md).

Startup takes about a minute. Wait until CQL answers:

<!-- test: wait -->
```bash
until docker exec cass-quickstart cqlsh -e 'DESCRIBE KEYSPACES' >/dev/null 2>&1; do sleep 5; done
docker exec cass-quickstart nodetool status
```

You should see one line starting with `UN` (Up, Normal) in a datacenter called `datacenter1`. That name comes from `SimpleSnitch`, the snitch in the shipped `cassandra.yaml`. Real clusters name their datacenters with a different snitch; see the [deployment runbook](../05_cluster_deployment_and_config/02_cluster_deployment_runbook.md#1-pre-flight-planning). You'll need the datacenter name in the next step and in your application.

---

## 3. Create a keyspace and a table

Open the CQL shell:

```bash
docker exec -it cass-quickstart cqlsh
```

Paste the following into cqlsh. It stores temperature readings per sensor per day:

<!-- test: schema -->
```sql
CREATE KEYSPACE quickstart
  WITH replication = {'class': 'NetworkTopologyStrategy', 'datacenter1': 1};

USE quickstart;

CREATE TABLE readings_by_sensor_day (
    sensor_id  text,
    day        date,
    reading_at timestamp,
    value      double,
    PRIMARY KEY ((sensor_id, day), reading_at)
) WITH CLUSTERING ORDER BY (reading_at DESC);

INSERT INTO readings_by_sensor_day (sensor_id, day, reading_at, value)
  VALUES ('s-1', '2026-11-22', '2026-11-22 09:00:00+0000', 19.5);
INSERT INTO readings_by_sensor_day (sensor_id, day, reading_at, value)
  VALUES ('s-1', '2026-11-22', '2026-11-22 10:00:00+0000', 21.0);
INSERT INTO readings_by_sensor_day (sensor_id, day, reading_at, value)
  VALUES ('s-1', '2026-11-22', '2026-11-22 11:00:00+0000', 26.5);
INSERT INTO readings_by_sensor_day (sensor_id, day, reading_at, value)
  VALUES ('s-2', '2026-11-22', '2026-11-22 10:00:00+0000', 18.0);
```

What this shows:
* **`NetworkTopologyStrategy` with a datacenter name**, even on one node. Use it from day one; `SimpleStrategy` makes adding a second datacenter harder later. A real cluster uses a replication factor of 3 per datacenter.
* **The primary key is designed for one query**: "readings for one sensor on one day, newest first". `(sensor_id, day)` is the *partition key*: it decides which nodes store the rows. Adding `day` keeps each partition from growing forever (time bucketing). `reading_at` is the *clustering column*: it sorts rows inside the partition. See [schema design patterns](../02_data_modeling_and_indexing/01_schema_design_patterns.md).
* **`INSERT` is an upsert.** Running the same insert twice leaves one row, not two.

---

## 4. Query by partition key, and see what Cassandra refuses

The query the table was designed for:

<!-- test: query -->
```sql
SELECT reading_at, value FROM quickstart.readings_by_sensor_day
  WHERE sensor_id = 's-1' AND day = '2026-11-22';

SELECT reading_at, value FROM quickstart.readings_by_sensor_day
  WHERE sensor_id = 's-1' AND day = '2026-11-22' LIMIT 1;
```

The first query returns three rows, newest first. The second returns only the latest reading, `26.5`. Both read a single partition, which is the fastest read Cassandra can do.

Now ask a question the table was **not** designed for:

<!-- test: refused -->
```sql
SELECT * FROM quickstart.readings_by_sensor_day WHERE value > 25;
```

Cassandra refuses it:

```text
InvalidRequest: Error from server: code=2200 [Invalid query] message="Cannot execute this query as it might involve data filtering and thus may have unpredictable performance. If you want to execute this query despite the performance unpredictability, use ALLOW FILTERING"
```

This is the most important lesson about Cassandra. Without a partition key, the query would have to scan every partition on every node. Adding `ALLOW FILTERING` makes it run, but it gets slower as the table grows, and it can time out on a real cluster. See [anti-patterns](../01_architecture_and_mental_model/02_anti_patterns.md).

---

## 5. Add an index for the other question

If you really need to search by `value`, Cassandra 5.0's **Storage-Attached Index (SAI)** is the right tool:

<!-- test: sai -->
```sql
CREATE INDEX readings_value_idx ON quickstart.readings_by_sensor_day (value) USING 'sai';
```

The index builds in the background, so `CREATE INDEX` returns before it's ready. A query sent too early fails with `INDEX_NOT_AVAILABLE`. Check that it's ready:

<!-- test: sai-status -->
```sql
SELECT index_name, is_queryable, is_building
  FROM system_views.sai_column_indexes WHERE keyspace_name = 'quickstart';
```

When `is_queryable` is `True` (a second or two for a table this small; repeat the query if not), run the question again:

<!-- test: sai-query -->
```sql
SELECT sensor_id, reading_at, value FROM quickstart.readings_by_sensor_day WHERE value > 25;
```

It now returns the `26.5` reading without `ALLOW FILTERING`. An SAI query without a partition key still asks every node, so it is fine for occasional lookups, but the table design from step 3 should serve your hot path. Restricting the partition key as well (`WHERE sensor_id = 's-1' AND day = '2026-11-22' AND value > 25`) keeps the query on one partition. See [indexing & vector search](../02_data_modeling_and_indexing/02_indexing_and_vector_search.md).

Type `exit` to leave cqlsh.

---

## 6. Connect from an application

This example uses the Python driver. The [client drivers](../03_application_development/03_client_drivers.md) page shows the same settings for Java, Go and Node.js. Install the driver:

```bash
python3 -m pip install cassandra-driver
```

Save this as `quickstart.py`:

<!-- test: python -->
```python
from datetime import date, datetime, timezone

from cassandra import ConsistencyLevel
from cassandra.cluster import EXEC_PROFILE_DEFAULT, Cluster, ExecutionProfile
from cassandra.policies import DCAwareRoundRobinPolicy, TokenAwarePolicy

# Set the local datacenter and the consistency level explicitly. The defaults
# (guess the datacenter, LOCAL_ONE) are not what you want in production.
profile = ExecutionProfile(
    load_balancing_policy=TokenAwarePolicy(DCAwareRoundRobinPolicy(local_dc="datacenter1")),
    consistency_level=ConsistencyLevel.LOCAL_QUORUM,
)

# Create one Cluster and one Session per application, and reuse them.
cluster = Cluster(["127.0.0.1"], execution_profiles={EXEC_PROFILE_DEFAULT: profile})
session = cluster.connect("quickstart")

# Prepare each statement once; execute it many times.
insert = session.prepare(
    "INSERT INTO readings_by_sensor_day (sensor_id, day, reading_at, value) VALUES (?, ?, ?, ?)"
)
latest = session.prepare(
    "SELECT reading_at, value FROM readings_by_sensor_day WHERE sensor_id = ? AND day = ? LIMIT 1"
)

session.execute(insert, ("s-3", date(2026, 11, 22), datetime(2026, 11, 22, 12, 0, tzinfo=timezone.utc), 23.25))
row = session.execute(latest, ("s-3", date(2026, 11, 22))).one()
print(f"latest reading for s-3: {row.value}")

cluster.shutdown()
```

Run it:

```bash
python3 quickstart.py
```

It prints `latest reading for s-3: 23.25`. The script shows the three driver habits that matter most: one long-lived session, prepared statements, and an explicit local datacenter and consistency level.

---

## 7. Clean up

<!-- test: cleanup -->
```bash
docker rm -f cass-quickstart
```

This deletes the container and its data.

---

## 8. Where to go next

| You want to… | Read |
| :--- | :--- |
| Understand why Cassandra behaves like this | [The developer mental model](../01_architecture_and_mental_model/01_mental_model.md), then [anti-patterns](../01_architecture_and_mental_model/02_anti_patterns.md) |
| Design a real data model, step by step | [Tutorial: model a chat app](02_tutorial_data_modeling.md) |
| Practice running a cluster: a node failure, repair, a restore | [Tutorial: three-node cluster drill](03_tutorial_operations.md) |
| Learn what CQL queries can and can't do | [Querying with CQL](../03_application_development/05_querying_with_cql.md), clause by clause with real output, then the [functions](../09_reference/05_cql_functions.md) and [cqlsh](../09_reference/06_cqlsh.md) references |
| Design tables for your own queries | [Schema design patterns](../02_data_modeling_and_indexing/01_schema_design_patterns.md) |
| Write a production application | [Client drivers](../03_application_development/03_client_drivers.md), [performant writes](../03_application_development/01_performant_writes.md), [consistency](../03_application_development/04_consistency_and_transactions.md) |
| Run a 3-node cluster on your laptop | [`test_env/`](../test_env/README.md) (`scripts/up.sh` starts one in about 5 minutes) |
| Run Cassandra on Kubernetes | [Cassandra on Kubernetes](../04_infrastructure_and_cloud/05_kubernetes.md) |
| Deploy a real cluster | [Configuration](../05_cluster_deployment_and_config/01_configuration_and_tuning.md), [deployment runbook](../05_cluster_deployment_and_config/02_cluster_deployment_runbook.md), [security hardening](../05_cluster_deployment_and_config/03_security_hardening.md) |
