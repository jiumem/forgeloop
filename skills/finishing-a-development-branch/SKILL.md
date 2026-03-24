---
name: finishing-a-development-branch
description: Use when implementation is complete, all tests pass, and you need to finish the branch by confirming and executing the right integration action
---

# Finishing a Development Branch

## Overview

Guide completion of development work by recommending one finish action, asking for confirmation, and then executing it safely.

**Core principle:** Verify → Recommend → Confirm → Execute → Clean up only when appropriate.

**Boundary rule:** This skill is a branch-finishing protocol, not a generic git recipe. Use workflow context to identify the target branch, reuse the milestone's verification bar, and separate the feature worktree from the safe integration location where merge or branch deletion happens.

**Announce at start:** "I'm using the finishing-a-development-branch skill to complete this work."

## The Process

### Step 1: Verify Tests

Before recommending any finish action, rerun the milestone's required verification commands and confirm they pass.

```bash
<milestone verification commands>
```

If the repository requires broader verification before merge or PR, run that too.

If verification fails:
```
Tests failing (<N> failures). Must fix before completing:

[Show failures]

Cannot proceed with merge/PR until tests pass.
```

Stop. Do not proceed to Step 2. This skill does not repair implementation or reopen task execution.

Return control to the upstream workflow with the failed verification evidence so the main agent can decide whether to reopen the relevant task, rerun the milestone loop, or ask the user for direction.

If verification passes, continue to Step 2.

### Step 2: Determine Target Branch

Determine the target integration branch before presenting options.

Use this order:

1. Use the branch already established by the workflow or plan, if one exists
2. Otherwise infer from the repository's default integration branch, usually `main` or `master`
3. If the target branch is still unclear, ask the user before proceeding

Do not treat `git merge-base` output as a branch name. Use ancestry checks only as supporting evidence, not as the branch identifier shown to the user.

### Step 3: Recommend One Finish Action

Recommend exactly one action. Do not present a menu by default.

Use this order:

- Recommend **push and create a PR** by default when the branch should be reviewed or shared
- Recommend **merge locally** only when the repository is local-only or the user already indicated they want a local merge
- Use **keep as-is** only when the user explicitly wants to leave the branch for later
- Use **discard** only when the user explicitly wants to abandon the work

Ask for confirmation in one concise message, for example:

```text
Implementation complete. Recommended next step: push this branch and create a PR against <target-branch>.
Reply `confirm` to proceed, or tell me the different finish action you want.
```

If the user rejects the recommendation, switch to the requested finish action and confirm that instead.

### Step 4: Execute the Confirmed Action

#### Merge Locally

First move to a safe integration location that is not the feature branch's linked worktree. Use the main repository checkout or another workspace that is not attached to the feature branch.

```bash
git checkout <target-branch>
git pull
git merge <feature-branch>
<milestone verification commands>
git branch -d <feature-branch>
```

Then clean up the feature worktree.

#### Push and Create PR

```bash
git push -u origin <feature-branch>
gh pr create --title "<title>" --body "$(cat <<'EOF'
## Summary
<2-3 bullets of what changed>

## Test Plan
- [ ] <verification steps>
EOF
)"
```

Report the pushed branch and PR result. Keep the feature worktree.

#### Keep As-Is

Report: "Keeping branch <name>. Worktree preserved at <path>."

Do not clean up the feature worktree.

#### Discard

Require exact confirmation first:

```
This will permanently delete:
- Branch <name>
- All commits: <commit-list>
- Worktree at <path>

Type 'discard' to confirm.
```

Do not continue without the exact word `discard`.

First move to a safe integration location that is not the feature branch's linked worktree. Use the main repository checkout or another workspace that is not attached to the feature branch.

```bash
git checkout <target-branch>
git branch -D <feature-branch>
```

Then clean up the feature worktree.

### Step 5: Cleanup Worktree

Clean up only after a successful local merge or a confirmed discard.

Never remove the current safe integration location. Remove only the feature worktree path associated with `<feature-branch>`.

Locate the feature worktree directly:
```bash
git worktree list
```

If the feature worktree path is present:
```bash
git worktree remove <worktree-path>
```

Keep the worktree for PR or keep-as-is flows.

## Red Flags

**Never:**
- Proceed with failing tests
- Merge without verifying tests on result
- Delete work without confirmation
- Force-push without explicit request
- Present a full menu by default when one best-practice recommendation is clear

**Always:**
- Verify tests before recommending a finish action
- Recommend one best-practice action first
- Get exact `discard` confirmation before destructive cleanup
- Clean up worktree only after local merge or discard

## Used By

- **forgeloop:flat-tasks-loop** - After the flattened milestone is complete
- Manual broader completion by the main agent - When broader work is complete outside the flattened dispatcher
