# Anti-Patterns & Traps: What Kills Cassandra Performance

Many Cassandra production problems (high p99 latency, long GC pauses, timeouts, out-of-memory errors) come from how the application models and queries data rather than from the server itself.

Below are the **top 8 anti-patterns** to avoid. Section 9 lists the 5.0 guardrails operators can use to warn on or reject several of them.

---

## 1. The Queue Anti-Pattern (Cassandra is NOT a Message Broker)

* **The Anti-Pattern**: Using a Cassandra table to manage task queues, job processing, or unread notification states:
  ```sql
  -- ❌ DISASTER: Frequent inserts followed immediately by deletes
  INSERT INTO task_queue (task_id, status) VALUES (uuid, 'PENDING');
  -- Worker picks up task and deletes it:
  DELETE FROM task_queue WHERE task_id = uuid;
  ```
* **Why It Fails**:
  * Deletes in Cassandra do not remove data immediately; they write a **tombstone**.
  * A query reading the queue must scan past every tombstone still on disk. Tombstones can only be purged by compaction after `gc_grace_seconds` (default 10 days) has passed.
  * When a single read scans more than `tombstone_warn_threshold` (default 1,000) tombstones, Cassandra logs a warning.
  * When it scans more than `tombstone_failure_threshold` (default 100,000), the read is aborted with a `TombstoneOverwhelmingException`:
    `Scanned over 100000 tombstones during query '...' (last scanned row token was ... and partion key was (...)); query aborted`
* **The Solution**: Use a real message broker (Apache Kafka, Apache Pulsar, RabbitMQ, SQS) for queues. Use Cassandra for durable records.

---

## 2. The `ALLOW FILTERING` Trap in Production

* **The Anti-Pattern**: Appending `ALLOW FILTERING` to query columns that aren't indexed or part of the primary key:
  ```sql
  -- ❌ DISASTER: Scans every token range in the cluster
  SELECT * FROM users WHERE age > 30 AND status = 'ACTIVE' ALLOW FILTERING;
  ```
* **Why It Fails**:
  * Without a partition key restriction, Cassandra must read every partition on every replica range and discard non-matching rows.
  * It may work in development with 100 rows. In production with 100 million rows, it causes cluster-wide load and timeouts.
  * Operators can reject such queries with the `allow_filtering_enabled: false` guardrail.
* **The Solution**:
  * Create a dedicated table with an appropriate partition key.
  * Or use Cassandra 5.0 **Storage-Attached Indexing (SAI)** for moderate-throughput queries:
    ```sql
    CREATE INDEX users_age_idx ON users (age) USING 'sai';
    -- Served by the SAI index, no ALLOW FILTERING needed
    SELECT * FROM users WHERE age > 30;
    ```
    SAI is node-local, so a query without a partition key still fans out across the cluster. It makes each replica's work cheaper; it does not make the query single-partition. See [02_indexing_and_vector_search.md](../02_data_modeling_and_indexing/02_indexing_and_vector_search.md).

---

## 3. Huge Partitions

**Rule of thumb used throughout these docs: keep partitions under ~100 MB and ~100,000 rows.** This is a guideline, not a hard server limit. Smaller is better for latency, repair and streaming.

* **The Anti-Pattern**: Designing a table where all events for a high-volume entity land in a single partition:
  ```sql
  -- ❌ RISK: Unbounded partition for a busy IoT sensor or user
  CREATE TABLE telemetry (
      device_id text,
      recorded_at timestamp,
      reading double,
      PRIMARY KEY ((device_id), recorded_at)
  );
  ```
* **Why It Fails**:
  * A partition is never split across nodes. It lives entirely on that token's replicas, so a hot or huge partition concentrates load on those few nodes.
  * Large partitions increase heap pressure during reads, compaction, repair and streaming, which shows up as GC pauses and latency spikes.
* **Detecting it**: `nodetool tablestats` ("Compacted partition maximum bytes") and the `partition_size_warn_threshold` guardrail, which logs when flush or compaction writes a partition larger than the threshold (disabled by default).
* **The Solution**: Compound partition keys with **bucketing** (by month, day, or an integer bucket):
  ```sql
  -- ⚡ SAFE: Bounded partitions (1 partition per month per device)
  CREATE TABLE telemetry (
      device_id text,
      year_month text, -- e.g., '2026-11'
      recorded_at timestamp,
      reading double,
      PRIMARY KEY ((device_id, year_month), recorded_at)
  );
  ```

---

## 4. Multi-Partition `BATCH` for High-Speed Ingest

* **The Anti-Pattern**: Grouping independent writes for different partitions into one `BATCH` to "speed up" ingest:
  ```sql
  -- ❌ ANTI-PATTERN: Logged batch across unrelated partitions
  BEGIN BATCH
      INSERT INTO users (id, name) VALUES (uuid1, 'Alice');
      INSERT INTO users (id, name) VALUES (uuid2, 'Bob');
      INSERT INTO users (id, name) VALUES (uuid3, 'Charlie');
  APPLY BATCH;
  ```
* **Why It Fails**:
  * A logged batch is first written to the batchlog on other nodes, then applied to each partition's replicas, then the batchlog entry is removed. That is extra writes and round-trips.
  * One coordinator does all the fan-out, which concentrates CPU and memory on that node and makes the slowest replica set determine latency.
  * Batches larger than `batch_size_fail_threshold` (default 50KiB) are rejected.
* **The Solution**: Send independent writes as individual asynchronous statements (`session.executeAsync()`) with bounded concurrency. Keep multi-partition logged batches for the case they are designed for: keeping a few denormalized tables in sync atomically (see [01_schema_design_patterns.md](../02_data_modeling_and_indexing/01_schema_design_patterns.md)).

