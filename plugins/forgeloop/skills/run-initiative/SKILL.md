---
name: run-initiative
description: Use when the user asks to advance, continue, or resume an Initiative; the entry accepts initiative_key or planning_doc_path and uses the current planning documents, Global State Doc, and necessary runtime docs to determine the next step
---

# Run Initiative

<!-- forgeloop:anchor background -->
## Background

The Initiative execution system uses one control spine plus one unified execution backbone:

- `Supervisor` acts as the dispatcher and maintains the `Global State Doc`
- coder and reviewer advance formal runtime truth inside object-local review rolling docs
- `code-loop` is the only canonical runtime execution loop
- legal runtime object kinds are only `task`, `milestone`, and `initiative`

`task-loop`, `milestone-loop`, `initiative-loop`, and persisted `frontier` state are not part of the canonical runtime architecture.

The repo-local control-plane root contract lives at `../references/control-plane-roots.md`.
The only legal runtime object selection law lives at `references/runtime-object-selection.md`.

<!-- forgeloop:anchor delegation-contract -->
## Delegation Contract

`run-initiative` is a multi-agent dispatch skill.

If this skill has been invoked, treat that invocation itself as user authorization for the `Supervisor` to dispatch the required coder / reviewer subagents for the next step. Do not stop only to re-ask for ordinary coder / reviewer delegation.

If the current environment still prevents delegation, or if you will not actually dispatch the required coder / reviewer subagents in this activation, stop immediately and ask the user. Never treat that situation as permission for the `Supervisor` to continue by personally doing coder or reviewer work.

<!-- forgeloop:anchor runtime-rebinding-law -->
## Runtime Rebinding Law

Runtime-only rebinding is legal.

If the current execution problem is still fully contained inside the sealed execution map, the `Supervisor` may rebind from the current runtime object to the nearest sufficient runtime object and continue through the same `code-loop`.

This is neither a return to planning nor a wrapper-layer loop handoff; it is only a dispatcher-level current-object rebind inside one sealed execution map.

Return to planning only when the sealed execution map itself is missing, contradictory, or insufficient.

<!-- forgeloop:anchor runtime-read-law -->
## Runtime Read Law

Bind `plugins/forgeloop/skills/run-initiative/references/runtime-cutover.md` first and obey it.
Obey the shared packet law in `../references/anchor-addressing.md`.
Obey the shared truth-location law in `../references/truth-location.md`.
Do not restate packet completeness, selector legality, or supervisor-doc exclusion here unless this file adds a true local exception.

Derived views are helpers only. If a derived view is missing, stale, or conflicts with the rolling doc, invalidate it and read the rolling doc.

<!-- forgeloop:anchor goal -->
## Goal

In this framework, you act as the runtime `Supervisor`. You are responsible only for:

- binding the formal source refs for the current Initiative
- running the execution-side planning admission check before any runtime dispatch
- determining the current runtime object, or whether to stop, rebuild, or ask the user
- updating the `Global State Doc` when needed
- keeping runtime-plane bindings plane-local and ensuring they are closed before planning bindings stay live; current-object worker reuse and the at-most-one coder/reviewer rule per active loop layer are handled inside `code-loop`
- calling one of the following when needed: skill: `using-git-worktrees`, skill: `rebuild-runtime`, or skill: `code-loop`

You are not responsible for:

- writing code
- writing any review rolling doc body content
- maintaining parallel state outside the `Global State Doc` plus the object-local review rolling docs

`run-initiative` is the only runtime dispatcher that may bind the current runtime object.
It selects the current object only from formal runtime truth and `runtime-object-selection.md`.
`code-loop` executes only the already bound object.
If object-local execution proves that control should leave the current object, `code-loop` may record only the release fact in `last_transition` and stop.
Any change of current object becomes effective only after `run-initiative` rereads formal truth and rebinds the next object.

<!-- forgeloop:anchor core-rule -->
## Core Rule

You only determine the next step. You do not personally perform coding or review.

Before any runtime loop dispatch, first decide whether the planning document set is legal execution input.
This planning admission check lives inside `run-initiative`. It is not a separate skill, does not author planning docs, and does not replace runtime recovery.
It only accepts or rejects the current `Design Doc`, optional `Gap Analysis Doc`, and `Total Task Doc` as the legal runtime starting point.

<!-- forgeloop:anchor dispatch-rules -->
## Dispatch Rules

Once the next step is confirmed, dispatch exactly one downstream skill for that decision point, or stop and ask the user. Sequential redispatch after a skill returns is allowed only after rereading formal runtime state; parallel dispatch and speculative skipped steps are forbidden.

