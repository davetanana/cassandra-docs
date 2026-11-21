# GEMINI.md

@AGENTS.md

## Gemini CLI specifics

- `/validate-docs [NN ...|<page path>|release 5.0.N]` runs the validation workflows in `test_env/AGENTS.md` (command: `.gemini/commands/validate-docs.toml`).
- A full validation run takes 30–45 minutes, longer than the default shell timeout. Start it in the background: `test_env/scripts/run.sh > /tmp/validate.log 2>&1 &`. Then check `test_env/results/LATEST.md` once the process has exited.
- When working under `test_env/`, the rules in `test_env/AGENTS.md` (imported by `test_env/GEMINI.md`) also apply.
