---
name: run-initiative
description: Load when the user explicitly wants to execute, resume, recover, or cancel delivery of one formal Tracker Spec, one clearly large spec-level Ticket, or one bounded Initiative made of Specs. Do not recommend for a small Ticket or for multiple Initiatives.
---

# Run an Initiative

Deliver one coherent body of work through one primary **Delivery Worker**. The primary context plans the work, writes the code, owns the branch and Commits, adjudicates Review Findings, runs the final Gate, and completes the PR and Tracker work. Do not create a separate Supervisor or Coder child Agent.

Use two isolated, read-only Reviewers only once per delivery branch, immediately before the final Gate and PR. Review is a one-time adversarial audit, not an approval loop. Findings inform the Delivery Worker; they do not control it.

## Supported delivery shapes

Choose exactly one shape before making changes.

### Large Ticket

Use this shape only when one Ticket is large enough to require several coherent implementation Slices.

- Treat the Ticket as a Spec-level delivery contract.
- Use one branch for the whole Ticket.
- The Delivery Worker plans the Slices.
- Before Review, each Slice corresponds to one complete logical Commit or an explicit evidence-only result when the required behavior is already present.
- Run one dual-axis Review, one final Gate phase, and one PR for the whole Ticket.

If the Ticket is a small, direct change through an existing seam, do not use this Skill. Recommend direct implementation instead. A small Ticket normally introduces no new state, fact source, lifecycle, permission model, migration, compatibility behavior, or cross-path coordination and can be observed with one narrow validation path.

### Spec

- Use one branch for the whole Spec.
- Treat the Spec's Tickets as implementation Slices, not independent delivery units.
- Order the Tickets by their real dependencies and implement them on the same branch.
- Before Review, each Ticket corresponds to one complete logical Commit or an explicit evidence-only result when the Ticket already requires no code change.
- Do not create a branch, Review, Gate, PR, repair cycle, or integration result per Ticket.
- Run one dual-axis Review, one final Gate phase, and one PR for the complete Spec.

### Bounded Initiative

Use this shape for one bounded Initiative containing multiple Specs. Do not use it to combine multiple Initiatives.

- Deliver the Specs in dependency order.
- Apply the **Spec** shape independently to each Spec: one branch and one PR per Spec.
- Create one isolated Spec Reviewer and one isolated Standards Reviewer when the first Spec reaches Review.
- Reuse those same two Reviewer threads for every later Spec in this Initiative; never create a fresh pair merely because the next Spec starts.
- Rebind both Reviewers to the current Spec, Base, Head, branch, contract, and Diff on every Review.
- Prior Specs' full Diffs and ordinary Findings are out of scope. Retain only the Initiative goal, approved cross-Spec invariants, and earlier facts that materially affect the current Spec.
- Merge or otherwise complete each Spec according to the declared dependency and Integration Policy before starting a dependent Spec.

## Entry and preflight

Before the first write:

1. Read repository instructions, the configured Tracker instructions, the complete selected Ticket, Spec, or Initiative, relevant comments and dependencies, applicable `CONTEXT.md` files and ADRs, and the current Git state.
2. Resolve the delivery shape, approved Scope, target branch, Integration Policy, required validation commands, and formal acceptance outcomes.
3. Verify Tracker and Git authentication, required permissions, target state, and worktree safety.
4. Refuse to absorb unrelated user changes. Stop before writing when the selected delivery unit, Scope, target, permissions, or contract cannot be determined safely.
5. Create or recover the delivery branch only after the preflight succeeds. Use exactly one branch per Large Ticket or Spec.

Use the configured Tracker and Git host as durable facts. Do not create a parallel Ledger, repair-cycle state machine, shadow Verdict store, per-Slice Claim, or execution-state label.

## Plan the Slices

The Delivery Worker owns the implementation plan.

