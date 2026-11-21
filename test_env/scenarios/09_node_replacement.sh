#!/usr/bin/env bash
# DOC: 07_disaster_recovery/01_backup_and_disaster_recovery.md (section 1, dead node replacement)
# DIRTIES: yes
# CLAIMS: a non-seed node with empty data directories and -Dcassandra.replace_address_first_boot=<dead ip>
#         takes over the dead node's tokens at a NEW IP and streams its data; the dead IP leaves the ring;
#         leaving the flag set is harmless on later restarts (_first_boot is ignored after bootstrap).
set -uo pipefail
source "$(dirname "$0")/../scripts/lib.sh"
require_nodes cass1 cass2 cass3
DR=07_disaster_recovery/01_backup_and_disaster_recovery.md#1
OLD=$(node_ip cass3); NEW=$(node_ip cass3r)

make_test_table repks t 200
docker stop -t 30 cass3 >/dev/null   # simulate permanent hardware loss
for i in $(seq 1 60); do nt $SEED status | grep -q "^DN  *$OLD" && break; sleep 5; done
check_contains "$DR" "dead node shows DN" "DN" echo "$(nt $SEED status | grep "$OLD")"

"${COMPOSE[@]}" --profile replace up -d cass3r >/dev/null 2>&1
if wait_healthy cass3r 900; then pass "$DR" "replacement node started with replace_address_first_boot"
else fail "$DR" "replacement node started" "$(docker logs --tail 40 cass3r 2>&1)"; exit 0; fi
for i in $(seq 1 60); do nt $SEED status | grep -q "^UN  *$NEW" && ! nt $SEED status | grep -q " $OLD " && break; sleep 5; done

check_contains "$DR" "replacement is UN at the new IP" "UN" echo "$(nt $SEED status | grep "$NEW")"
if nt $SEED status | grep -q " $OLD "; then fail "$DR" "dead IP removed from the ring" "$OLD still listed"
else pass "$DR" "dead IP removed from the ring"; fi
check_equals "$DR" "replacement owns 16 tokens" 16 "$(nt $SEED ring | grep -c "^$NEW ")"
check_contains "$DR" "replacement keeps rack r3" "r3" nt cass3r info
check_equals "$DR" "all 200 rows readable at CL ALL" 200 "$(count_value repks t good)"
check_contains "$DR" "replacement logged that it is replacing the old address" "$OLD" echo "$(docker logs cass3r 2>&1 | grep -i replac)"

# Restart with the flag still present: should come back normally, not re-run a replacement
docker restart -t 60 cass3r >/dev/null
if wait_healthy cass3r 600 && wait_un 3 300; then pass "$DR" "restart with the flag still set is harmless (_first_boot ignored)"
else fail "$DR" "restart with the flag still set" "$(docker logs --tail 40 cass3r 2>&1)"; fi
