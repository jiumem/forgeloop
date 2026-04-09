# Initiative Review Rolling Doc Contract

<!-- forgeloop:anchor purpose -->
## Purpose

`Initiative Review Rolling Doc` is the only append-only formal review surface for one Initiative delivery loop.

It carries only:

- Initiative identity and continuity
- Initiative review contract snapshot
- one coder-authored `review_handoff` per round when an Initiative candidate is formally ready for review
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

- `object_type: initiative`
- `schema_version: 2`
- `initiative_key`
- `coder_slot`
- `created_at`

`review_contract_snapshot` is the smallest durable Initiative review contract snapshot. It may summarize goal, `milestone_scope`, and stable authority pointers such as `acceptance_authority_ref`, `acceptance_index_ref`, and `evidence_entrypoint_ref`, but it must not restate Initiative success criteria or become a reviewer bootstrap dossier.
When one of these pointers targets a Markdown anchor, store it as compact repo-root-relative-doc-ref#anchor-selector shorthand for the canonical `doc_ref + anchor_selector` pair. Packet assembly must split that shorthand back into the canonical pair before dispatch.

<!-- forgeloop:anchor round-shape-law -->
## Round Shape Law

Every Initiative round has at most:

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

The current Initiative handoff is the latest `review_handoff` in the current round.

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
- `delivery_readiness`
- `release_safety`
- `evidence_adequacy`
- `residual_risks`
- `open_issues`
- `next_action`
- `required_follow_ups`
- `findings`

`review_result.next_action` must be one of:

- `continue_coder_round`
- `initiative_delivered`
- `wait_for_user`
- `stop_on_blocker`

Materialization law:

- these values are the canonical Initiative reviewer output vocabulary
- `code-loop` may materialize them directly into the `Global State Doc`
- `continue_coder_round` means same-Initiative repair in a new Initiative round with the same execution universe still bound
- `initiative_delivered` is the only legal Initiative acceptance result that materializes to the delivered stop state
- none of these values authorizes planning re-entry or execution-map regeneration

`review_result` is actionable only when:

- its `round` matches the current round
- its `review_target_ref` matches the current round's `review_handoff.review_target_ref`

One Initiative round closes only when its `review_result` exists.

<!-- forgeloop:anchor previous-review-law -->
## Previous Review Law

Initiative repair history should be linked minimally:

- use `review_handoff.addresses_review_result_id` to point at the exact prior reviewer judgment being addressed
- do not create run-id chains, history indexes, or replay ledgers inside this doc

<!-- forgeloop:anchor derived-view-usage -->
## Recommended Derived-View Usage

- `current-effective` should expose only the latest round's `review_handoff`, the same round's `review_result` when present, and the addressed prior `review_result` when the handoff links one
- `round-scoped/round-<n>.md` is the preferred hot-path helper for one complete Initiative round
- current workspace diff may help explain a blocker, but it is not the default Initiative review surface
- derived views are hot-path helpers only; if any view is missing, stale, or conflicts with the authoritative rolling doc, invalidate it and reread the rolling doc

<!-- forgeloop:anchor recommended-template -->
## Recommended Template

- `review_result` field structure is owned by `plugins/forgeloop/agents/initiative_reviewer.toml`; this template is only an aligned example.

````markdown
# Initiative Review Rolling Doc: day7-first-situation-closure

```forgeloop
kind: review_header
object_type: initiative
schema_version: 2
initiative_key: day7-first-situation-closure
coder_slot: coder
created_at: 2026-03-30T10:00:00Z
```

```forgeloop
kind: review_contract_snapshot
goal: Deliver the first blessed reply-only Day 7 path.
milestone_scope:
  - D7FS-M1
  - D7FS-M2
  - D7FS-M3
  - D7FS-M4
acceptance_authority_ref: docs/initiatives/active/day7-first-situation-closure/total-task-doc.md#initiative/success-criteria/ic-1
acceptance_index_ref: docs/initiatives/active/day7-first-situation-closure/total-task-doc.md#acceptance-matrix/initiative-acceptance-index/ic-1
evidence_entrypoint_ref: docs/initiatives/active/day7-first-situation-closure/total-task-doc.md#acceptance-matrix/evidence-entrypoints
```

```forgeloop
kind: review_handoff
round: 1
author_role: coder
created_at: 2026-03-30T12:00:00Z
review_target_ref: initiative-rounds/day7/r1
compare_base_ref: initiative-rounds/day7/r0
summary: Ready for Initiative review after composing milestone evidence into one delivery candidate.
evidence_refs:
  - local://g3-output/day7-r1.txt
```

```forgeloop
kind: review_result
review_result_id: review-init-day7-r1
round: 1
author_role: reviewer
created_at: 2026-03-30T12:30:00Z
review_target_ref: initiative-rounds/day7/r1
verdict: clean
delivery_readiness: pass
release_safety: pass
evidence_adequacy: pass
residual_risks: []
open_issues: []
next_action: initiative_delivered
required_follow_ups: []
findings: []
```
````

<!-- forgeloop:anchor initialization-law -->
## Initialization Law

When the rolling doc does not yet exist:

- initialize only `review_header` and `review_contract_snapshot`
- write `coder_slot=coder` into the header
- let the `Global State Doc` carry `round=1`
- do not append fake `review_handoff` or `review_result` blocks during cold start
