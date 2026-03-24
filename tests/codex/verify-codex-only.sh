#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

for path in \
  .claude-plugin \
  .cursor-plugin \
  .opencode \
  hooks \
  commands \
  agents \
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

for agent in \
  .codex/agents/design_challenger.toml \
  .codex/agents/implementer.toml \
  .codex/agents/spec_reviewer.toml \
  .codex/agents/code_reviewer.toml \
  .codex/agents/plan_reviewer.toml
do
  if [ ! -f "$agent" ]; then
    echo "missing custom agent: $agent"
    exit 1
  fi

  if ! rg -q '^name = ' "$agent" || ! rg -q '^description = ' "$agent" || ! rg -q '^developer_instructions = """' "$agent"; then
    echo "custom agent missing required fields: $agent"
    exit 1
  fi
done

if rg -n \
  -g 'README.md' \
  -g '.codex/INSTALL.md' \
  -g 'docs/forgeloop/install.md' \
  -g 'docs/forgeloop/testing.md' \
  -g '.codex/agents/*.toml' \
  -g 'scripts/install.sh' \
  -g 'skills/**/*.md' \
  -g '.github/**/*.md' \
  -g '!tests/codex/verify-codex-only.sh' \
  'Claude Code|OpenCode|Gemini CLI|Cursor|Skill tool|Task tool|TodoWrite|CLAUDE\.md|GEMINI\.md|~/.agents/skills|Superpowers|superpowers' \
  . >/tmp/forgeloop-codex-only-check.txt
then
  echo "forbidden platform terms found:"
  cat /tmp/forgeloop-codex-only-check.txt
  exit 1
fi

echo "codex-only verification passed"
