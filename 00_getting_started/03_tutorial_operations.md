# Tutorial: Run a Three-Node Cluster and Practice a Failure

> [!CAUTION]
> Commands on this page can change or delete data and affect running clusters. Try them on a test or staging cluster first, and read the [disclaimer](../README.md#disclaimer). The guide is provided "as is", without warranty.

<!-- test-env: cluster -->

In this tutorial you run a three-node cluster on your laptop, see how data is replicated, stop a node and watch what still works, bring it back, repair, and then recover from a "bad" `TRUNCATE` with snapshots. It takes about 30 minutes. It's the drill every operator should have done once before an incident forces it.

Every command is run by [`test_env` scenario 15](../test_env/README.md) against the same cluster, and its output is compared with what this page shows.

> [!WARNING]
> Everything here runs against the disposable Docker cluster in [`test_env/`](../test_env/README.md). Never point these commands at a real cluster: they stop nodes and truncate tables.

```mermaid
flowchart LR
    A["Steps 1-2: Healthy cluster,<br/>RF 3"] --> B["Step 3: Stop a node"]
    B --> C["Step 4: QUORUM works,<br/>ALL is refused"]
    C --> D["Step 5: Writes continue,<br/>hints are kept"]
    D --> E["Step 6: Node returns,<br/>hints replay, repair"]
    E --> F["Step 7: Snapshot,<br/>then a bad TRUNCATE"]
    F --> G["Step 8: Restore on<br/>every node"]
```

---

## 1. Start the cluster

You need Docker with 6 GB of memory and the repository cloned. From the repository root:

```bash
cd test_env && scripts/up.sh
```

`up.sh` starts `cass1`, `cass2` and `cass3` one at a time, which takes about five minutes, in one datacenter (`dc1`) with one node per rack (`r1` to `r3`). Then look at the cluster:

```bash
docker exec cass1 nodetool status
```

Each node is one line that starts with two letters: **U**p or **D**own, then **N**ormal, **J**oining, **L**eaving or **M**oving. The other columns are the address, the data load, the token count (16), the share of data it owns, its Host ID and its rack. To see just the state, address and rack, sorted:

<!-- test: sh:ops-status -->
```bash
docker exec cass1 nodetool status | awk '/^[UD][NLJM] / {print $1, $2, $NF}' | sort -k2
```
```text
UN 172.30.0.11 r1
UN 172.30.0.12 r2
UN 172.30.0.13 r3
```

---

## 2. Create replicated data

A keyspace with replication factor 3 in `dc1` keeps a copy of every row on all three nodes. Write three accounts at `QUORUM`, which waits for two of the three copies:

<!-- test: sh:ops-schema -->
```bash
docker exec -i cass1 cqlsh --no-color <<'CQL'
CREATE KEYSPACE IF NOT EXISTS drill WITH replication = {'class': 'NetworkTopologyStrategy', 'dc1': 3};
CREATE TABLE IF NOT EXISTS drill.accounts (account_id text PRIMARY KEY, owner text, balance decimal);
CONSISTENCY QUORUM
INSERT INTO drill.accounts (account_id, owner, balance) VALUES ('acc-1', 'ana', 100.00);
INSERT INTO drill.accounts (account_id, owner, balance) VALUES ('acc-2', 'ben', 250.00);
INSERT INTO drill.accounts (account_id, owner, balance) VALUES ('acc-3', 'chloe', 75.50);
SELECT * FROM drill.accounts;
CQL
```
```text
Consistency level set to QUORUM.

 account_id | balance | owner
------------+---------+-------
      acc-1 |  100.00 |   ana
      acc-2 |  250.00 |   ben
      acc-3 |   75.50 | chloe

(3 rows)
```

Which nodes hold `acc-1`? `nodetool getendpoints` computes it from the partition key's token:

<!-- test: sh:ops-endpoints -->
```bash
docker exec cass1 nodetool getendpoints drill accounts acc-1 | sort
```
```text
172.30.0.11
172.30.0.12
172.30.0.13
```

All three, as RF 3 on three nodes means. On a bigger cluster, each partition lives on 3 of the N nodes, and `getendpoints` tells you which.

---

## 3. Stop a node

<!-- test: sh:ops-stop -->
```bash
docker stop cass3 >/dev/null
until docker exec cass1 nodetool status | grep -q '^DN'; do sleep 2; done
docker exec cass1 nodetool status | awk '/^[UD][NLJM] / {print $1, $2, $NF}' | sort -k2
```
```text
UN 172.30.0.11 r1
UN 172.30.0.12 r2
DN 172.30.0.13 r3
```

A clean stop announces itself, so the others mark it `DN` (Down, Normal) at once. A crashed node takes 10 to 30 seconds to be marked down, through gossip.

---

## 4. See what still works

With one of three replicas down, `QUORUM` still has its two replicas:

<!-- test: sh:ops-quorum -->
```bash
docker exec cass1 cqlsh --no-color -e "CONSISTENCY QUORUM; SELECT * FROM drill.accounts WHERE account_id = 'acc-1';"
```
```text
Consistency level set to QUORUM.

 account_id | balance | owner
------------+---------+-------
      acc-1 |  100.00 |   ana

(1 rows)
```

`ALL` needs every replica, so it's refused before anything is read. The `2>&1 >/dev/null` keeps only the error:

<!-- test: sh:ops-all-refused -->
```bash
docker exec cass1 cqlsh --no-color -e "CONSISTENCY ALL; SELECT * FROM drill.accounts WHERE account_id = 'acc-1';" 2>&1 >/dev/null
```
```text
<stdin>:1:NoHostAvailable: ('Unable to complete the operation against any hosts', {<Host: 127.0.0.1:9042 dc1>: Unavailable('Error from server: code=1000 [Unavailable exception] message="Cannot achieve consistency level ALL" info={\'consistency\': \'ALL\', \'required_replicas\': 3, \'alive_replicas\': 2}')})
```

This is why production uses `LOCAL_QUORUM` and avoids `ALL`: with RF 3, `LOCAL_QUORUM` survives one node down per datacenter, which covers a rolling restart, a crash or a replacement. See [consistency levels](../03_application_development/04_consistency_and_transactions.md).

---

## 5. Keep writing while the node is down

Change ana's balance while `cass3` is down:

<!-- test: sh:ops-write-while-down -->
```bash
docker exec cass1 cqlsh --no-color -e "CONSISTENCY QUORUM; UPDATE drill.accounts SET balance = 60.00 WHERE account_id = 'acc-1';"
```
```text
Consistency level set to QUORUM.
```

The write succeeded on `cass1` and `cass2`. `cass1` coordinated it, so it also stored a **hint**: the mutation `cass3` missed, kept on disk in the hints directory under `cass3`'s Host ID, for up to `max_hint_window` (3 hours by default):

<!-- test: sh:ops-hint-file -->
```bash
until docker exec cass1 sh -c 'ls /var/lib/cassandra/hints | grep -q "\.hints$"'; do sleep 2; done
docker exec cass1 sh -c 'ls /var/lib/cassandra/hints | grep -c "\.hints$"'
```
```text
1
```

`nodetool listpendinghints` and `system_views.pending_hints` list hints only once the hint file being written has been closed, so right after a write they can still say there are none, even though the file exists.

---

## 6. Bring the node back, then repair

<!-- test: sh:ops-start -->
```bash
docker start cass3 >/dev/null
until docker exec cass1 nodetool status 2>/dev/null | grep -q '^UN  172.30.0.13'; do sleep 3; done
docker exec cass1 nodetool status | awk '/^[UD][NLJM] / {print $1, $2, $NF}' | sort -k2
```
```text
UN 172.30.0.11 r1
UN 172.30.0.12 r2
UN 172.30.0.13 r3
```

When `cass3` is back, `cass1` replays the hint to it and deletes the file:

<!-- test: sh:ops-hints-replayed -->
```bash
until [ "$(docker exec cass1 sh -c 'ls /var/lib/cassandra/hints | grep -c "\.hints$"')" = 0 ]; do sleep 2; done
docker exec cass1 cqlsh --no-color -e "CONSISTENCY ALL; SELECT * FROM drill.accounts WHERE account_id = 'acc-1';"
```
```text
Consistency level set to ALL.

 account_id | balance | owner
------------+---------+-------
      acc-1 |   60.00 |   ana

(1 rows)
```

`ALL` works again and every replica returns the new balance.

Hints only cover short outages, and a coordinator that dies loses its hints. After any outage longer than `max_hint_window`, and on a schedule in any case, run a **repair**, which compares the replicas and streams any differences:

<!-- test: sh:ops-repair -->
```bash
docker exec cass1 nodetool repair drill | grep -o 'Repair completed successfully' | head -1
```
```text
Repair completed successfully
```

Without a grep, `nodetool repair` prints one line per repair session. In 5.0, repair is incremental by default, and every table must be repaired within `gc_grace_seconds` (10 days by default) or deleted data can come back. The [housekeeping page](../06_operations_and_housekeeping/02_housekeeping_and_automations.md#2-scheduled-repairs-preventing-resurrected-data) shows why, and [auto-repair](../06_operations_and_housekeeping/06_auto_repair.md) can schedule it for you.

---

## 7. Take a snapshot, then make a mistake

A snapshot is a set of hard links to the node's current SSTables. It's instant and takes no extra space until compaction replaces the files. Snapshots are per node, so take one on **every** node, with the same tag:

<!-- test: sh:ops-snapshot -->
```bash
for n in cass1 cass2 cass3; do docker exec $n nodetool snapshot -t before-oops drill; done
```
```text
Requested creating snapshot(s) for [drill] with snapshot name [before-oops] and options {skipFlush=false}
Snapshot directory: before-oops
Requested creating snapshot(s) for [drill] with snapshot name [before-oops] and options {skipFlush=false}
Snapshot directory: before-oops
Requested creating snapshot(s) for [drill] with snapshot name [before-oops] and options {skipFlush=false}
Snapshot directory: before-oops
```

Now the mistake: someone truncates the table.

<!-- test: sh:ops-truncate -->
```bash
docker exec cass1 cqlsh --no-color -e "CONSISTENCY ALL; TRUNCATE drill.accounts; SELECT count(*) FROM drill.accounts;"
```
```text
Consistency level set to ALL.

 count
-------
     0

(1 rows)

Warnings :
Aggregation query used without partition key
```

`TRUNCATE` also took a snapshot of its own first (`auto_snapshot: true` in the shipped `cassandra.yaml`), named `truncated-<timestamp>-accounts`:

<!-- test: sh:ops-list-snapshots -->
```bash
docker exec cass1 sh -c 'ls -d /var/lib/cassandra/data/drill/accounts-*/snapshots/*' | xargs -n1 basename | sed -E 's/[0-9]{13}/<timestamp>/'
```
```text
before-oops
truncated-<timestamp>-accounts
```

---

## 8. Restore on every node

`nodetool import` loads SSTables from a directory into the live table. On each node, copy the snapshot's data files to a staging directory (leaving out `manifest.json` and `schema.cql`), give them to the `cassandra` user, and import them:

<!-- test: sh:ops-restore -->
```bash
for n in cass1 cass2 cass3; do
  docker exec $n bash -c '
    snap=$(ls -d /var/lib/cassandra/data/drill/accounts-*/snapshots/before-oops)
    rm -rf /tmp/restore && mkdir /tmp/restore
    find "$snap" -maxdepth 1 -type f ! -name manifest.json ! -name schema.cql -exec cp {} /tmp/restore/ \;
    chown -R cassandra:cassandra /tmp/restore
    nodetool import drill accounts /tmp/restore'
done
docker exec cass1 cqlsh --no-color -e "CONSISTENCY ALL; SELECT * FROM drill.accounts;"
```
```text
Consistency level set to ALL.

 account_id | balance | owner
------------+---------+-------
      acc-1 |   60.00 |   ana
      acc-2 |  250.00 |   ben
      acc-3 |   75.50 | chloe

(3 rows)
```

The data is back, including the balance written while `cass3` was down, because the snapshot was taken after the repair.

Two rules from this drill apply to every real restore ([DR runbook, section 0](../07_disaster_recovery/01_backup_and_disaster_recovery.md#0-two-rules-that-apply-to-every-restore)):

* **Restore on every replica.** Importing on one node gives you one copy, and reads at `QUORUM` would still find the other replicas empty.
* **Remove the newer data first.** Here `TRUNCATE` had already done it. If you import an old snapshot over newer data, the newer writes win, because Cassandra keeps the value with the highest timestamp.

---

## 9. What you practiced, and clean up

* Read `nodetool status`, and find a partition's replicas with `getendpoints`.
* `QUORUM` survives one node down at RF 3, and `ALL` doesn't.
* Hints repair short outages; `nodetool repair` repairs everything else.
* Snapshots on every node, then `nodetool import` on every node, restore a table.

Next: the [nodetool operations guide](../06_operations_and_housekeeping/01_nodetool_operations_guide.md), the [troubleshooting playbook](../06_operations_and_housekeeping/05_troubleshooting_playbook.md), and the full [disaster recovery runbook](../07_disaster_recovery/01_backup_and_disaster_recovery.md), including replacing a dead node.

To remove the drill's data and keep the cluster:

```bash
docker exec cass1 cqlsh -e "DROP KEYSPACE drill;"
for n in cass1 cass2 cass3; do docker exec $n nodetool clearsnapshot --all drill; done
```

To stop the cluster and delete all its data: `scripts/down.sh` (from `test_env/`).
