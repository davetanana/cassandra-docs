# AGENTS.md (test_env): Instructions for AI Agents Validating the Guide

You are validating and maintaining the **Field Guide for Apache Cassandra 5.0**: the markdown pages one level up. This folder runs the guide's claims against a real Docker cluster. Read [README.md](README.md) for the human-facing description, topology and scenario list.

This file applies to every agent: OpenAI Codex reads it directly, and Claude Code and Gemini CLI import it from `CLAUDE.md` and `GEMINI.md` in this folder. The repository-wide rules in [../AGENTS.md](../AGENTS.md) also apply.

## Ground rules

1. **The running cluster is the arbiter of behavior; the Cassandra source is the arbiter of names and defaults.** Neither your memory nor another doc site settles a disagreement. If a doc claim and a test result disagree, reproduce it by hand (`docker exec cass1 nodetool ...` / `cqlsh -e ...`) before you edit anything.
2. **A FAIL means the doc or the test is wrong. Decide which.**
   - If the test is wrong (bad assertion, timing, wrong expectation), fix the scenario and say why in your summary.
   - If the doc is wrong, fix the doc page and keep the test. The test is now a regression check for the corrected claim.
   - Never weaken an assertion just to make it pass. Never delete a failing check without telling the user what claim it covered.
3. **Every check carries a `doc_ref`** (`path/page.md#section`) so a failure leads straight to the text to fix. Keep these refs accurate when you move or rename doc sections.
4. **Keep the docs and the tests in sync in both directions.**
   - When you change a factual claim in a doc page (default, error text, command, procedure step), add or update a check here if it can be tested on a small cluster.
   - When a scenario reveals behavior the docs don't mention (a warning, a caveat, a version difference), add it to the relevant page.
5. **The cluster is disposable.** `scripts/down.sh` deletes all volumes. Never point these scripts at a real cluster. Never remove the `cassdocs` compose project name, the `172.30.0.0/24` network, or the hardcoded container names: the scripts depend on them.
6. **Don't publish secrets or personal data.** The S3 test credentials are fixed test values. Keep it that way.

## Standard workflows

### A. Validate everything (before a release, or after editing many pages)
```bash
cd test_env && scripts/run.sh --down        # 30-45 min; run it in the background and wait for it to exit
cat results/LATEST.md
```
For each FAIL: open `results/<ts>/<scenario>.log`, reproduce by hand, then classify it as a doc bug or a test bug (ground rule 2). Re-run only the affected scenario, e.g. `scripts/run.sh 05`, and read `results/LAST_PARTIAL.md`. Partial runs never overwrite `LATEST.md`. Finish with a short report listing each failure, its cause, and the files you changed.

### B. Validate one page you just edited
1. Find the scenarios that cover it: `grep -l "<page file name>" scenarios/*.sh`.
2. `scripts/up.sh` (skip if cass1–cass3 are already UN), then `scripts/run.sh <NN> ...`.
3. If no scenario covers the claim you changed, add checks (workflow D).

### C. New Cassandra 5.0.x release
1. Set `CASSANDRA_IMAGE=cassandra:5.0.<new>` and `CASSANDRA_SRC=<checkout of that tag>` in `.env`.
2. Regenerate the reference pages from the repository root:
   ```bash
   python3 tools/gen_yaml_reference.py     "$CASSANDRA_SRC" -o 09_reference/01_cassandra_yaml_reference.md
   python3 tools/gen_nodetool_reference.py "$CASSANDRA_SRC" -o 09_reference/02_nodetool_reference.md
   python3 tools/check_docs.py "$CASSANDRA_SRC" && python3 tools/check_links.py
   ```
3. Read the new release's sections in `NEWS.txt` and `CHANGES.txt`. List anything that affects claims in the guide.
4. Run workflow A. Fix the docs.
5. Update the "Version scope" line in `../README.md` and rule 1 in `../AI_USAGE.md` (and the matching line in `../AGENTS.md`). Then run `python3 tools/build_ai_bundle.py`.
6. If a run turns up a new trap (behavior that surprises operators), add it to rule 6 in `../AI_USAGE.md` and to the "Real doc bugs" list below.

### D. Add a check or a scenario
- **Small factual claim** (a default, an error, a syntax point):
  - CQL behavior goes in `scenarios/03_cql_claims.sh` as a `claim` line.
  - Defaults visible in `system_views.settings` go in the here-doc table in `scenarios/02_config_defaults.sh`.
  - nodetool behavior goes in `scenarios/04_nodetool_claims.sh`.
- **A procedure** (multi-step runbook): create `scenarios/NN_name.sh` from the closest existing one.
  - Header tags:
    - `# DOC:` (pages covered)
    - `# CLAIMS:` (plain-English list)
    - `# DIRTIES: yes` if it changes topology or config
    - `# MANAGES_CLUSTER: yes` if it starts or stops the cluster itself
  - Use the helpers in `scripts/lib.sh`: `cq`, `cq_val`, `nt`, `wait_un`, `wait_healthy`, `table_dir`, `set_yaml`, `make_test_table`, `count_value`, `doc_block`, `doc_result`, `check_doc_examples`, `check_*`.
  - Run the commands **exactly as the doc shows them** where possible (same flags, same order). The point is to test the doc, not an idealized version of it.
  - Better still, read them from the page: put `<!-- test: NAME -->` on the line before a fenced code block, and use `doc_block <page> NAME` in the scenario (see scenarios 12 and 13). Then the page and the test can't drift apart. Don't rename a marker without updating its scenario.
