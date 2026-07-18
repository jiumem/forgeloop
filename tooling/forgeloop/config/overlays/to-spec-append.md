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
