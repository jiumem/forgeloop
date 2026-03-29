#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

expected_agents=(
  design_challenger
  plan_reviewer
  coder
  task_reviewer
  milestone_reviewer
  initiative_reviewer
  code_reviewer
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
skills/brainstorming/SKILL.md:design_challenger
skills/brainstorming/design-challenger-prompt.md:design_challenger
skills/writing-plans/SKILL.md:plan_reviewer
skills/writing-plans/plan-document-reviewer-prompt.md:plan_reviewer
skills/task-loop/SKILL.md:coder
skills/task-loop/SKILL.md:task_reviewer
skills/milestone-loop/SKILL.md:coder
skills/milestone-loop/SKILL.md:milestone_reviewer
skills/initiative-loop/SKILL.md:coder
skills/initiative-loop/SKILL.md:initiative_reviewer
skills/requesting-code-review/SKILL.md:code_reviewer
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
