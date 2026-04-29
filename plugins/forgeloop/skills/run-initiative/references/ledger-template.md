# <Initiative Name> Ledger

Language note: this template defines structure only. Write headings and prose in the primary language of the user's request, while preserving technical identifiers, paths, commands, and protocol tokens.

## Initiative

- Initiative root: `<initiative-root>`
- Design: `./DESIGN.md` when present
- Plan: `./PLAN.md`
- Branch: `codex/<initiative-code>-<initiative-slug>`
- Base commit:
- Delivery: `./DELIVERY.md` when complete
- Handoff: `docs/initiatives/handoff/<initiative-code>-<initiative-slug>.md` when complete
- PR: pending

## Run Policy

- Execution unit: Milestone
- Coder: generic subagent by task entrypoint and role protocol, high reasoning effort when available, no parent context dependency
- Reviewer: generic subagent by task entrypoint and role protocol, high reasoning effort when available, no parent context dependency
- Preferred Coder task name: `coder_<initiative-code>`
- Preferred Reviewer task name: `reviewer_<initiative-code>`
- Extract `<initiative-code>` from the initiative directory's three-digit prefix, for example `001-auth-hardening` uses `coder_001` and `reviewer_001`.
- For older uncoded initiatives, fall back to slug-based names by lowercasing and replacing non `[a-z0-9_]` characters with `_`.
- Scheduler owns `LEDGER.md` status and verdict updates.
- Coder may write implementation and evidence but not Milestone status or reviewer verdict.
- Reviewer returns a verdict report and does not edit code, PLAN, LEDGER, or evidence.
- Commit / push are evidence and recovery points, not approval. Coder push before Reviewer `PASS` is only a review candidate.
- Default primary commit granularity is one coherent commit per Milestone; Work Items are not commit units by default.
- Reviewer-directed repairs may add fixup commits inside the same Milestone diff range.
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

For repairs, record both the fixup commit and whether final review considered the cumulative Milestone diff when needed. If the same Milestone receives `REPAIR_REQUIRED` three times, or the same blocking issue survives two repair attempts, set the Milestone to `PAUSED`, record the structural blocker, and stop for human architectural decision.

## Final Validation

- Status: pending
- Commands:
- Notes:

If final validation fails, keep the initiative in `active/`, record the blockers here, repair the affected diff, and rerun review before completion.

## Completion

- Status: active
- Completed path: `docs/initiatives/completed/<initiative-code>-<initiative-slug>/` when complete
- Delivery artifact: `./DELIVERY.md` when complete
- Handoff artifact: `docs/initiatives/handoff/<initiative-code>-<initiative-slug>.md` when complete
- Completion rule: move from `active/` to `completed/` only after all Milestones are `PASS` and final validation is recorded.

## Residual Risks

- none recorded
