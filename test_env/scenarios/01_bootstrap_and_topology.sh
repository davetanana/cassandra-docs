#!/usr/bin/env bash
# DOC: 05_cluster_deployment_and_config/02_cluster_deployment_runbook.md, 03_security_hardening.md
# CLAIMS: one-at-a-time bootstrap gives 3 UN nodes with 16 tokens each; one schema version;
#         GossipingPropertyFileSnitch DC/rack; system_auth defaults to SimpleStrategy RF 1 and the
#         runbook's ALTERs work; security ships disabled; statusbinary prints "running".
set -uo pipefail
source "$(dirname "$0")/../scripts/lib.sh"
require_nodes cass1 cass2 cass3
RB=05_cluster_deployment_and_config/02_cluster_deployment_runbook.md
SEC=05_cluster_deployment_and_config/03_security_hardening.md

check_equals "$RB#5" "3 nodes are UN after sequential bootstrap" 3 "$(up_count)"
for n in cass1 cass2 cass3; do
  ip=$(node_ip $n)
  check_equals "$RB#4" "$n owns num_tokens=16 tokens" 16 "$(nt $SEED ring | grep -c "^$ip ")"
  check_equals "$SEC" "$n: statusbinary prints 'running'" running "$(nt $n statusbinary | tr -d '[:space:]')"
done
check_equals "$RB#7" "describecluster shows a single schema version" 1 \
  "$(nt $SEED describecluster | sed -n '/Schema versions:/,/^$/p' | grep -c '\[')"
check_contains "$RB#4" "cass2 reports DC dc1 (GossipingPropertyFileSnitch)" "dc1" nt cass2 info
check_contains "$RB#4" "cass2 reports rack r2" "r2" nt cass2 info

check_contains "$SEC#1" "system_auth ships as SimpleStrategy" "SimpleStrategy" \
  cq $SEED "SELECT replication FROM system_schema.keyspaces WHERE keyspace_name='system_auth';"
check_contains "$SEC#2" "authenticator ships as AllowAllAuthenticator" "AllowAllAuthenticator" \
  cq $SEED "SELECT value FROM system_views.settings WHERE name='authenticator';"
check_contains "$RB#4" "allocate_tokens_for_local_replication_factor is 3" "3" \
  cq $SEED "SELECT value FROM system_views.settings WHERE name='allocate_tokens_for_local_replication_factor';"

for ks in system_auth system_distributed system_traces; do
  check_ok "$RB#6" "ALTER KEYSPACE $ks to NetworkTopologyStrategy dc1:3" \
    cq $SEED "ALTER KEYSPACE $ks WITH replication = {'class':'NetworkTopologyStrategy','dc1':3};"
done
check_contains "$SEC#1" "system_auth now replicated with NTS" "NetworkTopologyStrategy" \
  cq $SEED "SELECT replication FROM system_schema.keyspaces WHERE keyspace_name='system_auth';"
