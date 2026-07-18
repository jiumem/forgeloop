# Repair, Branch, and Integration Protocol

## Repair Cycles

One repair cycle contains at most three ordinary Candidate-changing repair rounds. The initial cycle is anchored by the confirmed native Ticket Claim and effective Spec, Ticket, and applicable ADR revisions. A renewed cycle is anchored by the exact native `RUN_PAUSED / REPAIR_BUDGET` record that ended the preceding cycle.

Use the same Ticket, Run, and Branch across cycles. Bind Coder results, combined Review results, repair rounds, pauses, diagnoses, and resumes to the current `cycle_anchor`. Old-cycle evidence may inform diagnosis but cannot authorize a new-cycle Candidate or Verdict.

Use one Coder and two isolated Reviewers throughout an active cycle. After automatic renewal, continue the fresh Coder that performed Exhaustion Diagnosis and create two fresh isolated Reviewers for the renewed cycle. Child identity remains live orchestration context, not durable state.

## Repair Loop

For Reviewer Findings, a candidate-caused Required Check failure, or compatibility or merge-conflict resolution, continue the original Coder for a separate read-only Coder turn that follows the Repair Diagnosis protocol. Complete it before authorizing any candidate code change; the Scheduler then validates its structure and routes the declared classification.

Diagnosis is a zero-write, zero-budget preflight and does not create durable Tracker state. If it is interrupted before the repair result, rerun the diagnosis from current durable evidence before any further code change.

Route the complete diagnosis as follows:

- `LOCAL_REPAIR`: the existing interface can honestly express the correct behavior, there is one authoritative fact source, and no shared Seam or parallel path needs convergence. Continue the original Coder inside Ticket Scope.
- `STRUCTURAL_REPAIR`: a correct in-Scope repair must converge a fact source, interface, shared Seam, or parallel implementation. Continue the original Coder, require it to invoke `$codebase-design` before modifying code, then implement the declared convergence and prove it through the public Seam.
- `CONTRACT_BLOCKER`: a correct repair must expand Ticket Scope or change the Spec, Ticket Acceptance criteria, product behavior, an ADR, or an approved public interface. Persist the existing contract-blocker pause; do not authorize code changes or consume a repair round.

When either axis returns `REPAIR_REQUIRED`, wait for the other axis, then continue the original Coder with both complete Finding sets. Do not merge, reorder, or reinterpret Findings. Continue each original Reviewer with the new fixed Head and only that Reviewer's own axis history.

Every later authorized code-changing repair returns to the Validation Strategy and TDD rules in [coder.md](coder.md). Repair Diagnosis and Exhaustion Diagnosis are read-only and do not invoke `$tdd`; when the approved repair changes reproducible public behavior, the subsequent code-changing turn invokes it before production edits.

Allow at most three ordinary repair rounds per `cycle_anchor`. Count every authorized Candidate code change or Head rewrite against this cycle budget, whether triggered by Reviewer Findings, a candidate-caused Required Check failure, rebase, or compatibility or merge-conflict resolution. Diagnosis turns do not consume this budget. A contract blocker or external infrastructure failure also consumes no round.

The second and third diagnoses must compare current evidence with prior diagnosis and repair history, state whether the prior mechanism hypothesis was falsified, and identify whether different `finding_id` values share one mechanism. New evidence may escalate `LOCAL_REPAIR` to `STRUCTURAL_REPAIR` or `STRUCTURAL_REPAIR` to `CONTRACT_BLOCKER`; it must not downgrade `STRUCTURAL_REPAIR` to `LOCAL_REPAIR` without new evidence.

After the third repair, a fixed Head with two fresh `PASS` Verdicts may integrate normally. If any Blocking Finding, candidate-caused failure, or unresolved compatibility or merge conflict remains, publish and exactly confirm `RUN_PAUSED` with reason=`REPAIR_BUDGET`; do not start a fourth repair in that cycle. Preserve the Run, Ticket Claim, Branch, Candidate, Findings, validation evidence, diagnosis history, and the cycle's start and end evidence.

Only after that pause is confirmed may the Scheduler create a fresh Coder for the read-only Exhaustion Diagnosis defined in [coder.md](coder.md). Give it the complete semantic context; do not ask it to infer missing evidence from field names or summaries.

The Coder owns the semantic recommendation. The Scheduler checks completeness and contradiction against the same context and current native facts, but does not parse, score, keyword-match, or independently recompute mechanism, Scope, progress, or recommendation:

- `AUTO_REPAIR_RENEWAL`: when the Agent concludes that the old mechanism is falsified, a materially different in-Scope hypothesis is credible and falsifiable, and real net progress exists. Compete to publish and exactly confirm `RUN_RESUMED` with reason=`AUTO_REPAIR_RENEWAL`; only the winning native Resume may authorize Candidate mutation.
- `IMPLEMENTATION_BLOCKED`: publish and exactly confirm `RUN_PAUSED` with reason=`IMPLEMENTATION_BLOCKED`, preserving the complete diagnosis. An unconditional continue is insufficient. Only a bound new fact or hypothesis, contract reclassification, or cancellation may re-enter read-only Exhaustion Diagnosis.
- `CONTRACT_BLOCKER`: keep the Run paused with zero Candidate mutation and zero repair-budget effect when correct work requires changing the formal contract.

