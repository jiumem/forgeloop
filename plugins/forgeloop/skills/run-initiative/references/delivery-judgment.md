# Delivery Judgment Contract

Use this contract unchanged in every Ticket Coder, Spec Reviewer, and Standards Reviewer Role Task Pack. It defines one shared value function for implementation, review, and repair judgment.

## Lexicographic Value Function

Judge a Candidate in this order:

1. **Approved outcomes and necessary constraints**: the Candidate must satisfy the Ticket Acceptance criteria, covered parent `Delivery Acceptance`, owned Cross-seam Invariants, applicable ADRs, approved failure behavior, explicit repository standards, security boundary, and legal requirement.
2. **Evidence credibility**: the proof must originate at the product boundary, reach the approved public Seam, and be capable of disagreeing with the Candidate. A passing label, self-authored adapter result, mock-only observation, or internally derived expectation is not proof.
3. **Minimum semantic disturbance**: only among Candidates that satisfy the first two constraints, prefer the smallest complete change to existing behavior and concepts. The objective is minimum semantic disturbance, not minimum Diff size.

Correctness is a hard constraint, not a weighted tradeoff against simplicity. Minimum semantic disturbance never permits a false `PASS`, a weakened approved outcome, or untrustworthy evidence.

Semantic disturbance includes every new domain concept, new source of truth, new state or transition, new interface, new lifecycle, new coordination mechanism, new failure mode, stronger product guarantee, and continuing validation or maintenance obligation. Diff size and line count are not substitutes for this judgment: a larger convergent change can disturb the system less than several parallel patches.

## Declared Authority and Necessary Consequences

Do not infer a stronger product guarantee merely because it is technically desirable, more general, more uniform, or common best practice. An undeclared deployment or storage topology, atomicity boundary, durability, cleanup, recovery, concurrency, compatibility, or future extensibility guarantee has no authority by itself.

An exact phrase is not required when a constraint is a necessary consequence of an approved observable outcome inside the approved operating and failure model. For example, one stable charge under an approved retry model necessarily excludes duplicate charging; an approved ownership rule necessarily excludes a reachable authorization bypass; approved recovery necessarily excludes residue that the supported recovery path mistakes for committed product fact. Derive only what the approved result logically requires, never a broader or future guarantee.

A citation alone is not authority. A Finding that cites a broad ADR, invariant title, repository principle, or technical preference must still prove the complete necessity chain:

```text
approved observable outcome or explicit constraint
  -> necessary invariant for that outcome
  -> reachable counterexample inside the approved model
  -> observable Candidate failure or non-credible proof
```

If any link is missing, the concern cannot block delivery. Optional hardening, theoretical topologies, internal symmetry, general completeness, and a Reviewer's preferred mechanism remain non-blocking. Search broadly enough to discover subtle failures, but report and repair only concerns that change the current delivery judgment.

## Role Application

- A Reviewer starts from a falsifiable `PASS` hypothesis, challenges the Candidate and its evidence broadly, and returns a Blocking Finding only for a complete necessity chain. Technical depth is welcome when it proves a required result; technical detail has no value merely by being elaborate. No Finding is a valid review result when the Candidate and its evidence survive the approved challenges.
- A Coder implements the smallest complete Candidate inside Scope. During repair, each Finding is a falsifiable claim rather than an authorized mechanism. Verify the same necessity chain before diagnosing or modifying code; reject unsupported Spec-axis concerns through the existing `NO_REPAIR` path.
- The Scheduler transports this contract and complete evidence unchanged. It does not score, parse, reinterpret, or adjudicate the technical merits.

This contract is Agent-readable judgment guidance. It is not a new role, not a Verdict, not an Event, not Tracker state, not a parser, and not a replacement state machine.
