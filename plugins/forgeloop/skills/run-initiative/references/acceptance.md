# Final Acceptance Seal

## Ticket Delivery Prerequisite

Close a Ticket only after the Coder supplied Acceptance evidence and final-Head validation, both Ticket Reviewers returned `PASS` for the same unchanged Base/Head and effective revisions, the Candidate entered the declared branch according to Integration Policy, required native checks passed, and the Tracker records its Integration Result.

Two Ticket Verdicts without integration mean only `READY_FOR_MERGE`. A closed but unmerged PR/MR is not complete. `NO_CHANGE_REQUIRED` completes through an `ALREADY_PRESENT` Integration Result after the same dual review.

## Seal Eligibility

The Scheduler owns Seal Eligibility after integration. It creates no final Reviewer, runs no new semantic review or end-to-end journey, and does not judge product correctness. Final Acceptance only proves that existing semantic evidence and native delivery facts still form one complete, internally consistent delivery bound to the final target Commit.

For a Spec, require all of the following before publishing `PASS`:

- every Ticket in confirmed Scope is Closed with two bound Ticket `PASS` Verdicts under the effective Spec, Ticket, ADR, and repair-cycle revisions;
- every Ticket has one valid Ticket Integration Result, and every reviewed Candidate is bound through its declared integration method to the delivered history;
- every stable `Delivery Acceptance` reference has an Owning Ticket and existing semantic evidence already judged by that Ticket's Spec Reviewer;
- every Cross-seam Proof has its approved Owning Ticket evidence, and every `SHARED` delivery also has passing Final Integration Gate evidence;
- no Open, Blocked, repair, pending human-merge, missing-check, or unresolved Final Gate Finding remains;
- every Integration `target_after` is an ancestor of or equal to the final target Commit, and the final target Commit is exactly the Commit covered by the latest applicable delivery validation;
- the Spec Revision, Scope, target identity, Integration Policy, and any required `Release Boundary` reference remain unchanged.

Use cross-Spec invariants only as evidence for the Delivery Acceptance items that reference them, never as a second Acceptance source. Read each Ticket's complete Integration binding; summaries or ancestry alone cannot substitute for the native provenance required above.

For an `INDEPENDENT` topology, the approved Ticket graph must assign every combined or Cross-seam behavior to an Owning Ticket whose Base includes its declared dependencies. Seal Eligibility does not invent a missing final proof owner. For `SHARED`, the Final Integration Gate is the last workflow stage permitted to produce an implementation Finding; Final Acceptance cannot create a new implementation Finding, rewrite a Ticket Verdict, or create repair work.

## Blocked Routes

Return `ACCEPTANCE_BLOCKED` only for an incomplete, stale, unreadable, or contradictory Seal input. Persist `ACCEPTANCE_RESULT result=ACCEPTANCE_BLOCKED` and then `RUN_PAUSED reason=ACCEPTANCE_BLOCKED` only when the owning action cannot finish immediately. Do not consume a repair round.

Every blocker has one existing owner and action:

- For failed or ambiguous checkpoint publication or read-back, refresh the target and retry the same literal-safe write with the same idempotency key; do not recompute product judgment.
- For target drift before the Seal, publish no `PASS` and return to the applicable Integration or Final Integration Gate on the new target facts. Reuse still-valid Ticket Verdicts only under their existing invalidation rules.
- For Spec Revision or confirmed membership drift, use the existing Spec Change or Contract Reconciliation path; Final Acceptance changes no contract fact.
- When Delivery Acceptance or Cross-seam Proof lacks an Owning Ticket or existing semantic proof, report that the upstream planning contract is incomplete and pause without inventing an owner, test, or repair item.
- When a Ticket Integration Result is missing or invalid, return to that Ticket's integration path; do not reinterpret review evidence as delivery.
- For pending Required Checks, protection, permissions, mergeability, or human merge, return to the existing integration path that owns that fact.

