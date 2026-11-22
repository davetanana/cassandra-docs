#!/usr/bin/env bash
# DOC: 03_application_development/05_querying_with_cql.md, 09_reference/05_cql_functions.md, 09_reference/06_cqlsh.md
#      (and any other page with "<!-- test: q:... -->", "sh:..." or "run:..." examples, except pages marked
#      "<!-- test-env: cluster -->", which scenario 15 runs on the 3-node cluster)
# CLAIMS: every example query in those pages prints exactly the output the page shows, including the exact
#         error text for refused queries; cqlsh shell commands, batch-mode exit codes and the scripting
#         recipes behave as shown; illustrative (time-dependent) examples run without errors.
# MANAGES_CLUSTER: yes
# DIRTIES: yes
# Runs on the quickstart's single node (datacenter1), started from the quickstart page itself.
set -uo pipefail
source "$(dirname "$0")/../scripts/lib.sh"
QS=00_getting_started/01_quickstart.md
QP=03_application_development/05_querying_with_cql.md
C=cass-quickstart

cluster_down >/dev/null 2>&1
docker rm -f "$C" >/dev/null 2>&1
bash -c "$(doc_block "$QS" start | sed "s#cassandra:5.0#$CASSANDRA_IMAGE#g")" >/dev/null
for _ in $(seq 1 60); do docker exec "$C" cqlsh -e 'DESCRIBE KEYSPACES' >/dev/null 2>&1 && break; sleep 5; done

# The sample data the other pages build on. Load it, then wait for the SAI indexes to finish building.
load_sample_data() { doc_block "$QP" run:examples-setup | docker exec -i "$C" cqlsh; }
check_ok "$QP#1-set-up-the-sample-data" "sample-data setup block runs" load_sample_data
for _ in $(seq 1 30); do
  doc_block "$QP" q:examples-indexes | docker exec -i "$C" cqlsh 2>&1 | grep -q False || break; sleep 2
done

# The pages in reading order (the functions and cqlsh pages use the data loaded above), then any other page
# that has tested examples.
pages="$QP 09_reference/05_cql_functions.md 09_reference/06_cqlsh.md"
for p in $(cd "$DOCS_DIR" && grep -rlE --include='*.md' --exclude-dir=.git --exclude-dir=build --exclude-dir=dist \
                 '^<!-- test: (q|sh|run):' . | sed 's#^\./##' | sort); do
  grep -qx '<!-- test-env: cluster -->' "$DOCS_DIR/$p" && continue   # those run on the 3-node cluster (scenario 15)
  case " $pages " in *" $p "*) ;; *) pages="$pages $p" ;; esac
done
for p in $pages; do
  log "examples in $p"
  ( cd "$DOCS_DIR" && check_doc_examples "$p" "$C" )   # sh: examples run from the repository root, as readers do
done

docker rm -f "$C" >/dev/null 2>&1
