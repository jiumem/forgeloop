# Milestone Review Rolling Doc Contract

<!-- forgeloop:anchor purpose -->
## Purpose

`Milestone Review Rolling Doc` is the only append-only formal review surface for one Milestone.

It carries only:

- Milestone identity and continuity
- Milestone review contract snapshot
- one coder-authored `review_handoff` per round when a Milestone candidate is formally ready for review
- one reviewer-authored `review_result` per round

It does not carry coder progress logs, gate attempt logs, navigation indexes, or evidence catalogs.
It does not carry reviewer identity, physical thread ids, or session-local binding state.

<!-- forgeloop:anchor legal-machine-blocks -->
## Legal Machine Blocks

- `review_header`
- `review_contract_snapshot`
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

`review_contract_snapshot` is the smallest durable Milestone review contract snapshot. It may summarize goal, `task_scope`, acceptance, and other static Milestone-local review truth, but it must not become a reviewer bootstrap dossier.

<!-- forgeloop:anchor round-shape-law -->
## Round Shape Law

Every Milestone round has at most:

- one `review_handoff`
- one `review_result`

Same-round supersede is illegal.

If new coder work is required after one `review_result`, the supervisor opens the next round in the `Global State Doc` first.

Do not append a second same-round `review_handoff` or `review_result`.

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

The current Milestone handoff is the latest `review_handoff` in the current round.

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

- `continue_milestone_repair`
- `enter_initiative_review`
- `select_next_ready_object`
- `wait_for_user`
- `stop_on_blocker`

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

- `current-effective` should expose only the latest round's `review_handoff`, the same round's `review_result` when present, and the addressed prior `review_result` when the handoff links one
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
acceptance:
  - pnpm gate:visor.decision-system
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

- initialize only `review_header` and `review_contract_snapshot`
- write `coder_slot=coder` into the header
- let the `Global State Doc` carry `round=1`
- do not append fake `review_handoff` or `review_result` blocks during cold start
