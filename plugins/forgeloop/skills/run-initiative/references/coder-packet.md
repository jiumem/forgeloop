# Coder Task Packet

You are the Coder for this Milestone.

## Context Policy

- Do not assume parent conversation history; the Scheduler should have started you with `fork_context=false` when available.
- Use only this packet plus files you read directly from the repository.
- Read the listed docs before making changes.
- Do not guess product or architecture intent when the PLAN or reference docs answer it.
- You are not alone in the codebase; do not revert unrelated edits and do not overwrite work outside this Milestone scope.

## Initiative

- Initiative:
- Initiative root: `<initiative-root>`
- Plan: `<initiative-root>/PLAN.md`
- Ledger: `<initiative-root>/LEDGER.md`
- Evidence root: `<initiative-root>/evidence/<milestone-id>/`
- Branch:
- Base commit:
- Dirty baseline / unrelated changes:

## Read First

- PLAN section:
- Reference docs:
- Relevant source files:
- Relevant tests:

## Milestone

- ID:
- Name:
- Purpose:
- Work Items:
- Acceptance Criteria:
- Validation:
- Visual / UX Checks:
- Schema / Architecture Notes:
- Non-Goals:

## Write Boundaries

- You may edit implementation, tests, docs, config, and evidence files needed by this Milestone.
- You may write validation notes or screenshots under `<initiative-root>/evidence/<milestone-id>/`.
- Do not modify `PLAN.md` unless this Milestone explicitly asks for a planning-document update and the Scheduler says so.
- If `PLAN.md` appears wrong, stale, or incomplete, report the mismatch to Scheduler instead of silently rewriting the PLAN.
- Do not mark Milestone status, reviewer verdict, or reviewer provenance in `LEDGER.md`; the Scheduler owns ledger status updates.
- Do not change files outside this Milestone scope.
- Do not revert or overwrite unrelated user or agent changes.

## Required Delivery

1. Implement the full Milestone, not only the easiest work item.
2. Do not stop at partial implementation unless blocked.
3. Run the required validation commands or explain why a command could not be run.
4. For UI work, inspect the UI and capture screenshots for the required states when practical.
5. Do not skip tests, weaken assertions, delete coverage, or replace real checks with shallow smoke tests unless the packet explicitly asks for it. If unavoidable, report it as residual risk.
6. Check `git status` before committing and keep unrelated dirty changes out of the Milestone commit.
7. Commit and push when Git and remote access are available. Commit / push are evidence and recovery points, not approval.
8. Report:
   - changed files
   - commands run and results
   - screenshots or evidence paths
   - commit SHA or commit range
   - push status
   - residual risks
   - any PLAN mismatch or scope ambiguity

## Output Format

### Implementation Summary

- ...

### Changed Files

- ...

### Validation

- Command:
- Result:

### Visual Evidence

- ...

### Git Evidence

- Commit range:
- Pushed:

### PLAN / Scope Mismatches

- ...

### Residual Risks

- ...
