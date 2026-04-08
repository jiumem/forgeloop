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
- one authoritative review rolling doc
- one current `review_handoff` in the current round when the object is at reviewer entry
- at most one `review_result` in the current round
- one `Global State Doc` materialization of reviewer entry
- one upstream dispatcher: `run-initiative`

`review rolling doc` carries only object identity, static review contract, and review-cycle truth. It does not carry coder progress logs, gate attempt ledgers, or runtime routing facts.

<!-- forgeloop:anchor mode-bindings -->
## Mode Bindings

<!-- forgeloop:anchor task-mode -->
### Task

- `active_plane`: `task`
- rolling doc contract: `plugins/forgeloop/skills/run-initiative/references/task-review-rolling-doc.md`
- reviewer: `task_reviewer`
- current handoff opener: latest `review_handoff` in the current Task round
- current review result: same-round `review_result`, when present
- supervisor default coder continuation action when no formal coder exit exists: `continue_coder_round`
- supervisor reviewer-entry materialization action: `enter_review`
- legal reviewer next actions:
  - `continue_task_repair`
  - `select_next_ready_object`
  - `task_done`
  - `escalate_to_milestone`
  - `wait_for_user`
  - `stop_on_blocker`

<!-- forgeloop:anchor milestone-mode -->
### Milestone

- `active_plane`: `milestone`
- rolling doc contract: `plugins/forgeloop/skills/run-initiative/references/milestone-review-rolling-doc.md`
- reviewer: `milestone_reviewer`
- current handoff opener: latest `review_handoff` in the current Milestone round
- current review result: same-round `review_result`, when present
- supervisor default coder continuation action when no formal coder exit exists: `continue_coder_round`
- supervisor reviewer-entry materialization action: `enter_review`
- legal reviewer next actions:
  - `continue_milestone_repair`
  - `enter_initiative_review`
  - `select_next_ready_object`
  - `wait_for_user`
  - `stop_on_blocker`

<!-- forgeloop:anchor initiative-mode -->
### Initiative

- `active_plane`: `initiative`
- rolling doc contract: `plugins/forgeloop/skills/run-initiative/references/initiative-review-rolling-doc.md`
- reviewer: `initiative_reviewer`
- current handoff opener: latest `review_handoff` in the current Initiative round
- current review result: same-round `review_result`, when present
- supervisor default coder continuation action when no formal coder exit exists: `continue_coder_round`
- supervisor reviewer-entry materialization action: `enter_review`
- legal reviewer next actions:
  - `continue_initiative_repair`
  - `mark_initiative_delivered`
  - `wait_for_user`
  - `stop_on_blocker`
- terminal review consequence: `mark_initiative_delivered`; dispatcher terminal stop state: `initiative_delivered`

<!-- forgeloop:anchor consumer-law -->
## Consumer Law

When `code-loop` binds one mode, it must then consume:

- the exact `next_action` semantics from the bound rolling-doc contract
- the runtime routing vocabulary from `plugins/forgeloop/skills/run-initiative/references/global-state.md`
- the exact judgment surface from the bound reviewer prompt

Do not create a second mode contract here by paraphrasing all legal `verdict + next_action` combinations.
