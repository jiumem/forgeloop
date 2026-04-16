**Languages:** [English](README.md) | [Simplified Chinese](README.zh-CN.md)

# Forgeloop

Forgeloop is a Codex-native engineering workflow for teams that want planning, execution, review, and recovery to run from explicit formal state instead of chat memory.

`1.0.0` ships as a repo-local Codex plugin package under [`plugins/forgeloop/`](plugins/forgeloop/). It is not a Python package and it is not a generic prompt collection.

## What 1.0 Is

Forgeloop 1.0 is a small formal workflow kernel built around:

- one planning control spine: `Planning State Doc`
- one runtime control spine: `Global State Doc`
- one planning dispatcher: `run-planning`
- one runtime dispatcher: `run-initiative`
- one single-stage planning loop: `planning-loop`
- one single-object runtime loop: `code-loop`

The workflow is strict by design:

- planning must seal before runtime may start
- cross-stage planning continuation requires reread plus explicit rebind
- runtime executes one bound object at a time
- object release does not automatically bind the next object
- recovery must come from formal docs, not from prior thread memory

## Core Model

### Planning Plane

- `run-planning` is the top entry.
- `planning-loop` closes exactly one bound stage: `design`, optional `gap_analysis`, or `total_task_doc`.
- `Planning State Doc` is the only planning-wide control spine.
- planning rolling docs carry round, handoff, review, seal, and reopen history, but not dispatcher truth.

### Runtime Plane

- `run-initiative` is the only runtime dispatcher that may bind the current runtime object.
- `code-loop` executes only the already bound object.
- legal runtime object kinds are only `task`, `milestone`, and `initiative`.
- `Global State Doc` is the only runtime-wide control spine.
- runtime review rolling docs carry object-local coder/reviewer truth, not dispatcher truth.

### Object Selection

Runtime does not persist a `frontier` plane. When the current object releases control, the release is written as runtime history, then `run-initiative` rereads formal truth and uses the shared runtime selector to bind the next object.

That selector lives in [`plugins/forgeloop/skills/run-initiative/references/runtime-object-selection.md`](plugins/forgeloop/skills/run-initiative/references/runtime-object-selection.md).

## Shipped Surface

### Skills

- `run-planning`: top-level planning dispatcher
- `planning-loop`: single-stage planning closure
- `run-initiative`: top-level runtime dispatcher
- `code-loop`: unified runtime object executor
- `rebuild-runtime`: runtime control-plane recovery
- `using-git-worktrees`: workspace binding and execution readiness

### Agents

Forgeloop ships a narrow custom role layer under [`plugins/forgeloop/agents/`](plugins/forgeloop/agents/):

- planning: `planner`, `design_reviewer`, `gap_reviewer`, `total_task_doc_reviewer`
- runtime: `coder`, `task_reviewer`, `milestone_reviewer`, `initiative_reviewer`

Skills own dispatch policy and packet construction. Agent manifests own role behavior. Formal truth keeps only durable slot and state fields; session-local reusable worker bindings never become control-plane truth.

## Repository Layout

- [`plugins/forgeloop/skills/`](plugins/forgeloop/skills/) is the shipped workflow surface.
- [`plugins/forgeloop/agents/`](plugins/forgeloop/agents/) is the shipped custom role layer.
- [`plugins/forgeloop/scripts/`](plugins/forgeloop/scripts/) contains bundle, validation, and install helpers.
- [`docs/forgeloop/`](docs/forgeloop/) contains install, agent, testing, and release-facing support docs.
- [`tests/codex/`](tests/codex/) contains Codex-only release gates and benchmarks.

For repo-local Initiatives, the only legal control-plane root is a sibling `.forgeloop/` directory next to the Initiative docs.

## Install

Forgeloop installation has two steps:

1. install the plugin in Codex
2. materialize the custom agents

Install flow:

1. Pull the latest repository state.
2. Restart Codex so it reloads the repo marketplace.
3. Open the Codex Plugins directory or CLI plugin picker.
4. Choose the repo marketplace `Forgeloop Local`.
5. Install the `Forgeloop` plugin.
6. Materialize the shipped agents:

```bash
bash plugins/forgeloop/scripts/materialize-agents.sh
```

For a project-local override:

```bash
bash plugins/forgeloop/scripts/materialize-agents.sh --project-dir /path/to/project
```

More detail lives in [docs/forgeloop/install.md](docs/forgeloop/install.md) and [docs/forgeloop/agents.md](docs/forgeloop/agents.md).

## Release Validation

The 1.0 release surface is guarded by Codex-only checks under [`tests/codex/`](tests/codex/). The minimum release gate is documented in [docs/forgeloop/testing.md](docs/forgeloop/testing.md) and currently includes:

- `bash tests/codex/p0-validation.sh`
- `bash tests/codex/plugin-smoke.sh`
- `bash tests/codex/verify-codex-only.sh`

Formal loop bundles are exported with:

```bash
python3 plugins/forgeloop/scripts/export_formal_loops_bundle.py
```

## Who This Is For

Forgeloop fits teams that want:

- explicit planning before execution
- durable control state instead of “just continue from chat”
- runtime recovery from formal docs
- object-local review and acceptance gates
- a Codex-native workflow with narrow agent roles

It is not aimed at lightweight prompt-only usage or ad hoc one-shot coding sessions.

## Versioning

Release history lives in [CHANGELOG.md](CHANGELOG.md).

## License

MIT. See [LICENSE](LICENSE).
