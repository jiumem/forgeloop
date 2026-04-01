## Forgeloop Agent Manifests

This directory is the source-of-truth manifest layer for the Forgeloop suite's custom agents.

- `plugins/forgeloop/skills/` dispatch these agents by name
- `plugins/forgeloop/scripts/materialize-agents.sh` copies these manifests into `${CODEX_HOME:-~/.codex}/agents`
- `plugins/forgeloop/scripts/materialize-agents.sh --project-dir <path>` copies these manifests into `<path>/.codex/agents/`
- runtime workflow roles now center on `coder`, `task_reviewer`, `milestone_reviewer`, and `initiative_reviewer`
- the planning roles `planner`, `design_reviewer`, `gap_reviewer`, and `plan_reviewer` are dispatched inside `run-planning` through the internal `planning-loop`
- runtime workflow-facing manifests obey the single runtime cutover contract in `plugins/forgeloop/skills/run-initiative/references/runtime-cutover.md`; the current runtime target is `minimal_preferred`, while planning remains out of cutover scope in this phase
- every workflow-facing manifest expects each packet to be self-sufficient for the current object and round; previous-packet and delta-only assumptions are not part of the subagent contract
