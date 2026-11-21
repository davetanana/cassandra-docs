## What this changes

<!-- One or two sentences. Link the issue if there is one: "Fixes #123". -->

## How the claims were verified

<!-- For each new or changed fact, say how you checked it. Delete the rows that don't apply. -->

| Claim | Evidence |
| :--- | :--- |
| <!-- e.g. default of `compaction_throughput` --> | <!-- link to conf/cassandra.yaml on cassandra-5.0, or the 09_reference/ row --> |
| <!-- e.g. behavior of `nodetool import` --> | <!-- test_env scenario NN, and its PASS line --> |

## Checklist

- [ ] `python3 tools/check_links.py` passes
- [ ] `python3 tools/check_docs.py <cassandra-checkout>` passes
- [ ] `python3 tools/build_ai_bundle.py --check` passes (if you added or renamed a page, run it without `--check` and commit `llms.txt`)
- [ ] If I changed a testable claim (a default, an error message, a command, a procedure step), I added or updated a check in `test_env/scenarios/` and ran it, or I explained below why I couldn't
- [ ] I didn't edit generated pages by hand (`09_reference/01_…`, `09_reference/02_…`, `llms.txt`)
- [ ] The text is my own or comes from Apache Cassandra with attribution. Nothing is copied from vendor docs, blogs or Stack Overflow
- [ ] No real hostnames, IPs (outside the `test_env` range and RFC 5737/1918 examples), credentials or personal data
- [ ] If I renamed a `##` heading, I fixed the links and `test_env` references that pointed to its anchor

## Scenario results (if any)

<!-- Paste the scenario summary lines from test_env/results/<run>/summary.md, or write "not applicable". -->
