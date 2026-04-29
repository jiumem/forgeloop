# DESIGN｜<Initiative Title>

Status: Draft / Active / Superseded
Initiative: `<code>-<slug>`
Created: <yyyy-mm-dd>
Updated: <yyyy-mm-dd>
Source Request: <short description or link>

---

## 1. Candidate Snapshot

Describe the candidate Initiative in plain language.

Include:

- original request or candidate source
- why this may deserve a formal Initiative
- current intended outcome
- known constraints before planning

Do not define Milestones, Tasks, PR sequence, or execution order.

---

## 2. Coarse Context Scan

Summarize only the coarse context used to build the Value Question Directory Tree.

Include relevant project artifacts read during the coarse scan:

| Source | What it contributed |
|---|---|
| `<path>` | <fact or framing contribution> |

Keep this section short. Deep facts belong in Focused Context Findings.

---

## 3. Value Question Directory Tree

Paste the directory-tree artifact produced before focused investigation.

Rules:

- directory-tree form only
- no flat Q-list as the main structure
- no final decisions inside the tree
- no evidence bullets inside the tree
- no Milestone / Task / PR decomposition

```text
0. <这个候选 Initiative 是否值得进入 DESIGN.md？>
├── ...
└── ...
```

---

## 4. Focused Context Findings

Summarize only source-backed findings that affect Decision Records.

Each finding should be concise and evidence-oriented.

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

**PLAN Impact**  
- Scope implication: <what later PLAN.md should preserve>
- Non-Goals implication: <what later PLAN.md should exclude>
- Acceptance input: <what later PLAN.md may turn into acceptance criteria>
- Evidence implication: <what later PLAN.md may require as evidence>

Do not define Milestones, Tasks, PR sequence, execution order, or `LEDGER.md` state here.

**Residual Risk**  
<Accepted risk, unresolved uncertainty, or condition that may require revision.>

---

## 6. Remaining Blockers

List blockers that prevent activation or planning.

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

---

## 7. Activation / Disposition

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
