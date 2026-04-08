# Task Review Rolling Doc Contract

<!-- forgeloop:anchor purpose -->
## Purpose

`Task Review Rolling Doc` is the only append-only formal review surface for one Task.

It carries only:

- Task identity and continuity
- Task review contract snapshot
- one coder-authored `review_handoff` per round when a Task candidate is formally ready for review
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

- `object_type: task`
- `schema_version: 2`
- `initiative_key`
- `milestone_key`
- `task_key`
- `coder_slot`
- `created_at`

`review_contract_snapshot` is the smallest durable Task review contract snapshot. It may summarize scope, `spec_refs`, and stable authority pointers such as `acceptance_authority_ref`, `acceptance_index_ref`, and `evidence_entrypoint_ref`, but it must not restate Task acceptance content or become a reviewer bootstrap dossier.

<!-- forgeloop:anchor round-shape-law -->
## Round Shape Law

Every Task round has at most:

- one `review_handoff`
- one `review_result`

Same-round supersede is illegal.

Do not append:

- a second `review_handoff` in the same round
- a second `review_result` in the same round
- a same-round replacement for an earlier handoff or review result

If new coder work is required after one `review_result`, the supervisor opens the next round in the `Global State Doc` first.

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

`addresses_review_result_id` is legal only for a repair round. It points to the previous reviewer judgment this round is explicitly addressing.

The current Task handoff is the latest `review_handoff` in the current round.

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
- `functional_correctness`
- `validation_adequacy`
- `local_structure_convergence`
- `local_regression_risk`
- `open_issues`
- `next_action`
- `findings`

`review_result.next_action` must be one of:

- `continue_task_repair`
- `select_next_ready_object`
- `task_done`
- `escalate_to_milestone`
- `wait_for_user`
- `stop_on_blocker`

`review_result` is actionable only when:

- its `round` matches the current round
- its `review_target_ref` matches the current round's `review_handoff.review_target_ref`

One Task round closes only when its `review_result` exists.

<!-- forgeloop:anchor previous-review-law -->
## Previous Review Law

Task repair history should be linked minimally:

- use `review_handoff.addresses_review_result_id` to point at the exact prior reviewer judgment being addressed
- do not create run-id chains, history indexes, or replay ledgers inside this doc

If the previous review link cannot be expressed with one `review_result_id`, do not expand this doc into an index. Use a disposable derived view or reread the formal history directly.

<!-- forgeloop:anchor derived-view-usage -->
## Recommended Derived-View Usage

- `current-effective` should expose only the latest round's `review_handoff`, the same round's `review_result` when present, and the addressed prior `review_result` when the handoff links one
- `round-scoped/round-<n>.md` is the preferred hot-path helper for one complete round
- current workspace diff may help explain a blocker, but it is not the default Task review surface
- derived views are hot-path helpers only; if any view is missing, stale, or conflicts with the authoritative rolling doc, invalidate it and reread the rolling doc

<!-- forgeloop:anchor recommended-template -->
## Recommended Template

- `review_result` field structure is owned by `plugins/forgeloop/agents/task_reviewer.toml`; this template is only an aligned example.

````markdown
# Task Review Rolling Doc: D7FS-T1

```forgeloop
kind: review_header
object_type: task
schema_version: 2
initiative_key: day7-first-situation-closure
milestone_key: D7FS-M1
task_key: D7FS-T1
coder_slot: coder
created_at: 2026-03-30T10:00:00Z
```

```forgeloop
kind: review_contract_snapshot
summary: Lock the canonical runtime contract for PRICE_PUSHBACK.
spec_refs:
  - kairos_foundation/packages/engines-visor/src/kernel/decision-core.ts
acceptance_authority_ref: docs/initiatives/active/day7-first-situation-closure/total-task-doc.md#task-ledger/task-definitions/d7fs-t1
acceptance_index_ref: docs/initiatives/active/day7-first-situation-closure/total-task-doc.md#acceptance-matrix/task-acceptance-index/d7fs-t1
evidence_entrypoint_ref: docs/initiatives/active/day7-first-situation-closure/total-task-doc.md#acceptance-matrix/evidence-entrypoints
```

```forgeloop
kind: review_handoff
round: 1
author_role: coder
created_at: 2026-03-30T10:25:00Z
review_target_ref: commits/abc123
compare_base_ref: commits/prev999
summary: Ready for Task review after tightening runtime contract assertions.
evidence_refs:
  - local://gate-output/task-d7fs-t1.txt
```

```forgeloop
kind: review_result
review_result_id: review-task-d7fs-t1-r1
round: 1
author_role: reviewer
created_at: 2026-03-30T10:35:00Z
review_target_ref: commits/abc123
verdict: clean
functional_correctness: pass
validation_adequacy: pass
local_structure_convergence: pass
local_regression_risk: low
open_issues: []
next_action: task_done
findings: []
```
````

<!-- forgeloop:anchor initialization-law -->
## Initialization Law

When the rolling doc does not yet exist:

- initialize only `review_header` and `review_contract_snapshot`
- write `coder_slot=coder` into the header
- let `code-loop` write `round=1` into the `Global State Doc`
- do not append fake `review_handoff` or `review_result` blocks during cold start
