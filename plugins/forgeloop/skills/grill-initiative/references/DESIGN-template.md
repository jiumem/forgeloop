# DESIGN｜<Initiative Title>

Status: Draft / Sealed / Superseded
Initiative: `<code>-<slug>`
Created: <yyyy-mm-dd>
Updated: <yyyy-mm-dd>
Source Request: <short description or link>
Sealed At: <yyyy-mm-dd or none>

Status rules:

- `Draft`: working design artifact; not a formal planning source.
- `Sealed`: user-confirmed design source for `plan-initiative`.
- `Superseded`: retired design source; read-only unless explicitly restored.

Do not mark `Sealed` before explicit user confirmation. Sealing may only update status and sealing metadata; it must not rewrite, re-synthesize, renumber, or materially reorganize the document body.

---

## 1. Candidate Snapshot

Describe the candidate Initiative in plain language.

Include:

- original request or candidate source
- proposed code / slug
- why this may deserve a formal Initiative
- current intended outcome
- known constraints before planning

Do not define Milestones, Tasks, PR sequence, execution order, or `LEDGER.md` state.

---

## 2. Coarse Context Scan

Summarize only the coarse context used to build the Value Question Directory Tree.

Coarse scan explains relevance only. Detailed observed facts belong in Focused Context Findings.

| Source | Why it matters |
|---|---|
| `<path>` | <why this source is relevant to the candidate or risk surface> |

Keep this section short. Do not turn it into lightweight findings.

---

## 3. Value Question Directory Tree

Paste the directory-tree artifact produced before focused investigation.

Rules:

- directory-tree form only
- no flat Q-list as the main structure
- no final decisions inside the tree
- no evidence bullets inside the tree
- no Milestone / Task / PR decomposition
- no command lists or exact evidence filenames
- no angle-bracket placeholders from templates
- parent nodes should be candidate-specific decisive uncertainties when possible
- every retained leaf node must have a stable `Lxxx` ID

```text
0. <candidate-specific viability question>
├── 1. <candidate-specific decisive uncertainty>
│   ├── L001｜<source-checkable design uncertainty?>
│   └── L002｜<source-checkable design uncertainty?>
└── 2. <candidate-specific decisive uncertainty>
    └── L003｜<source-checkable design uncertainty?>
```

A retained leaf is any final question node kept in the tree. Retained leaves must never silently disappear. If a leaf later proves invalid, duplicate, low-value, or out of scope, close it explicitly in the Leaf Resolution Matrix.

---

## 4. Focused Context Findings

Summarize only source-backed findings that affect leaf resolution, Decision Records, blockers, follow-ups, residual risks, or selected design.

For absence claims, include the command/search basis or mark confidence lower. Do not write “not found” or “does not exist” as a high-confidence fact without the search basis that supports it.

```text
F001｜<Finding Title>
Fact: <observed fact>
Source: <path, command, artifact, or unavailable>
Affects: <L001 / D001 / B001 / FU001 / R001>
Confidence / Gap: <high / medium / low / missing source / conflict>
```

Do not summarize files that do not affect a leaf resolution or decision.

---

## 5. Leaf Resolution Matrix

Every retained Leaf ID from the Value Question Directory Tree must appear exactly once in this table.

Allowed resolutions:

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

| Leaf ID | Leaf Question | Resolution | Landing | Rationale |
|---|---|---|---|---|
| L001 | <question text> | Decided | D001 | <why this is resolved by the decision> |
| L002 | <question text> | Design Landing | §9 Activated Design Detail | <why a design section is sufficient> |
| L003 | <question text> | Activation Blocker | B001 | <why this blocks sealing> |

Rules:

- `Decided` leaves must point to at least one Decision Record.
- `Design Landing` leaves must point to a Selected Design or Design Detail section.
- `Downstream Constraint` leaves must point to a Decision Record or explicit downstream constraint.
- `Activation Blocker` leaves must point to a `Bxxx` blocker.
- `Design Follow-up` leaves must point to a `FUxxx` follow-up.
- `Residual Risk` leaves must point to a `Rxxx` residual risk.
- `Rejected`, `Deferred`, `Merged`, and `Out of Scope` leaves must include a concise rationale and landing.

Coverage by parent node, risk lens, or vague prose is not sufficient.

---

## 6. Decision Records

Each decision must be evidence-backed, criterion-backed, and linked to the leaf nodes it resolves.

Do not output final decisions as a tree.

Every accepted Decision Record must produce enough Selected Design or Design Detail for `plan-initiative` to derive a `PLAN.md` without inventing design.

### D001｜<Decision Title>

Covers: L001, L004

**Decision**  
<The final design decision.>

**Evidence**  
- `F001` / `<path>`: <source-backed evidence>
- `F002` / `<path>`: <source-backed evidence>

**Decision Criteria**
- <criterion used to judge alternatives>
- <criterion used to judge alternatives>

**Rejected Alternatives**
- <alternative>: Rejected because <reason>.
- <alternative>: Rejected because <reason>.

**Design Impact**
<How this decision changes objects, interfaces, state, data, test strategy, boundaries, or truth sources.>

**Downstream Constraint**
<What later `plan-initiative` must preserve or validate. Do not define Milestones, Tasks, PR sequence, execution order, or `LEDGER.md` state here.>

**Residual Risk**
<Accepted risk, unresolved uncertainty, or condition that may require revision. Use `none` if no residual risk remains.>

---

## 7. Scope / Non-Goals

This section defines the Initiative boundary that downstream planning must preserve.

### 7.1 In Scope

