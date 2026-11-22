# Contributing

Corrections, new runbooks and new validation scenarios are all welcome. This guide stays useful only while it matches the real behavior of Apache Cassandra 5.0.x, so every change must keep it **verifiable**.

## Ground rules

1. **Cite the code or a test.** For a claim about a name or a default, link to the Cassandra source on the `cassandra-5.0` branch (`conf/cassandra.yaml`, `Config.java`, the nodetool sources) or to the generated pages in `09_reference/`. For a claim about behavior, add or point to a check in [`test_env/`](test_env/README.md).
2. **When a check fails, decide whether the doc or the test is wrong, and fix that one.** Never weaken an assertion just to make a check pass.
3. **Don't edit generated pages by hand.** `09_reference/01_cassandra_yaml_reference.md`, `09_reference/02_nodetool_reference.md` and `llms.txt` are generated; see [tools/README.md](tools/README.md).
4. **Write only original text.** Don't paste text from vendor docs, blogs, Stack Overflow or other non-Apache-2.0 sources; paraphrase and link instead. Excerpts from Apache Cassandra (Apache-2.0) are fine, with attribution.
5. **Follow the trademark rules** in [AGENTS.md](AGENTS.md#licensing-and-trademarks-required). Don't present this guide as official ASF documentation.

## How to submit a change

1. **Open an issue first for anything bigger than a fix.** For a new page, a restructure or a new scenario, use the "New runbook or improvement" issue template so we can agree on where it goes before you write it. Typos and small corrections can go straight to a pull request.
2. **Fork the repository and create a branch** from `main`, named after the change (`fix-auto-repair-default`, `runbook-sstable-upgrade`).
3. **Make the change**, following the ground rules above and the [style](#style) rules.
4. **Run the checks** in the next section. Fix anything that fails before you push.
5. **Open a pull request against `main`.** The template asks how you verified each claim. Fill it in: that table is what reviewers check first.
6. **CI runs the static checks** (links, drift against the `cassandra-5.0` source, `llms.txt`, shell syntax and shellcheck). A red check blocks the merge.
7. **A maintainer reviews it.** If your change touches a claim that `test_env` covers, the maintainer may run the cluster validation before merging. Expect review comments about evidence more than about wording.
8. **We squash-merge** once the checks pass and the review is approved.

## Before you open a pull request

You need Python 3 (no packages) and a checkout of the Cassandra `cassandra-5.0` branch:

```bash
git clone --depth 1 --branch cassandra-5.0 https://github.com/apache/cassandra.git ../cassandra
```

Then run the same checks CI runs:

```bash
python3 tools/check_links.py
python3 tools/check_diagrams.py              # add --render if you have Docker (CI does)
python3 tools/check_docs.py ../cassandra
python3 tools/build_ai_bundle.py --check     # if it fails, run it without --check and commit llms.txt
```

To preview the guide as a website (optional; CI builds it on every pull request and fails on broken links or anchors):

```bash
python3 -m pip install -r tools/site-requirements.txt
python3 tools/build_site.py && mkdocs serve -f build/site/mkdocs.yml    # then open http://127.0.0.1:8000
```

If you changed anything under `test_env/`, also run the shell checks. `shellcheck` is optional locally because CI runs it, but it saves a round trip:

```bash
for f in test_env/scripts/*.sh test_env/scenarios/*.sh; do bash -n "$f"; done
shellcheck -S error test_env/scripts/*.sh test_env/scenarios/*.sh
```

To add an example query with its output, you don't need to write a test: mark it as described in [test_env/AGENTS.md](test_env/AGENTS.md#d-add-a-check-or-a-scenario) and scenario 14 checks it.

If you changed a testable claim, run its scenario as well. The scenario table in [test_env/README.md](test_env/README.md) shows which scenarios cover which pages. You need Docker with 6–9 GB of memory.

```bash
cd test_env && scripts/up.sh && scripts/run.sh <NN>    # <NN> is the scenario number, for example 03
```

If you can't run Docker, say so in the pull request and a maintainer will run the scenario. The full cluster validation also runs monthly, and maintainers run it before each release.

## Style

See the "Style" section of [AGENTS.md](AGENTS.md#style). In short: plain US English, numbered `##` sections, GitHub alerts for irreversible steps, 5.0 key names with units, and commands that run as written.

## Using an AI assistant to contribute

That's fine. Claude Code, Gemini CLI, OpenAI Codex and other tools that read `AGENTS.md` pick up this repository's rules automatically. See [AI_USAGE.md](AI_USAGE.md). You are still responsible for checking the result: AI-written claims must meet the same verification rules as any other change.

## Licensing

By contributing, you agree that your contribution is licensed under the [Apache License 2.0](LICENSE), the same license as the rest of the guide (Apache-2.0 §5). Add your name to `NOTICE` only if you contribute a substantial new page.
