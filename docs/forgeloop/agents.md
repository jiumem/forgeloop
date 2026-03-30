# Forgeloop Custom Agents

Forgeloop 0.4.0 ships a small, explicit set of custom agent manifests under `plugins/forgeloop/agents/`.

These agents are the stable role layer for the built-in workflow skills. They are intentionally narrow. The skill decides when to dispatch them and binds the formal input surface; the custom agent defines how that role should think and what it should return.

All Forgeloop custom agents default to `gpt-5.4` with `high` reasoning effort. Model policy lives in the agent TOML files, not in individual workflow skills. `plugins/forgeloop/scripts/materialize-agents.sh` copies those manifests into Codex global agent storage by default, or into a target project's `.codex/agents/` when `--project-dir` is supplied.

## Shipped Agent Set

### `planner`

- Stage: planning authoring
- Used by: `run-planning` via `planning-loop`
- Purpose: act as the single continuous planning owner, write and repair the current `Design Doc`, optional `Gap Analysis Doc`, or `Total Task Doc`, and append planner facts to the active planning rolling doc
- Returns: formal planner facts and current document refs in the active planning rolling doc

### `design_reviewer`

- Stage: Design-stage formal review inside planning
- Used by: `run-planning` via `planning-loop`
- Purpose: execute the formal Design Doc review, write only to the active `Design Rolling Doc`, and judge whether design closure is structurally sound and ready to advance
- Returns: Design-stage formal review result in the active `Design Rolling Doc`

### `gap_reviewer`

- Stage: Gap-stage formal review inside planning
- Used by: `run-planning` via `planning-loop`
- Purpose: execute the formal Gap Analysis Doc review, write only to the active `Gap Rolling Doc`, and judge whether gap closure is factually grounded and ready to advance
- Returns: Gap-stage formal review result in the active `Gap Rolling Doc`

### `plan_reviewer`

- Stage: Total-task-stage formal review inside planning
- Used by: `run-planning` via `planning-loop`
- Purpose: execute the formal `Total Task Doc` review, write only to the active `Plan Rolling Doc`, and judge whether the execution map is structurally complete and ready to seal
- Returns: Plan-stage formal review result in the active `Plan Rolling Doc`

### `coder`

- Stage: runtime execution
- Used by: `task-loop`, `milestone-loop`, `initiative-loop`
- Purpose: act as the single continuous coding owner, execute `G1` / `G2` / `G3` as assigned, and append coder facts to the active rolling doc
- Returns: formal coder and gate facts in the active rolling doc

### `task_reviewer`

- Stage: Task formal review
- Used by: `task-loop`
- Purpose: execute `R1` against the current Task anchor after `G1 -> anchor / fixup`
- Returns: Task-level formal review result in the active `Task Review Rolling Doc`

### `milestone_reviewer`

- Stage: Milestone formal review
- Used by: `milestone-loop`
- Purpose: execute `R2` against the current Milestone stage candidate after `G2`
- Returns: Milestone-level formal review result in the active `Milestone Review Rolling Doc`

### `initiative_reviewer`

- Stage: Initiative formal review
- Used by: `initiative-loop`
- Purpose: execute `R3` against the current Initiative delivery candidate after `G3`
- Returns: Initiative-level formal review result in the active `Initiative Review Rolling Doc`

## Boundary Rules

- Skills own dispatch policy and packet construction
- Custom agents own role behavior and output discipline
- The main agent keeps responsibility for requirements, decisions, and final outputs
- Do not add agents that duplicate an existing role with different wording
- Do not use a custom agent when a built-in `default`, `worker`, or `explorer` agent is enough

## Current Contract

The current Forgeloop custom agent set includes eight agents. If a workflow needs another named role, add it explicitly under `plugins/forgeloop/agents/`, wire it from the relevant packaged skill, and extend the repository self-checks in `tests/codex/verify-codex-only.sh`.

## Packaging Notes

- `plugins/forgeloop/agents/` is the source-of-truth manifest location for custom agents.
- `plugins/forgeloop/skills/` is the source-of-truth skill location for the shipped workflow package.
- `plugins/forgeloop/scripts/materialize-agents.sh` copies the manifests into `${CODEX_HOME:-~/.codex}/agents` by default, or into a target project's `.codex/agents/` when requested.
