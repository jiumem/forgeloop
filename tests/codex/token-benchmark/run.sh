#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"

cd "$ROOT"

python3 tests/codex/token-benchmark/benchmark.py \
  --fixtures tests/codex/token-benchmark/fixtures/scenarios.json \
  "$@"
