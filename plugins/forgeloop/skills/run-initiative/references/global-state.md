# Global State Doc Contract

<!-- forgeloop:anchor purpose -->
## Purpose

`Global State Doc` is the only runtime-wide update-only control spine.

It exists to let `run-initiative`, `task-loop`, `milestone-loop`, `initiative-loop`, and `rebuild-runtime` recover one current active object, one current runtime route, and one recent transition without inventing a second state model.

<!-- forgeloop:anchor durable-rules -->
## Durable Rules

- Only these machine blocks are legal here:
  - `global_state_header`
  - `current_snapshot`
  - `next_action`
  - `last_transition`
- These blocks are update-only. Rewrite the latest version in place; do not append a log of historical state blocks.
- Repo-local refs inside this doc must keep repo-root-relative durable form.
- `current_snapshot` carries only the minimum active-object state needed for recovery.
- `next_action` must use the canonical runtime routing vocabulary directly. Do not invent parallel supervisor-only names such as `dispatch_coder_continue_task`.
- `request_reviewer_handoff` is a rolling-doc-local coder intent, not a legal `Global State Doc.next_action.action`. After a valid current handoff exists, the `Global State Doc` materializes reviewer entry as `enter_r1`, `enter_r2`, or `enter_r3`.

<!-- forgeloop:anchor formal-block-contract -->
## Formal Block Contract

- `global_state_header` must include `kind`, `initiative_key`, `total_task_doc_ref`, `created_at`, and `updated_at`.
- `current_snapshot` must include `kind`, `active_plane`, and `initiative_key`.
- `current_snapshot` variants:
  - `active_plane=task`: include `milestone_key`, `task_key`, `coder_slot`, and `round`.
  - `active_plane=milestone`: include `milestone_key`, `coder_slot`, and `round`.
  - `active_plane=initiative`: include `coder_slot` and `round` while Initiative work is still active; when `next_action.action=initiative_delivered`, `coder_slot` and `round` may be omitted for the delivered stop snapshot.
  - `active_plane=frontier`: no concrete active object is currently bound; `task_key`, `coder_slot`, and `round` must be omitted; `milestone_key` may remain only when the next ready-object search is already constrained to one Milestone.
- `next_action` must include `kind`, `action`, `blocking_reason`, and `updated_at`.
- `next_action.blocking_reason` must be non-null only for `wait_for_user` or `stop_on_blocker`; all other actions must write `blocking_reason: null`.
- `last_transition` must include `kind`, `updated_at`, `from_action`, `to_action`, and `reason`.
- `last_transition.to_action` should match the currently written `next_action.action`.
- `last_transition.from_action` may be the prior runtime action or a lifecycle marker such as `cold_start` or `runtime_recovery`.
- When a repair task has been objectized from a Milestone or Initiative and the callback is still active, `last_transition` must additionally include:
  - `callback_source_plane`
  - `callback_return_rolling_doc_ref`
  - `callback_round_behavior`
- `callback_source_plane` must be exactly `milestone` or `initiative`.
- `callback_source_milestone_key` is required when `callback_source_plane=milestone`.
- `callback_return_rolling_doc_ref` must stay repo-root-relative and point to the source review rolling doc that should regain control.
- `callback_round_behavior` must be exactly `continue_current_round` or `enter_next_round`.

<!-- forgeloop:anchor runtime-routing-vocabulary -->
## Canonical Runtime Routing Vocabulary

`next_action.action` may only use these values:

- Task-layer routing:
  - `continue_task_coder_round`
  - `enter_r1`
  - `continue_task_repair`
  - `return_to_source_object`
  - `select_next_ready_object`
  - `task_done`
  - `escalate_to_milestone`
- Milestone-layer routing:
  - `continue_milestone_repair`
  - `objectize_task_repair`
  - `enter_r2`
  - `enter_initiative_review`
- Initiative-layer routing:
  - `continue_initiative_repair`
  - `objectize_task_repair`
  - `enter_r3`
  - `mark_initiative_delivered`
  - `initiative_delivered`
- Shared stop routing:
  - `wait_for_user`
  - `stop_on_blocker`

If the current next step is derived from a rolling doc, preserve the same literal action value when it is already in this routing vocabulary.

<!-- forgeloop:anchor recommended-template -->
## Recommended Template

````markdown
# <initiative_key> Global State

```forgeloop
kind: global_state_header
initiative_key: day7-first-situation-closure
total_task_doc_ref: docs/initiatives/active/day7-first-situation-closure/total-task-doc.md
created_at: 2026-03-30T10:00:00Z
updated_at: 2026-03-30T10:00:00Z
```

```forgeloop
kind: current_snapshot
active_plane: task
initiative_key: day7-first-situation-closure
milestone_key: D7FS-M1
task_key: D7FS-T1
coder_slot: coder
round: 1
```

```forgeloop
kind: next_action
action: continue_task_coder_round
blocking_reason: null
updated_at: 2026-03-30T10:00:00Z
```

```forgeloop
kind: last_transition
updated_at: 2026-03-30T10:00:00Z
from_action: cold_start
to_action: continue_task_coder_round
reason: initial_task_entry
```
````

<!-- forgeloop:anchor field-guidance -->
## Field Guidance

- `current_snapshot.active_plane` must be exactly one of `task`, `milestone`, `initiative`, or `frontier`.
- Include only the active object keys needed for that plane. Do not keep a parallel full frontier table here.
- A frontier snapshot is legal after a clean Task or Milestone has closed but the next ready object is not yet uniquely bound.
- A delivered Initiative stop snapshot may keep only `initiative_key` when `next_action.action=initiative_delivered`.
- `coder_slot` is the logical owner identity. Never persist physical thread ids here.
- `round` is object-local and supervisor-owned whenever a concrete active object is still bound.
- `last_transition` may carry callback or recovery details when a repair task was objectized, but those details must remain transition-scoped rather than becoming a second state model.
- Callback metadata in `last_transition` is mandatory while an objectized repair task remains the active Task.

<!-- forgeloop:anchor snapshot-variants -->
## Snapshot Variants

Frontier selection after a clean Task may be written as:

````markdown
```forgeloop
kind: current_snapshot
active_plane: frontier
initiative_key: day7-first-situation-closure
milestone_key: D7FS-M1
```
````

Objectized repair callback metadata may be written as:

````markdown
```forgeloop
kind: last_transition
updated_at: 2026-03-30T10:30:00Z
from_action: objectize_task_repair
to_action: continue_task_repair
reason: milestone_requested_bounded_repair_task
callback_source_plane: milestone
callback_source_milestone_key: D7FS-M1
callback_return_rolling_doc_ref: .forgeloop/day7-first-situation-closure/milestone-review/D7FS-M1.md
callback_round_behavior: enter_next_round
```
````

<!-- forgeloop:anchor bootstrap-law -->
## Bootstrap Law

On runtime cold start or runtime rebuild:

- initialize only the legal blocks above
- keep the first writable state thin
- let object-level rolling docs carry coder/reviewer body content
- do not derive block names or `next_action` spellings from old design examples when this contract is available
