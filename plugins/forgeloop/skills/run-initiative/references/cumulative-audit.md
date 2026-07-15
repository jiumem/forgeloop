# Cumulative PR/MR Audit

Load this protocol after [final-integration-gate.md](final-integration-gate.md) only when the approved Ticket graph declares `Branch topology: SHARED` with reason `CUMULATIVE_AUDIT`. It extends neither Integration Policy nor permissions. Return `FAILED_PRECONDITION` for an undeclared runtime switch, fewer than two implementation Tickets, a missing native PR/MR runtime, or Local.

## Cumulative Delivery Range

Use immutable `spec_delivery_base` from the existing `RUN_CLAIMED` Payload, and freeze the Integration Branch Head as `delivery_head` when the Final Integration Gate starts. Keep these Git bindings distinct:

- `review_base / candidate_head`: immutable dual-Verdict inputs for each ordinary Ticket.
- `spec_delivery_base / delivery_head`: the complete Spec delivery range, not a new Verdict input.
- `target_before / target_after`: the final native Spec Integration Result.

The Gate proves that `spec_delivery_base...delivery_head` contains every approved Ticket and no unattributed Commit, retains every Ticket-to-Candidate-to-Integration mapping, and executes the parent Validation Entries and every existing owner-referenced Proof on the fixed Head. Cumulative audit gains no invariant ownership and creates no second Verdict schema. Return `CONTRACT_BLOCKER` for a required Contract, Proof mapping, Spec, ADR, Scope, product behavior, or target change.

## Native Audit Projection

After range and behavior evidence pass, create or reuse one valid native PR/MR identity for the exact Spec reference, revision, `delivery_head`, and target. Query native facts after an ambiguous create: reuse one unique match and stop on conflicts or multiple matches. Do not maintain a long-lived Draft PR/MR from the first Ticket.

Generate the body from Tracker and Git native facts. Include:

- Spec reference and revision;
- `spec_delivery_base...delivery_head`, declared target, and current target Commit;
- every completed in-Scope Ticket;
- each Ticket Candidate, dual Verdicts, and Integration Result mapping;
- Cross-seam Invariants and their existing Proof entry points;
- Required Checks, final validation evidence, known limitations, and any explicit Release Boundary.

The body is an audit projection, not a source of truth. Ticket state, Checkpoints, Commits, native PR/MR, merge facts, and Final Acceptance retain ownership. Regenerate a missing, stale, or conflicting projection from native facts; never use it to overwrite them.

Use the Final Integration Gate's literal-safe write and exact native read-back rules. The projection is not a Durable Checkpoint and adds no Event, parser, or fact source.

## PR/MR Lifecycle

Use this order: fixed `delivery_head` → create or reuse PR/MR → Required Checks → refresh projection → literal-safe write → exact read-back → merge. Checks that exist only after PR/MR creation are never creation prerequisites.

A Head change invalidates old Gate evidence, Checks, and projection. Complete the ordinary repair Ticket, rebind `delivery_head`, and refresh the same PR/MR. Read-only target, mergeability, Check, or projection refresh creates no Ticket and consumes no repair budget.

Under `human-merge`, use the existing `RUN_PAUSED reason=READY_FOR_HUMAN_MERGE` only after Checks and the latest exact body read-back pass, keeping the Spec Open. Under `auto-merge`, require the fixed Head, current target combination, Required Checks, protection, permissions, and projection.

The cumulative PR/MR proves only Git delivery eligibility. After merge, record Spec-level `target_before / target_after`, then run fresh Spec Acceptance on the actual `target_after`; PR/MR readability, approval, or mergeability never substitutes for Acceptance.

## Scope

One approved Spec revision and target has at most one cumulative PR/MR. A multi-Spec Initiative may have one per applicable member Spec but must not aggregate multiple Specs into one PR/MR or create an integration owner under the Initiative. Local has no cumulative PR/MR surface and rejects `CUMULATIVE_AUDIT`; its other legal SHARED reasons remain available.

Do not add Stacked PRs, a Draft PR phase, Reviewer type, Event, terminal state, repair budget, Tracker Item type, or second fact source.