- For a Large Ticket, derive the smallest coherent Slices needed to satisfy the complete Ticket.
- For a Spec, use its Tickets as Slices and preserve their declared dependencies and Scope.
- Give every Slice one observable purpose and either one intended logical Commit or an evidence-only result proving that the approved behavior is already present.
- Keep cross-Slice invariants and shared interfaces visible so local work does not create parallel fact sources or incompatible paths.
- Do not ask for approval of an implementation plan when it stays inside the already approved contract. Stop with `CONTRACT_BLOCKER` when correct work requires changing the approved product outcome, Scope, ADR, public interface, or failure behavior.

## Implement quickly

Implement Slices serially on the delivery branch.

- Do not create a Coder child Agent. The Delivery Worker investigates, edits, and commits directly.
- During Slice implementation, do not run the dual-axis Review, the complete repository Gate, CI, integration checks, PR checks, or formal Tracker checkpoints.
- The Delivery Worker may run narrow, fast local checks when they materially shorten the feedback loop. These checks are not delivery Gates and need no durable checkpoint.
- Keep unrelated changes out of every Commit.
- Temporary or fixup Commits are allowed while coding. Before Review, consolidate the history so each changed Slice or Ticket maps to one complete, explainable logical Commit.
- When a Slice or Ticket already satisfies its approved outcome, record it as `NO_CHANGE_REQUIRED` with its observed behavior and validation evidence. Map that evidence-only result into Review without creating an empty Commit.
- A Slice Commit may depend on earlier Slice Commits on the same branch; it does not need independent release or integration status.

Do not publish the PR until the one-time Review and final Gate phase are complete.

## One-time dual-axis Review

After every Slice is implemented and the logical Commit history is ready:

1. Freeze the delivery Base and Head and capture the complete branch Diff, Slice evidence map, approved contract, repository standards, and relevant evidence. The map binds each changed Slice to its logical Commit and each `NO_CHANGE_REQUIRED` Slice to its observable evidence.
2. Apply the review stance and axis-specific instructions from `$spec-standards-review`.
3. For a Large Ticket or standalone Spec, create one fresh isolated Spec Reviewer and one fresh isolated Standards Reviewer and run them in parallel.
4. For a Bounded Initiative, continue the Initiative's existing two Reviewer threads, preserving axis isolation and rebinding them to only the current Spec's frozen inputs.
5. Each Reviewer is read-only and returns Findings from only its own axis. Neither Reviewer reads or reacts to the other axis.
6. Collect both reports once. Do not ask either Reviewer to reconsider, approve repairs, review a changed Head, or enter a repair cycle.
7. Immediately preserve the frozen Base/Head, both complete reports, and their Finding IDs in a plain comment on the selected Tracker delivery item. This is the existing durable collaboration surface, not a Verdict, Event, Ledger, or approval gate.

Require comprehensive inspection but selective reporting: Reviewers must inspect the entire frozen Scope deeply and must not omit material current-delivery problems, while excluding low-value technical cleanliness, tooling-enforced issues, and speculative product or operating conditions outside the approved contract.

A clean report is valid. Reviewer output is evidence, not authority, and does not produce `PASS`, `REPAIR_REQUIRED`, a durable Verdict, or permission to merge.

## Adjudicate Findings once

The Delivery Worker considers every Finding independently and records one disposition:

- `FIXED`: the Finding identifies a real current-delivery problem; implement the smallest complete correction and bind it to a repair Commit and validation evidence.
- `REJECTED`: evidence shows that the Finding lacks current authority, a reachable consequence, concrete risk, or a violated requirement, or that the implementation already satisfies the required result. Record the reason; do not send it back for Reviewer approval.
- `CONTRACT_BLOCKER`: the Finding is valid but correct resolution requires changing the approved Spec, Scope, ADR, public interface, or product behavior. Stop without inventing the decision.

Do not automatically accept a Reviewer's preferred mechanism. Diagnose the underlying problem and choose the smallest complete correction that preserves existing concepts and facts.

After adjudicating every Finding, preserve the complete dispositions, reasons, repair Commits, validation evidence, and resulting Head in a second plain comment on the same Tracker item before entering the final Gate. If recovery finds the Review report but not this disposition record, re-adjudicate the persisted Findings against the current branch without contacting the Reviewers.

