#!/usr/bin/env bash
# DOC: 06_operations_and_housekeeping/06_auto_repair.md
# MANAGES_CLUSTER: yes
# DIRTIES: yes
# CLAIMS: without -Dcassandra.autorepair.enable=true, nodetool reports auto-repair unsupported (switch 1).
#         With the flag but scheduling off (switch 2), commands print "Auto-repair is not enabled" and exit 0.
#         After `setautorepairconfig start_scheduler true`, get/set/status work as documented, and the
#         table-level auto_repair options are accepted.
set -uo pipefail
source "$(dirname "$0")/../scripts/lib.sh"
AR=06_operations_and_housekeeping/06_auto_repair.md

# check_enabled_ok DOC "desc" cmd... : must exit 0 AND must not print the silent "not enabled" message
check_enabled_ok() {
  local ref="$1" desc="$2"; shift 2; local out rc
  out=$("$@" 2>&1); rc=$?
  if [ $rc -eq 0 ] && ! grep -q "not enabled" <<<"$out"; then pass "$ref" "$desc"; else fail "$ref" "$desc" "rc=$rc: $out"; fi
}

unset JVM_EXTRA_OPTS_ALL
reset_cluster
check_contains "$AR#switch-1-the-jvm-property-permanent" "without the JVM flag, setautorepairconfig says it is not enabled via the property" \
  "not enabled via -Dcassandra.autorepair.enable=true" nt $SEED setautorepairconfig start_scheduler true
check_contains "$AR#switch-1-the-jvm-property-permanent" "without the JVM flag, getautorepairconfig fails with 'Server is not initialized yet'" \
  "Server is not initialized yet" nt $SEED getautorepairconfig

log "restarting the cluster with -Dcassandra.autorepair.enable=true (irreversible on real clusters)"
export JVM_EXTRA_OPTS_ALL="-Dcassandra.autorepair.enable=true"
reset_cluster

out=$(nt $SEED setautorepairconfig -t full min_repair_interval 5d 2>&1); rc=$?
if [ $rc -eq 0 ] && grep -q "Auto-repair is not enabled" <<<"$out"; then
  pass "$AR#switch-2-scheduling-reversible" "with the flag but scheduling off, set prints 'Auto-repair is not enabled' and exits 0"
else fail "$AR#switch-2-scheduling-reversible" "with the flag but scheduling off, set prints 'Auto-repair is not enabled' and exits 0" "rc=$rc: $out"; fi
check_contains "$AR#switch-2-scheduling-reversible" "...and getautorepairconfig prints the same" "Auto-repair is not enabled" nt $SEED getautorepairconfig

for n in cass1 cass2 cass3; do
  check_ok "$AR#switch-2-scheduling-reversible" "$n: setautorepairconfig start_scheduler true" nt $n setautorepairconfig start_scheduler true
done
check_enabled_ok "$AR" "getautorepairconfig works once scheduling is on" nt $SEED getautorepairconfig
check_contains   "$AR" "config lists the full repair type" "full" nt $SEED getautorepairconfig
check_enabled_ok "$AR" "autorepairstatus -t full" nt $SEED autorepairstatus -t full
check_enabled_ok "$AR" "setautorepairconfig -t full enabled true" nt $SEED setautorepairconfig -t full enabled true
check_enabled_ok "$AR" "setautorepairconfig -t full min_repair_interval 5d" nt $SEED setautorepairconfig -t full min_repair_interval 5d
check_contains   "$AR" "the new min_repair_interval is visible" "5d" nt $SEED getautorepairconfig
check_enabled_ok "$AR" "setautorepairconfig min_repair_task_duration 10s" nt $SEED setautorepairconfig min_repair_task_duration 10s

make_test_table arks events 10
check_ok "$AR" "ALTER TABLE ... WITH auto_repair = {'incremental_enabled': 'false'}" \
  cq $SEED "ALTER TABLE arks.events WITH auto_repair = {'incremental_enabled': 'false'};"
check_ok "$AR" "ALTER TABLE ... WITH auto_repair = {'priority': '3'}" \
  cq $SEED "ALTER TABLE arks.events WITH auto_repair = {'priority': '3'};"
unset JVM_EXTRA_OPTS_ALL
