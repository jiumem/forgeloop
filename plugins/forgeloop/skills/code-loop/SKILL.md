---
name: code-loop
description: Unified runtime object loop. Use when one confirmed runtime object must continue in task, milestone, or initiative mode; this skill preserves one durable `coder_slot`, one object-local round, and one mode-specific review contract.
---

# Code Loop

<!-- forgeloop:anchor role -->
## Role

`code-loop` is the unified runtime-object executor under `run-initiative`.

You act as the runtime-object `Supervisor`: keep the minimum runtime control plane, preserve one durable `coder_slot`, dispatch the `coder`, dispatch the mode-bound reviewer, and route only within one currently bound runtime mode.

Supported modes:

- `task`
- `milestone`
- `initiative`

`code-loop` unifies the execution backbone. It does not erase mode-specific contracts.

You are not responsible for writing code, writing reviewer body content, or creating a second runtime truth source.

<!-- forgeloop:anchor mode-binding -->
## Mode Binding

The caller must bind exactly one `mode`:

- `task`
- `milestone`
- `initiative`

The bound mode determines:

- `current_snapshot.active_plane` legality
- the mode-specific rolling-doc contract ref
- the reviewer binding
- the gate-result block kind
- the current handoff opener and latest-matching-result law
- the legal same-object repair and upstream return semantics

Bind those mode-specific consumers from `references/runtime-object-modes.md`.

Do not infer mode semantics from memory or from examples when the bound mode reference and rolling-doc contract already exist.

<!-- forgeloop:anchor canonical-runtime-contract-refs -->
## Canonical Runtime Contract Refs

Always bind:

- `../run-initiative/references/global-state.md`
- `../run-initiative/references/runtime-cutover.md`
- `../references/anchor-addressing.md`
- `../references/derived-views.md`
- `references/runtime-object-modes.md`

Then bind the mode-specific rolling-doc contract ref named by `references/runtime-object-modes.md`.

<!-- forgeloop:anchor truth-sources-boundaries -->
## Truth Sources And Hard Boundaries

The formal input surface contains only the Initiative static truth trio `design_ref`, `gap_analysis_ref`, and `total_task_doc_ref` (`gap_analysis_ref` may be `N/A` for some Initiative types), the `Global State Doc`, the bound mode-specific review rolling doc, and the necessary Git / test / release facts.

Hard boundaries:

- `current_runtime_cutover_mode` must be bound before choosing the default read path
- the `Global State Doc` remains the only runtime-wide control spine
- the bound rolling doc remains the only object-local collaboration truth
- mode-specific `next_action`, handoff, review-result, and callback semantics stay defined by the bound rolling-doc contract, the `Global State Doc` contract, and the mode-bound reviewer prompt; do not restate them here as a parallel contract
- `request_reviewer_handoff` remains rolling-doc-local coder intent rather than a legal `Global State Doc.next_action.action`
- `round` is object-local and supervisor-owned through the `Global State Doc`; coder and reviewer only echo it in the rolling doc
- when the active object is already in flight, preserve `coder_slot` and `round`; only a fresh object with no rolling doc yet may initialize `coder_slot=coder` and `round=1`
- `coder_slot` is the only durable owner identity
- physical thread reuse is optional and carries no formal meaning
- all recovery must come from the current packet plus the bound formal docs, never from prior-thread memory as the only legality basis
- every `R1` / `R2` / `R3` entry must use a fresh reviewer for the current handoff
- if the `Global State Doc` conflicts with the bound rolling doc, hand control back to `rebuild-runtime`

<!-- forgeloop:anchor runtime.packet-law -->
## Runtime Worker Packet Law

Obey the shared packet law in `../references/anchor-addressing.md` and the runtime cutover law in `../run-initiative/references/runtime-cutover.md`.
Do not restate packet completeness, selector legality, or supervisor-doc exclusion here unless this file adds a true local exception.

Local exceptions for runtime worker packets:

- coder packets must additionally carry current `mode`, current `round`, current `coder_slot`, and callback metadata when this is an objectized repair Task
- reviewer packets must additionally carry the current handoff tuple: `round`, `handoff_id`, and `review_target_ref`

<!-- forgeloop:anchor workflow -->
## Workflow

