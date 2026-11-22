#!/usr/bin/env bash
# DOC: 00_getting_started/01_quickstart.md
# CLAIMS: the quickstart runs as written: the node starts with only MAX_HEAP_SIZE set (1 GB heap, no
#         HEAP_NEWSIZE warning) in datacenter1; the schema and partition queries work; the filtering
#         query is refused with the quoted error; the SAI index answers it; the Python example prints
#         the documented line; cleanup removes the container.
# MANAGES_CLUSTER: yes
# DIRTIES: yes
# The code blocks are read from the page itself (doc_block), so the page and this test can't drift apart.
set -uo pipefail
source "$(dirname "$0")/../scripts/lib.sh"
QS=00_getting_started/01_quickstart.md
C=cass-quickstart
PY_IMAGE="${PY_IMAGE:-python:3.12-slim}"

block() { doc_block "$QS" "$1" | sed "s#cassandra:5.0#$CASSANDRA_IMAGE#g"; }   # test the image under test
cql_block() { block "$1" | docker exec -i "$C" cqlsh 2>&1; }

# This scenario uses its own standalone container; stop the 3-node cluster to free memory.
cluster_down >/dev/null 2>&1
docker rm -f "$C" >/dev/null 2>&1

for b in start wait schema query refused sai sai-status sai-query python cleanup; do
  [ -n "$(block $b)" ] || fail "$QS" "page has a '<!-- test: $b -->' code block" "marker or block missing"
done

check_ok "$QS#2-start-one-node" "the documented docker run starts the node" bash -c "$(block start)"
for _ in $(seq 1 60); do docker exec "$C" cqlsh -e 'DESCRIBE KEYSPACES' >/dev/null 2>&1 && break; sleep 5; done
out=$(bash -c "$(block wait)" 2>&1)
check_contains "$QS#2-start-one-node" "nodetool status shows datacenter1" "Datacenter: datacenter1" echo "$out"
check_contains "$QS#2-start-one-node" "the node is UN" "UN " echo "$out"
check_contains "$QS#2-start-one-node" "MAX_HEAP_SIZE=1G gives a 1024 MB heap" "/ 1024.00" nt "$C" info
if docker logs "$C" 2>&1 | grep -q "HEAP_NEWSIZE"; then
  fail "$QS#2-start-one-node" "no HEAP_NEWSIZE warning when only MAX_HEAP_SIZE is set" "$(docker logs "$C" 2>&1 | grep HEAP_NEWSIZE)"
else pass "$QS#2-start-one-node" "no HEAP_NEWSIZE warning when only MAX_HEAP_SIZE is set"; fi

check_ok "$QS#3-create-a-keyspace-and-a-table" "schema block runs without errors" cql_block schema
check_contains "$QS#3-create-a-keyspace-and-a-table" "keyspace uses NetworkTopologyStrategy datacenter1:1" "'datacenter1': '1'" \
  cq "$C" "SELECT replication FROM system_schema.keyspaces WHERE keyspace_name='quickstart';"

out=$(cql_block query)
check_contains "$QS#4-query-by-partition-key-and-see-what-cassandra-refuses" "partition query returns 3 rows" "(3 rows)" echo "$out"
check_equals "$QS#4-query-by-partition-key-and-see-what-cassandra-refuses" "newest-first order: LIMIT 1 returns 26.5" 26.5 \
  "$(echo "$out" | awk '/\(1 rows\)/ {print last} NF {last=$NF}')"
check_contains "$QS#4-query-by-partition-key-and-see-what-cassandra-refuses" "the non-key query is refused with the quoted error" \
  "Cannot execute this query as it might involve data filtering and thus may have unpredictable performance." cql_block refused

S5="$QS#5-add-an-index-for-the-other-question"
check_ok "$S5" "CREATE INDEX ... USING 'sai' runs" cql_block sai
for _ in $(seq 1 30); do cql_block sai-status | grep -q True && break; sleep 2; done
check_contains "$S5" "sai_column_indexes reports the index as queryable" "True" cql_block sai-status
out=$(cql_block sai-query)
check_contains "$S5" "after the SAI index, value > 25 returns the 26.5 reading" "26.5" echo "$out"
check_contains "$S5" "SAI query needs no ALLOW FILTERING" "(1 rows)" echo "$out"

block python > "$ENV_DIR/shared/quickstart.py"
out=$(docker run --rm --network "container:$C" -v "$ENV_DIR/shared:/shared:ro" "$PY_IMAGE" \
  sh -c 'pip install -q --disable-pip-version-check --root-user-action=ignore cassandra-driver >/dev/null 2>&1 && python3 /shared/quickstart.py' 2>&1)
check_contains "$QS#6-connect-from-an-application" "Python example prints the documented line" "latest reading for s-3: 23.25" echo "$out"
rm -f "$ENV_DIR/shared/quickstart.py"

check_ok "$QS#7-clean-up" "cleanup command removes the container" bash -c "$(block cleanup)"
