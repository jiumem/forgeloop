# Runtime Object Bindings Reference

<!-- forgeloop:anchor document-role -->
## Document Role

- Plane: runtime object-local binding contract
- Applies to: `code-loop`
- Primary readers: runtime `Supervisor`
- Primary purpose: bind one runtime object kind to its rolling-doc contract, reviewer role, and reviewer-output materialization law

This file binds object-local review surfaces only.
It does not define runtime hierarchy, wrapper law, or next-object selection.
Those belong only to `plugins/forgeloop/skills/run-initiative/references/runtime-object-selection.md`.

<!-- forgeloop:anchor task-kind -->
## Task

- `active_object_kind`: `task`
- rolling doc contract: `plugins/forgeloop/skills/run-initiative/references/task-review-rolling-doc.md`
- reviewer: `task_reviewer`
- current handoff opener: the current round's `review_handoff`, when present
- current review result: same-round `review_result`, when present
- legal reviewer next actions:
  - `continue_coder_round`
  - `advance_frontier`
  - `wait_for_user`
  - `stop_on_blocker`
- reviewer materialization:
  - `continue_coder_round` -> `continue_same_object`
  - `advance_frontier` -> `advance_to_next_object`
  - `wait_for_user` -> `waiting`
  - `stop_on_blocker` -> `blocked`

<!-- forgeloop:anchor milestone-kind -->
## Milestone

- `active_object_kind`: `milestone`
- rolling doc contract: `plugins/forgeloop/skills/run-initiative/references/milestone-review-rolling-doc.md`
- reviewer: `milestone_reviewer`
- current handoff opener: the current round's `review_handoff`, when present
- current review result: same-round `review_result`, when present
- legal reviewer next actions:
  - `continue_coder_round`
  - `advance_frontier`
  - `wait_for_user`
  - `stop_on_blocker`
- reviewer materialization:
  - `continue_coder_round` -> `continue_same_object`
  - `advance_frontier` -> `advance_to_next_object`
  - `wait_for_user` -> `waiting`
  - `stop_on_blocker` -> `blocked`

<!-- forgeloop:anchor initiative-kind -->
## Initiative

- `active_object_kind`: `initiative`
- rolling doc contract: `plugins/forgeloop/skills/run-initiative/references/initiative-review-rolling-doc.md`
- reviewer: `initiative_reviewer`
- current handoff opener: the current round's `review_handoff`, when present
- current review result: same-round `review_result`, when present
- legal reviewer next actions:
  - `continue_coder_round`
  - `initiative_delivered`
  - `wait_for_user`
  - `stop_on_blocker`
- reviewer materialization:
  - `continue_coder_round` -> `continue_same_object`
  - `initiative_delivered` -> `initiative_completed`
  - `wait_for_user` -> `waiting`
  - `stop_on_blocker` -> `blocked`

<!-- forgeloop:anchor consumer-law -->
## Consumer Law

When `code-loop` binds one runtime object kind, it must consume:

- the bound rolling-doc contract as the canonical reviewer-output contract for that object kind
- the canonical runtime routing vocabulary from `plugins/forgeloop/skills/run-initiative/references/global-state.md`
- the exact judgment surface from the bound reviewer prompt

`enter_review` remains supervisor-only transient state materialization for handoff entry and is not a legal reviewer output.

`advance_frontier` means only this:

- the current object may release control back to the runtime `Supervisor`
- the `Supervisor` must then use the shared selection contract to choose the next runtime object
- `advance_frontier` never authorizes persisting `frontier` as a runtime plane or object

Do not create a second object-selection law here.
