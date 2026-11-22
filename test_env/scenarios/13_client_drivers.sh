#!/usr/bin/env bash
# DOC: 03_application_development/03_client_drivers.md
# CLAIMS: the Go (gocql v2) and Node.js examples in section 7 compile and run as written against the
#         quickstart node and print the documented line; the Node.js driver refuses to connect without
#         localDataCenter.
# MANAGES_CLUSTER: yes
# DIRTIES: yes
# Uses the quickstart page's own start/schema blocks for the data, and the drivers page's code blocks.
set -uo pipefail
source "$(dirname "$0")/../scripts/lib.sh"
QS=00_getting_started/01_quickstart.md
DRV=03_application_development/03_client_drivers.md
S7="$DRV#7-python-go-and-nodejs-same-rules-different-defaults"
C=cass-quickstart
GO_IMAGE="${GO_IMAGE:-golang:1.23}"
NODE_IMAGE="${NODE_IMAGE:-node:22-slim}"
WORK="$ENV_DIR/shared/drivers"

cluster_down >/dev/null 2>&1
docker rm -f "$C" >/dev/null 2>&1
rm -rf "$WORK"; mkdir -p "$WORK/go" "$WORK/node"

bash -c "$(doc_block "$QS" start | sed "s#cassandra:5.0#$CASSANDRA_IMAGE#g")" >/dev/null
for _ in $(seq 1 60); do docker exec "$C" cqlsh -e 'DESCRIBE KEYSPACES' >/dev/null 2>&1 && break; sleep 5; done
doc_block "$QS" schema | docker exec -i "$C" cqlsh >/dev/null 2>&1 \
  || { fail "$QS#3-create-a-keyspace-and-a-table" "quickstart schema loads (prerequisite)" "cqlsh failed"; docker rm -f "$C" >/dev/null; exit 1; }

for b in go nodejs; do
  [ -n "$(doc_block "$DRV" $b)" ] || fail "$DRV" "page has a '<!-- test: $b -->' code block" "marker or block missing"
done

# Go: the page's install command, then its program.
doc_block "$DRV" go > "$WORK/go/main.go"
out=$(docker run --rm --network "container:$C" -v "$WORK/go:/src" -w /src "$GO_IMAGE" sh -c \
  'go mod init example.com/quickstart >/dev/null 2>&1 && go get github.com/apache/cassandra-gocql-driver/v2 >/dev/null 2>&1 && go run .' 2>&1)
check_contains "$S7" "Go example (gocql v2) runs and prints the documented line" "latest reading for s-1: 26.5" echo "$out"

# Node.js: the page's install command, then its program.
doc_block "$DRV" nodejs > "$WORK/node/index.js"
cat > "$WORK/node/no_dc.js" <<'EOF'
const cassandra = require('cassandra-driver');
const client = new cassandra.Client({ contactPoints: ['127.0.0.1'] });
client.connect().then(() => { console.log('connected without localDataCenter'); return client.shutdown(); })
  .catch((err) => { console.log(String(err.message)); return client.shutdown(); });
EOF
out=$(docker run --rm --network "container:$C" -v "$WORK/node:/app" -w /app "$NODE_IMAGE" sh -c \
  'npm install --silent --no-audit --no-fund cassandra-driver >/dev/null 2>&1 && node index.js && node no_dc.js' 2>&1)
check_contains "$S7" "Node.js example runs and prints the documented line" "latest reading for s-1: 26.5" echo "$out"
check_contains "$S7" "Node.js driver refuses to connect without localDataCenter" "'localDataCenter' is not defined in Client options" echo "$out"

rm -rf "$WORK"
docker rm -f "$C" >/dev/null 2>&1
