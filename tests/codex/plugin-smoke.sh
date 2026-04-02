#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TMP_ROOT="$(mktemp -d)"
trap 'rm -rf "$TMP_ROOT"' EXIT

PROJECT_DIR="${TMP_ROOT}/project"
CODEX_HOME_DIR="${TMP_ROOT}/codex-home"
mkdir -p "${PROJECT_DIR}"

cd "${ROOT}"

python3 - <<'PY'
import json
from pathlib import Path

root = Path(".")
plugin_manifest = root / "plugins" / "forgeloop" / ".codex-plugin" / "plugin.json"
marketplace_manifest = root / ".agents" / "plugins" / "marketplace.json"

plugin = json.loads(plugin_manifest.read_text())
marketplace = json.loads(marketplace_manifest.read_text())

assert plugin["name"] == "forgeloop", plugin["name"]
assert plugin["version"] == "0.6.0", plugin["version"]
assert plugin["skills"] == "./skills/", plugin["skills"]

entry = next(item for item in marketplace["plugins"] if item["name"] == "forgeloop")
assert marketplace["name"] == "forgeloop-local", marketplace["name"]
assert entry["source"]["path"] == "./plugins/forgeloop", entry["source"]["path"]
assert entry["policy"]["installation"] == "AVAILABLE", entry["policy"]["installation"]
assert entry["policy"]["authentication"] == "ON_INSTALL", entry["policy"]["authentication"]
PY

for skill in run-planning planning-loop run-initiative rebuild-runtime task-loop milestone-loop initiative-loop using-git-worktrees; do
  if [ ! -f "${ROOT}/plugins/forgeloop/skills/${skill}/SKILL.md" ]; then
    echo "packaged skill missing: ${skill}"
    exit 1
  fi
done

for agent in planner design_reviewer gap_reviewer plan_reviewer coder task_reviewer milestone_reviewer initiative_reviewer; do
  if [ ! -f "${ROOT}/plugins/forgeloop/agents/${agent}.toml" ]; then
    echo "packaged agent missing: ${agent}"
    exit 1
  fi
done

CODEX_HOME="${CODEX_HOME_DIR}" bash "${ROOT}/plugins/forgeloop/scripts/materialize-agents.sh"

for agent in planner design_reviewer gap_reviewer plan_reviewer coder task_reviewer milestone_reviewer initiative_reviewer; do
  if [ ! -f "${CODEX_HOME_DIR}/agents/${agent}.toml" ]; then
    echo "global agent was not materialized: ${agent}"
    exit 1
  fi
done

bash "${ROOT}/plugins/forgeloop/scripts/materialize-agents.sh" --project-dir "${PROJECT_DIR}"

for agent in planner design_reviewer gap_reviewer plan_reviewer coder task_reviewer milestone_reviewer initiative_reviewer; do
  if [ ! -f "${PROJECT_DIR}/.codex/agents/${agent}.toml" ]; then
    echo "project agent was not materialized: ${agent}"
    exit 1
  fi
done

echo "plugin smoke test passed"
