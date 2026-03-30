---
name: using-git-worktrees
description: Use when starting feature work that needs isolation from current workspace or before executing implementation plans - creates isolated git worktrees with smart directory selection and safety verification
---

# Using Git Worktrees

## Overview

Git worktrees create isolated workspaces sharing the same repository, allowing work on multiple branches simultaneously without switching.

**Core principle:** Default to the configured global Codex worktree root, but honor explicit user overrides. Then apply safety verification.

**V1 isolation rule:** One Initiative uses one dedicated worktree. Milestone changes happen by switching the branch inside that Initiative worktree, not by creating a second worktree for the same Initiative.

**Naming principle:** Worktree names follow Initiative identity; branch names follow the current main closure boundary.

**Announce at start:** "I'm using the using-git-worktrees skill to bind or prepare an isolated workspace."

**Reuse rule:** This skill decides whether to reuse the current workspace or create a new worktree. Callers should not invent their own definition of a correctly bound or execution-ready Initiative workspace.

## Execution Modes

This skill supports two caller intents:

- `bind_only`: bind the active Initiative workspace and target branch so the caller may materialize workspace-local refs and inspect or recover runtime state. In this mode, do naming, location selection, ignore verification, reuse or worktree creation, and safe branch selection as needed, but do not run repo setup or baseline verification.
- `execution_ready`: first satisfy `bind_only`, then run repo-obvious setup and baseline verification before returning ready for execution.

If the caller explicitly names one of these modes, follow it. If the caller does not name a mode:

- default to `bind_only` when the caller only needs workspace identity for routing, recovery, or runtime-doc reads
- default to `execution_ready` when the caller is about to enter coder or reviewer execution work

## Naming Contract

Decide both the worktree name and the branch name before any reuse or worktree creation decision.

- If the user explicitly names a branch, use it as `BRANCH_NAME`.
- Otherwise if the current work item has a uniquely known `milestone-key`, derive `BRANCH_NAME` as `codex/<initiative-key>/<milestone-key>`.
- Otherwise derive `BRANCH_NAME` as `codex/<initiative-key>/initiative`.
- If the user explicitly names a worktree, honor that override.
- Otherwise derive `WORKTREE_NAME` as `codex/<initiative-key>`.
- Do not silently invent different names when `initiative-key` is missing. If `milestone-key` is missing, fall back to the Initiative branch instead of blocking.

If the target branch already exists and is already in use by another worktree:
- Stop and surface the conflict
- Ask for a different branch name or a different location only if needed

If the target branch already exists but is not attached to another worktree:
- Reuse that branch
- Do not invent a replacement branch name just because it already exists

## Reuse Current Workspace Or Create A Worktree

Before reusing the current workspace, first honor any explicit user location override.

If the user explicitly names a worktree location, that location wins. Do not reuse the current workspace instead just because it was already bound or prepared earlier in the workflow.

Only when there is no explicit user location override should you decide whether the current workspace is already the intended Initiative workspace for the requested mode.

You may reuse the current workspace only when one of these is true:
- It was already bound or prepared earlier in this same workflow by `forgeloop:using-git-worktrees`
- The user explicitly says the current workspace is the intended Initiative workspace to continue using

If neither condition is true, create a new worktree by following this skill.

If you reuse the current workspace:
- Confirm the current workspace is already the intended Initiative worktree
- Confirm the current branch is not `main` or `master`
- If the current branch already matches the intended `BRANCH_NAME`, continue
- If the current branch does not match but the workspace is clean enough to switch, switch or create the intended `BRANCH_NAME` in this same Initiative worktree
- If the workspace is not clean enough to switch branches safely, stop and surface the conflict
- In `bind_only`, stop here once workspace and branch binding are correct
- In `execution_ready`, verify the project setup and clean baseline for the current workspace before returning ready
- Report that the current Initiative worktree was reused instead of creating a new worktree

Do not let callers or local guesswork bypass this rule.

## Directory Selection Process

Follow this priority order:

### 1. Honor Explicit User Override

If the user explicitly names a worktree location, use it.

Supported explicit overrides:

- `.worktrees/`
- `worktrees/`
- `~/.codex/worktrees/<project-name>/`
- a custom absolute path or `~/`-prefixed root directory

If the user provides a custom root directory, create the worktree under:

```text
<custom-root>/<project-name>/<worktree-name>
```

### 2. Check AGENTS.md Preference

```bash
grep -i "worktree" AGENTS.md 2>/dev/null
```

**If preference specified:** Use it without asking.

### 3. Check Existing Directories

```bash
# Check in priority order
ls -d .worktrees 2>/dev/null     # Preferred (hidden)
ls -d worktrees 2>/dev/null      # Alternative
```

**If found:** Use that directory. If both exist, `.worktrees` wins.

### 4. Default To Global Codex Worktree Root

If there is no explicit user override, no `AGENTS.md` preference, and no project-local worktree directory, default to:

```text
~/.codex/worktrees/<project-name>/
```

Do not ask just to choose between `.worktrees/` and `~/.codex/worktrees/<project-name>/` when the default is already clear.

## Safety Verification

