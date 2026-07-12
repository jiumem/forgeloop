---
name: grill-with-docs
description: Load when the user explicitly wants sustained design clarification that also preserves confirmed domain terms and decisions.
---

Run a `/grilling` session, using the `/domain-modeling` skill.

## Forgeloop Boundaries

Ask only one high-impact question at a time and provide a recommended answer. Maintain the single source of truth through `$domain-modeling` only when domain information actually changes:

- Write settled domain terminology only to `CONTEXT.md`, with no implementation details;
- Write a long-term decision to an ADR only after it satisfies all three ADR thresholds and the user confirms it;
- Do not write the same fact to both `CONTEXT.md` and an ADR.

Do not create a Spec, Ticket, or implementation code. If the user cancels or stops, preserve confirmed domain-documentation updates, list resolved questions, unresolved questions, and files actually written, and state clearly that the design is incomplete. Report the design phase as complete only after the user confirms that shared understanding has been reached; at that point, summarize resolved questions, unresolved questions, and files actually written. Do not automatically start `$to-spec`, `$to-tickets`, or `$run-initiative`.
