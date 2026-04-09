#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

check_pattern() {
  local file="$1"
  local pattern="$2"

  if ! rg -q "$pattern" "$file"; then
    echo "control-plane root lint: missing ${pattern} in ${file}"
    exit 1
  fi
}

check_pattern \
  "plugins/forgeloop/skills/references/control-plane-roots.md" \
  'only legal repo-local control-plane root'
check_pattern \
  "plugins/forgeloop/skills/references/control-plane-roots.md" \
  'README\.md'
check_pattern \
  "plugins/forgeloop/skills/run-planning/SKILL.md" \
  'Do not search for alternate repo-local planning control-plane roots'
check_pattern \
  "plugins/forgeloop/skills/run-initiative/SKILL.md" \
  'Do not search for alternate repo-local runtime control-plane roots'
check_pattern \
  "plugins/forgeloop/skills/planning-loop/references/planning-rolling-doc.md" \
  'The rolling doc is the authority for round, handoff, review-result, seal, and reopen history'
check_pattern \
  "plugins/forgeloop/skills/planning-loop/references/design-doc.md" \
  '以 rolling doc 为准'
check_pattern \
  "plugins/forgeloop/skills/planning-loop/references/gap-analysis.md" \
  '以 rolling doc 为准'

while IFS= read -r file; do
  if rg -q 'unless explicit sealed refs override|override the defaults|Legacy repo-root|wider repo recovery|wider repo search' "$file"; then
    echo "control-plane root lint: stale multi-root wording remains in ${file}"
    exit 1
  fi
done <<'EOF'
plugins/forgeloop/skills/references/control-plane-roots.md
plugins/forgeloop/skills/run-planning/SKILL.md
plugins/forgeloop/skills/run-initiative/SKILL.md
plugins/forgeloop/skills/run-planning/references/planning-state.md
plugins/forgeloop/skills/planning-loop/references/planning-rolling-doc.md
plugins/forgeloop/skills/run-initiative/references/global-state.md
plugins/forgeloop/skills/planning-loop/references/total-task-doc.md
docs/forgeloop/install.md
EOF

if rg -P -n \
  -g '*.md' \
  '\.forgeloop/(?!planning-state\.md|design-rolling\.md|gap-rolling\.md|plan-rolling\.md|global-state\.md|task-review/|milestone-review/|initiative-review\.md)[A-Za-z0-9_-]+/(?:planning-state\.md|design-rolling\.md|gap-rolling\.md|plan-rolling\.md|global-state\.md|task-review/|milestone-review/|initiative-review\.md)' \
  plugins/forgeloop \
  docs/initiatives/active \
  tests/codex \
  tests/fixtures \
  tests/codex/token-benchmark/fixtures \
  >/tmp/forgeloop-control-plane-legacy-paths.txt
then
  echo "control-plane root lint: legacy initiative-key control-plane paths remain:"
  cat /tmp/forgeloop-control-plane-legacy-paths.txt
  exit 1
fi

python3 - <<'PY'
from pathlib import Path

repo = Path(".")

expected = {
    "plugins/forgeloop/skills/planning-loop/references/design-doc.md",
    "plugins/forgeloop/skills/planning-loop/references/gap-analysis.md",
    "plugins/forgeloop/skills/planning-loop/references/total-task-doc.md",
    "plugins/forgeloop/skills/planning-loop/references/planning-rolling-doc.md",
}

for path in expected:
    if not (repo / path).is_file():
        raise SystemExit(f"control-plane root lint: missing canonical planning ref {path}")

planning_loop = (repo / "plugins/forgeloop/skills/planning-loop/SKILL.md").read_text()
for path in expected:
    if path not in planning_loop:
        raise SystemExit(f"control-plane root lint: planning-loop missing canonical ref {path}")

fixture_paths = [
    Path("tests/fixtures/anchor-slicing/planning-review-stale-results.md"),
    Path("tests/fixtures/anchor-slicing/planning-plan-review-sample.md"),
    Path("tests/fixtures/anchor-slicing/planning-header-only.md"),
    Path("tests/fixtures/anchor-slicing/planning-missing-round-planner-update.md"),
    Path("tests/codex/token-benchmark/fixtures/planning-gap-reopen-sample.md"),
    Path("tests/codex/token-benchmark/fixtures/planning-design-handoff-sample.md"),
    Path("tests/codex/token-benchmark/fixtures/planning-design-repair-sample.md"),
]

for path in fixture_paths:
    text = (repo / path).read_text()
    if "stage_reference_ref: references/" in text:
        raise SystemExit(f"control-plane root lint: fixture still uses relative stage_reference_ref in {path}")
    if "rolling_doc_contract_ref: references/planning-rolling-doc.md" in text:
        raise SystemExit(f"control-plane root lint: fixture still uses relative rolling_doc_contract_ref in {path}")
PY

echo "control-plane root lint passed"
