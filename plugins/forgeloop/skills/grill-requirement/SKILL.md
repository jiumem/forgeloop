---
name: grill-requirement
description: Stress-test a vague requirement before it becomes a PLAN.md, Initiative, issue list, or code change. Use when the user asks to clarify, grill, stress-test, or challenge a requirement, refactor idea, architecture direction, migration plan, or implementation plan.
---

# grill-requirement

Grill the user relentlessly until the requirement is safe to plan. Do not write code, issues, `PLAN.md`, or `LEDGER.md`.

Treat the requirement as a design decision tree, not a checklist. Walk the highest-impact unresolved branch first, resolving dependencies between decisions one by one. Let the tree expand when new risks, alternatives, stakeholders, constraints, or architectural seams appear.

Ask exactly one question at a time unless the user asks for a batch. For every question, include:

- Branch: the decision-tree branch being resolved
- Question: one precise question
- Why it matters: what planning or architecture choice depends on it
- Recommended answer: the default you would choose and why
- Impact if different: what changes if the user rejects the recommendation

If the answer can be found by reading the codebase or existing docs, inspect them instead of asking the user. Read only what helps resolve the current branch.

Do not spawn subagents unless the user explicitly asks for parallel investigation. Keep the decision tree in the main thread.

Keep these states distinct:

- confirmed: user or source-of-truth docs decided it
- recommended: you recommend it, but the user has not confirmed it
- open: unresolved but not yet blocking
- blocking: unresolved and blocks planning
- non-goal: explicitly out of scope
- deferred: useful later, not needed now

Use these as radar, not limits: goal, scope, non-goals, compatibility, architecture, API, data/state, migration, validation, delivery evidence, rollback, ownership, alternatives, residual risk.

Stop grilling when you can clearly choose one disposition:

- ready_for_write_plan
- needs_more_research
- split_requirement
- not_an_initiative
- defer
- reject

When stopping, summarize only: provisional requirement, disposition, confirmed decisions, open blockers, non-goals, recommended next step.
