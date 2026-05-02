---
name: plan-initiative
description: Use when the user selects an Initiative or DESIGN.md and wants a runnable PLAN.md/LEDGER.md organized by Milestones for later run-initiative execution; do not use to code.
---

# plan-initiative

## Trigger

Use this skill when the user chooses an initiative, asks for a PLAN, asks to turn `DESIGN.md` into an executable plan, or asks to prepare work that will later be run by `run-initiative`.

## Goal

Write a concise `PLAN.md` that can be consumed directly by `run-initiative`, plus a minimal `LEDGER.md`. `DESIGN.md` is the design decision source of truth when present; `PLAN.md` is the execution contract.

Do not re-litigate design decisions from `DESIGN.md` unless it is missing, stale, contradicted by repository facts, or explicitly superseded by the user.

## DESIGN.md Status Gate

When an Initiative has `DESIGN.md`, `plan-initiative` may consume it only when the document contains:

```text
Status: Sealed
```

`Status: Draft`, `Status: Superseded`, missing `Status`, unknown status, or conflicting status markers are hard blockers for planning.

If the user asks to plan from a non-`Sealed` `DESIGN.md`, stop without writing or updating `PLAN.md` / `LEDGER.md`. Tell the user to return to `grill-initiative` to revise, restore, supersede, or seal the design first.

Do not convert `Draft` to `Sealed` inside `plan-initiative`. Sealing belongs only to `grill-initiative` after explicit user confirmation.

## DESIGN.md Intake Gate

After the status gate passes, run structural intake QA before writing or updating `PLAN.md` / `LEDGER.md`.

This gate is read-only for `DESIGN.md`. Do not repair, normalize, seal, rewrite, renumber, or reinterpret the design inside `plan-initiative`. If intake fails, stop and tell the user which DESIGN sections must be repaired in `grill-initiative`.

Required intake checks:

- `DESIGN.md` has no remaining angle-bracket template placeholders such as `<...>`.
- `Activation Blockers` exists and is `none`.
- `Leaf Resolution Matrix` exists.
- Every retained `Lxxx` leaf in the Value Question Directory Tree appears exactly once in the Leaf Resolution Matrix.
- `Decision Records` exists and contains accepted decisions when the matrix has any `Decided` leaf.
- Every accepted Decision Record has `Covers: Lxxx`.
- Every accepted Decision Record has non-empty `Design Impact`.
- Every accepted Decision Record has non-empty `Downstream Constraint`.
- Rejected alternatives, design follow-ups, and residual risks are preserved when present.

If the DESIGN uses a legacy `Coverage Check` section instead of `Leaf Resolution Matrix`, treat it as insufficient for new planning unless the user explicitly asks for legacy handling. Prefer sending it back through `grill-initiative` to produce a sealed matrix-backed DESIGN.

When intake passes, carry all `Downstream Constraint` content into `PLAN.md` as planning constraints, acceptance criteria, validation checks, or reviewer focus. Do not silently drop downstream constraints because they are not convenient Milestone work items.

## Read First

1. The user request, selected recommendation file, and `<initiative-root>/DESIGN.md` when present
2. Existing ADR, gap, audit, or product docs referenced by `DESIGN.md` or the user
3. Relevant source and test areas
4. Existing `docs/initiatives/active/<initiative-code>-<slug>/PLAN.md` if updating an active initiative
5. Existing `docs/initiatives/active/<initiative-code>-<slug>/LEDGER.md` if execution has already started
6. Existing `docs/initiatives/handoff/` findings when the selected initiative is based on prior handoff
7. Existing `docs/initiatives/completed/` and `docs/initiatives/archived/` entries when avoiding duplicate initiatives

## Write Target

Default initiative directory:

```text
docs/initiatives/active/<initiative-code>-<initiative-slug>/
```

Initiative naming rules:

- Every new initiative directory name must start with a three-digit code prefix, such as `001-auth-hardening`.
- Determine `<initiative-code>` by scanning existing `docs/initiatives/handoff/`, `active/`, `completed/`, and `archived/` entries and choosing the next unused three-digit code. Recommendation snapshot codes are provisional and do not reserve numbers.
- Preserve an existing code when updating an active initiative.
- When expanding a recommendation, preserve its proposed code only if that code is still unused by `handoff/`, `active/`, `completed/`, and `archived/`; otherwise assign the next unused code.
- Use the same coded slug consistently in PLAN paths, LEDGER paths, branches, evidence paths, and completion paths.

Required files:

```text
PLAN.md
LEDGER.md
```

Optional files:

```text
DESIGN.md                 # optional, but when present must be Status: Sealed
evidence/                 # created by run-initiative as needed
```

