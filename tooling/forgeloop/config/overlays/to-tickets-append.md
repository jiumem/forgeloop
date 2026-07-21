## Forgeloop Planning Contract Gap Handoff

When normal decomposition discovers that the approved parent contract must change, return `CONTRACT_BLOCKER` with the existing Spec reference, locatable evidence, affected contract sections, and the smallest proposed revision summary. Keep Tracker writes at zero and tell the user to invoke `$to-spec` explicitly for an in-place Planning Revision. `$to-tickets` must not edit the parent itself and must not create a replacement Spec. After the same existing Spec has a confirmed effective Revision, a later explicit `$to-tickets` invocation may restart decomposition from that Revision.

## Forgeloop Shared Delivery Declaration

Keep three approved facts independent:

- Branch topology: `INDEPENDENT | SHARED`.
- Shared-branch reason: `WIDE_REFACTOR | NON_GREEN_MIGRATION | ATOMIC_DELIVERY | CUMULATIVE_AUDIT`.
- Integration policy: `auto-merge | human-merge`.

Every `SHARED` Spec uses one Spec Root Final Integration Gate. The Gate coordinates final validation and native integration; it is not a Ticket, Reviewer, Acceptance level, Event, state, or fact source. `CUMULATIVE_AUDIT` only extends legal SHARED reasons; it grants no merge authority and changes no other reason. Offer it only for a Spec with a native PR/MR runtime and at least two implementation Tickets. A single-Ticket cumulative delivery remains `INDEPENDENT`. Local does not offer this reason, while its other legal SHARED reasons remain available.

For any proposed `SHARED` topology, show this declaration with the complete Ticket and dependency drafts:

```text
Branch topology: SHARED
Shared-branch reason: <WIDE_REFACTOR | NON_GREEN_MIGRATION | ATOMIC_DELIVERY | CUMULATIVE_AUDIT>
Integration branch: <derived Spec branch>
Target: <declared target>
Final integration gate owner: SPEC_ROOT
Final delivery surface: <configured target integration>
```

Resolve every angle-bracket field before approval. For `CUMULATIVE_AUDIT`, the delivery surface must resolve to one native PR/MR for the Spec revision and target. Require one user approval for the declaration, Ticket bodies, blocking edges, risk classifications, and invariant ownership. Rejection keeps `INDEPENDENT`; `$run-initiative` never switches at runtime.

Do not draft a ceremony Ticket that only re-runs parent Validation Entries, owner Proofs, CI, PR/MR creation, or integration. When the final stage has independent implementation work, use an ordinary vertical Ticket and classify its real risk. Final validation reuses the parent Delivery Acceptance, Validation Entries, and existing invariant Owner Proofs without gaining ownership.

Return `FAILED_PRECONDITION` with zero Tracker writes for a legacy `Final integration owner` field, a missing `Final integration gate owner: SPEC_ROOT`, or a ceremony-only final Ticket. Do not parse, alias, migrate, or fall back to the old declaration.

## Forgeloop Final Gate Repair Mode

Enter this mode only when the user explicitly invokes `$to-tickets` with a formal `RUN_PAUSED` from the Final Integration Gate containing `finding_id`, evidence references, owning Scope, and a stable `repair_key` for every Final Gate Finding. Read the owning Spec, applicable Initiative, `delivery_head`, existing Open Tickets, and every Ticket carrying any key.

- Keep the approved parent contract, completed Tickets, and their Checkpoints unchanged. Return `CONTRACT_BLOCKER` instead of drafting repair Tickets when a Finding requires changing the Spec, `Delivery Acceptance`, Cross-seam Invariant, Proof mapping, ADR, Scope, Ticket Acceptance criteria, confirmed Initiative membership, Branch Topology, or target.
- Use the affected Spec as `owning_spec_ref` for every Final Gate Finding. Never create a repair Ticket directly under an Initiative; return `CONTRACT_BLOCKER` when no member Spec can own the Finding.
- Query every key before drafting. Reuse the unique matching unfinished repair Ticket; stop on an ambiguous or conflicting key. Multiple keys may share a Ticket only when its body lists every key and the Findings form one atomic vertical slice.
- For unmatched keys, draft only the smallest vertical Tickets needed for the Findings; do not decompose the whole Spec again. When a Finding traces to a completed Ticket, record `source_ticket_ref` without reopening or modifying it.
- Record `owning_spec_ref`, applicable Initiative reference, source type, `repair_key`, `finding_id`, final Commit or `delivery_head`, observable repair checks, and genuine blockers in each repair Ticket. Keep it inside approved Scope.
- Preserve the normal user quiz and approval before idempotent publication. After an ambiguous write, query every `repair_key` and verify body and parent relation before retrying; never create a duplicate because the first response was uncertain.

This mode creates or reuses formal repair Tickets only after the user explicitly invokes `$to-tickets`. It does not resume `$run-initiative`; the user resumes the original Run separately after the Tracker work is valid.

## Forgeloop Spec Revision Reconciliation Mode

Enter this mode either when the user explicitly invokes `$to-tickets` for a formal Spec with a material new Revision and a paused Run, or when `$run-initiative` delegates an exactly read-back approval record and its complete reconciliation package. Read the previous and current Spec Revisions plus every existing child Ticket, including body, comments, status, parent, blockers, and existing Ticket Revision records.

