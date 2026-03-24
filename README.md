**Languages:** [English](README.md) | [简体中文](README.zh-CN.md)

# Forgeloop

Forgeloop is a Codex-only workflow layer built from composable skills. It turns Codex into a stricter engineering process: design first, plan second, implement in small verified steps, and review before moving on.

`0.1.1` is intentionally shipped as a Codex skill pack, not as a Python package.

## Origin

Forgeloop is built from a customized adaptation of [obra/superpowers](https://github.com/obra/superpowers). This repository keeps the core workflow idea, then narrows and rewires it for a Codex-only setup and this project's own engineering constraints.

## Workflow

1. `brainstorming` turns rough requests into a reviewed design.
2. `using-git-worktrees` creates an isolated workspace when the work should not happen in the current tree.
3. `writing-plans` converts the design into tiny, explicit implementation steps.
4. `task-loop` or `flat-tasks-loop` carries out the plan.
5. `test-driven-development`, `requesting-code-review`, and `verification-before-completion` enforce quality gates during implementation.
6. `finishing-a-development-branch` handles merge, PR, keep, or discard decisions at the end.

These skills are meant to be mandatory workflow constraints, not optional suggestions.

Project-scoped custom agents live in [`.codex/agents`](.codex/agents). They handle bounded roles such as `design_challenger`, `plan_reviewer`, `implementer`, `spec_reviewer`, and `code_reviewer`.

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

Detailed setup notes live in [docs/forgeloop/install.md](docs/forgeloop/install.md).
The shipped custom agent set is documented in [docs/forgeloop/agents.md](docs/forgeloop/agents.md).

## Included Skills

**Planning and execution**
- `using-forgeloop`
- `brainstorming`
- `writing-plans`
- `task-loop`
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
