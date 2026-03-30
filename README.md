**Languages:** [English](README.md) | [Simplified Chinese](README.zh-CN.md)

# Forgeloop

Forgeloop is a Codex-only workflow layer built from composable skills. It turns Codex into a stricter engineering process: design first, plan second, implement in small verified steps, and review before moving on.

`0.2.0` is intentionally shipped as a Codex skill pack, not as a Python package.

## Origin

Forgeloop is built from a customized adaptation of [obra/superpowers](https://github.com/obra/superpowers). This repository keeps the core workflow idea, then narrows and rewires it for a Codex-only setup and this project's own engineering constraints.

## Workflow

1. `brainstorming` turns rough requests into a reviewed design.
2. `using-git-worktrees` creates an isolated workspace when the work should not happen in the current tree.
3. `writing-plans` converts the design into tiny, explicit implementation steps.
4. `run-initiative` is the runtime entry: it binds the active Initiative and resumes the correct closure loop.
5. `task-loop`, `milestone-loop`, and `initiative-loop` perform Task, Milestone, and Initiative closure; `flat-tasks-loop` remains available for bounded flat-plan execution.
6. `test-driven-development`, `requesting-code-review`, and `verification-before-completion` enforce quality gates during implementation.
7. `finishing-a-development-branch` handles merge, PR, keep, or discard decisions at the end.

These skills are meant to be mandatory workflow constraints, not optional suggestions.

The suite's custom agent manifests live in [`agents/`](agents). They now cover the planning roles `planner`, `design_reviewer`, `gap_reviewer`, and `plan_reviewer`, the runtime workflow roles `coder`, `task_reviewer`, `milestone_reviewer`, and `initiative_reviewer`, plus auxiliary roles such as `design_challenger` and `code_reviewer`. The installer materializes them into a target project's `.codex/agents/`.

## Installation

If you're inside this checkout, install with:

```bash
bash scripts/install.sh --yes
```

If you want a managed checkout in `~/.codex/forgeloop`, use:

```bash
git clone https://github.com/jiumem/forgeloop.git ~/.codex/forgeloop
bash ~/.codex/forgeloop/scripts/install.sh --yes --source ~/.codex/forgeloop
```

To enable the same agent layer in a Codex project:

```bash
bash ~/.codex/forgeloop/scripts/install.sh --yes --source ~/.codex/forgeloop --project-dir /path/to/project
```

Detailed setup notes live in [docs/forgeloop/install.md](docs/forgeloop/install.md).
The shipped custom agent set is documented in [docs/forgeloop/agents.md](docs/forgeloop/agents.md).

## Included Skills

**Planning and execution**
- `using-forgeloop`
- `brainstorming`
- `run-planning`
- `planning-loop` (internal planning stage skill)
- `writing-plans`
- `run-initiative`
- `task-loop`
- `milestone-loop`
- `initiative-loop`
- `flat-tasks-loop`
- `dispatching-parallel-agents`
- `using-git-worktrees`
- `finishing-a-development-branch`

**Quality**
- `test-driven-development`
- `requesting-code-review`
- `receiving-code-review`
- `verification-before-completion`
- `systematic-debugging`

## Verification

Codex-specific validation steps are documented in [docs/forgeloop/testing.md](docs/forgeloop/testing.md).

## Philosophy

- Test first.
- Prefer explicit plans over improvisation.
- Use isolated agents when tasks are independent.
- Review early so problems do not compound.
- Verify behavior instead of trusting claims.

## License

MIT License. See [LICENSE](LICENSE).
