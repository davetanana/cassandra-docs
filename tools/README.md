# Tools

Scripts that keep this guide accurate and help readers use it. All of them need only Python 3 (standard library); a few use Docker or a Cassandra source checkout, as noted. Run them from the repository root.

> [!CAUTION]
> These tools read files and print results. They don't connect to a Cassandra cluster. The stress profile in [`stress/`](stress/) **does** write data: run it only against a disposable or staging cluster. See the [disclaimer](../README.md#disclaimer).

| Tool | For | Needs |
| :--- | :--- | :--- |
| [`capacity_plan.py`](#capacity_planpy) | Readers: how many nodes of a machine, with availability, durability and rough cost | Python |
| [`stress/starter_profile.yaml`](#stressstarter_profileyaml) | Readers: a `cassandra-stress` profile to benchmark throughput per node | `cassandra-stress`, a staging cluster |
| [`check_links.py`](#check_linkspy) | Contributors: relative links and `#anchors` | Python |
| [`check_docs.py`](#check_docspy) | Contributors: `nodetool` commands and flags, and `cassandra.yaml` keys, exist in Cassandra | A Cassandra checkout |
| [`check_diagrams.py`](#check_diagramspy) | Contributors: Mermaid diagrams render on GitHub | Python; Docker for `--render` |
| [`gen_yaml_reference.py`](#gen_yaml_referencepy-and-gen_nodetool_referencepy), [`gen_nodetool_reference.py`](#gen_yaml_referencepy-and-gen_nodetool_referencepy) | Maintainers: regenerate the two generated reference pages | A Cassandra checkout |
| [`build_ai_bundle.py`](#build_ai_bundlepy) | Maintainers: `llms.txt` and the single-file AI bundle | Python |
| [`build_site.py`](#build_sitepy) | Maintainers: the optional searchable site | Python; `mkdocs` to build |
| `cassandra_source.py` | Shared parsing helpers for the generators and `check_docs.py` | |

The live-cluster checks are in [`test_env/`](../test_env/README.md), not here.

Several tools read a Cassandra source checkout. Use the branch the guide describes:

```bash
git clone --depth 1 --branch cassandra-5.0 https://github.com/apache/cassandra.git ../cassandra
```

---

## `capacity_plan.py`

Works out how many nodes of a machine type a workload needs, and prints availability, durability and a rough monthly list-price cost. The formulas, assumptions and sources are on the [capacity planning](../05_cluster_deployment_and_config/05_capacity_planning.md) page; the script only does the arithmetic.

```bash
python3 tools/capacity_plan.py --list-machines             # built-in machine profiles
python3 tools/capacity_plan.py --machine aws-i4i.2xlarge \
  --data 3TB --growth 50 --years 2 \
  --writes 15000 --write-size 1KiB --reads 30000 --read-size 2KiB \
  --compression 0.5 --strategy ucs --replace-hours 12 --afr 2
```

| Group | Options |
| :--- | :--- |
| Workload | `--data` (one copy, uncompressed: `3TB`, `500GiB`), `--growth` (%/year), `--years`, `--writes`, `--write-size`, `--reads`, `--read-size` (per second, per datacenter), `--read-cl` (`local_quorum` or `local_one`) |
| Cluster | `--rf`, `--dcs`, `--racks`, `--strategy` (`ucs`, `lcs`, `stcs`, `twcs`), `--compression` (from `nodetool tablestats`), `--write-amp`, `--index-overhead`, `--sstables-per-read`, `--cache-hit`, `--replace-hours`, `--stream-mibps`, `--ops-per-node` (from your benchmark) |
| Machine | `--machine <profile>`, or describe one: `--disk`, `--read-iops`, `--nic-gbps`, `--disk-mbps`, `--price-hour`; planning shares `--iops-util`, `--nic-util` (default 0.5) |
| Availability and durability | `--instance-sla`, `--zone-sla`, `--maintenance-min`, `--afr` |

Any profile value can be overridden. Every result is a **planning estimate**: profile figures are the providers' published maximums and list prices on the date the page gives, and throughput per node must come from your own benchmark. Exit code 0, or 2 for bad arguments.

## `stress/starter_profile.yaml`

A commented [`cassandra-stress`](../09_reference/03_tools_reference.md#6-cassandra-stress-load-generation) user profile for measuring `--ops-per-node`. Copy it, replace the table with yours, and set the populations, sizes and replication. The [capacity planning page](../05_cluster_deployment_and_config/05_capacity_planning.md#a-starter-stress-profile) shows how to check it on the quickstart node and how to run a fixed-rate benchmark on staging. It creates the `stress_plan` keyspace and writes data.

## `check_links.py`

Checks every relative link and `#anchor` in the Markdown pages, using GitHub's anchor rules.

```bash
python3 tools/check_links.py               # or --docs <dir> to check another copy
```

It also checks that every guide page in the numbered folders has the `[!CAUTION]` notice linking to the [disclaimer](../README.md#disclaimer) under its title. Prints each broken link with its file and line, and each page missing the notice. Exit code 1 if anything is wrong.

## `check_docs.py`

Drift checker: reports `nodetool` commands and flags, and `cassandra.yaml` keys, that the docs use but the given Cassandra checkout doesn't define.

```bash
python3 tools/check_docs.py ../cassandra            # exit 1 on errors
python3 tools/check_docs.py ../cassandra --strict   # warnings fail too
```

* **Errors**
  * A `nodetool <cmd>` in inline code or a code block where `<cmd>` isn't a registered command or group.
  * An unknown subcommand of `repair_admin` or `bootstrap`.
  * A flag the command doesn't define.
  * A top-level key in a `yaml` code block that `Config.java` doesn't accept.
* **Warnings**
  * Inline `` `key: value` `` mentions using a deprecated alias (e.g. `compaction_throughput_mb_per_sec`).
  * Inline mentions of a name that appears nowhere in the config or Java source.
* **Not checked**
  * Nested yaml keys inside code blocks.
  * CQL syntax.
  * JVM flags.
  * Values and defaults: the checker confirms a key exists, not that the value the docs give for it is right. The [`test_env`](../test_env/README.md) scenarios check values on a live cluster.
* Shell comments and quoted strings in code blocks are ignored, so prose such as `echo "waiting for nodetool to respond"` doesn't count as an invocation.
* Generated pages under `09_reference/` and this `tools/` directory are skipped.

## `check_diagrams.py`

Lints every Mermaid diagram. A flowchart label that starts with a number and a period (`["1. Repair"]`) renders on GitHub as "Unsupported markdown: list"; write `Step 1:` or `§1` instead.

```bash
python3 tools/check_diagrams.py            # lint only
python3 tools/check_diagrams.py --render   # also render each diagram with the Mermaid CLI in Docker
```

`--render` uses the pinned `minlag/mermaid-cli` image, so a syntax error fails here instead of showing as an error box on GitHub. Exit code 1 on problems, 2 if Docker is missing or fails.

## `gen_yaml_reference.py` and `gen_nodetool_reference.py`

Generate the two reference pages from a Cassandra checkout. Don't edit those pages by hand.

```bash
python3 tools/gen_yaml_reference.py     ../cassandra -o 09_reference/01_cassandra_yaml_reference.md
python3 tools/gen_nodetool_reference.py ../cassandra -o 09_reference/02_nodetool_reference.md
```

* `gen_yaml_reference.py` reads `conf/cassandra.yaml`, `conf/cassandra_latest.yaml` and `Config.java`. Each key gets its value, whether it is active or commented out, the `cassandra_latest.yaml` value when it differs, deprecated aliases, and the source comment.
* `gen_nodetool_reference.py` reads `NodeTool.java` and the `@Command`, `@Arguments` and `@Option` annotations in `tools/nodetool/*.java`.
* Without `-o`, they write to standard output. `git` is optional and is used only to record the commit hash.

Re-run both, then `check_docs.py`, for every new 5.0.x release (workflow C in [test_env/AGENTS.md](../test_env/AGENTS.md)).

## `build_ai_bundle.py`

Builds `llms.txt` (the page index for AI assistants) from the README's Table of Contents, and two single-file bundles in `dist/` (the guide, and the reference pages) for attaching to a chat or a release.

```bash
python3 tools/build_ai_bundle.py           # write llms.txt and dist/
python3 tools/build_ai_bundle.py --check   # exit 1 if llms.txt is stale; writes nothing
```

`--base-url` makes the links in `llms.txt` absolute. Run it after any change to the README's Table of Contents, and commit `llms.txt`. `dist/` isn't committed. See [AI_USAGE.md](../AI_USAGE.md).

## `build_site.py`

Stages the pages and writes an MkDocs config for the optional searchable site. The pages themselves aren't changed.

```bash
python3 tools/build_site.py
pip install -r tools/site-requirements.txt
mkdocs build --strict -f build/site/mkdocs.yml   # or: mkdocs serve -f build/site/mkdocs.yml
```

`--repo-url` (default: the git `origin` remote) turns links to non-Markdown files into GitHub URLs. CI builds the site on every pull request; `.github/workflows/pages.yml` publishes it only when run by hand.

---

## Before you open a pull request

```bash
python3 tools/check_links.py
python3 tools/check_docs.py ../cassandra
python3 tools/build_ai_bundle.py --check
python3 tools/check_diagrams.py
```

All four must pass. CI runs them, plus `check_diagrams.py --render` and the site build. If you changed a claim the cluster can test, also run the matching [`test_env`](../test_env/README.md) scenario.

## Licensing note

The generated pages reproduce comments and help text from the Apache Cassandra source, which is under the Apache License 2.0. Keep the attribution header that the generators write at the top of each page.
