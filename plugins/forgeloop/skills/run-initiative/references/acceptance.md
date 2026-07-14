# Final Acceptance

## Ticket Gate

Close a Ticket only after the Coder supplied Acceptance evidence and final-Head validation, both Ticket Reviewers returned `PASS` for the same unchanged Base/Head and Spec Revision, the candidate entered the declared branch according to Integration Policy, required native checks passed, and the Tracker records the candidate and Integration Result.

Two Ticket Verdicts without integration mean only `READY_FOR_MERGE`. A closed but unmerged PR/MR is not complete. `NO_CHANGE_REQUIRED` completes through an `ALREADY_PRESENT` Integration Result after the same dual review.

## Acceptance Reviewer

Always create a fresh isolated, read-only Acceptance Reviewer after integration. Do not retain or reuse a Ticket Reviewer for final acceptance.

Give the Acceptance Reviewer a self-contained Role Task Pack containing:

- `level: SPEC | INITIATIVE` and the formal parent reference and revision;
- the final target Commit and target branch;
- member Specs or Tickets and their native completion facts plus each Ticket's complete Integration binding;
- the applicable formal Spec or member Specs' `Delivery Acceptance` with stable references, cross-item Dependencies, delivery evidence, validation entry points, known limitations, and any `Release Boundary` for reporting only;
- explicit read-only permissions and the required Verdict.

The Reviewer must inspect the final target tree and return:

```yaml
level: SPEC | INITIATIVE
verdict: PASS | REPAIR_REQUIRED | ACCEPTANCE_BLOCKED
subject_ref: <ref>
revision: <revision>
final_commit: <sha>
findings:
  - finding_id: <stable-id>
    evidence: <observable evidence>
    observed: <actual>
    expected: <required>
    repair_check: <observable check>
```

The Reviewer judges only `Delivery Acceptance` and does not execute or validate any Post-delivery Release Action. It must not edit code, Tracker items, Specs, Tickets, or acceptance criteria, and must not create repair work. Return `ACCEPTANCE_BLOCKED` only when the frozen parent, revision, final Commit, membership, or required evidence cannot be read or validated; explain the missing input in Findings.

Before `PASS`, verify that every Integration `target_after` is an ancestor of or equal to the final target Commit. If a force-push or history rewrite removes an integrated target_after, return `REPAIR_REQUIRED` through the existing Acceptance Repair Boundary with the missing integration evidence. Ancestry alone is not behavior proof: a later revert may preserve ancestry, so still inspect the final tree, public Seams, and observable `Delivery Acceptance` behavior.

## Acceptance Seal

After an Acceptance Reviewer returns `PASS`, refresh the target before rendering its Payload. If it no longer equals `final_commit`, publish no `PASS`; rerun the applicable Acceptance on the new final Commit. The last successful target refresh is the Seal eligibility linearization point.

The Acceptance Seal is a name for the existing confirmed root `ACCEPTANCE_RESULT: PASS`, not a new Event or state. It gains durable existence only after #12 literal-safe transport and exact native read-back confirm the complete Payload. A failed, ambiguous, missing, truncated, or mismatched write forms no Seal; recovery or retry must refresh the target again. The Seal binds the acceptance level, subject and revision, applicable confirmed membership, final target Commit, idempotency key, and native checkpoint reference. CLI success, a `PASS` substring, or partial-field matching is insufficient.

For a single Spec, its confirmed final Spec `PASS` is the root Seal. In a multi-Spec Run, member Spec results remain provisional, must all bind the same final Commit, and form a root Seal only when the matching Initiative `PASS` is confirmed. Target drift before the eligibility refresh invalidates current Acceptance and restarts the applicable same-Commit sequence. Drift after that successful refresh counts as post-seal when the pending Payload later passes exact read-back, even if the Scheduler observes the drift before confirmation; it must not invalidate the Seal, rerun Acceptance, rewrite history, or reopen the Run. If publication is not confirmed, no Seal exists and recovery must refresh again.

After the Seal exists, Tracker closure and Claim release are administrative. Recovery resumes any unfinished member closure, root closure, or Claim release from the Seal even if the target has since advanced.

## Spec Gate

