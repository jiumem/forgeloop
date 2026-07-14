# Cumulative PR/MR Audit

Load this protocol only when the approved Ticket graph declares `Branch topology: SHARED` with reason `CUMULATIVE_AUDIT`. It extends neither Integration Policy nor permissions. Reject an undeclared runtime switch, a single implementation Ticket, a missing final `integrate-and-verify` Ticket, or a runtime without native PR/MR support before delivery work begins.

## Serial Shared-branch Delivery

When acquiring the first root Claim, freeze the current target Commit as `spec_delivery_base`. Persist the topology, reason, declared Integration Branch, and `spec_delivery_base` in the existing `RUN_CLAIMED` Payload. Only after winning the Claim and confirming exact native read-back, create the Branch from that exact Commit before starting a Ticket. Recovery uses the immutable binding; it never reinterprets a later target Head as the delivery Base. If the Branch or Claim already exists without one consistent binding, stop with `RECOVERY_CONFLICT`.

Run one ordinary Ticket at a time. Freeze its Base from the current Spec Integration Branch Head, use the normal Coder, dual Review, repair budget, and Integration Result, then close it as soon as its reviewed Candidate enters that Branch. Requery the Frontier before the next Ticket. Do not keep ordinary Tickets Open until the cumulative PR/MR.

The final Ticket becomes eligible only after every ordinary delivery Ticket is closed with a verifiable Integration Result. Missing Tickets, missing or conflicting Integration evidence, unattributed Commits, worktree changes, or behavior outside approved Scope return locatable Findings and prohibit a mergeable PR/MR.

## Immutable Audit Ranges

Keep three Git bindings distinct:

- `review_base / candidate_head`: normal immutable Verdict inputs for the final Ticket.
- `spec_delivery_base / delivery_head`: the complete Spec delivery range; freeze and persist `spec_delivery_base` from the target Commit when the Spec Integration Branch is first created, and bind `delivery_head` to its final audited Head.
- `target_before / target_after`: the final native Integration Result defined by the target-drift protocol.

The `spec_delivery_base / delivery_head` range is supplemental audit evidence, not Verdict inputs. Before initial PR/MR creation, require only the Spec Integration Branch Head to equal the reviewed `candidate_head` and bind that Commit as `delivery_head`. After create or reuse, verify that the native PR/MR Head equals `delivery_head`. Any later Head rewrite returns through Coder validation and dual Review, then rebinds the new reviewed `candidate_head` as `delivery_head` before refreshing the same PR/MR. For `NO_CHANGE_REQUIRED`, require `review_base == candidate_head == delivery_head`; Reviewers inspect the current tree, complete range, and existing evidence. When the final Ticket changes code, its Verdict Diff remains `review_base...candidate_head`, while the complete delivery range stays supplemental. This creates neither a second Reviewer type nor a second Verdict schema.

The final Coder and Reviewers verify that the range contains every approved Ticket and no unapproved or unattributed Commit, preserves each Ticket-to-Candidate-to-Integration mapping, satisfies Delivery Acceptance and final validation entries, and re-executes or verifies every existing owner-referenced Proof on `delivery_head`. The final Ticket gains no invariant ownership. A code repair touching an owner's Contract path must rerun that Proof on the new Head; changing a Contract, Proof mapping, Spec, ADR, Scope, product behavior, or approved writable Scope returns `CONTRACT_BLOCKER`.

Conflict resolution, candidate-caused Check repair, rebase, or any other Head change follows Repair Diagnosis, the final Ticket's Coder and both original Reviewers, and its shared three-round budget. Read-only target, mergeability, Check, or evidence refresh consumes no round. The Scheduler never edits code.

## Native Audit Projection

After the final Candidate receives dual `PASS`, create or reuse at most one valid native PR/MR identity for the exact Spec reference, revision, and target. Query native facts after an ambiguous create; reuse one unique match and stop on conflicting or multiple matches. Do not maintain a long-lived Draft PR/MR from the first Ticket.

Generate the body from Tracker and Git native facts. Include:

- Spec reference and revision;
- `spec_delivery_base...delivery_head` and the declared target plus current target Commit;
- every completed in-Scope Ticket;
- each Ticket's reviewed Candidate, Integration evidence, and both Verdict references, including the final Ticket;
- Cross-seam Invariants with their existing Proof entry points;
- Required Checks and final validation evidence;
- known limitations and any explicit Release Boundary.

The body is an audit projection, not a source of truth. Ticket state, checkpoints, Commits, native PR/MR and merge facts, and Final Acceptance retain ownership. A missing, stale, or conflicting projection blocks merge; regenerate it from native facts instead of using it to overwrite them.

Treat the generated body as dynamic untrusted literal data. Render it without shell interpretation and publish it through the runtime's file or stdin transport; never use an inline dynamic argument, shell concatenation, command substitution, or manual escaping. Read it back from the native PR/MR reference and require exact native read-back except the checkpoint contract's newline normalization. The projection is not a Durable Checkpoint and adds no Event, parser, or fact source.

## PR/MR Lifecycle

Use this order: dual Review `PASS` → create or reuse PR/MR → Required Checks → refresh projection → literal-safe write → exact read-back → merge. Checks that exist only after PR/MR creation are never required beforehand. Repair, completed Checks, or target refresh updates the same PR/MR identity and regenerates its projection from current native facts.

If Head changes, invalidate the old Verdicts and Checks through existing rules, then repeat Coder validation, dual Review, Checks, projection refresh, and read-back on the same PR/MR. Under `human-merge`, pause with `READY_FOR_HUMAN_MERGE` only after Checks and the latest projection read-back are ready, keeping the final Ticket and Spec Open. Under `auto-merge`, require the unchanged reviewed Head and revision, Required Checks, protection, permissions, current-target evidence, and confirmed projection.

The cumulative merge provides Git delivery eligibility only. Record the final `target_before / target_after`, close the final Ticket after integration, and run fresh Spec Acceptance on the actual target Commit. PR/MR readability, approval, or mergeability never substitutes for Acceptance.

## Scope Boundaries

One Spec has at most one cumulative PR/MR for its approved revision and target. A multi-Spec Initiative may have one per applicable member Spec but must not aggregate multiple Specs into one PR/MR or create an integration owner under the Initiative. The Local runtime has no cumulative PR/MR surface and must reject `CUMULATIVE_AUDIT`; its other approved shared-branch reasons remain unchanged.

Do not add Stacked PRs, a Draft PR phase, a Reviewer type, Event, terminal state, repair budget, Tracker Item type, or second fact source.
