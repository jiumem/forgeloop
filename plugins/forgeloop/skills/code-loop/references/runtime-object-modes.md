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
- one session-local reusable `coder` binding for the currently bound `mode`
- one session-local reusable `reviewer` binding for the currently bound `mode`
- one supervisor-owned object-local `round`
- one authoritative review rolling doc
- one current coder intent from the latest `coder_update` in the current round when present
- one current `review_handoff` in the current round when the object is at reviewer entry
- at most one `review_result` in the current round
- one `Global State Doc` materialization of reviewer entry
- one upstream dispatcher: `run-initiative`

These per-mode session-local bindings are runtime-private only. They may be recreated after session loss and must never be written into the `Global State Doc` or the rolling docs.

The bound Task / Milestone / Initiative review rolling doc carries only object identity, static review contract, and review-cycle truth. It does not carry coder progress logs, gate attempt ledgers, or runtime routing facts.

<!-- forgeloop:anchor shared-runtime-author-intent-law -->
## Shared Runtime Author-Intent Law

Across `task`, `milestone`, and `initiative` modes:

- current coder intent: the latest `coder_update` in the current round, when present
- current handoff opener: the current round's `review_handoff`, when present
- current review result: the current round's `review_result`, when present

Legal coder-local `next_action` values:

- `continue_local_repair`
- `request_reviewer_handoff`
- `wait_for_user`
- `stop_on_blocker`

Law:

- reviewer entry is legal only when the current round exposes one legal `review_handoff`
- that `review_handoff` must be opened by the latest current-round `coder_update.next_action=request_reviewer_handoff`
- reviewer outputs still use the canonical runtime routing vocabulary from `global-state.md`
- `code-loop` must not invent a second runtime dispatcher vocabulary here

<!-- forgeloop:anchor mode-bindings -->
## Mode Bindings

<!-- forgeloop:anchor task-mode -->
### Task

- `active_plane`: `task`
- rolling doc contract: `plugins/forgeloop/skills/run-initiative/references/task-review-rolling-doc.md`
- reviewer: `task_reviewer`
- current handoff opener: the current round's `review_handoff`, when present
- current review result: same-round `review_result`, when present
- supervisor default coder continuation action when no formal coder exit exists: `continue_coder_round`
- supervisor reviewer-entry materialization action: `enter_review`
- legal reviewer next actions:
  - `continue_coder_round`
  - `advance_frontier`
  - `wait_for_user`
  - `stop_on_blocker`
- reviewer materialization:
  - `continue_coder_round` -> `continue_coder_round`
  - `advance_frontier` -> `advance_frontier`
  - `wait_for_user` -> `wait_for_user`
  - `stop_on_blocker` -> `stop_on_blocker`

<!-- forgeloop:anchor milestone-mode -->
### Milestone

- `active_plane`: `milestone`
- rolling doc contract: `plugins/forgeloop/skills/run-initiative/references/milestone-review-rolling-doc.md`
- reviewer: `milestone_reviewer`
- current handoff opener: the current round's `review_handoff`, when present
- current review result: same-round `review_result`, when present
- supervisor default coder continuation action when no formal coder exit exists: `continue_coder_round`
- supervisor reviewer-entry materialization action: `enter_review`
- legal reviewer next actions:
  - `continue_coder_round`
  - `advance_frontier`
  - `wait_for_user`
  - `stop_on_blocker`
- reviewer materialization:
  - `continue_coder_round` -> `continue_coder_round`
  - `advance_frontier` -> `advance_frontier`
  - `wait_for_user` -> `wait_for_user`
  - `stop_on_blocker` -> `stop_on_blocker`

<!-- forgeloop:anchor initiative-mode -->
### Initiative

- `active_plane`: `initiative`
- rolling doc contract: `plugins/forgeloop/skills/run-initiative/references/initiative-review-rolling-doc.md`
- reviewer: `initiative_reviewer`
- current handoff opener: the current round's `review_handoff`, when present
- current review result: same-round `review_result`, when present
- supervisor default coder continuation action when no formal coder exit exists: `continue_coder_round`
- supervisor reviewer-entry materialization action: `enter_review`
- legal reviewer next actions:
  - `continue_coder_round`
  - `initiative_delivered`
  - `wait_for_user`
  - `stop_on_blocker`
- reviewer materialization:
  - `continue_coder_round` -> `continue_coder_round`
  - `initiative_delivered` -> `initiative_delivered`
  - `wait_for_user` -> `wait_for_user`
  - `stop_on_blocker` -> `stop_on_blocker`

<!-- forgeloop:anchor consumer-law -->
## Consumer Law

When `code-loop` binds one mode, it must consume:

- the bound rolling-doc contract as the canonical reviewer-output contract for that mode
- the canonical runtime routing vocabulary from `plugins/forgeloop/skills/run-initiative/references/global-state.md`
- the exact judgment surface from the bound reviewer prompt

`code-loop` may materialize reviewer `next_action` values directly into the `Global State Doc` because both surfaces now share one runtime vocabulary.

`enter_review` remains supervisor-only state materialization for handoff entry and is not a legal reviewer output.

Do not create a second mode contract here by paraphrasing separate per-mode dispatcher vocabularies.
