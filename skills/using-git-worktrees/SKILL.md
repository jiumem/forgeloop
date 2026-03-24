---
name: using-git-worktrees
description: Use when starting feature work that needs isolation from current workspace or before executing implementation plans - creates isolated git worktrees with smart directory selection and safety verification
---

# Using Git Worktrees

## Overview

Git worktrees create isolated workspaces sharing the same repository, allowing work on multiple branches simultaneously without switching.

**Core principle:** Default to the configured global Codex worktree root, but honor explicit user overrides. Then apply safety verification.

**Announce at start:** "I'm using the using-git-worktrees skill to set up an isolated workspace."

**Reuse rule:** This skill decides whether to reuse the current workspace or create a new worktree. Callers should not invent their own definition of a "safe isolated workspace."

## Branch Naming Contract

Decide the branch name before any reuse or worktree creation decision.

- If the user explicitly names a branch, use it.
- Otherwise derive `BRANCH_NAME` as `codex/<feature-slug>`.
- Use a short, stable slug based on the feature or task name.
- Do not silently invent a different branch name when the chosen one already exists or is already checked out elsewhere.

If the target branch already exists or is already in use by another worktree:
- Stop and surface the conflict
- Ask for a different branch name or a different location only if needed

## Reuse Current Workspace Or Create A Worktree

Before reusing the current workspace, first honor any explicit user location override.

If the user explicitly names a worktree location, that location wins. Do not reuse the current workspace instead just because it was prepared earlier in the workflow.

Only when there is no explicit user location override should you decide whether the current workspace is already a prepared implementation environment.

You may reuse the current workspace only when one of these is true:
- It was already prepared earlier in this same workflow by `forgeloop:using-git-worktrees`
- The user explicitly says the current workspace is the prepared environment to continue using

If neither condition is true, create a new worktree by following this skill.

If you reuse the current workspace:
- Confirm the current branch is not `main` or `master`
- Confirm the current branch already matches the intended `BRANCH_NAME`
- Verify the project setup and clean baseline for the current workspace before returning ready
- Report that the current workspace was reused instead of creating a new worktree

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
<custom-root>/<project-name>/<branch-name>
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

If the reuse rule above is satisfied, stay in the current workspace and skip worktree creation. Only do this when the current branch already matches the intended `BRANCH_NAME`. Then continue with project setup and baseline verification in the current workspace.

### 1.6. Decide Branch Name

`BRANCH_NAME` should already be determined by the branch naming contract above before reaching creation steps.

### 2. Create Worktree

```bash
# Determine full path
case $LOCATION in
  .worktrees|worktrees)
    path="$LOCATION/$BRANCH_NAME"
    ;;
  ~/.codex/worktrees/*)
    path="$HOME/.codex/worktrees/$project/$BRANCH_NAME"
    ;;
  ~/*)
    path="${LOCATION/#\~/$HOME}/$project/$BRANCH_NAME"
    ;;
  /*)
    path="$LOCATION/$project/$BRANCH_NAME"
    ;;
esac

# Create worktree with new branch
git worktree add "$path" -b "$BRANCH_NAME"
cd "$path"
```

### 3. Run Project Setup

Auto-detect and run appropriate setup:

```bash
# Node.js
if [ -f package.json ]; then npm install; fi

# Rust
if [ -f Cargo.toml ]; then cargo build; fi

# Python
if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
if [ -f pyproject.toml ]; then poetry install; fi

# Go
if [ -f go.mod ]; then go mod download; fi
```

### 4. Verify Clean Baseline

Run tests to ensure worktree starts clean:

```bash
# Examples - use project-appropriate command
npm test
cargo test
pytest
go test ./...
```

**If tests fail:** Report failures, ask whether to proceed or investigate.

**If tests pass:** Report ready.

### 5. Report Location

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
| No explicit branch provided | Derive `codex/<feature-slug>` |
| Branch already exists or is checked out elsewhere | Stop and surface conflict |
| Reusing current workspace on the wrong branch | Stop and surface conflict |
| AGENTS.md specifies location | Use it |
| `.worktrees/` exists | Use it (verify ignored) |
| `worktrees/` exists | Use it (verify ignored) |
| Both exist | Use `.worktrees/` |
| No preference or local dir | Use `~/.codex/worktrees/<project-name>/` |
| Auto-selected local directory not ignored | Fall back to global Codex worktree root |
| Explicit local override not ignored | Stop and surface the problem |
| Tests fail during baseline | Report failures + ask |
| No package.json/Cargo.toml | Skip dependency install |

## Common Mistakes

### Skipping ignore verification

- **Problem:** Worktree contents get tracked, pollute git status
- **Fix:** Always run `git check-ignore` on the selected project-local directory before creating the worktree

### Reusing the current workspace on the wrong branch

- **Problem:** Work starts on a branch that does not match the requested or derived target branch
- **Fix:** Reuse only when the current branch already equals `BRANCH_NAME`

### Mutating the repository during environment setup

- **Problem:** A setup skill unexpectedly edits `.gitignore` or creates a commit on the current branch
- **Fix:** Never commit from this skill; stop or fall back to the global worktree root

### Assuming directory location

- **Problem:** Creates inconsistency, violates project conventions
- **Fix:** Follow priority: user override > AGENTS.md > existing dirs > default global root

### Guessing a branch name after collision

- **Problem:** Creates hidden branch drift and makes later cleanup confusing
- **Fix:** Use the explicit name or derived `codex/<feature-slug>`, then stop if it conflicts

### Proceeding with failing tests

- **Problem:** Can't distinguish new bugs from pre-existing issues
- **Fix:** Report failures, get explicit permission to proceed

### Hardcoding setup commands

- **Problem:** Breaks on projects using different tools
- **Fix:** Auto-detect from project files (package.json, etc.)

## Example Workflow

```
You: I'm using the using-git-worktrees skill to set up an isolated workspace.

[Check .worktrees/ - exists]
[Verify ignored - git check-ignore confirms .worktrees/ is ignored]
[Decide branch: codex/auth]
[Create worktree: git worktree add .worktrees/codex/auth -b codex/auth]
[Run npm install]
[Run npm test - 47 passing]

Worktree ready at /Users/jesse/myproject/.worktrees/codex/auth
Tests passing (47 tests, 0 failures)
Ready to implement auth feature
```

## Red Flags

**Never:**
- Create worktree without verifying it's ignored (project-local)
- Edit `.gitignore` or create a commit from this skill
- Skip baseline test verification
- Proceed with failing tests without asking
- Assume directory location when ambiguous
- Override an explicit user location request with reuse logic
- Reuse the current workspace on a different branch than `BRANCH_NAME`
- Silently pick a different branch after a conflict
- Skip AGENTS.md check

**Always:**
- Honor explicit user location overrides before reuse checks
- Decide the branch name before `git worktree add`
- Reuse the current workspace only when its branch already matches `BRANCH_NAME`
- Follow directory priority: user override > AGENTS.md > existing dirs > default global root
- Verify directory is ignored for project-local
- Auto-detect and run project setup
- Verify clean test baseline

## Integration

**Called by:**
- **brainstorming** - Use when approved work should move into an isolated implementation workspace
- **task-loop** - REQUIRED before executing any tasks
- **flat-tasks-loop** - REQUIRED before executing any tasks
- Any skill needing isolated workspace

**Pairs with:**
- **finishing-a-development-branch** - REQUIRED for cleanup after work complete
