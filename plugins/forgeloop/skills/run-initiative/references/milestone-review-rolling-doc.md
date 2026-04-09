# Milestone Review Rolling Doc Contract

<!-- forgeloop:anchor purpose -->
## Purpose

`Milestone Review Rolling Doc` is the only append-only formal review surface for one Milestone.

It carries only:

- Milestone identity and continuity
- Milestone review contract snapshot
- one or more coder-authored `coder_update` blocks in the current round before reviewer entry
- one coder-authored `review_handoff` per round when the current round is formally ready for review
- one reviewer-authored `review_result` per round

It does not carry coder progress logs, gate attempt logs, navigation indexes, or evidence catalogs.
It does not carry reviewer identity, physical thread ids, or session-local binding state.

<!-- forgeloop:anchor legal-machine-blocks -->
## Legal Machine Blocks

- `review_header`
- `review_contract_snapshot`
- `coder_update`
- `review_handoff`
- `review_result`

Header and contract snapshot are initialized once. All later formal facts append only.

<!-- forgeloop:anchor header-law -->
## Header Law

`review_header` must include:

- `object_type: milestone`
- `schema_version: 2`
- `initiative_key`
- `milestone_key`
- `coder_slot`
- `created_at`

`review_contract_snapshot` is the smallest durable Milestone review contract snapshot. It may summarize goal, `task_scope`, and stable authority pointers such as `acceptance_authority_ref`, `reference_assignment_ref`, `acceptance_index_ref`, and `evidence_entrypoint_ref`, but it must not restate Milestone acceptance content or become a reviewer bootstrap dossier.
When one of these pointers targets a Markdown anchor, store it as compact repo-root-relative-doc-ref#anchor-selector shorthand for the canonical `doc_ref + anchor_selector` pair. Packet assembly must split that shorthand back into the canonical pair before dispatch.

<!-- forgeloop:anchor round-shape-law -->
## Round Shape Law

Every Milestone round may have:

- multiple `coder_update` blocks before reviewer entry
- at most one `review_handoff`
- at most one `review_result`

Law:

- the latest `coder_update` in the current round is the current coder intent until the round appends `review_handoff`
- once the round appends `review_handoff`, do not append a later `coder_update` in that same round
- same-round supersede is legal only for `coder_update`
- same-round supersede is illegal for `review_handoff` and `review_result`

If new coder work is required after one `review_result`, the supervisor opens the next round in the `Global State Doc` first.

<!-- forgeloop:anchor coder-update-law -->
## Coder Update Law

`coder_update` is the only coder-owned formal round-intent block in this doc.

It must include:

- `kind`
- `round`
- `author_role: coder`
- `created_at`
- `next_action`
- `summary`
- `blocking_reason`

`next_action` may only be:

- `continue_local_repair`
- `request_reviewer_handoff`
- `wait_for_user`
- `stop_on_blocker`

Law:

- `blocking_reason` must be non-null only for `wait_for_user` or `stop_on_blocker`; all other values must write `blocking_reason: null`
- the latest `coder_update` in the current round is the only actionable coder intent before reviewer entry
- `continue_local_repair` means stay in the same object and the same round
- `request_reviewer_handoff` means the coder is formally asking to open reviewer entry for this same round; it does not by itself replace `review_handoff`
- `wait_for_user` and `stop_on_blocker` are formal coder stop intents and must not be left only in prose

<!-- forgeloop:anchor review-handoff-law -->
## Review Handoff Law

`review_handoff` is the only coder-owned reviewer-entry block in this doc.

It must include:

- `kind`
- `round`
- `author_role: coder`
- `created_at`
- `review_target_ref`
- `compare_base_ref`
- `summary`
- `evidence_refs`

It may additionally include:

- `addresses_review_result_id`

Law:

- append `review_handoff` only when the latest current-round `coder_update.next_action=request_reviewer_handoff`
- do not append `review_handoff` as a progress note, tentative candidate, or partial checkpoint
- one round allows at most one coder-authored `review_handoff`
- if the current round is not ready for review, do not write a `review_handoff`

<!-- forgeloop:anchor review-result-law -->
## Review Result Law

`review_result` is the only reviewer-owned formal result block in this doc.

It must include:

- `kind`
- `review_result_id`
- `round`
- `author_role: reviewer`
- `created_at`
- `review_target_ref`
- `verdict`
- `stage_structure_convergence`
- `mainline_merge_safety`
- `evidence_adequacy`
- `residual_risks`
- `open_issues`
- `next_action`
- `required_follow_ups`
- `findings`

`review_result.next_action` must be one of:

