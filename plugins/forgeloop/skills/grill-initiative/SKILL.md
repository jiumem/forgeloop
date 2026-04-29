---
name: grill-initiative
description: Use when the user asks to grill, stress-test, pressure-test, design, clarify, or validate a candidate Initiative before planning; produces decision-first DESIGN.md artifacts and never writes PLAN.md or LEDGER.md.
---

# grill-initiative

## Purpose

Stress-test a candidate Initiative before planning. Produce a source-backed `DESIGN.md` that records the value-question tree, focused findings, decision records, selected design, and design details needed by `plan-initiative`.

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

Before emitting the Value Question Directory Tree, you MUST read
`references/value-question-directory-tree-template.md` in this turn.
Do not infer the format from the file name.
If the template cannot be read, stop and report the blocker.

### 1. Coarse Context Scan

Read only enough repo context to understand the candidate Initiative and its likely risk surface.

Coarse Context Scan should explain why sources matter, not what they prove. Detailed observed facts belong in Focused Context Findings.

Output a concise scan summary only if it helps frame the next artifact.

Do not perform deep source investigation yet.

### 2. Output Value Question Directory Tree

This is the first required visible artifact.

Use `references/value-question-directory-tree-template.md`.

The tree must:

- map the question space in compact directory-tree form
- start from whether the candidate deserves `DESIGN.md`
- use parent nodes as decisive uncertainties, not document-section labels
- use mandatory axes as generation aids, not as default final parent nodes
- make final parent nodes candidate-specific when possible
- use child nodes as design-risk questions, not implementation tasks
- activate only the risk lenses that matter to the candidate
- avoid flat `Q001 / Q002 / Q003` checklists as the main structure
- avoid final decisions, evidence bullets, recommendations, or field-heavy cards inside the tree
- remove all angle-bracket placeholders from final output

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

For absence claims, include the command/search basis or mark confidence lower. Do not write "not found" or "does not exist" as a high-confidence fact without the search basis that supports it.

Do not summarize files that do not affect a Decision Record.

### 5. Output Decision Records

Do not output decisions as a tree.

Each decision must include:

- Decision
- Evidence
- Decision Criteria
- Rejected Alternatives
- Design Impact
- Downstream Constraint
- Residual Risk

`Design Impact` explains how the decision changes objects, interfaces, state, data, test strategy, boundaries, or truth sources.

`Downstream Constraint` explains what later `plan-initiative` must preserve or validate.

Do not define Milestones, Tasks, PR sequence, execution order, exact test file names, function-level implementation steps, or `LEDGER.md` state.

Every accepted Decision Record must produce enough Selected Design or Design Detail for `plan-initiative` to derive a `PLAN.md` without inventing design.

### 6. Output Selected Design

Describe the chosen system shape.

Selected Design must include:

- target design summary
- core objects
- formal flow
- boundary rules
- invariants
- source anchors

Source anchors may name paths and their current design relevance, but must not prescribe execution order or become a work plan.

Selected Design is the design source of truth for downstream planning. It is not an implementation work order.

Do not define Milestones, Tasks, PR sequence, execution order, exact test file names, function-level implementation steps, or `LEDGER.md` state.

### 7. Output Design Details

Include only sections activated by the Value Question Directory Tree and Decision Records.

Use relevant sections from:

- Interface Contract
- Data Model
- State Lifecycle
- Test Feedback Strategy
- Migration / Compatibility
- Runtime / Operations
- Security / Policy

Each activated Risk Lens must either produce a corresponding Design Detail section or land explicitly in Coverage Check as a blocker, follow-up, residual risk, rejection, or deferral.

Do not mechanically fill every section. Omit design surfaces that were not activated by the candidate.

Do not define Milestones, Tasks, PR sequence, execution order, exact test file names, function-level implementation steps, or `LEDGER.md` state.

### 8. Output Coverage Check

Every high-value leaf in the Value Question Directory Tree must land in one of:

- a Decision Record
- a Selected Design element
- a Design Detail section
- a Downstream Constraint
- an Activation Blocker
- a Design Follow-up
- a Residual Risk
- an explicit rejection or deferral

Every accepted Decision Record must have enough design landing for downstream planning without requiring `plan-initiative` to invent design.

### 9. Output Remaining Blockers

Split blockers into:

- Activation Blockers: blockers that prevent activation of this `DESIGN.md` or prevent downstream planning.
- Design Follow-ups: non-blocking design constraints or open points that do not prevent activation, but that later `plan-initiative` must explicitly preserve or resolve.

If none, say `none` explicitly.

### 10. Ask Final Activation Question

If no activation blockers remain, ask whether the user confirms activating the Initiative and writing:

```text
docs/initiatives/active/<code>-<slug>/DESIGN.md
```

This is the only user-facing question in the default workflow.

If activation blockers remain, do not ask for activation. Ask whether to keep the result as a draft, revise the candidate, or defer.

If the user already explicitly requested writing `DESIGN.md` and the target path is unambiguous, write it without asking again.

Do not mark Status as `Active` before explicit activation confirmation. If the user did not explicitly request writing `DESIGN.md`, status must remain `Draft` and the final section must ask the activation question.

### 11. Write DESIGN.md

When confirmed or explicitly requested, write `DESIGN.md` using `references/DESIGN-template.md`.

The file must include:

- Candidate Snapshot
- Coarse Context Scan
- Value Question Directory Tree
- Focused Context Findings
- Decision Records
- Selected Design
- Design Details
- Coverage Check
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
- ensure every high-value tree leaf lands in a decision, selected design, design detail, downstream constraint, blocker, follow-up, residual risk, rejection, or deferral
- ensure accepted decisions produce enough selected design or design detail for `plan-initiative` to derive a plan without inventing design
- describe the chosen system shape through core objects, formal flow, boundary rules, invariants, and source anchors when relevant
- include only design-detail sections activated by the candidate's risk lenses and decisions
- keep Coarse Context Scan as relevance framing, not lightweight findings
- support absence claims with search/command basis or lower confidence
- keep status `Draft` unless activation or writing was explicitly confirmed
- preserve planning boundary: no Milestone, Task, PR, command-sequence, or ledger planning
- make the output durable enough for `plan-initiative` to consume

## Output Shape

During the conversation, output staged artifacts in this order:

1. Value Question Directory Tree
2. Focused Context Findings
3. Decision Records
4. Selected Design
5. Design Details
6. Coverage Check
7. Remaining Blockers
8. Final Activation Question or Disposition

When writing the file, use the canonical shape in `references/DESIGN-template.md`.
