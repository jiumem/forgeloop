---
name: task-loop
description: Compatibility frontend. Use when the `Global State Doc` has uniquely confirmed that current progress is at a ready or active Task; this wrapper binds `mode=task` and dispatches `code-loop`.
---

# Task Loop

<!-- forgeloop:anchor role -->
`task-loop` is a compatibility wrapper over `code-loop`.

Goal: bind `mode=task` and enter `code-loop` for one already-bound Task.
Do not redefine routing, cutover, packet, review, or recovery law here.
If the active Task or current round cannot be confirmed uniquely, stop and hand control back to `run-initiative`.
Never create wrapper-local state, wrapper-local action names, or wrapper-local recovery rules.

<!-- forgeloop:anchor canonical-runtime-contract-refs -->
## Canonical Runtime Contract Refs

- shared executor -> `../code-loop/SKILL.md`
- mode binding reference -> `../code-loop/references/runtime-object-modes.md`

<!-- forgeloop:anchor truth-sources-boundaries -->
## Boundary

- this wrapper binds only `mode=task`
- `code-loop` owns routing, cutover, packet law, handoff law, review law, and recovery law
- the wrapper must not create Task-local control state or duplicate runtime contracts

<!-- forgeloop:anchor task.cutover-mode-law -->
## Workflow

1. Confirm one active Task and one current round uniquely.
2. Bind `mode=task`.
3. Dispatch skill: `code-loop`.

<!-- forgeloop:anchor stop-conditions -->
## Stop Conditions

Stop immediately and hand control back upstream or to the user when:

- the active Task cannot be confirmed uniquely
- the Task-plane entry is illegal under the current runtime contracts

<!-- forgeloop:anchor red-lines -->
## Red Lines

Never:

- fork Task supervisory logic away from `code-loop`
- maintain a second Task control path here
- re-specify Task rolling-doc or reviewer contracts here

<!-- forgeloop:anchor completion-criteria -->
## Completion Criteria

On correct completion, all of the following should be true:

- Task-plane entry remains legal
- `mode=task` is bound explicitly
- all further Task supervision happens through `code-loop`
- no second runtime truth source has been created
