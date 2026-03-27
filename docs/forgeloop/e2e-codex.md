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

### 1. Startup Skill

Prompt:

```text
Use the using-forgeloop skill. Reply with exactly the sentence inside the SUBAGENT-STOP block and nothing else.
```

Expected result:

```text
If you were dispatched as a subagent to execute a specific task, skip this skill.
```

Pass criteria:

- the response matches exactly
- Codex logs show it read `~/.codex/forgeloop/skills/using-forgeloop/SKILL.md`

### 2. Brainstorming Gate

Prompt:

```text
Use the brainstorming skill. Reply with one sentence describing the hard gate in that skill, with no bullet points.
```

Expected result:

- the reply clearly states that no implementation work may begin until a design has been presented and approved

Pass criteria:

- the answer reflects the hard gate from the skill
- Codex logs show it read `~/.codex/forgeloop/skills/brainstorming/SKILL.md`

### 3. Writing Plans Skill

Prompt:

```text
Use the writing-plans skill. Reply with exactly the required sub-skill name that plan headers must mention for agentic workers.
```

Expected result:

```text
forgeloop:task-loop
```

Pass criteria:

- the response is exactly that skill name
- Codex logs show it read `~/.codex/forgeloop/skills/writing-plans/SKILL.md`

### 4. Code Review Dispatch

Prompt:

```text
Use the requesting-code-review skill. Reply with exactly the custom agent name that this skill dispatches.
```

Expected result:

```text
code_reviewer
```

Pass criteria:

- the response is exactly `code_reviewer`
- Codex logs show it read `~/.codex/forgeloop/skills/requesting-code-review/SKILL.md`

## Example Commands

```bash
tmpdir=$(mktemp -d)
git init -q "$tmpdir"

codex exec -C "$tmpdir" --sandbox read-only --skip-git-repo-check \
  'Use the using-forgeloop skill. Reply with exactly the sentence inside the SUBAGENT-STOP block and nothing else.'

codex exec -C "$tmpdir" --sandbox read-only --skip-git-repo-check \
  'Use the brainstorming skill. Reply with one sentence describing the hard gate in that skill, with no bullet points.'

codex exec -C "$tmpdir" --sandbox read-only --skip-git-repo-check \
  'Use the writing-plans skill. Reply with exactly the required sub-skill name that plan headers must mention for agentic workers.'

codex exec -C "$tmpdir" --sandbox read-only --skip-git-repo-check \
  'Use the requesting-code-review skill. Reply with exactly the custom agent name that this skill dispatches.'
```

## Release Interpretation

This checklist is a **release verification step**, not a CI gate.

Release confidence is high when:

- install smoke test passes
- codex-only repository check passes
- brainstorm server integration test passes
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
