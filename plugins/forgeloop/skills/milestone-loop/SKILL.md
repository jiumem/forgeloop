---
name: milestone-loop
description: Compatibility frontend. Use when the `Global State Doc` has uniquely confirmed that current progress is at a ready or active Milestone; this wrapper binds `mode=milestone` and dispatches `code-loop`.
---

# Milestone Loop

<!-- forgeloop:anchor role -->
## Role

`milestone-loop` is a compatibility frontend.

It no longer owns the full Milestone supervisory law. Its only job is to confirm Milestone-plane entry remains legal, bind `mode=milestone`, and dispatch `code-loop`.

Milestone semantics such as `continue_milestone_repair`, `objectize_task_repair`, `enter_r2`, `enter_initiative_review`, and `select_next_ready_object` remain defined by the canonical runtime contracts rather than by this wrapper.

<!-- forgeloop:anchor canonical-runtime-contract-refs -->
## Canonical Runtime Contract Refs

- shared `Global State Doc` contract -> `../run-initiative/references/global-state.md`
- shared runtime cutover contract -> `../run-initiative/references/runtime-cutover.md`
- shared supervisor backbone -> `../code-loop/SKILL.md`
- mode binding reference -> `../code-loop/references/runtime-object-modes.md`
- `Milestone Review Rolling Doc` contract -> `../run-initiative/references/milestone-review-rolling-doc.md`

<!-- forgeloop:anchor truth-sources-boundaries -->
## Truth Sources And Hard Boundaries

The formal input surface contains only the Initiative static truth trio, the `Global State Doc`, the current `Milestone Review Rolling Doc`, the included Task evidence, and the necessary Git / PR / merge-base / test facts.

Hard boundaries:

- `current_runtime_cutover_mode` must be bound before dispatch
- this wrapper must not create independent Milestone supervisory law
- the current Milestone handoff and latest matching `r2_result` remain defined by the `Milestone Review Rolling Doc` contract
- `coder_slot`, `round`, objectized repair callback handling, and reviewer-entry materialization remain owned by the `Global State Doc` plus `code-loop`

<!-- forgeloop:anchor milestone.cutover-mode-law -->
## Milestone Cutover Mode Law

Bind `../run-initiative/references/runtime-cutover.md` before deciding the Milestone default read path.

This wrapper does not redefine Milestone packet or fallback semantics. After binding `mode=milestone`, consume the shared cutover law through `code-loop`.

<!-- forgeloop:anchor workflow -->
## Workflow

1. Confirm `current_runtime_cutover_mode`.
2. Confirm `current_snapshot.active_plane=milestone`, unless this is a fresh Milestone entry being initialized now.
3. Confirm one active Milestone uniquely.
4. Bind `mode=milestone`.
5. Dispatch skill: `code-loop`.
6. Do not duplicate Milestone routing, handoff, or review-result logic here.

<!-- forgeloop:anchor stop-conditions -->
## Stop Conditions

Stop immediately and hand control back upstream or to the user when:

- the active Milestone cannot be confirmed uniquely
- the Milestone-plane entry is illegal under the current `Global State Doc`
- the required Milestone rolling doc contract cannot be bound uniquely

<!-- forgeloop:anchor red-lines -->
## Red Lines

Never:

- fork Milestone supervisory logic away from `code-loop`
- maintain a second Milestone control path here
- re-specify Milestone rolling-doc or reviewer contracts here
- treat this wrapper as permission to bypass the canonical `G2 -> R2` chain

<!-- forgeloop:anchor completion-criteria -->
## Completion Criteria

On correct completion, all of the following should be true:

- Milestone-plane entry remains legal
- `mode=milestone` is bound explicitly
- all further Milestone supervision happens through `code-loop`
- no second runtime truth source has been created