- Preserve every Completed or Closed Ticket and its history unchanged.
- Compare the revised contract only with Open Tickets. Evaluate `retain`, `update`, `supersede`, and `create`, prefer `retain > update > supersede/create`, and form the smallest set of actions that reaches the approved target bodies and relationships.
- In explicit mode, present that set and obtain normal user approval before writing. In delegated mode, require every action and allowed equivalent outcome to be present in the approved package; do not quiz the user or request another approval.
- Reuse an Open Ticket when its delivery goal remains valid. Update only the approved contract fields and blockers. Create only missing vertical slices. Do not delete obsolete Open Tickets; mark them superseded and close them only when the current mode's approval explicitly includes that action.
- For an unfinished ceremony-only Ticket from the replaced shared-delivery protocol, mark it superseded, close it, and remove its native parent relation and blocking edges only after explicit user approval; in delegated mode, the bound package is that approval and must not be requested again. This is approved Tracker reconciliation, not runtime compatibility or automatic migration.
- Before every write, refresh the current Ticket and search for the approved target fact. Reuse a unique equivalent fact, perform the approved action only when its expected predecessor still holds, and stop when current facts exceed the approved equivalent boundary. If a write result is ambiguous, query and verify before retrying.
- Complete create and update actions, then all approved parent and blocking relationships, before reading back each affected Ticket's complete final facts. Only after that read-back render the complete Ticket Revision to a temporary file with a non-interpreting file-writing capability and append it through the configured file-backed Tracker operation; never place dynamic Revision text in an inline body/message argument, shell interpolation, or command substitution. Append or reuse one effective Ticket Revision binding the complete body, relationships, approval record, effective Spec/ADR Revisions, materiality judgment, and Repair Lineage. A missing prior Ticket Revision uses the approved pre-change facts as a baseline and does not reset repair budget.
- Query every successor of the same Ticket predecessor. Reuse equivalent successors and select the smallest immutable native Comment ID, Note ID, or Local append position as canonical; stop with `RECOVERY_CONFLICT` for different successors or missing, equal, or incomparable ordering. Intermediate Ticket states never become an effective Revision, enter the Frontier, reset budget, or certify a Candidate.
- Only a material Revision affecting this Ticket opens a new initial repair cycle; unrelated or non-material changes do not reset its budget, and a legitimately new Ticket preserves Repair Lineage so equivalent failed work cannot be hidden behind a new identity.
- Process obsolete Open Tickets only after every retained, updated, or created Ticket has its approved final facts and canonical effective Revision. Return a complete native read-back of the reconciled Ticket graph and Repair Lineage.
- Stop with `CONTRACT_BLOCKER` when reconciliation requires a different core Problem, Actor, delivery target, expanded Scope, Spec rewrite, ADR change, or Initiative membership change.

Do not modify the Spec, ADRs, parent Initiative, Completed Tickets, Run Claim, or Run checkpoints. This mode reconciles Tracker Tickets only; it does not resume `$run-initiative`. The Scheduler alone decides whether the fully reconciled Run remains paused or competes to resume.

## Forgeloop Formal Design Document Contract

In normal decomposition mode, read the parent Spec's referenced Formal Design Document when present and verify its current repository content before drafting. Treat the Spec and applicable ADRs as higher-level authority. The Formal Design Document refines their confirmed implementation design but cannot expand Scope, add product behavior, or strengthen delivery guarantees.

After code exploration and before drafting, semantically determine whether multiple modules, Tickets, implementation sessions, or Reviewers would otherwise have to repeat or independently invent the same interface, authority rule, data model, state transition, transaction, recovery, security, or compatibility decision. Do not require a Formal Design Document merely because the feature is large, important, or `HIGH_RISK`; do not use a score, keyword list, field-presence check, or fixed count.

If the shared decisions are unresolved, the necessary document is missing, or the document conflicts with the Spec or applicable ADRs, return `DESIGN_DOCUMENT_REQUIRED`, identify the exact shared decisions and locatable code or contract evidence, keep Tracker writes at zero, and recommend that the user explicitly invoke `$grill-with-docs` to create or revise the same document in place. Do not distribute the missing design across Ticket bodies, modify the Formal Design Document, edit the parent Spec, create a replacement Spec, or automatically invoke another Workflow. `DESIGN_DOCUMENT_REQUIRED` is an Agent-readable planning result, not Tracker state. Use the existing `CONTRACT_BLOCKER` path instead only when the product contract, Scope, acceptance, irreversible architecture decision, or approved public interface must change.

When the Formal Design Document is complete, add an optional `## Design Document` section to each affected Ticket containing only the stable document reference and relevant section references. Do not copy the shared design into Ticket bodies. Omit the section for unaffected Tickets and for Specs that need no separate document.

Bind every applicable Design Reviewer to the same confirmed document and relevant sections. An exact Design Document clause may support a concern, but it does not replace the required binding to an approved Delivery Acceptance, Cross-seam Invariant, applicable ADR, or approved failure behavior, and it cannot create a stronger acceptance standard. The Reviewer must not author or revise the document. A newly exposed shared implementation question returns `DESIGN_DOCUMENT_REQUIRED` to `$grill-with-docs`; a missing product or architecture decision follows the existing `CONTRACT_BLOCKER` path.
