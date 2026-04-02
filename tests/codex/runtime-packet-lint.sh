#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

check_pattern() {
  local file="$1"
  local pattern="$2"

  if ! rg -q "$pattern" "$file"; then
    echo "runtime packet lint: missing ${pattern} in ${file}"
    exit 1
  fi
}

check_pattern \
  "plugins/forgeloop/skills/references/anchor-addressing.md" \
  '`run-initiative/SKILL.md`, or `code-loop/SKILL.md`'
check_pattern \
  "plugins/forgeloop/skills/run-initiative/references/runtime-cutover.md" \
  'Ordinary coder / reviewer packets remain anchor-addressed minimal in every supported runtime mode'
check_pattern \
  "plugins/forgeloop/skills/code-loop/SKILL.md" \
  'Obey the shared packet law in `../references/anchor-addressing.md` and the runtime cutover law'

python3 - <<'PY'
import json
from pathlib import Path

scenarios = json.loads(Path("tests/codex/token-benchmark/fixtures/scenarios.json").read_text())
targets = {
    "Same-Task Same-Round Coder Continue",
    "Same-Task Handoff To Fresh Reviewer",
    "Milestone Review",
    "Initiative Review",
    "same-task warm-path delta legal",
    "same-task warm-path delta illegal -> full packet fallback",
    "selector legality failure -> full-doc fallback",
}
forbidden = {
    "plugins/forgeloop/skills/run-initiative/SKILL.md",
    "plugins/forgeloop/skills/code-loop/SKILL.md",
    "plugins/forgeloop/skills/task-loop/SKILL.md",
    "plugins/forgeloop/skills/milestone-loop/SKILL.md",
    "plugins/forgeloop/skills/initiative-loop/SKILL.md",
}
for scenario in scenarios:
    if scenario["name"] not in targets:
        continue

    promoted_non_agent_full_doc = False
    for item in scenario["minimal_packet"]:
        path = item.get("path") or item.get("doc")
        if path in forbidden:
            raise SystemExit(
                f"runtime packet lint: worker minimal packet still references supervisor skill doc in scenario {scenario['name']}: {path}"
            )
        if item.get("type") == "full_doc":
            if path == "docs/initiatives/active/anchor-sliced-dispatch-optimization/total-task-doc.md":
                raise SystemExit(
                    f"runtime packet lint: worker minimal packet still includes full Total Task Doc in scenario {scenario['name']}"
                )
            if path and not path.startswith("plugins/forgeloop/agents/"):
                promoted_non_agent_full_doc = True

    if promoted_non_agent_full_doc:
        if not scenario.get("minimal_fallback_mode"):
            raise SystemExit(
                f"runtime packet lint: missing minimal_fallback_mode for promoted worker packet in scenario {scenario['name']}"
            )
        if not scenario.get("minimal_fallback_reason"):
            raise SystemExit(
                f"runtime packet lint: missing minimal_fallback_reason for promoted worker packet in scenario {scenario['name']}"
            )
PY

echo "runtime packet lint passed"
