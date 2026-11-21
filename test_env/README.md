# Test Environment: Validating the Field Guide Against a Real Cluster

The pages in this guide make hundreds of factual claims: defaults, error messages, command syntax, and multi-step runbooks. `tools/check_docs.py` checks names against the source code. **This folder checks behavior.** It runs claims and procedures against a small Docker cluster and records PASS/FAIL per claim, each with a link to the page it came from.

It is deliberately small: 3 nodes on a laptop, with optional extra nodes for the replacement and multi-DC scenarios. It proves that commands, defaults and procedures work as written. It does **not** prove anything about performance, cloud-provider behavior, or scale.

---

## Quick start

```bash
cd test_env
cp .env.example .env          # optional: pin CASSANDRA_IMAGE to an exact 5.0.x tag
scripts/up.sh                 # 3 nodes, started one at a time (3-5 minutes)
scripts/run.sh                # every scenario; about 30-45 minutes because some reset the cluster
cat results/LATEST.md         # summary, with failures linked to doc pages
scripts/down.sh               # remove containers AND volumes
```

Run a subset by number prefix: `scripts/run.sh 03 05`. Add `--down` to tear down afterwards.

**Requirements:**
- Docker with Compose v2.
- At least **6 GB** of Docker memory for 3 nodes, or **9 GB** for scenarios 09 and 10, which add a 4th node.
- Linux/amd64 or arm64 (the official `cassandra` image is multi-arch).
- `python3` for scenario 00, and optionally `shellcheck`.

## Topology

| Container | IP | DC / rack | Role | Started by |
|---|---|---|---|---|
| cass1 | 172.30.0.11 | dc1 / r1 | seed | `up.sh` |
| cass2 | 172.30.0.12 | dc1 / r2 | seed | `up.sh` (after cass1 is healthy) |
| cass3 | 172.30.0.13 | dc1 / r3 | non-seed | `up.sh` (after cass2 is healthy) |
| cass3r | 172.30.0.23 | dc1 / r3 | replacement for cass3 at a new IP | scenario 09 (`--profile replace`) |
| cass4 | 172.30.0.21 | dc2 / r1 | new datacenter, `auto_bootstrap: false` | scenario 10 (`--profile dc2`) |
| s3mock | 172.30.0.40:9090 | n/a | S3-compatible backup target | scenario 07 (`--profile s3`) |

Every node uses `GossipingPropertyFileSnitch`, `num_tokens: 16`, and otherwise the image's shipped `cassandra.yaml`. The container's `/shared` maps to `test_env/shared/` for staging files.

## Scenarios

| # | Scenario | Validates | Changes the cluster? |
|---|---|---|---|
| 00 | `docs_static` | Every complete shell script in the docs parses (`bash -n`, and `shellcheck` if installed); runs `tools/check_docs.py` if `CASSANDRA_SRC` is set | no cluster needed |
| 01 | `bootstrap_and_topology` | Deployment runbook: sequential bootstrap, 16 tokens, one schema version, snitch DC/rack, `system_auth` defaults and the ALTERs | no |
| 02 | `config_defaults` | About 25 default values quoted in the docs, read from `system_views.settings` | no |
| 03 | `cql_claims` | SAI vs legacy index, operator limits, analyzer options, ANN rules, masking functions, DDM off by default, TTL limit, batch limit, grammar, table defaults | no |
| 04 | `nodetool_claims` | `compact` is major; bare `clearsnapshot` is refused; `-pr` + `-dc` is refused; `setconcurrency`; `refresh` is deprecated; output field names; snapshot TTL and age options | no |
| 05 | `restore_import` | DR rule 0 (restoring an old snapshot doesn't undo newer writes), TRUNCATE + `nodetool import` on every replica | no |
| 06 | `dropped_table_restore` | The `dropped-*` snapshot, `schema.cql` with `ID =`, re-creating into the same directory, import | no |
| 07 | `s3_backup_include_pattern` | The documented `aws s3 sync --include "*/snapshots/${TAG}/*"` uploads only the current tag (S3Mock) | no |
| 08 | `rolling_restart` | drain → stop → start keeps QUORUM writes available; CL ALL fails while a node is down; a yaml change applied during the roll takes effect | **yes** |
| 09 | `node_replacement` | `replace_address_first_boot` at a new IP: tokens, rack and data taken over; old IP removed; flag harmless on restart | **yes** |
| 10 | `add_datacenter` | `auto_bootstrap: false`, system keyspace ALTERs, `nodetool rebuild dc1`, LOCAL_ONE reads in dc2 | **yes** |
| 11 | `auto_repair` | The "not enabled" message without the JVM flag; with it, the documented `nodetool` auto-repair commands and table options work | **yes** (restarts with a JVM flag) |

The runner resets the cluster (`down -v` then `up`) after any scenario that changes it, so scenarios never depend on each other.

## Reading results

`scripts/run.sh` writes `results/<timestamp>/`:
- `results.tsv`: one row per check, with the columns `scenario`, `status`, `doc_ref`, `check` and `detail`.
- `<scenario>.log`: the full output of each scenario.
- `summary.md`. A full run also copies it to `results/LATEST.md` (with `LATEST.tsv`). A run of selected scenarios copies it to `results/LAST_PARTIAL.md` instead, so the committed full-run evidence in `LATEST.md` is never replaced by a partial run.

Statuses:
- **PASS**: the doc's claim held on a real node.
- **FAIL**: the claim didn't hold. **Either the doc or the test is wrong.** Work out which before changing anything (see [AGENTS.md](AGENTS.md)).
- **WARN**: the claim couldn't be checked (for example, the setting isn't exposed in a virtual table).
- **SKIP**: a prerequisite was missing (shellcheck, or `CASSANDRA_SRC`).