Automatic repair has no fixed total-cycle ceiling. Every renewed cycle repeats the same three-round boundary and semantic exhaustion gate without creating a replacement Ticket, Run, or Branch.

Any code change, rebase, replacement of the frozen review Base, or conflict resolution invalidates both prior Verdicts. Target movement alone does not. Require the Coder to validate the new Head and both Reviewers to issue fresh Verdicts for the complete cumulative Diff.

## Branch Ownership

Use one independent Branch per Ticket by default. Use a shared Spec Integration Branch only when `$to-tickets` declared `WIDE_REFACTOR`, `NON_GREEN_MIGRATION`, `ATOMIC_DELIVERY`, or `CUMULATIVE_AUDIT` together with `Final integration gate owner: SPEC_ROOT`. Neither the Scheduler nor Coder may switch modes ad hoc. Every shared delivery follows [final-integration-gate.md](final-integration-gate.md); cumulative delivery also follows [cumulative-audit.md](cumulative-audit.md).

The Scheduler prepares the Branch and Base. The Coder edits, validates, and commits only Ticket Scope. Reviewers inspect fixed Commit objects. The Scheduler owns push, PR/MR creation or reuse, Required Checks, merge, and closure. Let the configured Tracker Runtime decide when remote publication occurs; do not impose an extra Draft-PR phase.

## Integration Policy

If the target moves after Review, retain dual `PASS` only while the Candidate Review inputs remain unchanged. Before integration, refresh the current target, native mergeability, Integration Policy, Required Checks, and native merge evidence. Automatic integration requires platform evidence for the unchanged Candidate plus current target. If current-combination checks cannot be proved, pause through `CHECKS_BLOCKED` or follow the configured `human-merge` policy; do not infer safety from file overlap or a single `MERGEABLE` or `CLEAN` value, and do not trigger an extra full CI run.

A platform-native merge or squash preserves the dual `PASS` when Candidate Head is unchanged, no unreviewed conflict repair occurred, and native evidence binds that Candidate to `target_after`. A rebase, target merge into the Candidate Branch, manual conflict resolution, or any other Head rewrite returns through Repair Diagnosis, Coder validation, and dual Review.

Target refresh, mergeability and Check refresh, read-only Acceptance, and pre- or post-seal drift consume no repair round. A Candidate code change or Head rewrite enters Repair Diagnosis and consumes one round from the current cycle's three-round budget when authorized.

- `auto-merge`: integrate only after both Verdicts have `PASS`, Base/Head and revision remain unchanged, and existing Required Checks, protection rules, and permissions pass.
- `human-merge`: persist `RUN_PAUSED` with reason=`READY_FOR_HUMAN_MERGE` and preserve the Branch and PR/MR. Ticket integration keeps that Ticket Open; a Final Integration Gate must keep the Spec Open with no current Ticket. Refresh native facts after user action.
- Missing policy prohibits automatic merge. A one-run override requires explicit user confirmation recorded in the Tracker.
- Automatic integration does not authorize deployment, release, data migration execution, or any other irreversible external action.
- A closed but unmerged PR/MR is not integrated.

When a Required Check fails, inspect its existing evidence before acting. If the failure is candidate-caused, send its complete evidence into Repair Diagnosis before deciding whether it is in Scope. Route the diagnosis; only an authorized Candidate code change or Head rewrite consumes one ordinary repair round, invalidates both Verdicts, and repeats Coder validation and dual review. If the failure is caused by permissions, infrastructure, an unrelated target-branch failure, or evidence that cannot be attributed safely, persist `RUN_PAUSED` with reason=`CHECKS_BLOCKED`. Do not trigger an extra full CI run merely to classify the failure.

For `NO_CHANGE_REQUIRED`, verify `Base == Head` and both Reviewer Verdicts, then record `INTEGRATION_RESULT` with result=`ALREADY_PRESENT` and the current target as `target_before == target_after`; do not create an empty Commit or meaningless PR/MR.

In shared-branch mode, an ordinary Ticket completes after its reviewed Candidate enters the declared Integration Branch. After all ordinary Tickets complete legally, the Spec Root Final Integration Gate owns target delivery; no Ticket owns that Gate.

## Merge Conflicts

Diagnose compatibility and conflict evidence before invoking `$resolving-merge-conflicts`. For an authorized local or structural repair, return the work to the current Coder and keep it inside Ticket Scope; pause on `CONTRACT_BLOCKER`. Do not let the Scheduler choose a side or perform destructive reset, discard, or abort operations. After a resolved conflict changes code or Base, consume the shared repair round and return through Coder validation and both Reviewer gates.