---

## 5. Unbounded Collections (`list`, `set`, `map`)

* **The Anti-Pattern**: Appending items to a non-frozen collection indefinitely:
  ```sql
  -- ❌ ANTI-PATTERN: Appending to an unbounded list
  ALTER TABLE user_history ADD log_events list<text>;
  UPDATE user_history SET log_events = log_events + ['Logged in at ...'] WHERE user_id = ?;
  ```
* **Why It Fails**:
  * A collection is read as a whole: selecting the column materializes every element, so the cost of each read grows with the collection.
  * Removing or overwriting elements creates tombstones inside the row.
  * Appending (`+`) is a blind write and does **not** read first. Setting or removing a list element by index (`log_events[3] = ...`, `DELETE log_events[3]`) and removing list elements by value (`log_events - [...]`) **do** require a read-before-write.
  * Operators can cap collections with the `collection_size_*` and `items_per_collection_*` guardrails (disabled by default).
* **The Solution**: Turn the collection items into **rows** in a separate table using clustering keys:
  ```sql
  -- ⚡ SAFE: Rows instead of collection elements
  CREATE TABLE user_log_events (
      user_id uuid,
      event_id timeuuid,
      event_text text,
      PRIMARY KEY ((user_id), event_id)
  ) WITH CLUSTERING ORDER BY (event_id DESC);
  ```
  Bucket this table too if a single user can accumulate more events than the partition-size rule of thumb allows.

---

## 6. Re-Preparing Statements on Every Query

* **The Anti-Pattern**: Preparing the CQL query inside a request handler:
  ```java
  // ❌ Re-prepares on every incoming HTTP request
  public User getUser(UUID id) {
      PreparedStatement stmt = session.prepare("SELECT * FROM users WHERE id = ?");
      return mapper.map(session.execute(stmt.bind(id)));
  }
  ```
* **Why It Fails**:
  * `session.prepare()` costs a round-trip to the server to parse the statement and return its ID. The Java driver 4.x caches prepared statements by query string, but every call still goes through that cache lookup, and drivers without such a cache re-prepare each time.
  * It adds latency to every call and churns the server's prepared statement cache.
* **The Solution**: Prepare all statements **once** at application startup, store the `PreparedStatement` in a field or dependency-injected singleton, and only call `stmt.bind()` at runtime.

---

## 7. Opening and Closing Sessions Per Request

* **The Anti-Pattern**: Creating a new driver session inside a function:
  ```java
  // ❌ CATASTROPHIC: Creating sessions per request
  public void saveRecord(Record r) {
      try (CqlSession session = CqlSession.builder().build()) {
          session.execute(...);
      }
  }
  ```
* **Why It Fails**:
  * Building a `CqlSession` contacts the cluster, downloads topology and schema metadata, opens connection pools to the nodes, and starts event-loop threads. That takes far longer than a query and exhausts sockets and threads under load.
* **The Solution**: Maintain **one** `CqlSession` per application lifecycle and share it across all threads. See [03_client_drivers.md](../03_application_development/03_client_drivers.md).

---

## 8. Using `ALL` Consistency Level

* **The Anti-Pattern**: Setting `ConsistencyLevel.ALL` on writes or reads "just to be completely safe".
* **Why It Fails**:
  * `ALL` requires an acknowledgment from **every replica** of the partition, in every datacenter.
  * If a single replica is down, the request fails with `UnavailableException`. If one is slow (GC pause, compaction, network), it fails with a read or write timeout.
  * It removes Cassandra's tolerance of replica failure.
* **The Solution**: Use `LOCAL_QUORUM` for reads and writes. With replication factor 3 per DC, it gives read-your-writes consistency within the local datacenter while tolerating one replica down. Operators can block `ALL` with the `read_consistency_levels_disallowed` / `write_consistency_levels_disallowed` guardrails. See [04_consistency_and_transactions.md](../03_application_development/04_consistency_and_transactions.md).

---

## 9. Guardrails That Catch These Patterns

All are in `conf/cassandra.yaml`. Most are disabled by default. Settings in the guardrails framework (the `*_enabled`, `*_warn_threshold` / `*_fail_threshold` pairs and the consistency-level lists) apply only to ordinary users: superusers and internal queries bypass them. The older `tombstone_*` and `batch_size_*` thresholds apply to everyone.

| Anti-pattern | Guardrail(s) | Shipped default |
| :--- | :--- | :--- |
| `ALLOW FILTERING` | `allow_filtering_enabled` | `true` (allowed) |
| Tombstone-heavy reads | `tombstone_warn_threshold` / `tombstone_failure_threshold` | 1,000 / 100,000 |
| Large partitions | `partition_size_warn_threshold` / `partition_size_fail_threshold` (checked at flush/compaction; logs only) | disabled |
| Tombstone-heavy partitions | `partition_tombstones_warn_threshold` / `_fail_threshold` (checked at flush/compaction; logs only) | disabled |
| Large batches | `batch_size_warn_threshold` / `batch_size_fail_threshold` | 5KiB / 50KiB |
| Unlogged multi-partition batches | `unlogged_batch_across_partitions_warn_threshold` | 10 |
| Big collections | `collection_size_*`, `items_per_collection_*` | disabled |
| Large `IN` lists | `partition_keys_in_select_*`, `in_select_cartesian_product_*` | disabled |
| `ALL` / other CLs | `read_consistency_levels_disallowed`, `write_consistency_levels_disallowed` | empty |
| Too many tables / indexes | `tables_*`, `secondary_indexes_per_table_*`, `sai_sstable_indexes_per_query_*` | mostly disabled |
