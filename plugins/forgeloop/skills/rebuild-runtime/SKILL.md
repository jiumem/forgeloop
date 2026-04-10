---
name: rebuild-runtime
description: Use when the runtime control plane is missing, conflicting, or cannot uniquely recover the next step; this skill reads the static truth sources, the Global State Doc, review rolling docs, and necessary Git facts to rebuild the minimum control plane needed to continue dispatch
---

# Rebuild Runtime

<!-- forgeloop:anchor role -->
`rebuild-runtime` does recovery only. It does not code, it does not review, and it does not replace `run-initiative` for ongoing dispatch. Here you act as a recovery-state `Supervisor`: rebuild the minimum runnable control plane from the formal truth sources and engineering facts, then hand the system back upstream.

<!-- forgeloop:anchor canonical-runtime-contract-refs -->
## Canonical Runtime Contract Refs

Always bind:

- `plugins/forgeloop/skills/run-initiative/references/global-state.md`
- `plugins/forgeloop/skills/run-initiative/references/runtime-cutover.md`
- `plugins/forgeloop/skills/run-initiative/references/runtime-object-selection.md`
- `plugins/forgeloop/skills/code-loop/references/runtime-object-modes.md`
- `plugins/forgeloop/skills/references/anchor-addressing.md`
- `plugins/forgeloop/skills/references/derived-views.md`

Then bind the object-kind-specific rolling-doc contract named by `plugins/forgeloop/skills/code-loop/references/runtime-object-modes.md`.

<!-- forgeloop:anchor truth-sources-boundaries -->
## Truth Sources And Hard Boundaries

The formal input surface contains only the Initiative static truth trio, the `Global State Doc`, the object-local review rolling docs, and the necessary Git / PR / commit / test facts.

Hard boundaries:

- recover only the logical `coder_slot`, never the physical `agent_id`
- do not attempt to recover any reviewer binding or session-local thread table as formal state
- recover the current object-local `round`, never invent a new round
- write to the `Global State Doc` only when necessary
- the only updatable blocks are `runtime_state_header`, `current_snapshot`, `next_action`, and `last_transition`
- do not write any rolling doc body content
- do not modify the static truth sources and do not create a second state model in JSON / notes / hidden memory

<!-- forgeloop:anchor workflow -->
## Workflow

1. Bind the current Initiative and recover one legal current runtime object
- First bind the active Initiative and prove that runtime admission is still legal.
- If `Global State Doc` already binds one legal current object, recover that object first.
- If the persisted control state is missing, stale, conflicting, or still exposes `frontier`, do not invent a second recovery hierarchy.
- Use `plugins/forgeloop/skills/run-initiative/references/runtime-object-selection.md` as the only legal selector for recovering one current runtime object.
- Recover exactly one `active_object_kind`, one `active_object_key`, one `rolling_doc_ref`, and when recoverable one `coder_slot` plus one `round`.
- If exactly one legal current runtime object cannot be recovered, stop and hand control back upstream.

2. Recover current object-local formal state
- Read `runtime-cutover.md` first and bind `current_runtime_cutover_mode`.
- Read the bound object-local rolling doc through the runtime cutover law and shared packet law.
- Recover the latest current-round `coder_update`, the current round's `review_handoff`, and the same-round `review_result` when present.
- If a round exposes duplicate `review_handoff` or duplicate `review_result`, stop and surface the illegal state explicitly.
- Recover only from formal runtime truth. Workspace diff, chat summaries, and interrupted worker intent may help explain what happened, but they must never promote object progression without a rereadable formal block.

3. Recover the current runtime route
- Respect canonical stop literals `waiting`, `blocked`, and `initiative_delivered` when they are still consistent with newer formal facts.
- If the current round has a `review_result`, recover the next control state from that result using `plugins/forgeloop/skills/code-loop/references/runtime-object-modes.md`.
- If the current round has a `review_handoff` and no `review_result`, preserve the current object and recover in-object review entry.
- If the current round has no `review_handoff` and no `review_result`, preserve the current object and recover in-object coder continuation.
- If the current round has no formal `coder_update`, `review_handoff`, or `review_result`, recover coder continuation from the last legal formal state instead of inventing a new object.

4. Rewrite the minimum control plane
- If the `Global State Doc` does not exist, initialize `runtime_state_header` first according to the canonical contract.
- Write `current_snapshot` as the uniquely recovered active object, `rolling_doc_ref`, `coder_slot`, and object-local `round`.
- Write `next_action` as the uniquely recovered next step.
- Write `last_transition` as a recovery transition explaining why the control plane was rebuilt, and classify the cause in `last_transition.reason` using the smallest fitting class.
- After writing, immediately hand control back to skill: `run-initiative`.

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
- recover or persist `frontier` as the active runtime object

<!-- forgeloop:anchor completion-criteria -->
## Completion Criteria

On correct completion, all of the following should be true:

- the current active object, active `round`, and `coder_slot` can be recovered uniquely
- the `Global State Doc` exists, and `current_snapshot`, `next_action`, and `last_transition` are self-consistent
- the upstream dispatcher can re-enter `run-initiative` and continue without hidden context
- no second runtime truth source has been created outside the `Global State Doc` plus the object-local review rolling docs
