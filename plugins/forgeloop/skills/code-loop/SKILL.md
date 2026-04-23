---
name: code-loop
description: Unified runtime executor. Use when one confirmed runtime object must continue under a bound object kind of `task`, `milestone`, or `initiative`; this skill owns the full object-local dispatch backbone.
---

# Code Loop

`code-loop` is the only runtime execution loop.

You act as the runtime `Supervisor` for exactly one currently bound runtime object.
The bound object may be a `task`, `milestone`, or `initiative`.
This skill does not define runtime hierarchy and does not persist `frontier`.

If the current object should continue same-object repair or review, keep the same object.
If object-local execution proves that the current object should no longer remain active, record only the release fact in `last_transition` and stop.
Do not prebind, persist, or imply the next object here.
The caller must reread formal runtime truth and use `runtime-object-selection.md` before any object change becomes effective.

<!-- forgeloop:anchor canonical-runtime-contract-refs -->
## Canonical Runtime Contract Refs

Always bind:

- `plugins/forgeloop/skills/run-initiative/references/global-state.md`
- `plugins/forgeloop/skills/run-initiative/references/runtime-cutover.md`
- `plugins/forgeloop/skills/references/anchor-addressing.md`
- `plugins/forgeloop/skills/references/derived-views.md`
- `plugins/forgeloop/skills/code-loop/references/runtime-object-modes.md`

Then bind the object-kind-specific rolling-doc contract named by `plugins/forgeloop/skills/code-loop/references/runtime-object-modes.md`.

<!-- forgeloop:anchor truth-sources-boundaries -->
## Truth Sources And Hard Boundaries

The formal input surface contains only the Initiative static truth trio, the `Global State Doc`, the bound object-local review rolling doc, and the necessary Git / test / release facts.

Obey the shared packet law in `plugins/forgeloop/skills/references/anchor-addressing.md` and the runtime cutover law in `plugins/forgeloop/skills/run-initiative/references/runtime-cutover.md`.

Hard boundaries:

- the `Global State Doc` remains the only runtime-wide control spine
- the bound review rolling doc remains the only object-local review truth
- review rolling docs carry only object identity, static contract, and review-cycle truth
- preserve `coder_slot` and `round` while the same object remains active
- each runtime object kind may keep one session-local reusable reviewer binding for the current loop; that binding never becomes formal truth
- if the `Global State Doc` conflicts with the bound rolling doc, hand control back to `rebuild-runtime`
- prior-thread memory is never a legality basis by itself
- before entering `code-loop`, the caller must already bind the concrete active review rolling doc ref for the current object

<!-- forgeloop:anchor delegation-context-isolation -->
## Delegation Context Isolation

Coder and reviewer agents must not inherit the runtime `Supervisor` conversation context.
The supervisor's context is routing state only; it is not an authoritative worker packet and must not be silently transferred to workers.

When creating a coder or reviewer with `spawn_agent`, set `fork_context=false`.
The created worker must receive only the explicit packet assembled for that role, including the bound refs, selectors, current round, active workspace, and role-specific instructions.

When reusing a live worker with `send_input`, send a complete explicit continuation packet for the current decision point.
Do not rely on the worker remembering prior hidden supervisor context, previous packet state, or informal narration.

If the environment cannot create or reuse workers without inheriting supervisor context, stop and surface that as a delegation blocker instead of dispatching a contaminated worker.

<!-- forgeloop:anchor workflow -->
## Workflow

1. Bind the current object
- Read the runtime cutover contract first and bind `current_runtime_cutover_mode`.
- Follow the bound read order and use derived views only as legal hot-path helpers.
- Confirm one active Initiative and one active runtime object uniquely.
- Confirm the active rolling doc matches the bound object and the recovered `coder_slot` / `round`.

