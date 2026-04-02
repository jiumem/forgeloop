---
name: initiative-loop
description: Compatibility frontend. Use when the `Global State Doc` has uniquely confirmed that current progress is at a ready or active Initiative; this wrapper binds `mode=initiative` and dispatches `code-loop`.
---

# Initiative Loop

<!-- forgeloop:anchor role -->
## Role

`initiative-loop` is a compatibility frontend.

It no longer owns the full Initiative supervisory law. Its only job is to confirm Initiative-plane entry remains legal, bind `mode=initiative`, and dispatch `code-loop`.

Initiative semantics such as `continue_initiative_repair`, `objectize_task_repair`, `enter_r3`, `mark_initiative_delivered`, and dispatcher-written `initiative_delivered` remain defined by the canonical runtime contracts rather than by this wrapper.

<!-- forgeloop:anchor canonical-runtime-contract-refs -->
## Canonical Runtime Contract Refs

- shared `Global State Doc` contract -> `../run-initiative/references/global-state.md`
- shared runtime cutover contract -> `../run-initiative/references/runtime-cutover.md`
- shared supervisor backbone -> `../code-loop/SKILL.md`
- mode binding reference -> `../code-loop/references/runtime-object-modes.md`
- `Initiative Review Rolling Doc` contract -> `../run-initiative/references/initiative-review-rolling-doc.md`

<!-- forgeloop:anchor truth-sources-boundaries -->
## Truth Sources And Hard Boundaries

The formal input surface contains only the Initiative static truth trio, the `Global State Doc`, the current `Initiative Review Rolling Doc`, the included Milestone evidence, and the necessary release / rollout / deployment / flag / readiness / test facts.

Hard boundaries:

- `current_runtime_cutover_mode` must be bound before dispatch
- this wrapper must not create independent Initiative supervisory law
- the current Initiative handoff and latest matching `r3_result` remain defined by the `Initiative Review Rolling Doc` contract
- `coder_slot`, `round`, objectized repair callback handling, and reviewer-entry materialization remain owned by the `Global State Doc` plus `code-loop`

<!-- forgeloop:anchor initiative.cutover-mode-law -->
## Initiative Cutover Mode Law

Bind `../run-initiative/references/runtime-cutover.md` before deciding the Initiative default read path.

This wrapper does not redefine Initiative packet or fallback semantics. After binding `mode=initiative`, consume the shared cutover law through `code-loop`.

<!-- forgeloop:anchor workflow -->
## Workflow

1. Confirm `current_runtime_cutover_mode`.
2. Confirm `current_snapshot.active_plane=initiative`, unless this is a fresh Initiative entry being initialized now.
3. Confirm one active Initiative uniquely.
4. Bind `mode=initiative`.
5. Dispatch skill: `code-loop`.
6. Do not duplicate Initiative routing, handoff, or review-result logic here.

<!-- forgeloop:anchor stop-conditions -->
## Stop Conditions

Stop immediately and hand control back upstream or to the user when:

- the active Initiative cannot be confirmed uniquely
- the Initiative-plane entry is illegal under the current `Global State Doc`
- the required Initiative rolling doc contract cannot be bound uniquely

<!-- forgeloop:anchor red-lines -->
## Red Lines

Never:

- fork Initiative supervisory logic away from `code-loop`
- maintain a second Initiative control path here
- re-specify Initiative rolling-doc or reviewer contracts here
- treat this wrapper as permission to bypass the canonical `G3 -> R3` chain

<!-- forgeloop:anchor completion-criteria -->
## Completion Criteria

On correct completion, all of the following should be true:

- Initiative-plane entry remains legal
- `mode=initiative` is bound explicitly
- all further Initiative supervision happens through `code-loop`
- no second runtime truth source has been created