- **An example query with its output** (no scenario code needed): put the query in a fenced block after `<!-- test: q:NAME -->`, and the output `cqlsh` prints in a second fenced block (`text`) right after it. Scenario 14 finds every such marker in every page, runs the query on the quickstart node with the `examples` sample data, and compares the output. Leading and trailing blank lines, trailing spaces and the `<stdin>:N:` error prefix are ignored; everything else must match.
  - `sh:NAME` does the same for a bash block run on the host (the container is `cass-quickstart`).
  - Examples that need the 3-node cluster (for example `docker exec cass1 ...`) go in a page with the line `<!-- test-env: cluster -->`. Scenario 15 runs those pages on the cluster from `test_env/`, and scenario 14 skips them.
  - `run:NAME` only checks that the block runs without `Error` or `Exception`. Use it when the output changes from run to run (times, UUIDs, versions, `COPY` row order), and label any output you show as illustrative.
  - Write the expected output by running the query, never by hand. Make outputs deterministic: fixed `USING TIMESTAMP`, a `WHERE` that fixes the row set, and no `now()` in compared examples.
  - Create your own keyspace. Don't depend on other scenarios.
  - Bash must run on macOS `/bin/bash` 3.2: no associative arrays, no `mapfile`, no `${var,,}`.
- Add the scenario to the table in `README.md` and remove it from the "Not yet automated" list if it covers something there.

## Pitfalls seen while building this

- `cqlsh` exits non-zero on most errors but not all. `claim`/`check_*` also look for `Error` in the output. Use `cq_val` to extract a single value.
- In the official image, data lives in `/var/lib/cassandra/data`. The docs use `/mnt/cassandra/data`; pass paths as variables.
- `docker exec` runs as root. Files you stage for `nodetool import` must be `chown cassandra:cassandra`.
- `nodetool import` *moves* files by default, so re-stage before importing again.
- After `docker stop`, gossip takes 10–30 s to mark a node DN. Poll; don't sleep a fixed time.
- 5-node scenarios need about 9 GB of Docker memory. "Exited (137)" means the container ran out of memory.
- **Docker Hub lags upstream.** On 2026-11-21, `cassandra:5.0` was **5.0.9** and there was no `5.0.10` tag. Results record the version actually tested. Build from source (README) to test a newer one.
- **S3 target:** MinIO's community images are no longer on Docker Hub, so this uses Adobe S3Mock. AWS CLI 2.15 and 2.27 fail against it with "Connection was closed"; 2.42.1 works. Keep both pinned.
- **Commands that exit 0 without doing anything.** The auto-repair commands print "Auto-repair is not enabled" and exit 0 when scheduling is off. Assert on output, not on the exit code (see `check_enabled_ok` in scenario 11).
- **Real doc bugs this environment caught on its first run.** Keep these as regression checks:
  - a 20-year TTL is rejected under `storage_compatibility_mode: CASSANDRA_4` (the expiry passes 2038)
  - `clearsnapshot --older-than` requires `--all`
  - without the JVM flag, `getautorepairconfig` fails with "Server is not initialized yet"
  - `getautorepairconfig` hides a repair type's settings until that type is enabled
  - a query sent right after `CREATE INDEX ... USING 'sai'` fails with `INDEX_NOT_AVAILABLE`: the index builds in the background (caught by scenario 12)
- **Behavior found while writing the scenario 14 examples** (each is now a compared example):
  - a timestamp string without a zone is parsed in the coordinator's time zone, not UTC
  - `floor(ts, 1w)` without a start argument gives weeks starting on Thursday (the epoch's weekday)
  - `avg()` and `collection_avg()` of an integer column are truncated to an integer
  - cqlsh in batch mode (`-e`, `-f`, piped input) keeps going after a failed statement and exits 2 at the end
  - `cast()` of a bare constant in the select list is refused ("Cannot infer type"); use a type hint such as `(double)2`
- **Found while measuring SAI for the capacity-planning page:** a vector index made rewriting the same SSTables about 100 times slower (251 s against 3 s for 200,000 rows), and `cassandra-stress` (5.0.9) can't read `vector` types: it logs a parse error for any vector table on the cluster, and a profile with a vector column fails with "Unable to find table". The page's stress example sends stderr to a log for that reason.
- **Found while writing the capacity-planning page:** `nodetool setstreamthroughput <n>` takes megabits/s unless `-m` is given. The nodetool guide said MiB/s. Now a check in scenario 04.

## Files

| Path | Purpose |
|---|---|
| `docker-compose.yml` | cluster definition (profiles: `replace`, `dc2`, `s3`) |
| `.env.example` | image pin, heap, `CASSANDRA_SRC` |
| `scripts/lib.sh` | helpers and result recording |
| `scripts/up.sh`, `down.sh`, `run.sh` | lifecycle and runner |
| `scenarios/NN_*.sh` | one file per area of the guide; `14_query_examples.sh` runs the `q:`/`sh:`/`run:` examples in every page on the quickstart node, `15_cluster_tutorials.sh` those in pages marked `<!-- test-env: cluster -->` on the 3-node cluster |
| `config/` | yaml fragments mounted read-only at `/test_config` (use `apply_yaml`) |
| `shared/` | mounted at `/shared` in every node, for staging |
| `results/` | run outputs; `LATEST.md` is the latest **full** run (committed per release); `LAST_PARTIAL.md` is the latest run of selected scenarios |
| `AGENTS.md` (this file), `CLAUDE.md`, `GEMINI.md` | agent instructions; the latter two import this file |
| `../.claude/skills/validate-docs/SKILL.md` | `/validate-docs` for Claude Code |
| `../.gemini/commands/validate-docs.toml` | `/validate-docs` for Gemini CLI |
| `../.github/workflows/validate.yml` | manual or scheduled CI run of these scenarios |
