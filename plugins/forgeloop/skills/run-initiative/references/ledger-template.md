# <Initiative Name> Ledger

## Initiative

- Initiative root: `<initiative-root>`
- Plan: `./PLAN.md`
- Branch: `codex/<initiative-slug>`
- Base commit:
- Delivery: `./DELIVERY.md` when complete
- PR: pending

## Run Policy

- Execution unit: Milestone
- Coder: generic subagent by task packet, high reasoning effort when available, no parent context dependency
- Reviewer: generic subagent by task packet, high reasoning effort when available, no parent context dependency
- Preferred Coder task name: `coder_<initiative_slug_snake>`
- Preferred Reviewer task name: `reviewer_<initiative_slug_snake>`
- Normalize subagent `task_name` by lowercasing and replacing non `[a-z0-9_]` characters with `_`.
- Scheduler owns `LEDGER.md` status and verdict updates.
- Coder may write implementation and evidence but not Milestone status or reviewer verdict.
- Reviewer returns a verdict report and does not edit code, PLAN, LEDGER, or evidence.
- Commit / push are evidence and recovery points, not approval.
- Scheduler-owned recovery updates should be committed when Git is available.
- Reviewer `PASS` is required before advancing to the next Milestone.

## Allowed Milestone Statuses

- `TODO`
- `CODING`
- `REVIEW`
- `REPAIR`
- `PASS`
- `PAUSED`
- `CANCELLED`

Only `PASS` advances. `CANCELLED` is skipped only when explicitly cancelled. `PAUSED` does not complete the initiative.

## Milestones

| ID | Status | Commit Range | Pushed | Validation | Evidence | Reviewer Verdict | Reviewer Provenance | Notes |
|---|---|---|---|---|---|---|---|---|
| M01 | TODO | - | no | - | - | - | - | - |

## Repair History

Record only repair facts that affect recovery or final delivery. Do not record validation, commit, push, or packaging as reviewer approval.

For repairs, record both the fixup commit and whether final review considered the cumulative Milestone diff when needed.

## Final Validation

- Status: pending
- Commands:
- Notes:

If final validation fails, keep the initiative in `active/`, record the blockers here, repair the affected diff, and rerun review before completion.

## Completion

- Status: active
- Completed path: `docs/initiatives/completed/<initiative-slug>/` when complete
- Delivery artifact: `./DELIVERY.md` when complete
- Completion rule: move from `active/` to `completed/` only after all Milestones are `PASS` and final validation is recorded.

## Residual Risks

- none recorded
