---
name: code-loop
description: Unified runtime executor. Use when one confirmed runtime object must continue under a bound `mode` of `task`, `milestone`, or `initiative`; this skill owns the full object-local dispatch backbone.
---

# Code Loop

<!-- forgeloop:anchor role -->
## Role

`code-loop` is the only runtime loop executor under `run-initiative`.

The caller binds exactly one runtime `mode`, and `code-loop` then owns the full object-local supervision for that mode: recovery, collaboration-surface initialization, coder dispatch, reviewer dispatch, review-result handling, and object-local round progression.

Supported modes:

- `task`
- `milestone`
- `initiative`

`code-loop` unifies execution law while consuming mode-specific contracts from bound references. It is not a wrapper, and it is not a second dispatcher.

You are not responsible for writing code, writing reviewer body content, or creating a second runtime truth source.

<!-- forgeloop:anchor canonical-runtime-contract-refs -->
## Canonical Runtime Contract Refs

Always bind:

- `plugins/forgeloop/skills/run-initiative/references/global-state.md`
- `plugins/forgeloop/skills/run-initiative/references/runtime-cutover.md`
- `plugins/forgeloop/skills/references/anchor-addressing.md`
- `plugins/forgeloop/skills/references/derived-views.md`
- `plugins/forgeloop/skills/code-loop/references/runtime-object-modes.md`

Then bind the mode-specific rolling-doc contract named by `plugins/forgeloop/skills/code-loop/references/runtime-object-modes.md`.

<!-- forgeloop:anchor truth-sources-boundaries -->
## Truth Sources And Hard Boundaries

The formal input surface contains only the Initiative static truth trio, the `Global State Doc`, the bound mode-specific review rolling doc, and the necessary Git / test / release facts.

Obey the shared packet law in `plugins/forgeloop/skills/references/anchor-addressing.md` and the runtime cutover law in `plugins/forgeloop/skills/run-initiative/references/runtime-cutover.md`.

Hard boundaries:

- the `Global State Doc` remains the only runtime-wide control spine
- the bound review rolling doc remains the only object-local review truth
- review rolling docs carry only object identity, static contract, and review-cycle truth: `review_header`, `review_contract_snapshot`, `review_handoff`, and `review_result`
- coder progress logs and gate attempt ledgers do not belong in review rolling docs
- `round` is object-local and supervisor-owned through the `Global State Doc`; coder and reviewer only echo it in the rolling doc
- preserve `coder_slot` and `round` while the same object remains active
- each runtime `mode` may keep one session-local reusable reviewer binding for the current loop; that binding never becomes formal truth
- if the `Global State Doc` conflicts with the bound rolling doc, hand control back to `rebuild-runtime`
- prior-thread memory is never a legality basis by itself
- before entering `code-loop`, the caller must already bind the concrete active review rolling doc ref for the current object; `code-loop` consumes that bound ref and does not search a review-doc root to guess one

<!-- forgeloop:anchor workflow -->
## Workflow

1. Bind the current object and mode
- First bind `current_runtime_cutover_mode`.
- Follow the mode-selected read order defined by `plugins/forgeloop/skills/run-initiative/references/runtime-cutover.md`; use `plugins/forgeloop/skills/references/derived-views.md` only for legal hot-path helpers.
- Confirm one active Initiative and one active runtime object uniquely.
- Confirm that the bound `mode` matches `current_snapshot.active_plane`, unless this is a fresh object entry being initialized now.
- Confirm the active rolling doc matches the bound object and the recovered `coder_slot` / `round`.

2. Recover or initialize the review surface
- If the rolling doc exists, recover the latest round's `review_handoff` and same-round `review_result` from the authoritative rolling doc or legal derived views.
- If the rolling doc does not exist, initialize only the legal header and contract snapshot for the bound mode, then write `coder_slot=coder` and `round=1` through the canonical `Global State Doc` rules before dispatching the first coder round.
- Do not append fake handoff or review-result blocks during cold start.

3. Determine the current object-local frontier
- If the current round already exposes one legal `review_handoff` and no matching `review_result`, do not redispatch `coder`; dispatch the reviewer directly.
- If the current round already exposes one matching `review_result`, do not redispatch `coder`; handle that review result directly.
- Otherwise continue with coder dispatch for the current round.
- If the current round exposes more than one legal `review_handoff`, or more than one legal same-round matching `review_result`, stop and surface the formal-state conflict explicitly.

4. Dispatch the `coder`
- Keep one durable `coder_slot`.
- For the current runtime session, keep at most one reusable `coder` binding and one reusable `reviewer` binding for the bound `mode`.
- If the bound `coder` already has a live `agent_id` in this session, reuse it with `send_input`; do not call `spawn_agent` again for the same live coder binding.
- Only when the bound mode has no usable coder binding, or the old coder binding is known closed, dead, or unrecoverable, may the supervisor create or rebind that worker with `spawn_agent`.
- The coder packet must carry:
  - Initiative static truth refs
  - `Global State Doc`
  - the active mode-specific review rolling doc
  - current `mode`
  - current `round`
  - current `coder_slot`
  - the exact selectors required for this object and round

