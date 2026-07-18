## Integration Policy

`Integration policy: <auto-merge|human-merge>`. Automatic integration is prohibited when it is missing. Local still represents candidate implementations through Git Branches/Commits; do not treat Markdown state as proof that code has been integrated.

## Tracker Runtime Operations

- **Frontier**: Scan the authorized Spec's Open Ticket files, excluding unresolved blockers and existing Claims; rescan after every advancement and select deterministically by number.
- **Claim**: Compete for the Initiative Scheduler in the Tracker directory by atomically creating `scheduler.lock`, then atomically create `<ticket>.claim` for the Ticket; the lock records `run_id` and does not use a short TTL. Losers must not create a Coder.
- **Checkpoints**: Append minimal records with Run ID and an event-specific idempotency key under the configured Agent Run section. Collect both Ticket Verdicts independently and write one combined `REVIEW_RESULT`. Do not add a parser, sequence chain, or duplicate idempotency key; append `EVENT_SUPERSEDED` to correct an error.
- **Candidate implementation**: Associate the Ticket Branch and Commit; do not use `claimed` or Reviewer PASS to misrepresent integration as complete.
- **Integration**: Integrate with `auto-merge` only when both Verdicts are PASS and Base/Head are unchanged; for `human-merge`, record `READY_FOR_HUMAN_MERGE`, wait for user action, and then refresh Git facts.
- **Closure**: After verifying that the Commit entered the declared branch, record `INTEGRATION_RESULT`, mark the Ticket `resolved`, then atomically remove only its owned Ticket lock. In a multi-Spec Run, keep member Specs Open through Initiative Acceptance; on Initiative PASS, resolve member Specs first and the parent last, then atomically remove only the owned `scheduler.lock`. A stored Run ID mismatch, dirty worktree, lock conflict, or inconsistent Git state must leave the Item Open and provide recovery steps.
