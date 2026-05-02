---
name: grill-initiative
description: Use when the user asks to grill, stress-test, pressure-test, design, clarify, or validate a candidate Initiative before planning; creates or updates a document-first Draft DESIGN.md, closes every Value Question leaf, and seals only on explicit user confirmation.
---

# grill-initiative

## Purpose

Stress-test a candidate Initiative before planning. The durable output is a source-backed `DESIGN.md` that records the value-question tree, focused findings, leaf resolutions, decision records, selected design, implementation-relevant design guidance, blockers, follow-ups, and residual risks needed by `plan-initiative`.

This skill does not write code, does not create `PLAN.md`, does not create `LEDGER.md`, and does not run the Initiative.

The `DESIGN.md` file is the primary working artifact. The conversation is only a control surface for concise progress summaries, sealing questions, blockers, and user裁决.

---

## Trigger

Use this skill when the user asks to grill, stress-test, pressure-test, design, clarify, or validate a candidate Initiative before planning, especially when the request is vague, high-risk, architectural, data/state-heavy, or likely to affect long-lived project structure.

Examples:

- “Grill initiative 008 before planning.”
- “Pressure-test this migration idea before writing PLAN.md.”
- “Turn this candidate into a DESIGN.md.”
- “Check whether this should become an Initiative.”
- “先把这个专项拷打一遍，不要急着写 PLAN。”

---

## Language Rule

Write `DESIGN.md` and user-facing summaries in the primary language of the user's request.

Preserve file paths, status tokens, IDs, commands, code symbols, object names, and API names as written.

---

## Read First

Read only enough context to understand the candidate Initiative before building the first Value Question Directory Tree.

Prefer, when present:

- repository README / AGENTS / CLAUDE / Codex instructions
- existing `docs/initiatives/**` records
- recommendation notes or handoff notes
- domain or context docs
- obvious source entrypoints related to the candidate
- existing tests, schemas, fixtures, or examples only when they are needed for the coarse scan

Before writing or revising the Value Question Directory Tree, you MUST read:

```text
references/value-question-directory-tree-template.md
```

Before writing or revising `DESIGN.md`, you MUST read:

```text
references/DESIGN-template.md
```

Before writing or revising `Design Details`, you MUST read:

```text
references/design-detail-lens-blocks.md
```

Do not infer any required format from memory. If a required template or reference cannot be read, stop and report the blocker.

---

## Write Target

The durable output is:

```text
docs/initiatives/active/<code>-<slug>/DESIGN.md
```

Use an existing Initiative path if the user provides one.

If no active Initiative path exists, do not guess a conflicting code. Inspect existing Initiative-like directories before choosing a code and slug, including when present:

```text
docs/initiatives/active/
docs/initiatives/completed/
docs/initiatives/archived/
docs/initiatives/handoff/
docs/initiatives/recommendations/
```

Recommendation codes are provisional unless already activated.

Do not write `PLAN.md` or `LEDGER.md`.

Do not leave angle-bracket placeholders such as `<...>` in final written files.

---

## State Model

`DESIGN.md` uses document-source status, not execution lifecycle status.

Allowed statuses:

```text
Draft
Sealed
Superseded
```

### Draft

`Draft` means the design is the current working artifact. It may be updated as investigation and user裁决 continue.

A `Draft` DESIGN.md must not be consumed by `plan-initiative` as a formal planning source.

### Sealed

`Sealed` means the user has explicitly confirmed that the current Draft is the formal design source for downstream planning.

Sealing is not a rewrite. When the user confirms sealing, only update:

- `Status: Draft` -> `Status: Sealed`
- `Updated` / sealing metadata when present
- final disposition wording when needed

Do not re-investigate, re-synthesize, materially rewrite, renumber IDs, reorder major sections, or invent new decisions during sealing.

### Superseded

`Superseded` means this design is no longer the active design source. Treat it as read-only unless the user explicitly asks to restore or revise it.

### Existing DESIGN.md Handling

If `DESIGN.md` already exists:

| Existing Status | Allowed behavior |
|---|---|
| `Draft` | Continue revising the same draft. Preserve stable IDs. |
| `Sealed` | Do not modify the body unless the user explicitly asks to revise, reopen, or supersede the sealed design. |
| `Superseded` | Treat as read-only unless the user explicitly asks to restore or fork it. |
| Missing / unknown | Ask no routine question; mark the uncertainty in the file and normalize only when safe. |

During Draft revision, do not renumber existing Leaf IDs, Finding IDs, Decision IDs, Blocker IDs, Follow-up IDs, or Residual Risk IDs unless the user explicitly asks for a full rewrite.

---

## Core Workflow

Run as a document-first initiative interrogation.

Do not generate the full design body in chat first and then rewrite it into the file. Create or update `DESIGN.md` directly with `Status: Draft`, and use the conversation only for concise progress summaries, decision batches, blockers, and sealing confirmation.

Do not ask routine intermediate questions. If a missing user decision blocks sealing, record it in `Open Questions` or `Activation Blockers`, then ask one compact decision batch.

