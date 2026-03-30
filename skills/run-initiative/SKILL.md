---
name: run-initiative
description: Use when the user asks to advance, continue, or resume an Initiative; the entry accepts initiative_key or planning_doc_path and uses the sealed planning docs, Global State Doc, and necessary runtime docs to determine the current next step
---

# Run Initiative

## Background

The Initiative execution loop uses one control spine plus three execution loops:
- `Supervisor` acts as the dispatcher and maintains the `Global State Doc`
- coder and reviewer perform formal handoff inside object-level review rolling docs
- the system enters the Task, Milestone, or Initiative review/repair loop based on the current progress position

## Goal

In this framework, you act as the `Supervisor` dispatcher. You are responsible only for:
- binding the formal source paths for the current Initiative
- running the execution-side planning admission check before any runtime dispatch
- determining the current next step, or whether to stop, rebuild, or ask the user
- updating the `Global State Doc` when needed
- calling one of the following when needed: skill: `using-git-worktrees`, skill: `rebuild-runtime`, skill: `task-loop`, skill: `milestone-loop`, or skill: `initiative-loop`

You are not responsible for:
- writing code
- writing any review rolling doc body content
- maintaining parallel state outside the four formal runtime docs

## Core Rule

You only determine the current next step. You do not personally perform coding or review.

Before any runtime loop dispatch, first decide whether the sealed planning docs are legal execution input. This planning admission check lives inside `run-initiative`; it is not a separate skill, it does not author planning docs, and it does not replace runtime recovery. It only accepts or rejects the current planning truth as a legal runtime starting point.

## Dispatch Rules

Once the current next step is confirmed, call the required skill in order, or stop and ask the user. Only one skill may be called at a time: no parallelism, no skipped steps.

The `Global State Doc` carries only the minimum control-plane state: `current_snapshot`, `next_action`, `last_transition`, plus explicit waiting / blocked / done signals.
Each update exists only to support the current next-step dispatch. Do not write coder / reviewer body content, do not keep process logs, and do not create a second state model outside the formal runtime docs.

## When To Stop Or Ask The User

- the total task doc is not sealed or is obviously unfinished
- the sealed design doc is missing, unfinished, or lacks an explicit `Gap Analysis Requirement`
- the sealed design doc requires gap analysis but the gap analysis doc is missing, unfinished, or inconsistent with the total task doc
- the sealed planning docs are missing basic execution structure, such as Initiative boundary, Milestone structure, Task Ledger, integration path, reference assignment, acceptance matrix, or residual-risk registration
- the current next step cannot be determined uniquely
- a new Initiative is starting but there is no clear first executable Task
- the system is already in a delivered stop state, or it is in waiting / blocked and this activation does not clearly resolve that stop reason

## Main Flow

### Step 1: Bind Input

First bind the formal source paths for the current Initiative.

1. Use the user-provided `planning_doc_path`, `initiative_key`, or the only verifiable active Initiative in the current workspace to bind the current Initiative. If it cannot be verified uniquely, ask the user directly.
2. Prefer exploring under the parent path of the user-provided total task doc. Only if that is insufficient should you continue under the repo `docs/` tree.
3. At most seven formal source slots must be confirmed: `design_ref`, `gap_analysis_ref`, `total_task_doc_ref`, `global_state_doc_ref`, `task_review_rolling_doc_root_ref`, `milestone_review_rolling_doc_root_ref`, and `initiative_review_rolling_doc_ref`.
4. `gap_analysis_ref` may be `N/A` only when the sealed `Design Doc` explicitly marks `Gap Analysis Requirement: not_required`.
5. The four runtime slots may temporarily point to missing files or directories on cold start, but the canonical paths must already be uniquely confirmed.
6. If `design_ref` or `total_task_doc_ref` is missing, if `gap_analysis_ref` is required but missing, or if `total_task_doc_ref` cannot identify the Initiative reference entry clearly, stop, do not write `Global State Doc`, and ask the user to provide or confirm the missing information.

### Step 2: Run Planning Admission And Determine The Current Next Step

After reading the formal docs, first decide whether the planning truth may legally enter runtime, then determine the current next step directly.

1. Read `total_task_doc_ref` and `global_state_doc_ref` first.
2. Read `design_ref` before any runtime routing. Read `gap_analysis_ref` when the sealed `Design Doc` marks `Gap Analysis Requirement: required`, or when the upstream planning refs disagree and the conflict must be resolved.
3. Inside this skill, perform a thin planning admission check. At minimum confirm all of the following:
- `total_task_doc_ref` is sealed and not obviously unfinished
- `design_ref` is sealed and explicitly states `Gap Analysis Requirement: required | not_required`
- if `Gap Analysis Requirement: required`, `gap_analysis_ref` exists, is sealed, and the `Total Task Doc` points to it explicitly; otherwise the `Total Task Doc` marks gap refs `N/A`
- the Initiative boundary and success criteria are explicit enough to execute
- the Milestone structure, Task Ledger, branch and PR integration path, legal reference assignments, acceptance matrix, and global residual risks are explicit enough to act on
4. If planning admission fails, stop and challenge the user directly to repair planning truth. Do not call skill: `rebuild-runtime` just to paper over illegal planning input, and do not enter any execution loop.
5. If needed, then read the currently active review rolling doc in a targeted way. Only when document facts are still insufficient should you add the minimum necessary Git / test facts.
6. Then decide directly:
- if the `Global State Doc` already records a delivered stop state such as `initiative_delivered`: stop and explain the current stop point
- if the `Global State Doc` already records waiting or blocked: first check whether this activation clearly resolves that stop reason
  - if not, stop at that state
  - if yes, record that resume in `last_transition`, then continue from newer formal runtime truth instead of treating the stop as terminal
