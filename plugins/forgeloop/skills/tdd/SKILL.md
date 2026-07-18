---
name: tdd
description: Load when implementing a feature or fixing a bug test-first, especially through a reliable public behavior seam.
---

# Test-Driven Development

TDD is the red → green loop. This skill is the reference that makes that loop produce tests worth keeping: what a good test is, where tests go, the anti-patterns, and the rules of the loop. Every section applies on every cycle — consult them before and during the loop, not after.

When exploring the codebase, read `CONTEXT.md` (if it exists) so test names and interface vocabulary match the project's domain language, and respect ADRs in the area you're touching.

## What a good test is

Tests verify behavior through public interfaces, not implementation details. Code can change entirely; tests shouldn't. A good test reads like a specification — "user can checkout with valid cart" tells you exactly what capability exists — and survives refactors because it doesn't care about internal structure.

See [tests.md](tests.md) for examples and [mocking.md](mocking.md) for mocking guidelines.

## Seams — where tests go

A **seam** is the public boundary you test at: the interface where you observe behavior without reaching inside. Tests live at seams, never against internals.

**Test only at pre-agreed seams.** Before writing any test, write down the seams under test and confirm them with the user. No test is written at an unconfirmed seam. You can't test everything — agreeing the seams up front is how testing effort lands on the critical paths and complex logic instead of every edge case.

Ask: "What's the public interface, and which seams should we test?"

## Anti-patterns

- **Implementation-coupled** — mocks internal collaborators, tests private methods, or verifies through a side channel (querying the database instead of using the interface). The tell: the test breaks when you refactor but behavior hasn't changed.
- **Tautological** — the assertion recomputes the expected value the way the code does (`expect(add(a, b)).toBe(a + b)`, a snapshot derived by hand the same way, a constant asserted equal to itself), so it passes by construction and can never disagree with the code. Expected values must come from an independent source of truth — a known-good literal, a worked example, the spec.
- **Horizontal slicing** — writing all tests first, then all implementation. Bulk tests verify _imagined_ behavior: you test the _shape_ of things rather than user-facing behavior, the tests go insensitive to real changes, and you commit to test structure before understanding the implementation. Work in **vertical slices** instead — one test → one implementation → repeat, each test a **tracer bullet** that responds to what the last cycle taught you.

## Rules of the loop

- **Red before green.** Write the failing test first, then only enough code to pass it. Don't anticipate future tests or add speculative features.
- **One slice at a time.** One seam, one test, one minimal implementation per cycle.
- **Refactoring is not part of the loop.** It belongs to the review stage (see the `spec-standards-review` skill), not the red → green implementation cycle.

## Forgeloop Orchestrated Invocation

When an owning Workflow supplies an approved Validation Entry, public Seam, Scope, and stop conditions, treat that as the already-approved public Seam. Do not ask the user to approve it again, choose a different Seam, or expand the contract from inside the child task. Return control to the owning Workflow when the supplied strategy is missing or contradictory.

Use this Skill for a reproducible behavior change: new behavior, a defect repair, or a recovery behavior whose missing result can be observed through the approved public Seam. Run the public entry from the repository root before modifying production code. The Red must fail because the target behavior is absent, not because of a syntax error, unavailable unrelated service, or deliberately broken fixture. When the test does not exist at Base, the valid Red state is the frozen Base production code plus only the new test. Preserve the actual command and failure, implement the smallest vertical change, then run the same repo-root command against the final Head and observe Green.

Do not manufacture a Red for behavior-preserving work, `NO_CHANGE_REQUIRED`, or an external condition that the current environment cannot legally establish. Those cases follow the owning contract's approved baseline, structural, or external validation path. If a required behavior-changing Red cannot be reproduced through the approved Seam, return the blocker; do not substitute an internal helper, mock-only path, recording adapter, or harness-generated conclusion.
