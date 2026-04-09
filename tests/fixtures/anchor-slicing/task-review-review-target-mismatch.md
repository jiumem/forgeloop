# Task Review Rolling Doc: Review Target Mismatch

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
summary: Review target mismatch should fail derive.
```

```forgeloop
kind: coder_update
round: 1
author_role: coder
created_at: 2026-03-31T09:05:00Z
next_action: request_reviewer_handoff
summary: Review target mismatch fixture still opens reviewer entry legally.
blocking_reason: null
```

```forgeloop
kind: review_handoff
round: 1
author_role: coder
created_at: 2026-03-31T09:12:00Z
review_target_ref: commits/sample-a1
compare_base_ref: commits/sample-base
summary: First malformed handoff.
evidence_refs:
  - tests/fixtures/anchor-slicing/task-review-review-target-mismatch.md
```

```forgeloop
kind: review_result
review_result_id: mismatch-r1
round: 1
author_role: reviewer
created_at: 2026-03-31T09:20:00Z
review_target_ref: commits/sample-a2
verdict: clean
functional_correctness: pass
validation_adequacy: pass
local_structure_convergence: pass
local_regression_risk: low
open_issues: []
next_action: advance_frontier
findings: []
```