The `Global State Doc` carries only the minimum control-plane state: `workspace_binding`, `current_snapshot`, `next_action`, and `last_transition`.
Each update exists only to support the current next-step dispatch. Do not write coder / reviewer body content, do not keep process logs, do not persist session-local `agent_id` bindings, and do not create a second state model outside the formal runtime docs.

### Worker Binding Law

- Any downstream worker dispatch must preserve supervisor/worker context isolation. New coder or reviewer agents must be created with `fork_context=false`; reused agents must receive complete explicit packets via `send_input`, not inherited supervisor conversation context.
- `spawn_agent` is create-only. Use it only when the bound runtime loop layer has no usable `coder` / reviewer `agent_id`, or when the previously bound one is known closed, dead, or otherwise unrecoverable.
- Reuse means dispatching the existing bound `agent_id` with `send_input`. Do not call `spawn_agent` again for a still-live Task / Milestone / Initiative worker just because the same loop continues into another round.
- `task_name`, role name, object key, or kind name are not reuse handles. Only the current session's stored `agent_id` binding is a legal reuse handle.
- If an existing bound worker must be reopened before more input can be sent, resume that same `agent_id`; do not treat ordinary continuation as a reason to mint a new thread.
- `close_agent` is runtime-local binding cleanup. Once a worker has been removed from the current reusable binding table, do not treat that old `agent_id` as the active reusable binding; later continuation must either reopen that same `agent_id` explicitly or create a new binding with `spawn_agent`.

<!-- forgeloop:anchor runtime-admission-law -->
## Runtime Admission Law

Planning admission must start from the planning document set itself and read only the minimum selectors required to prove runtime legality.

For execution admission, the only planning-status signals are the explicit `状态` markers in the current `Design Doc`, optional `Gap Analysis Doc`, and `Total Task Doc`.
Do not read planning rolling docs or planning reviewer history to decide whether runtime may start. Those belong to the planning loop, not to execution admission.

At minimum, admission must prove:

- the current `Design Doc` explicitly says `状态：sealed` and exposes an explicit `Gap Analysis Requirement`
- the current `Total Task Doc` explicitly says `状态：sealed` and exposes execution boundary, Initiative ref assignment, and the active object definition needed for this dispatch
- the current `Gap Analysis Doc` is read only when the current `Design Doc` requires it or when planning refs conflict, and in that case it must explicitly say `状态：sealed`

If the shared packet law or runtime cutover contract forces fallback or stop during admission, obey that result. Never guess past incomplete admission.

<!-- forgeloop:anchor when-to-stop -->
## When To Stop Or Ask The User

- the total task doc does not explicitly self-state `状态：sealed`, or it is obviously unfinished
- the design doc is missing, unfinished, does not explicitly self-state `状态：sealed`, or lacks an explicit `Gap Analysis Requirement`
- the design doc requires gap analysis but the gap analysis doc is missing, unfinished, does not explicitly self-state `状态：sealed`, or is inconsistent with the total task doc
- the planning documents marked `sealed` are missing basic execution structure, such as Initiative boundary, Milestone structure, Task Ledger, integration path, reference assignment, acceptance matrix, or residual-risk registration
- the confirmed next step requires coder or reviewer dispatch, but delegation is unavailable, blocked, or will not actually be performed in this activation
- the next step cannot be determined uniquely
- a new Initiative is starting but there is no clear first executable Task
- the system is already at `initiative_delivered`, or it is at `waiting` / `blocked` and this activation does not clearly resolve that stop reason

<!-- forgeloop:anchor main-flow -->
## Main Flow

### Step 1: Bind Input

First bind the formal source refs for the current Initiative.