## Planning Rules

- Milestone is the explicit delivery unit.
- Each Milestone should contain 3-5 work items.
- A normal initiative should contain 3-8 Milestones.
- Avoid more than 10 Milestones. Split the initiative if more are needed.
- Add an Acceptance & Hardening Milestone after important or risky business capability Milestones when quality needs a dedicated pass.
- Every Milestone must include acceptance criteria and reviewer focus.
- Use “Work Items” instead of turning implementation notes into formal scheduling objects.
- Do not generate document slices, old planning state, or old runtime state.
- For an existing active initiative, preserve `LEDGER.md` execution facts. Do not reset `PASS`, `REVIEW`, `REPAIR`, `PAUSED`, or `CANCELLED` Milestones unless the user explicitly asks for a plan rewrite.

## Language Rule

- Write `PLAN.md`, `LEDGER.md`, and any planning-support documents in the primary language of the user's request by default.
- If the request mixes languages, follow the language used for the user's requirements and decisions.
- Preserve technical identifiers, file paths, commands, code symbols, branch names, status tokens, and tool names as written.
- Keep protocol values such as `TODO`, `CODING`, `REVIEW`, `REPAIR`, `PASS`, `PAUSED`, `CANCELLED`, and `REPAIR_REQUIRED` unchanged.
- If the user explicitly requests a language, that instruction overrides the default.
- Template headings and explanatory text are structural guidance; translate or adapt them to the output language when writing the final document.

## Workflow

1. If `DESIGN.md` exists, read it first and verify it contains exactly one effective `Status: Sealed` marker before using it as a planning source.
2. If `DESIGN.md` exists but is not `Status: Sealed`, stop without writing `PLAN.md` or `LEDGER.md` and recommend `grill-initiative` sealing or revision.
3. Run the `DESIGN.md Intake Gate`. If intake fails, stop without writing `PLAN.md` or `LEDGER.md`.
4. Preserve sealed Decision Records, rejected alternatives, downstream constraints, design follow-ups, residual risks, and disposition.
5. If there is no `DESIGN.md` and the initiative still has blocking design ambiguity, stop and recommend `grill-initiative` before writing `PLAN.md`.
6. Read enough repository context to avoid guessing about architecture, tests, and validation commands.
7. Summarize execution-relevant design decisions, downstream constraints, and current gaps without copying entire reference docs.
8. Group work into Milestones that each produce an inspectable state.
9. Keep each Milestone to 3-5 work items.
10. Define concrete acceptance criteria for each Milestone.
11. Define validation commands or manual checks for each Milestone.
12. Add structured visual / UX checks for UI changes, including preview target, viewports, required states, and screenshot evidence.
13. Add reviewer focus for product, test, and architecture perspectives.
14. For a new initiative, create a minimal `LEDGER.md` skeleton using `references/ledger-template.md`, with all Milestones initially `TODO`.
15. For an existing active initiative, preserve existing `LEDGER.md` execution facts and only append or adjust future Milestones unless the user explicitly requests a full rewrite.

## Quality Bar

A valid PLAN:

- can be executed by a Scheduler without re-planning
- tells Coder what to read, what to change, what not to change, and how to validate
- tells Reviewer how to decide `PASS` vs `REPAIR_REQUIRED`
- consumes `DESIGN.md` only when it is `Status: Sealed`
- refuses sealed-but-incomplete `DESIGN.md` when structural intake QA fails
- preserves sealed `DESIGN.md` as design decision source of truth when present
- carries sealed DESIGN downstream constraints into scope, acceptance, validation, or reviewer focus
- includes a hardening Milestone when a risky capability needs quality consolidation
- avoids vague acceptance like “works well”, “tests sufficient”, or “code clean”
- avoids duplicating active or completed initiatives unless the new plan is explicitly a follow-up or v2
- does not overwrite existing execution facts when updating an active initiative

## Output Shape

Use `references/plan-template.md` as the canonical PLAN shape, `references/ledger-template.md` as the canonical LEDGER shape, and `references/hardening-milestone-template.md` when adding a hardening Milestone.

## Hard Stops

Stop and report a blocker if:

- `DESIGN.md` exists and does not contain exactly one effective `Status: Sealed` marker
- `DESIGN.md` exists with `Status: Draft`, `Status: Superseded`, missing status, unknown status, or conflicting status markers
- `DESIGN.md` exists but fails the `DESIGN.md Intake Gate`
- the user asks `plan-initiative` to seal, rewrite, or normalize `DESIGN.md`
- there is no `DESIGN.md` and blocking design ambiguity remains
