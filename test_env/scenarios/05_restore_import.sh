#!/usr/bin/env bash
# DOC: 07_disaster_recovery/01_backup_and_disaster_recovery.md (sections 0 and 2)
# CLAIMS: snapshots contain schema.cql and manifest.json; importing an OLD snapshot over newer data does
#         NOT undo the newer writes (last-write-wins); TRUNCATE creates a truncated-* snapshot;
#         TRUNCATE, then nodetool import on every replica, restores the data.
set -uo pipefail
source "$(dirname "$0")/../scripts/lib.sh"
require_nodes cass1 cass2 cass3
DR=07_disaster_recovery/01_backup_and_disaster_recovery.md
KS=drks; T=users; N=100

# stage NODE SNAPSHOT_TAG : copy only SSTable components (not manifest.json/schema.cql) to /tmp/stage
stage() {
  local n="$1" tag="$2" dir; dir=$(table_dir "$n" $KS $T)
  docker exec "$n" bash -c "rm -rf /tmp/stage && mkdir -p /tmp/stage &&
    find '$dir/snapshots/$tag' -maxdepth 1 -type f ! -name manifest.json ! -name schema.cql -exec cp {} /tmp/stage/ \; &&
    chown -R cassandra:cassandra /tmp/stage"
}

make_test_table $KS $T $N
for n in cass1 cass2 cass3; do nt $n snapshot -t good $KS >/dev/null; done
dir=$(table_dir cass1 $KS $T)
check_ok "$DR#0" "snapshot contains schema.cql" docker exec cass1 test -f "$dir/snapshots/good/schema.cql"
check_ok "$DR#0" "snapshot contains manifest.json" docker exec cass1 test -f "$dir/snapshots/good/manifest.json"

# The "bad deploy": overwrite every row
stmts=""; for ((i=0;i<N;i++)); do stmts+="UPDATE $KS.$T SET v='bad' WHERE id=$i;"; done
cq $SEED "$stmts" ALL >/dev/null

# Wrong way: import the old snapshot without truncating
for n in cass1 cass2 cass3; do stage $n good; nt $n import $KS $T /tmp/stage >/dev/null 2>&1; done
check_equals "$DR#0" "importing an old snapshot over newer data does NOT undo it (LWW)" 0 "$(count_value $KS $T good)"

# Right way: TRUNCATE, then import on EVERY replica
cq $SEED "TRUNCATE $KS.$T;" ALL >/dev/null
check_contains "$DR#2" "TRUNCATE leaves an automatic truncated-* snapshot" "truncated-" nt cass1 listsnapshots
for n in cass1 cass2 cass3; do
  stage $n good
  check_ok "$DR#2" "nodetool import on $n" nt $n import $KS $T /tmp/stage
done
check_equals "$DR#2" "after TRUNCATE + import on all replicas, all $N rows are restored" "$N" "$(count_value $KS $T good)"
check_equals "$DR#2" "no 'bad' rows remain" 0 "$(count_value $KS $T bad)"
