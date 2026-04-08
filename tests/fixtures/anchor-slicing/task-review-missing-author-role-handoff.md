# Task Review Rolling Doc: Missing Author Role On Review Handoff

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
summary: Missing author_role on review_handoff should fail derive.
```

```forgeloop
kind: review_handoff
round: 1
created_at: 2026-03-31T09:05:00Z
review_target_ref: commits/sample-a1
compare_base_ref: commits/sample-base
summary: This malformed block omits author_role.
```
