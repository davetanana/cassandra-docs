---
name: validate-docs
description: Validate the Field Guide for Apache Cassandra 5.0 against a real Docker cluster in test_env/, triage failures as doc bugs or test bugs, fix them, and report. Use when asked to validate, test, verify, or update the docs, after editing doc pages, or when a new Cassandra 5.0.x release is out. Args: optional scenario numbers (e.g. "03 05"), a page path, or "release 5.0.N".
---

# validate-docs

Follow `test_env/AGENTS.md`. It is the source of truth for the ground rules. This skill picks the workflow.

1. **Pick the workflow from the argument:**
   - no argument → workflow A (everything)
   - scenario numbers → run only those
   - a doc page path → workflow B: `grep -l "<file name>" test_env/scenarios/*.sh` gives the scenarios to run
   - `release 5.0.N` → workflow C
2. **Preflight.**
   - `docker info` must succeed. If it doesn't, tell the user Docker isn't running and stop.
   - Check Docker memory: at least 6 GB, or 9 GB for scenarios 09 and 10.
   - If `test_env/.env` is missing, copy it from `.env.example` and tell the user which image tag is in use.
3. **Run.**
   - Use `test_env/scripts/run.sh [NN ...]` in the background; a full run takes 30–45 minutes.
   - Wait for it to exit. Don't poll the log in a tight loop.
4. **Triage every FAIL and WARN** in `test_env/results/LATEST.md` (full run) or `test_env/results/LAST_PARTIAL.md` (selected scenarios):
   - Read `results/<ts>/<scenario>.log`.
   - Reproduce by hand with `docker exec cass1 nodetool ...` or `docker exec cass1 cqlsh -e "..."`.
   - Decide **doc bug** or **test bug**, and fix the right one. Verify names and defaults against the Cassandra source (`$CASSANDRA_SRC`) when the disagreement is about one.
   - Re-run just that scenario until it passes.
5. **Report** to the user:
   - a table of the checks that failed, each with its cause, whether it was a doc bug or a test bug, and the files changed
   - anything that remains unresolved
   - the image and version that were tested
   - Don't claim a scenario passed unless the final run shows PASS.
6. **Leave the cluster running** unless the user asked for `--down`. Mention that `test_env/scripts/down.sh` removes it.
