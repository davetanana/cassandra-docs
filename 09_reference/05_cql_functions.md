# CQL Functions Reference (Cassandra 5.0)

Every built-in CQL function in Cassandra 5.0, one entry each, with its syntax, arguments, return type and an example with the output `cqlsh` prints. The function list and the argument and return types come from the 5.0 source ([`cql3/functions/`](https://github.com/apache/cassandra/tree/cassandra-5.0/src/java/org/apache/cassandra/cql3/functions)). The examples are run against Cassandra 5.0 by [`test_env` scenario 14](../test_env/README.md), and their output is compared with what this page shows.

For the statement syntax, see the [CQL quick reference](04_cql_quick_reference.md). For how to use the functions in real queries, see [Querying with CQL](../03_application_development/05_querying_with_cql.md).

---

## 1. How to read this page

* **Sample data.** Examples that read a table use the `examples` keyspace. Create it with the setup block in [Querying with CQL, section 1](../03_application_development/05_querying_with_cql.md#1-set-up-the-sample-data). Examples on constants select `FROM system.local`, a table that always has exactly one row.
* **Column names.** Without an alias, `cqlsh` names the column after the call, prefixed with `system.` (the keyspace of built-in functions). Use `AS` to give it a readable name.
* **`null` in, `null` out.** Unless an entry says otherwise, a function returns `null` when an argument is `null`.
* **5.0 names.** 5.0 renamed most functions to snake case (`toDate` became `to_date`). The old names still work and are listed in [section 12](#12-pre-50-names). Two were removed: `dateOf` and `unixTimestampOf`.
* **Where functions are allowed.** In the select list of `SELECT`, in `INSERT` and `UPDATE` values, and on the right-hand side of `WHERE` conditions. You can't apply a function to a column in `WHERE` (`WHERE to_date(order_time) = ...` is refused), except `token()`.

| Section | Functions |
| :--- | :--- |
| [2. Aggregates](#2-aggregate-functions) | `count`, `min`, `max`, `sum`, `avg` |
| [3. Time and date](#3-time-and-date-functions) | `now`, `current_timeuuid`, `current_timestamp`, `current_date`, `current_time`, `to_date`, `to_timestamp`, `to_unix_timestamp`, `min_timeuuid`, `max_timeuuid`, `floor`, date arithmetic |
| [4. UUID](#4-uuid) | `uuid` |
| [5. Type conversion](#5-type-conversion) | `cast`, `<type>_as_blob`, `blob_as_<type>`, `to_json`, `from_json` |
| [6. Write metadata](#6-write-metadata-writetime-maxwritetime-ttl) | `writetime`, `maxwritetime`, `ttl` |
| [7. Token](#7-token) | `token` |
| [8. Math (new in 5.0)](#8-math-functions-new-in-50) | `abs`, `exp`, `log`, `log10`, `round` |
| [9. Collections (new in 5.0)](#9-collection-functions-new-in-50) | `map_keys`, `map_values`, `collection_count`, `collection_min`, `collection_max`, `collection_sum`, `collection_avg` |
| [10. Vector similarity (new in 5.0)](#10-vector-similarity-functions-new-in-50) | `similarity_cosine`, `similarity_dot_product`, `similarity_euclidean` |
| [11. Masking (new in 5.0)](#11-masking-functions-new-in-50) | `mask_default`, `mask_null`, `mask_replace`, `mask_inner`, `mask_outer`, `mask_hash` |

---

## 2. Aggregate functions

Aggregates combine the rows a query selects into one value, or one value per group with `GROUP BY`. An aggregate without a partition-key restriction reads the whole table, and `cqlsh` prints a warning saying so.

### `count`

| Syntax | Arguments | Returns |
| :--- | :--- | :--- |
| `count(*)`, `count(1)`, `count(column)` | `*`, or any column | `bigint` |

`count(*)` counts rows. `count(column)` counts rows where the column is not `null`; empty collections are `null`.

<!-- test: q:fn-count -->
```sql
SELECT count(*) AS products, count(tags) AS with_tags FROM examples.products;
```
```text
 products | with_tags
----------+-----------
        5 |         3

(1 rows)

Warnings :
Aggregation query used without partition key
```

### `min`, `max`

| Syntax | Arguments | Returns |
| :--- | :--- | :--- |
| `min(column)`, `max(column)` | Any column type that can be compared | The argument's type |

### `sum`, `avg`

| Syntax | Arguments | Returns |
| :--- | :--- | :--- |
| `sum(column)`, `avg(column)` | A numeric column (`tinyint` … `varint`, `float`, `double`, `decimal`, `counter`) | The argument's type |

Because the result has the argument's type, `avg` of an integer column is truncated to an integer. Cast to `double` or `decimal` for a fractional average:

<!-- test: q:fn-sum-avg -->
```sql
SELECT sum(order_id) AS s, avg(order_id) AS int_avg, avg(cast(order_id AS double)) AS real_avg,
       min(total) AS smallest, max(total) AS largest
  FROM examples.orders_by_customer WHERE customer_id = 'c-002';
```
```text
 s    | int_avg | real_avg | smallest | largest
------+---------+----------+----------+---------
 4003 |    2001 |   2001.5 |     7.25 |  120.00

(1 rows)
```

---

## 3. Time and date functions

### `now`, `current_timeuuid`

| Syntax | Arguments | Returns |
| :--- | :--- | :--- |
| `now()`, `current_timeuuid()` | None | `timeuuid` (version 1), unique for each call |

Use it as an insert value for `timeuuid` columns. It's evaluated on the coordinator, once per call.

### `current_timestamp`, `current_date`, `current_time`

| Syntax | Arguments | Returns |
| :--- | :--- | :--- |
| `current_timestamp()`, `current_date()`, `current_time()` | None | `timestamp`, `date` and `time` respectively, at the coordinator's clock |

<!-- test: run:fn-current -->
```sql
SELECT now(), current_timestamp(), current_date(), current_time() FROM system.local;
```
```text
 system.now()                         | system.current_timestamp()      | system.current_date() | system.current_time()
--------------------------------------+---------------------------------+-----------------------+-----------------------
 c12613a0-e67b-11f1-a6e3-e58019896701 | 2026-11-22 13:51:02.106000+0000 |            2026-11-22 |    13:51:02.106164092

(1 rows)
```
The output above is illustrative; your values will be the current time.

### `to_date`

| Syntax | Arguments | Returns |
| :--- | :--- | :--- |
| `to_date(value)` | `timestamp` or `timeuuid` | `date` (the UTC calendar day) |

### `to_timestamp`

| Syntax | Arguments | Returns |
| :--- | :--- | :--- |
| `to_timestamp(value)` | `date` or `timeuuid` | `timestamp` (a `date` becomes midnight UTC) |

### `to_unix_timestamp`

| Syntax | Arguments | Returns |
| :--- | :--- | :--- |
| `to_unix_timestamp(value)` | `timestamp`, `timeuuid` or `date` | `bigint`, milliseconds since 1970-01-01 00:00 UTC |

<!-- test: q:fn-time-conversion -->
```sql
SELECT order_time, to_date(order_time) AS day, to_unix_timestamp(order_time) AS epoch_ms,
       to_timestamp(to_date(order_time)) AS midnight
  FROM examples.orders_by_customer WHERE customer_id = 'c-002';
```
```text
 order_time                      | day        | epoch_ms      | midnight
---------------------------------+------------+---------------+---------------------------------
 2026-01-09 20:30:00.000000+0000 | 2026-01-09 | 1767990600000 | 2026-01-09 00:00:00.000000+0000
 2026-01-07 08:05:00.000000+0000 | 2026-01-07 | 1767773100000 | 2026-01-07 00:00:00.000000+0000

(2 rows)
```

### `min_timeuuid`, `max_timeuuid`

| Syntax | Arguments | Returns |
| :--- | :--- | :--- |
| `min_timeuuid(ts)`, `max_timeuuid(ts)` | `timestamp` | The smallest and largest possible `timeuuid` for that millisecond |

Use them to query a `timeuuid` clustering column by time, for example `WHERE id > max_timeuuid('2026-01-01') AND id < min_timeuuid('2026-02-01')`. Don't insert them: they aren't unique.

<!-- test: q:fn-minmax-timeuuid -->
```sql
SELECT min_timeuuid('2026-01-01 00:00:00+0000') AS lo, max_timeuuid('2026-01-01 00:00:00+0000') AS hi FROM system.local;
```
```text
 lo                                   | hi
--------------------------------------+--------------------------------------
 d0c3c000-e6a4-11f0-8080-808080808080 | d0c3e70f-e6a4-11f0-7f7f-7f7f7f7f7f7f

(1 rows)
```

### `floor`

| Syntax | Arguments | Returns |
| :--- | :--- | :--- |
| `floor(ts, duration [, start])` | `timestamp` or `timeuuid`, a `duration`, an optional `timestamp` | `timestamp` |
| `floor(d, duration [, start])` | `date`, a `duration`, an optional `date` | `date` |
| `floor(t, duration)` | `time`, a `duration` | `time` |

Rounds a time down to a multiple of the duration, counted from `start`. The default start is 1970-01-01 00:00 UTC. Most useful in `GROUP BY` for time buckets ([example](../03_application_development/05_querying_with_cql.md#7-aggregates-and-group-by)).

> [!WARNING]
> 1970-01-01 was a Thursday, so `floor(ts, 1w)` without a start gives weeks that begin on **Thursday**. Pass a Monday as the third argument for ISO weeks:

<!-- test: q:fn-floor -->
```sql
SELECT order_time, floor(order_time, 1h) AS hour, floor(order_time, 1w) AS week_from_thursday,
       floor(order_time, 1w, '2026-01-05') AS week_from_monday
  FROM examples.orders_by_customer WHERE customer_id = 'c-002';
```
```text
 order_time                      | hour                            | week_from_thursday              | week_from_monday
---------------------------------+---------------------------------+---------------------------------+---------------------------------
 2026-01-09 20:30:00.000000+0000 | 2026-01-09 20:00:00.000000+0000 | 2026-01-08 00:00:00.000000+0000 | 2026-01-05 00:00:00.000000+0000
 2026-01-07 08:05:00.000000+0000 | 2026-01-07 08:00:00.000000+0000 | 2026-01-01 00:00:00.000000+0000 | 2026-01-05 00:00:00.000000+0000

(2 rows)
```

### Date arithmetic

| Syntax | Arguments | Returns |
| :--- | :--- | :--- |
| `value + duration`, `value - duration` | `timestamp` or `date`, and a `duration` literal (`1d`, `2h30m`, `1mo`, `P1W`) | The first operand's type |

<!-- test: q:fn-date-arithmetic -->
```sql
SELECT order_time, order_time + 1d AS next_day, order_time - 2h30m AS earlier
  FROM examples.orders_by_customer WHERE customer_id = 'c-002';
```
```text
 order_time                      | next_day                        | earlier
---------------------------------+---------------------------------+---------------------------------
 2026-01-09 20:30:00.000000+0000 | 2026-01-10 20:30:00.000000+0000 | 2026-01-09 18:00:00.000000+0000
 2026-01-07 08:05:00.000000+0000 | 2026-01-08 08:05:00.000000+0000 | 2026-01-07 05:35:00.000000+0000

(2 rows)
```

---

## 4. UUID

### `uuid`

| Syntax | Arguments | Returns |
| :--- | :--- | :--- |
| `uuid()` | None | A random (version 4) `uuid`, different on every call |

<!-- test: run:fn-uuid -->
```sql
SELECT uuid() FROM system.local;
```

---

## 5. Type conversion

### `cast`

| Syntax | Arguments | Returns |
| :--- | :--- | :--- |
| `cast(value AS type)` | A native-type value; `type` is a native type | `type` |

Allowed: between numeric types (fractions are truncated toward zero), from any native type to `text` or `ascii`, and between `timestamp`, `date` and `timeuuid`. A `timestamp` cast to `text` uses ISO 8601. `cast` works only in the select list.

<!-- test: q:fn-cast -->
```sql
SELECT total, cast(total AS int) AS whole, cast(total AS text) AS label, cast(order_time AS date) AS day,
       cast(order_time AS text) AS iso
  FROM examples.orders_by_customer WHERE customer_id = 'c-002';
```
```text
 total  | whole | label  | day        | iso
--------+-------+--------+------------+--------------------------
 120.00 |   120 | 120.00 | 2026-01-09 | 2026-01-09T20:30:00.000Z
   7.25 |     7 |   7.25 | 2026-01-07 | 2026-01-07T08:05:00.000Z

(2 rows)
```

### `<type>_as_blob`, `blob_as_<type>`

| Syntax | Arguments | Returns |
| :--- | :--- | :--- |
| `<type>_as_blob(value)`, for example `text_as_blob`, `int_as_blob`, `bigint_as_blob` | A value of `<type>` | `blob` (the value's serialized bytes) |
| `blob_as_<type>(b)`, for example `blob_as_text`, `blob_as_int` | A `blob` holding a serialized `<type>` | `<type>` |

There is one pair for each native type.

<!-- test: q:fn-blob -->
```sql
SELECT text_as_blob('shipped!') AS b, blob_as_text(0x7368697070656421) AS t, int_as_blob(1) AS i FROM system.local;
```
```text
 b                  | t        | i
--------------------+----------+------------
 0x7368697070656421 | shipped! | 0x00000001

(1 rows)
```

### `to_json`

| Syntax | Arguments | Returns |
| :--- | :--- | :--- |
| `to_json(value)` | Any type | `text`: the value as JSON |

To return a whole row as JSON, use `SELECT JSON` instead ([example](../03_application_development/05_querying_with_cql.md#10-what-you-can-select)).

<!-- test: q:fn-to-json -->
```sql
SELECT to_json(tags) AS tags, to_json(price) AS price, to_json(embedding) AS embedding
  FROM examples.products WHERE product_id = 'p-20';
```
```text
 tags               | price | embedding
--------------------+-------+-----------------
 ["gas", "outdoor"] | 15.00 | [0.8, 0.3, 0.1]

(1 rows)
```

### `from_json`

| Syntax | Arguments | Returns |
| :--- | :--- | :--- |
| `from_json(json_text)` | A JSON string | The type of the column it's assigned to |

`from_json` needs to know the target type, so use it in `INSERT` and `UPDATE` values or in a `WHERE` condition, not in the select list. To insert a whole row from JSON, use `INSERT ... JSON` ([quick reference](04_cql_quick_reference.md#4-writes-insert-update-delete-batch)).

<!-- test: q:fn-from-json -->
```sql
CREATE TABLE IF NOT EXISTS examples.json_demo (id int PRIMARY KEY, tags set<text>);
INSERT INTO examples.json_demo (id, tags) VALUES (1, from_json('["b", "a", "b"]'));
SELECT * FROM examples.json_demo WHERE id = 1;
```
```text
 id | tags
----+------------
  1 | {'a', 'b'}

(1 rows)
```

---

## 6. Write metadata: `writetime`, `maxwritetime`, `ttl`

These are selectors rather than functions, but you call them the same way. They don't accept primary-key columns, which have no write time of their own.

| Syntax | Arguments | Returns |
| :--- | :--- | :--- |
| `writetime(column)` | A regular or static column | `bigint`, microseconds since the epoch. For a non-frozen collection, a `list<bigint>` with one value per element |
| `maxwritetime(column)` (new in 5.0) | A regular or static column | `bigint`: the newest write time in the column, including every element of a collection or UDT |
| `ttl(column)` | A regular or static column | `int`: seconds until the value expires, or `null` if it has no TTL |

<!-- test: q:fn-writetime -->
```sql
SELECT writetime(name) AS name_written, writetime(tags) AS per_element, maxwritetime(tags) AS newest
  FROM examples.products WHERE product_id = 'p-20';
SELECT writetime(product_id) FROM examples.products WHERE product_id = 'p-20';
```
```text
 name_written     | per_element                          | newest
------------------+--------------------------------------+------------------
 1767225600000000 | [1767225600000000, 1767225600000000] | 1767225600000000

(1 rows)
InvalidRequest: Error from server: code=2200 [Invalid query] message="Cannot use selection function writetime on PRIMARY KEY part product_id"
```

`ttl()` counts down, so its value depends on when you run it:

<!-- test: run:fn-ttl -->
```sql
INSERT INTO examples.json_demo (id, tags) VALUES (2, {'temporary'}) USING TTL 3600;
SELECT id, ttl(tags) FROM examples.json_demo WHERE id IN (1, 2);
```
```text
 id | ttl(tags)
----+-----------
  1 |      null
  2 |      3599

(2 rows)
```

---

## 7. Token

### `token`

| Syntax | Arguments | Returns |
| :--- | :--- | :--- |
| `token(pk1 [, pk2, ...])` | All partition-key columns, in order, or literal values for them | `bigint` with the default `Murmur3Partitioner` |

The token decides which nodes own a partition. `token()` is the one function you can apply to columns in `WHERE`, to scan a table range by range ([example](../03_application_development/05_querying_with_cql.md#10-what-you-can-select)).

<!-- test: q:fn-token -->
```sql
SELECT token('c-001') AS literal, token(customer_id) AS from_column
  FROM examples.orders_by_customer WHERE customer_id = 'c-001' LIMIT 1;
```
```text
 literal              | from_column
----------------------+----------------------
 -2905060879872292637 | -2905060879872292637

(1 rows)
```

---

## 8. Math functions (new in 5.0)

| Syntax | Arguments | Returns |
| :--- | :--- | :--- |
| `abs(x)` | Any numeric type | The argument's type: the absolute value |
| `exp(x)` | Any numeric type | The argument's type: *e* to the power `x` |
| `log(x)` | Any numeric type | The argument's type: the natural logarithm |
| `log10(x)` | Any numeric type | The argument's type: the base-10 logarithm |
| `round(x)` | Any numeric type | The argument's type: the nearest whole number. Halves round up toward positive infinity (2.5 → 3, −2.5 → −2) |

Because the result has the argument's type, `exp`, `log` and `log10` of an **integer** are truncated. Use a `double` when you need the fraction: a `double` column, or a constant with a type hint such as `(double)2`. (`cast()` works on columns, but not on a bare constant in the select list.)

<!-- test: q:fn-math -->
```sql
SELECT abs(-2.5) AS abs, exp(2) AS exp_int, exp((double)2) AS exp_double,
       log(10) AS log_int, log((double)10) AS log_double, log10((double)1000) AS log10,
       round(2.5) AS r1, round(-2.5) AS r2
  FROM system.local;
```
```text
 abs | exp_int | exp_double | log_int | log_double | log10 | r1 | r2
-----+---------+------------+---------+------------+-------+----+----
 2.5 |       7 |    7.38906 |       2 |    2.30259 |     3 |  3 | -2

(1 rows)
```

---

## 9. Collection functions (new in 5.0)

These work on one collection value in one row. To aggregate across rows, use the functions in section 2.

| Syntax | Arguments | Returns |
| :--- | :--- | :--- |
| `map_keys(m)` | A map | A `set` of the keys |
| `map_values(m)` | A map | A `list` of the values |
| `collection_count(c)` | A set, list or map | `int`: the number of elements |
| `collection_min(c)`, `collection_max(c)` | A set or list | The element type: the smallest or largest element |
| `collection_sum(c)`, `collection_avg(c)` | A set or list of numbers | The element type. Like `avg`, `collection_avg` of integers is truncated |

For a map, wrap it in `map_values()` before `collection_sum` and the others. Passing the map itself is refused:

<!-- test: q:fn-collections -->
```sql
SELECT order_id, items, map_keys(items) AS products, map_values(items) AS quantities,
       collection_count(items) AS lines, collection_sum(map_values(items)) AS units
  FROM examples.orders_by_customer WHERE customer_id = 'c-001';
SELECT collection_sum(items) FROM examples.orders_by_customer WHERE customer_id = 'c-001';
```
```text
 order_id | items                  | products         | quantities | lines | units
----------+------------------------+------------------+------------+-------+-------
     1003 |            {'p-40': 1} |         {'p-40'} |        [1] |     1 |     1
     1002 |            {'p-30': 1} |         {'p-30'} |        [1] |     1 |     1
     1001 | {'p-10': 1, 'p-20': 2} | {'p-10', 'p-20'} |     [1, 2] |     2 |     3

(3 rows)
InvalidRequest: Error from server: code=2200 [Invalid query] message="Function system.collection_sum requires a numeric set/list argument, but found argument items of type map<text, int>"
```

<!-- test: q:fn-collection-minmax -->
```sql
SELECT collection_min(tags) AS first, collection_max(tags) AS last,
       collection_avg([1, 2, 4]) AS int_avg, collection_avg([1.0, 2.0, 4.0]) AS decimal_avg
  FROM examples.products WHERE product_id = 'p-20';
```
```text
 first | last    | int_avg | decimal_avg
-------+---------+---------+-------------
   gas | outdoor |       2 |     2.33333

(1 rows)
```

---

## 10. Vector similarity functions (new in 5.0)

| Syntax | Arguments | Returns |
| :--- | :--- | :--- |
| `similarity_cosine(v1, v2)` | Two `vector<float, n>` of the same dimension | `float`, (1 + cosine) / 2. Between 0 and 1; higher is more similar. All-zero vectors are rejected |
| `similarity_dot_product(v1, v2)` | Same | `float`, (1 + dot product) / 2. Meaningful only for unit-length vectors |
| `similarity_euclidean(v1, v2)` | Same | `float`, 1 / (1 + squared distance). Higher is more similar |

The functions don't need an index. With an SAI vector index, use them next to `ORDER BY ... ANN OF` to show each result's score ([example](../03_application_development/05_querying_with_cql.md#9-vector-search-with-ann-of)). How to choose between them is on the [vector search page](../02_data_modeling_and_indexing/02_indexing_and_vector_search.md).

<!-- test: q:fn-similarity -->
```sql
SELECT product_id, embedding,
       similarity_cosine(embedding, [1.0, 0.0, 0.0]) AS cosine,
       similarity_dot_product(embedding, [1.0, 0.0, 0.0]) AS dot,
       similarity_euclidean(embedding, [1.0, 0.0, 0.0]) AS euclidean
  FROM examples.products WHERE product_id = 'p-10';
```
```text
 product_id | embedding     | cosine   | dot  | euclidean
------------+---------------+----------+------+-----------
       p-10 | [0.9, 0.1, 0] | 0.996942 | 0.95 |  0.980392

(1 rows)
```

---

## 11. Masking functions (new in 5.0)

The masking functions hide a value. You can call them in a query like any function. Their main use is in a column definition (`email text MASKED WITH mask_inner(1, 1)`), where they apply to every reader without the `UNMASK` permission. That use requires `dynamic_data_masking_enabled: true` in `cassandra.yaml`; calling them in a query doesn't. See [dynamic data masking](04_cql_quick_reference.md#9-dynamic-data-masking-50).

| Syntax | Arguments | Returns |
| :--- | :--- | :--- |
| `mask_default(x)` | Any type | A fixed value of the same type: `****` for text, `0` for numbers, `false` for booleans, `1970-01-01` for dates and timestamps, the all-zero UUID for UUIDs |
| `mask_null(x)` | Any type | `null` |
| `mask_replace(x, replacement)` | Any type, and a value of the same type | `replacement` |
| `mask_inner(x, begin, end [, padding])` | `text` or `ascii`, two `int`, an optional one-character `text` (default `*`) | The value with everything except the first `begin` and last `end` characters replaced |
| `mask_outer(x, begin, end [, padding])` | Same | The value with the first `begin` and last `end` characters replaced |
| `mask_hash(x [, algorithm])` | Any type, an optional algorithm name (default `SHA-256`) | `blob`: the hash of the serialized value |

<!-- test: q:fn-masking -->
```sql
SELECT name, mask_default(name) AS dflt, mask_null(name) AS nul, mask_replace(name, 'hidden') AS rep,
       mask_inner(name, 1, 1) AS inner_masked, mask_outer(name, 2, 2, '#') AS outer_masked
  FROM examples.products WHERE product_id = 'p-40';
SELECT mask_hash(name) AS sha256 FROM examples.products WHERE product_id = 'p-40';
```
```text
 name     | dflt | nul  | rep    | inner_masked | outer_masked
----------+------+------+--------+--------------+--------------
 Headlamp | **** | null | hidden |     H******p |     ##adla##

(1 rows)

 sha256
--------------------------------------------------------------------
 0x0d7744258fa44ea0e5b96c5423eefa9d313d4d9563c6a6e69c5958de3fd478ab

(1 rows)
```

---

## 12. Pre-5.0 names

5.0 added snake-case names. The old names still work, so queries written for 4.x keep running, but new code should use the 5.0 names.

| 5.0 name | Older name that still works |
| :--- | :--- |
| `to_date`, `to_timestamp`, `to_unix_timestamp` | `todate`, `totimestamp`, `tounixtimestamp` |
| `min_timeuuid`, `max_timeuuid` | `mintimeuuid`, `maxtimeuuid` |
| `current_timestamp`, `current_date`, `current_time`, `current_timeuuid` | `currenttimestamp`, `currentdate`, `currenttime`, `currenttimeuuid` |
| `<type>_as_blob`, `blob_as_<type>` | `<type>asblob`, `blobas<type>` (for example `textasblob`) |
| `to_json`, `from_json` | `tojson`, `fromjson` |
| *(removed)* | `dateof`: use `to_timestamp`. `unixtimestampof`: use `to_unix_timestamp` |

Function names are case-insensitive unless quoted, so `toDate` is the same as `todate`.

<!-- test: q:fn-legacy -->
```sql
SELECT textasblob('a') AS old_blob, totimestamp(to_date('2026-01-05 10:00:00+0000')) AS old_ts FROM system.local;
SELECT dateOf(now()) FROM system.local;
```
```text
 old_blob | old_ts
----------+---------------------------------
     0x61 | 2026-01-05 00:00:00.000000+0000

(1 rows)
InvalidRequest: Error from server: code=2200 [Invalid query] message="Unknown function 'dateof'"
```

---

## Sources

Repository files (branch `cassandra-5.0`):
* Function registry: [cql3/functions/NativeFunctions.java](https://github.com/apache/cassandra/blob/cassandra-5.0/src/java/org/apache/cassandra/cql3/functions/NativeFunctions.java)
* [TimeFcts.java](https://github.com/apache/cassandra/blob/cassandra-5.0/src/java/org/apache/cassandra/cql3/functions/TimeFcts.java), [UuidFcts.java](https://github.com/apache/cassandra/blob/cassandra-5.0/src/java/org/apache/cassandra/cql3/functions/UuidFcts.java), [AggregateFcts.java](https://github.com/apache/cassandra/blob/cassandra-5.0/src/java/org/apache/cassandra/cql3/functions/AggregateFcts.java), [CastFcts.java](https://github.com/apache/cassandra/blob/cassandra-5.0/src/java/org/apache/cassandra/cql3/functions/CastFcts.java), [BytesConversionFcts.java](https://github.com/apache/cassandra/blob/cassandra-5.0/src/java/org/apache/cassandra/cql3/functions/BytesConversionFcts.java), [ToJsonFct.java](https://github.com/apache/cassandra/blob/cassandra-5.0/src/java/org/apache/cassandra/cql3/functions/ToJsonFct.java), [FromJsonFct.java](https://github.com/apache/cassandra/blob/cassandra-5.0/src/java/org/apache/cassandra/cql3/functions/FromJsonFct.java)
* [MathFcts.java](https://github.com/apache/cassandra/blob/cassandra-5.0/src/java/org/apache/cassandra/cql3/functions/MathFcts.java), [CollectionFcts.java](https://github.com/apache/cassandra/blob/cassandra-5.0/src/java/org/apache/cassandra/cql3/functions/CollectionFcts.java), [VectorFcts.java](https://github.com/apache/cassandra/blob/cassandra-5.0/src/java/org/apache/cassandra/cql3/functions/VectorFcts.java), [masking/](https://github.com/apache/cassandra/tree/cassandra-5.0/src/java/org/apache/cassandra/cql3/functions/masking)
* `writetime`, `maxwritetime`, `ttl`: [cql3/selection/Selectable.java](https://github.com/apache/cassandra/blob/cassandra-5.0/src/java/org/apache/cassandra/cql3/selection/Selectable.java)

Official documentation: [CQL functions](https://cassandra.apache.org/doc/5.0/cassandra/developing/cql/functions.html).
