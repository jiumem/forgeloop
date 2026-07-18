---
name: run-initiative
description: Load when the user explicitly wants to execute, resume, recover, or cancel delivery from a formal Tracker Spec or persisted Initiative.
---

# Run an Initiative

Treat the configured Tracker as the sole source of truth for Specs, Tickets, dependencies, Claims, and live delivery state. Use the primary context as a thin Scheduler. Run one Ticket at a time. For each repair cycle, use one Coder and two isolated, read-only Reviewers; keep child identity out of durable state.

## Load Protocol Just in Time

Do not preload every Reference.

1. At entry, read [scheduler.md](references/scheduler.md), [events-and-recovery.md](references/events-and-recovery.md), and the configured runtime through [tracker-operations.md](references/tracker-operations.md).
2. For any declared `SHARED` topology, read [final-integration-gate.md](references/final-integration-gate.md) before the root Claim; when its reason is `CUMULATIVE_AUDIT`, also read [cumulative-audit.md](references/cumulative-audit.md).
3. Before creating a Coder, read [coder.md](references/coder.md).
4. Before creating Ticket Reviewers, read [reviewers.md](references/reviewers.md).
5. When repair, integration, or a merge conflict becomes relevant, read [repair-and-integration.md](references/repair-and-integration.md).
6. When a Spec becomes eligible for final acceptance, read [acceptance.md](references/acceptance.md).
7. For a multi-Spec run or a state conflict, also read [domain-and-state.md](references/domain-and-state.md).
8. When `CONTRACT_BLOCKER` requires user adjudication, read [contract-reconciliation.md](references/contract-reconciliation.md) before asking the user or changing any contract fact.

Follow the selected Reference completely. Do not invent unloaded protocol details.

## Entry Gate

Accept only:

- `run-initiative <spec-ref>` for one formal Spec;
- `run-initiative <initiative-ref>` for one persisted multi-Spec Initiative;
- `run-initiative <spec-ref...>` to preview a multi-Spec Initiative and idempotently create or reuse its parent Tracker Item only after explicit user confirmation.

Before the first write, read repository instructions, `docs/agents/issue-tracker.md`, relevant `CONTEXT.md` files and ADRs, the complete formal Tracker items, and current Git facts. Verify the Tracker runtime, authentication, permissions, Integration Policy, revisions, dependencies, target branch, and worktree. Refuse to start a new Ticket from an unowned dirty worktree; never absorb unrelated user changes into a candidate Commit.

Return `FAILED_PRECONDITION` without publishing a Claim or creating a child when a required input, permission, or runtime capability is missing. For legacy `PLAN.md` or `LEDGER.md`, offer migration or pinning to `2.5.0`; do not interpret either under the new semantics.

## Serial Scheduler Loop

