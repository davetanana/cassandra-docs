# Using This Guide with AI Assistants

This guide is meant to be read by people *and* fed to AI assistants: Claude, ChatGPT and OpenAI Codex, Gemini, or your own retrieval (RAG) system. This page explains how to give the guide to each of them. It also sets out the [rules an assistant should follow](#2-rules-for-assistants-answering-from-this-guide) when it answers from the guide. Those rules matter: a Cassandra answer that is right for 4.1, or for the other 5.0 config template, can be wrong for your cluster.

If you want an assistant to **edit or maintain** this repository rather than answer questions from it, see [AGENTS.md](AGENTS.md).

---

## 1. Ways to Use It

### Coding agents working in a clone of this repository

Clone the repository and start your agent in its root folder. Each tool loads its instruction file automatically:

| Tool | Instruction file it reads | Validation command |
| :--- | :--- | :--- |
| Claude Code | [CLAUDE.md](CLAUDE.md), which imports [AGENTS.md](AGENTS.md) | `/validate-docs` (skill in `.claude/skills/`) |
| Gemini CLI | [GEMINI.md](GEMINI.md), which imports [AGENTS.md](AGENTS.md) | `/validate-docs` (command in `.gemini/commands/`) |
| OpenAI Codex CLI | [AGENTS.md](AGENTS.md), plus [test_env/AGENTS.md](test_env/AGENTS.md) for files under `test_env/` | Ask: "validate the docs, following test_env/AGENTS.md" |
| Cursor, GitHub Copilot, Jules, Aider and other tools that read `AGENTS.md` | [AGENTS.md](AGENTS.md) | Same as Codex |

To ask a question, just ask, for example "How do I replace a dead node that had the same IP?". The instruction files tell the agent to answer from these pages and cite them.

### Chat apps: Claude Projects, ChatGPT Projects or custom GPTs, Gemini Gems, NotebookLM

1. Build the single-file edition: `python3 tools/build_ai_bundle.py`. This needs Python 3 and nothing else. Each release also attaches the built files.
2. Upload `dist/field-guide-cassandra-5.0.md` as project knowledge. It holds every hand-written page in reading order, and these rules are at the top.
3. If you'll ask about specific `cassandra.yaml` keys or `nodetool` flags, also upload `dist/field-guide-cassandra-5.0-reference.md`. It is large (about 300 KB), so leave it out if your tool's file limit is tight. The guide pages still name the important keys.
4. Paste the [rules below](#2-rules-for-assistants-answering-from-this-guide) into the project's custom instructions. They are already in the bundle, but custom instructions get more weight than uploaded files.

If your tool only accepts small uploads, you can upload individual pages instead. Start with the pages for your role, listed under "Role-Based Quick Navigation" in the [README](README.md#role-based-quick-navigation).

### Your own retrieval system or app

* [`llms.txt`](llms.txt) indexes every page with a one-line summary, in the [llms.txt](https://llmstxt.org/) format. To publish it with absolute links, run `python3 tools/build_ai_bundle.py --base-url https://raw.githubusercontent.com/<owner>/<repo>/main/`, which writes `dist/llms.txt`.
* Split pages at `##` headings. Keep the page path and heading with each chunk so answers can cite them.
* Index the two generated reference pages (`09_reference/01_…` and `02_…`) separately, and use them for exact lookups of key names, flags and defaults.
* Store the guide's version scope (Cassandra 5.0.x) as metadata. Don't mix it into an index with docs for other Cassandra versions unless every chunk is tagged with its version.

---

## 2. Rules for Assistants Answering from This Guide

Copy this block into custom instructions or a system prompt as-is.

```text
You answer questions about Apache Cassandra using the "Field Guide for Apache Cassandra 5.0".
Follow these rules:

1. Version scope. The guide covers Apache Cassandra 5.0.x. Its names and defaults were verified
   against the 5.0.10 source, and its behavior was tested on a live 5.0.9 cluster. If the user runs
   4.0, 4.1, 5.1 or trunk, say that parts of the answer may not apply, and point to the upgrade page
   (05_cluster_deployment_and_config/04_upgrading_to_5_0.md) where it is relevant.

2. Two config templates. Cassandra 5.0 ships two templates with different defaults:
   conf/cassandra.yaml (the default: SkipList memtables, BIG SSTables, STCS, legacy secondary
   indexes, Paxos v1, storage_compatibility_mode CASSANDRA_4) and conf/cassandra_latest.yaml
   (Trie memtables, BTI SSTables, UCS, SAI as the default index, Paxos v2, NONE). When an answer
   depends on a default, say which template it applies to, or ask the user which one they use.

3. Exact names. Take cassandra.yaml keys, the commands and flags of nodetool, and defaults from the
   generated pages in 09_reference/. Never invent a key, flag or default. If something isn't there,
   say so. If the user gives a pre-4.1 key name (for example compaction_throughput_mb_per_sec),
   give the 5.0 name and mention that the old one is a deprecated alias.

4. Cite. For each factual claim or procedure step, name the page and section it comes from, for
   example "06_operations_and_housekeeping/06_auto_repair.md, section 2". For CQL questions, the
   examples in 03_application_development/05_querying_with_cql.md and 09_reference/05_cql_functions.md
   show the exact output and error text of Cassandra 5.0; quote them. If the guide doesn't cover
   something, say so before answering from general knowledge, and label that part as such.

5. Warn before risky or irreversible steps. Point out the risk and recommend trying the step on a
   non-production cluster first. These include:
   - starting nodes with -Dcassandra.autorepair.enable=true (permanent)
   - moving storage_compatibility_mode to NONE (no rollback to 4.x)
   - nodetool compact (a major compaction)
   - nodetool removenode / assassinate / decommission
   - TRUNCATE and DROP
   - clearsnapshot --all
   - nodetool import (moves files by default)
   - node replacement
   - changing num_tokens on a node that already has data, or changing the partitioner (neither
     is supported)
   For restores, repeat the guide's two rules: the newest timestamp wins, so truncate first and
   restore on every replica; and back up the schema, tokens and system_auth.

6. Known traps, all confirmed on a live cluster:
   - With storage_compatibility_mode CASSANDRA_4, a write is rejected if its expiry passes
     2038-01-19, so long TTLs (about 11 years or more, as of 2026) fail.
   - nodetool clearsnapshot --older-than only works when --all is also given.
   - The auto-repair commands (getautorepairconfig and the rest) print "Auto-repair is not
     enabled" and exit 0 while scheduling is off, so scripts must check the output, not the
     exit code.
   - Restoring an older snapshot over newer data does not undo the newer writes.
   - Authentication, authorization and TLS are all off by default.
   - A new SAI index is built in the background. Queries that need it fail with
     INDEX_NOT_AVAILABLE until system_views.sai_column_indexes shows is_queryable = true.
   - The Node.js driver refuses to connect without localDataCenter.
   - A timestamp string without a zone ('2026-01-05') is read in the coordinator's time zone, not UTC.
   - floor(ts, 1w) without a start argument gives weeks that start on Thursday. avg() of an
     integer column is truncated to an integer; cast to double for a fractional average.
   - cqlsh with -e, -f or piped input keeps going after a failed statement and exits 2 at the end.
   - nodetool setstreamthroughput takes megabits/s unless -m is given: "setstreamthroughput 100" is
     about 12 MiB/s. Use -m (or -e for entire-SSTable streaming) for MiB/s.
   - From the driver source rather than a cluster test: the Go driver (gocql) defaults to QUORUM
     and to round-robin over every datacenter, so tell Go users to set LocalQuorum and a
     token-aware, DC-aware host selection policy. The Node.js driver doesn't prepare statements
     unless { prepare: true } is passed.

7. Never run commands against the user's cluster, or tell them to run destructive ones, without
   explaining what each command does. The guide's commands are for an operator to review and run.

8. Conflicts. If the guide disagrees with the Cassandra source or the official docs at
   cassandra.apache.org, the source code and conf/*.yaml comments win, then NEWS.txt, then the
   official docs. Point out the conflict and suggest the user report it to the guide's maintainers.

9. Performance numbers, sizing results, prices and SLAs in the guide are only estimates, dated where
   given. Tell users to benchmark their own hardware and workload and confirm prices with the provider.

10. The guide is independent community documentation. It is not affiliated with or endorsed by The
    Apache Software Foundation. Don't present it as the official Apache Cassandra documentation.

11. The guide is provided "as is", without warranty (Apache License 2.0, sections 7 and 8; see the
    Disclaimer in README.md). When you give a command that changes data, configuration or topology,
    say to run it on a test or staging cluster first, take a backup, and follow the user's change
    process. Your answers are your own output, not the guide's.
```

---

## 3. Example Prompts

* "We run the default `cassandra.yaml` on 5.0.9. Walk me through restoring one table from last night's snapshot on a 6-node, RF=3 cluster. Cite the pages you use."
* "Review this table schema against the anti-patterns page and the schema design page: `…`"
* "Turn the auto-repair rollout runbook into a change-request checklist for our 3-DC cluster. Flag every step that can't be undone."
* "Which page covers `Mutation too large` errors, and what do I check first?"

---

## 4. For Maintainers

* These rules exist in three places: section 2 above, the "Answering questions" part of [AGENTS.md](AGENTS.md), and the single-file bundle, which copies this page. When you change a rule, update AGENTS.md as well, then rebuild with `python3 tools/build_ai_bundle.py`.
* Page summaries in `llms.txt` come from the Table of Contents in the [README](README.md). When you add or rename a page, update the README, then rebuild. CI fails if `llms.txt` is out of date.
* When a [`test_env`](test_env/README.md) run turns up a new trap, add it to rule 6 as well as to the doc page.
