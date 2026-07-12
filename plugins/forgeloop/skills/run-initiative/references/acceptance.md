# Final Acceptance

## Ticket Gate

Close a Ticket only after the Coder supplied Acceptance evidence and final-Head validation, both Ticket Reviewers returned `PASS` for the same unchanged Base/Head and Spec Revision, the candidate entered the declared branch according to Integration Policy, required native checks passed, and the Tracker records the candidate and Integration Result.

Two Ticket Verdicts without integration mean only `READY_FOR_MERGE`. A closed but unmerged PR/MR is not complete. `NO_CHANGE_REQUIRED` completes through an `ALREADY_PRESENT` Integration Result after the same dual review.

## Acceptance Reviewer

Always create a fresh isolated, read-only Acceptance Reviewer after integration. Do not retain or reuse a Ticket Reviewer for final acceptance.

Give the Acceptance Reviewer a self-contained Role Task Pack containing:

- `level: SPEC | INITIATIVE` and the formal parent reference and revision;
- the final target Commit and target branch;
- member Specs or Tickets and their native completion and integration facts;
- Acceptance Criteria, cross-item Dependencies, delivery evidence, validation entry points, and known limitations;
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

The Reviewer must not edit code, Tracker items, Specs, Tickets, or acceptance criteria, and must not create repair work. Return `ACCEPTANCE_BLOCKED` only when the frozen parent, revision, final Commit, membership, or required evidence cannot be read or validated; explain the missing input in Findings.

## Spec Gate

Run fresh Spec Acceptance only when every Ticket in the current Scope is integrated, no Open, Blocked, repair, or pending human-merge Ticket remains, confirmed Scope has not drifted, and the final target Commit is known. Persist `ACCEPTANCE_RESULT level=SPEC` and record the delivery summary, validation entry point, evidence, limitations, and final references. For a single-Spec Run, close the Spec only on `PASS`.

For a multi-Spec Initiative, defer every Spec Acceptance until all Initiative Tickets are integrated. Freeze one final target Commit, then run each member Spec Acceptance sequentially against that same Commit while keeping all member Specs Open. If the target changes during this sequence, invalidate completed Acceptance Verdicts and restart the sequence from the new final Commit.

## Initiative Gate

A single-Spec Initiative completes with its Spec. For multiple Specs, create a fresh Initiative Acceptance Reviewer only after every member Spec passed, cross-Spec Dependencies are resolved, the confirmed member set and Initiative Revision remain valid, and all delivery entered the final target. Persist `ACCEPTANCE_RESULT level=INITIATIVE` and record cross-Spec evidence and limitations. Only on Initiative `PASS`, close the member Specs whose Acceptance still binds to the frozen final Commit, then close the Initiative parent last.

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

Treat spelling, formatting, links, and behavior-preserving clarification as non-material. Treat changes to the Problem, Actor, goal, Acceptance Criteria, failure states, permissions, Scope, interface, Schema, migration, Seam, target, or Initiative membership as material.

For a material change, require user confirmation, persist `RUN_PAUSED` with reason=`SPEC_CHANGE`, and expose `PAUSED_FOR_SPEC_CHANGE`. Resume only after the user explicitly invokes `$to-tickets` to reconcile Open Tickets and the Scheduler validates the new revision. Preserve completed history and invalidate affected Verdicts and Acceptance eligibility. When the core Problem, Actor, or delivery target is replaced, require a new Spec and mark the old one `SUPERSEDED` through the appropriate planning workflow.
