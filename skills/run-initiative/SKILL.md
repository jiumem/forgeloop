---
name: run-initiative
description: Use when the user asks to advance, continue, or resume an Initiative; the entry accepts initiative_key or planning_doc_path and uses the total task doc, Global State Doc, and necessary runtime docs to determine the current next step
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
- determining the current next step, or whether to stop, rebuild, or ask the user
- updating the `Global State Doc` when needed
- calling one of the following when needed: skill: `using-git-worktrees`, skill: `rebuild-runtime`, skill: `task-loop`, skill: `milestone-loop`, or skill: `initiative-loop`

You are not responsible for:
- writing code
- writing any review rolling doc body content
- maintaining parallel state outside the four formal runtime docs

## Core Rule

You only determine the current next step. You do not personally perform coding or review.

## Dispatch Rules

Once the current next step is confirmed, call the required skill in order, or stop and ask the user. Only one skill may be called at a time: no parallelism, no skipped steps.

The `Global State Doc` carries only the minimum control-plane state: `current_snapshot`, `next_action`, `last_transition`, plus explicit waiting / blocked / done signals.
Each update exists only to support the current next-step dispatch. Do not write coder / reviewer body content, do not keep process logs, and do not create a second state model outside the formal runtime docs.

## When To Stop Or Ask The User

- the total task doc is not sealed or is obviously unfinished
- the current next step cannot be determined uniquely
- a new Initiative is starting but there is no clear first executable Task
- the system is already in a stop state: waiting for the user, truly blocked, or already delivered

## Main Flow

### Step 1: Bind Input

First bind the formal source paths for the current Initiative.

1. Use the user-provided `planning_doc_path`, `initiative_key`, or the only verifiable active Initiative in the current workspace to bind the current Initiative. If it cannot be verified uniquely, ask the user directly.
2. Prefer exploring under the parent path of the user-provided total task doc. Only if that is insufficient should you continue under the repo `docs/` tree.
3. At most seven formal source slots must be confirmed: `design_ref`, `gap_analysis_ref`, `total_task_doc_ref`, `global_state_doc_ref`, `task_review_rolling_doc_root_ref`, `milestone_review_rolling_doc_root_ref`, and `initiative_review_rolling_doc_ref`.
4. `gap_analysis_ref` may be `N/A` only for non-refactor / non-migration / non-replacement / non-governance-convergence Initiatives.
5. The four runtime slots may temporarily point to missing files or directories on cold start, but the canonical paths must already be uniquely confirmed.
6. If `design_ref` or `total_task_doc_ref` is missing, if a refactor Initiative is missing `gap_analysis_ref`, or if `total_task_doc_ref` cannot identify the Initiative reference entry clearly, stop, do not write `Global State Doc`, and ask the user to provide or confirm the missing information.

### Step 2: Determine The Current Next Step

After reading the formal docs, determine the current next step directly.

1. Read `total_task_doc_ref` and `global_state_doc_ref` first.
2. If needed, then read the currently active review rolling doc in a targeted way. Only when document facts are still insufficient should you add the minimum necessary Git / test facts.
3. Then decide directly:
- if `total_task_doc_ref` is not sealed or is obviously unfinished: stop and challenge the user directly
- if the system is clearly already in a waiting-for-user, truly blocked, or delivered stop state: stop and explain the current stop point
- if `Global State Doc` is missing and no rolling doc exists: treat it as a new Initiative start
- if `Global State Doc` is missing but rolling docs already exist, or if `Global State Doc` clearly conflicts with the total task doc or rolling docs: call skill: `rebuild-runtime`
- if current progress clearly belongs to the Task review/repair loop, including continuing the currently bound Task, continuing repair on the current Task, or uniquely identifying the next ready Task: formally rebind `current_snapshot` and `next_action` to that Task if needed, then call skill: `task-loop`
- if current progress clearly belongs to a Milestone review/repair loop: formally rebind `current_snapshot` and `next_action` to that Milestone if needed, then call skill: `milestone-loop`
- if current progress clearly belongs to the Initiative review/repair loop: formally rebind `current_snapshot` and `next_action` to that Initiative if needed, then call skill: `initiative-loop`
- if the facts do not conflict but the current next step still cannot be determined uniquely: ask the user directly
4. You may confirm only one next step or one clear stop point. If facts conflict, call skill: `rebuild-runtime`; if they are ambiguous, ask the user.

### Step 3: Hand Environment Preparation To The Worktree Skill

Do this only when the current next step requires calling skill: `task-loop`, skill: `milestone-loop`, or skill: `initiative-loop`.

1. If the current next step is to stop, ask the user, or call skill: `rebuild-runtime`, skip this step.
2. If the current next step is to enter skill: `task-loop`, skill: `milestone-loop`, or skill: `initiative-loop`, call skill: `using-git-worktrees` first.
3. Whether to reuse the current workspace, switch branches, or create a worktree is decided entirely by `using-git-worktrees`; `run-initiative` must not pre-judge whether the current workspace is already prepared.
4. If `using-git-worktrees` returns ready, continue to Step 4. If it exposes a conflict, waiting state, or blocker, stop at that point.

### Step 4: Execute The Current Next Step

Consume only the conclusion already confirmed in the previous step. Do not reinterpret the facts.

1. New Initiative start: initialize the minimum `Global State Doc`. If there is a clear first executable Task, bind `current_snapshot` to that Task, switch `next_action` to the current Task coder round, then call skill: `task-loop`. Otherwise stop and challenge the user directly.
2. Existing Initiative resumes into the Task review/repair loop: if the Task that should be advanced is not yet formally bound in `current_snapshot`, rebind `current_snapshot` and `next_action` first, then call skill: `task-loop`.
3. Existing Initiative resumes into the Milestone review/repair loop: if the Milestone that should be advanced is not yet formally bound in `current_snapshot`, rebind `current_snapshot` and `next_action` first, then call skill: `milestone-loop`.
4. Existing Initiative resumes into the Initiative review/repair loop: if the Initiative that should be advanced is not yet formally bound in `current_snapshot`, rebind `current_snapshot` and `next_action` first, then call skill: `initiative-loop`.
5. `rebuild-runtime` is required: call skill: `rebuild-runtime`.
6. User confirmation is required: stop and ask the minimum necessary question.
7. The system is already in a stop state: stop and enter no loop.

If work will continue, first update the `Global State Doc` until it is clear enough. If the active object or active plane is about to change, the new `current_snapshot` and `next_action` must be written first so that a later `Supervisor` can quickly trace and recover the current progress state.

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
- enter the Milestone or Initiative review/repair loop directly while an active repair Task still has priority
- treat temporary commentary, session memory, or cache as facts equivalent to the formal runtime docs
- create a second state model inside JSON, notes, or hidden memory
- let `run-initiative` execute `G1`, `G2`, `G3`, `R1`, `R2`, or `R3` itself
- silently replace the current coder with a new logical owner
- continue advancing when `Global State Doc` already explicitly says to wait for the user

## Completion Criteria

After a correct `run-initiative` activation, the system should satisfy all of the following:
- the current Initiative is bound uniquely
- the current next step or stop point is unambiguous
- if execution continues, there is only one clear active loop
- if execution stops, the stop reason is clear
- no new runtime truth source exists outside the four formal runtime docs