Do not use subagents. The main agent owns investigation, pruning, synthesis, document edits, and sealing.

### 1. Resolve Target and Create / Update Draft

Resolve the Initiative code, slug, and target path.

Create or update:

```text
docs/initiatives/active/<code>-<slug>/DESIGN.md
```

Set or preserve:

```text
Status: Draft
```

Use `references/DESIGN-template.md` as the canonical section shape.

The first chat response after file creation or update should be brief:

```text
已更新：docs/initiatives/active/<code>-<slug>/DESIGN.md
当前状态：Draft
本轮正在收敛：<one-line summary>
```

Do not paste the full document body into chat.

### 2. Coarse Context Scan

Read only enough repo context to understand the candidate Initiative and likely risk surface.

Coarse Context Scan should explain why sources matter, not what they prove. Detailed observed facts belong in Focused Context Findings.

Write the scan into `DESIGN.md`.

Do not perform deep source investigation before the first Value Question Directory Tree is written.

### 3. Write Value Question Directory Tree with Leaf IDs

Write the Value Question Directory Tree into `DESIGN.md` using `references/value-question-directory-tree-template.md`.

The tree must:

- start from whether the candidate deserves a formal `DESIGN.md`
- use parent nodes as decisive uncertainties, not document-section labels
- make final parent nodes candidate-specific when possible
- use child nodes as design-risk questions, not implementation tasks
- activate only the risk lenses that matter to the candidate
- avoid flat `Q001 / Q002 / Q003` checklists as the main structure
- avoid final decisions, evidence bullets, recommendations, field-heavy cards, Milestones, Tasks, PR sequences, commands, or exact evidence filenames inside the tree
- assign a stable `Lxxx` Leaf ID to every retained leaf node
- remove all angle-bracket placeholders

A retained leaf is any final question node kept in the tree. Once a leaf is retained, it must never silently disappear. If it later proves invalid, duplicate, low-value, or out of scope, close it explicitly in the Leaf Resolution Matrix.

### 4. Focused Context Investigation

Investigate the retained leaves from the tree.

Read source files, docs, tests, schemas, examples, prior Initiative records, command outputs, and other project artifacts only when they can affect a leaf resolution, decision record, blocker, follow-up, or residual risk.

For absence claims, include the command/search basis or mark confidence lower. Do not write “not found” or “does not exist” as a high-confidence fact without the search basis that supports it.

Write findings into `DESIGN.md` as `Fxxx` records.

Every finding must include `Affects: Lxxx / Dxxx / Bxxx / FUxxx / Rxxx` as applicable.

Do not summarize files that do not affect a leaf resolution or decision.

### 5. Maintain Leaf Resolution Matrix

Maintain the Leaf Resolution Matrix in `DESIGN.md` continuously while drafting.

Every retained Leaf ID must appear exactly once in the matrix.

Allowed leaf resolutions:

```text
Decided
Design Landing
Downstream Constraint
Activation Blocker
Design Follow-up
Residual Risk
Rejected
Deferred
Merged
Out of Scope
```

Rules:

- `Decided` leaves must point to at least one Decision Record.
- `Design Landing` leaves must point to a Selected Design or Design Detail section.
- `Downstream Constraint` leaves must point to a Decision Record or explicit downstream constraint.
- `Activation Blocker` leaves must point to a `Bxxx` blocker.
- `Design Follow-up` leaves must point to a `FUxxx` follow-up.
- `Residual Risk` leaves must point to a `Rxxx` residual risk.
- `Rejected`, `Deferred`, `Merged`, and `Out of Scope` leaves must include a concise rationale and landing.

The matrix is the formal closure mechanism for the Value Question Directory Tree. Coverage by parent node, risk lens, or vague prose is not sufficient.

### 6. Write Decision Records

Write Decision Records into `DESIGN.md` only for decisions that change design shape, truth source, object boundaries, state lifecycle, interface contract, data model, test feedback strategy, migration boundary, runtime assumption, security boundary, scope, non-goals, or disposition.

Do not output decisions as a tree.

Each decision must include:

- `Covers: Lxxx, Lyyy`
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

### 7. Write Scope / Non-Goals and Selected Design

Write explicit Scope / Non-Goals before or inside Selected Design.

Selected Design must include:

- target design summary
- in scope
- non-goals
- core objects
- formal flow
- boundary rules
- invariants
- source anchors

Source anchors may name paths and their current design relevance. They may include contract surfaces, required validation surfaces, and source locations that downstream implementers/reviewers must inspect.

Source anchors must not prescribe Milestone order, Task sequence, PR queue, or function-level implementation steps.

Selected Design is the design source of truth for downstream planning. It is not an implementation work order.

### 8. Write Design Details

Before writing this section, read `references/design-detail-lens-blocks.md` in this turn.

Include only sections activated by the Value Question Directory Tree, Leaf Resolution Matrix, and Decision Records.

