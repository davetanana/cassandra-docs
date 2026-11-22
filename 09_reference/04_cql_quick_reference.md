# CQL Quick Reference (Cassandra 5.0, CQL 3.4.7)

> [!CAUTION]
> Commands on this page can change or delete data and affect running clusters. Try them on a test or staging cluster first, and read the [disclaimer](../README.md#disclaimer). The guide is provided "as is", without warranty.

A practical cheat sheet of the CQL syntax that Cassandra 5.0 accepts. Every statement form below was checked against the 5.0 grammar ([`src/antlr/Parser.g`](https://github.com/apache/cassandra/blob/cassandra-5.0/src/antlr/Parser.g)). Defaults come from the schema code. For the full specification, see the official CQL reference linked in [Sources](#sources). Modeling advice lives in [Schema Design Patterns](../02_data_modeling_and_indexing/01_schema_design_patterns.md) and [Indexing & Vector Search](../02_data_modeling_and_indexing/02_indexing_and_vector_search.md).

For worked examples with their output and the exact errors for refused queries, see [Querying with CQL](../03_application_development/05_querying_with_cql.md). Every function, with arguments, return type and an example, is in the [CQL functions reference](05_cql_functions.md). The shell itself is covered in the [cqlsh reference](06_cqlsh.md).

Conventions: `[optional]`, `a | b` = choose one, `...` = repeatable.

---

## 1. Keyspaces

```sql
CREATE KEYSPACE [IF NOT EXISTS] shop
  WITH replication = {'class': 'NetworkTopologyStrategy', 'us-east-1': 3, 'us-west-2': 3}
  AND durable_writes = true;

ALTER KEYSPACE [IF EXISTS] shop
  WITH replication = {'class': 'NetworkTopologyStrategy', 'us-east-1': 3};

DROP KEYSPACE [IF EXISTS] shop;
USE shop;
```
* Use `NetworkTopologyStrategy` in production, with DC names that match your snitch exactly. `SimpleStrategy` ignores racks and DCs.
* After changing replication, run a full repair (or `nodetool rebuild` for a brand-new DC). See the [deployment runbook](../05_cluster_deployment_and_config/02_cluster_deployment_runbook.md).

---

## 2. Tables

```sql
CREATE TABLE [IF NOT EXISTS] shop.orders_by_customer (
    customer_id uuid,
    order_month text,
    order_time  timestamp,
    order_id    uuid,
    status      text,
    total       decimal,
    customer_name text STATIC,                      -- one value per partition
    email       text MASKED WITH DEFAULT,           -- dynamic data masking (section 9)
    PRIMARY KEY ((customer_id, order_month), order_time, order_id)
) WITH CLUSTERING ORDER BY (order_time DESC, order_id ASC)
  AND default_time_to_live = 0
  AND comment = 'Orders per customer per month';
```

### ALTER TABLE (all forms accept `IF EXISTS` / `IF NOT EXISTS`, CQL 3.4.6+)
```sql
ALTER TABLE [IF EXISTS] t ADD [IF NOT EXISTS] col text;
ALTER TABLE t ADD (c1 int, c2 set<text> , c3 text MASKED WITH mask_inner(1, 1));
ALTER TABLE t DROP [IF EXISTS] col;                 -- or DROP (c1, c2) [USING TIMESTAMP <micros>]
ALTER TABLE t RENAME [IF EXISTS] pk_col TO new_name;   -- primary-key columns only
ALTER TABLE t ALTER [IF EXISTS] email MASKED WITH mask_hash();
ALTER TABLE t ALTER email DROP MASKED;
ALTER TABLE t WITH gc_grace_seconds = 3600 AND compaction = {'class': 'UnifiedCompactionStrategy'};

DROP TABLE [IF EXISTS] t;
TRUNCATE [TABLE] t;          -- needs all nodes up; takes an automatic snapshot if auto_snapshot is true
```
You cannot change a column's type (`ALTER ... TYPE` is rejected since 3.4.4), add or drop primary-key columns, or change the clustering order. To do any of those, create a new table and migrate.

### Table Options and Their Defaults

| Option | Default | Notes |
| :--- | :--- | :--- |
| `compaction` | `{'class': 'SizeTieredCompactionStrategy', 'min_threshold': 4, 'max_threshold': 32}` (or whatever `default_compaction` sets in yaml; `cassandra_latest.yaml` uses UCS) | See [Compaction Strategies](../06_operations_and_housekeeping/04_compaction_strategies.md) |
| `compression` | `{'class': 'LZ4Compressor', 'chunk_length_in_kb': 16}` | `{'enabled': false}` disables it |
| `gc_grace_seconds` | `864000` (10 days) | Repair must finish within this window |
| `default_time_to_live` | `0` (no TTL) | Seconds; max 20 years (630,720,000). Under `storage_compatibility_mode: CASSANDRA_4` the resulting expiry must also be before 2038-01-19 |
| `bloom_filter_fp_chance` | `0.01` (`0.1` with LCS) | |
| `caching` | `{'keys': 'ALL', 'rows_per_partition': 'NONE'}` | The row cache also needs `row_cache_size` > 0 in yaml |
| `speculative_retry` / `additional_write_policy` | `99p` / `99p` | `NONE`, `ALWAYS`, `Nms`, `Np`, `MIN(...)`, `MAX(...)` |
| `read_repair` | `BLOCKING` | `NONE` keeps writes atomic per partition across replicas, at the cost of monotonic quorum reads |
| `crc_check_chance` | `1.0` | |
| `memtable` | `default` | Names a `memtable.configurations` entry in yaml |
| `memtable_flush_period_in_ms` | `0` | |
| `min_index_interval` / `max_index_interval` | `128` / `2048` | Only used by the BIG format |
| `cdc` | `false` | Also needs `cdc_enabled: true` in yaml |
| `allow_auto_snapshot` | `true` | Per-table opt-out of snapshots on DROP/TRUNCATE |
| `incremental_backups` | `true` | Only matters when `incremental_backups: true` in yaml |
| `auto_repair` | per-type map | Per-table opt-out for the 5.0.8+ auto-repair scheduler |
| `comment`, `extensions` | `''`, `{}` | |

---

## 3. Data Types

| Category | Types |
| :--- | :--- |
| Numeric | `tinyint`, `smallint`, `int`, `bigint`, `varint`, `float`, `double`, `decimal`, `counter` |
| Text and binary | `text` (= `varchar`), `ascii`, `blob` |
| Time | `timestamp` (ms), `date`, `time` (ns), `duration` (e.g. `1h30m`, `P1DT2H`) |
| Identity | `uuid`, `timeuuid` |
| Other | `boolean`, `inet` |
| Collections | `list<T>`, `set<T>`, `map<K,V>`; `frozen<...>` to store the value as a single blob |
| Tuples and UDTs | `tuple<int, text>`; user-defined types (below) |
| **Vector (new in 5.0)** | `vector<float, 768>`, which is fixed-dimension. Any element type is allowed, but SAI vector indexes require `float`. |

Sizes and ranges of the scalar types:

| Type | Size and range | Notes |
| :--- | :--- | :--- |
| `tinyint`, `smallint`, `int`, `bigint` | Signed integers of 8, 16, 32 and 64 bits | Out-of-range literals are rejected, for example `Unable to make byte from '128'` for a `tinyint` |
| `varint` | Integer of any size | |
| `float`, `double` | 32-bit and 64-bit IEEE 754 | Inexact. Don't use them for money. |
| `decimal` | Decimal of any precision | Exact. Use it for money. |
| `counter` | Signed 64-bit | Only `+` and `-` updates, in tables where every non-key column is a counter |
| `text` (`varchar`), `ascii` | UTF-8 and US-ASCII strings | Size is limited in practice by mutation and partition size, not by the type |
| `blob` | Bytes | Literal `0xCAFE` |
| `timestamp` | Milliseconds since 1970-01-01 UTC, 64 bits | A string without a zone is read in the coordinator's time zone. `cqlsh` prints it in UTC. |
| `date` | Days, 32 bits | No time part |
| `time` | Nanoseconds since midnight, 64 bits | No date part |
| `duration` | Months, days and nanoseconds | Not allowed in a primary key: `duration type is not supported for PRIMARY KEY column` |
| `uuid`, `timeuuid` | 128 bits | `timeuuid` is version 1 (time-based) and sorts by its time |
| `boolean`, `inet` | `true`/`false`; an IPv4 or IPv6 address | |

```sql
CREATE TYPE [IF NOT EXISTS] shop.address (street text, city text, zip text);
ALTER TYPE [IF EXISTS] shop.address ADD [IF NOT EXISTS] country text;
ALTER TYPE shop.address RENAME [IF EXISTS] zip TO postcode;
DROP TYPE [IF EXISTS] shop.address;
```

**Literals**:
* `'text'`, `$$text with 'quotes'$$`
* `123`, `1.5`, `1e10`, `NaN`, `Infinity`
* `0xCAFE` (blob), `true`
* `123e4567-e89b-12d3-a456-426614174000` (uuid)
* `'2026-11-21 10:00:00+0000'`, `'2026-11-21'`
* `1h30m`
* `[1, 2]` (list or vector), `{1, 2}` (set), `{'k': 'v'}` (map), `(1, 'a')` (tuple), `{street: '1 Main', city: 'X'}` (UDT)

---

## 4. Writes: INSERT, UPDATE, DELETE, BATCH

```sql
-- INSERT: IF NOT EXISTS goes before USING
INSERT INTO t (k, c, v) VALUES (?, ?, ?) [IF NOT EXISTS] [USING TTL 86400 [AND TIMESTAMP 1700000000000000]];
INSERT INTO t JSON '{"k": 1, "v": "x"}' [DEFAULT NULL | DEFAULT UNSET];   -- omitted columns: tombstone vs untouched

-- UPDATE: USING goes before SET
UPDATE t [USING TTL 3600 [AND TIMESTAMP ...]]
   SET v = 'x',
       counter_col = counter_col + 1,        -- counters: only +/- (counter tables only)
       tags = tags + {'new'},                -- set add  (also: tags += {'new'})
       tags = tags - {'old'},                -- set remove
       events = events + ['e3'],             -- list append    (no read-before-write)
       events = ['e0'] + events,             -- list prepend
       events[2] = 'x',                      -- list set-by-index (read-before-write!)
       attrs['color'] = 'red',               -- map put
       addr.city = 'Paris'                   -- UDT field (non-frozen UDT)
 WHERE k = ? AND c = ?
 [IF EXISTS | IF v = 'old' AND n > 3 AND tags CONTAINS 'a' AND attrs['k'] IN ('x','y') AND n != 0];

-- DELETE: only USING TIMESTAMP is allowed
DELETE [v, attrs['color'], events[0], addr.city] FROM t [USING TIMESTAMP ...]
 WHERE k = ? [AND c = ? | AND c > ? AND c < ?]          -- row or range deletion
 [IF EXISTS | IF <conditions>];

-- BATCH: LOGGED by default; UNLOGGED or COUNTER on request
BEGIN [UNLOGGED | COUNTER] BATCH [USING TIMESTAMP ...]
  INSERT ...; UPDATE ...; DELETE ...;
APPLY BATCH;
```
* `TTL 0` or `TTL null` means no expiry. TTLs above 20 years are rejected. With `storage_compatibility_mode: CASSANDRA_4`, expiry is also capped at 2038-01-19.
* Binding `null` writes a tombstone; leave the parameter **unset** instead ([Performant Writes](../03_application_development/01_performant_writes.md)).
* Conditional (`IF`) statements are Paxos LWTs. In a batch, every conditional statement must target the same partition.
* `!=` is accepted only in `IF` conditions, not in `WHERE`.

---

## 5. Reads: SELECT

```sql
SELECT [JSON] [DISTINCT] <selectors | *>
  FROM t
 [WHERE <relations>]
 [GROUP BY <pk/clustering prefix>[, floor(ts_col, 1h)]]
 [ORDER BY <clustering col> [ASC|DESC] | ORDER BY <vector col> ANN OF <vector>]
 [PER PARTITION LIMIT n]
 [LIMIT n]
 [ALLOW FILTERING];
```

### Selectors
* Columns with aliases: `col AS alias`.
* Arithmetic: `a + b`, `-x`, `%`. Casts: `CAST(x AS text)`.
* `WRITETIME(col)`, `MAXWRITETIME(col)` (new in 5.0; the largest timestamp in a collection or UDT), `TTL(col)`.
* Collection element and slice: `m['k']`, `s[1..5]`, `l[..3]`. UDT field: `addr.city`.
* Functions and aggregates (section 6).

### WHERE Relations
| Form | Example |
| :--- | :--- |
| Equality / range | `k = ?`, `c > ? AND c <= ?` |
| `IN` | `k IN (?, ?)`, `c IN ?` |
| Multi-column (clustering tuple) | `(c1, c2) > (1, 'a')`, `(c1, c2) IN ((1,'a'), (2,'b'))` |
| Token | `token(k) > ? AND token(k) <= ?` |
| Collections (index or filtering) | `tags CONTAINS 'x'`, `attrs CONTAINS KEY 'color'`, `attrs['color'] = 'red'` |
| `LIKE` | **SASI indexes only** (SAI in 5.0 does not support `LIKE`) |
| `IS NOT NULL` | Only in `CREATE MATERIALIZED VIEW` |
| Custom index expression | `expr(index_name, '...')` |

Restriction rules in brief:
* Without an index, the full partition key must be given (by `=` or `IN`) before restricting clustering columns, and clustering columns are restricted in order. Only the last restricted one may use a range.
* Anything else needs a secondary index or `ALLOW FILTERING`. The `allow_filtering_enabled` guardrail can forbid the latter.
* `GROUP BY` takes a prefix of the primary key. Only the last element may be wrapped in a time function such as `floor(ts, 1h)`. Grouped queries are always paged internally.
* `ANN OF` requires `LIMIT` ≤ 1000 and is the only allowed ordering. See [Vector Search](../02_data_modeling_and_indexing/02_indexing_and_vector_search.md#4-querying-vectors-with-ann-of).

---

## 6. Built-In Functions

One entry per function, with arguments, return type and a tested example: [CQL functions reference](05_cql_functions.md).

| Group | Functions (5.0 snake_case names; legacy names still work but are deprecated) |
| :--- | :--- |
| Aggregates | `count(*)`, `count(col)`, `min`, `max`, `sum`, `avg` |
| Time & UUID | `now()`, `uuid()`, `current_timestamp()`, `current_date()`, `current_time()`, `current_timeuuid()`, `to_date(x)`, `to_timestamp(x)`, `to_unix_timestamp(x)`, `min_timeuuid(ts)`, `max_timeuuid(ts)`, `floor(ts, duration[, start])` |
| Conversion | `cast(x AS type)`, `<type>_as_blob(x)`, `blob_as_<type>(b)`, `to_json(x)`, `from_json(s)`, `token(pk...)` |
| **Math (new in 5.0)** | `abs(x)`, `exp(x)`, `log(x)`, `log10(x)`, `round(x)` |
| **Collections (new in 5.0)** | `map_keys(m)`, `map_values(m)`, `collection_count(c)`, `collection_min(c)`, `collection_max(c)`, `collection_sum(c)`, `collection_avg(c)` |
| **Vector similarity (new in 5.0)** | `similarity_cosine(v1, v2)`, `similarity_dot_product(v1, v2)`, `similarity_euclidean(v1, v2)`: higher = more similar |
| **Masking (new in 5.0)** | `mask_null(x)`, `mask_default(x)`, `mask_replace(x, replacement)`, `mask_inner(x, begin, end[, padding])`, `mask_outer(x, begin, end[, padding])`, `mask_hash(x[, algorithm])` (SHA-256 by default) |
| Date arithmetic | `ts + 1d`, `date - 2w`, `current_date() - 30d` |

Removed in 5.0: `dateOf` and `unixTimestampOf`; use `to_timestamp` and `to_unix_timestamp`.

### User-Defined Functions and Aggregates
```sql
CREATE [OR REPLACE] FUNCTION [IF NOT EXISTS] shop.fahrenheit(c double)
  RETURNS NULL ON NULL INPUT          -- or: CALLED ON NULL INPUT
  RETURNS double
  LANGUAGE java
  AS 'return c * 9.0 / 5.0 + 32;';

CREATE [OR REPLACE] AGGREGATE [IF NOT EXISTS] shop.my_avg(double)
  SFUNC state_fn STYPE tuple<int, double> [FINALFUNC final_fn] [INITCOND (0, 0.0)];

DROP FUNCTION [IF EXISTS] shop.fahrenheit[(double)];
DROP AGGREGATE [IF EXISTS] shop.my_avg[(double)];
```
UDFs are disabled unless `user_defined_functions_enabled: true` is set in yaml. Only Java is supported in 5.0; scripted UDFs were removed in 4.0.

---

## 7. Indexes and Materialized Views

```sql
-- Storage-Attached Index (recommended). 'sai' is the short name for 'StorageAttachedIndex'.
CREATE INDEX [IF NOT EXISTS] [name] ON t (col) USING 'sai' [WITH OPTIONS = {'case_sensitive': 'false', 'normalize': 'true', 'ascii': 'true'}];
CREATE INDEX ON t (values(set_or_list_col)) USING 'sai';   -- CONTAINS
CREATE INDEX ON t (keys(map_col))           USING 'sai';   -- CONTAINS KEY
CREATE INDEX ON t (entries(map_col))        USING 'sai';   -- map_col['k'] = v
CREATE INDEX ON t (full(frozen_col))        USING 'sai';   -- whole-value equality
CREATE INDEX ON t (embedding) USING 'sai' WITH OPTIONS = {'similarity_function': 'COSINE'};  -- vector

CREATE CUSTOM INDEX [IF NOT EXISTS] [name] ON t (col) USING 'org.apache.cassandra.index.sasi.SASIIndex';  -- SASI (experimental)
DROP INDEX [IF EXISTS] ks.index_name;
```
A plain `CREATE INDEX` **without** `USING` builds a legacy 2i under the shipped `cassandra.yaml` (`default_secondary_index: legacy_local_table`).

```sql
-- Materialized views: experimental, disabled unless materialized_views_enabled: true
CREATE MATERIALIZED VIEW [IF NOT EXISTS] ks.orders_by_status AS
  SELECT * FROM ks.orders
  WHERE status IS NOT NULL AND order_id IS NOT NULL
  PRIMARY KEY (status, order_id)
  [WITH CLUSTERING ORDER BY (order_id DESC)];
ALTER MATERIALIZED VIEW [IF EXISTS] ks.orders_by_status WITH comment = '...';
DROP MATERIALIZED VIEW [IF EXISTS] ks.orders_by_status;

CREATE TRIGGER [IF NOT EXISTS] trg ON ks.t USING 'com.example.MyTrigger';   -- the jar goes in conf/triggers
DROP TRIGGER [IF EXISTS] trg ON ks.t;
```

---

## 8. Roles, Users and Permissions

```sql
CREATE ROLE [IF NOT EXISTS] app_rw WITH PASSWORD = '...' AND LOGIN = true
   [AND SUPERUSER = false]
   [AND ACCESS TO DATACENTERS {'us-east-1'} | AND ACCESS TO ALL DATACENTERS]
   [AND ACCESS FROM CIDRS {'office'} | AND ACCESS FROM ALL CIDRS]
   [AND OPTIONS = {...}];
CREATE ROLE ops WITH HASHED PASSWORD = '$2a$10$...' AND LOGIN = true;   -- hash from tools/bin/hash_password
ALTER ROLE [IF EXISTS] app_rw WITH PASSWORD = '...';
DROP ROLE [IF EXISTS] app_rw;
GRANT ops TO alice;   REVOKE ops FROM alice;
LIST ROLES [OF alice] [NORECURSIVE];

GRANT SELECT, MODIFY ON KEYSPACE shop TO app_rw;          -- several permissions at once (3.4.6+)
GRANT SELECT ON ALL TABLES IN KEYSPACE shop TO reporting; -- 3.4.6+
GRANT UNMASK ON TABLE shop.users TO support;              -- see cleartext of masked columns (5.0)
GRANT SELECT_MASKED ON TABLE shop.users TO support;       -- filter on masked columns (5.0)
GRANT EXECUTE ON FUNCTION shop.fahrenheit(double) TO app_rw;
GRANT DESCRIBE ON ALL MBEANS TO monitoring;
REVOKE MODIFY ON KEYSPACE shop FROM app_rw;
LIST ALL PERMISSIONS [ON KEYSPACE shop] [OF app_rw] [NORECURSIVE];

ADD IDENTITY [IF NOT EXISTS] 'spiffe://example.org/app' TO ROLE 'app_rw';   -- mTLS authenticators (5.0)
DROP IDENTITY [IF EXISTS] 'spiffe://example.org/app';
```
Permissions: `CREATE`, `ALTER`, `DROP`, `SELECT`, `MODIFY`, `AUTHORIZE`, `DESCRIBE`, `EXECUTE`, `UNMASK`, `SELECT_MASKED`, `ALL [PERMISSIONS]`.

Resources:
* `ALL KEYSPACES`, `KEYSPACE ks`, `[TABLE] ks.t`, `ALL TABLES IN KEYSPACE ks`
* `ALL ROLES`, `ROLE r`
* `ALL FUNCTIONS [IN KEYSPACE ks]`, `FUNCTION ks.f(types)`
* `ALL MBEANS`, `MBEAN 'name'`, `MBEANS 'pattern'`

The legacy `CREATE USER ... WITH PASSWORD '...' [SUPERUSER | NOSUPERUSER]`, `ALTER USER`, `DROP USER` and `LIST USERS` still work. Nothing is enforced until you configure an authenticator and authorizer: see [Security Hardening](../05_cluster_deployment_and_config/03_security_hardening.md).

---

## 9. Dynamic Data Masking (5.0)

```sql
CREATE TABLE ks.users (id uuid PRIMARY KEY,
                       email text MASKED WITH DEFAULT,                 -- '****' for text
                       ssn   text MASKED WITH mask_inner(1, 1, 'X'),   -- keeps first and last char
                       card  text MASKED WITH mask_outer(0, 4));       -- keeps last 4
SELECT mask_hash(email) FROM ks.users;                                  -- also usable as a plain function
```
Requires `dynamic_data_masking_enabled: true`. Superusers and roles with `UNMASK` see cleartext. UDFs can be used as masking functions. See [Consistency & Transactions](../03_application_development/04_consistency_and_transactions.md#5-dynamic-data-masking-ddm-new-in-50) for the permission model.

---

## 10. DESCRIBE

`DESCRIBE` runs on the server (since 4.0), so drivers can use it too. `DESC` is an alias.

```sql
DESCRIBE CLUSTER;
DESCRIBE [FULL] SCHEMA;                  -- FULL includes system keyspaces
DESCRIBE KEYSPACES;   DESCRIBE [ONLY] KEYSPACE [ks];      -- ONLY: without its tables, types...
DESCRIBE TABLES;      DESCRIBE TABLE ks.t;
DESCRIBE INDEX ks.idx;   DESCRIBE MATERIALIZED VIEW ks.v;
DESCRIBE TYPES;       DESCRIBE TYPE ks.address;
DESCRIBE FUNCTIONS;   DESCRIBE FUNCTION ks.f;
DESCRIBE AGGREGATES;  DESCRIBE AGGREGATE ks.a;
DESCRIBE ks.anything [WITH INTERNALS];   -- generic lookup; WITH INTERNALS adds table IDs and dropped columns
```
`DESCRIBE KEYSPACE ks WITH INTERNALS` produces the DDL needed to re-create tables with their original IDs. This is useful when restoring snapshots (see the [DR runbook](../07_disaster_recovery/01_backup_and_disaster_recovery.md)).

---

## Sources

Repository files (branch `cassandra-5.0`):
* Grammar: [src/antlr/Parser.g](https://github.com/apache/cassandra/blob/cassandra-5.0/src/antlr/Parser.g), [src/antlr/Lexer.g](https://github.com/apache/cassandra/blob/cassandra-5.0/src/antlr/Lexer.g)
* Table defaults: [schema/TableParams.java](https://github.com/apache/cassandra/blob/cassandra-5.0/src/java/org/apache/cassandra/schema/TableParams.java), [schema/CompactionParams.java](https://github.com/apache/cassandra/blob/cassandra-5.0/src/java/org/apache/cassandra/schema/CompactionParams.java), [schema/CompressionParams.java](https://github.com/apache/cassandra/blob/cassandra-5.0/src/java/org/apache/cassandra/schema/CompressionParams.java), [schema/CachingParams.java](https://github.com/apache/cassandra/blob/cassandra-5.0/src/java/org/apache/cassandra/schema/CachingParams.java), [cql3/Attributes.java](https://github.com/apache/cassandra/blob/cassandra-5.0/src/java/org/apache/cassandra/cql3/Attributes.java) (MAX_TTL)
* Functions: [cql3/functions/](https://github.com/apache/cassandra/tree/cassandra-5.0/src/java/org/apache/cassandra/cql3/functions) (`MathFcts`, `CollectionFcts`, `VectorFcts`, `TimeFcts`, `UuidFcts`, `AggregateFcts`, `BytesConversionFcts`, `CastFcts`, `masking/`)
* SAI short name: [index/sai/StorageAttachedIndex.java](https://github.com/apache/cassandra/blob/cassandra-5.0/src/java/org/apache/cassandra/index/sai/StorageAttachedIndex.java)
* [doc/modules/cassandra/pages/developing/cql/changes.adoc](https://github.com/apache/cassandra/blob/cassandra-5.0/doc/modules/cassandra/pages/developing/cql/changes.adoc) and [CHANGES.txt](https://github.com/apache/cassandra/blob/cassandra-5.0/CHANGES.txt) (CASSANDRA-17221 math functions, CASSANDRA-18060 collection functions, CASSANDRA-17425 `maxwritetime`, CASSANDRA-18640 vector similarity functions)

Official documentation:
* CQL reference index: https://cassandra.apache.org/doc/5.0/cassandra/developing/cql/index.html
* Data types: https://cassandra.apache.org/doc/5.0/cassandra/developing/cql/types.html
* DDL: https://cassandra.apache.org/doc/5.0/cassandra/developing/cql/ddl.html
* DML: https://cassandra.apache.org/doc/5.0/cassandra/developing/cql/dml.html
* Functions: https://cassandra.apache.org/doc/5.0/cassandra/developing/cql/functions.html
* Security (roles and permissions): https://cassandra.apache.org/doc/5.0/cassandra/developing/cql/security.html
* Dynamic data masking: https://cassandra.apache.org/doc/5.0/cassandra/developing/cql/dynamic-data-masking.html
* SAI: https://cassandra.apache.org/doc/5.0/cassandra/developing/cql/indexing/sai/sai-overview.html
* CQL changes: https://cassandra.apache.org/doc/5.0/cassandra/developing/cql/changes.html