### For Project-Local Directories (.worktrees or worktrees)

**MUST verify the selected directory is ignored before creating worktree:**

```bash
# Check the selected directory only (respects local, global, and system gitignore)
git check-ignore -q "$LOCATION" 2>/dev/null
```

**If NOT ignored:**

Do not edit `.gitignore` or create a commit from this skill.

- If the project-local directory came from an explicit user override, stop and surface the problem. The directory must be ignored before it can be used.
- If the project-local directory was selected automatically from `AGENTS.md` or existing directories, do not mutate repository state here. Set `LOCATION` to `~/.codex/worktrees/<project-name>/` and continue with the global Codex worktree root instead.

**Why critical:** Prevents accidentally committing worktree contents to repository.

### For Global Directory (~/.codex/worktrees)

No .gitignore verification needed - outside project entirely.

## Creation Steps

### 1. Detect Project Name

```bash
project=$(basename "$(git rev-parse --show-toplevel)")
```

### 1.5. Reuse Current Workspace When Allowed

If the reuse rule above is satisfied, stay in the current workspace and skip worktree creation.

- If the current branch already matches the intended `BRANCH_NAME`, continue.
- If the current branch does not match but the workspace is clean enough to switch, switch or create the intended `BRANCH_NAME` in this same Initiative worktree.
- If the workspace is not clean enough to switch safely, stop and surface the conflict.

In `bind_only`, return once workspace and branch binding are confirmed.

In `execution_ready`, continue with project setup and baseline verification in the current workspace.

### 1.6. Decide Branch Name

`WORKTREE_NAME` and `BRANCH_NAME` should already be determined by the naming contract above before reaching creation steps.

### 2. Create Worktree

```bash
# Determine full path
case $LOCATION in
  .worktrees|worktrees)
    path="$LOCATION/$WORKTREE_NAME"
    ;;
  ~/.codex/worktrees/*)
    path="$HOME/.codex/worktrees/$project/$WORKTREE_NAME"
    ;;
  ~/*)
    path="${LOCATION/#\~/$HOME}/$project/$WORKTREE_NAME"
    ;;
  /*)
    path="$LOCATION/$project/$WORKTREE_NAME"
    ;;
esac

# Create parent directories when the worktree name contains nested segments
mkdir -p "$(dirname "$path")"

# If the Initiative worktree already exists, reuse it instead of creating a second one
if [ -d "$path" ]; then
  cd "$path"
  test -z "$(git status --porcelain)" || { echo "Existing Initiative worktree is not clean; stop and surface the conflict."; exit 1; }
  git checkout "$BRANCH_NAME" 2>/dev/null || git checkout -b "$BRANCH_NAME"
elif git worktree list --porcelain | grep -Fxq "branch refs/heads/$BRANCH_NAME"; then
  echo "Target branch is already attached to another worktree; stop and surface the conflict."
  exit 1
elif git show-ref --verify --quiet "refs/heads/$BRANCH_NAME"; then
  git worktree add "$path" "$BRANCH_NAME"
  cd "$path"
else
  # Create worktree with new branch
  git worktree add "$path" -b "$BRANCH_NAME"
  cd "$path"
fi
```

### 3. Run Project Setup (`execution_ready` only)

If the current mode is `bind_only`, skip this step.

Do not guess generic dependency installers.

First look for repo-documented or repo-obvious bootstrap commands. Prefer commands that respect an existing lockfile or existing tool contract, and avoid commands that may rewrite manifests or lockfiles just to prepare the workspace.

Examples when the repo clearly supports them:

```bash
# Node.js
if [ -f package-lock.json ]; then npm ci; fi

# Rust
if [ -f Cargo.toml ]; then cargo check; fi

# Python
# Use a repo-documented sync/bootstrap command only; do not guess between pip/poetry/uv.

# Go
# Usually no separate bootstrap step is needed before baseline verification.
```

If no setup command can be identified without guessing, stop and surface the gap instead of defaulting to `npm install`, `pip install -r requirements.txt`, `poetry install`, or similar generic installers.

### 4. Verify Clean Baseline (`execution_ready` only)

If the current mode is `bind_only`, skip this step.

Run the smallest repo-appropriate baseline verification after setup. Prefer commands already documented by the repo or already implied by the current project toolchain.

```bash
# Examples - use project-appropriate command
npm test
cargo test
pytest
go test ./...
```

If no baseline command can be uniquely determined, stop and surface the gap instead of pretending the workspace is ready.

**If tests fail:** Report failures, ask whether to proceed or investigate.

**If tests pass:** Report ready.

### 5. Report Location

In `bind_only`, report the bound workspace and branch without claiming execution readiness:

```
Workspace bound at <full-path>
Branch bound as <branch-name>
Ready for runtime-state reads or later execution preparation
```

In `execution_ready`, report readiness:

```
Worktree ready at <full-path>
Tests passing (<N> tests, 0 failures)
Ready to implement <feature-name>
```

## Quick Reference