Use only the relevant lens blocks from `references/design-detail-lens-blocks.md`:

- Interface Contract
- Data Model
- State Lifecycle
- Test Feedback Strategy
- Migration / Compatibility
- Runtime / Operations
- Security / Policy

Each activated Risk Lens must either produce a corresponding Design Detail section or land explicitly in the Leaf Resolution Matrix as a blocker, follow-up, residual risk, rejection, deferral, merge, or out-of-scope closure.

Do not mechanically fill every section. Delete inactive lens blocks instead of leaving empty headings or placeholder fields.

Do not define Milestones, Tasks, PR sequence, execution order, exact test file names, function-level implementation steps, or `LEDGER.md` state.

### 9. Write Blockers, Follow-ups, Residual Risks, and Open Questions

Split unresolved items into:

- Activation Blockers: blockers that prevent sealing or downstream planning.
- Design Follow-ups: non-blocking design constraints or open points that downstream planning must preserve or resolve.
- Residual Risks: accepted uncertainties or risks that do not block sealing.
- Open Questions: user or source questions still under discussion.

If none, write `none` explicitly.

Activation Blockers prevent sealing unless the user explicitly revises the design to resolve or reclassify them.

### 10. Validate Draft Before Asking to Seal

Before asking the user to seal, verify inside the document:

- `Status` is `Draft`
- every retained leaf has exactly one Leaf Resolution Matrix row
- every `Decided` leaf points to a Decision Record
- every Decision Record has `Covers: Lxxx`
- every Finding has `Affects: ...`
- accepted decisions have Selected Design or Design Detail landing
- Scope and Non-Goals are explicit
- no angle-bracket placeholders remain
- no Milestones, Tasks, PR sequence, execution order, exact test file names, function-level implementation steps, or `LEDGER.md` states were introduced
- Activation Blockers are either `none` or explicitly listed

If blockers remain, do not ask for sealing. Ask whether to revise, keep Draft, split, defer, or reject.

If no activation blockers remain, ask one compact sealing question:

```text
当前 Draft DESIGN.md 已可封板。是否确认将 Status 从 Draft 改为 Sealed，作为 plan-initiative 的正式设计法源？
```

### 11. Seal on Explicit User Confirmation

When the user confirms sealing, update only the status and sealing metadata:

```text
Status: Draft
```

becomes:

```text
Status: Sealed
```

Do not rewrite the body.

After sealing, respond only with:

```text
已封板：docs/initiatives/active/<code>-<slug>/DESIGN.md
Status: Sealed
Next: 可使用 plan-initiative 生成 PLAN.md / LEDGER.md。
```

---

## Chat Output Shape

Default chat output must be concise and operational.

Use this shape after each substantial update:

```text
已更新：docs/initiatives/active/<code>-<slug>/DESIGN.md
当前状态：Draft
本轮增量：
- <one concrete increment>
- <one concrete increment>
- <one concrete increment>

叶节点关闭：<closed>/<total>
待裁决：<none or compact decision batch>
```

Do not paste the full Value Question Directory Tree, full Decision Records, full Selected Design, or full `DESIGN.md` unless the user explicitly asks to view them in chat.

---

## Quality Bar

A successful run must:

- keep `DESIGN.md` as the only design正文 working artifact
- keep chat as control surface, not duplicate正文 output
- create or update `DESIGN.md` with `Status: Draft` before sealing
- never mark `Status: Sealed` without explicit user confirmation
- never rewrite the body during sealing
- avoid checklist-style interrogation
- surface the highest-leverage design uncertainties
- give every retained Value Question leaf a stable `Lxxx` ID
- close every retained leaf exactly once in the Leaf Resolution Matrix
- separate question-space mapping from final decisions
- support each decision with evidence and explicit criteria
- reject alternatives explicitly rather than silently pruning them
- ensure every accepted decision produces enough Selected Design or Design Detail for `plan-initiative` to derive a plan without inventing design
- include Scope and Non-Goals
- describe the chosen system shape through core objects, formal flow, boundary rules, invariants, and source anchors when relevant
- include only design-detail sections activated by the candidate's risk lenses and decisions
- preserve truth-source, state, interface, migration, test-feedback, runtime, and policy boundaries when relevant
- record blockers, follow-ups, residual risks, and open questions separately
- never write `PLAN.md`, `LEDGER.md`, Milestones, Tasks, PR sequence, execution order, or run state
- never write Design Details from memory; read `references/design-detail-lens-blocks.md` before using lens blocks

---

## Hard Stops

Stop and report a blocker if:

- the candidate cannot be mapped to a safe target path
- required templates cannot be read
- `Design Details` are needed but `references/design-detail-lens-blocks.md` cannot be read
- the user asks to seal but activation blockers remain unresolved
- the user asks to plan from a `Draft` DESIGN.md
- the user asks to modify a `Sealed` DESIGN.md without explicitly choosing revise/reopen/supersede semantics
- source facts conflict and the conflict changes a decision, but the conflict cannot be resolved or safely classified as residual risk
