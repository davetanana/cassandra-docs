#!/usr/bin/env bash
# DOC: 00_getting_started/03_tutorial_operations.md (and any other page marked "<!-- test-env: cluster -->")
# DIRTIES: yes
# CLAIMS: the operations tutorial runs as written on the 3-node cluster and prints what it shows: status and
#         replica placement, QUORUM working and ALL refused with one node down, a hint file kept and then
#         replayed, repair, snapshots on every node, TRUNCATE's automatic snapshot, and the import restore.
set -uo pipefail
source "$(dirname "$0")/../scripts/lib.sh"
require_nodes cass1 cass2 cass3
wait_un 3

# A rerun on the same cluster starts from a clean keyspace.
cq cass1 "DROP KEYSPACE IF EXISTS drill;" >/dev/null 2>&1
for n in cass1 cass2 cass3; do nt "$n" clearsnapshot --all drill >/dev/null 2>&1; done

for p in $(cd "$DOCS_DIR" && grep -rlx --include='*.md' --exclude-dir=.git --exclude-dir=build --exclude-dir=dist \
             '<!-- test-env: cluster -->' . | sed 's#^\./##' | sort); do
  log "examples in $p"
  ( cd "$ENV_DIR" && check_doc_examples "$p" cass1 )
done

docker start cass3 >/dev/null 2>&1   # in case a failed step left it stopped; the runner resets the cluster anyway
