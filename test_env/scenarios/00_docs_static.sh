#!/usr/bin/env bash
# DOC: all pages (static checks; no cluster needed)
# MANAGES_CLUSTER: yes
# CLAIMS: every full shell script in the docs parses; shellcheck finds no errors; yaml keys and
#         nodetool commands named in the docs exist in the Cassandra source (needs CASSANDRA_SRC)
set -uo pipefail
source "$(dirname "$0")/../scripts/lib.sh"

work=$(mktemp -d)
# Extract fenced ```bash blocks. Only blocks that start with a shebang are complete scripts; check those strictly.
python3 - "$DOCS_DIR" "$work" <<'EOF'
import re, sys, pathlib
docs, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
for md in sorted(docs.rglob("*.md")):
    if "test_env" in md.parts: continue
    for i, m in enumerate(re.finditer(r"```(?:bash|sh)\n(.*?)```", md.read_text(), re.S)):
        body = m.group(1)
        if body.lstrip().startswith("#!"):
            name = f"{md.relative_to(docs).as_posix().replace('/', '__')}__{i}.sh"
            (out / name).write_text(body)
EOF

n=0
for s in "$work"/*.sh; do
  [ -e "$s" ] || break; n=$((n+1))
  ref=$(basename "$s" | sed 's/__[0-9]*\.sh$//; s/__/\//g')
  check_ok "$ref" "script parses (bash -n): $(head -3 "$s" | grep -oE '/[A-Za-z0-9_./-]+\.sh' | head -1)" bash -n "$s"
  if command -v shellcheck >/dev/null; then
    check_ok "$ref" "shellcheck -S error: $(basename "$s")" shellcheck -S error -s bash "$s"
  fi
done
[ "$n" -eq 0 ] && warn "docs" "no complete scripts found to check"
command -v shellcheck >/dev/null || skip "docs" "shellcheck" "install shellcheck for deeper script checks"

if [ -n "${CASSANDRA_SRC:-}" ] && [ -f "$CASSANDRA_SRC/build.xml" ]; then
  check_contains "docs" "tools/check_docs.py finds 0 errors against $CASSANDRA_SRC" "0 error(s)" \
    python3 "$DOCS_DIR/tools/check_docs.py" "$CASSANDRA_SRC"
else
  skip "docs" "tools/check_docs.py" "set CASSANDRA_SRC in .env to an apache/cassandra checkout"
fi
rm -rf "$work"
