#!/usr/bin/env bash

set -uo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TMP_ROOT="$(mktemp -d)"
trap 'rm -rf "$TMP_ROOT"' EXIT

cd "$ROOT"

status=0

run_step() {
  local label="$1"
  shift

  echo "== ${label} =="
  if "$@"; then
    echo "[pass] ${label}"
  else
    echo "[fail] ${label}"
    status=1
  fi
  echo
}

run_step \
  "anchor-slice-smoke" \
  bash tests/codex/anchor-slice-smoke.sh

run_step \
  "runtime-packet-lint" \
  bash tests/codex/runtime-packet-lint.sh

run_step \
  "token-benchmark" \
  bash tests/codex/token-benchmark/run.sh \
    --json-out "${TMP_ROOT}/benchmark.json" \
    --dump-packets "${TMP_ROOT}/packets"

run_step \
  "baseline-compare" \
  bash tests/codex/token-benchmark/run.sh \
    --json-out "${TMP_ROOT}/benchmark-compare.json" \
    --compare-baseline tests/codex/token-benchmark/baseline.json

exit "${status}"
