# cqlsh: The CQL Shell (Cassandra 5.0)

> [!CAUTION]
> Commands on this page can change or delete data and affect running clusters. Try them on a test or staging cluster first, and read the [disclaimer](../README.md#disclaimer). The guide is provided "as is", without warranty.

`cqlsh` is the command-line client that ships with Cassandra. Use it to explore a cluster, run schema changes, script one-off queries, and export or import small tables as CSV. This page covers how to run it, interactive and scripted use, output formats, every shell command, configuration files and `COPY`. Options and defaults come from the 5.0 source ([`pylib/cqlshlib/cqlshmain.py`](https://github.com/apache/cassandra/blob/cassandra-5.0/pylib/cqlshlib/cqlshmain.py) and [`copyutil.py`](https://github.com/apache/cassandra/blob/cassandra-5.0/pylib/cqlshlib/copyutil.py)).

Examples with output use the quickstart node and the `examples` keyspace from [Querying with CQL, section 1](../03_application_development/05_querying_with_cql.md#1-set-up-the-sample-data). [`test_env` scenario 14](../test_env/README.md) runs them against Cassandra 5.0 and compares the output with this page. Other tools (`sstableloader`, the SSTable tools, `cassandra-stress`) are in the [tools reference](03_tools_reference.md).

---

## 1. Running cqlsh

| Where | Command |
| :--- | :--- |
| Docker (no install needed) | `docker exec -it <container> cqlsh`, or `docker run --rm -it cassandra:5.0 cqlsh <host>` to reach another host |
| Tarball install | `bin/cqlsh [host [port]]`. It needs Python on the `PATH`. |
| deb / rpm package | `cqlsh [host [port]]` |

`bin/cqlsh` lists Python 3.8–3.11 as supported and accepts up to 3.13; 3.6 and 3.7 are deprecated. It uses the Python driver bundled in `lib/`. Set `CQLSH_NO_BUNDLED=1` to use a driver installed with pip instead.

To connect, give the host and port, or set them in `cqlshrc` ([section 6](#6-configuration-files-cqlshrc-and-credentials)) or in `$CQLSH_HOST` / `$CQLSH_PORT`. A host given on the command line wins. The default is `127.0.0.1` port `9042`.

```bash
cqlsh 10.0.1.10 9042 -u app_admin --request-timeout 30
```

### Command-line options

| Option | Purpose |
| :--- | :--- |
| `-u`, `--username` / `-p`, `--password` | Authenticate. Passing `-p` on the command line prints a warning; use a credentials file instead ([section 6](#6-configuration-files-cqlshrc-and-credentials)). If you give `-u` without `-p`, cqlsh prompts for the password. |
| `-k`, `--keyspace` | Start in this keyspace |
| `-e`, `--execute "STATEMENTS"` | Run the statements, then exit ([section 3](#3-scripting-with-cqlsh)) |
| `-f`, `--file FILE` | Run the statements in FILE, then exit |
| `--ssl` | Connect with TLS (configure `[ssl]` in cqlshrc) |
| `--connect-timeout SECS` | Default **5** |
| `--request-timeout SECS` | Default **10**. Raise it for slow queries, schema changes and `TRUNCATE`. |
| `--protocol-version N`, `--cqlversion V` | Force a native protocol or CQL version. Normally negotiated. |
| `--cqlshrc PATH`, `--credentials PATH` | Use other config and credentials files |
| `-C`/`--color`, `--no-color` | Force color on or off. Color is on only for an interactive terminal. |
| `-t`, `--tty` | Behave as if the input were a terminal |
| `--encoding ENC` | Output encoding (default `utf-8`) |
| `--disable-history` | Don't save this session's history |
| `--browser BROWSER` | The browser `HELP` opens for CQL topics |
| `--debug` | Print driver and connection details |
| `-v`, `--version` | Print the cqlsh version |

### Environment variables

| Variable | Effect |
| :--- | :--- |
| `CQLSH_HOST`, `CQLSH_PORT` | Default host and port |
| `CQL_HISTORY` | History file (default `~/.cassandra/cqlsh_history`) |
| `CQLSH_PROMPT` | Text shown on its own line above every prompt. Useful to label production: `CQLSH_PROMPT='*** PROD ***'` |
| `TZ` | Time zone for displaying timestamps, unless `[ui] timezone` is set in cqlshrc |
| `SSL_CERTFILE`, `SSL_VALIDATE` | The CA file and whether to validate the server certificate, if not set in cqlshrc |
| `CQLSH_NO_BUNDLED` | Use the pip-installed Python driver instead of the bundled one |

---

## 2. Interactive use

```text
$ docker exec -it cass-quickstart cqlsh
Connected to Test Cluster at 127.0.0.1:9042
[cqlsh 6.2.0 | Cassandra 5.0.9 | CQL spec 3.4.7 | Native protocol v5]
Use HELP for help.
cqlsh> USE examples;
cqlsh:examples> SELECT order_id, total
            ... FROM orders_by_customer WHERE customer_id = 'c-002';
```

* **Statements end with `;`.** Until you type one, cqlsh shows the `...` continuation prompt. Shell commands such as `EXPAND` don't need it.
* **Tab completes** keywords, keyspaces, tables and columns.
* **The prompt shows the current keyspace** after `USE`.
* **History** is kept in `~/.cassandra/cqlsh_history`. Use the up arrow, or `HISTORY` to list it. History can hold passwords from `CREATE ROLE` statements; use `--disable-history` when you type secrets, or delete the lines afterwards.
* **`HELP`** lists topics; `HELP SELECT` and the others open the CQL documentation in a browser, or print its URL.

---

## 3. Scripting with cqlsh

Pass statements with `-e`, a file with `-f`, or pipe them in. All three are "batch mode": no prompt and no color.

> [!IMPORTANT]
> In batch mode, cqlsh **keeps going after a failed statement** and exits with code **2** at the end if any statement failed. It doesn't stop at the first error. If later statements depend on earlier ones, run them one at a time and check each exit code. Errors go to standard error, with a `<stdin>:N:` prefix (or the file name) in front of the message.

<!-- test: sh:cqlsh-exit-code -->
```bash
printf '%s\n' "SELECT count(*) AS n FROM examples.orders_by_customer WHERE customer_id = 'c-002';" \
              "SELECT * FROM examples.no_such_table;" \
              "SELECT count(*) AS n FROM examples.orders_by_customer WHERE customer_id = 'c-001';" \
  | docker exec -i cass-quickstart cqlsh --no-color > out.txt 2> err.txt
echo "exit code: $?"
echo "--- standard output:"; cat out.txt
echo "--- standard error:";  cat err.txt
rm out.txt err.txt
```
```text
exit code: 2
--- standard output:

 n
---
 2

(1 rows)

 n
---
 3

(1 rows)
--- standard error:
<stdin>:3:InvalidRequest: Error from server: code=2200 [Invalid query] message="table no_such_table does not exist"
```

The second statement failed, the third still ran, and the exit code is 2.

**One value into a shell variable.** cqlsh has no "raw" output mode. Take the line after the dashes:

<!-- test: sh:cqlsh-one-value -->
```bash
n=$(docker exec cass-quickstart cqlsh --no-color -e "SELECT count(*) FROM examples.orders_by_customer WHERE customer_id = 'c-001';" \
    | awk 'f && NF { print $1; exit } /^-+$/ { f = 1 }')
echo "c-001 has $n orders"
```
```text
c-001 has 3 orders
```

**A file of statements.** Use `-f` for schema files. Put `USE` or full `keyspace.table` names in the file, and check the exit code:

```bash
cqlsh -f schema.cql || { echo "schema.cql had errors" >&2; exit 1; }
```

**Machine-readable output.** For JSON, use `SELECT JSON` (one JSON document per row). For CSV, use `COPY ... TO STDOUT` ([section 7](#7-copy-to--copy-from-csv-export-and-import)). For anything bigger than a quick script, use a [driver](../03_application_development/03_client_drivers.md); it gives you typed values, paging and retries.

---

## 4. Shell commands

These are cqlsh commands, not CQL: drivers don't understand them.

| Command | What it does |
| :--- | :--- |
| `CONSISTENCY [level]` | Show or set the consistency level for later statements. **The cqlsh default is `ONE`**, not the `LOCAL_ONE` most drivers use. |
| `SERIAL CONSISTENCY [SERIAL \| LOCAL_SERIAL]` | The serial consistency level for lightweight transactions. Default `SERIAL`. |
| `TRACING ON \| OFF` | Print the server-side trace of each statement ([section 5](#5-reading-a-trace)) |
| `PAGING [ON \| OFF \| <n>]` | Interactive paging. Default on, **100** rows per page. |
| `EXPAND ON \| OFF` | Vertical output: one line per column. Good for wide rows. |
| `CAPTURE '<file>'` / `CAPTURE OFF` | Also write query output to a file |
| `SOURCE '<file>'` | Run the statements in a file |
| `DESCRIBE ...` / `DESC ...` | Show schema as CQL. Runs on the server since 4.0, so drivers can use it too ([quick reference](04_cql_quick_reference.md#10-describe)). |
| `SHOW VERSION`, `SHOW HOST`, `SHOW SESSION <trace id>`, `SHOW REPLICAS <token> [keyspace]` | Versions, the connected host, a past trace, or the nodes that own a token |
| `LOGIN <user> ['<password>']` | Reconnect as another role |
| `COPY ...` | CSV import and export ([section 7](#7-copy-to--copy-from-csv-export-and-import)) |
| `USE <keyspace>` | Set the current keyspace (this one is CQL) |
| `CLEAR` / `CLS`, `HISTORY`, `HELP [topic]`, `EXIT` / `QUIT` | Housekeeping |

### `CONSISTENCY`

<!-- test: q:cqlsh-consistency -->
```sql
CONSISTENCY
CONSISTENCY LOCAL_QUORUM
CONSISTENCY
```
```text
Current consistency level is ONE.
Consistency level set to LOCAL_QUORUM.
Current consistency level is LOCAL_QUORUM.
```

On a single node, `LOCAL_QUORUM` is 1 replica, so queries still work. On a real cluster, match what your application uses before you compare results with it. See [consistency levels](../03_application_development/04_consistency_and_transactions.md).

### `PAGING`

<!-- test: q:cqlsh-paging -->
```sql
PAGING
PAGING 2
SELECT order_id FROM examples.orders_by_customer WHERE customer_id = 'c-001';
PAGING OFF
```
```text
PAGING is ON
Page size: 100
Page size: 2

 order_id
----------
     1003
     1002
     1001

(3 rows)
PAGING set to OFF
```

In an interactive session, cqlsh stops after each page and waits for a key press (`---MORE---`). In batch mode it fetches all pages without waiting. Paging also affects which queries are allowed: `ORDER BY` with `IN` on the partition key needs `PAGING OFF` ([example](../03_application_development/05_querying_with_cql.md#5-order-by)).

### `EXPAND`

<!-- test: q:cqlsh-expand -->
```sql
EXPAND ON
SELECT * FROM examples.products WHERE product_id = 'p-20';
EXPAND OFF
```
```text
EXPAND set to ON

@ Row 1
------------+--------------------
 product_id | p-20
 category   | outdoor
 embedding  | [0.8, 0.3, 0.1]
 name       | Camp stove
 price      | 15.00
 tags       | {'gas', 'outdoor'}


(1 rows)
EXPAND set to OFF
```

### `SHOW` and `DESCRIBE`

<!-- test: run:cqlsh-show -->
```sql
SHOW VERSION
SHOW HOST
DESCRIBE TABLES
DESCRIBE TABLE examples.products
```

`SHOW VERSION` prints the cqlsh, Cassandra, CQL and protocol versions, for example `[cqlsh 6.2.0 | Cassandra 5.0.9 | CQL spec 3.4.7 | Native protocol v5]`. `DESCRIBE TABLE` prints the full `CREATE TABLE` statement with every table option, followed by the table's indexes. That makes it the quickest way to see a table's actual settings.

---

## 5. Reading a trace

`TRACING ON` makes Cassandra record each step of a request. cqlsh prints the trace after the result:

<!-- test: run:cqlsh-tracing -->
```sql
TRACING ON
SELECT order_id FROM examples.orders_by_customer WHERE customer_id = 'c-002';
TRACING OFF
```

Output (illustrative; times and addresses differ):

```text
Tracing session: bfc4f270-e67a-11f1-a6e3-e58019896701

 activity                                                                     | timestamp                  | source     | source_elapsed | client
------------------------------------------------------------------------------+----------------------------+------------+----------------+-----------
                                                           Execute CQL3 query | 2026-11-22 13:43:50.296000 | 172.17.0.2 |              0 | 127.0.0.1
                  Parsing SELECT order_id FROM examples.orders_by_customer... | 2026-11-22 13:43:50.297000 | 172.17.0.2 |           1797 | 127.0.0.1
                                                          Preparing statement | 2026-11-22 13:43:50.297001 | 172.17.0.2 |           1971 | 127.0.0.1
                       Executing single-partition query on orders_by_customer | 2026-11-22 13:43:50.298000 | 172.17.0.2 |           2473 | 127.0.0.1
                                                 Acquiring sstable references | 2026-11-22 13:43:50.298001 | 172.17.0.2 |           2620 | 127.0.0.1
    Skipped 0/0 non-slice-intersecting sstables, included 0 due to tombstones | 2026-11-22 13:43:50.298002 | 172.17.0.2 |           2728 | 127.0.0.1
                                    Merged data from memtables and 0 sstables | 2026-11-22 13:43:50.298003 | 172.17.0.2 |           2856 | 127.0.0.1
                                       Read 2 live rows and 0 tombstone cells | 2026-11-22 13:43:50.298004 | 172.17.0.2 |           2897 | 127.0.0.1
                                                             Request complete | 2026-11-22 13:43:50.299075 | 172.17.0.2 |           3075 | 127.0.0.1
```

| Column | Meaning |
| :--- | :--- |
| `activity` | The step, with the thread pool in brackets on a real trace (`[ReadStage-3]`) |
| `source` | The node that did the step. On a multi-node cluster, look for steps on replicas other than the coordinator. |
| `source_elapsed` | Microseconds since that node started on the request. A big jump between two lines is where the time went. |
| `client` | The address of the client that sent the query |

What to look for:

* **`Merged data from memtables and N sstables`.** A high N on a read means compaction is behind or the data model spreads a partition across many SSTables.
* **`Read N live rows and M tombstone cells`.** A large M explains slow reads and `TombstoneOverwhelmingException` ([troubleshooting](../06_operations_and_housekeeping/05_troubleshooting_playbook.md)).
* **Steps on several nodes**, and the gap between `Sending ... message` and the reply: that's network or a slow replica.

Traces are stored in the `system_traces` keyspace for one day (`trace_type_query_ttl`). Tracing adds load, so turn it on for single statements, not for traffic. To sample production traffic, use `nodetool settraceprobability` sparingly ([nodetool reference](02_nodetool_reference.md)).

---

## 6. Configuration files: `cqlshrc` and `credentials`

cqlsh reads `~/.cassandra/cqlshrc` (or `--cqlshrc`). A fully commented sample ships as `conf/cqlshrc.sample`. The sections you will use most:

```ini
[authentication]
credentials = ~/.cassandra/credentials   ; keeps passwords off the command line
keyspace = my_ks

[connection]
hostname = 10.0.1.10
port = 9042
ssl = true
timeout = 10            ; connect timeout, seconds (default 5)
request_timeout = 30    ; default 10

[ssl]
certfile = ~/keys/ca.pem      ; CA used to validate the server
validate = true
; userkey / usercert only when client_encryption_options.require_client_auth is true
userkey = ~/keys/client.key
usercert = ~/keys/client.pem

[ui]
time_format = %Y-%m-%d %H:%M:%S%z
timezone = Etc/UTC
float_precision = 5     ; default 5
double_precision = 12   ; default 5 in the shell; COPY TO uses 12 unless told otherwise

[history]
disabled = false

[copy]                         ; defaults for COPY TO and COPY FROM
numprocesses = 4
[copy-from:my_ks.my_table]     ; per-table overrides: [copy:ks.t], [copy-from:ks.t], [copy-to:ks.t]
ingestrate = 20000
```

Credentials go in a separate file:

```ini
; ~/.cassandra/credentials
[PlainTextAuthProvider]
username = app_admin
password = s3cret
```

> [!WARNING]
> cqlsh ignores the credentials file, with a warning, if it is readable by group or others or isn't owned by you. Run `chmod 600 ~/.cassandra/credentials`. A `username` or `password` in `cqlshrc` itself still works in 5.0 but prints a deprecation notice.

---

## 7. `COPY TO` / `COPY FROM`: CSV export and import

```sql
COPY my_ks.users (user_id, email, created_at) TO '/tmp/users.csv' WITH HEADER = true;
COPY my_ks.users (user_id, email, created_at) FROM '/tmp/users.csv' WITH HEADER = true AND MAXINSERTERRORS = 100;
```

The file path is on the machine where cqlsh runs. With `docker exec`, that's inside the container. `TO STDOUT` and `FROM STDIN` are also accepted:

<!-- test: run:cqlsh-copy-stdout -->
```sql
COPY examples.products (product_id, name, price) TO STDOUT WITH HEADER = true;
```

```text
product_id,name,price
p-40,Headlamp,99.90
p-10,Trail mug,12.50
p-50,Tea towel,40.00
p-20,Camp stove,15.00
p-30,Chef knife,15.00
```

`COPY` reads in parallel, so the row order isn't fixed. `COPY TO` has no `WHERE`: it exports whole tables, or a token range with `BEGINTOKEN` and `ENDTOKEN`.

| Option (applies to) | Default (from `copyutil.py`) | Notes |
| :--- | :--- | :--- |
| `DELIMITER`, `QUOTE`, `ESCAPE` (both) | `,` `"` `\` | |
| `HEADER` (both) | `false` | |
| `NULL` (both) | empty string | The string that represents null |
| `DATETIMEFORMAT` (both) | the cqlshrc `time_format` | |
| `NUMPROCESSES` (both) | cores − 1, capped at **16** | Worker processes |
| `MAXATTEMPTS` (both) | 5 | Retries per batch or page |
| `REPORTFREQUENCY`, `RATEFILE`, `CONFIGFILE`, `DECIMALSEP`, `THOUSANDSSEP`, `BOOLSTYLE` (both) | | Progress, rate log, alternative config file, number/boolean formats |
| `INGESTRATE` (FROM) | 100000 rows/s | An approximate cap; lower it to protect a busy cluster |
| `CHUNKSIZE` (FROM) | 5000 | Rows sent to each worker at a time |
| `MINBATCHSIZE` / `MAXBATCHSIZE` (FROM) | 10 / 20 | Rows per **single-partition** unlogged batch |
| `MAXROWS`, `SKIPROWS`, `SKIPCOLS` (FROM) | -1 (all), 0, none | |
| `MAXPARSEERRORS` / `MAXINSERTERRORS` (FROM) | -1 (unlimited) / 1000 | Failed rows are written to `ERRFILE` |
| `PREPAREDSTATEMENTS` (FROM) | true | |
| `TTL` (FROM) | -1 (none) | Applies a TTL to every imported row |
| `PAGESIZE` / `PAGETIMEOUT` (TO) | 1000 / 10 s (scaled up with page size) | |
| `MAXREQUESTS` (TO) | 6 | Concurrent page requests per worker |
| `BEGINTOKEN` / `ENDTOKEN` (TO) | full ring | Export a slice of the ring |
| `MAXOUTPUTSIZE` (TO) | -1 | Split the output into files of N rows |
| `ENCODING`, `FLOATPRECISION`, `DOUBLEPRECISION` (TO) | `utf8`, 5, 12 | |

> [!NOTE]
> `COPY` is meant for small to medium data sets (up to a few million rows) and for moving data between environments. It is not a backup tool. For bulk loads use `sstableloader` or a Spark job; for backups use snapshots ([DR runbook](../07_disaster_recovery/01_backup_and_disaster_recovery.md)). The sample `conf/cqlshrc.sample` comments show `chunksize = 1000` and `minbatchsize = 2`; the code defaults above are what actually applies when you set nothing.

---

## Sources

Repository files (branch `cassandra-5.0`):
* [bin/cqlsh](https://github.com/apache/cassandra/blob/cassandra-5.0/bin/cqlsh) (Python version checks) and [bin/cqlsh.py](https://github.com/apache/cassandra/blob/cassandra-5.0/bin/cqlsh.py) (`CQLSH_NO_BUNDLED`)
* [pylib/cqlshlib/cqlshmain.py](https://github.com/apache/cassandra/blob/cassandra-5.0/pylib/cqlshlib/cqlshmain.py): options, defaults (timeouts, page size 100, consistency `ONE`, precision), environment variables, batch-mode exit code 2
* [pylib/cqlshlib/copyutil.py](https://github.com/apache/cassandra/blob/cassandra-5.0/pylib/cqlshlib/copyutil.py): `COPY` options and defaults
* [pylib/cqlshlib/sslhandling.py](https://github.com/apache/cassandra/blob/cassandra-5.0/pylib/cqlshlib/sslhandling.py): `SSL_CERTFILE`, `SSL_VALIDATE`
* [conf/cqlshrc.sample](https://github.com/apache/cassandra/blob/cassandra-5.0/conf/cqlshrc.sample)

Official documentation: [cqlsh](https://cassandra.apache.org/doc/5.0/cassandra/managing/tools/cqlsh.html).
