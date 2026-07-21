## Forgeloop Planning Revision Mode

Enter this mode only when the user explicitly invokes `$to-spec` with one approved existing Spec and a planning-stage `CONTRACT_BLOCKER` from `$to-tickets` that is bound to the current Revision, and no child Ticket has been published. The earlier new-Spec-only publication restriction does not apply in this mode. Treat the referenced Tracker item as the same existing Spec throughout the revision. Validate the complete proposed body against the ordinary publication gates and obtain approval for the exact revised body before writing.

Immediately before the first write, refresh and verify the current Spec body, state, and Revision, the `CONTRACT_BLOCKER` binding, and that no child Ticket has been published. Return `FAILED_PRECONDITION` when required input is missing or unreadable. Return `RECOVERY_CONFLICT` when the Revision, blocker, or child-Ticket facts drift. Every failed precondition leaves Tracker writes at zero and must not fall through to normal new-Spec publication or create a replacement Spec.

Publish one successor of the current predecessor Revision on the same existing Spec:

- render the complete new body, predecessor Revision reference, and approval reference to a temporary file with a non-interpreting file-writing capability, then append one native Revision record through the configured file-backed Tracker operation; never place dynamic content in an inline argument, shell interpolation, command substitution, or heredoc;
- query every successor of the same predecessor before publication and after an ambiguous result; reuse one unique equivalent successor and return `RECOVERY_CONFLICT` for different successors or missing, equal, or incomparable native ordering;
- update only the current Spec body to the approved canonical projection, then require exact read-back of both the Revision record and complete body; after an ambiguous result, query first and retry only after proving that no equivalent write exists.

This mode must not create a replacement Spec. Require a new Spec only when the core Problem, primary Actor, or observable product goal is replaced rather than clarified. It does not publish Tickets or modify any existing child Ticket.

## Forgeloop Approved Revision Mode

Enter this mode only when `$run-initiative` supplies one exactly read-back native approval record and its complete reconciliation package for an existing paused Run. The package must bind the predecessor Spec Revision, complete target Spec body, approved ADR and Open Ticket effects, Candidate disposition, recovery choice, and stable `package_id`. Treat those fields as Agent-readable contract evidence; use the exact identities only for authorization, idempotency, and conflict detection.

Do not interview the user, ask for test-Seam approval again, or reinterpret the approved change. Verify that the approval, package, predecessor Revision, current Spec body, and current Run still agree before writing. If the core Problem, primary Actor, or observable delivery outcome changes, write nothing and return that the old Run must be cancelled and a new Spec created.

Publish the approved Revision on the existing Spec:

- render the complete new Spec, predecessor reference, approval reference, and `package_id` to a temporary file with a non-interpreting file-writing capability, then append it through the configured file-backed Tracker operation as one native Revision record; never place dynamic Revision text in an inline body/message argument, shell interpolation, or command substitution;
- query every successor of the same predecessor before publication and after ambiguous results;
- reuse one unique equivalent successor; when several equivalent successors exist, choose the one with the smallest immutable native Comment ID, Note ID, or Local append position;
- stop with `RECOVERY_CONFLICT` for different successors or missing, equal, or incomparable native ordering;
- update the current Spec body only to the exact canonical Revision projection, then read back both the Revision record and complete body before returning success.

This mode owns only Spec Revision publication. It does not revise ADRs, reconcile Tickets, resume the Run, or turn Revision fields into a parser-driven workflow.

## Forgeloop Formal Design Document Contract

Apply this contract when publishing a new Spec or an in-place planning Revision. Semantically determine whether the resolved solution depends on shared implementation decisions that later modules, Tickets, implementers, or Reviewers would otherwise have to repeat or independently invent. Relevant decisions may include module interfaces, authoritative data ownership or schemas, permission enforcement, state transitions and transactions, concurrency and ordering, failure and recovery behavior, or compatibility rules.

Do not require a Formal Design Document merely because the feature is large, important, or technically sophisticated. Do not use a score, keyword list, field-presence check, or fixed module or Ticket count. A separate document is necessary only when the shared implementation design cannot remain local to ordinary Spec decisions and individual Tickets without creating parallel sources of truth.

When a confirmed Formal Design Document exists, read it with the applicable ADRs, verify that it does not contradict the complete candidate Spec, and add one optional `## Design Document` section immediately before `## Further Notes` containing its stable repository reference. Do not copy its detailed design into the Spec. In `Implementation Decisions`, retain only what is necessary to understand product Scope, public behavior, acceptance, and irreversible constraints; reference the Formal Design Document for detailed module, state, schema, transaction, security, and recovery design.

When a Formal Design Document is necessary but missing, unresolved, or contradictory, return `CONTEXT_INSUFFICIENT`, identify the exact shared decisions or conflict, keep Tracker writes at zero, and recommend that the user explicitly invoke `$grill-with-docs`. Do not create or revise the document inside `$to-spec`, and do not automatically invoke another Workflow. A simple feature whose design can remain local proceeds without the optional section.