- if `Global State Doc` is missing and no rolling doc exists: treat it as a new Initiative start
- if `Global State Doc` is missing but rolling docs already exist, or if `Global State Doc` clearly conflicts with the total task doc or rolling docs: call skill: `rebuild-runtime`
- if current progress clearly belongs to the Task review/repair loop, including continuing the currently bound Task, continuing repair on the current Task, or uniquely identifying the next ready Task: formally rebind `current_snapshot` and `next_action` to that Task if needed, then call skill: `task-loop`
- if current progress clearly belongs to a Milestone review/repair loop: formally rebind `current_snapshot` and `next_action` to that Milestone if needed, then call skill: `milestone-loop`
- if current progress clearly belongs to the Initiative review/repair loop: formally rebind `current_snapshot` and `next_action` to that Initiative if needed, then call skill: `initiative-loop`
- if the facts do not conflict but the current next step still cannot be determined uniquely: ask the user directly
7. You may confirm only one next step or one clear stop point. If facts conflict, call skill: `rebuild-runtime`; if they are ambiguous, ask the user.

### Step 3: Hand Environment Preparation To The Worktree Skill

Do this only when the current next step requires calling skill: `task-loop`, skill: `milestone-loop`, or skill: `initiative-loop`.

1. If the current next step is to stop, ask the user, or call skill: `rebuild-runtime`, skip this step.
2. If the current next step is to enter skill: `task-loop`, skill: `milestone-loop`, or skill: `initiative-loop`, call skill: `using-git-worktrees` first.
3. Whether to reuse the current workspace, switch branches, or create a worktree is decided entirely by `using-git-worktrees`; `run-initiative` must not pre-judge whether the current workspace is already prepared.
4. If `using-git-worktrees` returns ready, continue to Step 4. If it exposes a conflict, waiting state, or blocker, stop at that point.

### Step 4: Execute The Current Next Step

Consume only the conclusion already confirmed in the previous step. Do not reinterpret the facts.

1. New Initiative start: after planning admission has already passed, initialize the minimum `Global State Doc`. If there is a clear first executable Task, bind `current_snapshot` to that Task, switch `next_action` to the current Task coder round, then call skill: `task-loop`. Otherwise stop and challenge the user directly.
2. Existing Initiative resumes into the Task review/repair loop: if the Task that should be advanced is not yet formally bound in `current_snapshot`, rebind `current_snapshot` and `next_action` first, then call skill: `task-loop`.
3. Existing Initiative resumes into the Milestone review/repair loop: if the Milestone that should be advanced is not yet formally bound in `current_snapshot`, rebind `current_snapshot` and `next_action` first, then call skill: `milestone-loop`.
4. Existing Initiative resumes into the Initiative review/repair loop: if the Initiative that should be advanced is not yet formally bound in `current_snapshot`, rebind `current_snapshot` and `next_action` first, then call skill: `initiative-loop`.
5. `rebuild-runtime` is required: call skill: `rebuild-runtime`.
6. User confirmation is required: stop and ask the minimum necessary question.
7. The system is already in a stop state: stop and enter no loop.

If work will continue, first update the `Global State Doc` until it is clear enough. If the active object or active plane is about to change, the new `current_snapshot` and `next_action` must be written first so that a later `Supervisor` can quickly trace and recover the current progress state.

When the active object is already in flight or has been recovered from an existing rolling doc, `current_snapshot` should preserve the active `coder_slot` and current object-local `round`. Only on first entry into a fresh runtime object with no rolling doc yet may `current_snapshot` temporarily omit them; the target loop must then initialize `coder_slot=coder` and object-local `round=1` before dispatching the first coder round.

### Step 5: Loop Back

After any loop returns, reread the `Global State Doc` and the active rolling doc that was just modified. Do not infer from cached expectations about what should have happened in the previous round. Go straight back to Step 2 and re-determine the current next step.

Keep advancing until one of these stop points appears:
- waiting for human judgment
- a true blocker exists
- the user asked to pause
- the Initiative has completed delivery

## Prohibitions

Never:
- write formal coder or reviewer content into any review rolling doc
- infer `Gap Analysis Requirement` from loose Initiative labels instead of reading the sealed `Design Doc`
- enter the Milestone or Initiative review/repair loop directly while an active repair Task still has priority
- treat temporary commentary, session memory, or cache as facts equivalent to the formal runtime docs
- use skill: `rebuild-runtime` to compensate for illegal or unfinished planning truth
- create a second state model inside JSON, notes, or hidden memory
- let `run-initiative` execute `G1`, `G2`, `G3`, `R1`, `R2`, or `R3` itself
- silently replace the current coder with a new logical owner
- continue advancing when `Global State Doc` already explicitly says to wait for the user

## Completion Criteria

After a correct `run-initiative` activation, the system should satisfy all of the following:
- the current Initiative is bound uniquely
- the current next step or stop point is unambiguous
- if execution continues, the sealed planning docs have already passed the in-skill planning admission check
- if execution continues, there is only one clear active loop
- if execution stops, the stop reason is clear
- no new runtime truth source exists outside the four formal runtime docs