Run fresh Spec Acceptance only when every Ticket in the current Scope is integrated, no Open, Blocked, repair, or pending human-merge Ticket remains, confirmed Scope has not drifted, and the final target Commit is known. Verify every `Delivery Acceptance` reference against the final target and persist `ACCEPTANCE_RESULT level=SPEC` with the delivery summary, validation entry point, evidence, limitations, and final references. For a single-Spec Run, close the Spec only on `PASS`.

For a multi-Spec Initiative, defer every Spec Acceptance until all Initiative Tickets are integrated. Freeze one final target Commit, then run each member Spec Acceptance sequentially against that same Commit while keeping all member Specs Open. If the target changes during this sequence, invalidate completed Acceptance Verdicts and restart the sequence from the new final Commit.

## Initiative Gate

A single-Spec Initiative completes with its Spec. For multiple Specs, create a fresh Initiative Acceptance Reviewer only after every member Spec passed, cross-Spec Dependencies are resolved, the confirmed member set and Initiative Revision remain valid, and all delivery entered the final target. Judge only the member Specs' `Delivery Acceptance`; use cross-Spec invariants only as evidence for the Delivery Acceptance items that reference them, never as a parallel completion standard. Persist `ACCEPTANCE_RESULT level=INITIATIVE` and record cross-Spec evidence and limitations. Only on Initiative `PASS`, close the member Specs whose Acceptance still binds to the frozen final Commit, then close the Initiative parent last.

An unexecuted Post-delivery Release Action is not an Acceptance failure and must not return `REPAIR_REQUIRED`. When a Spec has a `Release Boundary`, preserve its Tracking reference verbatim in the completion report. `run-initiative` must not mutate the referenced item's Open/Closed state, assignee, labels, or comments; they must remain unchanged.

For `ACCEPTANCE_BLOCKED`, correct a Scheduler-supplied frozen input and continue the same Acceptance Reviewer when possible. Otherwise persist `ACCEPTANCE_RESULT`, then `RUN_PAUSED` with reason=`ACCEPTANCE_BLOCKED`. Do not derive a repair key, create repair work, or consume an ordinary repair round.

## Acceptance Repair Boundary

On `REPAIR_REQUIRED`, keep every affected parent Open and derive a stable `repair_key` from the Acceptance level, parent reference, revision, final Commit, and `finding_id`. Search for an existing formal Open repair Ticket with that key.

- If `$to-tickets` already created a matching in-scope Ticket, reuse it through the ordinary Frontier after validating its relationship and revision.
- If no matching Ticket exists, persist `RUN_PAUSED` with reason=`ACCEPTANCE_REPAIR`, report the Findings and repair key, and tell the user to invoke `$to-tickets` explicitly.
- For Spec Acceptance, use that Spec as `owning_spec_ref`. For Initiative Acceptance, give every repair slice one existing member Spec `owning_spec_ref` whose approved Scope covers it; use coordinated Tickets under multiple member Specs when genuinely required. Do not create a Ticket directly under the Initiative.
- Route to `CONTRACT_BLOCKER` when repair changes Scope, Spec, ADR, or confirmed Initiative membership.

After an Initiative repair changes the final target Commit, invalidate all member Spec Acceptance Verdicts and repeat the complete Spec Acceptance sequence before Initiative Acceptance. Because member Specs remain Open until Initiative `PASS`, do not introduce a reopen state.

Do not let `run-initiative` create, delete, rewrite, or implicitly invoke work that belongs to `$to-tickets`. Do not rewrite historical Ticket Verdicts.

## Material Revisions

Treat spelling, formatting, links, behavior-preserving clarification, and movement of the declared target branch Head as non-material. Treat changes to the Problem, Actor, goal, `Delivery Acceptance`, Ticket Acceptance criteria, failure states, permissions, Scope, interface, Schema, migration, Seam, declared delivery target identity or policy, or Initiative membership as material.

For a material change, require user confirmation, persist `RUN_PAUSED` with reason=`SPEC_CHANGE`, and expose `PAUSED_FOR_SPEC_CHANGE`. Resume only after the user explicitly invokes `$to-tickets` to reconcile Open Tickets and the Scheduler validates the new revision. Preserve completed history and invalidate affected Verdicts and Acceptance eligibility. When the core Problem, Actor, or delivery target is replaced, require a new Spec and mark the old one `SUPERSEDED` through the appropriate planning workflow.
