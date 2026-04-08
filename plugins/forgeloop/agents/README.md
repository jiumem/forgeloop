## Forgeloop Agent Manifests

This directory is the source-of-truth manifest layer for the Forgeloop suite's custom agents.

- `plugins/forgeloop/skills/` dispatch these agents by name
- `plugins/forgeloop/scripts/materialize-agents.sh` copies these manifests into `${CODEX_HOME:-~/.codex}/agents`
- `plugins/forgeloop/scripts/materialize-agents.sh --project-dir <path>` copies these manifests into `<path>/.codex/agents/`
- runtime workflow roles now center on `coder`, `task_reviewer`, `milestone_reviewer`, and `initiative_reviewer`; each runtime loop reuses one `coder` plus one `reviewer` inside the current session, while formal truth keeps only `coder_slot`
- the planning roles `planner`, `design_reviewer`, `gap_reviewer`, and `total_task_doc_reviewer` are dispatched inside `run-planning` through the internal `planning-loop`; each planning stage reuses one `planner` plus one `reviewer` inside the current session, while formal truth keeps only `planner_slot`
- only one plane's reusable worker table should remain live at once; cross-plane handoff must close the old plane's bindings before the next plane stays active
- runtime workflow-facing manifests obey the single runtime cutover contract in `plugins/forgeloop/skills/run-initiative/references/runtime-cutover.md`; the current runtime target is `minimal_preferred`, while planning remains out of cutover scope in this phase
- workflow-facing manifests obey the shared packet law in `plugins/forgeloop/skills/references/anchor-addressing.md`
