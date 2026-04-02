#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

check_pattern() {
  local file="$1"
  local pattern="$2"

  if ! rg -q "$pattern" "$file"; then
    echo "planning runner regression: missing ${pattern} in ${file}"
    exit 1
  fi
}

check_pattern \
  "plugins/forgeloop/skills/run-planning/SKILL.md" \
  'Sequential redispatch after `planning-loop` returns is allowed'
check_pattern \
  "plugins/forgeloop/skills/run-planning/SKILL.md" \
  'same activation after state refresh'
check_pattern \
  "plugins/forgeloop/skills/run-planning/SKILL.md" \
  'reread the `Planning State Doc` and the minimum formal planning truth needed for that route'
check_pattern \
  "plugins/forgeloop/skills/run-planning/SKILL.md" \
  'explicitly bind the target stage from `last_transition`, then go back to Step 2 in the same activation'
check_pattern \
  "plugins/forgeloop/skills/run-planning/SKILL.md" \
  'one activation may legally advance across multiple planning stages'

echo "planning runner regression passed"
