**Languages:** [English](README.md) | [Simplified Chinese](README.zh-CN.md)

# Forgeloop

Forgeloop is a Codex-only workflow layer built from composable skills. It turns Codex into a stricter engineering process: design first, plan second, implement in small verified steps, and review before moving on.

`0.7.1` ships as a repo-local Codex plugin package. It is not a Python package.

## Origin

Forgeloop is built from a customized adaptation of [obra/superpowers](https://github.com/obra/superpowers). This repository keeps the core workflow idea, then narrows and rewires it for a Codex-only setup and this project's own engineering constraints.

## Workflow

1. `run-planning` is the planning entry: it binds the active Initiative's planning inputs plus minimum planning control plane, then routes into the confirmed planning stage.
2. `planning-loop` is the internal single-stage planning closure skill used by `run-planning`.
3. `run-initiative` is the runtime entry: it binds the active Initiative, runs planning admission, calls `using-git-worktrees` when needed, and resumes the correct closure loop.
4. `task-loop`, `milestone-loop`, and `initiative-loop` perform Task, Milestone, and Initiative closure.
5. `rebuild-runtime` recovers the runtime control plane when state is missing, conflicting, or cannot be resumed directly.

These skills are meant to be mandatory workflow constraints, not optional suggestions.

For repo-local Initiatives, both planning and runtime control-plane docs now default to an Initiative-local sibling `.forgeloop/` directory next to the Initiative documents.

The suite's custom agent manifests live in [`plugins/forgeloop/agents/`](plugins/forgeloop/agents). They cover the planning roles `planner`, `design_reviewer`, `gap_reviewer`, and `plan_reviewer`, plus the runtime workflow roles `coder`, `task_reviewer`, `milestone_reviewer`, and `initiative_reviewer`. Those manifests are materialized into Codex global agent storage by default, or into a target project's `.codex/agents/` when you pass `--project-dir`.

## Installation

Forgeloop installation has two separate steps:

1. Install the plugin in Codex.
2. Materialize the custom agents with the script below.

### 1. Install the plugin in Codex

This first step is interactive. Use either:

- the Codex desktop app Plugins directory, or
- the Codex CLI plugin picker via `/plugins`

Use this flow:

1. Restart Codex after pulling the latest repository state.
2. Open the Plugins directory in Codex.
3. Choose the repo marketplace `Forgeloop Local`.
4. Install the `Forgeloop` plugin.

### 2. Materialize the custom agents

After the plugin is installed, run:

```bash
bash plugins/forgeloop/scripts/materialize-agents.sh
```

That installs the Forgeloop custom agents into Codex global agent storage.

If you need a project-local override instead, run:

```bash
bash plugins/forgeloop/scripts/materialize-agents.sh --project-dir /path/to/project
```

The script does not install the plugin itself. Plugin installation is still an interactive Codex step.

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

## Release Notes

Release history lives in [CHANGELOG.md](CHANGELOG.md).

## Philosophy

- Test first.
- Prefer explicit plans over improvisation.
- Use isolated agents when tasks are independent.
- Review early so problems do not compound.
- Verify behavior instead of trusting claims.

## License

MIT License. See [LICENSE](LICENSE).