- `continue_coder_round`
- `advance_frontier`
- `wait_for_user`
- `stop_on_blocker`

Materialization law:

- these values are the canonical Milestone reviewer output vocabulary
- `code-loop` may materialize them directly into the `Global State Doc`
- `continue_coder_round` means same-Milestone repair in a new Milestone round with the same execution universe still bound
- `advance_frontier` means the current Milestone has passed its own layer and runtime frontier must advance
- none of these values authorizes planning re-entry, Task regeneration, or a new execution-map decomposition

`review_result` is actionable only when:

- its `round` matches the current round
- its `review_target_ref` matches the current round's `review_handoff.review_target_ref`

One Milestone round closes only when its `review_result` exists.

<!-- forgeloop:anchor previous-review-law -->
## Previous Review Law

Milestone repair history should be linked minimally:

- use `review_handoff.addresses_review_result_id` to point at the exact prior reviewer judgment being addressed
- do not create run-id chains, history indexes, or replay ledgers inside this doc

<!-- forgeloop:anchor derived-view-usage -->
## Recommended Derived-View Usage

- `current-effective` should expose only the latest current-round `coder_update`, the current round's `review_handoff` when present, the same round's `review_result` when present, and the addressed prior `review_result` when the handoff links one
- `round-scoped/round-<n>.md` is the preferred hot-path helper for one complete Milestone round
- current workspace diff may help explain a blocker, but it is not the default Milestone review surface
- derived views are hot-path helpers only; if any view is missing, stale, or conflicts with the authoritative rolling doc, invalidate it and reread the rolling doc

<!-- forgeloop:anchor recommended-template -->
## Recommended Template

- `review_result` field structure is owned by `plugins/forgeloop/agents/milestone_reviewer.toml`; this template is only an aligned example.

````markdown
# Milestone Review Rolling Doc: D7FS-M1

```forgeloop
kind: review_header
object_type: milestone
schema_version: 2
initiative_key: day7-first-situation-closure
milestone_key: D7FS-M1
coder_slot: coder
created_at: 2026-03-30T10:00:00Z
```

```forgeloop
kind: review_contract_snapshot
goal: Lock the canonical runtime contract and HUD truth surface.
task_scope:
  - D7FS-T1
  - D7FS-T2
acceptance_authority_ref: docs/initiatives/active/day7-first-situation-closure/total-task-doc.md#milestone-master-table/milestone-acceptance/d7fs-m1
reference_assignment_ref: docs/initiatives/active/day7-first-situation-closure/total-task-doc.md#milestone-master-table/milestone-reference-assignment/d7fs-m1
acceptance_index_ref: docs/initiatives/active/day7-first-situation-closure/total-task-doc.md#acceptance-matrix/milestone-acceptance-index/d7fs-m1
evidence_entrypoint_ref: docs/initiatives/active/day7-first-situation-closure/total-task-doc.md#acceptance-matrix/evidence-entrypoints
```

```forgeloop
kind: coder_update
round: 1
author_role: coder
created_at: 2026-03-30T10:40:00Z
next_action: continue_local_repair
summary: Integrated Task outputs and still tightening the HUD truth boundary.
blocking_reason: null
```

```forgeloop
kind: coder_update
round: 1
author_role: coder
created_at: 2026-03-30T11:00:00Z
next_action: request_reviewer_handoff
summary: Ready for Milestone review after composing Task outputs into one stage candidate.
blocking_reason: null
```

```forgeloop
kind: review_handoff
round: 1
author_role: coder
created_at: 2026-03-30T11:00:00Z
review_target_ref: milestone-rounds/d7fs-m1/r1
compare_base_ref: milestone-rounds/d7fs-m1/r0
summary: Ready for Milestone review after composing Task outputs into one stage candidate.
evidence_refs:
  - local://g2-output/d7fs-m1-r1.txt
```

```forgeloop
kind: review_result
review_result_id: review-ms-d7fs-m1-r1
round: 1
author_role: reviewer
created_at: 2026-03-30T11:20:00Z
review_target_ref: milestone-rounds/d7fs-m1/r1
verdict: changes_requested
stage_structure_convergence: fail
mainline_merge_safety: fail
evidence_adequacy: pass
residual_risks:
  - Current Task outputs do not yet compose into one stable Milestone boundary.
open_issues:
  - The mainline integration surface is still carrying a split truth path.
next_action: continue_coder_round
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

- initialize only `review_header` and `review_contract_snapshot`
- write `coder_slot=coder` into the header
- let the `Global State Doc` carry `round=1`
- do not append fake `coder_update`, `review_handoff`, or `review_result` blocks during cold start
