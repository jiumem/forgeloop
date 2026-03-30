## Forgeloop Agent Manifests

This directory is the source-of-truth manifest layer for the Forgeloop suite's custom agents.

- `skills/` dispatch these agents by name
- `scripts/install.sh --project-dir <path>` copies these manifests into `<path>/.codex/agents/`
- the source repository itself intentionally does not keep a repo-local `.codex/`
- runtime workflow roles now center on `coder`, `task_reviewer`, `milestone_reviewer`, and `initiative_reviewer`
- the planning roles `planner`, `design_reviewer`, `gap_reviewer`, and `plan_reviewer` are dispatched inside `run-planning` through the internal `planning-loop`
- auxiliary roles such as `design_challenger` and `code_reviewer` remain available for adjacent non-runtime workflow steps