Final Acceptance has no implementation Finding, repair-ticket, or contract-writing path. A genuinely new product defect observed after delivery is new tracked work outside this completed Run, not a late mutation of its historical Verdicts.

## Acceptance Seal

After all eligibility checks pass, refresh the target immediately before rendering the Payload. If it no longer equals the eligible final target Commit, publish no `PASS` and follow the target-drift route above. This last successful target refresh is the Seal eligibility linearization point.

Publish the existing `ACCEPTANCE_RESULT` with:

```yaml
level: SPEC | INITIATIVE
result: PASS
subject_ref: <ref>
revision: <effective revision>
membership: <confirmed member refs and revisions when applicable>
final_commit: <final target Commit>
integration_refs: <complete Integration Result references>
evidence_refs: <existing Ticket and Final Gate semantic evidence>
limitations: <known approved limitations>
idempotency_key: <stable key>
```

The Acceptance Seal is the confirmed root `ACCEPTANCE_RESULT: PASS`, not a new Event, state, Reviewer type, or product judgment. It exists only after literal-safe publication and exact native read-back confirm the complete Payload. A failed, ambiguous, missing, truncated, or mismatched write forms no Seal. CLI success, a `PASS` substring, or partial-field matching is insufficient.

For a single Spec, its confirmed Spec `PASS` is the root Seal. In a multi-Spec Run, member Spec results remain provisional, must all bind the same final Commit, and form a root Seal only when the Initiative `PASS` binds that same final Commit and confirmed membership. Target drift before the eligibility refresh invalidates the pending result. Drift after the successful eligibility refresh is post-seal when the already-rendered Payload later passes exact read-back; it must not invalidate the Seal, rewrite history, or reopen the Run.

After the Seal exists, Tracker closure and Claim release are administrative. Recovery resumes unfinished member closure, root closure, or Claim release from the Seal even if the target has since advanced.

## Spec and Initiative Closure

Evaluate Spec Seal Eligibility only when every Ticket in that Spec is integrated and no delivery blocker remains. For a single-Spec Run, publish the confirmed Spec `PASS`, close the Spec, then release its root Claim.

For a multi-Spec Initiative, wait until all Initiative Tickets are integrated. Freeze one final target Commit, evaluate each member Spec sequentially against that same final Commit, publish provisional member Spec `PASS` results, keeping all member Specs Open. If the target changes before the Initiative Seal, invalidate the pending sequence and reevaluate eligibility against the new final Commit through the blocked route.

Evaluate Initiative Seal Eligibility only after every member Spec has a provisional `PASS`, cross-Spec Dependencies are resolved, confirmed membership and Initiative Revision remain valid, and all results bind the same final Commit. Publish `ACCEPTANCE_RESULT level=INITIATIVE result=PASS`. Only on Initiative `PASS` with exact read-back may the Scheduler close the member Specs, then close the Initiative parent last.

## Release Boundary

Final Acceptance does not execute or validate any Post-delivery Release Action. An unexecuted action does not block Seal Eligibility. Preserve every `Release Boundary` Tracking reference verbatim in the completion report. `run-initiative` must not mutate the referenced item's Open/Closed state, assignee, labels, or comments; they must remain unchanged.

## Material Revisions

Treat spelling, formatting, links, behavior-preserving clarification, and movement of the declared target branch Head as non-material. Treat changes to the Problem, Actor, goal, `Delivery Acceptance`, Ticket Acceptance criteria, failure states, permissions, Scope, interface, Schema, migration, Seam, declared delivery target identity or policy, or Initiative membership as material.

For a material change, require user confirmation, persist `RUN_PAUSED` with reason=`SPEC_CHANGE`, and expose `PAUSED_FOR_SPEC_CHANGE`. Resume only after the user explicitly invokes `$to-tickets` to reconcile Open Tickets and the Scheduler validates the new revision. Preserve completed history and invalidate affected Verdicts and Seal Eligibility. When the core Problem, Actor, or delivery target is replaced, require a new Spec and mark the old one `SUPERSEDED` through the appropriate planning workflow.
