# Codex E2E Verification

This document captures the manual end-to-end verification for Forgeloop skill loading in a real Codex runtime.

It is intentionally **not** a CI test. The goal is to verify Codex itself can discover, load, and follow the installed skills in a fresh session. That behavior depends on the host runtime, not only on repository files.

## When To Run

Run this checklist when:

- preparing a release
- changing install paths or skill layout
- changing `agents/`
- changing startup or workflow entry skills
- upgrading Codex and wanting to confirm runtime compatibility

You do not need to run it for every normal content edit.

## Preconditions

- `codex` CLI is installed and usable on the machine
- this repository has been installed with `bash scripts/install.sh --yes --source <repo>`
- the installed skill link exists at `~/.codex/skills/forgeloop`
- the target test repository has been enabled with `bash <repo>/scripts/install.sh --yes --source <repo> --project-dir <tmpdir>`

## Recommended Environment

Use a fresh temporary Git repository so the test does not rely on repo-local skill discovery from this checkout:

```bash
tmpdir=$(mktemp -d)
git init -q "$tmpdir"
bash ~/.codex/forgeloop/scripts/install.sh --yes --source ~/.codex/forgeloop --project-dir "$tmpdir"
```

Run all `codex exec` checks against that temporary directory with `-C "$tmpdir"`.

## Verification Cases

### 1. Planning Entry

Prompt:

```text
Use the run-planning skill. Reply with exactly the internal stage skill name that it dispatches and nothing else.
```

Expected result:

```text
planning-loop
```

Pass criteria:

- the response matches exactly
- Codex logs show it read `~/.codex/forgeloop/skills/run-planning/SKILL.md`

### 2. Planning Stage Author

Prompt:

```text
Use the planning-loop skill. Reply with exactly the continuous planning author role name that this skill dispatches.
```

Expected result:

```text
planner
```

Pass criteria:

- the response is exactly `planner`
- Codex logs show it read `~/.codex/forgeloop/skills/planning-loop/SKILL.md`

### 3. Runtime Recovery Dispatch

Prompt:

```text
Use the run-initiative skill. Reply with exactly the recovery skill name it calls when runtime state is missing or conflicts with formal docs.
```

Expected result:

```text
rebuild-runtime
```

Pass criteria:

- the response is exactly that skill name
- Codex logs show it read `~/.codex/forgeloop/skills/run-initiative/SKILL.md`

### 4. Task Review Dispatch

Prompt:

```text
Use the task-loop skill. Reply with exactly the custom reviewer agent name it dispatches for Task formal review.
```

Expected result:

```text
task_reviewer
```

Pass criteria:

- the response is exactly `task_reviewer`
- Codex logs show it read `~/.codex/forgeloop/skills/task-loop/SKILL.md`

## Example Commands

```bash
tmpdir=$(mktemp -d)
git init -q "$tmpdir"

codex exec -C "$tmpdir" --sandbox read-only --skip-git-repo-check \
  'Use the run-planning skill. Reply with exactly the internal stage skill name that it dispatches and nothing else.'

codex exec -C "$tmpdir" --sandbox read-only --skip-git-repo-check \
  'Use the planning-loop skill. Reply with exactly the continuous planning author role name that this skill dispatches.'

codex exec -C "$tmpdir" --sandbox read-only --skip-git-repo-check \
  'Use the run-initiative skill. Reply with exactly the recovery skill name it calls when runtime state is missing or conflicts with formal docs.'

codex exec -C "$tmpdir" --sandbox read-only --skip-git-repo-check \
  'Use the task-loop skill. Reply with exactly the custom reviewer agent name it dispatches for Task formal review.'
```

## Release Interpretation

This checklist is a **release verification step**, not a CI gate.

Release confidence is high when:

- install smoke test passes
- codex-only repository check passes
- this manual Codex E2E checklist passes in a fresh session

## Common Failure Modes

- `codex` answers without using the requested skill:
  likely install or discovery problem
- `~/.codex/skills/forgeloop` is missing or points to the wrong checkout:
  rerun the installer
- Codex reads repo-local files instead of installed files:
  rerun the test in a fresh temporary Git repository
- answer is close but not exact for exact-match checks:
  inspect the skill text or adjust the prompt if Codex runtime behavior changed
