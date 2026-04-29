# Recommended Initiative Sequence

Language note: this template defines structure only. Write headings and prose in the primary language of the user's request, while preserving technical identifiers, paths, commands, and protocol tokens.

## Baseline

- Date:
- Branch:
- Head:
- Workspace:
- Inputs inspected:

## Existing Initiative And Handoff Check

Summarize active, completed, archived, handoff, and prior recommendation entries that affected ranking. Note any duplicate candidates that were deferred or reframed as follow-up / v2 work.

## Baseline Summary

Summarize the current project state, strengths, gaps, and risks.

## Recommendation Principles

Use these ranking dimensions:

- Product impact
- Engineering leverage
- Risk reduction
- Execution readiness

## Recommended Sequence

### 1. `<proposed-initiative-code>-<initiative-slug>` — <Initiative Name>

Code note:
- Proposed code only; final code is assigned by `grill-initiative` or `plan-initiative` when creating `active/`.

Why now:
- ...

Expected outcome:
- ...

Suggested size:
- 3-8 Milestones; do not exceed 10 Milestones without splitting the initiative.

Hardening recommendation:
- Recommended / Not needed
- Reason:

Primary risks:
- ...

Read first:
- ...

Suggested DESIGN path:
- `docs/initiatives/active/<proposed-initiative-code>-<initiative-slug>/DESIGN.md`

Suggested PLAN path:
- `docs/initiatives/active/<proposed-initiative-code>-<initiative-slug>/PLAN.md`

Duplicate check:
- Not already active/completed, or explicitly a follow-up/v2 because ...

Why before the next initiative:
- ...

### 2. `<proposed-initiative-code>-<initiative-slug>` — <Initiative Name>

...

## Not Recommended Yet

- <Direction>: <reason to defer>

## Suggested Next Action

Recommend the one initiative that should be expanded with `grill-initiative` or `plan-initiative` next.
