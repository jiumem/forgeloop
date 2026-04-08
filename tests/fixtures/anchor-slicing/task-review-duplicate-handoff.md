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
summary: Fixture with duplicate review handoffs in one round.
spec_refs:
  - docs/initiatives/active/anchor-sliced-dispatch-optimization/design.md
acceptance:
  - sample fixture only
```

```forgeloop
kind: review_handoff
round: 1
author_role: coder
created_at: 2026-03-31T09:10:00Z
review_target_ref: commits/sample-a1
compare_base_ref: commits/sample-base
summary: First current-round handoff.
evidence_refs:
  - tests/fixtures/anchor-slicing/task-review-duplicate-handoff.md
```

```forgeloop
kind: review_handoff
round: 1
author_role: coder
created_at: 2026-03-31T09:18:00Z
review_target_ref: commits/sample-a2
compare_base_ref: commits/sample-base
summary: Second same-round handoff should fail derive.
evidence_refs:
  - tests/fixtures/anchor-slicing/task-review-duplicate-handoff.md
```
