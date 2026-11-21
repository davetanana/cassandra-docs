# CLAUDE.md

@AGENTS.md

## Claude Code specifics

- `/validate-docs [NN ...|<page path>|release 5.0.N]` runs the validation workflows in `test_env/AGENTS.md` (skill: `.claude/skills/validate-docs/SKILL.md`).
- Run `test_env/scripts/run.sh` with `run_in_background` and wait for the completion notification. Don't poll the log.
- When working under `test_env/`, the rules in `test_env/AGENTS.md` (imported by `test_env/CLAUDE.md`) also apply.