- <what this Initiative explicitly covers>
- <what this Initiative explicitly covers>

### 7.2 Non-Goals

- <adjacent concern that must not be planned in this Initiative>
- <adjacent concern that must not be planned in this Initiative>

### 7.3 Boundary Rationale

Explain why the boundary is correct, especially when adjacent work is tempting but would change the Initiative type.

---

## 8. Selected Design

Selected Design describes the chosen system shape. It is the design source of truth for downstream planning, not an implementation work order.

Do not define Milestones, Tasks, PR sequence, execution order, exact test file names, function-level implementation steps, or `LEDGER.md` state.

### 8.1 Target Design Summary

<Use 3-6 concise paragraphs to describe the selected design and why this shape follows from the decisions.>

### 8.2 Core Objects

| Object | Role | Truth Source | Lifecycle / Notes |
|---|---|---|---|
| `<object>` | <what it represents> | <canonical source> | <creation, update, completion, or retirement semantics> |

### 8.3 Formal Flow

```text
<Trigger / Input>
  -> <Domain / Service>
  -> <Persistence / State>
  -> <API / UI / Export>
```

### 8.4 Boundary Rules

- <formal path, allowed boundary, or forbidden shortcut>
- <mock / fixture / fallback boundary, when relevant>

### 8.5 Invariants

- <behavior, truth-source, data, state, or interface invariant that must always hold>
- <behavior, truth-source, data, state, or interface invariant that must always hold>

### 8.6 Source Anchors

Source anchors help downstream implementers and reviewers find existing code surfaces without turning this document into a plan.

They may name contract surfaces, required validation surfaces, and relevant source locations. They must not prescribe Milestone order, Task sequence, PR queue, or function-level implementation steps.

- `<path>`: <current role / relevant existing behavior>
- `<path>`: <current mock / fallback / truth-source gap>
- `<path>`: <contract, schema, API, service, UI, or validation anchor>

---

## 9. Design Details

Include only activated design lenses. Delete inactive blocks.

Include a section when the Value Question Directory Tree, Leaf Resolution Matrix, and Decision Records activated that design surface. Omit sections that do not apply.

Each activated Risk Lens must either produce a corresponding Design Detail section or land explicitly in the Leaf Resolution Matrix as a blocker, follow-up, residual risk, rejection, deferral, merge, or out-of-scope closure.

Do not define Milestones, Tasks, PR sequence, execution order, exact test file names, function-level implementation steps, or `LEDGER.md` state.

Before writing activated lens blocks, read:

```text
references/design-detail-lens-blocks.md
```

<!-- Include only if activated by the Value Question Directory Tree, Leaf Resolution Matrix, and Decision Records. Delete inactive blocks. Do not leave empty headings or placeholder fields. -->

---

## 10. Remaining Blockers, Follow-ups, Risks, and Open Questions

### 10.1 Activation Blockers

List blockers that prevent sealing this `DESIGN.md` or prevent downstream planning.

If none, write:

```text
none
```

For each blocker, include:

```text
B001｜<Blocker Title>
Leaf: L001
Reason: <why this blocks sealing or planning>
Needed: <source, decision, or user constraint needed to unblock>
```

### 10.2 Design Follow-ups

List non-blocking design constraints or open points that do not prevent sealing, but that later `plan-initiative` must explicitly preserve or resolve.

If none, write:

```text
none
```

For each follow-up, include:

```text
FU001｜<Follow-up Title>
Leaf: L001
Constraint: <what downstream planning must preserve or resolve>
Landing: <Decision Record, Design Detail, Downstream Constraint, or Residual Risk it relates to>
```

### 10.3 Residual Risks

List accepted uncertainties or risks that do not block sealing.

If none, write:

```text
none
```

For each residual risk, include:

```text
R001｜<Risk Title>
Leaf: L001
Risk: <accepted uncertainty or risk>
Reason accepted: <why this does not block sealing>
Required monitoring / future trigger: <what would reopen or escalate it>
```

### 10.4 Open Questions

List unresolved questions still under discussion.

If none, write:

```text
none
```

For each open question, include:

```text
OQ001｜<Question Title>
Leaf: L001
Question: <what remains unknown>
Blocking status: <blocks sealing / does not block sealing>
```

---

## 11. Sealing / Disposition

Choose one disposition:

```text
Ready for sealing
Keep as draft
Split required
Defer to research
Reject
Superseded
```

Explain why.

If ready for sealing, include the target path:

```text
docs/initiatives/active/<code>-<slug>/DESIGN.md
```

If not ready, state the next safe action.

If Activation Blockers are not `none`, disposition must not be `Ready for sealing` unless the blocker is reclassified or resolved in the document.

---

## 12. Draft Validation Checklist

Before asking the user to seal, verify:

| Check | Status |
|---|---|
| Status is `Draft` | <pass/fail> |
| Every retained `Lxxx` appears exactly once in Leaf Resolution Matrix | <pass/fail> |
| Every `Decided` leaf points to at least one `Dxxx` | <pass/fail> |
| Every Decision Record has `Covers: Lxxx` | <pass/fail> |
| Every Finding has `Affects: ...` | <pass/fail> |
| Accepted decisions land in Selected Design or Design Details | <pass/fail> |
| Scope and Non-Goals are explicit | <pass/fail> |
| No template placeholders remain | <pass/fail> |
| No Milestones / Tasks / PR sequence / execution order / `LEDGER.md` state appears | <pass/fail> |
| Activation Blockers are resolved or explicitly listed | <pass/fail> |
