#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

expected_agents=(
  planner
  design_reviewer
  gap_reviewer
  plan_reviewer
  coder
  task_reviewer
  milestone_reviewer
  initiative_reviewer
)

expected_skills=(
  run-planning
  planning-loop
  run-initiative
  rebuild-runtime
  task-loop
  milestone-loop
  initiative-loop
  using-git-worktrees
)

unexpected_paths=(
  skills
  agents
  tests/brainstorm-server
)

for path in \
  .codex \
  .claude-plugin \
  .cursor-plugin \
  .opencode \
  hooks \
  commands \
  scripts/install.sh \
  scripts/install.ps1 \
  tests/claude-code \
  tests/opencode \
  tests/explicit-skill-requests \
  tests/skill-triggering \
  tests/subagent-driven-dev \
  GEMINI.md \
  gemini-extension.json \
  package.json \
  docs/README.opencode.md
do
  if [ -e "$path" ]; then
    echo "unexpected file remains: $path"
    exit 1
  fi
done

for path in "${unexpected_paths[@]}"; do
  if [ -e "$path" ]; then
    echo "unexpected legacy path remains: $path"
    exit 1
  fi
done

for agent in "${expected_agents[@]}"; do
  agent_path="plugins/forgeloop/agents/${agent}.toml"

  if [ ! -f "$agent_path" ]; then
    echo "missing packaged custom agent: $agent_path"
    exit 1
  fi

  if ! rg -q "^name = \"${agent}\"$" "$agent_path"; then
    echo "custom agent name mismatch: $agent_path"
    exit 1
  fi

  if ! rg -q '^description = ' "$agent_path" || ! rg -q '^developer_instructions = """' "$agent_path"; then
    echo "custom agent missing required fields: $agent_path"
    exit 1
  fi
done

