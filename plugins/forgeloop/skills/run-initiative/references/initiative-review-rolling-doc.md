# Initiative Review Rolling Doc Contract

## Purpose

`Initiative Review Rolling Doc` is the only append-only formal collaboration surface for one Initiative delivery loop.

It carries:

- Initiative identity and continuity
- Initiative delivery contract snapshot
- coder `G3` facts
- current Initiative review handoff
- `R3` results

## Legal Machine Blocks

- `initiative_review_header`
- `initiative_contract_snapshot`
- `coder_update`
- `g3_result`
- `r3_result`

Header and contract snapshot are initialized once. All later formal facts append only.

## Canonical Initiative Vocabulary

- `g3_result.next_action` must be one of:
  - `continue_initiative_repair`
  - `objectize_task_repair`
  - `enter_r3`
  - `wait_for_user`
  - `stop_on_blocker`
- `r3_result.next_action` must be one of:
  - `continue_initiative_repair`
  - `objectize_task_repair`
  - `mark_initiative_delivered`
  - `wait_for_user`
  - `stop_on_blocker`

## Handoff Law

- The current Initiative handoff is the latest `g3_result` in the current round whose `next_action=enter_r3`.
- Every `g3_result` that opens reviewer handoff must include `handoff_id` and `review_target_ref`.
- `R3` is actionable only when `round`, `handoff_id`, and `review_target_ref` match the current handoff exactly.

## Recommended Template

````markdown
# Initiative Review Rolling Doc: day7-first-situation-closure

```forgeloop
kind: initiative_review_header
initiative_key: day7-first-situation-closure
coder_slot: coder
created_at: 2026-03-30T10:00:00Z
```

```forgeloop
kind: initiative_contract_snapshot
goal: Deliver the first blessed reply-only Day 7 path.
milestone_scope:
  - D7FS-M1
  - D7FS-M2
  - D7FS-M3
  - D7FS-M4
success_criteria:
  - review.md reflects closure state and residual risks
```

```forgeloop
kind: g3_result
round: 1
author_role: coder
created_at: 2026-03-30T12:00:00Z
verdict: pass
next_action: enter_r3
handoff_id: init-day7-r1-h1
review_target_ref: initiative-rounds/day7/r1
milestones:
  - milestone-review/D7FS-M1.md
  - milestone-review/D7FS-M2.md
  - milestone-review/D7FS-M3.md
  - milestone-review/D7FS-M4.md
evidence_refs:
  - local://g3-output/day7-r1.txt
```

```forgeloop
kind: r3_result
round: 1
author_role: reviewer
created_at: 2026-03-30T12:30:00Z
handoff_id: init-day7-r1-h1
review_target_ref: initiative-rounds/day7/r1
verdict: clean
next_action: mark_initiative_delivered
required_follow_ups: []
```
````

## Initialization Law

When the rolling doc does not yet exist:

- initialize only `initiative_review_header` and `initiative_contract_snapshot`
- write `coder_slot=coder` into the header
- let the `Global State Doc` carry `round=1`
- do not append fake `g3_result` or `r3_result` blocks during cold start
