# Task Review Rolling Doc Contract

<!-- forgeloop:anchor purpose -->
## Purpose

`Task Review Rolling Doc` is the only append-only formal collaboration surface for one Task.

It carries:

- Task identity and continuity
- Task contract snapshot
- coder implementation facts
- `G1` results
- `anchor / fixup` handoff blocks
- `R1` results

<!-- forgeloop:anchor legal-machine-blocks -->
## Legal Machine Blocks

- `task_review_header`
- `task_contract_snapshot`
- `coder_update`
- `g1_result`
- `anchor_ref`
- `fixup_ref`
- `r1_result`

Header and contract snapshot are initialized once. All later formal facts append only.

<!-- forgeloop:anchor canonical-task-vocabulary -->
## Canonical Task Vocabulary

- `g1_result.next_action` must be one of:
  - `continue_task_coder_round`
  - `request_reviewer_handoff`
  - `wait_for_user`
  - `stop_on_blocker`
- `r1_result.next_action` must be one of:
  - `continue_task_repair`
  - `return_to_source_object`
  - `select_next_ready_object`
  - `task_done`
  - `escalate_to_milestone`
  - `wait_for_user`
  - `stop_on_blocker`

`request_reviewer_handoff` remains rolling-doc-local coder intent. Once one valid current handoff exists, the `Global State Doc` should materialize reviewer entry as `enter_r1` rather than copying `request_reviewer_handoff` directly.

<!-- forgeloop:anchor handoff-law -->
## Handoff Law

- The current Task handoff is the latest `anchor_ref` or `fixup_ref` in the current round.
- Every `anchor_ref` and `fixup_ref` must include `handoff_id` and `review_target_ref`.
- `R1` is actionable only when `round`, `handoff_id`, and `review_target_ref` match the current handoff exactly.
- `anchor_ref` or `fixup_ref` is legal only after `G1 pass`.

<!-- forgeloop:anchor latest-matching-result-law -->
## Latest Matching Result Law

- If multiple `r1_result` blocks exist, only the latest appended result whose `round`, `handoff_id`, and `review_target_ref` match the current handoff is actionable.
- Older matching results remain history and must not be treated as current.
- A mismatched or stale `r1_result` does not close the round.

<!-- forgeloop:anchor derived-view-usage -->
## Recommended Derived-View Usage

- `current-effective` should expose only the current Task handoff plus the latest matching `r1_result`.
- `handoff-scoped/<handoff_id>.md` is the preferred hot-path helper for fresh reviewer entry when the authoritative rolling doc ref is still bound explicitly in the packet.
- `attempt-aware/round-<n>.md` is the preferred hot-path helper for same-Task same-round recovery.
- If any derived view disagrees with the authoritative rolling doc, invalidate it and reread the formal rolling doc.

<!-- forgeloop:anchor recommended-template -->
## Recommended Template

````markdown
# Task Review Rolling Doc: D7FS-T1

```forgeloop
kind: task_review_header
initiative_key: day7-first-situation-closure
milestone_key: D7FS-M1
task_key: D7FS-T1
coder_slot: coder
created_at: 2026-03-30T10:00:00Z
```

```forgeloop
kind: task_contract_snapshot
summary: Lock the canonical runtime contract for PRICE_PUSHBACK.
spec_refs:
  - kairos_foundation/packages/engines-visor/src/kernel/decision-core.ts
acceptance:
  - pnpm gate:visor.decision-system
```

```forgeloop
kind: coder_update
round: 1
author_role: coder
created_at: 2026-03-30T10:15:00Z
summary: Tightened runtime contract assertions.
files_touched:
  - kairos_foundation/packages/engines-visor/src/kernel/decision-core.ts
```

```forgeloop
kind: g1_result
round: 1
author_role: coder
created_at: 2026-03-30T10:20:00Z
verdict: pass
next_action: request_reviewer_handoff
commands:
  - pnpm gate:visor.decision-system
evidence_refs:
  - local://gate-output/task-d7fs-t1.txt
```

```forgeloop
kind: anchor_ref
round: 1
author_role: coder
created_at: 2026-03-30T10:25:00Z
handoff_id: task-d7fs-t1-r1-a1
review_target_ref: commits/abc123
commit: anchor(d7fs-t1): lock runtime contract
sha: abc123
```

```forgeloop
kind: r1_result
round: 1
author_role: reviewer
created_at: 2026-03-30T10:35:00Z
handoff_id: task-d7fs-t1-r1-a1
review_target_ref: commits/abc123
verdict: clean
next_action: task_done
findings: []
```
````

<!-- forgeloop:anchor initialization-law -->
## Initialization Law

When the rolling doc does not yet exist:

- initialize only `task_review_header` and `task_contract_snapshot`
- write `coder_slot=coder` into the header
- let `task-loop` write `round=1` into the `Global State Doc`
- do not append fake `coder_update`, `g1_result`, or `r1_result` blocks just to make the file look complete
