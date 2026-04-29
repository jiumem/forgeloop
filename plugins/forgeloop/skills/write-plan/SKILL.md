---
name: write-plan
description: Use when the user selects an Initiative or gives a requirement and wants a runnable PLAN.md/LEDGER.md organized by Milestones for later run-initiative execution; do not use to code.
---

# write-plan

## Trigger

Use this skill when the user chooses an initiative, asks for a PLAN, asks to turn a requirement into an executable plan, or asks to prepare work that will later be run by `run-initiative`.

## Goal

Write a concise `PLAN.md` that can be consumed directly by `run-initiative`. The PLAN is the only execution planning contract for a selected initiative.

Design docs, ADRs, gap notes, audits, user requests, and existing code are reference inputs. They are not Forgeloop lifecycle objects.

## Read First

1. The user request, any `grill-requirement` decision summary, and any selected recommendation file
2. Existing design, ADR, gap, audit, or product docs referenced by the user
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
DESIGN.md                 # only when the user asks for a design article or the project needs one
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

1. Clarify only blocking ambiguity in the initiative goal, scope, and non-goals. If the requirement still has multiple blocking decision-tree branches, stop and recommend `grill-requirement` before writing PLAN.md. Otherwise make reasonable assumptions and record them in PLAN.md.
2. Read enough repository context to avoid guessing about architecture, tests, and validation commands.
3. Summarize execution-relevant design decisions and current gaps without copying entire reference docs.
4. Group work into Milestones that each produce an inspectable state.
5. Keep each Milestone to 3-5 work items.
6. Define concrete acceptance criteria for each Milestone.
7. Define validation commands or manual checks for each Milestone.
8. Add structured visual / UX checks for UI changes, including preview target, viewports, required states, and screenshot evidence.
9. Add reviewer focus for product, test, and architecture perspectives.
10. For a new initiative, create a minimal `LEDGER.md` skeleton using `references/ledger-template.md`, with all Milestones initially `TODO`.
11. For an existing active initiative, preserve existing `LEDGER.md` execution facts and only append or adjust future Milestones unless the user explicitly requests a full rewrite.

## Quality Bar

A valid PLAN:

- can be executed by a Scheduler without re-planning
- tells Coder what to read, what to change, what not to change, and how to validate
- tells Reviewer how to decide `PASS` vs `REPAIR_REQUIRED`
- keeps Design / Gap / ADR documents as reference inputs, not copied truth sources
- includes a hardening Milestone when a risky capability needs quality consolidation
- avoids vague acceptance like “works well”, “tests sufficient”, or “code clean”
- avoids duplicating active or completed initiatives unless the new plan is explicitly a follow-up or v2
- does not overwrite existing execution facts when updating an active initiative

## Output Shape

Use `references/plan-template.md` as the canonical PLAN shape, `references/ledger-template.md` as the canonical LEDGER shape, and `references/hardening-milestone-template.md` when adding a hardening Milestone.
