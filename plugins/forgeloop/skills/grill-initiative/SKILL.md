---
name: grill-initiative
description: Use when the user asks to grill, stress-test, pressure-test, design, clarify, or validate a candidate Initiative before planning; produces DESIGN.md decisions and never writes PLAN.md or LEDGER.md.
---

# grill-initiative

## Purpose

Stress-test a candidate Initiative before planning. Produce a source-backed `DESIGN.md` that records the value-question tree, focused findings, and decision records needed by `plan-initiative`.

This skill does not write code, does not create `PLAN.md`, does not create `LEDGER.md`, and does not run the Initiative.

## Trigger

Use this skill when the user asks to grill, stress-test, pressure-test, design, clarify, or validate a candidate Initiative before planning, especially when the request is vague, high-risk, architectural, data/state-heavy, or likely to affect long-lived project structure.

Examples:

- “Grill initiative 008 before planning.”
- “Pressure-test this migration idea before writing PLAN.md.”
- “Turn this candidate into a DESIGN.md.”
- “Check whether this should become an Initiative.”

## Read First

Read only enough context to understand the candidate Initiative before building the first visible artifact.

Prefer, when present:

- repository README / AGENTS / CLAUDE instructions
- existing `docs/initiatives/**` records
- recommendation notes
- domain or context docs
- obvious source entrypoints related to the candidate
- existing tests or schema files only when they are needed for the coarse scan

Do not perform deep source investigation before emitting the Value Question Directory Tree.

## Write Target

The durable output is:

```text
docs/initiatives/active/<code>-<slug>/DESIGN.md
```

Use an existing Initiative path if the user provides one.

If no active Initiative path exists, do not guess a conflicting code. Inspect existing `docs/initiatives/active/`, `docs/initiatives/completed/`, and related Initiative directories before proposing a code and slug.

If `DESIGN.md` already exists, do not silently overwrite it. Revise it only when the user explicitly asks for a revision. Preserve prior decision records unless they are explicitly superseded.

Do not write `PLAN.md` or `LEDGER.md`.

## Core Workflow

Run as a staged initiative interrogation. Do not ask intermediate user questions.

Emit staged visible artifacts as progress outputs, then continue automatically unless the user interrupts. Do not expose private chain-of-thought. Show only reviewable artifacts, evidence paths, and stage conclusions.

Do not do all investigation silently and then output every artifact at the end. The Value Question Directory Tree must be shown before focused investigation starts.

### 1. Coarse Context Scan

Read only enough repo context to understand the candidate Initiative and its likely risk surface.

Output a concise scan summary only if it helps frame the next artifact.

Do not perform deep source investigation yet.

### 2. Output Value Question Directory Tree

This is the first required visible artifact.

Use `references/value-question-directory-tree-template.md`.

The tree must:

- map the question space in compact directory-tree form
- start from whether the candidate deserves `DESIGN.md`
- use parent nodes as decisive uncertainties, not document-section labels
- use child nodes as design-risk questions, not implementation tasks
- activate only the risk lenses that matter to the candidate
- avoid flat `Q001 / Q002 / Q003` checklists as the main structure
- avoid final decisions, evidence bullets, recommendations, or field-heavy cards inside the tree

The tree is a map of high-value uncertainties. It is not the decision result.

### 3. Focused Context Investigation

Investigate the high-value nodes from the tree.

Read source files, docs, tests, schemas, examples, prior Initiative records, and other project artifacts only when they can affect a decision record.

Do not use subagents. The main agent owns all investigation, pruning, and synthesis.

### 4. Output Focused Context Findings

Summarize only source-backed findings that affect decisions.

Each finding should include:

- observed fact
- source path or command result when available
- confidence or gap when relevant
- which decision it affects

Do not summarize files that do not affect a Decision Record.

### 5. Output Decision Records

Do not output decisions as a tree.

Each decision must include:

- Decision
- Evidence
- Decision Criteria
- Rejected Alternatives
- PLAN Impact
- Residual Risk

`PLAN Impact` may mention scope, non-goals, acceptance inputs, evidence implications, or planning constraints.

`PLAN Impact` must not define Milestones, Tasks, PR sequence, execution order, or `LEDGER.md` state.

### 6. Output Remaining Blockers

List blockers that prevent activation or planning.

If none, say `none` explicitly.

### 7. Ask Final Activation Question

If no activation blockers remain, ask whether the user confirms activating the Initiative and writing:

```text
docs/initiatives/active/<code>-<slug>/DESIGN.md
```

This is the only user-facing question in the default workflow.

If activation blockers remain, do not ask for activation. Ask whether to keep the result as a draft, revise the candidate, or defer.

If the user already explicitly requested writing `DESIGN.md` and the target path is unambiguous, write it without asking again.

### 8. Write DESIGN.md

When confirmed or explicitly requested, write `DESIGN.md` using `references/DESIGN-template.md`.

The file must include:

- Candidate Snapshot
- Coarse Context Scan
- Value Question Directory Tree
- Focused Context Findings
- Decision Records
- Remaining Blockers
- Activation / Disposition

Do not write `PLAN.md` or `LEDGER.md`.

## Quality Bar

A successful run must:

- avoid checklist-style interrogation
- surface the highest-leverage design uncertainties
- separate question-space mapping from final decisions
- support each decision with evidence and explicit criteria
- reject alternatives explicitly rather than silently pruning them
- preserve planning boundary: no Milestone, Task, PR, command-sequence, or ledger planning
- make the output durable enough for `plan-initiative` to consume

## Output Shape

During the conversation, output staged artifacts in this order:

1. Value Question Directory Tree
2. Focused Context Findings
3. Decision Records
4. Remaining Blockers
5. Final Activation Question or Disposition

When writing the file, use the canonical shape in `references/DESIGN-template.md`.
