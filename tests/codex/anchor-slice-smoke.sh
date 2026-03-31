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

echo "anchor slice smoke test passed"
