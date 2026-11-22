#!/usr/bin/env bash
# DOC: 06_operations_and_housekeeping/01_nodetool_operations_guide.md, 02_housekeeping_and_automations.md
# CLAIMS: compact with no flags is a MAJOR compaction; a bare clearsnapshot is refused; -pr cannot be
#         combined with -dc; setconcurrency exists and setconcurrentreads does not; refresh is
#         deprecated; sample output field names; snapshot --ttl and clearsnapshot --older-than work;
#         setstreamthroughput takes megabits/s unless -m (MiB/s) is given.
set -uo pipefail
source "$(dirname "$0")/../scripts/lib.sh"
require_nodes cass1 cass2 cass3
NT=06_operations_and_housekeeping/01_nodetool_operations_guide.md
HK=06_operations_and_housekeeping/02_housekeeping_and_automations.md

make_test_table ntks t 50

check_contains "$HK#4" "bare 'nodetool clearsnapshot' is refused" "Specify snapshot name or --all" nt $SEED clearsnapshot
check_contains "$NT#4" "repair -pr combined with -dc is refused" "Primary range repair should be performed on all nodes" \
  nt $SEED repair -pr -dc dc1 ntks
check_ok       "$NT#7" "setconcurrency ReadStage 64 works" nt $SEED setconcurrency ReadStage 64
check_contains "$NT#7" "getconcurrency ReadStage shows 64" "64" nt $SEED getconcurrency ReadStage
nt $SEED setconcurrency ReadStage 32 >/dev/null 2>&1
if nt $SEED setconcurrentreads 64 >/dev/null 2>&1; then fail "$NT#7" "setconcurrentreads does not exist" "command succeeded"
else pass "$NT#7" "setconcurrentreads does not exist"; fi
check_contains "$NT#3" "refresh prints its deprecation notice" "deprecated" nt $SEED refresh ntks t
check_ok       "$NT#7" "settimeout read 5000" nt $SEED settimeout read 5000
check_contains "$NT#7" "gettimeout read shows 5000" "5000" nt $SEED gettimeout read
# setstreamthroughput takes megabits/s unless -m is given (SetStreamThroughput.java)
nt $SEED setstreamthroughput 100 >/dev/null 2>&1
check_contains "$NT#7" "setstreamthroughput 100 (no -m) means 100 megabits/s, about 11.9 MiB/s" "11.92" nt $SEED getstreamthroughput -m
check_ok       "$NT#7" "setstreamthroughput -m 100 sets MiB/s" nt $SEED setstreamthroughput -m 100
check_contains "$NT#7" "getstreamthroughput -m shows 100.0 MiB/s" "100.0 MiB/s" nt $SEED getstreamthroughput -m
check_contains "$NT#7" "setstreamthroughput -e sets the entire-SSTable cap in MiB/s" "100.0 MiB/s" \
  bash -c "docker exec $SEED nodetool setstreamthroughput -e 100 && docker exec $SEED nodetool getstreamthroughput -e"
nt $SEED setstreamthroughput -m 24 >/dev/null 2>&1; nt $SEED setstreamthroughput -e 24 >/dev/null 2>&1

check_contains "$NT#2" "tablestats field 'Compacted partition maximum bytes'" "Compacted partition maximum bytes" nt $SEED tablestats ntks.t
check_contains "$NT#2" "tablestats field 'Maximum tombstones per slice (last five minutes)'" \
  "Maximum tombstones per slice (last five minutes)" nt $SEED tablestats ntks.t
check_contains "$NT#2" "tpstats lists the MUTATION_REQ message type" "MUTATION_REQ" nt $SEED tpstats

# compact (no flags) = major: several SSTables become one
for i in 1 2 3; do
  cq $SEED "INSERT INTO ntks.t (id, v) VALUES ($((1000+i)), 'x');" ALL >/dev/null
  nt $SEED flush ntks t
done
before=$(nt $SEED tablestats ntks.t | awk -F: '/SSTable count/ {gsub(/ /,"",$2); print $2; exit}')
nt $SEED compact ntks t
sleep 2
after=$(nt $SEED tablestats ntks.t | awk -F: '/SSTable count/ {gsub(/ /,"",$2); print $2; exit}')
if [ "${before:-0}" -ge 2 ] && [ "${after:-9}" = 1 ]; then pass "$NT#3" "compact without flags is a major compaction ($before -> 1 SSTable)"
else fail "$NT#3" "compact without flags is a major compaction" "SSTables before=$before after=$after"; fi

check_ok "$NT#3" "garbagecollect -g CELL accepted" nt $SEED garbagecollect -g CELL ntks t
check_ok "$NT#5" "snapshot --ttl 1h" nt $SEED snapshot --ttl 1h -t ttl_test ntks
check_contains "$NT#5" "listsnapshots shows the ttl snapshot" "ttl_test" nt $SEED listsnapshots
check_ok "$HK#3" "clearsnapshot --all --older-than 30d" nt $SEED clearsnapshot --all --older-than 30d
check_contains "$NT#5" "--older-than without --all is refused" "Specify snapshot name or --all" nt $SEED clearsnapshot --older-than 30d
check_ok "$NT#5" "clearsnapshot -t ttl_test" nt $SEED clearsnapshot -t ttl_test
check_ok "$NT#4" "repair -pr -full on a keyspace" nt $SEED repair -pr -full ntks
check_ok "$NT#4" "repair -pr -local is allowed" nt $SEED repair -pr -local ntks
