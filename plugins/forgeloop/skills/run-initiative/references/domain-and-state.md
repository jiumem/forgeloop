# Domain and State Contract

## Domain Objects

- **Initiative**: one user-authorized delivery scope. A single Spec is its own run root. Multiple Specs use one persisted parent Tracker Item with a confirmed member set and derived Initiative Revision.
- **Spec**: the formal delivery contract, including Revision, target branch, Scope, and `Delivery Acceptance`; an optional `Release Boundary` only records post-delivery actions.
- **Ticket**: the smallest vertical slice that a fresh Coder can implement and two fresh Reviewers can verify through a public Seam.
- **Frontier**: the Ticket Frontier of all Open, Unblocked, Unclaimed Tickets inside the authorized scope.
- **Agent Run**: the durable execution evidence for one Ticket: Coder result, fixed candidate Commit, two independent Verdicts, repair rounds, and Integration Result. Child thread identity is not durable state.
- **Review Verdict**: one axis's `PASS`, `REPAIR_REQUIRED`, or `REVIEW_BLOCKED`, bound to a fixed Base, Head, and Spec Revision.

## Sources of Truth

- Use `CONTEXT.md` for domain terminology and ADRs for durable architectural decisions.
- Use the configured Tracker for Specs, Tickets, membership, dependencies, native Claims, discussions, and Open/Closed state.
- Use Branch, Commit, PR/MR, checks, and merge facts for candidate implementation and integration.
- Use code, tests, and observable validation evidence for behavior.
- Use the formal Spec's `Delivery Acceptance` as the single source of truth for Spec completion. Ticket Acceptance criteria govern only their Ticket slices.

Append-only checkpoints explain what a Run observed and decided. They never override native Tracker or Git facts. Stop recovery when the two conflict; do not choose whichever is convenient.

## Invariants

1. Allow one valid root Scheduler Run and at most one active Ticket per Initiative.
2. Keep the root Run Claim on the Spec or Initiative parent. Express the current Ticket Claim through the configured native Tracker mechanism, not a duplicate Event.
3. Use a fresh Coder and two fresh isolated Reviewers for every Ticket. Reuse those live threads only for repair of that Ticket; create fresh children after Scheduler-task recovery.
4. Make the Coder implement and validate, Reviewers judge read-only fixed Commits, and the Scheduler orchestrate integration and state writes.
5. Hold both Ticket Reviewer results until both finish, then persist one combined review checkpoint. Never expose one axis to the other.
6. Invalidate both Verdicts whenever code, Base, Head, Spec Revision, or final target changes.
7. Close a Ticket only after integration. Close a single Spec only after its fresh Acceptance `PASS`. In a multi-Spec Run, keep member Specs Open through Initiative Acceptance; on Initiative `PASS`, close the valid member Specs first and the Initiative parent last.
8. Keep `PAUSED` Items Open and reserve the Claim for the original Run. On `CANCELLED`, release only that Run's Claims and never represent it as `COMPLETED`.
9. Keep every `Release Boundary` Tracking reference and Post-delivery action outside the Ticket Frontier, Spec Scope, and Initiative membership.

## Forbidden Secondary State

Do not create `PLAN.md`, `LEDGER.md`, execution-state labels, a separate event database, or a child-thread registry. Do not copy Tracker relationships into repository files. Local Markdown is the configured Tracker, not a mirror.
