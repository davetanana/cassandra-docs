# Documentation Tools

Scripts that keep these docs tied to the Apache Cassandra source. They read a **Cassandra source checkout** that you pass as an argument, so they work from a standalone docs repository. They need Python 3 and nothing else (standard library only). `git` is optional and is used only to record the commit hash.

| Script | What it does |
| :--- | :--- |
| `gen_yaml_reference.py` | Generates `09_reference/01_cassandra_yaml_reference.md` from `conf/cassandra.yaml`, `conf/cassandra_latest.yaml` and `Config.java`. Each key gets its value, whether it is active or commented out, the `cassandra_latest.yaml` value when it differs, deprecated aliases, and the source comment. |
| `gen_nodetool_reference.py` | Generates `09_reference/02_nodetool_reference.md` from `NodeTool.java` and the `@Command` / `@Arguments` / `@Option` annotations in `tools/nodetool/*.java`. |
| `check_docs.py` | Drift checker. It reports `nodetool` commands, subcommands and flags, and `cassandra.yaml` keys, that are used in the docs but don't exist in the given checkout. |
| `cassandra_source.py` | Shared parsing helpers used by the three scripts. |
| `build_ai_bundle.py` | Builds `llms.txt` and the single-file AI bundle from the README Table of Contents. `--check` fails if `llms.txt` is stale. |
| `build_site.py` | Stages the pages and writes an MkDocs config for the searchable site on GitHub Pages. Install the pinned site packages with `pip install -r tools/site-requirements.txt`, then run `mkdocs build --strict -f build/site/mkdocs.yml` (or `mkdocs serve -f build/site/mkdocs.yml` to preview). CI builds it on every pull request; `.github/workflows/pages.yml` publishes it when you run that workflow by hand. |
| `check_links.py` | Checks every relative link and `#anchor` in the Markdown pages. |
| `check_diagrams.py` | Lints every Mermaid diagram (labels like `"1. Step"` render on GitHub as "Unsupported markdown: list"). With `--render` it also renders each diagram with the Mermaid CLI in Docker, so syntax errors fail before GitHub shows them. |

## Usage

Run these from the docs root. Point them at a checkout of the branch the docs describe, e.g. `cassandra-5.0`.

```bash
git clone --branch cassandra-5.0 --depth 1 https://github.com/apache/cassandra.git /tmp/cassandra

# Regenerate the reference pages
python3 tools/gen_yaml_reference.py     /tmp/cassandra -o 09_reference/01_cassandra_yaml_reference.md
python3 tools/gen_nodetool_reference.py /tmp/cassandra -o 09_reference/02_nodetool_reference.md

# Check the hand-written pages for drift (exit code 1 on errors; --strict also fails on warnings)
python3 tools/check_docs.py /tmp/cassandra
```

Re-run all three whenever you move to a new Cassandra release (e.g. 5.0.10 → 5.0.11), and run `check_docs.py` in CI on every docs change.

## What `check_docs.py` checks, and its limits

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
  * Values and defaults: the checker confirms a key exists, not that the value the docs give for it is right.
* Shell comments and quoted strings in code blocks are ignored, so prose such as `echo "waiting for nodetool to respond"` doesn't count as an invocation.
* Generated pages under `09_reference/` and this `tools/` directory are skipped.

## Licensing note

The generated pages reproduce comments and help text from the Apache Cassandra source, which is under the Apache License 2.0. Keep the attribution header that the generators write at the top of each page.
