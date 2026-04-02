# Runtime Object Modes Reference

This reference is the only mode-local binding surface for `code-loop`.

It replaces compatibility wrappers such as `task-loop`, `milestone-loop`, and `initiative-loop`.
When `run-initiative` binds one runtime `mode`, `code-loop` must consume this file directly rather than entering a second wrapper skill.

This file binds mode-local differences only. It does not create a second dispatcher, a second recovery layer, or a second routing vocabulary.

<!-- forgeloop:anchor shared-backbone -->
## Shared Backbone

All runtime object modes share the same supervisor backbone:

- one uniquely bound active object
- one logical `coder_slot`
- one supervisor-owned object-local `round`
- one authoritative rolling doc
- one current handoff tuple
- one latest matching review result
- one `Global State Doc` materialization of reviewer entry
- one upstream dispatcher: `run-initiative`

`request_reviewer_handoff` is never a legal `Global State Doc.next_action.action`.

After a valid current handoff exists, runtime reviewer entry is materialized as `enter_r1`, `enter_r2`, or `enter_r3`.

This reference binds mode consumers. It does not redefine the legal runtime vocabulary or reviewer judgment contracts.

<!-- forgeloop:anchor mode-bindings -->
## Mode Bindings

<!-- forgeloop:anchor task-mode -->
### Task

- `active_plane`: `task`
- rolling doc contract: `../../run-initiative/references/task-review-rolling-doc.md`
- reviewer: `task_reviewer`
- gate-result block kind: `g1_result`
- current handoff opener: latest `anchor_ref` or `fixup_ref` in the current round
- current review result: latest matching `r1_result` for that handoff
- common Task entry and reviewer actions remain `continue_task_coder_round` and `enter_r1`

<!-- forgeloop:anchor milestone-mode -->
### Milestone

- `active_plane`: `milestone`
- rolling doc contract: `../../run-initiative/references/milestone-review-rolling-doc.md`
- reviewer: `milestone_reviewer`
- gate-result block kind: `g2_result`
- current handoff opener: latest `g2_result` in the current round whose `next_action=enter_r2`
- current review result: latest matching `r2_result` for that handoff

<!-- forgeloop:anchor initiative-mode -->
### Initiative

- `active_plane`: `initiative`
- rolling doc contract: `../../run-initiative/references/initiative-review-rolling-doc.md`
- reviewer: `initiative_reviewer`
- gate-result block kind: `g3_result`
- current handoff opener: latest `g3_result` in the current round whose `next_action=enter_r3`
- current review result: latest matching `r3_result` for that handoff
- terminal review consequence: `mark_initiative_delivered`; dispatcher terminal stop state: `initiative_delivered`

<!-- forgeloop:anchor consumer-law -->
## Consumer Law

When `code-loop` binds one mode, it must then consume:

- the exact `next_action` and callback semantics from the bound rolling-doc contract
- the runtime routing vocabulary from `../../run-initiative/references/global-state.md`
- the exact judgment surface from the bound reviewer prompt

Do not create a second mode contract here by paraphrasing all legal `verdict + next_action` combinations.

<!-- forgeloop:anchor callback-round-law -->
## Callback Round Law

When Milestone or Initiative work objectizes a repair Task, `code-loop` and `rebuild-runtime` must bind `callback_round_behavior` from the source formal block kind:

- gate-side objectization from actionable `g2_result` or `g3_result` -> `continue_current_round`
- review-side objectization from actionable `r2_result` or `r3_result` -> `enter_next_round`

Do not infer callback round behavior from prose summaries when the source block kind is available.
