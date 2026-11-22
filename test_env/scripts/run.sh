#!/usr/bin/env bash
# Run validation scenarios and write results/<timestamp>/, plus results/LATEST.md (full runs) or
# results/LAST_PARTIAL.md (runs of selected scenarios).
#
# Usage:
#   scripts/run.sh                 # all scenarios, in order
#   scripts/run.sh 02 04           # scenarios whose file name starts with 02 or 04
#   scripts/run.sh --down 07       # tear the cluster down afterwards
#
# Scenario header tags (first 15 lines of each scenarios/*.sh):
#   # DOC:      page(s) the scenario validates
#   # DIRTIES:  yes  -> the scenario changes topology/config, so the cluster is reset before the next scenario
#   # MANAGES_CLUSTER: yes -> the scenario starts and stops the cluster itself (runner doesn't pre-start it)
set -uo pipefail
ENV_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TEARDOWN=0
SELECT=()
for a in "$@"; do case "$a" in --down) TEARDOWN=1;; -h|--help) sed -n 2,13p "$0"; exit 0;; *) SELECT+=("$a");; esac; done

TS=$(date +%Y%m%d-%H%M%S)
OUT="$ENV_DIR/results/$TS"; mkdir -p "$OUT"
export RESULTS_FILE="$OUT/results.tsv"; : > "$RESULTS_FILE"
source "$ENV_DIR/scripts/lib.sh"
SCENARIO=runner

scenarios=()
for f in "$ENV_DIR"/scenarios/[0-9]*.sh; do
  b=$(basename "$f")
  if [ ${#SELECT[@]} -eq 0 ]; then scenarios+=("$f"); continue; fi
  for s in "${SELECT[@]}"; do [[ "$b" == "$s"* ]] && scenarios+=("$f"); done
done
[ ${#scenarios[@]} -eq 0 ] && { echo "no scenarios matched: ${SELECT[*]}"; exit 2; }

tag() { sed -n '1,15p' "$1" | sed -n "s/^# $2:[[:space:]]*//p" | head -1; }
running() { docker inspect -f '{{.State.Running}}' cass1 2>/dev/null | grep -q true; }

dirty=0; image=""; version=""
for f in "${scenarios[@]}"; do
  name=$(basename "${f%.sh}")
  if [ "$(tag "$f" MANAGES_CLUSTER)" != "yes" ]; then
    if [ "$dirty" = 1 ]; then reset_cluster; dirty=0
    elif ! running || [ "$(up_count)" != 3 ]; then reset_cluster; fi
  fi
  log "=== $name  ($(tag "$f" DOC))"
  start=$(date +%s)
  SCENARIO="$name" bash "$f" > "$OUT/$name.log" 2>&1
  rc=$?
  cat "$OUT/$name.log" | grep -E 'PASS|FAIL|WARN|SKIP' >&2 || true
  [ $rc -ne 0 ] && printf '%s\tFAIL\t%s\t%s\t%s\n' "$name" "$(tag "$f" DOC)" "scenario exited with code $rc" "see $name.log" >> "$RESULTS_FILE"
  log "=== $name finished in $(( $(date +%s) - start ))s (rc=$rc)"
  [ "$(tag "$f" DIRTIES)" = "yes" ] && dirty=1
  # Record the version while a node is up: later scenarios (12, 13) stop the 3-node cluster.
  if running; then
    image=$(docker inspect -f '{{.Config.Image}}' cass1 2>/dev/null)
    version=$(docker exec cass1 nodetool version 2>/dev/null | awk '{print $2}')
  fi
done

# ---- summary (capture the version before any teardown) ----
if running; then
  image=$(docker inspect -f '{{.Config.Image}}' cass1 2>/dev/null)
  version=$(docker exec cass1 nodetool version 2>/dev/null | awk '{print $2}')
fi
image=${image:-$CASSANDRA_IMAGE}
# Only standalone-container scenarios ran (12, 13, 14): take the version the official image declares.
if [ -z "$version" ]; then
  version=$(docker image inspect "$image" --format '{{range .Config.Env}}{{println .}}{{end}}' 2>/dev/null |
            sed -n 's/^CASSANDRA_VERSION=//p')
  [ -n "$version" ] && version="$version (from the image's CASSANDRA_VERSION)"
fi
[ "$TEARDOWN" = 1 ] && cluster_down
{
  echo "# Validation results ($TS)"
  echo
  echo "- Image: \`$image\`  Cassandra: \`${version:-unknown (cluster down)}\`"
  echo "- Docs commit: \`$(git -C "$ENV_DIR" rev-parse --short HEAD 2>/dev/null || echo n/a)\`"
  echo
  echo "| Scenario | PASS | FAIL | WARN | SKIP |"
  echo "|---|---|---|---|---|"
  awk -F'\t' '{c[$1","$2]++; s[$1]=1} END {for (k in s) printf "| %s | %d | %d | %d | %d |\n", k, c[k",PASS"], c[k",FAIL"], c[k",WARN"], c[k",SKIP"]}' "$RESULTS_FILE" | sort
  echo
  echo "## Failures and warnings (fix the doc or the test; see test_env/AGENTS.md)"
  echo
  awk -F'\t' '$2=="FAIL"||$2=="WARN" {printf "- **%s** `%s` %s: %s. %s\n", $2, $1, $3, $4, $5}' "$RESULTS_FILE"
} > "$OUT/summary.md"
# LATEST.md is the committed evidence for a release, so only a full run replaces it.
if [ ${#SELECT[@]} -eq 0 ]; then
  cp "$OUT/summary.md" "$ENV_DIR/results/LATEST.md"; cp "$RESULTS_FILE" "$ENV_DIR/results/LATEST.tsv"
else
  cp "$OUT/summary.md" "$ENV_DIR/results/LAST_PARTIAL.md"
  log "partial run: summary in results/LAST_PARTIAL.md (results/LATEST.md is only replaced by a full run)"
fi
cat "$OUT/summary.md"
! grep -q $'\tFAIL\t' "$RESULTS_FILE"
