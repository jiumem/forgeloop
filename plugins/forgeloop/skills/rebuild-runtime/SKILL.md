---
name: rebuild-runtime
description: Use when the runtime control plane is missing, conflicting, or cannot uniquely recover the next step; this skill reads the static truth sources, the Global State Doc, review rolling docs, and necessary Git facts to rebuild the minimum control plane needed to continue dispatch
---

# Rebuild Runtime

<!-- forgeloop:anchor role -->
`rebuild-runtime` does recovery only. It does not code, it does not review, and it does not replace `run-initiative` for ongoing dispatch. Here you act as a recovery-state `Supervisor`: rebuild the minimum runnable control plane from the formal truth sources and engineering facts, then hand the system back upstream.

<!-- forgeloop:anchor canonical-runtime-contract-refs -->
## Canonical Runtime Contract Refs

- shared `Global State Doc` contract -> `../run-initiative/references/global-state.md`
- `Task Review Rolling Doc` contract -> `../run-initiative/references/task-review-rolling-doc.md`
- `Milestone Review Rolling Doc` contract -> `../run-initiative/references/milestone-review-rolling-doc.md`
- `Initiative Review Rolling Doc` contract -> `../run-initiative/references/initiative-review-rolling-doc.md`
- runtime cutover contract -> `../run-initiative/references/runtime-cutover.md`
- shared anchor-addressing contract -> `../references/anchor-addressing.md`
- shared derived-view contract -> `../references/derived-views.md`

<!-- forgeloop:anchor truth-sources-boundaries -->
## Truth Sources And Hard Boundaries

The formal input surface contains only the Initiative static truth trio `design_ref`, `gap_analysis_ref`, and `total_task_doc_ref` (`gap_analysis_ref` may be `N/A` for some Initiative types), the `Global State Doc`, the three layers of review rolling docs, and the necessary Git / PR / commit / test facts.

Hard boundaries:
- recover only the logical `coder_slot`, never the physical `agent_id`
- recover the current object-local `round`, never invent a new round
- write to the `Global State Doc` only when necessary
- if the `Global State Doc` does not exist, you may initialize `global_state_header` only according to the canonical `Global State Doc` contract
- if the existing `global_state_header` conflicts with static truth-source bindings, you may correct `global_state_header` first, but only according to the canonical `Global State Doc` contract
- the only updatable blocks are `global_state_header`, `current_snapshot`, `next_action`, and `last_transition`
- do not write any rolling doc body content
- do not modify the static truth sources and do not create a second state model in JSON / notes / hidden memory
- do not invent runtime block shape or `next_action` spelling from memory or older design examples when the canonical runtime contract refs above are available
- bind the runtime cutover contract first and choose the default recovery read path from `current_runtime_cutover_mode`; do not hardcode minimal-first or full-doc-first recovery anywhere else

<!-- forgeloop:anchor shared-runtime-recovery-law -->
## Shared Runtime Recovery Law

- `round` is object round and supervisor-owned through the `Global State Doc`; coder and reviewers only echo it in rolling docs
- if the existing `Global State Doc` still agrees with newer formal facts, preserve its `round`; otherwise recover `round` from the active rolling doc when that rolling doc exposes one unique current round
- the current review handoff is object-scoped:
  - Task: the latest `anchor_ref` or `fixup_ref` in the current round
  - Milestone: the latest `g2_result` in the current round whose `next_action=enter_r2`
  - Initiative: the latest `g3_result` in the current round whose `next_action=enter_r3`
- a review result is actionable only when its `round`, `handoff_id`, and `review_target_ref` match that current handoff exactly; if multiple review results match one current handoff, only the latest appended matching block is actionable
- a new round opens only on first entry into an object, after a reviewer requests same-object repair, or after callback semantics from a repair Task explicitly say the source object should enter the next round
- if callback metadata must be recovered for an objectized repair Task, recover `callback_round_behavior` from the source formal block kind: actionable `g2_result` / `g3_result` objectization means `continue_current_round`; actionable `r2_result` / `r3_result` objectization means `enter_next_round`

<!-- forgeloop:anchor recovery-order -->
## Recovery Order

First read the runtime cutover contract and bind `current_runtime_cutover_mode`.

If `current_runtime_cutover_mode=full_doc_default`, authoritative full-document recovery may be the default order and minimal-path recovery stays a validation sidecar.

If `current_runtime_cutover_mode=minimal_preferred` or `minimal_required`, recover in this order:

1. the existing `Global State Doc`, but only while it still agrees with newer formal facts
2. the active rolling doc's `current-effective` view when it is still legal and rebuildable
3. `handoff-scoped` and `attempt-aware` views for the active candidate
4. authoritative rolling-doc block scans
5. full-document recovery only when the thinner layers cannot prove one unique frontier

Every promotion to a lower-priority layer must carry an explicit reason. In `minimal_required`, stop instead of using ordinary full-document fallback unless the cutover contract explicitly allows the disaster-recovery exception.

<!-- forgeloop:anchor derived-view-invalidation -->
## Derived-View Invalidation

