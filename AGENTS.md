# AGENTS.md: Instructions for AI Coding Agents

This file is for AI agents working in this repository: OpenAI Codex, Gemini CLI (through [GEMINI.md](GEMINI.md)), Claude Code (through [CLAUDE.md](CLAUDE.md)), Cursor, Copilot and others. People using the guide with a chat assistant should read [AI_USAGE.md](AI_USAGE.md) instead.

## What this repository is

The **Field Guide for Apache Cassandra® 5.0** is independent, Apache-2.0 licensed Markdown documentation of runbooks and guidance for Cassandra 5.0.x. It is not affiliated with The Apache Software Foundation.

| Path | Contents | Edit by hand? |
| :--- | :--- | :--- |
| `00_…/` to `08_…/` | Hand-written guide pages, in lifecycle order (`00_getting_started/` is the quickstart) | Yes |
| `09_reference/01_cassandra_yaml_reference.md`, `02_nodetool_reference.md` | Generated from a Cassandra source checkout | **No.** Regenerate them with `tools/` |
| `09_reference/03_…` to `06_…` | Hand-written reference pages (tools, CQL, CQL functions, cqlsh) | Yes |
| `README.md` | Table of contents, version scope, role navigation. The TOC bullets also feed `llms.txt` | Yes |
| `AI_USAGE.md`, `llms.txt` | How to use the guide with AI assistants, and the generated page index | `AI_USAGE.md`: yes. `llms.txt`: no, it is generated |
| `tools/` | Python 3 scripts (standard library only): reference generators, drift checker, link checker, AI bundle builder | Yes |
| `test_env/` | Docker Compose cluster and bash scenarios that check the guide's claims on a live cluster. It has its own [AGENTS.md](test_env/AGENTS.md) | Yes |
| `LICENSE`, `NOTICE` | Apache-2.0 text and attribution | Only to add attribution |

## Two kinds of task

### Answering questions from the guide
Follow the rules in [AI_USAGE.md §2](AI_USAGE.md#2-rules-for-assistants-answering-from-this-guide):
- Scope is 5.0.x. Say which config template (`cassandra.yaml` or `cassandra_latest.yaml`) a default comes from.
- Take exact names from `09_reference/`, and never invent a key, flag or default.
- Cite the page and section you got each answer from.
- Warn before irreversible operations, and mention the known traps listed there.
- Never run commands against anything except the disposable `test_env` cluster.

### Changing the guide
1. **Check facts before you write them.** These are the arbiters:
   - **Names and defaults:** the Apache Cassandra source on the `cassandra-5.0` branch: `conf/cassandra.yaml`, `conf/cassandra_latest.yaml`, `Config.java`, and `tools/nodetool/*.java`. Ask the user for a checkout path or clone one (`git clone --depth 1 --branch cassandra-5.0 https://github.com/apache/cassandra.git`).
   - **Behavior:** the `test_env` cluster.
   - Your memory, blog posts and other vendors' docs don't decide anything. When this guide and the official docs disagree, say which one the source supports.
2. **Keep the docs and the tests in sync.** When you change a claim that a small cluster can test (a default, an error message, a command, a procedure step), add or update a check in `test_env/scenarios/`. Follow [test_env/AGENTS.md](test_env/AGENTS.md).
3. **Run the static checks before you finish.** All of them must pass:
   ```bash
   python3 tools/check_links.py                       # relative links and #anchors
   python3 tools/check_docs.py <cassandra-checkout>   # nodetool commands, flags and yaml keys exist
   python3 tools/build_ai_bundle.py --check           # llms.txt matches the README TOC
   ```
4. **Adding, renaming or removing a page:**
   - Update the TOC bullet and phase in `README.md`, and the role table if it applies.
   - Fix every link that pointed to the old path.
   - Run `python3 tools/build_ai_bundle.py` and commit the new `llms.txt`.
   - Update `doc_ref`s in `test_env/scenarios/*.sh` (`grep -rn "<old file name>" test_env/scenarios`).
5. **New Cassandra 5.0.x release:** follow workflow C in [test_env/AGENTS.md](test_env/AGENTS.md). In short: regenerate the two reference pages, read `NEWS.txt` and `CHANGES.txt`, run the full validation, and update the version-scope line in `README.md`.

## Style

* Write in plain US English for working engineers. Prefer short sentences, and make each step something the reader can act on.
* Number top-level sections (`## 1. Title`). Anchors such as `#2-enabling-it-two-switches` are linked from other pages and from tests, so check for incoming links before you rename a heading.
* Use GitHub alerts (`> [!IMPORTANT]`, `> [!WARNING]`, `> [!NOTE]`) for irreversible or surprising behavior.
* Use tables with `:---` alignment. Tag code blocks with a language (`bash`, `yaml`, `sql`).
* Use 5.0 key names with units (`compaction_throughput: 64MiB/s`). Mention deprecated names only as aliases.
* Say which template a default comes from whenever the two templates differ.
* Label performance numbers as illustrative.
* Commands must run as written. Don't put placeholders where a reader would paste them unchanged; use `<angle_brackets>` and say what to substitute.

## Licensing and trademarks: required

* All content is Apache-2.0. Don't paste text from sources under other licenses, for example vendor documentation, Stack Overflow (CC BY-SA), or blog posts. Paraphrase and link instead. Excerpts from Apache Cassandra itself are fine, with attribution, because it is Apache-2.0.
* Keep the attribution header that the generators write on generated pages, and keep `NOTICE` intact.
* Trademarks: use "Apache Cassandra®" on first use in the README. Don't use the Cassandra logo. Don't name the project, repository or site in a way that suggests it is official ("Apache Cassandra Docs", "cassandra-docs"). Don't claim the ASF endorses the guide.
* Don't add personal data, real hostnames, IPs other than the `test_env` range and RFC 5737/1918 example ranges, or credentials other than the fixed `test_env` test values.

## Tool-specific notes

* **Claude Code:** `/validate-docs` (in `.claude/skills/validate-docs/`) runs the validation workflows.
* **Gemini CLI:** `/validate-docs` (in `.gemini/commands/validate-docs.toml`) does the same.
* **Codex and others:** when asked to "validate the docs", follow [test_env/AGENTS.md](test_env/AGENTS.md) workflow A, or workflow B for a single page.
* Every agent: validation runs take 30–45 minutes and need Docker with 6–9 GB of memory. Run them in the background and wait for them to exit. If the sandbox has no Docker, say so; don't skip the step without saying so.
