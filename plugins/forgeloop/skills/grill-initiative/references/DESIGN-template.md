# DESIGN｜<Initiative Title>

Status: Draft / Active / Superseded
Initiative: `<code>-<slug>`
Created: <yyyy-mm-dd>
Updated: <yyyy-mm-dd>
Source Request: <short description or link>

Status must remain `Draft` unless the user explicitly confirmed activation or explicitly requested writing the `DESIGN.md` to the active target path. Do not mark `Active` before explicit activation confirmation.

---

## 1. Candidate Snapshot

Describe the candidate Initiative in plain language.

Include:

- original request or candidate source
- proposed code / slug
- why this may deserve a formal Initiative
- current intended outcome
- known constraints before planning

Do not define Milestones, Tasks, PR sequence, or execution order.

---

## 2. Coarse Context Scan

Summarize only the coarse context used to build the Value Question Directory Tree.

Coarse scan explains relevance only. Detailed observed facts belong in Focused Context Findings.

Include relevant project artifacts read during the coarse scan:

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
- no angle-bracket placeholders from templates
- parent nodes should be candidate-specific decisive uncertainties when possible

```text
0. <candidate-specific viability question>
├── ...
└── ...
```

---

## 4. Focused Context Findings

Summarize only source-backed findings that affect Decision Records.

Each finding should be concise and evidence-oriented.

For absence claims, include the command/search basis or mark confidence lower. Do not write "not found" or "does not exist" as a high-confidence fact without the search basis that supports it.

```text
F001｜<Finding Title>
Fact: <observed fact>
Source: <path, command, artifact, or unavailable>
Affects: <D001 / D002 / ...>
Confidence / Gap: <high / medium / low / missing source / conflict>
```

Do not summarize files that do not affect a Decision Record.

---

## 5. Decision Records

Each decision must be evidence-backed and criterion-backed.

Do not output final decisions as a tree.

Every accepted Decision Record must produce enough Selected Design or Design Detail for `plan-initiative` to derive a `PLAN.md` without inventing design.

### D001｜<Decision Title>

**Decision**  
<The final design decision.>

**Evidence**  
- `<path or finding id>`: <source-backed evidence>
- `<path or finding id>`: <source-backed evidence>

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
<Accepted risk, unresolved uncertainty, or condition that may require revision.>

---

## 6. Selected Design

Selected Design describes the chosen system shape. It is the design source of truth for downstream planning, not an implementation work order.

Do not define Milestones, Tasks, PR sequence, execution order, exact test file names, or function-level implementation steps.

### 6.1 Target Design Summary

<Use 3-6 concise paragraphs to describe the selected design and why this shape follows from the decisions.>

### 6.2 Core Objects

| Object | Role | Truth Source | Lifecycle / Notes |
|---|---|---|---|
| `<object>` | <what it represents> | <canonical source> | <creation, update, completion, or retirement semantics> |

### 6.3 Formal Flow

```text
<Trigger / Input>
  -> <Domain / Service>
  -> <Persistence / State>
  -> <API / UI / Export>
```

### 6.4 Boundary Rules

- <formal path, allowed boundary, or forbidden shortcut>
- <mock / fixture / fallback boundary, when relevant>

### 6.5 Invariants

- <behavior, truth-source, data, state, or interface invariant that must always hold>
- <behavior, truth-source, data, state, or interface invariant that must always hold>

### 6.6 Source Anchors

Source anchors help downstream implementers and reviewers find the existing code surfaces without turning this document into a plan.

- `<path>`: <current role / relevant existing behavior>
- `<path>`: <current mock / fallback / truth-source gap>
- `<path>`: <contract, schema, API, service, UI, or test anchor>

---

## 7. Design Details

Only include activated sections. Do not mechanically fill every section.

Include a section when the Value Question Directory Tree and Decision Records activated that design surface. Omit sections that do not apply.

Each activated Risk Lens must either produce a corresponding Design Detail section or land explicitly in Coverage Check as a blocker, follow-up, residual risk, rejection, or deferral.

Do not define Milestones, Tasks, PR sequence, execution order, exact test file names, or function-level implementation steps.

### 7.1 Interface Contract

- Formal entrypoints:
- Input semantics:
- Output semantics:
- Error semantics:
- Idempotency / repeat behavior:
- Forbidden shortcuts:

### 7.2 Data Model

- Core entities:
- Identity / uniqueness:
- Source fields vs derived fields:
- Persistence / auditability:
- Truth-source risks:

### 7.3 State Lifecycle

- Allowed states:
- Allowed transitions:
- Failure states:
- Retry / repeat / idempotency:
- Recovery semantics:

### 7.4 Test Feedback Strategy

- Blocking behavior invariants:
- Real-path requirements:
- Allowed mocks / fixtures:
- Forbidden mock acceptance:
- Failure-path proof:

### 7.5 Migration / Compatibility

- Old path:
- New path:
- Compatibility window:
- Deletion / retirement condition:
- Fallback policy:

### 7.6 Runtime / Operations

- Runtime scale assumption:
- Scheduling / freshness assumption:
- Failure recovery:
- Observability:
- Out-of-scope runtime hardening:

### 7.7 Security / Policy

- Access boundary:
- Sensitive data / secret boundary:
- Audit requirement:
- Human confirmation requirement:

---

## 8. Coverage Check

Every high-value leaf in the Value Question Directory Tree must land in one of:

- a Decision Record
- a Selected Design element
- a Design Detail section
- a Downstream Constraint
- an Activation Blocker
- a Design Follow-up
- a Residual Risk
- an explicit rejection or deferral

Use the table to prove that the question tree, decisions, and design do not drift apart.

| Value question / risk lens | Covered by | Landing |
|---|---|---|
| <question or activated lens> | D001 / Selected Design / Design Details / Blocker / Residual Risk | <where the issue lands and why> |

---

## 9. Remaining Blockers

### 9.1 Activation Blockers

List blockers that prevent activation of this `DESIGN.md` or prevent downstream planning.

If none, write:

```text
none
```

For each blocker, include:

```text
B001｜<Blocker Title>
Reason: <why this blocks activation or planning>
Needed: <source, decision, or user constraint needed to unblock>
```

### 9.2 Design Follow-ups

List non-blocking design constraints or open points that do not prevent activation, but that later `plan-initiative` must explicitly preserve or resolve.

If none, write:

```text
none
```

For each follow-up, include:

```text
FU001｜<Follow-up Title>
Constraint: <what downstream planning must preserve or resolve>
Landing: <Decision Record, Design Detail, Downstream Constraint, or Residual Risk it relates to>
```

---

## 10. Activation / Disposition

Choose one disposition:

```text
Ready for activation
Keep as draft
Split required
Defer to research
Reject
Superseded
```

Explain why.

If ready for activation, include the target path:

```text
docs/initiatives/active/<code>-<slug>/DESIGN.md
```

If not ready, state the next safe action.

If the user did not explicitly request writing `DESIGN.md`, leave status as `Draft` and ask the activation question outside the file rather than marking this document `Active`.
