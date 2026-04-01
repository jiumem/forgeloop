#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TMP_ROOT="$(mktemp -d)"
trap 'rm -rf "$TMP_ROOT"' EXIT

cd "$ROOT"

python3 plugins/forgeloop/scripts/anchor_slices.py check \
  docs/initiatives/active/anchor-sliced-dispatch-optimization/design.md \
  docs/initiatives/active/anchor-sliced-dispatch-optimization/gap-analysis.md \
  docs/initiatives/active/anchor-sliced-dispatch-optimization/total-task-doc.md \
  plugins/forgeloop/skills/references/anchor-addressing.md \
  plugins/forgeloop/skills/references/derived-views.md \
  plugins/forgeloop/skills/references/validation-matrix.md \
  plugins/forgeloop/skills/planning-loop/references/planning-rolling-doc.md \
  plugins/forgeloop/skills/run-initiative/references/global-state.md \
  plugins/forgeloop/skills/run-initiative/references/task-review-rolling-doc.md \
  plugins/forgeloop/skills/run-initiative/references/milestone-review-rolling-doc.md \
  plugins/forgeloop/skills/run-initiative/references/initiative-review-rolling-doc.md \
  tests/fixtures/anchor-slicing/anchors-ok.md

if python3 plugins/forgeloop/scripts/anchor_slices.py check \
  tests/fixtures/anchor-slicing/anchors-duplicate.md
then
  echo "duplicate-anchor fixture unexpectedly passed"
  exit 1
fi

if python3 plugins/forgeloop/scripts/anchor_slices.py check \
  tests/fixtures/anchor-slicing/anchors-illegal.md
then
  echo "illegal-anchor fixture unexpectedly passed"
  exit 1
fi

python3 plugins/forgeloop/scripts/anchor_slices.py slice \
  --doc tests/fixtures/anchor-slicing/anchors-ok.md \
  --anchor intro >"${TMP_ROOT}/intro.txt"

if ! rg -q "legal intro anchor" "${TMP_ROOT}/intro.txt"; then
  echo "slice output did not contain expected body"
  exit 1
fi

python3 plugins/forgeloop/scripts/anchor_slices.py derive \
  --doc tests/fixtures/anchor-slicing/task-review-sample.md \
  --out "${TMP_ROOT}/derived"

for path in \
  "${TMP_ROOT}/derived/current-effective.md" \
  "${TMP_ROOT}/derived/attempt-aware/round-1.md" \
  "${TMP_ROOT}/derived/attempt-aware/round-2.md" \
  "${TMP_ROOT}/derived/handoff-scoped/sample-r1-a1.md" \
  "${TMP_ROOT}/derived/handoff-scoped/sample-r2-a1.md"
do
  if [ ! -f "$path" ]; then
    echo "missing derived view: $path"
    exit 1
  fi
done

if ! rg -q "sample-r2-a1" "${TMP_ROOT}/derived/current-effective.md"; then
  echo "current-effective view did not include the latest handoff"
  exit 1
fi

if rg -q "sample-r1-a1" "${TMP_ROOT}/derived/current-effective.md"; then
  echo "current-effective view still included a stale handoff"
  exit 1
fi

if rg -q "Round 1" "${TMP_ROOT}/derived/current-effective.md"; then
  echo "current-effective view still included stale round sections"
  exit 1
fi

HANDOFF_COUNT="$(rg -c "^handoff_id: sample-r2-a1$" "${TMP_ROOT}/derived/handoff-scoped/sample-r2-a1.md")"
if [ "${HANDOFF_COUNT}" -ne 2 ]; then
  echo "handoff-scoped view should contain exactly one handoff block plus one matching review result"
  exit 1
fi

python3 plugins/forgeloop/scripts/anchor_slices.py derive \
  --doc tests/fixtures/anchor-slicing/planning-header-only.md \
  --out "${TMP_ROOT}/header-only"

if ! rg -q "No round-scoped formal blocks" "${TMP_ROOT}/header-only/current-effective.md"; then
  echo "header-only derive did not degrade to an empty current frontier"
  exit 1
fi

if python3 plugins/forgeloop/scripts/anchor_slices.py derive \
  --doc tests/fixtures/anchor-slicing/task-review-duplicate-handoff.md \
  --out "${TMP_ROOT}/duplicate-handoff"
then
  echo "duplicate-handoff fixture unexpectedly derived successfully"
  exit 1
fi

if python3 plugins/forgeloop/scripts/anchor_slices.py derive \
  --doc tests/fixtures/anchor-slicing/task-review-malformed-handoff.md \
  --out "${TMP_ROOT}/malformed-handoff"
