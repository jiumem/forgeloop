# Domain and State Contract

## Domain Objects

- **Initiative**: one user-authorized delivery scope. A single Spec is its own run root. Multiple Specs use one persisted parent Tracker Item with a confirmed member set and derived Initiative Revision.
- **Spec**: the formal delivery contract, including Revision, target branch, Scope, and `Delivery Acceptance`; an optional `Release Boundary` only records post-delivery actions.
- **Ticket**: the smallest vertical slice that a fresh Coder can implement and two fresh Reviewers can verify through a public Seam.
- **Frontier**: the Ticket Frontier of all Open, Unblocked, Unclaimed Tickets inside the authorized scope.
- **Agent Run**: the durable execution evidence for one Ticket: Coder result, fixed candidate Commit, two independent Verdicts, repair rounds, and Integration Result. Child thread identity is not durable state.
- **Review Verdict**: one axis's `PASS`, `REPAIR_REQUIRED`, or `REVIEW_BLOCKED`, bound to a fixed Base, Head, and Spec Revision.
- **Branch Topology**: `INDEPENDENT` or user-approved `SHARED`; it describes where Ticket Candidates integrate, not who may merge.
- **Shared-branch Reason**: `WIDE_REFACTOR`, `NON_GREEN_MIGRATION`, `ATOMIC_DELIVERY`, or `CUMULATIVE_AUDIT`; it justifies `SHARED` without replacing Integration Policy.
- **Integration Policy**: `auto-merge` or `human-merge`; it alone governs merge authority under the configured runtime.

## Sources of Truth

- Use `CONTEXT.md` for domain terminology and ADRs for durable architectural decisions.
- Use the configured Tracker for Specs, Tickets, membership, dependencies, native Claims, discussions, and Open/Closed state.
- Use Branch, Commit, PR/MR, checks, and merge facts for candidate implementation and integration.
- Use code, tests, and observable validation evidence for behavior.
- Use the formal Spec's `Delivery Acceptance` as the single source of truth for Spec completion. Ticket Acceptance criteria govern only their Ticket slices.

Append-only checkpoints explain what a Run observed and decided. They never override native Tracker or Git facts. Stop recovery when the two conflict; do not choose whichever is convenient.

## Evidence Bindings

### Candidate Review

Bind each Ticket Review to immutable inputs:

```yaml
review_base: <frozen reviewed Base commit>
candidate_head: <reviewed Head commit>
spec_revision: <formal Spec revision>
coder_evidence: <bound shared evidence references>
```

The review_base is an immutable Commit, not a moving alias. The target reference moving alone does not invalidate unchanged dual `PASS` Verdicts. Invalidate both Verdicts only when candidate code, review_base, candidate_head, Spec Revision, or bound shared Coder evidence changes. A rebase, target merge into the Candidate Branch, or conflict repair changes the Candidate Head and therefore requires renewed Coder validation and dual Review.

### Integration Result

Bind each non-empty Integration Result to:

```yaml
candidate_head: <reviewed Candidate commit>
target_before: <target commit immediately before integration>
target_after: <target commit produced or confirmed by integration>
integration_method: <merge | squash | already_present | configured native method>
native_ref: <PR/MR, checks, and merge evidence>
```

This binding proves how one reviewed Candidate entered one observed target history. It does not change the Candidate Review binding.

### Final Acceptance

A confirmed root Acceptance binds:

```yaml
acceptance_level: <SPEC | INITIATIVE>
subject_revision: <subject reference and revision>
membership: <confirmed members when applicable>
final_target_commit: <accepted immutable target commit>
idempotency_key: <stable acceptance checkpoint key>
native_checkpoint_ref: <confirmed native reference>
```

This binding is the Acceptance Seal. It proves the approved Delivery Acceptance at one immutable Commit, not the behavior of future target commits.

## Invariants

1. Allow one valid root Scheduler Run and at most one active Ticket per Initiative.
2. Keep the root Run Claim on the Spec or Initiative parent. Express the current Ticket Claim through the configured native Tracker mechanism, not a duplicate Event.
3. Use a fresh Coder and two fresh isolated Reviewers for every Ticket. Reuse those live threads only for repair of that Ticket; create fresh children after Scheduler-task recovery.
4. Make the Coder implement and validate, Reviewers judge read-only fixed Commits, and the Scheduler orchestrate integration and state writes.
5. Hold both Ticket Reviewer results until both finish, then persist one combined review checkpoint. Never expose one axis to the other.
6. Keep Candidate Review, Integration Result, and Final Acceptance evidence bound to their own immutable inputs; apply each binding's own invalidation rule.
7. Close a Ticket only after integration. Close a single Spec only after its fresh Acceptance `PASS`. In a multi-Spec Run, keep member Specs Open through Initiative Acceptance; on Initiative `PASS`, close the valid member Specs first and the Initiative parent last.
8. Keep `PAUSED` Items Open and reserve the Claim for the original Run. On `CANCELLED`, release only that Run's Claims and never represent it as `COMPLETED`.
9. Keep every `Release Boundary` Tracking reference and Post-delivery action outside the Ticket Frontier, Spec Scope, and Initiative membership.

## Forbidden Secondary State

Do not create `PLAN.md`, `LEDGER.md`, execution-state labels, a separate event database, or a child-thread registry. Do not copy Tracker relationships into repository files. Local Markdown is the configured Tracker, not a mirror.
