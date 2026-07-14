# Durable Checkpoints and Recovery

## Checkpoint Set

Use only `RUN_CLAIMED`, `CODER_RESULT`, `REVIEW_RESULT`, `INTEGRATION_RESULT`, `ACCEPTANCE_RESULT`, `RUN_PAUSED`, `RUN_CANCELLED`, `RUN_RESUMED`, and `EVENT_SUPERSEDED`.

`RUN_CLAIMED` belongs on the Spec or Initiative root. Do not emit a `TICKET_CLAIMED` Event: native assignment or the configured Local Ticket Claim already owns that fact. `REVIEW_RESULT` contains both independently collected Ticket Verdicts. `ACCEPTANCE_RESULT` carries `level=SPEC|INITIATIVE`.

## Minimal Durable Record

Treat every Durable Checkpoint as two views of one existing record, not as new state:

- The **Native envelope** contains the GitHub or GitLab native reference and server timestamp, or the Local record position and append timestamp. Read these facts only from the write result and native read-back.
- The **Prepared Literal Payload** contains the Agent-declared event facts and every dynamic value as literal data. It must not contain a native timestamp or reference that cannot exist before publication.

The Prepared Literal Payload needs only:

```yaml
run_id: <stable-id>
event: <type>
idempotency_key: <stable-event-specific-key>
subject_ref: <root|spec|ticket-ref>
```

Never use a Native envelope timestamp to decide a Claim winner, derive idempotency identity, or compare Payloads.

Before any Tracker write, render the complete Prepared Literal Payload with a file-writing capability that does not interpret shell syntax. Treat Findings, evidence, identifiers, Tracker and Git references, Markdown fences, quotes, backslashes, Unicode, and multiline text as opaque literal data. For remote runtimes, place the temporary Payload outside the repository worktree and clean it up after confirmed read-back or explicit failure.

Never construct or transmit dynamic Payload text through inline `--body` or `--message`, `echo` or `printf`, an unquoted heredoc, `eval`, command substitution, or a manual shell escaping template. Supplying `--body-file` does not make a file safe if an interpreting shell command generated it.

Add only facts needed by that event:

- Claim: root revision and multi-Spec confirmation reference when applicable.
- Coder: result, Base/Head, Spec Revision, repair round, diagnosis summary and finding dispositions when repairing, Commit and evidence references.
- Review: Base/Head, Spec Revision, repair round, and both complete axis Verdicts.
- Integration: result, candidate_head, target_before, target_after, integration_method, and native_ref for merge or already-present evidence.
- Acceptance: level, parent revision, applicable confirmed membership, final target Commit, Verdict, Findings, and repair key when needed.
- Pause, resume, or cancel: reason, current Ticket if any, and recovery evidence.

Build an idempotency key from the stable identity of the write. Include Base/Head, revision, axis or acceptance level, and repair round whenever they can distinguish two valid checkpoints. Do not add a sequence chain, parser, serializer, or second state engine.

## Publish and Confirm

Before publication, query by the existing idempotency key. If there is one record with an identical Payload, reuse it without another write. If there is one different record, or more than one record whether their Payload bodies are identical or different, stop with `RECOVERY_CONFLICT`; never overwrite or choose one.

After publication, use the returned native reference to read back the record. For comparison, normalize CRLF to LF and reduce terminal line breaks to at most one trailing LF; every other byte of text must match the complete Prepared Literal Payload. A matching `run_id`, Event, or idempotency key alone is insufficient. Validate that the Native envelope is unique, but do not mix its reference or timestamp into Payload comparison.

For an ambiguous write result, query before retrying. A unique identical record confirms the write; no record permits a retry; a conflicting or non-unique result stops with `RECOVERY_CONFLICT`. If a reported-success write reads back as missing, truncated, or different, the checkpoint is unconfirmed: keep the Item Open and its Claims recoverable, report the native reference and the body difference, and publish no dependent checkpoint.

Never edit a published checkpoint. Use `EVENT_SUPERSEDED` only to correct a confirmed historical error with replacement evidence. An uncertain transport, failed read-back, or idempotency conflict must not use `EVENT_SUPERSEDED`.

## Claim and Cancellation

Retain the root Claim and current Ticket Claim while paused. On cancellation, first publish `RUN_CANCELLED`, stop dispatching and best-effort interrupt active children, preserve Branches, Commits, Findings, and evidence, then release only Claims owned by this `run_id`. A completed Run ignores a later cancellation request and reports that it is already complete.

On successful Ticket completion, close the Ticket and then release only its native Claim owned by this `run_id`; for Local, atomically remove the current Ticket lock as its owner. On successful Run completion, publish final Acceptance, close the root Item, and then release the root Scheduler Claim; for Local, atomically remove `scheduler.lock` as its owner. On GitHub or GitLab, the closed native Item plus its final Integration or Acceptance checkpoint makes the historical Claim inactive; do not delete the Claim Comment or Note.

Do not use a short TTL to infer that a long-running task is dead. GitHub and GitLab use the deterministic earliest valid root Claim. Local allows only the owning Run ID to remove its atomic locks.

## Recovery

1. Read native Tracker state, valid checkpoints, Branch, Commit, PR/MR, checks, and merge facts.
2. Reconstruct only the last checkpoint whose native references still agree. Do not rely on child thread existence or conversation memory.
3. Verify the root Claim owner, current Ticket Claim, Base/Head, Spec Revision, multi-Spec revision, confirmation reference, and any existing Verdicts. Before an Acceptance Seal, also verify the current target. After a Seal, verify its immutable binding and native read-back instead; later target movement does not conflict with it. Treat a closed Ticket with valid Integration or a closed root with final Acceptance as a completed inactive Claim, not a resumable owner.
4. Publish `RUN_RESUMED` under the original `run_id` and continue after the last verified durable checkpoint. Do not replay a confirmed write.
5. Create fresh isolated children for the next required role and give each a self-contained Role Task Pack containing only durable role-relevant history.

When a confirmed root Acceptance `PASS` is an Acceptance Seal, resume unfinished closure and Claim release from that Seal. Target movement after the Seal does not invalidate it or require another Reviewer.

Repair Diagnosis is a temporary preflight, not a new checkpoint. When recovery finds it was interrupted before the repair result, rerun the diagnosis from current trigger evidence, cumulative Diff, and durable repair history before authorizing further code changes.

Stop with `RECOVERY_CONFLICT` when native facts disagree with checkpoints, duplicate valid root Claims exist, Base/Head or material revision drifted, a retained dirty change cannot be attributed to the current Ticket, or multi-Spec membership changed without confirmation. Require the original Run or explicit user adjudication for takeover.