1. Bind the current object and mode
- First bind `current_runtime_cutover_mode`.
- Follow the mode-selected read order defined by `../run-initiative/references/runtime-cutover.md`; use `../references/derived-views.md` only for legal hot-path helpers.
- Confirm one active Initiative and one active runtime object uniquely.
- Confirm that the bound `mode` matches `current_snapshot.active_plane`, unless this is a fresh object entry being initialized now.
- Bind the mode-specific rolling-doc contract ref, reviewer, gate block kind, and current handoff law from `references/runtime-object-modes.md`.
- Confirm the active rolling doc matches the bound object and the recovered `coder_slot` / `round`.

2. Recover or initialize the object-local collaboration surface
- If the rolling doc exists, recover the current handoff and latest actionable result from the authoritative rolling doc or legal derived views.
- If the rolling doc does not exist, initialize only the legal header and contract snapshot for the bound mode, then write `coder_slot=coder` and `round=1` through the canonical `Global State Doc` rules before dispatching the first coder round.
- Do not append fake gate blocks, fake handoff blocks, or fake review blocks during cold start.

3. Dispatch the coder
- Keep one durable `coder_slot`.
- Preserve the same `coder_slot` across rounds unless the runtime control plane has formally rebound ownership.
- The coder packet must carry:
  - Initiative static truth refs
  - `Global State Doc`
  - the active mode-specific rolling doc
  - current `mode`
  - current `round`
  - current `coder_slot`
  - the exact selectors required for this object and round
  - callback metadata when this is an objectized repair Task

4. Handle the gate result
- Read only the latest gate result for the current round that is legal for the bound mode.
- If the gate result requests in-mode repair, stay in the same mode and same round when the bound contracts allow it.
- If the gate result opens reviewer entry, require one valid current handoff first, then materialize reviewer entry in the `Global State Doc`.
- If the gate result requests waiting or blocker, write the stop state and return upstream.
- Any illegal gate-result / handoff combination is a formal stop.

5. Dispatch the mode-specific reviewer
- Bind the reviewer from `references/runtime-object-modes.md`.
- Every review entry uses a freshly spawned reviewer for the current handoff.
- Every review entry uses the current handoff tuple:
  - `round`
  - `handoff_id`
  - `review_target_ref`
- Derived views are optional hot-path helpers only.

6. Handle the review result
- Use only the latest matching review result for the current handoff.
- If the result requests same-object repair, increment the object-local `round`, preserve `coder_slot`, and continue in the same mode.
- If the result requests upstream return, rebind `current_snapshot` and `next_action` according to the bound mode contracts, then hand control back upstream.
- If the result requests objectized repair Task detour, write callback metadata into `last_transition` using the bound callback-round law from `references/runtime-object-modes.md`, switch control back to Task plane, then hand control back upstream.
- If the result requests terminal delivery marking, accept only the Initiative-mode legal terminal transition.
- Any illegal `verdict + next_action` combination is a formal stop.

7. Return upstream

`code-loop` never decides the next runtime object beyond the current formal result.

After one legal object-local conclusion is written, return to `run-initiative` for the next dispatch decision.

<!-- forgeloop:anchor stop-conditions -->
## Stop Conditions

Stop immediately and hand control back upstream or to the user when:

- the active Initiative cannot be confirmed uniquely
- the active object cannot be confirmed uniquely
- the bound `mode` cannot be confirmed uniquely
- the `Global State Doc` conflicts with the mode-specific rolling doc
- the current handoff cannot be recovered uniquely
- the latest actionable review result cannot be recovered uniquely
- the coder or reviewer exposes a real blocker
- the shared packet law or bound runtime cutover mode makes the current read surface illegal and does not allow fallback

<!-- forgeloop:anchor red-lines -->
## Red Lines

Never:

- write coder or reviewer body content into the `Global State Doc`
- dispatch multiple coders concurrently for the same runtime object
- silently replace the logical `coder_slot`
- skip the mode-required gate -> handoff -> review path
- invent a mode-specific action not defined by the bound contracts
- create a second runtime truth source outside the `Global State Doc` and the authoritative rolling docs
- persist decisions that depend only on a derived view without the authoritative ref basis

<!-- forgeloop:anchor completion-criteria -->
## Completion Criteria

On correct completion, all of the following should be true:

- one Initiative is bound uniquely
- one runtime object and one `mode` are bound uniquely
- `coder_slot` continuity is unambiguous
- object-local `round` continuity is unambiguous
- the current handoff and latest actionable review result can be recovered uniquely
- the mode-specific gate / handoff / review chain remains contract-correct
- no second runtime truth source has been created
