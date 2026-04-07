# Initiative Review Rolling Doc Contract

<!-- forgeloop:anchor purpose -->
## Purpose

`Initiative Review Rolling Doc` is the only append-only formal collaboration surface for one Initiative delivery loop.

It carries:

- Initiative identity and continuity
- Initiative delivery contract snapshot
- coder `G3` facts
- current Initiative review handoff
- `R3` results

<!-- forgeloop:anchor legal-machine-blocks -->
## Legal Machine Blocks

- `initiative_review_header`
- `initiative_contract_snapshot`
- `coder_update`
- `g3_result`
- `r3_result`

Header and contract snapshot are initialized once. All later formal facts append only.

<!-- forgeloop:anchor canonical-initiative-vocabulary -->
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

<!-- forgeloop:anchor handoff-law -->
## Handoff Law

- The current handoff is the latest `g3_result` in the current round whose `next_action=enter_r3`.
- `R3` is actionable only when `round`, `handoff_id`, and `review_target_ref` match that handoff exactly.
- If multiple matching results exist, only the latest one is actionable.
- Every `g3_result` that opens reviewer handoff must include `handoff_id`, `review_target_ref`, and `compare_base_ref`.
- `review_target_ref` names the Initiative delivery candidate being judged for the current handoff.
- `compare_base_ref` names the baseline the reviewer should compare against when judging that Initiative candidate.

<!-- forgeloop:anchor compare-base-law -->
## Compare Base Law

- The first Initiative handoff in one round must set `compare_base_ref` to the baseline that immediately preceded that round's Initiative delivery candidate.
- A later same-round Initiative handoff must keep the same `compare_base_ref`; same-round Initiative review stays cumulative unless the supervisor formally opens a new round.
- When `R3` requests same-Initiative repair and the supervisor opens the next round, the new round's first Initiative handoff must set `compare_base_ref` to the previous round's latest reviewed `review_target_ref`.
- Do not change `compare_base_ref` mid-round just because a later Milestone repair, a broader branch diff, or a wider workspace state exists.

<!-- forgeloop:anchor latest-matching-result-law -->
## Latest Matching Result Law

- If multiple `r3_result` blocks exist, only the latest appended result whose `round`, `handoff_id`, and `review_target_ref` match the current handoff is actionable.
- Older matching results remain history and must not be treated as current.
- A mismatched or stale `r3_result` does not close the round.

<!-- forgeloop:anchor derived-view-usage -->
## Recommended Derived-View Usage

- `current-effective` should expose only the current Initiative handoff plus the latest matching `r3_result`.
- `handoff-scoped/<handoff_id>.md` is the preferred hot-path helper for fresh `R3` entry when the authoritative rolling doc ref is still bound explicitly in the packet.
- `attempt-aware/round-<n>.md` is the preferred hot-path helper for same-Initiative round recovery.
- For Initiative review, the default delivery delta is `compare_base_ref .. review_target_ref` from the current handoff.
- Current workspace diff may help explain a blocker, but it is not the default Initiative review surface.
- Derived views are hot-path helpers only. If any view is missing, stale, or conflicts with the authoritative rolling doc, invalidate it and reread the rolling doc.

<!-- forgeloop:anchor recommended-template -->
## Recommended Template

- `r3_result` field structure is owned by `plugins/forgeloop/agents/initiative_reviewer.toml`; this template is only an aligned example.

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
compare_base_ref: initiative-rounds/day7/r0
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
delivery_readiness: pass
release_safety: pass
evidence_adequacy: pass
residual_risks: []
open_issues: []
next_action: mark_initiative_delivered
required_follow_ups: []
findings: []
```
````

<!-- forgeloop:anchor initialization-law -->
## Initialization Law

When the rolling doc does not yet exist:

- initialize only `initiative_review_header` and `initiative_contract_snapshot`
- write `coder_slot=coder` into the header
- let the `Global State Doc` carry `round=1`
- do not append fake `g3_result` or `r3_result` blocks during cold start
