## Integration Policy

`Integration policy: <auto-merge|human-merge>`. Automatic integration is prohibited when it is missing. Branch protection, Required Checks, and permissions take precedence; do not fall back to Local when authentication or permission checks fail.

## Tracker Runtime Operations

- **Frontier**: Query the Spec's Open child Issues, excluding items that still have an Open blocker, already have a valid Claim, or fall outside the authorized Scope; query again after every advancement.
- **Claim**: Publish `RUN_CLAIMED` on the Spec or Initiative root; the earliest valid server-side root Claim wins. Only the winner may claim one current Ticket through its native assignee state. Do not duplicate the Ticket Claim as an Event.
- **Checkpoints**: Append minimal idempotent checkpoints through Issue Comments. Collect both Ticket Verdicts independently and write one combined `REVIEW_RESULT`; do not modify published records, and append `EVENT_SUPERSEDED` to correct an error.
- **Candidate implementation**: Associate the Ticket Branch, Commit, and PR; a closed but unmerged PR is not complete.
- **Integration**: Let the Scheduler own push, PR handling, checks, and merge. Execute `auto-merge` only when both Verdicts are PASS, Head is unchanged, and Required Checks and permissions are satisfied. Return a candidate-caused Check failure to the original Coder under the shared repair budget; pause on permissions, infrastructure, or unrelated failures. For `human-merge`, write `READY_FOR_HUMAN_MERGE` and wait for a refresh.
- **Closure**: After verifying native merge facts, record `INTEGRATION_RESULT`, close the Ticket, and treat its assignee Claim as inactive. In a multi-Spec Run, keep member Specs Open through Initiative Acceptance; on Initiative PASS, close member Specs first and the parent last. Treat the closed root's historical Claim as inactive and do not delete Claim Comments. Authentication, permission, Branch Protection, or externally blocked Checks must leave Items Open and provide a recoverable diagnostic.
