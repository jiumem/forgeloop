# Milestone Review Rolling Doc Contract

<!-- forgeloop:anchor purpose -->
## Purpose

`Milestone Review Rolling Doc` is the only append-only formal collaboration surface for one Milestone.

It carries:

- Milestone identity and continuity
- Milestone contract snapshot
- coder `G2` facts
- current Milestone review handoff
- `R2` results

<!-- forgeloop:anchor legal-machine-blocks -->
## Legal Machine Blocks

- `milestone_review_header`
- `milestone_contract_snapshot`
- `coder_update`
- `g2_result`
- `r2_result`

Header and contract snapshot are initialized once. All later formal facts append only.

<!-- forgeloop:anchor canonical-milestone-vocabulary -->
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

<!-- forgeloop:anchor handoff-law -->
## Handoff Law

- The current handoff is the latest `g2_result` in the current round whose `next_action=enter_r2`.
- `R2` is actionable only when `round`, `handoff_id`, and `review_target_ref` match that handoff exactly.
- If multiple matching results exist, only the latest one is actionable.
- Every `g2_result` that opens reviewer handoff must include `handoff_id` and `review_target_ref`.

<!-- forgeloop:anchor latest-matching-result-law -->
## Latest Matching Result Law

- If multiple `r2_result` blocks exist, only the latest appended result whose `round`, `handoff_id`, and `review_target_ref` match the current handoff is actionable.
- Older matching results remain history and must not be treated as current.
- A mismatched or stale `r2_result` does not close the round.

<!-- forgeloop:anchor derived-view-usage -->
## Recommended Derived-View Usage

- `current-effective` should expose only the current Milestone handoff plus the latest matching `r2_result`.
- `handoff-scoped/<handoff_id>.md` is the preferred hot-path helper for fresh `R2` entry when the authoritative rolling doc ref is still bound explicitly in the packet.
- `attempt-aware/round-<n>.md` is the preferred hot-path helper for same-Milestone round recovery.
- Derived views are hot-path helpers only. If any view is missing, stale, or conflicts with the authoritative rolling doc, invalidate it and reread the rolling doc.

<!-- forgeloop:anchor recommended-template -->
## Recommended Template

- `r2_result` field structure is owned by `plugins/forgeloop/agents/milestone_reviewer.toml`; this template is only an aligned example.

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
stage_structure_convergence: fail
mainline_merge_safety: fail
evidence_adequacy: pass
residual_risks:
  - Current task anchors do not yet compose into one stable Milestone boundary.
open_issues:
  - The mainline integration surface is still carrying a split truth path.
next_action: continue_milestone_repair
required_follow_ups:
  - tighten HUD truth exposure
findings:
  - id: ms-d7fs-m1-r1-f1
    evidence_level: Confirmed
    summary: The current Milestone candidate still exposes a split truth path at the integration boundary.
```
````

<!-- forgeloop:anchor initialization-law -->
## Initialization Law

When the rolling doc does not yet exist:

- initialize only `milestone_review_header` and `milestone_contract_snapshot`
- write `coder_slot=coder` into the header
- let the `Global State Doc` carry `round=1`
- do not append fake `g2_result` or `r2_result` blocks during cold start
