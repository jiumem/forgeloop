# Global State Doc Contract

<!-- forgeloop:anchor purpose -->
## Purpose

`Global State Doc` is the only runtime-wide update-only control spine.

It exists to let `run-initiative`, `code-loop`, and `rebuild-runtime` recover one current active object, one current runtime route, and one recent transition without inventing a second state model.

For repo-local Initiatives, required placement is sibling `.forgeloop/global-state.md` under the Initiative document directory.

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
- `review_handoff` and `review_result` are rolling-doc-local facts, not legal `Global State Doc` blocks. The `Global State Doc` materializes only the canonical runtime control state derived from them plus the active coder/reviewer dispatch state.
- physical `agent_id`s, reviewer bindings, and other session-local worker identity belong to runtime-private state only. They are never legal `Global State Doc` fields.
- cross-plane worker cleanup is mandatory before execution changes planes; runtime bindings must be closed before planning bindings stay active, and planning bindings must be closed before runtime bindings stay active

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

<!-- forgeloop:anchor runtime-routing-vocabulary -->
## Canonical Runtime Routing Vocabulary

`next_action.action` may only use these values:

- `continue_coder_round`
- `enter_review`
- `advance_frontier`
- `initiative_delivered`
- `wait_for_user`
- `stop_on_blocker`

Law:

- `continue_coder_round` means the currently bound runtime object remains active and the same logical `coder_slot` continues after formal state refresh.
- `enter_review` means the currently bound runtime object already exposes one legal current `review_handoff` and reviewer entry is the only legal next step.
- `advance_frontier` means the currently bound runtime object has been accepted at its own runtime layer and `run-initiative` must resolve the next concrete runtime object from formal truth.
- `advance_frontier` is runtime-only frontier progress. It is never permission to reopen planning, regenerate Task plans, or synthesize a new execution map.
- `initiative_delivered` is the only terminal delivered state.
- `wait_for_user` and `stop_on_blocker` are the only canonical stop actions.
- any legacy frontier-selection literal outside the canonical vocabulary is illegal in the `Global State Doc`.
- `review_result.next_action` uses the same canonical runtime vocabulary, except that `enter_review` remains a supervisor-side materialization state rather than a reviewer output.

<!-- forgeloop:anchor supervisor-materialization-law -->
## Supervisor Materialization Law

When `run-initiative`, `code-loop`, or `rebuild-runtime` materializes formal runtime truth into the `Global State Doc`:

- no current-round `review_handoff` and no current-round matching `review_result` -> `next_action.action=continue_coder_round`
- one legal current-round `review_handoff` and no current-round matching `review_result` -> `next_action.action=enter_review`

Task-mode reviewer materialization:

- `continue_coder_round` -> keep the current Task bound, open the next Task round, write `next_action.action=continue_coder_round`
- `advance_frontier` -> move to `active_plane=frontier`, clear concrete Task execution fields, write `next_action.action=advance_frontier`
- `wait_for_user` -> write `next_action.action=wait_for_user`
- `stop_on_blocker` -> write `next_action.action=stop_on_blocker`

Milestone-mode reviewer materialization:

- `continue_coder_round` -> keep the current Milestone bound, open the next Milestone round, write `next_action.action=continue_coder_round`
- `advance_frontier` -> move to `active_plane=frontier`, clear concrete Milestone execution fields except any still-legal frontier constraint, write `next_action.action=advance_frontier`
- `wait_for_user` -> write `next_action.action=wait_for_user`
- `stop_on_blocker` -> write `next_action.action=stop_on_blocker`

Initiative-mode reviewer materialization:

- `continue_coder_round` -> keep the current Initiative bound, open the next Initiative round, write `next_action.action=continue_coder_round`
- `initiative_delivered` -> keep `active_plane=initiative`, write `next_action.action=initiative_delivered`, and allow delivered-stop snapshot shape
- `wait_for_user` -> write `next_action.action=wait_for_user`
- `stop_on_blocker` -> write `next_action.action=stop_on_blocker`

Reviewer-side action names and supervisor-side action names now share one canonical runtime vocabulary.

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
action: continue_coder_round
blocking_reason: null
updated_at: 2026-03-30T10:00:00Z
```

```forgeloop
kind: last_transition
updated_at: 2026-03-30T10:00:00Z
from_action: cold_start
to_action: continue_coder_round
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
- reviewer continuity is never a formal field here; reused reviewers remain session-local only.
- `round` is object-local and supervisor-owned whenever a concrete active object is still bound.
- `last_transition` may carry resume or recovery details, but it must not become a second state model.

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

<!-- forgeloop:anchor bootstrap-law -->
## Bootstrap Law

On runtime cold start or runtime rebuild:

- initialize only the legal blocks above
- keep the first writable state thin
- let object-level rolling docs carry coder/reviewer body content
- do not derive block names or `next_action` spellings from old design examples when this contract is available