Invalidate a derived view and fall back to the authoritative rolling doc when:

- a newer formal block was appended after the view was materialized
- the view no longer points at the current handoff
- the rolling doc now exposes multiple actionable results instead of one unique result
- selector legality for the view's supporting formal inputs can no longer be proven

Do not try to repair recovery by interpreting stale derived output as if it were newer formal truth.

<!-- forgeloop:anchor when-to-trigger -->
## When To Trigger

Trigger only in the following situations:
- the `Global State Doc` is missing, but rolling docs already exist
- the `Global State Doc` clearly conflicts with the total task doc or the rolling docs
- `code-loop` or a compatibility wrapper finds that the control plane cannot be recovered uniquely when binding an object
- the original thread cannot continue, but the formal docs and Git facts are still sufficient for recovery

This skill does not handle the following:
- a new Initiative cold start with no runtime docs at all
- cases that only need an implementation environment and should call skill: `using-git-worktrees`
- cases where the next step is already clear and recovery is unnecessary

<!-- forgeloop:anchor workflow -->
## Workflow

1. Bind the recovery surface
- Read `total_task_doc_ref` and the runtime cutover contract first, then read the existing `Global State Doc` and the three rolling docs through the mode-selected recovery path
- If the static truth sources are missing, or the Initiative binding cannot be confirmed uniquely, stop and ask the user
- If there is no rolling doc at all and no `Global State Doc`, treat it as a cold start, hand control back upstream, and do not write runtime state

2. Determine the current formal frontier
- First respect waiting / blocked / done signals that are consistent with the newer formal facts
- Prefer current-effective derived views only when they can still be rebuilt from the same authoritative rolling docs without legality drift; otherwise invalidate them and reread the formal rolling docs
- If a derived view is invalid, record whether the reason was newer formal blocks, multiple actionable results, handoff mismatch, or selector legality failure before promoting recovery
- Otherwise, use the newest formal frontier that has not yet closed as the active candidate
- If multiple candidates coexist, the fixed priority is: active Task repair / coder round > active Milestone review / repair > active Initiative review / repair > frontier selection after the last clean object
- Chat summaries, cache, and session memory never participate in adjudication

3. Determine the active object and next action
- Prefer the newest actionable block that already carries a legal literal `next_action`.
- Reuse `coder_slot` and `round` from the `Global State Doc` when they are still consistent; otherwise recover them from the active rolling doc.
- Apply this precedence:
  1. active Task
  2. active Milestone
  3. active Initiative
  4. frontier selection after the last clean object
- Within one plane, actionable reviewer output wins over coder output.
- For Initiative delivery, recover reviewer intent exactly: actionable `r3_result.next_action=mark_initiative_delivered` becomes dispatcher stop state `initiative_delivered`.
- A repair Task callback overrides ordinary frontier selection while that callback is still active.
- If no single plane, object, `coder_slot`, `round`, and `next_action` can be proven, stop and ask the user.

4. Rewrite the minimum control plane
- If the `Global State Doc` does not exist, initialize `global_state_header` first according to the canonical `Global State Doc` contract
- If the existing `global_state_header` conflicts with the Initiative binding or the `total_task_doc_ref`, correct `global_state_header` first according to the canonical `Global State Doc` contract
- Write `current_snapshot` as the uniquely recovered active plane / active object / `coder_slot` / object `round`, using the canonical `Global State Doc` contract
- Write `next_action` as the uniquely recovered next step, using the canonical runtime routing vocabulary from the `Global State Doc` contract
- Write `last_transition` as a recovery transition explaining why the control plane was rebuilt, using the canonical `Global State Doc` contract
- After writing, immediately hand control back to skill: `run-initiative` so the upstream dispatcher can reconfirm the recovered active plane and continue through `code-loop`

<!-- forgeloop:anchor stop-conditions -->
## Stop Conditions

Stop immediately and hand control back upstream or to the user when:
- the Initiative binding or static truth sources cannot be confirmed uniquely
- multiple active candidates coexist and Git / formal docs still cannot break the tie
- the rolling docs conflict with each other and it is impossible to tell which side is newer
- there are no runtime docs and the case should be handled as a cold start
- the facts show the system should wait for the user, but the waiting reason cannot be stated formally

<!-- forgeloop:anchor red-lines -->
## Red Lines

Never:
- write rolling doc body content
- recover a physical owner / thread id as formal state
- let an outdated `Global State Doc` override newer rolling-doc facts
- treat chat memory, cache, or local derived hints as formal truth sources
- silently guess the active object, `coder_slot`, or next action

<!-- forgeloop:anchor completion-criteria -->
## Completion Criteria

On correct completion, all of the following should be true:
- the current active plane, active object, active `round`, and `coder_slot` can be recovered uniquely
- the `Global State Doc` exists, and `current_snapshot`, `next_action`, and `last_transition` are self-consistent
- the upstream dispatcher can re-enter `run-initiative` and continue without hidden context
- no second runtime truth source has been created outside the four formal runtime surfaces
