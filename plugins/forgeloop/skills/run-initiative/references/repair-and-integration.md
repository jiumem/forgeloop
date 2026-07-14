# Repair, Branch, and Integration Protocol

## Repair Loop

For Reviewer Findings, a candidate-caused Required Check failure, or compatibility or merge-conflict resolution, continue the original Coder for a separate read-only Coder turn that follows the Repair Diagnosis protocol. Complete it before authorizing any candidate code change; the Scheduler then validates its structure and routes the declared classification.

Diagnosis is a zero-write, zero-budget preflight and does not create durable Tracker state. If it is interrupted before the repair result, rerun the diagnosis from current durable evidence before any further code change.

Route the complete diagnosis as follows:

- `LOCAL_REPAIR`: the existing interface can honestly express the correct behavior, there is one authoritative fact source, and no shared Seam or parallel path needs convergence. Continue the original Coder inside Ticket Scope.
- `STRUCTURAL_REPAIR`: a correct in-Scope repair must converge a fact source, interface, shared Seam, or parallel implementation. Continue the original Coder, require it to invoke `$codebase-design` before modifying code, then implement the declared convergence and prove it through the public Seam.
- `CONTRACT_BLOCKER`: a correct repair must expand Ticket Scope or change the Spec, Ticket Acceptance criteria, product behavior, an ADR, or an approved public interface. Persist the existing contract-blocker pause; do not authorize code changes or consume a repair round.

When either axis returns `REPAIR_REQUIRED`, wait for the other axis, then continue the original Coder with both complete Finding sets. Do not merge, reorder, or reinterpret Findings. Continue each original Reviewer with the new fixed Head and only that Reviewer's own axis history.

Allow at most three ordinary repair rounds per Ticket. Count every authorized Candidate code change or Head rewrite against this one budget, whether triggered by Reviewer Findings, a candidate-caused Required Check failure, rebase, or compatibility or merge-conflict resolution. Diagnosis turns do not consume this budget. A contract blocker or external infrastructure failure also consumes no round.

The second and third diagnoses must compare current evidence with prior diagnosis and repair history, state whether the prior mechanism hypothesis was falsified, and identify whether different `finding_id` values share one mechanism. New evidence may escalate `LOCAL_REPAIR` to `STRUCTURAL_REPAIR` or `STRUCTURAL_REPAIR` to `CONTRACT_BLOCKER`; it must not downgrade `STRUCTURAL_REPAIR` to `LOCAL_REPAIR` without new evidence.

After the third repair, a fixed Head with two fresh `PASS` Verdicts may integrate normally. If any Blocking Finding, candidate-caused failure, or unresolved compatibility or merge conflict remains, persist `RUN_PAUSED` with reason=`REPAIR_BUDGET`; do not start a fourth repair. Record the three diagnosis classifications, falsified hypotheses, unresolved Findings, current shared mechanism, and next legal action. Never rewrite `REPAIR_REQUIRED` as `PASS`.

Any code change, rebase, replacement of the frozen review Base, or conflict resolution invalidates both prior Verdicts. Target movement alone does not. Require the Coder to validate the new Head and both Reviewers to issue fresh Verdicts for the complete cumulative Diff.

## Branch Ownership

Use one independent Branch per Ticket by default. Use a shared Spec Integration Branch only when `$to-tickets` already declared a Wide Refactor, an independently non-green migration, or required atomic delivery, together with a final `integrate-and-verify` Ticket. Neither the Scheduler nor Coder may switch modes ad hoc.

The Scheduler prepares the Branch and Base. The Coder edits, validates, and commits only Ticket Scope. Reviewers inspect fixed Commit objects. The Scheduler owns push, PR/MR creation or reuse, Required Checks, merge, and closure. Let the configured Tracker Runtime decide when remote publication occurs; do not impose an extra Draft-PR phase.

## Integration Policy

If the target moves after Review, retain dual `PASS` only while the Candidate Review inputs remain unchanged. Before integration, refresh the current target, native mergeability, Integration Policy, Required Checks, and native merge evidence. Automatic integration requires platform evidence for the unchanged Candidate plus current target. If current-combination checks cannot be proved, pause through `CHECKS_BLOCKED` or follow the configured `human-merge` policy; do not infer safety from file overlap or a single `MERGEABLE` or `CLEAN` value, and do not trigger an extra full CI run.

A platform-native merge or squash preserves the dual `PASS` when Candidate Head is unchanged, no unreviewed conflict repair occurred, and native evidence binds that Candidate to `target_after`. A rebase, target merge into the Candidate Branch, manual conflict resolution, or any other Head rewrite returns through Repair Diagnosis, Coder validation, and dual Review.

Target refresh, mergeability and Check refresh, read-only Acceptance, and pre- or post-seal drift consume no repair round. A Candidate code change or Head rewrite enters Repair Diagnosis and consumes one round from the shared three-round budget when authorized.

- `auto-merge`: integrate only after both Verdicts have `PASS`, Base/Head and revision remain unchanged, and existing Required Checks, protection rules, and permissions pass.
- `human-merge`: persist `RUN_PAUSED` with reason=`READY_FOR_HUMAN_MERGE`, preserve the Branch and PR/MR, keep the Ticket Open, and refresh native facts after user action.
- Missing policy prohibits automatic merge. A one-run override requires explicit user confirmation recorded in the Tracker.
- Automatic integration does not authorize deployment, release, data migration execution, or any other irreversible external action.
- A closed but unmerged PR/MR is not integrated.

When a Required Check fails, inspect its existing evidence before acting. If the failure is candidate-caused, send its complete evidence into Repair Diagnosis before deciding whether it is in Scope. Route the diagnosis; only an authorized Candidate code change or Head rewrite consumes one ordinary repair round, invalidates both Verdicts, and repeats Coder validation and dual review. If the failure is caused by permissions, infrastructure, an unrelated target-branch failure, or evidence that cannot be attributed safely, persist `RUN_PAUSED` with reason=`CHECKS_BLOCKED`. Do not trigger an extra full CI run merely to classify the failure.

For `NO_CHANGE_REQUIRED`, verify `Base == Head` and both Reviewer Verdicts, then record `INTEGRATION_RESULT` with result=`ALREADY_PRESENT` and the current target as `target_before == target_after`; do not create an empty Commit or meaningless PR/MR.

In shared-branch mode, a Ticket completes after its Commit enters the declared Integration Branch. The final `integrate-and-verify` Ticket owns delivery to the target branch.

## Merge Conflicts

Diagnose compatibility and conflict evidence before invoking `$resolving-merge-conflicts`. For an authorized local or structural repair, return the work to the current Coder and keep it inside Ticket Scope; pause on `CONTRACT_BLOCKER`. Do not let the Scheduler choose a side or perform destructive reset, discard, or abort operations. After a resolved conflict changes code or Base, consume the shared repair round and return through Coder validation and both Reviewer gates.
