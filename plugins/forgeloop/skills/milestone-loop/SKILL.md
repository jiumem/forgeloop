---
name: milestone-loop
description: Compatibility frontend. Use when the `Global State Doc` has uniquely confirmed that current progress is at a ready or active Milestone; this wrapper binds `mode=milestone` and dispatches `code-loop`.
---

# Milestone Loop

<!-- forgeloop:anchor role -->
`milestone-loop` is a compatibility wrapper over `code-loop`.

Goal: bind `mode=milestone` and enter `code-loop` for one already-bound Milestone.
Do not redefine routing, cutover, packet, review, or recovery law here.
If the active Milestone or current round cannot be confirmed uniquely, stop and hand control back to `run-initiative`.
Never create wrapper-local state, wrapper-local action names, or wrapper-local recovery rules.

<!-- forgeloop:anchor canonical-runtime-contract-refs -->
## Canonical Runtime Contract Refs

- shared executor -> `../code-loop/SKILL.md`
- mode binding reference -> `../code-loop/references/runtime-object-modes.md`

<!-- forgeloop:anchor truth-sources-boundaries -->
## Boundary

- this wrapper binds only `mode=milestone`
- `code-loop` owns routing, cutover, packet law, handoff law, review law, and recovery law
- the wrapper must not create Milestone-local control state or duplicate runtime contracts

<!-- forgeloop:anchor milestone.cutover-mode-law -->
## Workflow

1. Confirm one active Milestone and one current round uniquely.
2. Bind `mode=milestone`.
3. Dispatch skill: `code-loop`.

<!-- forgeloop:anchor stop-conditions -->
## Stop Conditions

Stop immediately and hand control back upstream or to the user when:

- the active Milestone cannot be confirmed uniquely
- the Milestone-plane entry is illegal under the current runtime contracts

<!-- forgeloop:anchor red-lines -->
## Red Lines

Never:

- fork Milestone supervisory logic away from `code-loop`
- maintain a second Milestone control path here
- re-specify Milestone rolling-doc or reviewer contracts here

<!-- forgeloop:anchor completion-criteria -->
## Completion Criteria

On correct completion, all of the following should be true:

- Milestone-plane entry remains legal
- `mode=milestone` is bound explicitly
- all further Milestone supervision happens through `code-loop`
- no second runtime truth source has been created
