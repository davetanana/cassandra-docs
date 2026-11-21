#!/usr/bin/env bash
# Start the 3-node dc1 cluster one node at a time, as the deployment runbook prescribes.
# Usage: scripts/up.sh            (cass1 -> cass2 -> cass3; compose depends_on waits for health)
set -euo pipefail
source "$(dirname "$0")/lib.sh"
SCENARIO=up
log "starting cass1, cass2, cass3 with ${CASSANDRA_IMAGE:-image from .env or cassandra:5.0} (this takes 3-5 minutes)"
"${COMPOSE[@]}" up -d --wait cass1 cass2 cass3
wait_un 3
nt "$SEED" status
log "cluster is up: $(nt "$SEED" version)"