1. Freeze every binding required by the loaded protocols, then create or recover the single valid root Scheduler Run and win its deterministic Claim.
2. Requery the Frontier from native Tracker facts. Never keep a stale Frontier snapshot.
3. Claim exactly one Ticket through the configured native mechanism. Do not start another Ticket until this one completes, pauses, or is cancelled.
4. Refresh the declared target or Integration Branch, freeze the Ticket Base from its current Head, and prepare the Ticket Branch. Create a fresh isolated Coder with a self-contained Role Task Pack containing the approved Validation Entries, public Seam, Acceptance Prerequisites, and validation evidence contract. The Coder follows that contract-bound validation path; for a reproducible behavior change it invokes `$tdd` before modifying production code, while behavior-preserving and declared external paths keep their approved evidence semantics. It then implements, validates, and creates the candidate Commit.
5. Validate the Coder result before persisting it: the reported Head must equal the Ticket Branch Head, every Ticket change must be committed, no unrelated worktree change may enter the candidate, and the evidence must be complete and bound to the approved strategy, Base, and Head. Do not impose universal Red/Green or judge evidence credibility; the Reviewers own that semantic judgment. Pause on `IMPLEMENTATION_BLOCKED`; route `CONTRACT_BLOCKER` to user adjudication. For `READY_FOR_REVIEW` or `NO_CHANGE_REQUIRED`, freeze the candidate Base/Head.
6. Create fresh isolated Spec and Standards Reviewers. They may run concurrently inside the active Ticket, but both remain read-only and review the same fixed Commit range.
7. Collect both Verdicts privately. Do not publish either result where the other Reviewer could read it. After both finish, validate their bindings and persist one combined `REVIEW_RESULT`. If either returns `REVIEW_BLOCKED`, continue only that Reviewer when access to identical frozen input is restored; if any shared input changes, invalidate both results and continue both original Reviewers. Otherwise pause without consuming a repair round.
8. On any repair trigger, continue the current-cycle Coder for an independent read-only Repair Diagnosis turn with the complete evidence and history. Validate its fields and route its classification without reinterpreting Findings. Only an authorized `LOCAL_REPAIR` or `STRUCTURAL_REPAIR` may enter a subsequent code-changing Coder turn; any changed Head invalidates both previous Verdicts, after which each current-cycle Reviewer receives only its own axis history. After the third failed repair, exactly confirm `RUN_PAUSED / REPAIR_BUDGET`, then use a fresh Coder for semantic, read-only Exhaustion Diagnosis. A winning `AUTO_REPAIR_RENEWAL` keeps the same Ticket, Run, and Branch and starts a fresh three-round cycle without user approval.
9. On `CONTRACT_BLOCKER`, keep contract writes at zero until the Contract Reconciliation protocol has completed internal Design Review and one exact user decision has been published and read back. A bound approval lets the Scheduler orchestrate the existing contract-owning Skills without additional user invocations or approvals.
10. After two `PASS` Verdicts for the unchanged Base/Head, integrate the Candidate into the declared target for `INDEPENDENT`, or into the approved Spec Integration Branch for `SHARED`. The Scheduler owns remote publication, PR/MR handling, Required Checks, integration, and Tracker closure; it does not modify the implementation.
11. For a SHARED Spec, close an ordinary Ticket after it enters the Integration Branch. Record its Ticket Integration Result, release its native Claim, stop dispatching to its child threads, and requery the Frontier.
12. For a single-Spec Run, after all ordinary Tickets complete, let the Spec Root Final Integration Gate deliver a `SHARED` Spec to the target; `INDEPENDENT` uses its existing Ticket Integration Results. Then run fresh Spec Acceptance on the actual final Commit and close the Spec only on `PASS`.
13. For a multi-Spec Run, after all Initiative Tickets complete, execute each SHARED member Spec's Final Integration Gate independently. After every member delivery enters the target, freeze one final Commit and run each Spec Acceptance sequentially against that same Commit while keeping member Specs Open.
14. After all member Spec Verdicts have `PASS`, run fresh Initiative Acceptance. Only on Initiative `PASS`, close the member Specs and then the Initiative parent last. After root closure, release the root Scheduler Claim according to the configured runtime.

## Delivery Completion Report

Final Acceptance judges only the formal Specs' `Delivery Acceptance`. If a completed Spec declares a `Release Boundary`, close it under the existing single- or multi-Spec rule and report: `Delivery is complete; Release was not executed by this Run`, followed by its Post-delivery action and Tracking reference.

A Tracking reference is read-only context outside delivery scope. This Workflow must not create, claim, update, or close the referenced external item. It must not add a dedicated Reviewer, Acceptance level, Event, terminal state, repair budget, permission, or automatic release action.

## Terminal States

- `COMPLETED`: every applicable Acceptance level has `PASS`, final Git integration is verified, and the root Item is closed last.
- `PAUSED`: ordinary repair is exhausted, human merge is pending, a required child cannot be created, Review or Acceptance input is blocked, required checks are externally blocked, or recovery facts conflict. Keep the root Item Open and preserve the Claim for the original Run.
- `CONTRACT_BLOCKER`: the contract, Scope, Spec, or ADR requires user adjudication. Persist it as a paused Run without consuming ordinary repair rounds.
- `PAUSED_FOR_ACCEPTANCE_REPAIR`: final acceptance found work that needs a formal Ticket. Persist the Findings and repair key, keep the root Open, and tell the user to invoke `$to-tickets` explicitly. Do not create or invoke it yourself.
- `CANCELLED`: record cancellation, stop dispatching and best-effort interrupt currently running child threads, release only this Run's Claims, and preserve candidate Git evidence.
- `FAILED_PRECONDITION`: fail before any Claim or child starts.

Do not create or update `PLAN.md`, `LEDGER.md`, or execution-state labels. Do not add host-specific child configuration to Role Task Packs. Do not let the Coder approve, publish, merge, or close its own work. Do not treat Reviewer `PASS`, an unmerged PR/MR, or a completed child thread as delivery completion.
