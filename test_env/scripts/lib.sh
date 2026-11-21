#!/usr/bin/env bash
# Shared helpers for the validation scenarios. Source this file; don't execute it.
# Every check records one row in $RESULTS_FILE:  scenario <TAB> status <TAB> doc_ref <TAB> check <TAB> detail

ENV_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DOCS_DIR="$(cd "$ENV_DIR/.." && pwd)"
COMPOSE=(docker compose --project-directory "$ENV_DIR" -f "$ENV_DIR/docker-compose.yml")
if [ -f "$ENV_DIR/.env" ]; then COMPOSE+=(--env-file "$ENV_DIR/.env"); set -a; source "$ENV_DIR/.env"; set +a; fi
CASSANDRA_IMAGE="${CASSANDRA_IMAGE:-cassandra:5.0}"; export CASSANDRA_IMAGE

SCENARIO="${SCENARIO:-$(basename "${0%.sh}")}"
RESULTS_FILE="${RESULTS_FILE:-$ENV_DIR/results/adhoc.tsv}"
mkdir -p "$(dirname "$RESULTS_FILE")" "$ENV_DIR/shared"

DATA=/var/lib/cassandra/data      # data_file_directories inside the official image
SEED=cass1

node_ip() {   # bash 3.2 compatible (macOS /bin/bash): no associative arrays
  case "$1" in cass1) echo 172.30.0.11;; cass2) echo 172.30.0.12;; cass3) echo 172.30.0.13;;
               cass3r) echo 172.30.0.23;; cass4) echo 172.30.0.21;; esac
}

log()  { printf '\033[1;34m[%s]\033[0m %s\n' "$SCENARIO" "$*" >&2; }
_rec() { printf '%s\t%s\t%s\t%s\t%s\n' "$SCENARIO" "$1" "$2" "$3" "$(printf '%s' "$4" | tr '\t\n' '  ' | cut -c1-300)" >> "$RESULTS_FILE"; }
pass() { _rec PASS "$1" "$2" "${3:-}"; printf '  \033[32mPASS\033[0m %s\n' "$2" >&2; }
fail() { _rec FAIL "$1" "$2" "${3:-}"; printf '  \033[31mFAIL\033[0m %s -- %s\n' "$2" "${3:-}" >&2; }
warn() { _rec WARN "$1" "$2" "${3:-}"; printf '  \033[33mWARN\033[0m %s -- %s\n' "$2" "${3:-}" >&2; }
skip() { _rec SKIP "$1" "$2" "${3:-}"; printf '  SKIP %s -- %s\n' "$2" "${3:-}" >&2; }

# check_ok DOC_REF "description" cmd...           -> PASS if cmd exits 0
check_ok() {
  local ref="$1" desc="$2"; shift 2; local out
  if out=$("$@" 2>&1); then pass "$ref" "$desc"; else fail "$ref" "$desc" "$out"; fi
}
# check_contains DOC_REF "description" "needle" cmd...   -> PASS if output contains needle (exit code ignored)
check_contains() {
  local ref="$1" desc="$2" needle="$3"; shift 3; local out
  out=$("$@" 2>&1)
  if grep -qF -- "$needle" <<<"$out"; then pass "$ref" "$desc"; else fail "$ref" "$desc" "expected '$needle' in: $out"; fi
}
# check_equals DOC_REF "description" expected actual
check_equals() {
  if [ "$3" == "$4" ]; then pass "$1" "$2"; else fail "$1" "$2" "expected '$3', got '$4'"; fi
}

nt()  { local n="$1"; shift; docker exec "$n" nodetool "$@"; }
# cq NODE "CQL" [CONSISTENCY]   runs cqlsh inside NODE; prints output, returns cqlsh's exit code
cq()  { local n="$1" q="$2" cl="${3:-}"; [ -n "$cl" ] && q="CONSISTENCY $cl; $q"; docker exec "$n" cqlsh --no-color -e "$q"; }
# cq_val NODE "SELECT single_value ..." [CL] -> prints the first data value only
cq_val() { cq "$@" | awk 'f && NF && !/^\(/ {gsub(/^ +| +$/,""); print; exit} /^-+/ {f=1}'; }

up_count() { nt "$SEED" status 2>/dev/null | grep -c '^UN' || true; }

# wait_un N [timeout_s]   wait until N nodes report UN (as seen from the seed)
wait_un() {
  local want="$1" t="${2:-600}" i=0
  while [ "$(up_count)" != "$want" ]; do
    (( i += 5 )); [ "$i" -ge "$t" ] && { log "timeout waiting for $want UN nodes"; nt "$SEED" status >&2; return 1; }
    sleep 5
  done
}
wait_healthy() {
  local n="$1" t="${2:-600}" i=0
  until [ "$(docker inspect -f '{{.State.Health.Status}}' "$n" 2>/dev/null)" == "healthy" ]; do
    (( i += 5 )); [ "$i" -ge "$t" ] && { log "timeout waiting for $n healthy"; return 1; }
    sleep 5
  done
}

cluster_up()   { "$ENV_DIR/scripts/up.sh"; }
cluster_down() { "$ENV_DIR/scripts/down.sh"; }
reset_cluster() { log "resetting cluster (all data is discarded)"; cluster_down && cluster_up; }

# set_yaml NODE key value : replace a top-level scalar key (or append it if absent). Restart to apply.
set_yaml() {
  docker exec "$1" bash -c "f=/etc/cassandra/cassandra.yaml; if grep -qE '^$2:' \$f; then sed -i -E 's|^$2:.*|$2: $3|' \$f; else echo '$2: $3' >> \$f; fi"
}
# apply_yaml NODE fragment.yaml : append a block from test_env/config/ (only for keys that are commented out by default)
apply_yaml() { docker exec "$1" bash -c "cat /test_config/$2 >> /etc/cassandra/cassandra.yaml"; }

# restart_node NODE : the documented sequence (drain, stop, start), then wait for health and UN
restart_node() {
  local n="$1" total; total=$(up_count)
  nt "$n" drain >/dev/null 2>&1 || true
  docker stop -t 60 "$n" >/dev/null && docker start "$n" >/dev/null
  wait_healthy "$n" && wait_un "$total"
}

# table_dir NODE ks table : resolve the live table directory from its id (no globs)
table_dir() {
  local id
  id=$(cq_val "$1" "SELECT id FROM system_schema.tables WHERE keyspace_name='$2' AND table_name='$3';" | tr -d '-')
  [ -n "$id" ] && echo "$DATA/$2/$3-$id"
}

# make_test_table ks table rows : RF3 keyspace, simple table, N rows with v='good'
make_test_table() {
  local ks="$1" t="$2" n="${3:-100}" i stmts=""
  cq "$SEED" "CREATE KEYSPACE IF NOT EXISTS $ks WITH replication = {'class':'NetworkTopologyStrategy','dc1':3};
              CREATE TABLE IF NOT EXISTS $ks.$t (id int PRIMARY KEY, v text);" >/dev/null
  for ((i=0;i<n;i++)); do stmts+="INSERT INTO $ks.$t (id, v) VALUES ($i, 'good');"; done
  cq "$SEED" "$stmts" ALL >/dev/null
}
count_value() { cq_val "$SEED" "SELECT count(*) FROM $1.$2 WHERE v='$3' ALLOW FILTERING;" ALL; }

require_nodes() {
  for n in "$@"; do
    docker inspect -f '{{.State.Running}}' "$n" 2>/dev/null | grep -q true || { log "node $n is not running; run scripts/up.sh"; exit 3; }
  done
}
