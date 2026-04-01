# Gap Rolling Doc: SAMPLE-REOPEN

```forgeloop
kind: planning_rolling_header
initiative_key: anchor-sliced-dispatch-optimization
stage: gap_analysis_doc
artifact_ref: docs/initiatives/active/anchor-sliced-dispatch-optimization/gap-analysis.md
planner_slot: planner
created_at: 2026-03-31T10:00:00Z
```

```forgeloop
kind: planning_contract_snapshot
created_at: 2026-03-31T10:00:00Z
stage: gap_analysis_doc
artifact_ref: docs/initiatives/active/anchor-sliced-dispatch-optimization/gap-analysis.md
stage_reference_ref: references/gap-analysis.md
rolling_doc_contract_ref: references/planning-rolling-doc.md
design_ref: docs/initiatives/active/anchor-sliced-dispatch-optimization/design.md
```

```forgeloop
kind: planner_update
round: 3
author_role: planner
created_at: 2026-03-31T10:05:00Z
next_action: request_reviewer_handoff
summary: Gap analysis update is ready for review.
```

```forgeloop
kind: gap_analysis_ref
round: 3
author_role: planner
created_at: 2026-03-31T10:06:00Z
handoff_id: gap-r3-a1
review_target_ref: docs/initiatives/active/anchor-sliced-dispatch-optimization/gap-analysis.md#gap-v3
```

```forgeloop
kind: gap_review_result
round: 3
author_role: reviewer
created_at: 2026-03-31T10:15:00Z
handoff_id: gap-r3-a1
review_target_ref: docs/initiatives/active/anchor-sliced-dispatch-optimization/gap-analysis.md#gap-v3
verdict: changes_requested
seal_status: not_sealed
next_action: wait_for_upstream_judgment
upstream_reopen_recommendation.target_stage: Design Doc
upstream_reopen_recommendation.reason: design baseline changed after gap authoring started
```