1. Use the user-provided `planning_doc_path`, `initiative_key`, or the only verifiable active Initiative in the current workspace to bind the current Initiative. If it cannot be verified uniquely, ask the user.
2. When `planning_doc_path` is provided, prefer exploring under its parent path. Only if that is insufficient should you continue under the repo `docs/` tree.
3. When the sealed planning artifact directory is known, derive the one legal repo-local runtime control-plane root from `../references/control-plane-roots.md`: sibling `.forgeloop/` under that Initiative document directory. Bind the runtime refs there directly. Do not search for alternate repo-local runtime control-plane roots elsewhere in the repository.
4. Confirm seven Initiative-bound source slots as canonical refs: `design_ref`, `gap_analysis_ref`, `total_task_doc_ref`, `global_state_doc_ref`, `task_review_rolling_doc_root_ref`, `milestone_review_rolling_doc_root_ref`, and `initiative_review_rolling_doc_ref`.
5. `gap_analysis_ref` may be `N/A` only when the sealed `Design Doc` explicitly marks `Gap Analysis Requirement: not_required`.
6. The four runtime slots may temporarily point to missing files or directories on cold start, but the canonical repo-root-relative refs must already be uniquely confirmed.
7. For repo-local targets, the durable value of each source slot must be a repo-root-relative ref. Do not bind current-workspace absolute paths, worktree-specific absolute paths, or shell-cwd-relative paths here.
8. Bind `runtime_cutover_ref=plugins/forgeloop/skills/run-initiative/references/runtime-cutover.md` and `runtime_object_selection_ref=plugins/forgeloop/skills/run-initiative/references/runtime-object-selection.md` separately as framework contract refs before any runtime routing or packet assembly.
9. If `design_ref` or `total_task_doc_ref` is missing, if `gap_analysis_ref` is required but missing, or if `total_task_doc_ref` cannot identify the Initiative reference entry clearly, stop, do not write `Global State Doc`, and ask the user to provide or confirm the missing information.

### Step 2: Run Planning Admission Only When The Admission Basis Changes

After binding the planning refs, run this check only on cold start, after any bound planning ref changes, after `rebuild-runtime`, or when sealed planning truth conflicts with persisted runtime truth. Do not rerun it as the default hot-path loop on every runtime return.

1. Read `runtime_cutover_ref` first and bind `current_runtime_cutover_mode`.
2. Read `total_task_doc_ref` next.
3. Read `design_ref` before any runtime routing. Read `gap_analysis_ref` only when the current `Design Doc` marks `Gap Analysis Requirement: required`, or when the upstream planning refs disagree and the conflict must be resolved.
4. Outside cold start or rebuild recovery, obey the bound runtime cutover contract plus the shared packet law for minimal reads versus fallback.
5. Inside this skill, keep planning admission thin. At minimum confirm all of the following:
   - `total_task_doc_ref` explicitly says `状态：sealed` and is not obviously unfinished
   - `design_ref` explicitly says `状态：sealed` and explicitly states `Gap Analysis Requirement: required | not_required`
   - if `Gap Analysis Requirement: required`, `gap_analysis_ref` exists, explicitly says `状态：sealed`, and the `Total Task Doc` points to it explicitly; otherwise the `Total Task Doc` marks gap refs `N/A`
   - the Initiative boundary and success criteria are explicit enough to execute
   - the Milestone structure, Task Ledger, integration path, legal reference assignments, acceptance matrix, and global residual risks are explicit enough to act on
6. Treat any mismatch between those document-level status lines and the execution structure they claim to seal as illegal planning input. Do not reopen planning history from rolling docs here to guess intent.
7. If planning admission fails, stop and ask the user to repair the planning truth. Do not call skill: `rebuild-runtime` just to paper over illegal planning input, and do not enter any execution loop.
8. If admission passes and runtime routing still needs workspace-local runtime docs, continue to Step 3.

### Step 3: Bind The Active Initiative Workspace

Do this whenever runtime routing or loop execution needs workspace-local runtime docs.

This is the first step that may materialize workspace-local absolute paths from the durable repo-root-relative refs bound in Step 1. No earlier step may convert those refs into workspace-specific paths.

1. If planning admission has already failed, or if the current stop point is already clear without reading workspace-local runtime docs, skip this step.
2. If runtime routing depends on `global_state_doc_ref` or any rolling doc and the current workspace is not already confirmed as the active Initiative workspace, call skill: `using-git-worktrees` first in `bind_only` mode.
3. `bind_only` means: confirm or create or reuse the active Initiative workspace and target branch so runtime refs may be materialized and read, but do not require repo setup or baseline verification yet.
4. Whether to reuse the current workspace, switch branches, or create a worktree is decided entirely by `using-git-worktrees`; `run-initiative` must not pre-judge whether the current workspace is already prepared.
5. Once the active Initiative workspace is confirmed, materialize `global_state_doc_ref`, `task_review_rolling_doc_root_ref`, `milestone_review_rolling_doc_root_ref`, and `initiative_review_rolling_doc_ref` against that workspace. From that point onward in this activation, use only those materialized paths for runtime reads and writes.
6. Never write the materialized absolute paths back into the `Total Task Doc` or any other durable planning truth.
7. If `using-git-worktrees` in `bind_only` mode exposes a conflict, waiting state, or blocker, stop at that point.

