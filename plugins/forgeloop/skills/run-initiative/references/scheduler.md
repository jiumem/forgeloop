# Scheduler Protocol

## Entry and Scope

Resolve formal references and read their complete bodies, comments, relationships, and current state. Run one Spec directly. Before creating a parent Item for multiple Specs, show the member Specs, cross-Spec Dependencies, target branch, Integration Policy, and material risks, then wait for explicit user confirmation. Build the canonical parent title as `[Initiative] <outcome-oriented title>` and render the `[Initiative]` prefix exactly once, even when the supplied title already contains a canonical or legacy prefix. Derive `initiative_revision` from the confirmed member references and revisions, target branch, and Integration Policy before creation. Query for an existing parent with that Revision and canonical title: reuse one unique valid match, stop on ambiguous matches, and create only when none exists. If creation returns an ambiguous result, query again before retrying. Preserve the confirmation as a native Tracker comment. Require renewed confirmation when any member changes.

## Preflight

Before the root Claim, verify the configured Tracker runtime, CLI, authentication, repository permissions, Integration Policy, formal references, revisions, dependency graph, target branch, Branch Protection or Protected Branch, Required Checks, current Base, and worktree.

Do not test child availability by creating disposable children. Handle an actual creation failure at the phase where that role is required. Return `FAILED_PRECONDITION` before the root Claim for every other preflight failure.

Do not start a new Ticket when the worktree contains changes not owned by a recoverable current Run. On recovery, bind every retained change to the original Ticket and candidate Branch before continuing.

## Root Claim and Frontier

Place the one competitive `RUN_CLAIMED` record on the run root: the Spec for a single-Spec run or the Initiative parent for a multi-Spec run. On GitHub or GitLab, the earliest valid server-side root Claim wins. For Local, the atomic Scheduler lock wins. A losing Scheduler stops without creating a Coder.

After winning the root Claim, recompute the Frontier from native Tracker facts on every round. Use explicit Tracker order when available; otherwise use ascending persistent Ticket ID. Select and natively claim only one Open, Unblocked, Unclaimed Ticket. Do not duplicate the Ticket Claim as a second Event.

When no Ticket is eligible, report Completed, Blocked, Claimed, Invalid Reference, and State Conflict buckets. Complete only when every required Ticket is integrated and final Acceptance passes; otherwise pause with the concrete blockers.

## Role Task Pack

Every first child message must be self-contained because it does not inherit the Scheduler conversation. Include:

- the role and objective;
- the resolved path to the applicable role protocol;
- frozen Ticket, Spec, revision, Base, Head or target, and Integration mode;
- only the repository instructions, ADRs, dependency conclusions, and evidence needed by that role;
- writable Scope for a Coder or explicit read-only Scope for a Reviewer;
- the required result and stop conditions.

Do not include host-specific child configuration or unrelated Scheduler history. The task message defines the role.

## Child Continuity

- Create one fresh Coder only after the Ticket Claim succeeds.
- Create the two fresh Reviewers only after a valid Coder result freezes Base/Head.
- The two Reviewers may run concurrently, but neither may receive or discover the other axis's result.
- For live repair rounds, continue the same Coder and the same two Reviewer threads so each role retains its own history.
- After the Ticket ends, send no further work to those threads and create fresh children for the next Ticket. Do not depend on a host-level close operation.
- On cancellation, stop dispatching and best-effort interrupt only the currently running children.
- After Scheduler-task recovery, do not depend on old child availability. Create a fresh child for the required role from durable Tracker and Git facts.

If a required child cannot actually be created, persist `RUN_PAUSED` with reason=`AGENT_UNAVAILABLE`; never collapse the two review axes into one role.

If a Reviewer returns `REVIEW_BLOCKED`, finish collecting the other axis without exposing either result. When access to the exact same frozen inputs is restored without changing their contents, continue only the blocked Reviewer. When Ticket, Spec Revision, Base/Head, Coder evidence, or any other shared input changes, invalidate both collected results and continue both original Reviewers with the corrected common task pack. Otherwise persist the combined result and `RUN_PAUSED` with reason=`REVIEW_BLOCKED`. Do not send blocked input to the Coder or consume an ordinary repair round.

## Repair Diagnosis Routing

Before repair, validate that every diagnosis field is present, then route the declared classification under the Repair protocol. The Scheduler must not classify the mechanism itself, merge classifications, or authorize a repair from an incomplete diagnosis. It must not merge, reorder, or rewrite Reviewer Findings.

## Scheduler Responsibilities

- After every Ticket Claim, refresh the declared target or Integration Branch and freeze Base from its current Head before preparing the Ticket Branch.
- Publish idempotent durable checkpoints after validating their references.
- Do not advance the Frontier, Integration, Acceptance, or Closure until native read-back confirms the complete Prepared Literal Payload.
- After an Acceptance Reviewer returns `PASS`, refresh the target again before rendering an Acceptance `PASS` Payload.
- Validate that the reported Head equals the Ticket Branch Head, all Ticket implementation changes are committed, unrelated worktree changes remain outside the candidate, and the fixed Base is still valid. Do not rerun the Coder's complete validation suite.
- Hold both Reviewer results privately until both finish, then validate their common Base/Head and persist one combined review checkpoint.
- Orchestrate repair, remote branch publication, PR/MR creation or reuse, Required Checks, merge, pause, cancellation, recovery, acceptance, and Tracker closure.
- Consume naturally occurring CI according to repository policy; do not trigger an extra full CI run.

Do not let the Scheduler implement a fix, resolve a code conflict itself, override a Reviewer judgment, or treat orchestration state as proof of code behavior.
