# Design Detail Lens Blocks

Use this reference only after the Value Question Directory Tree, Leaf Resolution Matrix, and Decision Records have activated one or more design lenses.

Rules:

- Copy only activated lens blocks into `DESIGN.md`.
- Delete inactive blocks.
- Do not leave empty headings, placeholder fields, or unused bullets.
- Do not mechanically fill every lens.
- Do not invent a lens block just because it exists in this reference.
- If an activated lens does not need a detail block, close it explicitly in the Leaf Resolution Matrix as a blocker, follow-up, residual risk, rejection, deferral, merge, or out-of-scope closure.
- Do not define Milestones, Tasks, PR sequence, execution order, exact test file names, function-level implementation steps, or `LEDGER.md` state.

---

## Interface Contract

Use only when the Initiative adds or changes an API, CLI, UI route, internal service boundary, adapter, repository, SDK call, module interface, skill interface, or document handoff interface.

- Formal entrypoints:
- Input semantics:
- Output semantics:
- Error semantics:
- Idempotency / repeat behavior:
- Forbidden shortcuts:

---

## Data Model

Use only when the Initiative touches schema, database tables, entity identity, derived fields, caches, parquet / files, migrations, indexing, snapshots, auditability, or generated document fields.

- Core entities:
- Identity / uniqueness:
- Source fields vs derived fields:
- Persistence / auditability:
- Truth-source risks:

---

## State Lifecycle

Use only when the Initiative touches tasks, cases, workflow states, status transitions, retries, idempotency, recovery, partial success, concurrency, Draft/Sealed status, or document lifecycle.

- Allowed states:
- Allowed transitions:
- Failure states:
- Retry / repeat / idempotency:
- Recovery semantics:

---

## Test Feedback Strategy

Use only when acceptance depends on tests, fixtures, mocks, E2E flows, real data, CI, regression, reviewer checks, or Agent-runnable feedback loops.

- Blocking behavior invariants:
- Real-path requirements:
- Allowed mocks / fixtures:
- Forbidden mock acceptance:
- Failure-path proof:

---

## Migration / Compatibility

Use only when old and new paths may coexist.

- Old path:
- New path:
- Compatibility window:
- Deletion / retirement condition:
- Fallback policy:

---

## Runtime / Operations

Use only when the Initiative touches production-like execution, scheduling, scale, performance, data freshness, observability, failure recovery, or repeated Agent operation.

- Runtime scale assumption:
- Scheduling / freshness assumption:
- Failure recovery:
- Observability:
- Out-of-scope runtime hardening:

---

## Security / Policy

Use only when the Initiative touches permissions, auth, secrets, privacy, regulated data, destructive operations, external calls, audit logs, or human confirmation.

- Access boundary:
- Sensitive data / secret boundary:
- Audit requirement:
- Human confirmation requirement:
