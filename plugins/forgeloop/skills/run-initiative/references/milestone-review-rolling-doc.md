# Milestone Review Rolling Doc Contract

## Purpose

`Milestone Review Rolling Doc` is the only append-only formal collaboration surface for one Milestone.

It carries:

- Milestone identity and continuity
- Milestone contract snapshot
- coder `G2` facts
- current Milestone review handoff
- `R2` results

## Legal Machine Blocks

- `milestone_review_header`
- `milestone_contract_snapshot`
- `coder_update`
- `g2_result`
- `r2_result`

Header and contract snapshot are initialized once. All later formal facts append only.

## Canonical Milestone Vocabulary

- `g2_result.next_action` must be one of:
  - `continue_milestone_repair`
  - `objectize_task_repair`
  - `enter_r2`
  - `wait_for_user`
  - `stop_on_blocker`
- `r2_result.next_action` must be one of:
  - `continue_milestone_repair`
  - `objectize_task_repair`
  - `enter_initiative_review`
  - `select_next_ready_object`
  - `wait_for_user`
  - `stop_on_blocker`

## Handoff Law

- The current Milestone handoff is the latest `g2_result` in the current round whose `next_action=enter_r2`.
- Every `g2_result` that opens reviewer handoff must include `handoff_id` and `review_target_ref`.
- `R2` is actionable only when `round`, `handoff_id`, and `review_target_ref` match the current handoff exactly.

## Recommended Template

````markdown
# Milestone Review Rolling Doc: D7FS-M1

```forgeloop
kind: milestone_review_header
initiative_key: day7-first-situation-closure
milestone_key: D7FS-M1
coder_slot: coder
created_at: 2026-03-30T10:00:00Z
```

```forgeloop
kind: milestone_contract_snapshot
goal: Lock the canonical runtime contract and HUD truth surface.
task_scope:
  - D7FS-T1
  - D7FS-T2
acceptance:
  - pnpm gate:visor.decision-system
```

```forgeloop
kind: g2_result
round: 1
author_role: coder
created_at: 2026-03-30T11:00:00Z
verdict: pass
next_action: enter_r2
handoff_id: ms-d7fs-m1-r1-h1
review_target_ref: milestone-rounds/d7fs-m1/r1
anchors:
  - task-review/D7FS-T1.md#handoff:task-d7fs-t1-r1-a1
  - task-review/D7FS-T2.md#handoff:task-d7fs-t2-r1-a1
evidence_refs:
  - local://g2-output/d7fs-m1-r1.txt
```

```forgeloop
kind: r2_result
round: 1
author_role: reviewer
created_at: 2026-03-30T11:20:00Z
handoff_id: ms-d7fs-m1-r1-h1
review_target_ref: milestone-rounds/d7fs-m1/r1
verdict: changes_requested
next_action: continue_milestone_repair
required_follow_ups:
  - tighten HUD truth exposure
```
````

## Initialization Law

When the rolling doc does not yet exist:

- initialize only `milestone_review_header` and `milestone_contract_snapshot`
- write `coder_slot=coder` into the header
- let the `Global State Doc` carry `round=1`
- do not append fake `g2_result` or `r2_result` blocks during cold start
