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

unexpected_paths=(
  skills/brainstorming
  skills/dispatching-parallel-agents
  skills/finishing-a-development-branch
  skills/flat-tasks-loop
  skills/receiving-code-review
  skills/requesting-code-review
  skills/systematic-debugging
  skills/test-driven-development
  skills/using-forgeloop
  skills/verification-before-completion
  skills/writing-plans
  agents/design_challenger.toml
  agents/code_reviewer.toml
  tests/brainstorm-server
)

for path in \
  .codex \
  .claude-plugin \
  .cursor-plugin \
  .opencode \
  hooks \
  commands \
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

if [ ! -f "scripts/install.sh" ]; then
  echo "missing install script: scripts/install.sh"
  exit 1
fi

for path in "${unexpected_paths[@]}"; do
  if [ -e "$path" ]; then
    echo "unexpected legacy path remains: $path"
    exit 1
  fi
done

for agent in "${expected_agents[@]}"; do
  agent_path="agents/${agent}.toml"

  if [ ! -f "$agent_path" ]; then
    echo "missing custom agent: $agent_path"
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

for agent_path in agents/*.toml; do
  agent_name="$(basename "$agent_path" .toml)"

  if [[ ! " ${expected_agents[*]} " =~ " ${agent_name} " ]]; then
    echo "unexpected custom agent file: $agent_path"
    exit 1
  fi
done

while IFS=':' read -r file agent; do
  if [ -z "$file" ]; then
    continue
  fi

  if ! rg -q "\`${agent}\`" "$file"; then
    echo "dispatch file does not reference expected agent ${agent}: $file"
    exit 1
  fi
done <<'EOF'
skills/run-planning/SKILL.md:planning-loop
skills/planning-loop/SKILL.md:planner
skills/planning-loop/SKILL.md:design_reviewer
skills/planning-loop/SKILL.md:gap_reviewer
skills/planning-loop/SKILL.md:plan_reviewer
skills/task-loop/SKILL.md:coder
skills/task-loop/SKILL.md:task_reviewer
skills/milestone-loop/SKILL.md:coder
skills/milestone-loop/SKILL.md:milestone_reviewer
skills/initiative-loop/SKILL.md:coder
skills/initiative-loop/SKILL.md:initiative_reviewer
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
skills/planning-loop/SKILL.md:request_reviewer_handoff
skills/planning-loop/SKILL.md:latest `planner_update` in the current round is the current planner intent
skills/planning-loop/references/planning-rolling-doc.md:request_reviewer_handoff
skills/planning-loop/references/planning-rolling-doc.md:only the latest appended matching block is actionable
skills/run-planning/SKILL.md:stay visible as a reopen route
skills/planning-loop/SKILL.md:planner_slot=planner
skills/planning-loop/SKILL.md:round=1
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
skills/task-loop/SKILL.md:handoff_id
skills/task-loop/SKILL.md:continue_task_coder_round
skills/milestone-loop/SKILL.md:enter_r2
skills/milestone-loop/SKILL.md:handoff_id
skills/initiative-loop/SKILL.md:mark_initiative_delivered
skills/initiative-loop/SKILL.md:initiative_delivered
skills/rebuild-runtime/SKILL.md:mark_initiative_delivered
skills/rebuild-runtime/SKILL.md:current object-local `round`
agents/coder.toml:request_reviewer_handoff
agents/initiative_reviewer.toml:mark_initiative_delivered
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
  -g 'docs/forgeloop/e2e-codex.md' \
  -g 'agents/*.toml' \
  -g 'scripts/install.sh' \
  -g 'skills/**/*.md' \
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
  -g 'agents/*.toml' \
  -g 'scripts/install.sh' \
  -g 'skills/**/*.md' \
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
