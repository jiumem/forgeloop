# Task Review Rolling Doc: Invalid Round

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
summary: Non-numeric round should fail derive.
```

```forgeloop
kind: coder_update
round: 1
author_role: coder
created_at: 2026-03-31T09:04:00Z
next_action: request_reviewer_handoff
summary: Non-numeric round should fail derive.
blocking_reason: null
```

```forgeloop
kind: review_handoff
round: one
author_role: coder
created_at: 2026-03-31T09:05:00Z
review_target_ref: commits/sample-a1
compare_base_ref: commits/sample-base
summary: This malformed block uses a non-numeric round.
```
