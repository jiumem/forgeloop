# Design Challenger Dispatch Template

Use this template when dispatching the `design_challenger` custom agent.

**Purpose:** Stress-test the current design before it moves into implementation planning.

**Dispatch after:** `Design Brief v0` and a written `Design Draft` or spec document exist.

## Input Contract

- `DESIGN_BRIEF`: problem statement, goals, non-goals, success criteria, constraints, open questions
- `DESIGN_DRAFT`: current design draft or spec document
- `GOVERNING_DOCS`: architecture rules, terminology docs, or prior decisions that constrain the design
- `REPO_CONTEXT`: only the repo structure, boundaries, and current constraints that matter to this design
- `REVIEW_FOCUS`: the main risk areas for this round, such as module boundaries, task decomposability, migration safety, or acceptance criteria
- `DESCRIPTION`: one-sentence summary of what this design is trying to solve

## Deliverable Contract

The agent must return `Design Critique`.

For each finding include:
- `severity`: `blocking` | `major` | `minor`
- `location`
- `finding`
- `impact`
- `repair_direction`

## Boundary

- Do not ask the user questions directly
- Do not rewrite the architecture unless the current draft is fundamentally invalid
- Do not optimize for elegance; optimize for planning-readiness
- Focus on structural and verification issues, not wording polish

## Residual Review Variant

For a second-round review, add:
- `PRIOR_CRITIQUE_V1`
- `RESOLUTION_LOG`

When those are provided, the agent should return `Residual Critique` and only report:
1. unresolved blockers from the prior round
2. newly exposed high-severity issues that would still prevent planning
