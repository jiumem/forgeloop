# Forgeloop Custom Agents

Forgeloop 0.1.1 ships a small, explicit set of project-scoped custom agents under `.codex/agents/`.

These agents are the stable role layer for the built-in workflow skills. They are intentionally narrow. The skill decides when to dispatch them and assembles the task packet; the custom agent defines how that role should think and what it should return.

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

### `implementer`

- Stage: implementation
- Used by: `task-loop`
- Purpose: execute one bounded task packet, write or update tests, verify the result, and report status
- Returns: `DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT`

### `spec_reviewer`

- Stage: implementation review
- Used by: `task-loop`
- Purpose: verify the implementation matches the requested task specification
- Returns: `Spec Review`

### `code_reviewer`

- Stage: implementation review
- Used by: `task-loop`, `requesting-code-review`
- Purpose: review production readiness, test quality, regressions, and maintainability for the provided review scope
- Returns: strengths, findings by severity, and a readiness assessment for the reviewed scope

## Boundary Rules

- Skills own dispatch policy and packet construction
- Custom agents own role behavior and output discipline
- The main agent keeps responsibility for requirements, decisions, and final outputs
- Do not add agents that duplicate an existing role with different wording
- Do not use a custom agent when a built-in `default`, `worker`, or `explorer` agent is enough

## 0.1.1 Contract

For 0.1.1, these five agents are the official Forgeloop custom agent set. If a workflow needs another named role, add it explicitly under `.codex/agents/`, wire it from the relevant skill, and extend the repository self-checks in `tests/codex/verify-codex-only.sh`.
