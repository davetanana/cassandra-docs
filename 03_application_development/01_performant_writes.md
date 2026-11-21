# Performant Writes: Maximizing Throughput & Minimizing Overhead

Writing data to Apache Cassandra is inherently fast because writes are appended to an in-memory memtable (`SkipListMemtable` by default in 5.0; `TrieMemtable` is opt-in, and is the default in `cassandra_latest.yaml`) and to the sequential on-disk `CommitLog`. However, application developers frequently cripple their write performance by making poor client choices.

Here is how to get the most write throughput out of your cluster. Actual numbers depend on hardware, replication factor (RF), consistency level (CL), and row size.

---

## 1. Rule #1: Use Asynchronous Pipelining (Never Block on Writes)

Executing writes synchronously one-by-one is the most common reason application ingest pipelines run slowly.

```java
// ❌ ANTI-PATTERN: Synchronous blocking write (throughput limited by one round-trip per write)
for (UserEvent event : events) {
    session.execute(insertStmt.bind(event.getId(), event.getData())); // Blocks on network!
}
```

Every `session.execute()` forces your thread to wait for the network round-trip to the Cassandra coordinator.

### The Performant Pattern: Asynchronous Ingest with Backpressure
Use `executeAsync()` and throttle in-flight requests using a `Semaphore` so you don't exhaust client memory:

```java
// ✅ PERFORMANT: Async pipelined writes (typically an order of magnitude more throughput than synchronous writes)
int MAX_IN_FLIGHT = 1024;
Semaphore semaphore = new Semaphore(MAX_IN_FLIGHT);

for (UserEvent event : events) {
    semaphore.acquire(); // Throttle in-flight requests

    BoundStatement bound = insertStmt.bind(event.getId(), event.getData());
    CompletionStage<AsyncResultSet> future = session.executeAsync(bound);

    future.whenComplete((result, error) -> {
        semaphore.release(); // Free up slot for next write
        if (error != null) {
            logger.error("Failed to write event", error);
        }
    });
}
```

---

## 2. Rule #2: Avoid Multi-Partition `BATCH` Statements

A common mistake is bundling 100 random writes into a `BEGIN BATCH ... APPLY BATCH` block, assuming it functions like a SQL batch insert.

### Why Multi-Partition Batches Hurt Performance:
1. When a **logged** batch (the default) contains different partition keys, the coordinator must first store a copy in the `system.batches` batchlog on other nodes (to guarantee that all mutations are eventually applied), send the writes to the replicas of every partition, wait for them, and then delete the batchlog entry.
2. The coordinator holds the whole batch in memory and does all the fan-out work, so it becomes a CPU and memory bottleneck.
3. `UNLOGGED` batches skip the batchlog but still concentrate the fan-out on one coordinator, and Cassandra logs a warning when one spans more partitions than `unlogged_batch_across_partitions_warn_threshold` (default 10).

**The one legitimate multi-partition use:** a small **logged** batch that keeps a few denormalized tables in sync (for example `users_by_id` and `users_by_email`). You pay the batchlog cost to get "all or eventually all" atomicity (not isolation). See [01_schema_design_patterns.md](../02_data_modeling_and_indexing/01_schema_design_patterns.md).

```sql
-- ❌ ANTI-PATTERN: Multi-partition logged batch (forces a batchlog write on the coordinator)
BEGIN BATCH
    INSERT INTO users (user_id, name) VALUES (?, 'Alice');
    INSERT INTO users (user_id, name) VALUES (?, 'Bob');
    INSERT INTO orders (order_id, user_id) VALUES (?, ?);
APPLY BATCH;
```

### When BATCH Is Good: Single-Partition Batches
If every statement in the batch targets the **same keyspace and the exact same partition key value**, the writes are combined into a single mutation that is applied atomically on each replica **without touching the batchlog**:

```sql
-- ✅ PERFORMANT: Single-partition batch (multiple tables or rows, SAME keyspace and partition key)
BEGIN BATCH
    INSERT INTO user_profiles (user_id, email) VALUES (?, 'alice@example.com');
    INSERT INTO user_events (user_id, event_time, event_type) VALUES (?, toTimestamp(now()), 'LOGIN');
APPLY BATCH;
```

> [!NOTE]
> **Server-side guardrails (defaults in `cassandra.yaml`, Cassandra 5.0)**
> * `batch_size_warn_threshold: 5KiB` – batches larger than this log a warning.
> * `batch_size_fail_threshold: 50KiB` – batches larger than this are rejected.
> * `unlogged_batch_across_partitions_warn_threshold: 10` – unlogged batches touching more partitions log a warning.
> * Maximum TTL is 20 years (630,720,000 seconds); larger values are rejected. **But** with the default `storage_compatibility_mode: CASSANDRA_4`, any write whose expiry would fall after **2038-01-19** is also rejected ("exceeds maximum supported expiration date of 2038-01-19..."). In 2026 that limits TTLs to about 11 years, until the cluster finishes the `storage_compatibility_mode` upgrade to `NONE` (see [Upgrading to 5.0](../05_cluster_deployment_and_config/04_upgrading_to_5_0.md)).
> * `tombstone_warn_threshold: 1000` / `tombstone_failure_threshold: 100000` – tombstones scanned per read before warning / aborting the query.
> * `partition_keys_in_select_*` and `in_select_cartesian_product_*` guardrails limit `IN` queries (disabled by default, `-1`).

