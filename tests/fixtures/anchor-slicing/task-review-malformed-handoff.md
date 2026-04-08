# Task Review Rolling Doc: ASDO-TX

```forgeloop
kind: review_header
object_type: task
schema_version: 2
initiative_key: anchor-sliced-dispatch-optimization
milestone_key: ASDO-MX
task_key: ASDO-TX
coder_slot: coder
created_at: 2026-03-31T09:00:00Z
```

```forgeloop
kind: review_contract_snapshot
summary: Fixture with a malformed handoff block.
spec_refs:
  - docs/initiatives/active/anchor-sliced-dispatch-optimization/design.md
acceptance_authority_ref: docs/initiatives/active/anchor-sliced-dispatch-optimization/total-task-doc.md#task-ledger/task-definitions/asdo-t5
acceptance_index_ref: docs/initiatives/active/anchor-sliced-dispatch-optimization/total-task-doc.md#acceptance-matrix/task-acceptance-index/asdo-t5
evidence_entrypoint_ref: docs/initiatives/active/anchor-sliced-dispatch-optimization/total-task-doc.md#acceptance-matrix/evidence-entrypoints
```

```forgeloop
kind: review_handoff
round: 1
author_role: coder
created_at: 2026-03-31T09:10:00Z
review_target_ref: commits/sample-a1
summary: Malformed handoff omits compare_base_ref.
evidence_refs:
  - tests/fixtures/anchor-slicing/task-review-malformed-handoff.md
```
