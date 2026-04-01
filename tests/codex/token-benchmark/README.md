# Forgeloop Token Benchmark

This directory contains a lightweight, repo-local benchmark for the anchor-addressed dispatch change set.

It is intentionally contract-level rather than runtime-telemetry-level:

- it measures the shipped formal docs, slices, and derived views that the repo currently exposes
- it compares a representative legacy full-document packet against the intended minimal packet for each scenario
- it uses a stable approximation (`ceil(characters / 4)`) instead of provider-specific tokenizer output

The benchmark is meant to answer three questions quickly:

1. Which docs are being read on each representative path?
2. How large is the legacy packet versus the minimal packet?
3. Where do hot-path savings come from, and which scenarios still rely on legal full-document fallback?

## Representative Scenarios

The fixtures cover at least these paths:

- runtime cold start
- runtime resume into active task
- same-task same-round coder continue
- same-task handoff to fresh reviewer
- milestone review
- initiative review
- rebuild-runtime
- waiting / blocked resume

## Run

From repo root:

```bash
bash tests/codex/token-benchmark/run.sh
```

## Output

The benchmark prints:

- the legacy docs read set
- the minimal packet read set
- approximate packet size in chars / lines / words / approx tokens, including packet wrapper metadata plus referenced body content
- per-scenario reduction percentage
- hot-path and cold-path aggregate reduction
- Task hot-path average reduction
- any explicit fallback points recorded by the fixture

The script is also an acceptance gate:

- total reduction must stay at or above `45%`
- Task hot-path average reduction must stay near `50%`, currently enforced as `>= 50%`

## Notes

- The reported token numbers are approximate and intentionally deterministic.
- The benchmark uses only tracked repo fixtures plus temporary derived views generated during the run.
- Derived views are materialized into a temporary directory during the run and never become durable truth.
- This benchmark proves approximate packet-shape and read-surface shrinkage; it still does not replace real provider telemetry.
