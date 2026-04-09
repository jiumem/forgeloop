---
name: rebuild-runtime
description: Use when the runtime control plane is missing, conflicting, or cannot uniquely recover the next step; this skill reads the static truth sources, the Global State Doc, review rolling docs, and necessary Git facts to rebuild the minimum control plane needed to continue dispatch
---

# Rebuild Runtime

<!-- forgeloop:anchor role -->
`rebuild-runtime` does recovery only. It does not code, it does not review, and it does not replace `run-initiative` for ongoing dispatch. Here you act as a recovery-state `Supervisor`: rebuild the minimum runnable control plane from the formal truth sources and engineering facts, then hand the system back upstream.

<!-- forgeloop:anchor canonical-runtime-contract-refs -->
## Canonical Runtime Contract Refs

- shared `Global State Doc` contract -> `plugins/forgeloop/skills/run-initiative/references/global-state.md`
- `Task Review Rolling Doc` contract -> `plugins/forgeloop/skills/run-initiative/references/task-review-rolling-doc.md`
- `Milestone Review Rolling Doc` contract -> `plugins/forgeloop/skills/run-initiative/references/milestone-review-rolling-doc.md`
- `Initiative Review Rolling Doc` contract -> `plugins/forgeloop/skills/run-initiative/references/initiative-review-rolling-doc.md`
- runtime cutover contract -> `plugins/forgeloop/skills/run-initiative/references/runtime-cutover.md`
- shared anchor-addressing contract -> `plugins/forgeloop/skills/references/anchor-addressing.md`
- shared derived-view contract -> `plugins/forgeloop/skills/references/derived-views.md`

<!-- forgeloop:anchor truth-sources-boundaries -->
## Truth Sources And Hard Boundaries

The formal input surface contains only the Initiative static truth trio, the `Global State Doc`, the three layers of review rolling docs, and the necessary Git / PR / commit / test facts.

Hard boundaries:

- recover only the logical `coder_slot`, never the physical `agent_id`
- do not attempt to recover any reviewer binding or session-local thread table as formal state
- recover the current object-local `round`, never invent a new round
- write to the `Global State Doc` only when necessary
- the only updatable blocks are `global_state_header`, `current_snapshot`, `next_action`, and `last_transition`
- do not write any rolling doc body content
- do not modify the static truth sources and do not create a second state model in JSON / notes / hidden memory

<!-- forgeloop:anchor shared-runtime-recovery-law -->
## Shared Runtime Recovery Law

- `round` is object-local and supervisor-owned through the `Global State Doc`
- if the existing `Global State Doc` still agrees with newer formal facts, preserve its `round`; otherwise recover `round` from the active rolling doc when that rolling doc exposes one unique current round
- the current review handoff is object-scoped:
  - Task: the latest `review_handoff` in the current Task round
  - Milestone: the latest `review_handoff` in the current Milestone round
  - Initiative: the latest `review_handoff` in the current Initiative round
- a review result is actionable only when its `round` matches the current handoff round and its `review_target_ref` matches the current handoff's `review_target_ref`
- one round may expose at most one `review_handoff` and at most one `review_result`
- when recovery rebuilds reviewer entry, preserve the current handoff's `compare_base_ref`; do not fall back to workspace diff just because the review result does not echo the compare base
- a new round opens only on first entry into an object or after a reviewer requests same-object repair
- if `current_snapshot.active_plane=frontier` or `next_action.action=advance_frontier`, recover exactly one next runtime object from the admitted planning truth plus authoritative rolling docs
- use the same closure-first order as `run-initiative`: required current Milestone closure -> required current Initiative closure -> exactly one next-ready Task
- runtime recovery may rebuild the frontier, but it must not reopen planning, regenerate Task plans, or invent a new execution map

<!-- forgeloop:anchor recovery-order -->
## Recovery Order

First read the runtime cutover contract and bind `current_runtime_cutover_mode`.

If `current_runtime_cutover_mode=full_doc_default`, authoritative full-document recovery may be the default order and minimal-path recovery stays a validation sidecar.

If `current_runtime_cutover_mode=minimal_preferred` or `minimal_required`, recover in this order:

1. the existing `Global State Doc`, but only while it still agrees with newer formal facts
2. the active rolling doc's `current-effective` view when it is still legal and rebuildable
3. the active rolling doc's `round-scoped/round-<n>.md` view for the active candidate
4. authoritative rolling-doc block scans
5. full-document recovery only when the thinner layers cannot prove one unique frontier

