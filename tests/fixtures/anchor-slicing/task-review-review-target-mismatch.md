# Task Review Rolling Doc: Review Target Mismatch

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
summary: Review target mismatch should fail derive.
```

```forgeloop
kind: anchor_ref
round: 1
author_role: coder
created_at: 2026-03-31T09:12:00Z
handoff_id: mismatch-h1
review_target_ref: commits/sample-a1
compare_base_ref: commits/sample-base
commit: anchor(sample): first state
sha: abc1234
```

```forgeloop
kind: r1_result
round: 1
author_role: reviewer
created_at: 2026-03-31T09:20:00Z
handoff_id: mismatch-h1
review_target_ref: commits/sample-a2
verdict: clean
functional_correctness: pass
validation_adequacy: pass
local_structure_convergence: pass
local_regression_risk: low
open_issues: []
next_action: task_done
findings: []
```
