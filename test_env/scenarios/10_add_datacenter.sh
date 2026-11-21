#!/usr/bin/env bash
# DOC: 05_cluster_deployment_and_config/02_cluster_deployment_runbook.md (section 6, adding a datacenter)
# DIRTIES: yes
# CLAIMS: a new-DC node with auto_bootstrap: false joins holding no user data; after ALTER KEYSPACE adds
#         the DC, `nodetool rebuild <source-dc>` streams the existing data so LOCAL_ONE reads in dc2 succeed.
set -uo pipefail
source "$(dirname "$0")/../scripts/lib.sh"
require_nodes cass1 cass2 cass3
RB=05_cluster_deployment_and_config/02_cluster_deployment_runbook.md#6

make_test_table dcks t 100
"${COMPOSE[@]}" --profile dc2 up -d cass4 >/dev/null 2>&1
if wait_healthy cass4 900 && wait_un 4; then pass "$RB" "dc2 node joins and is UN"
else fail "$RB" "dc2 node joins" "$(docker logs --tail 40 cass4 2>&1)"; exit 0; fi
check_contains "$RB" "cass4 reports Datacenter dc2" "dc2" nt cass4 info
check_contains "$RB" "auto_bootstrap: false is in cass4's cassandra.yaml" "auto_bootstrap: false" docker exec cass4 grep '^auto_bootstrap' /etc/cassandra/cassandra.yaml

for ks in dcks system_auth system_distributed system_traces; do
  check_ok "$RB" "ALTER KEYSPACE $ks to add dc2" \
    cq $SEED "ALTER KEYSPACE $ks WITH replication = {'class':'NetworkTopologyStrategy','dc1':3,'dc2':1};"
done
check_ok "$RB" "nodetool rebuild dc1 on the new-DC node" nt cass4 rebuild dc1
got=$(cq_val cass4 "SELECT count(*) FROM dcks.t;" LOCAL_ONE)
check_equals "$RB" "LOCAL_ONE read in dc2 returns all 100 rows after rebuild" 100 "$got"
