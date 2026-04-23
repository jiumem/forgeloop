# Global State Doc Control Reference

<!-- forgeloop:anchor document-role -->
## Document Role

- Plane: runtime control spine
- Applies to: one active Initiative runtime session
- Primary readers: `run-initiative`, `code-loop`, and `rebuild-runtime`
- Primary purpose: keep only the minimum runtime control state needed for recovery, dispatch, and legal stop routing

<!-- forgeloop:anchor legal-blocks -->
## Legal Blocks

- `runtime_state_header`
- `workspace_binding`
- `current_snapshot`
- `next_action`
- `last_transition`

<!-- forgeloop:anchor bootstrap-law -->
## Bootstrap Law

- On cold start, initialize `runtime_state_header`, `workspace_binding`, `current_snapshot`, `next_action`, and `last_transition`.
- Write `workspace_binding` as soon as the active Initiative worktree is bound.
- Do not invent reviewer-ready, delivered, or rebound state during bootstrap.
- Once runtime truth can recover a unique current object, rewrite the initialized blocks from that formal state instead of keeping placeholder control values.

<!-- forgeloop:anchor control-law -->
## Control Law

- `Global State Doc` is the only runtime-wide control spine.
- `workspace_binding` is the legal persisted home for the active Initiative worktree binding.
- reviewer identity, physical `agent_id`, and session-local worker bindings are never legal fields here.

<!-- forgeloop:anchor durable-rules -->
## Durable Rules

- `current_snapshot` carries only:
  - `initiative_key`
  - `active_object_kind`
  - `active_object_key`
  - `rolling_doc_ref`
  - and when known `coder_slot` plus `round`
- `active_object_kind` may only be:
  - `task`
  - `milestone`
  - `initiative`
- `frontier` is never a legal persisted object kind, plane, or current snapshot value.
- `rolling_doc_ref` must use durable repo-root-relative refs.
- `workspace_binding` carries only:
  - `initiative_key`
  - `worktree_name`
  - `branch_name`
  - `active_worktree_path`
  - `updated_at`
- `active_worktree_path` must be an absolute path to the intended active Git worktree for this Initiative.
- `workspace_binding` may contain machine-local path state, but it is not trusted blindly; every activation must verify it against Git worktree facts before use.
- `next_action` owns only immediate dispatch or terminal stop for the currently bound object.
- `last_transition` owns recovery, resume, same-object continuation, runtime-only rebinding, and object-advance facts.

<!-- forgeloop:anchor workspace-binding-law -->
## Workspace Binding Law

`workspace_binding` records where this Initiative is supposed to continue work.
It exists so recovery can return to the same old worktree instead of creating or selecting a replacement path.

When `using-git-worktrees` binds `ACTIVE_WORKTREE_PATH`, it must materialize or update `workspace_binding` in the `Global State Doc` once that doc is writable from the bound worktree.

On resume:

- if `workspace_binding.active_worktree_path` exists, verify that path exists, is a Git worktree, and is attached to `workspace_binding.branch_name`
- if the verified path matches the target branch, continue from that old worktree
- if the path is missing, stale, or branch-mismatched, inspect Git worktree facts before creating anything
- if Git proves exactly one registered worktree for the target branch, continue from that worktree and repair `workspace_binding`
- if `workspace_binding` conflicts with Git facts and cannot be repaired uniquely, stop and surface the conflict

Do not replace an old registered Initiative worktree just because the current shell started elsewhere.
Do not use `workspace_binding.active_worktree_path` without verification.

<!-- forgeloop:anchor runtime-routing-vocabulary -->
## Canonical Runtime Routing Vocabulary

`next_action.action` may only be:

- `enter_code_loop`
- `waiting`
- `blocked`
- `initiative_delivered`

`last_transition.transition` may only be:

- `cold_start`
- `recover_in_object`
- `resume_waiting`
- `resume_blocked`
- `continue_same_object`
- `advance_to_next_object`
- `rebind_within_execution_map`
- `initiative_completed`

