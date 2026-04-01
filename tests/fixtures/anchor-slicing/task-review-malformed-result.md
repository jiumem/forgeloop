# Task Review Rolling Doc: ASDO-TX

```forgeloop
kind: task_review_header
initiative_key: anchor-sliced-dispatch-optimization
milestone_key: ASDO-MX
task_key: ASDO-TX
coder_slot: coder
created_at: 2026-03-31T09:00:00Z
```

```forgeloop
kind: task_contract_snapshot
summary: Fixture with a malformed review result block.
spec_refs:
  - docs/initiatives/active/anchor-sliced-dispatch-optimization/design.md
acceptance:
  - sample fixture only
```

```forgeloop
kind: g1_result
round: 1
author_role: coder
created_at: 2026-03-31T09:10:00Z
verdict: pass
next_action: request_reviewer_handoff
```

```forgeloop
kind: anchor_ref
round: 1
author_role: coder
created_at: 2026-03-31T09:12:00Z
handoff_id: sample-r1-a1
review_target_ref: commits/sample-a1
commit: anchor(sample): first state
sha: abc1234
```

```forgeloop
kind: r1_result
round: 1
author_role: reviewer
created_at: 2026-03-31T09:20:00Z
verdict: clean
next_action: task_done
```
