# Repository Operating Law

## Default mode
- Work initiative-first.
- Bind every delivery run to one Initiative total-task document under `docs/initiatives/`.
- Do not bypass formal Task/Milestone/Initiative quality transitions.

## Governance boundaries
- Do not modify `.agents/`, `.codex/`, or repository governance assets during normal delivery runs.
- Governance assets only change through dedicated governance PRs.

## Runtime discipline
- Treat `.initiative-runtime/` as rebuildable cache, not truth.
- Rebuild initiative state from tracked sources when cache is missing or stale.

## Planning discipline
- Do not start implementation from raw requirements.
- Always route through the total-task document and its assigned references.

## Review guidelines
- Flag dual source of truth, shadow state, implicit fallback, no-exit compatibility logic, invasive bridge layers, and leaky abstraction.
- Require Spec-Refs when contracts, fields, interfaces, migrations, or state transitions change.