5. Handle coder return
- If the current round now exposes one legal `review_handoff` and no `review_result`, materialize reviewer entry in the `Global State Doc`.
- If the current round still exposes neither `review_handoff` nor `review_result`, keep the object in coder mode.
- Treat coder natural-language completion as non-authoritative until the expected `review_handoff` can be reread from the authoritative rolling doc and the reviewer-entry materialization can be written legally.
- Do not synthesize a canonical stop state from coder natural-language status alone. Runtime stop literals belong in the `Global State Doc` only when they already exist as explicit upstream control decisions or when they are required by a legal `review_result.next_action`.
- Any illegal duplicate handoff or duplicate result is a formal stop.

6. Dispatch the mode-specific reviewer
- Bind the reviewer from `references/runtime-object-modes.md`.
- Reuse the current mode's reviewer binding with `send_input` when it still has a live `agent_id` in this session; otherwise create or rebind exactly one reviewer for this mode with `spawn_agent`.
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
- Treat reviewer `next_action` as canonical runtime control input for the current object-local conclusion.
- Materialize reviewer output directly into the `Global State Doc`.

Task mode:
- `continue_coder_round` -> keep the current Task bound, increment the Task round, keep the same `coder_slot`, write `next_action.action=continue_coder_round`, then return upstream
- `advance_frontier` -> move to `active_plane=frontier`, clear concrete Task execution fields, write `next_action.action=advance_frontier`, then return upstream
- `wait_for_user` -> write `next_action.action=wait_for_user`, then return upstream
- `stop_on_blocker` -> write `next_action.action=stop_on_blocker`, then return upstream

Milestone mode:
- `continue_coder_round` -> keep the current Milestone bound, increment the Milestone round, keep the same `coder_slot`, write `next_action.action=continue_coder_round`, then return upstream
- `advance_frontier` -> move to `active_plane=frontier`, clear concrete Milestone execution fields except any still-legal frontier constraint, write `next_action.action=advance_frontier`, then return upstream
- `wait_for_user` -> write `next_action.action=wait_for_user`, then return upstream
- `stop_on_blocker` -> write `next_action.action=stop_on_blocker`, then return upstream

Initiative mode:
- `continue_coder_round` -> keep the current Initiative bound, increment the Initiative round, keep the same `coder_slot`, write `next_action.action=continue_coder_round`, then return upstream
- `initiative_delivered` -> keep Initiative delivered-stop snapshot shape legal, write `next_action.action=initiative_delivered`, then return upstream
- `wait_for_user` -> write `next_action.action=wait_for_user`, then return upstream
- `stop_on_blocker` -> write `next_action.action=stop_on_blocker`, then return upstream

- Do not call planning skills from here.
- Do not regenerate Task plans from reviewer output.
- Do not create a new runtime object inside `code-loop`.
- Any illegal `verdict + next_action` combination is a formal stop.

8. Return upstream

`code-loop` never decides the next runtime object beyond the current formal result.

After one legal object-local conclusion is written, return to `run-initiative` for the next dispatch decision.

<!-- forgeloop:anchor stop-conditions -->
## Stop Conditions

Stop immediately and hand control back upstream or to the user when:

- the active Initiative cannot be confirmed uniquely
- the active object cannot be confirmed uniquely
- the bound `mode` cannot be confirmed uniquely
- the `Global State Doc` conflicts with the mode-specific rolling doc
- the current round exposes more than one `review_handoff`
- the current round exposes more than one `review_result`
- an explicit canonical stop state has already been entered in the `Global State Doc`
- the shared packet law or bound runtime cutover mode makes the current read surface illegal and does not allow fallback

<!-- forgeloop:anchor red-lines -->
## Red Lines

Never:

- write coder or reviewer body content into the `Global State Doc`
- dispatch multiple coders concurrently for the same runtime object
- silently replace the logical `coder_slot`
- persist any physical `agent_id`, reviewer binding, or session-local thread table into formal runtime truth
- skip the round-required handoff -> review path once a handoff exists
- invent a mode-specific action not defined by the bound contracts
- create a second runtime truth source outside the `Global State Doc` and the authoritative rolling docs

<!-- forgeloop:anchor completion-criteria -->
## Completion Criteria

On correct completion, all of the following should be true:

- one Initiative is bound uniquely
- one runtime object and one `mode` are bound uniquely
- `coder_slot` continuity is unambiguous
- session-local reviewer reuse, when present, remains invisible to formal truth
- object-local `round` continuity is unambiguous
- the current round's `review_handoff` and `review_result` can be recovered uniquely when they exist
- the mode-specific review chain remains contract-correct
- no second runtime truth source has been created