### Step 4: Determine The Current Runtime Object

After admission is legal, determine exactly one current runtime object.

1. If `Global State Doc` already binds one legal current object and that object still has an open same-object repair or review cycle, preserve that object, preserve `coder_slot`, preserve `round`, and continue.
2. Otherwise bind `plugins/forgeloop/skills/run-initiative/references/runtime-object-selection.md` and use it as the only legal next-object selector.
3. `frontier` is never a legal persisted runtime object or plane. If older runtime truth still exposes `frontier`, treat that state as stale and recover through the shared selection contract instead of preserving it.
4. If the current object is no longer the nearest sufficient execution focus, but the sealed execution map still proves the next legal object uniquely, rebind to that object without returning to planning.
5. If the sealed execution map cannot identify exactly one next runtime object, stop and ask the user.
6. Only after one legal current object has been bound may `run-initiative` write `current_snapshot` and re-enter `code-loop`.

### Step 5: Determine The Runtime Next Step

After binding the formal runtime truth, resolve exactly one outcome for this activation:

1. stop if the current legal state is already `initiative_delivered`, `waiting`, or `blocked`
2. call skill: `rebuild-runtime` when the `Global State Doc`, the bound rolling doc, or the sealed execution map conflict, or when the active current object can no longer be recovered uniquely from formal runtime truth
3. enter skill: `code-loop` when one legal current object is already bound and the next object-local step is same-object continuation or review-cycle continuation
4. if the sealed execution map proves a different current object uniquely, rewrite `current_snapshot`, record `last_transition.transition=rebind_within_execution_map`, set `next_action.action=enter_code_loop`, then enter skill: `code-loop`
5. stop and ask the user only when the formal facts are legal but the next step still cannot be determined uniquely

Do not create a second interruption taxonomy here. Use exactly this triage: conflicting -> rebuild; legal but ambiguous -> ask the user; otherwise continue.
Use the smallest fitting class: conflicting -> rebuild; legal but ambiguous -> ask the user; otherwise continue.
Use `rebind_within_execution_map` only when the new active object is already proved uniquely in this activation. Otherwise record only the release fact and let the ordinary selection contract choose the next object.
- if workspace diff or interrupted agent narration suggests progress that has not appeared as a rereadable `coder_update`, `review_handoff`, or `review_result`: do not advance the object from that hint alone; continue only from the last legal formal runtime state or call skill: `rebuild-runtime` when the active state is no longer provable uniquely

### Step 6: Prepare Execution And Execute The Next Step

Consume only the conclusion already resolved in Step 5.

1. If the confirmed next step is to call skill: `code-loop`, ensure the already bound active Initiative workspace is `execution_ready` first. `execution_ready` means the active Initiative workspace has completed any project-declared environment preparation from `AGENTS.md` or repo operator docs, plus repo-obvious setup and baseline verification, strongly enough to enter coder or reviewer execution. If this activation has only completed `bind_only`, call skill: `using-git-worktrees` again in `execution_ready` mode against that same workspace.
2. Before any `code-loop` dispatch, bind the concrete active review rolling doc ref for the selected object:
   - Task -> derive `task_review_rolling_doc_ref` from `task_review_rolling_doc_root_ref` and the bound `task_key` using the shared runtime naming law
   - Milestone -> bind the current Milestone's explicit review rolling doc ref from `3.4 Milestone Reference Assignment`
   - Initiative -> bind `initiative_review_rolling_doc_ref`
   Keep the authoritative `doc_ref + anchor_selector` bindings for the bound object available to `code-loop`.
3. If work will continue, materialize the resolved `Global State Doc` first so that `workspace_binding`, `current_snapshot`, `next_action`, and `last_transition` are already sufficient for later recovery.
4. Then dispatch exactly one downstream skill:
   - current-object continuation or runtime-only rebind -> skill: `code-loop`
   - control-plane recovery -> skill: `rebuild-runtime`
   - stop state or required user confirmation -> stop directly

Do not precompose a second object-local reviewer-entry packet here. Once the current object and its rolling doc ref are bound, `code-loop` owns coder / reviewer entry for that object.

<!-- forgeloop:anchor red-lines -->
## Red Lines

Never:

- persist `frontier` into `Global State Doc`
- require runtime to stay on the same bound object when the sealed execution map already proves a better current object
- return to planning only because the current object is no longer the best execution focus
- reintroduce wrapper-layer runtime law outside `code-loop`
- encode runtime object selection separately in both dispatcher and recovery logic
- let PR structure replace runtime object truth
