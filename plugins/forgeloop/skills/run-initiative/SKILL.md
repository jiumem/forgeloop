---
name: run-initiative
description: Load when the user explicitly wants to execute, resume, recover, or cancel delivery from a formal Tracker Spec or persisted Initiative.
---

# Run an Initiative

Treat the configured Tracker as the sole source of truth for Specs, Tickets, dependencies, Claims, and live delivery state. Use the primary context as a thin Scheduler. Run one Ticket at a time. For each Ticket, use a fresh Coder and two isolated, read-only Reviewers; continue those same three child threads through repair rounds for that Ticket, and never reuse them for another Ticket.

## Load Protocol Just in Time

Do not preload every Reference.

1. At entry, read [scheduler.md](references/scheduler.md), [events-and-recovery.md](references/events-and-recovery.md), and the configured runtime through [tracker-operations.md](references/tracker-operations.md).
2. Before creating a Coder, read [coder.md](references/coder.md).
3. Before creating Ticket Reviewers, read [reviewers.md](references/reviewers.md).
4. When repair, integration, or a merge conflict becomes relevant, read [repair-and-integration.md](references/repair-and-integration.md).
5. When a Spec becomes eligible for final acceptance, read [acceptance.md](references/acceptance.md).
6. For a multi-Spec run or a state conflict, also read [domain-and-state.md](references/domain-and-state.md).

Follow the selected Reference completely. Do not invent unloaded protocol details.

## Entry Gate

Accept only:

- `run-initiative <spec-ref>` for one formal Spec;
- `run-initiative <initiative-ref>` for one persisted multi-Spec Initiative;
- `run-initiative <spec-ref...>` to preview a multi-Spec Initiative and idempotently create or reuse its parent Tracker Item only after explicit user confirmation.

Before the first write, read repository instructions, `docs/agents/issue-tracker.md`, relevant `CONTEXT.md` files and ADRs, the complete formal Tracker items, and current Git facts. Verify the Tracker runtime, authentication, permissions, Integration Policy, revisions, dependencies, target branch, and worktree. Refuse to start a new Ticket from an unowned dirty worktree; never absorb unrelated user changes into a candidate Commit.

Return `FAILED_PRECONDITION` without publishing a Claim or creating a child when a required input, permission, or runtime capability is missing. For legacy `PLAN.md` or `LEDGER.md`, offer migration or pinning to `2.5.0`; do not interpret either under the new semantics.

## Serial Scheduler Loop

1. Create or recover the single valid root Scheduler Run and win its deterministic Claim.
2. Requery the Frontier from native Tracker facts. Never keep a stale Frontier snapshot.
3. Claim exactly one Ticket through the configured native mechanism. Do not start another Ticket until this one completes, pauses, or is cancelled.
4. Refresh the declared target or Integration Branch, freeze the Ticket Base from its current Head, and prepare the Ticket Branch. Create a fresh isolated Coder with a self-contained Role Task Pack. The Coder implements, validates, and creates the candidate Commit.
5. Validate the Coder result before persisting it: the reported Head must equal the Ticket Branch Head, every Ticket change must be committed, and no unrelated worktree change may enter the candidate. Pause on `IMPLEMENTATION_BLOCKED`; route `CONTRACT_BLOCKER` to user adjudication. For `READY_FOR_REVIEW` or `NO_CHANGE_REQUIRED`, freeze the candidate Base/Head.
6. Create fresh isolated Spec and Standards Reviewers. They may run concurrently inside the active Ticket, but both remain read-only and review the same fixed Commit range.
7. Collect both Verdicts privately. Do not publish either result where the other Reviewer could read it. After both finish, validate their bindings and persist one combined `REVIEW_RESULT`. If either returns `REVIEW_BLOCKED`, continue only that Reviewer when access to identical frozen input is restored; if any shared input changes, invalidate both results and continue both original Reviewers. Otherwise pause without consuming a repair round.
8. On `REPAIR_REQUIRED`, continue the original Coder with both axes' Findings, then continue each original Reviewer with only its own axis history. Any changed Head invalidates both previous Verdicts.
9. After two `PASS` Verdicts for the unchanged Base/Head, integrate through the configured policy. The Scheduler owns remote publication, PR/MR handling, Required Checks, merge, and Tracker closure; it does not modify the implementation.
10. Record the Integration Result, close the Ticket, release its native Claim according to the configured runtime, stop dispatching to its child threads, and requery the Frontier.
11. For one Spec, start fresh Spec Acceptance after all its Tickets integrate and close it only on `PASS`. For multiple Specs, wait until every Initiative Ticket integrates, freeze one final target Commit, then run each fresh Spec Acceptance sequentially against that same Commit while keeping every member Spec Open.
12. After all member Spec Verdicts have `PASS`, run fresh Initiative Acceptance. Only on Initiative `PASS`, close the member Specs and then the Initiative parent last. After root closure, release the root Scheduler Claim according to the configured runtime.

## Terminal States

- `COMPLETED`: every applicable Acceptance level has `PASS`, final Git integration is verified, and the root Item is closed last.
- `PAUSED`: ordinary repair is exhausted, human merge is pending, a required child cannot be created, Review or Acceptance input is blocked, required checks are externally blocked, or recovery facts conflict. Keep the root Item Open and preserve the Claim for the original Run.
- `CONTRACT_BLOCKER`: the contract, Scope, Spec, or ADR requires user adjudication. Persist it as a paused Run without consuming ordinary repair rounds.
- `PAUSED_FOR_ACCEPTANCE_REPAIR`: final acceptance found work that needs a formal Ticket. Persist the Findings and repair key, keep the root Open, and tell the user to invoke `$to-tickets` explicitly. Do not create or invoke it yourself.
- `CANCELLED`: record cancellation, stop dispatching and best-effort interrupt currently running child threads, release only this Run's Claims, and preserve candidate Git evidence.
- `FAILED_PRECONDITION`: fail before any Claim or child starts.

Do not create or update `PLAN.md`, `LEDGER.md`, or execution-state labels. Do not add host-specific child configuration to Role Task Packs. Do not let the Coder approve, publish, merge, or close its own work. Do not treat Reviewer `PASS`, an unmerged PR/MR, or a completed child thread as delivery completion.
