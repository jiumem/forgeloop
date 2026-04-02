# Forgeloop for Codex

Forgeloop `0.7.1` installs through a repo-local Codex plugin package at `plugins/forgeloop/`. It remains a Codex-native workflow layer rather than a Python package.

For repo-local Initiatives, the only legal planning and runtime control-plane root is a sibling `.forgeloop/` directory next to the Initiative documents.

## Install

Use this path when you are working inside this repository in the Codex app.

1. Clone or update the repository.
2. Restart Codex so it reloads the repo marketplace at `.agents/plugins/marketplace.json`.
3. Open the Plugins directory in Codex.
4. Choose the repo marketplace `Forgeloop Local`.
5. Install the `Forgeloop` plugin.
6. Materialize the custom agent manifests into Codex global agent storage:

```bash
bash plugins/forgeloop/scripts/materialize-agents.sh
```

7. If a specific project should use a project-local override instead, materialize into that project explicitly:

```bash
bash plugins/forgeloop/scripts/materialize-agents.sh --project-dir /path/to/project
```

## What the plugin installs

- The plugin exposes the distributable skill mirror under `plugins/forgeloop/skills/`.
- The plugin marketplace entry lives at `.agents/plugins/marketplace.json`.
- The plugin keeps a distributable copy of the custom agent manifests under `plugins/forgeloop/agents/`.

## What still needs a manual step

Codex plugins currently cover the installable workflow bundle, but Forgeloop still relies on custom agent manifests. Installing the plugin does not by itself populate either global Codex agent storage or a project-local `.codex/agents/`, so you must run `materialize-agents.sh` once after install.

## Updating

1. Pull the latest repository changes.
2. Restart Codex so it reloads the repo marketplace and plugin files.
3. Re-run the global agent materialization step:

```bash
bash plugins/forgeloop/scripts/materialize-agents.sh
```

4. If you use project-local overrides, re-run the project-scoped form for each affected project:

```bash
bash plugins/forgeloop/scripts/materialize-agents.sh --project-dir /path/to/project
```

## Uninstalling

1. Uninstall `Forgeloop` from the Codex Plugins directory.
2. Remove the global agent manifests if you no longer want the role layer:

```bash
rm -f "${CODEX_HOME:-$HOME/.codex}/agents/"{planner,design_reviewer,gap_reviewer,plan_reviewer,coder,task_reviewer,milestone_reviewer,initiative_reviewer}.toml
```

3. If you also created project-local overrides, remove those copies too:

```bash
rm -f /path/to/project/.codex/agents/{planner,design_reviewer,gap_reviewer,plan_reviewer,coder,task_reviewer,milestone_reviewer,initiative_reviewer}.toml
```

## Troubleshooting

If the plugin does not show up:

1. Check the repo marketplace exists: `cat .agents/plugins/marketplace.json`
2. Check the plugin manifest exists: `cat plugins/forgeloop/.codex-plugin/plugin.json`
3. Restart Codex after pulling the latest repository state

If the custom agents do not show up globally:

1. Re-run `bash plugins/forgeloop/scripts/materialize-agents.sh`
2. Check global agents exist: `find "${CODEX_HOME:-$HOME/.codex}/agents" -maxdepth 1 -name '*.toml'`

If the custom agents do not show up in a project-local override:

1. Re-run `bash plugins/forgeloop/scripts/materialize-agents.sh --project-dir /path/to/project`
2. Check project agents exist: `find /path/to/project/.codex/agents -maxdepth 1 -name '*.toml'`
