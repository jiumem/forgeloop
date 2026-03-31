## Forgeloop Agent Manifests

This directory is the source-of-truth manifest layer for the Forgeloop suite's custom agents.

- `plugins/forgeloop/skills/` dispatch these agents by name
- `plugins/forgeloop/scripts/materialize-agents.sh` copies these manifests into `${CODEX_HOME:-~/.codex}/agents`
- `plugins/forgeloop/scripts/materialize-agents.sh --project-dir <path>` copies these manifests into `<path>/.codex/agents/`
- runtime workflow roles now center on `coder`, `task_reviewer`, `milestone_reviewer`, and `initiative_reviewer`
- the planning roles `planner`, `design_reviewer`, `gap_reviewer`, and `plan_reviewer` are dispatched inside `run-planning` through the internal `planning-loop`
- all workflow-facing manifests now assume anchor-addressed minimal packets by default: authoritative refs, doc-local selectors, optional minimal slices, and explicit full-document fallback only on legality failure or recovery