---

## 3. Rule #3: The `null` Value Trap (Preventing Tombstone Generation)

In Cassandra, writing a `null` to a column does **not** simply skip the column. It writes a **tombstone** (a deletion marker) for that cell.

```java
// ❌ ANTI-PATTERN: Binding null creates a cell tombstone on disk!
PreparedStatement stmt = session.prepare("INSERT INTO users (id, name, email) VALUES (?, ?, ?)");
BoundStatement bound = stmt.bind(userId, "Alice", null); // WRITES A TOMBSTONE FOR EMAIL
session.execute(bound);
```

If your application updates records frequently and passes `null` for fields that haven't changed, you will generate large numbers of tombstones. Reads that scan more than `tombstone_failure_threshold` (default 100,000) tombstones fail with `TombstoneOverwhelmingException`.

### The Solution: Use Unset Parameters
Leave the optional parameter **unset**. Unset values require native protocol v4 or later (Cassandra 5.0 supports v3–v5 and defaults to v5); with Java driver 4.x, any variable you never set is sent as unset automatically:

```java
// ✅ PERFORMANT: Unset parameter ignores the column entirely (no tombstone)
BoundStatement bound = stmt.bind()
    .setUuid("id", userId)
    .setString("name", "Alice");
    // Leave 'email' unset! Do NOT call setString("email", null);

session.execute(bound);

// If a value was already set (e.g. a reused builder), clear it explicitly:
BoundStatement withoutEmail = bound.unset("email");
```

---

## 4. Rule #4: Understand Upsert Semantics

In Cassandra, `INSERT` and `UPDATE` are both **upserts** that write without reading first:
* Both write new cells carrying a write timestamp in microseconds. The Java driver 4.x generates this timestamp on the client by default; otherwise the coordinator assigns one.
* If a cell with the same primary key already exists, the newer timestamp wins (Last-Write-Wins).
* If a cell does not exist, it is created.

There is one important difference: `INSERT` also writes a **row marker** (primary-key liveness info). A row created by `INSERT` continues to exist even if all its non-key columns are later deleted or expire. A row created only by `UPDATE` has no row marker, so it disappears once all its non-key columns are null.

```sql
-- Both are upserts, but only the INSERT writes a row marker:
INSERT INTO user_settings (user_id, theme) VALUES (123, 'dark');
UPDATE user_settings SET theme = 'dark' WHERE user_id = 123;
```

> [!NOTE]
> Unlike relational databases, an `UPDATE` in Cassandra does **not** read the previous row before writing. The exceptions are Lightweight Transactions (`IF EXISTS`, `IF <condition>`) and some list operations (setting or deleting an element by index, removing elements by value), which require a read-before-write. Secondary indexes and materialized views also add work to each write.

---

## 5. Rule #5: Write TTLs Wisely

If your data naturally expires (e.g., session tokens, telemetry data, ephemeral cache):

```sql
-- ✅ RECOMMENDED: Set a default TTL at the table level
CREATE TABLE user_sessions (
    session_id uuid PRIMARY KEY,
    user_id uuid,
    login_time timestamp
) WITH default_time_to_live = 86400; -- 24 hours
```

### Table-Level vs. Query-Level TTLs:
* `default_time_to_live` is simply the TTL applied to writes that do not specify `USING TTL`. On disk, cells are stored the same way either way: each cell carries its own TTL and expiration time.
* The benefit of a table-level TTL is consistency: every write expires, and no code path can forget to set it.
* Efficient cleanup comes from the compaction strategy, not from where the TTL is set. For time-series data with a uniform TTL, use `TimeWindowCompactionStrategy`, which can drop whole SSTables once all their data has expired. Avoid mixing TTL and non-TTL data in the same table.
* The maximum TTL is 20 years; larger values are rejected. Under the default `storage_compatibility_mode: CASSANDRA_4`, expirations after 2038-01-19 are also rejected, so very long TTLs fail until you move to `storage_compatibility_mode: NONE`. (Verified on 5.0.9 by test_env scenario 03.)

---

## 6. Summary Checklist for High-Speed Writes

- [ ] Use `session.executeAsync()` pipelined with a `Semaphore` (e.g. 1,024 in-flight requests).
- [ ] Send unbatched individual mutations for independent partitions.
- [ ] Use single-partition batches for atomic multi-row updates to the same partition key, and small logged batches only to keep denormalized tables in sync.
- [ ] Mark retry-safe statements idempotent; never retry counter increments or list appends blindly.
- [ ] Never bind `null` to prepared statement parameters; leave them unset or call `.unset()`.
- [ ] Prefer table-level `default_time_to_live` for consistency, and pair TTL data with TWCS.
- [ ] Prepare all statements once at application bootstrap.
