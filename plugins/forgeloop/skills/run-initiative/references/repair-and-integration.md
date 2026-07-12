# Repair, Branch, and Integration Protocol

## Repair Loop

When either axis returns `REPAIR_REQUIRED`, wait for the other axis, then continue the original Coder with both complete Finding sets. Do not merge, reorder, or reinterpret Findings. Continue each original Reviewer with the new fixed Head and only that Reviewer's own axis history.

Allow at most two ordinary repair rounds per Ticket. Count every post-review return to the Coder for candidate code changes against the same budget, whether caused by Reviewer Findings, a candidate-caused Required Check failure, or merge-conflict resolution. If any Blocking Finding or candidate-caused failure remains after the second repair round, persist `RUN_PAUSED` with reason=`REPAIR_BUDGET`. A contract conflict, insufficient Scope, incompatible axes, required Spec/ADR change, or external infrastructure failure does not consume an ordinary repair round. Never rewrite `REPAIR_REQUIRED` as `PASS`.

Any code change, rebase, Base update, or conflict resolution invalidates both prior Verdicts. Require the Coder to validate the new Head and both Reviewers to issue fresh Verdicts for the complete cumulative Diff.

## Branch Ownership

Use one independent Branch per Ticket by default. Use a shared Spec Integration Branch only when `$to-tickets` already declared a Wide Refactor, an independently non-green migration, or required atomic delivery, together with a final `integrate-and-verify` Ticket. Neither the Scheduler nor Coder may switch modes ad hoc.

The Scheduler prepares the Branch and Base. The Coder edits, validates, and commits only Ticket Scope. Reviewers inspect fixed Commit objects. The Scheduler owns push, PR/MR creation or reuse, Required Checks, merge, and closure. Let the configured Tracker Runtime decide when remote publication occurs; do not impose an extra Draft-PR phase.

## Integration Policy

- `auto-merge`: integrate only after both Verdicts have `PASS`, Base/Head and revision remain unchanged, and existing Required Checks, protection rules, and permissions pass.
- `human-merge`: persist `RUN_PAUSED` with reason=`READY_FOR_HUMAN_MERGE`, preserve the Branch and PR/MR, keep the Ticket Open, and refresh native facts after user action.
- Missing policy prohibits automatic merge. A one-run override requires explicit user confirmation recorded in the Tracker.
- Automatic integration does not authorize deployment, release, data migration execution, or any other irreversible external action.
- A closed but unmerged PR/MR is not integrated.

When a Required Check fails, inspect its existing evidence before acting. If the failure is caused by the candidate and remains inside Ticket Scope, continue the original Coder with the check evidence, consume one ordinary repair round, invalidate both Verdicts after any code change, and repeat Coder validation and dual review. If the failure is caused by permissions, infrastructure, an unrelated target-branch failure, or evidence that cannot be attributed safely, persist `RUN_PAUSED` with reason=`CHECKS_BLOCKED`. Do not trigger an extra full CI run merely to classify the failure.

For `NO_CHANGE_REQUIRED`, verify `Base == Head` and both Reviewer Verdicts, then record `INTEGRATION_RESULT` with result=`ALREADY_PRESENT`; do not create an empty Commit or meaningless PR/MR.

In shared-branch mode, a Ticket completes after its Commit enters the declared Integration Branch. The final `integrate-and-verify` Ticket owns delivery to the target branch.

## Merge Conflicts

Return merge-conflict work to the current Coder and instruct it to invoke `$resolving-merge-conflicts` within Ticket Scope. Pause for incompatible product, Schema, or architecture intent. Do not let the Scheduler choose a side or perform destructive reset, discard, or abort operations. After a resolved conflict changes code or Base, return through Coder validation and both Reviewer gates.