| Situation | Action |
|-----------|--------|
| User explicitly names location | Use user override before considering reuse |
| User explicitly names branch | Use that branch name |
| No explicit branch provided and milestone known | Derive `BRANCH_NAME = codex/<initiative-key>/<milestone-key>` |
| No explicit branch provided and no milestone bound | Derive `BRANCH_NAME = codex/<initiative-key>/initiative` |
| No explicit worktree provided | Derive `WORKTREE_NAME = codex/<initiative-key>` |
| Branch already exists and is checked out elsewhere | Stop and surface conflict |
| Branch already exists but is free | Reuse that branch |
| Caller needs only runtime-state reads or recovery | Use `bind_only` |
| Caller is about to enter execution loop | Use `execution_ready` |
| Reusing current Initiative worktree on the wrong branch | Switch only if clean enough; otherwise stop |
| AGENTS.md specifies location | Use it |
| `.worktrees/` exists | Use it (verify ignored) |
| `worktrees/` exists | Use it (verify ignored) |
| Both exist | Use `.worktrees/` |
| No preference or local dir | Use `~/.codex/worktrees/<project-name>/` |
| Auto-selected local directory not ignored | Fall back to global Codex worktree root |
| Explicit local override not ignored | Stop and surface the problem |
| Initiative worktree path already exists | Reuse that Initiative worktree instead of creating a second one |
| Tests fail during baseline | Report failures + ask |
| No repo-obvious setup command | Stop and surface the gap |
| No baseline command can be identified | Stop and surface the gap |

## Common Mistakes

### Skipping ignore verification

- **Problem:** Worktree contents get tracked, pollute git status
- **Fix:** Always run `git check-ignore` on the selected project-local directory before creating the worktree

### Reusing the current workspace on the wrong branch

- **Problem:** Work starts on a branch that does not match the requested or derived target branch
- **Fix:** Reuse only inside the intended Initiative worktree, and switch branches only when the workspace is clean enough

### Mutating the repository during environment setup

- **Problem:** A setup skill unexpectedly edits `.gitignore` or creates a commit on the current branch
- **Fix:** Never commit from this skill; stop or fall back to the global worktree root

### Assuming directory location

- **Problem:** Creates inconsistency, violates project conventions
- **Fix:** Follow priority: user override > AGENTS.md > existing dirs > default global root

### Guessing a branch or worktree name

- **Problem:** Creates hidden branch drift and makes later cleanup confusing
- **Fix:** Use the explicit name, or derive `WORKTREE_NAME = codex/<initiative-key>` and `BRANCH_NAME` from the current main closure boundary; if milestone is unknown, fall back to `codex/<initiative-key>/initiative`

### Proceeding with failing tests

- **Problem:** Can't distinguish new bugs from pre-existing issues
- **Fix:** Report failures, get explicit permission to proceed

### Hardcoding setup commands

- **Problem:** Generic installers can mutate dependency state or guess the wrong toolchain
- **Fix:** Use repo-documented or repo-obvious bootstrap commands only; otherwise stop and surface the gap

## Example Workflow

```
You: I'm using the using-git-worktrees skill to bind or prepare an isolated workspace.

[Check .worktrees/ - exists]
[Verify ignored - git check-ignore confirms .worktrees/ is ignored]
[Decide worktree: codex/INIT-001]
[Decide branch: codex/INIT-001/MS-001]
[Create parent dir: mkdir -p .worktrees/codex]
[Create worktree: git worktree add .worktrees/codex/INIT-001 -b codex/INIT-001/MS-001]
[Run repo-obvious bootstrap: npm ci]
[Run npm test - 47 passing]

Worktree ready at /Users/jesse/myproject/.worktrees/codex/INIT-001
Tests passing (47 tests, 0 failures)
Ready to implement milestone MS-001 for Initiative INIT-001
```

## Red Flags

**Never:**
- Create worktree without verifying it's ignored (project-local)
- Edit `.gitignore` or create a commit from this skill
- Skip baseline test verification in `execution_ready`
- Proceed with failing tests without asking
- Assume directory location when ambiguous
- Override an explicit user location request with reuse logic
- Reuse a dirty Initiative worktree and switch branches without surfacing the conflict
- Silently pick a different branch after a conflict
- Skip AGENTS.md check

**Always:**
- Honor explicit user location overrides before reuse checks
- Decide the branch name before `git worktree add`
- Use `bind_only` when the caller only needs workspace identity for runtime-state reads or recovery
- Use `execution_ready` before entering coder or reviewer execution work
- Reuse the current Initiative worktree when possible, even if the branch needs to be switched, but only when the workspace is clean enough
- Reuse the current Initiative worktree when possible instead of creating a second worktree for the same Initiative
- Follow directory priority: user override > AGENTS.md > existing dirs > default global root
- Verify directory is ignored for project-local
- Use only repo-documented or repo-obvious setup commands
- Verify clean baseline or surface the gap

## Integration

**Called by:**
- **run-initiative** - use `bind_only` before reading workspace-local runtime docs, and upgrade to `execution_ready` only before entering `task-loop`, `milestone-loop`, or `initiative-loop`
- Any execution-side skill needing isolated workspace

**Pairs with:**
- **rebuild-runtime** - Use after workspace recovery only when the runtime control plane itself cannot be resumed directly
