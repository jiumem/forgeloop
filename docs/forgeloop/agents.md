# Forgeloop Custom Agents

Forgeloop 0.2.0 ships a small, explicit set of custom agent source manifests under `agents/`.

These agents are the stable role layer for the built-in workflow skills. They are intentionally narrow. The skill decides when to dispatch them and binds the formal input surface; the custom agent defines how that role should think and what it should return.

All Forgeloop custom agents default to `gpt-5.4` with `high` reasoning effort. Model policy lives in the agent TOML files, not in individual workflow skills. The installer copies these manifests into the target project's `.codex/agents/`.

## Shipped Agent Set

### `design_challenger`

- Stage: pre-planning design review
- Used by: `brainstorming`
- Purpose: stress-test a design brief or design draft before it moves into planning
- Returns: `Design Critique` with `blocking | major | minor` findings

### `plan_reviewer`

- Stage: plan validation
- Used by: `writing-plans`
- Purpose: verify the implementation plan is complete, aligned to the spec, and executable without an engineer getting stuck
- Returns: `Plan Review`

### `coder`

- Stage: runtime execution
- Used by: `task-loop`, `milestone-loop`, `initiative-loop`
- Purpose: act as the single continuous coding owner, execute `G1` / `G2` / `G3` as assigned, and append coder facts to the active rolling doc
- Returns: formal coder and gate facts in the active rolling doc

### `code_reviewer`

- Stage: implementation review
- Used by: `requesting-code-review`
- Purpose: review production readiness, test quality, regressions, and maintainability for the provided review scope
- Returns: strengths, findings by severity, and a readiness assessment for the reviewed scope

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

## 0.2.0 Contract

For 0.2.0, these seven agents are the official Forgeloop custom agent set. If a workflow needs another named role, add it explicitly under `agents/`, wire it from the relevant skill, and extend the repository self-checks in `tests/codex/verify-codex-only.sh`.
