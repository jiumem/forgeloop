# Forgeloop Token Benchmark

This directory contains a lightweight, repo-local benchmark for the anchor-addressed dispatch change set.

It is intentionally contract-level rather than runtime-telemetry-level:

- it measures the shipped formal docs, slices, and derived views that the repo currently exposes
- it compares a representative legacy full-document packet against the intended minimal packet for each scenario
- it uses a stable approximation (`ceil(characters / 4)`) instead of provider-specific tokenizer output
- it proves `packet-shape + read-surface shrink`, not provider token truth

The benchmark is meant to answer three questions quickly:

1. Which docs are being read on each representative path?
2. What are the exact legacy and minimal packet texts being compared?
3. Where do hot-path savings come from, and which scenarios still rely on legal full-document fallback?

## Representative Scenarios

The fixtures cover both scopes:

- `runtime / gating`
- `planning / report_only`

The representative paths currently include:

- runtime cold start
- runtime resume into active task
- same-task same-round coder continue
- same-task reviewer entry
- same-task warm-path delta legal
- same-task warm-path delta illegal -> full packet fallback
- selector legality failure -> full-doc fallback
- milestone review
- initiative review
- rebuild-runtime
- waiting / blocked resume
- planning cold entry
- same-stage planner continue
- current-stage reviewer entry
- review changes requested -> reopen next round

## Run

From repo root:

```bash
bash tests/codex/p0-validation.sh
```

The benchmark itself remains available as a sub-step:

```bash
bash tests/codex/token-benchmark/run.sh
```

## Output

The benchmark prints:

- the current `runtime_cutover_mode` and cutover scope before any runtime aggregate
- a full materialized `legacy packet` and `minimal packet` for each scenario before measuring them
- the legacy docs read set
- the minimal packet read set
- approximate packet size in chars / lines / words / approx tokens, including packet wrapper metadata plus referenced body content
- per-scenario reduction percentage
- runtime hot-path and cold-path aggregate reduction
- runtime Task hot-path average reduction
- planning report-only aggregate reduction
- any explicit fallback points recorded by the fixture

Optional outputs:

- `--dump-packets <dir>` writes the exact compared packet text for every scenario
- `--json-out <path>` writes a machine-readable benchmark report
- `--compare-baseline <path>` adds scenario-level diffs versus a saved baseline and fails on drift
- `--markdown-out <path>` writes a generated baseline markdown summary
- fallback scenarios may also run executable preconditions before the packet comparison so the report proves the triggering contract failure, not only the fallback packet shape

The script is also an acceptance gate:

- `runtime / gating` must keep total reduction at or above `45%`
- `runtime / gating` must keep Task hot-path average reduction at or above `50%`
- if runtime cutover mode is rolled back to `full_doc_default`, the runtime section remains reportable but the threshold gate becomes report-only
- `planning / report_only` is summarized separately and does not currently gate the run

## Notes

- The reported token numbers are approximate and intentionally deterministic.
- The benchmark uses only tracked repo fixtures plus temporary derived views generated during the run.
- Derived views are materialized into a temporary directory during the run and never become durable truth.
- Runtime cutover is repository-owned in `plugins/forgeloop/skills/run-initiative/references/runtime-cutover.md`; planning remains out of cutover scope in this benchmark.
- This benchmark proves approximate packet-shape and read-surface shrinkage; it still does not replace a provider tokenizer or real runtime telemetry.