Never run a second Review. If resolution stays inside the approved contract but requires replacing the Slice plan or materially redesigning the implementation, invalidate the current candidate and stop with `REPLAN_REQUIRED`. If it requires any contract, Scope, ADR, public-interface, or product-behavior change, stop only with `CONTRACT_BLOCKER`. Do not silently perform a large rewrite and do not start an automatic Review loop.

## Final Gate and PR

After every Finding has a disposition:

1. Run the complete repository-required Gate against the actual delivery branch Head.
2. Diagnose and fix Candidate-caused failures, then rerun the affected and complete required checks until the Gate is green.
3. Keep Gate fixes in explicit Commits and preserve the Finding dispositions.
4. If a Gate failure exposes a material redesign that remains inside the approved contract, stop with `REPLAN_REQUIRED`. If it requires changing the contract, Scope, ADR, public interface, or product behavior, stop with `CONTRACT_BLOCKER`. Never widen the work silently.
5. Create one PR for the complete Large Ticket or Spec only after the local Gate is green.
6. Follow the repository's Integration Policy, branch protection, Required Checks, and permissions. Candidate-caused PR failures return directly to the Delivery Worker for diagnosis and repair; they never reopen Review.
7. Pause on infrastructure, permission, target, or external-check failures that cannot safely be attributed to the Candidate.
8. Merge only when the actual PR Head satisfies the required checks and policy. This Skill does not authorize deployment, release, production migration, or other post-delivery actions.

For a Spec, do not mark its Slice Tickets delivered merely because their Commits or evidence-only results exist. After the Spec PR is integrated, verify that every Ticket's intended Commit or `NO_CHANGE_REQUIRED` evidence and acceptance outcome are present, then complete the Tickets and Spec according to the configured Tracker. For a Large Ticket, complete the Ticket only after its PR is integrated. For a Bounded Initiative, complete each Spec after its own PR is integrated and complete the Initiative only after every member Spec is delivered.

When the delivery contract declares a `Release Boundary`, report the remaining Post-delivery action and its Tracking reference after delivery completes. Do not execute that action or create, claim, update, or close the referenced external item; release and deployment remain outside this Skill's authority.

## Recovery and cancellation

Recover from the formal Tracker item, its persisted Review and disposition comments, delivery branch, Commit history, existing PR, and current required-check facts. Reconstruct the remaining Slices and phase from those durable sources; do not recreate the old Scheduler, child-Coder, repair-cycle, or Verdict protocol.

If exact completion or Review history cannot be established safely, preserve the branch and stop with `BLOCKED`, naming the missing fact rather than guessing. Cancellation stops new work, preserves existing Git evidence, avoids destructive cleanup, and updates only the selected delivery unit when the configured Tracker requires it.

## Outcomes

- `COMPLETED`: the intended branch is integrated, required checks passed, Finding dispositions are complete, and the selected Tracker items reflect delivery.
- `REPLAN_REQUIRED`: the approved contract remains sufficient, but the current candidate is no longer trustworthy because correct work requires a materially different Slice plan or implementation design. Preserve the branch and stop; do not automatically start another Review.
- `CONTRACT_BLOCKER`: delivery requires changing or adjudicating an approved product outcome, Scope, ADR, public interface, or failure behavior. This outcome takes precedence whenever such a contract change is required.
- `BLOCKED`: permissions, infrastructure, required external evidence, target state, or another recoverable external condition prevents safe progress.
- `CANCELLED`: the requested delivery was stopped without discarding existing work.
- `FAILED_PRECONDITION`: required inputs or authority were invalid before delivery work began.

## Non-goals

- No separate Supervisor or Coder child Agent.
- No Ticket Frontier scheduler inside one Spec.
- No branch, Review, Gate, PR, or repair cycle per Slice/Ticket.
- No repeated Review after Findings or Gate fixes.
- No Reviewer Verdict or automatic Reviewer–Worker negotiation.
- No use for a small direct-coding Ticket.
- No execution of multiple Initiatives as one run.
