# Durable Checkpoints and Recovery

## Checkpoint Set

Use only `RUN_CLAIMED`, `CODER_RESULT`, `REVIEW_RESULT`, `INTEGRATION_RESULT`, `ACCEPTANCE_RESULT`, `RUN_PAUSED`, `RUN_CANCELLED`, `RUN_RESUMED`, and `EVENT_SUPERSEDED`.

`RUN_CLAIMED` belongs on the Spec or Initiative root. Do not emit a `TICKET_CLAIMED` Event: native assignment or the configured Local Ticket Claim already owns that fact. `REVIEW_RESULT` contains both independently collected Ticket Verdicts. `ACCEPTANCE_RESULT` carries `level=SPEC|INITIATIVE`.

## Minimal Durable Record

Every checkpoint needs only:

```yaml
run_id: <stable-id>
event: <type>
idempotency_key: <stable-event-specific-key>
subject_ref: <root|spec|ticket-ref>
timestamp: <tracker-observed-time>
```

Use the Tracker server timestamp for GitHub or GitLab and the append-write time for Local Markdown. Do not use the timestamp as the Claim winner or idempotency identity when a stronger native ordering fact exists.

Add only facts needed by that event:

- Claim: root revision and multi-Spec confirmation reference when applicable.
- Coder: result, Base/Head, Spec Revision, repair round, Commit and evidence references.
- Review: Base/Head, Spec Revision, repair round, and both complete axis Verdicts.
- Integration: result, target, Commit, PR/MR and native merge or already-present evidence.
- Acceptance: level, parent revision, final target Commit, Verdict, Findings, and repair key when needed.
- Pause, resume, or cancel: reason, current Ticket if any, and recovery evidence.

Build an idempotency key from the stable identity of the write. Include Base/Head, revision, axis or acceptance level, and repair round whenever they can distinguish two valid checkpoints. Before writing, search for the same key and reuse the existing checkpoint. Do not add a sequence chain, parser, serializer, or second state engine.

Never edit a published checkpoint. Correct an error with `EVENT_SUPERSEDED` that identifies the original record and replacement evidence.

## Claim and Cancellation

Retain the root Claim and current Ticket Claim while paused. On cancellation, first publish `RUN_CANCELLED`, stop dispatching and best-effort interrupt active children, preserve Branches, Commits, Findings, and evidence, then release only Claims owned by this `run_id`. A completed Run ignores a later cancellation request and reports that it is already complete.

On successful Ticket completion, close the Ticket and then release only its native Claim owned by this `run_id`; for Local, atomically remove the current Ticket lock as its owner. On successful Run completion, publish final Acceptance, close the root Item, and then release the root Scheduler Claim; for Local, atomically remove `scheduler.lock` as its owner. On GitHub or GitLab, the closed native Item plus its final Integration or Acceptance checkpoint makes the historical Claim inactive; do not delete the Claim Comment or Note.

Do not use a short TTL to infer that a long-running task is dead. GitHub and GitLab use the deterministic earliest valid root Claim. Local allows only the owning Run ID to remove its atomic locks.

## Recovery

1. Read native Tracker state, valid checkpoints, Branch, Commit, PR/MR, checks, and merge facts.
2. Reconstruct only the last checkpoint whose native references still agree. Do not rely on child thread existence or conversation memory.
3. Verify the root Claim owner, current Ticket Claim, Base/Head, Spec Revision, target, multi-Spec revision, confirmation reference, and any existing Verdicts. Treat a closed Ticket with valid Integration or a closed root with final Acceptance as a completed inactive Claim, not a resumable owner.
4. Publish `RUN_RESUMED` under the original `run_id` and continue after the last verified durable checkpoint. Do not replay a confirmed write.
5. Create fresh isolated children for the next required role and give each a self-contained Role Task Pack containing only durable role-relevant history.

Stop with `RECOVERY_CONFLICT` when native facts disagree with checkpoints, duplicate valid root Claims exist, Base/Head or material revision drifted, a retained dirty change cannot be attributed to the current Ticket, or multi-Spec membership changed without confirmation. Require the original Run or explicit user adjudication for takeover.