2. Recover or initialize the review surface
- If the rolling doc exists, recover the latest current-round `coder_update`, the current round's `review_handoff`, and the same-round `review_result` from the authoritative rolling doc or legal derived views.
- If the rolling doc does not exist, initialize only the legal header and contract snapshot for the bound object kind, then write `coder_slot=coder` and `round=1` through the canonical `Global State Doc` rules before dispatching the first coder round.
- Do not append fake `coder_update`, `review_handoff`, or `review_result` blocks during cold start.

3. Determine the current object-local round state
- object-local round state means only the current object's in-round repair, review handoff, or review-result position.
- It is never a persisted runtime object, never a `current_snapshot` value, and never a substitute for dispatcher-side object selection.
- If the current round already exposes one matching current `review_result`, do not redispatch `coder`; handle that review result directly.
- If the current round exposes one legal `review_handoff`, dispatch the current reviewer directly.
- Otherwise dispatch `coder` for the current round.
- If the current round exposes more than one legal `review_handoff` or more than one legal matching current `review_result`, stop and surface the rolling-doc contract violation explicitly.

4. Dispatch the `coder`
- Keep one durable `coder_slot`.
- For the current runtime session, keep at most one reusable `coder` binding and one reusable `reviewer` binding for the bound object kind.
- If the bound `coder` already has a live `agent_id` in this session, reuse it with `send_input`; do not call `spawn_agent` again for the same live coder binding.
- Only when the bound object kind has no usable coder binding, or the old coder binding is known closed, dead, or unrecoverable, may the supervisor create or rebind that worker with `spawn_agent`.
- The coder packet must carry:
  - Initiative static truth refs
  - `Global State Doc`
  - the active object-local review rolling doc
  - current object kind
  - current `round`
  - current `coder_slot`
  - the exact selectors required for this object and round

5. Handle coder output
- Treat coder natural-language completion as non-authoritative until the expected `coder_update` or `review_handoff` can be reread from the authoritative rolling doc and the required control-plane materialization can be written legally.
- If the current round remains in same-object coder work, keep the same current object and return upstream only when the control plane has been materialized.
- If coder output opens reviewer entry, require one legal current `review_handoff` in the same round, then continue to Step 6 using that handoff.
- If coder output requests `wait_for_user` or `stop_on_blocker`, materialize the corresponding canonical stop state and stop.

6. Dispatch the reviewer
- Bind the reviewer from `references/runtime-object-modes.md`.
- Reuse the current object kind's reviewer binding with `send_input` when it still has a live `agent_id` in this session; otherwise create or rebind exactly one reviewer for this object kind with `spawn_agent`.
- Reviewer packets must carry:
  - `round`
  - `review_target_ref`
  - `compare_base_ref`
  - the object-local selectors required by the bound reviewer contract
  - the exact prior reviewer judgment referenced by `addresses_review_result_id`, when present
- Derived views are optional hot-path helpers only.
- Reviewer legality must always come from the current packet, rolling doc, and formal refs, not from prior thread memory.

7. Handle the review result
- Use only the latest current-round `review_result` whose `review_target_ref` matches the current handoff.
- Treat reviewer natural-language completion as non-authoritative until the expected `review_result` can be reread from the authoritative rolling doc and any required `Global State Doc` rewrite has succeeded.

When handling reviewer output:

- `continue_coder_round`
  - keep the same current object
  - increment round when the review contract requires a new round
  - continue in the same object

- `advance_frontier`
  - do not materialize `frontier`
  - write only a runtime object release fact into `last_transition`
  - stop and hand control back to `run-initiative`

- `wait_for_user`
  - materialize `waiting`
  - stop

- `stop_on_blocker`
  - materialize `blocked`
  - stop

- `initiative_delivered`
  - legal only when the current object kind is `initiative`
  - materialize `initiative_delivered`
  - stop

8. Return upstream

After one legal object-local conclusion is written, return to `run-initiative` for the next selection or stop decision.

<!-- forgeloop:anchor red-lines -->
## Red Lines

Never:

- persist `frontier`
- invent a second runtime hierarchy here
- force runtime to stay on the same object when the dispatcher has already rebound a new current object inside the same sealed execution map
- reinterpret PR packaging as runtime object truth