Law:

- `next_action` owns only in-object dispatch and terminal stop
- `last_transition` owns recovery, resume, and runtime-only object routing facts
- no runtime file may invent a parallel dispatcher vocabulary

`initiative_completed` is the routing fact that no runnable object remains and Initiative acceptance is satisfied.
`initiative_delivered` is the terminal stop action written after that fact is materialized.
Do not use `initiative_delivered` as a transition name.
Do not use `initiative_completed` as a persisted stop action.

<!-- forgeloop:anchor supervisor-materialization-law -->
## Supervisor Materialization Law

When runtime worker output is materialized into `Global State Doc`:

- coder or reviewer `continue_coder_round`
  - keep the current bound object
  - write `last_transition.transition=continue_same_object`
  - write `next_action.action=enter_code_loop`

- reviewer `advance_frontier`
  - `advance_frontier` is a release signal only and is never persisted as runtime state
  - write only `last_transition.transition=advance_to_next_object`
  - do not bind, imply, or persist the next object here
  - the caller must reread formal runtime truth, apply the shared selection contract, and only then, when rewriting `current_snapshot`, may record `last_transition.transition=rebind_within_execution_map`

- worker `wait_for_user`
  - write `next_action.action=waiting`

- worker `stop_on_blocker`
  - write `next_action.action=blocked`

- initiative reviewer `initiative_delivered`
  - write `last_transition.transition=initiative_completed`
  - write `next_action.action=initiative_delivered`

`enter_review` remains supervisor-only transient materialization for review entry and is never a terminal runtime action.

<!-- forgeloop:anchor formal-block-contract -->
## Formal Block Contract

- `runtime_state_header` must include:
  - `kind`
  - `initiative_key`
  - `created_at`
  - `updated_at`

- `workspace_binding` must include:
  - `kind`
  - `initiative_key`
  - `worktree_name`
  - `branch_name`
  - `active_worktree_path`
  - `updated_at`

- `current_snapshot` must include:
  - `kind`
  - `initiative_key`
  - `active_object_kind`
  - `active_object_key`
  - `rolling_doc_ref`

- `current_snapshot.coder_slot` and `current_snapshot.round` are required once they are recoverable.

- `next_action` must include:
  - `kind`
  - `action`
  - `updated_at`

- `last_transition` must include:
  - `kind`
  - `transition`
  - `updated_at`
  - `reason`

<!-- forgeloop:anchor recommended-template -->
## Recommended Template

````markdown
```forgeloop
kind: runtime_state_header
initiative_key: day7-first-situation-closure
created_at: 2026-04-02T00:00:00Z
updated_at: 2026-04-02T00:00:00Z
```

```forgeloop
kind: workspace_binding
initiative_key: day7-first-situation-closure
worktree_name: codex/day7-first-situation-closure
branch_name: codex/day7-first-situation-closure/initiative
active_worktree_path: /Users/example/.codex/worktrees/forgeloop/codex/day7-first-situation-closure
updated_at: 2026-04-02T00:00:00Z
```

```forgeloop
kind: current_snapshot
initiative_key: day7-first-situation-closure
active_object_kind: task
active_object_key: TASK-1
rolling_doc_ref: docs/initiatives/active/day7-first-situation-closure/.forgeloop/task-review/TASK-1.md
coder_slot: coder
round: 1
```

```forgeloop
kind: next_action
action: enter_code_loop
updated_at: 2026-04-02T00:00:00Z
```

```forgeloop
kind: last_transition
transition: cold_start
updated_at: 2026-04-02T00:00:00Z
reason: initial_runtime_entry
```
````

<!-- forgeloop:anchor red-lines -->
## Red Lines

- do not persist `frontier`
- do not persist arbitrary shell `cwd` or unverified workspace paths outside `workspace_binding`
- do not write coder or reviewer body content here
- do not persist session-local `agent_id` here
- do not create a second runtime control model outside this document and the object-local rolling docs
