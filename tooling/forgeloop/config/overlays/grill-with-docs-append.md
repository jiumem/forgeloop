## Forgeloop Boundaries

Ask only one high-impact question at a time and provide a recommended answer. Maintain the single source of truth through `$domain-modeling` only when domain information actually changes:

- Write settled domain terminology only to `CONTEXT.md`, with no implementation details;
- Write a long-term decision to an ADR only after it satisfies all three ADR thresholds and the user confirms it;
- Do not write the same fact to both `CONTEXT.md` and an ADR.

## Formal Design Document

Before declaring the design phase complete, semantically decide whether the confirmed design needs one durable Formal Design Document. It is necessary only when omitting it would force later Tickets, implementers, or Reviewers to repeat or independently invent shared engineering decisions across modules, Tickets, or sessions. Relevant decisions may include module responsibilities and interfaces, authoritative data ownership or schemas, permission and trust enforcement, state transitions and transactions, concurrency and ordering, failure and recovery behavior, or compatibility and migration rules.

Do not require a Formal Design Document merely because the feature is large, important, or technically sophisticated. Apply judgment to the complete design; do not use a score, keyword list, field-presence check, or fixed module or Ticket count. When the design can remain local to the Spec and Tickets, state that no separate Formal Design Document is necessary.

When one is necessary:

1. Explain which shared engineering decisions require a durable source of truth and why the Spec plus applicable ADRs cannot carry the detail cleanly.
2. Recommend one repository-native path, preferring an existing project convention instead of introducing a new documentation layout.
3. Ask the user whether to materialize the confirmed design there.
4. After confirmation, create or update that same document in place. Do not abandon it and create a replacement merely because the design changes.

The Formal Design Document records only confirmed current-scope implementation design. It may contain module seams, data and state models, key flows, failure behavior, security constraints, recovery rules, and validation strategy. It must not duplicate the complete Spec, replace an ADR, invent unresolved product behavior, or add speculative infrastructure. It refines the Spec and applicable ADRs and cannot override them. If no Spec exists yet, record the confirmed design context without inventing a future Spec identity; `$to-spec` may later reference the document.

`$domain-modeling` remains the sole owner of `CONTEXT.md` and ADR updates. `$grill-with-docs` directly owns creation and in-place revision of the Formal Design Document.

Do not create a Spec, Ticket, or implementation code. If the user cancels or stops, preserve confirmed domain-documentation updates and any confirmed Formal Design Document revision, list resolved questions, unresolved questions, and files actually written, and state clearly that the design is incomplete. Report the design phase as complete only after the user confirms that shared understanding has been reached; at that point, summarize resolved questions, unresolved questions, and files actually written. Do not automatically start `$to-spec`, `$to-tickets`, or `$run-initiative`.
