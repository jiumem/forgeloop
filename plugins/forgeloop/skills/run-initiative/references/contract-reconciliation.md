# Contract Reconciliation

## One Adjudication Boundary

Use this protocol only for a confirmed `RUN_PAUSED / CONTRACT_BLOCKER`. Keep ordinary repair budget unchanged and prohibit Candidate, Spec, ADR, and Ticket contract mutation until one user decision is published and exactly read back.

The coordinating Agent first synthesizes one complete reconciliation package from the effective contract, blocker evidence, Candidate and Verdict history, and current Tracker/Git facts. It must state:

- the old Run and pause, predecessor Spec/Ticket/ADR Revisions, and exact contract conflict;
- the complete proposed Spec and ADR content;
- each Open Ticket's target complete body and relationships as `retain`, `update`, `supersede`, or `create`, including allowed equivalent outcomes;
- Candidate and Verdict disposition, repair-budget effect, Repair Lineage, and the recovery result;
- `REJECT`, `APPROVE_PAUSE`, and `APPROVE_CONTINUE` as the only user choices.

Derive `package_id` from the exact rendered package. The identity supports authorization, idempotency, and drift detection; it does not replace Agent judgment about Scope, materiality, equivalence, or contract meaning.

Before asking the user, create one fresh isolated read-only Agent for internal Design Review, bound to the entire package and current native facts. It checks contract completeness, Ticket coverage, fact ownership, forward recovery, Candidate invalidation, and whether the core Problem, primary Actor, or observable delivery outcome changed. This is a temporary semantic review task, not a new durable Reviewer type or Verdict.

Require one semantic result:

- `PASS`: no Finding remains and the complete fixed package may be presented to the user;
- `DESIGN_GAPS`: every Finding states evidence, the missing decision or clarification, required proof, and `contract_impact: NONE | SPEC | ADR`;
- `REVIEW_BLOCKED`: required fixed input is unreadable or contradictory, with the missing fact identified.

Resolve `contract_impact=NONE` gaps autonomously and repeat internal Design Review on the complete revised package. Fold every genuine Spec or ADR choice into that same final package and repeat Review so the user is asked exactly once. Ask the user only after a `PASS`; `DESIGN_GAPS` or `REVIEW_BLOCKED` keeps contract writes at zero and does not count as user adjudication.

## Record the Decision

Present the complete reviewed package and ask for one choice. Append the exact choice, `package_id`, complete package, Run, pause, and predecessor Revisions to the paused Run's root Tracker Item. Render the complete record to a temporary file with a non-interpreting file-writing capability, publish through the configured file-backed Tracker operation, and exactly read it back. Never place dynamic package text in an inline body/message argument, shell interpolation, or command substitution. No contract write may begin before confirmation.

- `REJECT`: keep the original `CONTRACT_BLOCKER`, make no Spec, ADR, Ticket, Candidate, or Run change, and never execute that `package_id`.
- `APPROVE_PAUSE`: authorize the complete package and finish reconciliation, then remain paused.
- `APPROVE_CONTINUE`: authorize the same reconciliation and, only after complete native verification, compete to resume the original Run.

Any missing approval, changed package content, predecessor drift outside an approved equivalent boundary, ambiguous native result, or conflicting decision stops with zero further writes.

## Forward-Only Reconciliation

Orchestrate existing fact owners with self-contained task packs carrying the approval record and exact package. The user does not invoke or approve them separately:

1. `$to-spec` publishes and exactly reads back the canonical Spec Revision.
2. `$domain-modeling` publishes every required approved ADR Revision through the existing Git/PR policy and returns immutable Commit evidence.
3. Only after all required Spec and ADR facts are confirmed, `$to-tickets` reconciles affected Open Tickets, relationships, canonical effective Ticket Revisions, and Repair Lineage.
4. Read back the complete Spec/ADR/Ticket graph, Delivery Acceptance coverage, Frontier, Candidate disposition, and effective Revisions.

Reuse equivalent confirmed facts and fill only missing approved work. Never roll back a confirmed write, edit Completed or Closed Ticket history, or treat an intermediate body or relationship as an effective Revision. Preserve every prior Candidate Branch, Commit, Finding, and evidence reference as reusable read-only input; a new Revision invalidates qualification rather than evidence, so reused work must form a new Candidate bound to the effective Revisions and receive fresh dual review. Conflicting successors, unapproved drift, or incomplete proof leaves the Run paused at `RECOVERY_CONFLICT`.

If the core Problem, primary Actor, or observable delivery outcome changed, do not publish a Spec Revision or any reconciliation write. Exactly publish and read back `RUN_CANCELLED` for the old Run, stop dispatching and best-effort interrupt its active children, preserve its Tracker and Git history, release only its Claims, and require a new formal Spec. The old Run must never publish `CONTRACT_RECONCILED`, compete to Resume, or execute the old `package_id`.

After every approved fact agrees, publish and exactly confirm the existing `RUN_PAUSED` event with reason=`CONTRACT_RECONCILED`, the approval reference, canonical Revisions, Ticket graph, Candidate disposition, Repair Lineage, and recovery choice.

## Pause or Resume

`APPROVE_PAUSE` stops at the confirmed reconciliation anchor. A later explicit resume must compete from that same anchor.

For `APPROVE_CONTINUE`, reuse the Competitive Automatic Repair Resume fence from `events-and-recovery.md` with the confirmed `RUN_PAUSED / CONTRACT_RECONCILED` native record as `cycle_anchor`. Each executor uses a stable distinct `resume_attempt_id`; the earliest valid immutable native record is the only winner. Before Candidate mutation, recheck cancellation, Claims, Spec/Ticket/ADR Revisions, Ticket graph, Candidate Branch, and Head. Losers and conflicting native order stop.

Cancellation remains authoritative. After confirmed `RUN_CANCELLED`, start no new business write, only resolve ambiguous in-flight writes by reading native facts, preserve confirmed history, release the old Run's Claims, and never resume it.
