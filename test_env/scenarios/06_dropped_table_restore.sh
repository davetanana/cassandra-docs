#!/usr/bin/env bash
# DOC: 07_disaster_recovery/01_backup_and_disaster_recovery.md (section 2, dropped table)
# CLAIMS: DROP TABLE leaves a dropped-* snapshot in the OLD table directory (auto_snapshot: true);
#         its schema.cql carries "ID = <old id>", so re-creating the table from it reuses the old directory;
#         nodetool import of that snapshot on every replica restores the rows.
set -uo pipefail
source "$(dirname "$0")/../scripts/lib.sh"
require_nodes cass1 cass2 cass3
DR=07_disaster_recovery/01_backup_and_disaster_recovery.md
KS=dropks; T=orders; N=50

make_test_table $KS $T $N
old_dir=$(table_dir cass1 $KS $T)
cq $SEED "DROP TABLE $KS.$T;" >/dev/null
sleep 2

snap=$(docker exec cass1 bash -c "ls -d $old_dir/snapshots/dropped-* 2>/dev/null | head -1")
if [ -n "$snap" ]; then pass "$DR#2" "DROP TABLE created $(basename "$snap") in the old table directory"
else fail "$DR#2" "DROP TABLE creates a dropped-* snapshot" "none found under $old_dir/snapshots"; exit 0; fi
check_contains "$DR#2" "dropped snapshot's schema.cql contains the old table ID" "ID = " docker exec cass1 cat "$snap/schema.cql"

docker cp cass1:"$snap/schema.cql" "$ENV_DIR/shared/dropped_schema.cql" >/dev/null
check_ok "$DR#2" "re-create the table from the snapshot's schema.cql" docker exec cass1 cqlsh -f /shared/dropped_schema.cql
new_dir=$(table_dir cass1 $KS $T)
check_equals "$DR#2" "re-created table reuses the old directory (same ID)" "$old_dir" "$new_dir"

for n in cass1 cass2 cass3; do
  s=$(docker exec $n bash -c "ls -d $old_dir/snapshots/dropped-* | head -1")
  docker exec $n bash -c "rm -rf /tmp/stage && mkdir -p /tmp/stage &&
    find '$s' -maxdepth 1 -type f ! -name manifest.json ! -name schema.cql -exec cp {} /tmp/stage/ \; && chown -R cassandra:cassandra /tmp/stage"
  check_ok "$DR#2" "nodetool import on $n" nt $n import $KS $T /tmp/stage
done
check_equals "$DR#2" "all $N rows restored after DROP" "$N" "$(count_value $KS $T good)"
