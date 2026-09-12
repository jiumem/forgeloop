## Forgeloop Completion Boundary

After publication, return the parent Spec and Ticket references and tell the user they may explicitly invoke `$run-initiative` for the complete Spec. Do not start that Workflow automatically. The published Tickets become implementation Slices on the Spec's single delivery branch; they do not each receive a separate branch, Review, Gate, PR, or repair loop.

If the user instead selects one Ticket directly, recommend `$run-initiative` only when that Ticket is clearly large enough to need several coherent Slices. A small direct Ticket should use ordinary implementation. Do not recommend one `$run-initiative` invocation for multiple Initiatives.

## Forgeloop Planning Contract Gap Handoff

When normal decomposition discovers that the approved parent contract must change, return `CONTRACT_BLOCKER` with the existing Spec reference, locatable evidence, affected contract sections, and the smallest proposed revision summary. Keep Tracker writes at zero and tell the user to invoke `$to-spec` explicitly for an in-place Planning Revision. `$to-tickets` must not edit the parent itself and must not create a replacement Spec. After the same existing Spec has a confirmed effective Revision, a later explicit `$to-tickets` invocation may restart decomposition from that Revision.

## Forgeloop Delivery Shape

Do not create a ceremony Ticket for final validation, audit, Review, PR/MR creation, or integration. When the final stage has independent implementation work, express its real observable result as an ordinary vertical Ticket. The parent Spec remains the delivery contract, and `$run-initiative` performs one final Gate and one PR for the complete Spec.

## Forgeloop Formal Design Document Contract

In normal decomposition mode, read the parent Spec's referenced Formal Design Document when present and verify its current repository content before drafting. Treat the Spec and applicable ADRs as higher-level authority. The Formal Design Document refines their confirmed implementation design but cannot expand Scope, add product behavior, or strengthen delivery guarantees.

After code exploration and before drafting, semantically determine whether multiple modules, Tickets, implementation sessions, or Reviewers would otherwise have to repeat or independently invent the same interface, authority rule, data model, state transition, transaction, recovery, security, or compatibility decision. Do not require a Formal Design Document merely because the feature is large, important, or `HIGH_RISK`; do not use a score, keyword list, field-presence check, or fixed count.

If the shared decisions are unresolved, the necessary document is missing, or the document conflicts with the Spec or applicable ADRs, return `DESIGN_DOCUMENT_REQUIRED`, identify the exact shared decisions and locatable code or contract evidence, keep Tracker writes at zero, and recommend that the user explicitly invoke `$grill-with-docs` to create or revise the same document in place. Do not distribute the missing design across Ticket bodies, modify the Formal Design Document, edit the parent Spec, create a replacement Spec, or automatically invoke another Workflow. `DESIGN_DOCUMENT_REQUIRED` is an Agent-readable planning result, not Tracker state. Use the existing `CONTRACT_BLOCKER` path instead only when the product contract, Scope, acceptance, irreversible architecture decision, or approved public interface must change.

When the Formal Design Document is complete, add an optional `## Design Document` section to each affected Ticket containing only the stable document reference and relevant section references. Do not copy the shared design into Ticket bodies. Omit the section for unaffected Tickets and for Specs that need no separate document.

Bind every applicable Design Reviewer to the same confirmed document and relevant sections. An exact Design Document clause may support a concern, but it does not replace the required binding to an approved Delivery Acceptance, Cross-seam Invariant, applicable ADR, or approved failure behavior, and it cannot create a stronger acceptance standard. The Reviewer must not author or revise the document. A newly exposed shared implementation question returns `DESIGN_DOCUMENT_REQUIRED` to `$grill-with-docs`; a missing product or architecture decision follows the existing `CONTRACT_BLOCKER` path.
