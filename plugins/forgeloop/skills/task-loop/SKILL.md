---
name: task-loop
description: Compatibility frontend. Use when the `Global State Doc` has uniquely confirmed that current progress is at a ready or active Task; this wrapper binds `mode=task` and dispatches `code-loop`.
---

# Task Loop

<!-- forgeloop:anchor role -->
## Role

`task-loop` is a compatibility frontend.

It no longer owns the full Task supervisory law. Its only job is to confirm Task-plane entry remains legal, bind `mode=task`, and dispatch `code-loop`.

Task semantics such as `continue_task_coder_round`, `enter_r1`, `continue_task_repair`, `return_to_source_object`, `select_next_ready_object`, and `task_done` remain defined by the canonical runtime contracts rather than by this wrapper.

<!-- forgeloop:anchor canonical-runtime-contract-refs -->
## Canonical Runtime Contract Refs

- shared `Global State Doc` contract -> `../run-initiative/references/global-state.md`
- shared runtime cutover contract -> `../run-initiative/references/runtime-cutover.md`
- shared supervisor backbone -> `../code-loop/SKILL.md`
- mode binding reference -> `../code-loop/references/runtime-object-modes.md`
- `Task Review Rolling Doc` contract -> `../run-initiative/references/task-review-rolling-doc.md`

<!-- forgeloop:anchor truth-sources-boundaries -->
## Truth Sources And Hard Boundaries

The formal input surface contains only the Initiative static truth trio, the `Global State Doc`, the current `Task Review Rolling Doc`, and the necessary Git / test / commit facts.

Hard boundaries:

- `current_runtime_cutover_mode` must be bound before dispatch
- this wrapper must not create independent Task supervisory law
- the current Task handoff and latest matching `r1_result` remain defined by the `Task Review Rolling Doc` contract
- `coder_slot`, `round`, and reviewer-entry materialization remain owned by the `Global State Doc` plus `code-loop`

<!-- forgeloop:anchor task.cutover-mode-law -->
## Task Cutover Mode Law

Bind `../run-initiative/references/runtime-cutover.md` before deciding the Task default read path.

This wrapper does not redefine Task packet or fallback semantics. After binding `mode=task`, consume the shared cutover law through `code-loop`.

<!-- forgeloop:anchor workflow -->
## Workflow

1. Confirm `current_runtime_cutover_mode`.
2. Confirm `current_snapshot.active_plane=task`, unless this is a fresh Task entry being initialized now.
3. Confirm one active Task uniquely.
4. Bind `mode=task`.
5. Dispatch skill: `code-loop`.
6. Do not duplicate Task routing, handoff, or review-result logic here.

<!-- forgeloop:anchor stop-conditions -->
## Stop Conditions

Stop immediately and hand control back upstream or to the user when:

- the active Task cannot be confirmed uniquely
- the Task-plane entry is illegal under the current `Global State Doc`
- the required Task rolling doc contract cannot be bound uniquely

<!-- forgeloop:anchor red-lines -->
## Red Lines

Never:

- fork Task supervisory logic away from `code-loop`
- maintain a second Task control path here
- re-specify Task rolling-doc or reviewer contracts here
- treat this wrapper as permission to bypass the canonical `G1 -> anchor / fixup -> R1` chain

<!-- forgeloop:anchor completion-criteria -->
## Completion Criteria

On correct completion, all of the following should be true:

- Task-plane entry remains legal
- `mode=task` is bound explicitly
- all further Task supervision happens through `code-loop`
- no second runtime truth source has been created
