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
summary: Fixture with a handoff block missing round.
spec_refs:
  - docs/initiatives/active/anchor-sliced-dispatch-optimization/design.md
acceptance:
  - sample fixture only
```

```forgeloop
kind: review_handoff
author_role: coder
created_at: 2026-03-31T09:12:00Z
review_target_ref: commits/sample-a1
compare_base_ref: commits/sample-base
summary: Missing round on handoff should fail derive.
evidence_refs:
  - tests/fixtures/anchor-slicing/task-review-missing-round-handoff.md
```
