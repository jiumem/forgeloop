# Forgeloop Anchor-Sliced Validation Matrix

<!-- forgeloop:anchor document-role -->
## Document Role

- Plane: shared planning/runtime reference
- Applies to: anchor legality, minimal packet consumers, rolling-doc derived views, and migration/cutover checks
- Primary readers: coders, reviewers, and repository self-checks
- Primary purpose: define the minimum reusable evidence matrix for anchor-sliced dispatch

<!-- forgeloop:anchor matrix -->
## Validation Matrix

| Scenario | Expected Result | Suggested Entry Point |
| --- | --- | --- |
| unique text anchor resolves | `slice` returns exactly one bounded slice | `anchor_slices.py slice` |
| duplicate text anchor exists | `check` fails and names the duplicate selector | `anchor_slices.py check` |
| illegal text anchor syntax exists | `check` fails and names the offending line | `anchor_slices.py check` |
| adjacent anchors create an empty slice | `check` fails and names the empty selector | `anchor_slices.py check` |
| illegal selector input is requested | resolver stops with `illegal_selector` | `anchor_slices.py slice` |
| missing text anchor requested | resolver stops with `missing_anchor` | `anchor_slices.py slice` |
| required machine-addressed formal surface lacks mandated selectors | release gate fails on coverage violation | `anchor-slice-smoke` + required-surface list |
| minimal packet consumer gets legal selectors | consumer may stay on minimal-path read | workflow skills + tracked reference mirrors |
| selector legality fails | consumer promotes to full-document fallback or blocks | workflow skills |
| runtime review round exposes duplicate handoff or result blocks | `derive` fails instead of guessing a current result | `anchor_slices.py derive` |
| `round-scoped` is read for one review round | view includes the round's formal blocks in append order | `anchor_slices.py derive` |
| derived view is missing or stale | consumer may invalidate and reread formal doc | workflow skills + derived-view contract |
| newer formal block invalidates a derived view | consumer rejects the stale view and rebuilds from the authoritative rolling doc | `anchor_slices.py derive` + workflow skills |
| reviewer enters a handoff for the first time | packet stays self-sufficient and does not assume a previous packet | runtime reviewer manifests + loop skills |
| runtime reviewer packet is assembled for an active handoff | packet preserves current handoff identity, `compare_base_ref` when present, and object-local planning truth | shared packet law + runtime loop skills |
| delta conditions cannot be proven | supervisor falls back to a full packet instead of sending a delta-only packet | runtime loop skills + cutover notes |
| runtime cutover mode = `full_doc_default` | old full-document path remains the legal runtime default while minimal-path validation still runs | runtime cutover contract + workflow skills |

<!-- forgeloop:anchor benchmark-scope -->
## Benchmark Scope

- The benchmark proves `packet-shape + read-surface shrink`, not provider tokenizer output.
- Approximate tokens remain `ceil(characters / 4)` by design.
- `runtime / gating` scenarios are the only scenarios that currently enforce thresholds.
- Runtime validation must print and compare `current_runtime_cutover_mode`.
- `planning / report_only` scenarios are printed in a separate block and do not currently gate.
- `--compare-baseline` is expected to fail on baseline drift, including added/removed scenarios and non-zero scenario or aggregate deltas.

<!-- forgeloop:anchor fixtures -->
## Fixtures

- `tests/fixtures/anchor-slicing/anchors-ok.md`
- `tests/fixtures/anchor-slicing/anchors-duplicate.md`
- `tests/fixtures/anchor-slicing/anchors-illegal.md`
- `tests/fixtures/anchor-slicing/task-review-sample.md`
- `tests/fixtures/anchor-slicing/task-review-sample-appended.md`
- `tests/fixtures/anchor-slicing/planning-review-stale-results.md`
- `tests/codex/token-benchmark/fixtures/scenarios.json`

These fixtures are intentionally small. They prove contract behavior, not business-domain traces.

Coverage validation applies only to the required machine-addressed surface list defined by `anchor-addressing.md`. Optional workflow or explanatory docs may omit anchors without causing release failure.
`anchor_slices.py` must enforce that same required-surface list symmetrically. A surface is not formally required unless validation enforces it, and validation must not enforce a narrower or different set than the declared contract.

<!-- forgeloop:anchor release-gate -->
## Release Gate

Run from repo root:

```bash
bash tests/codex/p0-validation.sh
```

This is the single recommended entry point for the P0 validation closure.

It runs:

- `anchor-slice-smoke` for selector legality, machine-kind closure, derived-view rebuild, and contract-break detection
- `runtime-packet-lint` for reviewer compare-pair fixtures and object-local planning-truth packet shape
- `token-benchmark` for representative packet-shape and read-surface shrink
- `baseline compare` for scenario-level drift versus the saved machine-readable baseline
