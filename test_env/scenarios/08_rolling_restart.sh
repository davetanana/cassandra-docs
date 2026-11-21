#!/usr/bin/env bash
# DOC: 06_operations_and_housekeeping/02_housekeeping_and_automations.md (section 5),
#      03_application_development/04_consistency_and_transactions.md (DDM), 01_architecture_and_mental_model/02_anti_patterns.md (CL ALL)
# DIRTIES: yes
# CLAIMS: drain -> stop -> start, one node at a time, keeps QUORUM writes available; with one node down,
#         CL ALL fails while QUORUM succeeds; a yaml change applied during the rolling restart takes
#         effect (dynamic_data_masking_enabled: true makes MASKED WITH accepted).
set -uo pipefail
source "$(dirname "$0")/../scripts/lib.sh"
require_nodes cass1 cass2 cass3
HK=06_operations_and_housekeeping/02_housekeeping_and_automations.md#5
DDM=03_application_development/04_consistency_and_transactions.md#5-dynamic-data-masking-ddm-new-in-50
AP=01_architecture_and_mental_model/02_anti_patterns.md

make_test_table rrks t 0
written=0
for n in cass3 cass2 cass1; do
  other=cass1; [ "$n" = cass1 ] && other=cass2
  set_yaml "$n" dynamic_data_masking_enabled true
  nt "$n" drain >/dev/null 2>&1; docker stop -t 60 "$n" >/dev/null

  stmts=""; for i in $(seq 1 50); do stmts+="INSERT INTO rrks.t (id, v) VALUES ($((written+i)), 'good');"; done
  check_ok "$HK" "QUORUM writes succeed while $n is down" cq "$other" "$stmts" QUORUM
  written=$((written+50))
  out=$(cq "$other" "SELECT * FROM rrks.t WHERE id=1;" ALL 2>&1)
  if grep -qiE 'Unavailable|Error' <<<"$out"; then pass "$AP#8" "CL ALL fails while $n is down"
  else fail "$AP#8" "CL ALL fails while $n is down" "query succeeded: $out"; fi

  docker start "$n" >/dev/null
  wait_healthy "$n" && wait_un 3 && pass "$HK" "$n back to UN after drain/stop/start" || fail "$HK" "$n back to UN" "timeout"
done
check_equals "$HK" "all $written rows readable at CL ALL after the rolling restart" "$written" "$(count_value rrks t good)"
for n in cass1 cass2 cass3; do
  check_contains "$DDM" "$n: dynamic_data_masking_enabled=true after restart" "true" \
    cq $n "SELECT value FROM system_views.settings WHERE name='dynamic_data_masking_enabled';"
done
check_ok "$DDM" "MASKED WITH DEFAULT is accepted once DDM is enabled" \
  cq $SEED "CREATE TABLE rrks.masked (id int PRIMARY KEY, email text MASKED WITH DEFAULT);"
