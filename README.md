**Languages:** [English](README.md) | [Simplified Chinese](README.zh-CN.md)

# Forgeloop

Forgeloop is a Codex-only workflow layer built from composable skills. It turns Codex into a stricter engineering process: design first, plan second, implement in small verified steps, and review before moving on.

`0.3.0` is intentionally shipped as a Codex skill pack, not as a Python package.

## Origin

Forgeloop is built from a customized adaptation of [obra/superpowers](https://github.com/obra/superpowers). This repository keeps the core workflow idea, then narrows and rewires it for a Codex-only setup and this project's own engineering constraints.

## Workflow

1. `run-planning` is the planning entry: it binds the active Initiative planning surface and routes into the confirmed planning stage.
2. `planning-loop` is the internal single-stage planning closure skill used by `run-planning`.
3. `run-initiative` is the runtime entry: it binds the active Initiative, runs planning admission, calls `using-git-worktrees` when needed, and resumes the correct closure loop.
4. `task-loop`, `milestone-loop`, and `initiative-loop` perform Task, Milestone, and Initiative closure.
5. `rebuild-runtime` recovers the runtime control plane when state is missing, conflicting, or cannot be resumed directly.

These skills are meant to be mandatory workflow constraints, not optional suggestions.

The suite's custom agent manifests live in [`agents/`](agents). They cover the planning roles `planner`, `design_reviewer`, `gap_reviewer`, and `plan_reviewer`, plus the runtime workflow roles `coder`, `task_reviewer`, `milestone_reviewer`, and `initiative_reviewer`. The installer materializes them into a target project's `.codex/agents/`.

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

**Core Loop Skills**
- `run-planning`
- `planning-loop` (internal planning stage skill)
- `run-initiative`
- `using-git-worktrees`
- `rebuild-runtime`
- `task-loop`
- `milestone-loop`
- `initiative-loop`

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
