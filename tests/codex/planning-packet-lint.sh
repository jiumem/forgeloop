#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

check_pattern() {
  local file="$1"
  local pattern="$2"

  if ! rg -q "$pattern" "$file"; then
    echo "planning packet lint: missing ${pattern} in ${file}"
    exit 1
  fi
}

check_pattern \
  "plugins/forgeloop/skills/planning-loop/SKILL.md" \
  '`run-planning/SKILL.md` and `planning-loop/SKILL.md` are supervisor-layer docs, not ordinary planner/reviewer authoritative packet payload'
check_pattern \
  "plugins/forgeloop/skills/references/anchor-addressing.md" \
  'Supervisor or dispatcher skill docs are not worker authoritative packet payload'

while IFS= read -r file; do
  check_pattern \
    "$file" \
    'Do not require `run-planning/SKILL.md` or `planning-loop/SKILL.md`'
done <<'EOF'
plugins/forgeloop/agents/planner.toml
plugins/forgeloop/agents/design_reviewer.toml
plugins/forgeloop/agents/gap_reviewer.toml
plugins/forgeloop/agents/plan_reviewer.toml
EOF

while IFS= read -r file; do
  if rg -q '^- the `Planning State Doc`$' "$file"; then
    echo "planning packet lint: reviewer read surface still includes Planning State Doc in ${file}"
    exit 1
  fi
done <<'EOF'
plugins/forgeloop/agents/design_reviewer.toml
plugins/forgeloop/agents/gap_reviewer.toml
plugins/forgeloop/agents/plan_reviewer.toml
EOF

python3 - <<'PY'
import json
from pathlib import Path

scenarios = json.loads(Path("tests/codex/token-benchmark/fixtures/scenarios.json").read_text())
targets = {
    "same-stage planner continue",
    "fresh planning reviewer handoff",
}
for scenario in scenarios:
    if scenario["name"] not in targets:
        continue
    for item in scenario["minimal_packet"]:
        path = item.get("path") or item.get("doc")
        if path == "plugins/forgeloop/skills/planning-loop/SKILL.md":
            raise SystemExit(
                f"planning packet lint: worker minimal packet still references planning-loop/SKILL.md in scenario {scenario['name']}"
            )
        if path == "plugins/forgeloop/skills/run-planning/SKILL.md":
            raise SystemExit(
                f"planning packet lint: worker minimal packet still references run-planning/SKILL.md in scenario {scenario['name']}"
            )
PY

echo "planning packet lint passed"