`results/` is git-ignored, except that you may commit `results/LATEST.md` for a release as evidence of what was validated.

## Updating the docs after a new 5.0.x release

1. In `.env`, set `CASSANDRA_IMAGE=cassandra:5.0.<new>`. Set `CASSANDRA_SRC` to a checkout of that tag.
2. From the repository root, regenerate the reference pages and run the static checks (see [tools/README.md](../tools/README.md)):
   ```bash
   python3 tools/gen_yaml_reference.py     "$CASSANDRA_SRC" -o 09_reference/01_cassandra_yaml_reference.md
   python3 tools/gen_nodetool_reference.py "$CASSANDRA_SRC" -o 09_reference/02_nodetool_reference.md
   python3 tools/check_docs.py "$CASSANDRA_SRC" && python3 tools/check_links.py
   ```
3. Run `scripts/down.sh && scripts/run.sh --down`.
4. Fix each FAIL in the doc (or in the test, if the test was wrong), and re-run that scenario.
5. Update the "Version scope" line in the top-level [README.md](../README.md) and rule 1 in [AI_USAGE.md](../AI_USAGE.md). Run `python3 tools/build_ai_bundle.py`, then commit `results/LATEST.md`.

The summary records the image and the Cassandra version that was actually running (`nodetool version`). It captures them before `--down` tears the cluster down, so the version shown is the one tested, even when the image tag (such as `cassandra:5.0`) doesn't name a version.

## Running it with an AI assistant

The rules and workflows for agents are in [AGENTS.md](AGENTS.md). OpenAI Codex reads that file directly; Claude Code and Gemini CLI import it from [CLAUDE.md](CLAUDE.md) and [GEMINI.md](GEMINI.md). Start the agent from the repository root, then:

| Tool | Command |
| :--- | :--- |
| Claude Code | `/validate-docs`, `/validate-docs 03 05`, `/validate-docs 06_operations_and_housekeeping/06_auto_repair.md`, `/validate-docs release 5.0.11` |
| Gemini CLI | `/validate-docs` with the same arguments |
| Codex and other tools | "Validate the docs following test_env/AGENTS.md workflow A" (or B for one page, C for a new release) |

The key rule: when a check fails, the agent must decide whether the **doc** or the **test** is wrong, fix that one, and never weaken an assertion to make a check pass.

## Running it in CI

[`.github/workflows/validate.yml`](../.github/workflows/validate.yml) runs these scenarios on a GitHub-hosted runner. In a public repository the standard Linux runner has 16 GB of memory, which is enough for every scenario. In a private repository it has 7 GB, which is enough for every scenario except 09 and 10. It runs on manual dispatch, where you can choose the scenarios and the image, and once a month on a schedule. It uploads `results/` as a build artifact. The faster static checks run on every pull request in [`.github/workflows/docs.yml`](../.github/workflows/docs.yml).

## Testing a source build instead of the Docker Hub image

To validate an unreleased branch:
1. Build the tarball in the Cassandra checkout with `ant artifacts`. It lands at `build/apache-cassandra-*-bin.tar.gz`.
2. Wrap it in an image that uses the official image's entrypoint:
   ```dockerfile
   FROM cassandra:5.0
   ADD apache-cassandra-*-bin.tar.gz /opt/
   RUN rm -rf /opt/cassandra && mv /opt/apache-cassandra-* /opt/cassandra && chown -R cassandra:cassandra /opt/cassandra
   ```
3. Build it with `docker build -t cassandra:local .`, then set `CASSANDRA_IMAGE=cassandra:local` in `.env`.

## Adding a scenario

Copy the nearest scenario. Each one:
- sources `scripts/lib.sh` and declares header tags: `# DOC:`, `# CLAIMS:`, plus `# DIRTIES: yes` and `# MANAGES_CLUSTER: yes` when they apply;
- records each claim with `check_ok`, `check_contains`, `check_equals`, or `pass`/`fail`/`warn`/`skip`, always passing a `doc_ref` of the form `path/to/page.md#section`;
- creates its own keyspace;
- never relies on another scenario's data.

## Not yet automated

These procedures are documented but not yet tested here. Contributions welcome:
- point-in-time recovery from archived commitlogs (DR Scenario 3)
- full-cluster restore via `initial_token` and via `sstableloader` (DR Scenario 4)
- a 4.1 → 5.0 rolling upgrade, `storage_compatibility_mode` steps, and Paxos v2 enablement
- enabling security: auth, TLS and JMX
- the housekeeping scripts run verbatim: repair timer, disk watchdog, backup script (scenario 07 covers only the upload pattern)
- UCS migration, and switching between compaction strategies
- the troubleshooting playbook's log messages (inducing timeouts, tombstone failures, schema disagreement)
