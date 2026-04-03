# Planning State Doc Control Reference

<!-- forgeloop:anchor document-role -->
## Document Role

- Plane: planning control spine
- Applies to: the active planning state for one Initiative
- Primary readers: `run-planning` and `planning-loop`
- Primary purpose: keep only the minimum planning control state needed for recovery, dispatch, and legal stop routing
- For repo-local Initiatives, required placement is sibling `.forgeloop/planning-state.md` under the Initiative document directory

<!-- forgeloop:anchor legal-blocks -->
## Legal Blocks

- `planning_state_header`
- `current_snapshot`
- `next_action`
- `last_transition`

<!-- forgeloop:anchor control-law -->
## Control Law

- `Planning State Doc` is the only planning control spine.
- `current_snapshot` carries only the bound Initiative, active stage, active `artifact_ref`, active `rolling_doc_ref`, and when known `planner_slot` plus `round`.
- `artifact_ref` and `rolling_doc_ref` must use durable repo-root-relative refs. Materialize absolute paths only at dispatch time when needed.
- only a fresh stage with no rolling doc may temporarily omit `planner_slot` and `round`
- once `planner_slot` or `round` is known from the active rolling doc or recovery, write it back into `current_snapshot` immediately; do not leave recoverable values implicit after the stage is in flight
- `next_action` owns only immediate in-stage dispatch or terminal stop for the currently bound stage
- `last_transition` carries only the most recent bind, recovery, resume, reopen, or cross-stage routing fact
- no other planning doc may invent a parallel routing vocabulary

<!-- forgeloop:anchor canonical-planning-routing-vocabulary -->
## Canonical Planning Routing Vocabulary

`next_action.action` may only be:

- `enter_planning_loop`
- `waiting`
- `blocked`
- `sealed_planning_docs_ready`

`last_transition.transition` may only be:

- `cold_start_to_design`
- `recover_in_stage`
- `resume_waiting`
- `resume_blocked`
- `advance_to_gap_analysis`
- `advance_to_total_task_doc`
- `reopen_to_design`
- `reopen_to_gap_analysis`

Law:

- `next_action` owns only in-stage dispatch and terminal stop for the currently bound stage
- `last_transition` owns recovery, resume, and cross-stage routing facts
- no other planning doc may invent a parallel routing vocabulary

<!-- forgeloop:anchor supervisor-materialization-law -->
## Supervisor Materialization Law

When `planning-loop` materializes worker output into the `Planning State Doc`:

- `wait_for_upstream_judgment` -> `next_action.action=waiting`
- `stop_on_blocker` -> `next_action.action=blocked`
- clean seal of `Design Doc` writes only `last_transition.transition=advance_to_gap_analysis` when the sealed `Design Doc` explicitly marks `Gap Analysis Requirement: required`
- clean seal of `Design Doc` writes only `last_transition.transition=advance_to_total_task_doc` when the sealed `Design Doc` explicitly marks `Gap Analysis Requirement: not_required`
- clean seal of `Gap Analysis Doc` writes only `last_transition.transition=advance_to_total_task_doc`
- clean seal of `Total Task Doc` -> `next_action.action=sealed_planning_docs_ready`

Worker-local action names never become a parallel supervisor vocabulary.

<!-- forgeloop:anchor formal-block-contract -->
## Formal Block Contract

- `planning_state_header` must include `kind`, `initiative_key`, `created_at`, and `updated_at`.
- `current_snapshot` must include `kind`, `initiative_key`, `stage`, `artifact_ref`, and `rolling_doc_ref`.
- `current_snapshot.planner_slot` and `current_snapshot.round` are required once they are recoverable from the active rolling doc or prior control-plane truth.
- `next_action` must include `kind`, `action`, and `updated_at`.
- `last_transition` must include `kind`, `transition`, `updated_at`, and `reason`.
- `last_transition.transition` should remain compatible with the currently bound `next_action.action`.

<!-- forgeloop:anchor recommended-template -->
## Recommended Template

````markdown
```forgeloop
kind: planning_state_header
initiative_key: day7-first-situation-closure
created_at: 2026-04-02T00:00:00Z
updated_at: 2026-04-02T00:00:00Z
```

```forgeloop
kind: current_snapshot
initiative_key: day7-first-situation-closure
stage: design_doc
artifact_ref: docs/initiatives/active/day7-first-situation-closure/design.md
rolling_doc_ref: docs/initiatives/active/day7-first-situation-closure/.forgeloop/design-rolling.md
planner_slot: planner
round: 1
```

```forgeloop
kind: next_action
action: enter_planning_loop
updated_at: 2026-04-02T00:00:00Z
```

```forgeloop
kind: last_transition
transition: cold_start_to_design
updated_at: 2026-04-02T00:00:00Z
reason: initial_entry
```
````

<!-- forgeloop:anchor red-lines -->
## Red Lines

- do not write planner or reviewer body content here
- do not create a second planning control model outside the formal planning artifacts, rolling docs, and this document