then
  echo "malformed-handoff fixture unexpectedly derived successfully"
  exit 1
fi

if python3 plugins/forgeloop/scripts/anchor_slices.py derive \
  --doc tests/fixtures/anchor-slicing/task-review-malformed-result.md \
  --out "${TMP_ROOT}/malformed-result"
then
  echo "malformed-result fixture unexpectedly derived successfully"
  exit 1
fi

STALE_OUT="${TMP_ROOT}/stale-rebuild"
python3 plugins/forgeloop/scripts/anchor_slices.py derive \
  --doc tests/fixtures/anchor-slicing/task-review-sample.md \
  --out "${STALE_OUT}"

if python3 plugins/forgeloop/scripts/anchor_slices.py derive \
  --doc tests/fixtures/anchor-slicing/task-review-malformed-handoff.md \
  --out "${STALE_OUT}"
then
  echo "stale-rebuild malformed fixture unexpectedly derived successfully"
  exit 1
fi

if [ -e "${STALE_OUT}/current-effective.md" ] || [ -d "${STALE_OUT}/attempt-aware" ] || [ -d "${STALE_OUT}/handoff-scoped" ]; then
  echo "failed derive left stale derived views on disk"
  exit 1
fi

if python3 plugins/forgeloop/scripts/anchor_slices.py derive \
  --doc tests/fixtures/anchor-slicing/task-review-null-tuple.md \
  --out "${TMP_ROOT}/null-tuple"
then
  echo "null-tuple fixture unexpectedly derived successfully"
  exit 1
fi

if python3 plugins/forgeloop/scripts/anchor_slices.py derive \
  --doc tests/fixtures/anchor-slicing/task-review-missing-round-handoff.md \
  --out "${TMP_ROOT}/missing-round-handoff"
then
  echo "missing-round-handoff fixture unexpectedly derived successfully"
  exit 1
fi

if python3 plugins/forgeloop/scripts/anchor_slices.py derive \
  --doc tests/fixtures/anchor-slicing/task-review-missing-round-result.md \
  --out "${TMP_ROOT}/missing-round-result"
then
  echo "missing-round-result fixture unexpectedly derived successfully"
  exit 1
fi

if python3 plugins/forgeloop/scripts/anchor_slices.py derive \
  --doc tests/fixtures/anchor-slicing/task-review-missing-round-coder-update.md \
  --out "${TMP_ROOT}/missing-round-coder-update"
then
  echo "missing-round-coder-update fixture unexpectedly derived successfully"
  exit 1
fi

if python3 plugins/forgeloop/scripts/anchor_slices.py derive \
  --doc tests/fixtures/anchor-slicing/planning-missing-round-planner-update.md \
  --out "${TMP_ROOT}/planning-missing-round-planner-update"
then
  echo "planning-missing-round-planner-update fixture unexpectedly derived successfully"
  exit 1
fi

if python3 plugins/forgeloop/scripts/anchor_slices.py derive \
  --doc tests/fixtures/anchor-slicing/task-review-invalid-round.md \
  --out "${TMP_ROOT}/invalid-round"
then
  echo "invalid-round fixture unexpectedly derived successfully"
  exit 1
fi

if python3 plugins/forgeloop/scripts/anchor_slices.py derive \
  --doc tests/fixtures/anchor-slicing/task-review-duplicate-header.md \
  --out "${TMP_ROOT}/duplicate-header"
then
  echo "duplicate-header fixture unexpectedly derived successfully"
  exit 1
fi

if python3 plugins/forgeloop/scripts/anchor_slices.py derive \
  --doc tests/fixtures/anchor-slicing/task-review-duplicate-contract-snapshot.md \
  --out "${TMP_ROOT}/duplicate-contract-snapshot"
then
  echo "duplicate-contract-snapshot fixture unexpectedly derived successfully"
  exit 1
fi

if python3 plugins/forgeloop/scripts/anchor_slices.py derive \
  --doc tests/fixtures/anchor-slicing/milestone-review-missing-next-action.md \
  --out "${TMP_ROOT}/missing-next-action"
then
  echo "missing-next-action fixture unexpectedly derived successfully"
  exit 1
fi

if python3 plugins/forgeloop/scripts/anchor_slices.py derive \
  --doc tests/fixtures/anchor-slicing/task-review-missing-author-role-coder-update.md \
  --out "${TMP_ROOT}/missing-author-role-coder-update"
then
  echo "missing-author-role-coder-update fixture unexpectedly derived successfully"
  exit 1
fi

echo "anchor slice smoke test passed"
