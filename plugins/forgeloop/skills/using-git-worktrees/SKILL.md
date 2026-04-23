---
name: using-git-worktrees
description: Use when starting feature work that needs workspace isolation or before execution work; this skill binds or prepares one Initiative worktree without creating parallel workspace truth.
---

# Using Git Worktrees

## Core Law

One Initiative uses one dedicated worktree.
An explicit user location override wins.
Without an explicit override, this skill decides whether to reuse the current Initiative worktree or create one new worktree.

`bind_only` binds workspace and branch identity for runtime reads or recovery, then materializes `workspace_binding` when the `Global State Doc` is writable.
`execution_ready` first satisfies `bind_only`, then verifies repo setup and clean baseline.

If the caller does not name a mode:

- default to `bind_only` when the caller only needs workspace identity for routing, recovery, or runtime-doc reads
- default to `execution_ready` when the caller is about to enter coder or reviewer execution work

Callers must not invent their own reuse or readiness law outside this skill.

## Naming Law

- `WORKTREE_NAME = codex/<initiative-key>`
- `BRANCH_NAME = codex/<initiative-key>/<milestone-key>` when `milestone-key` is uniquely known
- otherwise `BRANCH_NAME = codex/<initiative-key>/initiative`
- if the user explicitly names a branch or worktree, use that value
- if `initiative-key` is missing, stop instead of inventing a name

If the target branch already exists and is not attached to another worktree, reuse that branch.
If the target branch is already attached to another worktree, stop and surface the conflict.

## Reuse Law

Reuse the current workspace only when all of the following are true:

- no explicit user location override conflicts with reuse
- the workspace can be proven to already be the intended Initiative worktree
- the current branch already matches the target branch, or the workspace is clean enough to switch safely

Otherwise create or reuse exactly one external worktree for that Initiative.
Never create a second worktree for the same Initiative just to enter another Milestone.

If reusing the current workspace:

- confirm it is not an unrelated workspace or a different Initiative worktree
- never switch branches through dirty state
- in `bind_only`, stop once workspace and branch identity are correct
- in `execution_ready`, continue into setup and baseline verification

## Location Law

Priority:
explicit user override > `AGENTS.md` > existing `.worktrees/` > existing `worktrees/` > `~/.codex/worktrees/<project-name>/`

Supported explicit overrides:

- `.worktrees/`
- `worktrees/`
- `~/.codex/worktrees/<project-name>/`
- a custom absolute path
- a custom `~/`-prefixed root directory

If the user provides a custom root directory, create the worktree at:

```text
<custom-root>/<project-name>/<worktree-name>
```

Project-local worktree directories must already be ignored.
If the selected project-local directory is not ignored:

- explicit override: stop
- auto-selected directory: fall back to the global Codex worktree root

Do not edit `.gitignore` from this skill.

## Creation Law

Before creating a new worktree:

- decide `WORKTREE_NAME`
- decide `BRANCH_NAME`
- decide the location
- run ignore verification when the selected location is project-local

If the target Initiative worktree path already exists:

- reuse that Initiative worktree instead of creating a second one
- if branch switch is needed, require a clean enough workspace first

If the target branch is attached to another worktree, stop.
If the target branch exists but is unattached, add the worktree on that branch.
Otherwise create the worktree with a new branch.

## Recovery Binding Law

On resume, recovery, or any activation that starts outside the active Initiative worktree, read `workspace_binding` from the `Global State Doc` when it is available.
Recover the active worktree from `workspace_binding`, durable identity, and Git facts.
If the Initiative's target branch is already attached to a registered worktree, that existing worktree is the active Initiative worktree and work must continue there.

Recovery order:

- derive `WORKTREE_NAME` and `BRANCH_NAME` from the Naming Law
- if `workspace_binding.active_worktree_path` exists, verify that path exists, is a Git worktree, and is attached to `BRANCH_NAME`
- if `workspace_binding.active_worktree_path` is verified, bind it as `ACTIVE_WORKTREE_PATH` and continue from that old worktree
- inspect registered worktrees with Git and find any worktree attached to `BRANCH_NAME`
- if exactly one registered worktree is attached to `BRANCH_NAME`, verify its path exists, bind it as `ACTIVE_WORKTREE_PATH`, continue from that existing worktree, and repair `workspace_binding`
- if no registered worktree is attached to `BRANCH_NAME` but the target branch exists unattached, create or add exactly one worktree using the Location Law
- if no target branch exists, create exactly one worktree and branch using the Creation Law
- if `workspace_binding` conflicts with Git facts and cannot be repaired uniquely, or Git facts cannot prove exactly one active worktree, stop and surface the conflict

An explicit user location override may select the creation location when no target worktree is already attached.
It must not create a second worktree for a branch that is already attached elsewhere.
Never create a replacement worktree or switch back to the original caller workspace when the old registered Initiative worktree can be found and verified.

## Activation Law

After creating, reusing, or confirming the target Initiative worktree, bind `ACTIVE_WORKTREE_PATH` to the absolute path of that worktree.

`ACTIVE_WORKTREE_PATH` is the only operational workspace for the remainder of the current activation.
If the selected worktree is not the caller's original current workspace, the caller must switch operational context to `ACTIVE_WORKTREE_PATH` immediately.

Switching operational context means all subsequent repo-local operations must use `ACTIVE_WORKTREE_PATH`, including:

- runtime ref materialization
- control-plane reads and writes
- setup and baseline commands
- coder and reviewer dispatch `cwd` / `cwds`
- Git status, diff, branch, and worktree checks for this Initiative

Do not continue repo-local reads, writes, setup, tests, or agent dispatch from the original workspace after an external worktree has been selected.
Do not treat a worktree as bound until its absolute path and branch identity have both been verified.
Once the `Global State Doc` is writable from `ACTIVE_WORKTREE_PATH`, write or repair its `workspace_binding` block with the verified `initiative_key`, `WORKTREE_NAME`, `BRANCH_NAME`, and `ACTIVE_WORKTREE_PATH`.

## Readiness Law

`bind_only` stops once `ACTIVE_WORKTREE_PATH` and branch identity are correct and the caller can continue from `ACTIVE_WORKTREE_PATH`.

`execution_ready` additionally requires all of the following:

- project-declared environment preparation from `AGENTS.md` or other repo operator docs, when such instructions exist
- repo-obvious setup success
- clean baseline verification success

Do not guess generic dependency installers or baseline commands.
Read and obey project-level `AGENTS.md` first when it declares environment preparation or operator-surface requirements.
Then use repo-documented or repo-obvious setup and baseline commands only.
If setup or baseline cannot be identified without guessing, stop and surface the gap as `execution_ready`, not as a task/object blocker.

Never proceed past failing baseline tests without explicit user judgment.
Never edit `.gitignore`, never commit from this skill, and never create a second Initiative worktree just to continue on another branch.