for agent_path in plugins/forgeloop/agents/*.toml; do
  agent_name="$(basename "$agent_path" .toml)"

  if [[ ! " ${expected_agents[*]} " =~ " ${agent_name} " ]]; then
    echo "unexpected custom agent file: $agent_path"
    exit 1
  fi
done

for skill in "${expected_skills[@]}"; do
  skill_path="plugins/forgeloop/skills/${skill}"

  if [ ! -d "$skill_path" ]; then
    echo "missing packaged skill directory: $skill_path"
    exit 1
  fi
done

python3 - <<'PY'
import json
from pathlib import Path

plugin_manifest = Path("plugins/forgeloop/.codex-plugin/plugin.json")
marketplace_manifest = Path(".agents/plugins/marketplace.json")

if not plugin_manifest.is_file():
    raise SystemExit(f"missing plugin manifest: {plugin_manifest}")

if not marketplace_manifest.is_file():
    raise SystemExit(f"missing marketplace manifest: {marketplace_manifest}")

plugin = json.loads(plugin_manifest.read_text())
marketplace = json.loads(marketplace_manifest.read_text())

assert plugin["name"] == "forgeloop", plugin["name"]
assert plugin["skills"] == "./skills/", plugin["skills"]
assert marketplace["name"] == "forgeloop-local", marketplace["name"]

entries = marketplace.get("plugins", [])
assert isinstance(entries, list) and entries, "marketplace plugins missing"
entry = next((item for item in entries if item.get("name") == "forgeloop"), None)
assert entry is not None, "forgeloop marketplace entry missing"
assert entry["source"]["path"] == "./plugins/forgeloop", entry["source"]["path"]
assert entry["policy"]["installation"] == "AVAILABLE", entry["policy"]["installation"]
assert entry["policy"]["authentication"] == "ON_INSTALL", entry["policy"]["authentication"]
PY

if [ ! -f "plugins/forgeloop/scripts/materialize-agents.sh" ]; then
  echo "missing plugin materialization script"
  exit 1
fi

while IFS=':' read -r file agent; do
  if [ -z "$file" ]; then
    continue
  fi

  if ! rg -q "\`${agent}\`" "$file"; then
    echo "dispatch file does not reference expected agent ${agent}: $file"
    exit 1
  fi
done <<'EOF'
plugins/forgeloop/skills/run-planning/SKILL.md:planning-loop
plugins/forgeloop/skills/planning-loop/SKILL.md:planner
plugins/forgeloop/skills/planning-loop/SKILL.md:design_reviewer
plugins/forgeloop/skills/planning-loop/SKILL.md:gap_reviewer
plugins/forgeloop/skills/planning-loop/SKILL.md:plan_reviewer
plugins/forgeloop/skills/task-loop/SKILL.md:coder
plugins/forgeloop/skills/task-loop/SKILL.md:task_reviewer
plugins/forgeloop/skills/milestone-loop/SKILL.md:coder
plugins/forgeloop/skills/milestone-loop/SKILL.md:milestone_reviewer
plugins/forgeloop/skills/initiative-loop/SKILL.md:coder
plugins/forgeloop/skills/initiative-loop/SKILL.md:initiative_reviewer
EOF

while IFS=':' read -r file pattern; do
  if [ -z "$file" ]; then
    continue
  fi

  if ! rg -q "$pattern" "$file"; then
    echo "planning protocol check failed for ${file}: missing ${pattern}"
    exit 1
  fi
done <<'EOF'
plugins/forgeloop/skills/planning-loop/SKILL.md:request_reviewer_handoff
plugins/forgeloop/skills/planning-loop/SKILL.md:latest `planner_update` in the current round is the current planner intent
plugins/forgeloop/skills/planning-loop/references/planning-rolling-doc.md:request_reviewer_handoff
plugins/forgeloop/skills/planning-loop/references/planning-rolling-doc.md:only the latest appended matching block is actionable
plugins/forgeloop/skills/run-planning/SKILL.md:stay visible as a reopen route
plugins/forgeloop/skills/planning-loop/SKILL.md:planner_slot=planner
plugins/forgeloop/skills/planning-loop/SKILL.md:round=1
EOF

while IFS=':' read -r file pattern; do
  if [ -z "$file" ]; then
    continue
  fi

  if ! rg -q "$pattern" "$file"; then
    echo "runtime protocol check failed for ${file}: missing ${pattern}"
    exit 1
  fi
done <<'EOF'
plugins/forgeloop/skills/task-loop/SKILL.md:handoff_id
plugins/forgeloop/skills/task-loop/SKILL.md:continue_task_coder_round
plugins/forgeloop/skills/milestone-loop/SKILL.md:enter_r2
plugins/forgeloop/skills/milestone-loop/SKILL.md:handoff_id
plugins/forgeloop/skills/initiative-loop/SKILL.md:mark_initiative_delivered
plugins/forgeloop/skills/initiative-loop/SKILL.md:initiative_delivered
plugins/forgeloop/skills/rebuild-runtime/SKILL.md:mark_initiative_delivered
plugins/forgeloop/skills/rebuild-runtime/SKILL.md:current object-local `round`
plugins/forgeloop/agents/coder.toml:request_reviewer_handoff
plugins/forgeloop/agents/initiative_reviewer.toml:mark_initiative_delivered
EOF

while IFS=':' read -r file pattern; do
  if [ -z "$file" ]; then
    continue
  fi

  if ! rg -q "$pattern" "$file"; then
    echo "runtime model policy check failed for ${file}: missing ${pattern}"
    exit 1
  fi
done <<'EOF'
plugins/forgeloop/agents/coder.toml:^model = "gpt-5.3-codex"$
plugins/forgeloop/agents/coder.toml:^model_reasoning_effort = "high"$
plugins/forgeloop/agents/task_reviewer.toml:^model = "gpt-5.4"$
plugins/forgeloop/agents/task_reviewer.toml:^model_reasoning_effort = "medium"$
plugins/forgeloop/agents/milestone_reviewer.toml:^model = "gpt-5.4"$
plugins/forgeloop/agents/milestone_reviewer.toml:^model_reasoning_effort = "medium"$
plugins/forgeloop/agents/initiative_reviewer.toml:^model = "gpt-5.4"$
plugins/forgeloop/agents/initiative_reviewer.toml:^model_reasoning_effort = "medium"$
docs/forgeloop/agents.md:gpt-5.3-codex
docs/forgeloop/agents.md:gpt-5.4
docs/forgeloop/agents.md:Supervisor
EOF

if [ ! -f "docs/forgeloop/agents.md" ]; then
  echo "missing agent inventory doc: docs/forgeloop/agents.md"
  exit 1
fi

for agent in "${expected_agents[@]}"; do
  if ! rg -q "\`${agent}\`" docs/forgeloop/agents.md; then
    echo "agent inventory doc missing ${agent}"
    exit 1
  fi
done

if rg -n \
  -g 'README.md' \
  -g 'README.zh-CN.md' \
  -g 'docs/forgeloop/install.md' \
  -g 'docs/forgeloop/testing.md' \
  -g 'docs/forgeloop/agents.md' \
  -g 'plugins/forgeloop/.codex-plugin/plugin.json' \
  -g 'plugins/forgeloop/agents/*.toml' \
  -g 'plugins/forgeloop/scripts/materialize-agents.sh' \
  -g 'plugins/forgeloop/skills/**/*.md' \
  -g '.github/**/*.md' \
  -g '!tests/codex/verify-codex-only.sh' \
  'Claude Code|OpenCode|Gemini CLI|Cursor|Skill tool|Task tool|TodoWrite|CLAUDE\.md|GEMINI\.md|~/.agents/skills' \
  . >/tmp/forgeloop-codex-only-check.txt
then
  echo "forbidden platform terms found:"
  cat /tmp/forgeloop-codex-only-check.txt
  exit 1
fi

if rg -n \
  -g 'docs/forgeloop/*.md' \
  -g 'plugins/forgeloop/agents/*.toml' \
  -g 'plugins/forgeloop/skills/**/*.md' \
  -g '.github/**/*.md' \
  -g '!docs/forgeloop/agents.md' \
  'Superpowers|superpowers' \
  . >/tmp/forgeloop-brand-check.txt
then
  echo "unexpected historical brand terms found outside README attribution:"
  cat /tmp/forgeloop-brand-check.txt
  exit 1
fi

echo "codex-only verification passed"
