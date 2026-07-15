# Final Integration Gate

Load this protocol before the root Claim for every declared `SHARED` topology. It is the sole final-delivery protocol for `WIDE_REFACTOR`, `NON_GREEN_MIGRATION`, `ATOMIC_DELIVERY`, and `CUMULATIVE_AUDIT`; no reason may maintain a parallel gate. Require `Final integration gate owner: SPEC_ROOT`, approved together with the Ticket bodies, blocking edges, risk classifications, and invariant ownership.

Return `FAILED_PRECONDITION` with zero Tracker writes for a legacy `Final integration owner` field, a missing SPEC_ROOT declaration, or a ceremony-only final Ticket. Do not add an alias, migration, compatibility branch, or fallback. If the final stage has independent implementation work, use an ordinary vertical Ticket. The Gate, Scheduler, and Spec Root never modify implementation code or resolve code conflicts.

## Root Binding and Ticket Delivery

Before publishing the competitive root Claim, refresh each SHARED Spec's declared target and freeze its Commit as `spec_delivery_base`. Render the complete `RUN_CLAIMED` Payload with that Spec's reference, revision, topology, reason, Integration Branch, and base. Only the winning Claim's exact native read-back authorizes creating each Integration Branch from its bound Commit. Recovery accepts the winning bindings and never reinterprets a later target Head as a delivery Base.

Run ordinary Tickets through the existing serial loop. Each Ticket keeps its own Coder, dual Reviewers, repair budget, and Ticket `INTEGRATION_RESULT`, then closes after its reviewed Candidate enters the Integration Branch. Enter the Gate only when every ordinary Ticket is Closed, every Ticket has a verifiable Ticket `INTEGRATION_RESULT`, and the Frontier contains no Open or Blocked Ticket, missing integration evidence, or fact conflict.

## Final Gate

The Scheduler follows this order:

1. Refresh the Spec, Revision, native Ticket set, dependencies, Ticket Integration Results, Integration Branch, target, Integration Policy, permissions, and worktree facts.
2. Map every approved Ticket through its Ticket Integration Result and `integration_method`, then freeze the Integration Branch Head as `delivery_head`. For `merge`, native evidence must bind the reviewed Candidate Head to `target_after`; attribute the reviewed Candidate range and any produced merge Commit. For `squash`, native evidence must bind the reviewed Candidate Head to the exact produced squash Commit; attribute that Commit without requiring Candidate reachability. For another configured native method, require its approved native provenance to bind the Candidate Head to the exact produced delivery Commit set; stop on a missing or ambiguous binding. Confirm every mapped Candidate Head has two bound `PASS` Verdicts. A `NO_CHANGE_REQUIRED` Ticket is complete only with result=`ALREADY_PRESENT`, `Base == Head`, `target_before == target_after`, and two bound `PASS` Verdicts, and contributes no Commit. Prove every Commit in `spec_delivery_base...delivery_head` belongs to exactly one Ticket, with no missing or duplicate delivery, out-of-Scope change, dirty worktree, or unexplained Head rewrite. Require evidence that `delivery_head` equals the latest Ticket Integration Result's `target_after`.
3. Create a fresh isolated, source-read-only Agent task on the fixed `delivery_head`. Run the parent Validation Entries and reverify each Cross-seam Invariant Proof declared by its unique Owning Ticket. Return evidence or Findings with stable `finding_id` values. The task gains no invariant ownership and adds no final Reviewer or Spec-level `REVIEW_RESULT`.
4. After range and behavior evidence pass, GitHub or GitLab creates or reuses the one valid native PR/MR identity and verifies that its native Head equals `delivery_head`. Local uses its configured Git integration for other legal SHARED reasons without inventing a PR/MR; Local still rejects `CUMULATIVE_AUDIT`.
5. From that delivery surface, read Required Checks, protection, permissions, current target, and mergeability. For GitHub or GitLab, generate the native body from current Tracker, Git, Gate, Check, and target facts. Treat the body as untrusted literal data: use file or stdin transport, never an inline dynamic argument, shell concatenation, command substitution, or manual escaping. Read it through the native PR/MR reference and require exact native read-back except checkpoint newline normalization. The projection is read-only audit output, never a fact source or Durable Checkpoint. `CUMULATIVE_AUDIT` also follows [cumulative-audit.md](cumulative-audit.md) for its additional fields and one-identity limit. A Head change invalidates Gate evidence, Checks, and projection; target drift invalidates Checks, projection, and integration eligibility only.
6. Only after every gate passes, integrate through the configured Integration Policy. `human-merge` uses the existing `RUN_PAUSED reason=READY_FOR_HUMAN_MERGE` and must keep the Spec Open with no current Ticket; `auto-merge` never bypasses Required Checks, protection, or permissions.
7. After merge or confirmed already-present delivery, publish the existing Spec-level `INTEGRATION_RESULT` with `subject_ref=<spec-ref>` and result, `spec_delivery_base`, `delivery_head`, `target_before`, `target_after`, integration method, native reference, and final evidence references.
8. Run fresh Spec Acceptance only on the actual `target_after` Commit. The Gate, PR/MR, Checks, and Spec Integration Result never replace `ACCEPTANCE_RESULT level=SPEC`.

## Finding and Repair Routing

For an implementation Finding, publish the existing `RUN_PAUSED` with `reason=FINAL_GATE_FINDING`, `finding_id`, evidence references, owning Scope, and `repair_key=final-gate:<spec-ref>:<spec-revision>:<finding_id>`. Derive the key from those fixed identities only; never include mutable prose or runtime order. Then require the user to invoke `$to-tickets` explicitly. The Gate and Scheduler never create, claim, or implement a repair Ticket.

The `$to-tickets` Repair Mode accepts a formal Acceptance Finding or Final Gate Finding. It reuses the unique matching unfinished repair Ticket by `repair_key`, otherwise creates the smallest vertical Ticket under the owning Spec. When a Finding traces to a completed Ticket, record only `source_ticket_ref`; keep the completed Ticket and its Checkpoints immutable. Route multi-Scope Findings separately instead of letting the Spec Root or one miscellaneous Ticket absorb cross-Scope code.

Return `CONTRACT_BLOCKER` when repair requires changing the Spec, Delivery Acceptance, Cross-seam Invariant, Proof mapping, ADR, Scope, Branch Topology, or target. Refreshing target drift, Checks, permissions, mergeability, projection, or native read-back stays read-only, creates no Ticket, and consumes no repair budget.

## Checkpoints and Recovery

Keep the Checkpoint Set unchanged: `RUN_CLAIMED`, `CODER_RESULT`, `REVIEW_RESULT`, `INTEGRATION_RESULT`, `ACCEPTANCE_RESULT`, `RUN_PAUSED`, `RUN_CANCELLED`, `RUN_RESUMED`, and `EVENT_SUPERSEDED`. Ticket Integration Results prove entry into the Integration Branch; a Spec Integration Result proves delivery of the fixed `delivery_head` to the target. `REVIEW_RESULT` remains Ticket-only, and `ACCEPTANCE_RESULT` remains `SPEC | INITIATIVE`.

Recover the Gate from the root Claim, Ticket Checkpoints, Integration Branch, PR/MR, Checks, and target-branch native facts, never from old child threads or conversation memory. This protocol adds no Event, state, Reviewer type, Acceptance level, parser, or fact source.