<!-- forgeloop:anchor when-to-trigger -->
## When To Trigger

Trigger only in the following situations:

- the `Global State Doc` is missing, but rolling docs already exist
- the `Global State Doc` clearly conflicts with the total task doc or the rolling docs
- `code-loop` finds that the control plane cannot be recovered uniquely when binding an object
- the original thread cannot continue, but the formal docs and Git facts are still sufficient for recovery

<!-- forgeloop:anchor workflow -->
## Workflow

1. Bind the recovery surface
- Read `total_task_doc_ref` and the runtime cutover contract first, then read the existing `Global State Doc` and the three rolling docs through the mode-selected recovery path
- If the static truth sources are missing, or the Initiative binding cannot be confirmed uniquely, stop and ask the user

2. Determine the current formal frontier
- First respect canonical stop literals `wait_for_user`, `stop_on_blocker`, and `initiative_delivered` when they are consistent with the newer formal facts
- Prefer `current-effective` only when it can still be rebuilt from the same authoritative rolling doc without legality drift; otherwise invalidate it and reread the formal rolling doc
- If a round exposes duplicate `review_handoff` or duplicate `review_result`, stop and surface the illegal state explicitly
- Recover only from formal runtime truth. Workspace diff, chat summaries, and interrupted worker intent may help explain what happened, but they must never promote object progression without a rereadable formal block.
- Otherwise, use the newest formal frontier that has not yet closed as the active candidate
- If multiple candidates coexist, the fixed priority is: active Task repair / coder round > active Milestone review / repair > active Initiative review / repair > frontier selection after the last clean object

3. Determine the active object and next action
- Reuse `coder_slot` and `round` from the `Global State Doc` when they are still consistent; otherwise recover them from the active rolling doc
- If the current round has a `review_handoff` and no `review_result`, recover reviewer entry
- If the current round has a `review_result`, recover next action from that result
- If the current round has neither, treat any uncommitted code or chat-only progress as unfinished in-object work and recover coder continuation from the last legal formal state instead of promoting the object
- If recovery lands on `current_snapshot.active_plane=frontier` or `next_action.action=advance_frontier`, apply the same fixed supervisor routing order used by `run-initiative`: required current Milestone closure -> required Initiative closure -> exactly one next-ready Task. Do not recover directly into Task plane merely because one next-ready Task can be guessed.
- For Initiative delivery, recover reviewer intent exactly: actionable `review_result.next_action=initiative_delivered` becomes dispatcher stop state `initiative_delivered`
- If no single plane, object, `coder_slot`, `round`, and `next_action` can be proven, stop and ask the user

4. Rewrite the minimum control plane
- If the `Global State Doc` does not exist, initialize `global_state_header` first according to the canonical contract
- Write `current_snapshot` as the uniquely recovered active plane / active object / `coder_slot` / object `round`
- Write `next_action` as the uniquely recovered next step, including recovered `blocking_reason` when the action is `wait_for_user` or `stop_on_blocker`
- Write `last_transition` as a recovery transition explaining why the control plane was rebuilt, and classify the cause in `last_transition.reason` using the smallest fitting class: `control_plane`, `formal_state`, `execution_ready`, `runtime_resource`, `transport`, or `object_blocker`
- After writing, immediately hand control back to skill: `run-initiative`

<!-- forgeloop:anchor red-lines -->
## Red Lines

Never:

- write rolling doc body content
- recover a physical owner / thread id as formal state
- recover a reviewer binding as if it were durable control-plane truth
- let an outdated `Global State Doc` override newer rolling-doc facts
- treat chat memory, cache, or local derived hints as formal truth sources
- promote interrupted work to reviewer-ready or review-complete without a rereadable `review_handoff` or `review_result`
- collapse tooling, transport, quota, or environment failures into fake object-level blocker claims
- silently guess the active object, `coder_slot`, or next action

<!-- forgeloop:anchor completion-criteria -->
## Completion Criteria

On correct completion, all of the following should be true:

- the current active plane, active object, active `round`, and `coder_slot` can be recovered uniquely
- the `Global State Doc` exists, and `current_snapshot`, `next_action`, and `last_transition` are self-consistent
- the upstream dispatcher can re-enter `run-initiative` and continue without hidden context
- no second runtime truth source has been created outside the `Global State Doc` plus the Task, Milestone, and Initiative review rolling-doc layers
