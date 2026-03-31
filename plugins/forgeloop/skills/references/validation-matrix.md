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
| missing text anchor requested | resolver stops with `missing_anchor` | `anchor_slices.py slice` |
| minimal packet consumer gets legal selectors | consumer may stay on minimal-path read | workflow skills + tracked reference mirrors |
| selector legality fails | consumer promotes to explicit full-document fallback or blocks | workflow skills |
| rolling doc has superseded same-handoff results | `current-effective` picks only the latest matching result | `anchor_slices.py derive` |
| derived view is missing or stale | consumer may invalidate and reread formal doc | workflow skills + derived-view contract |
| migration cutover disabled | old full-document path remains legal | workflow skills + migration notes |

<!-- forgeloop:anchor fixtures -->
## Fixtures

- `tests/fixtures/anchor-slicing/anchors-ok.md`
- `tests/fixtures/anchor-slicing/anchors-duplicate.md`
- `tests/fixtures/anchor-slicing/anchors-illegal.md`
- `tests/fixtures/anchor-slicing/task-review-sample.md`

These fixtures are intentionally small. They prove contract behavior, not business-domain traces.

<!-- forgeloop:anchor release-gate -->
## Release Gate

Run from repo root:

```bash
bash tests/codex/anchor-slice-smoke.sh
```

This check validates anchor syntax, duplicate detection, slice materialization, and derived-view rebuilding on the shipped fixtures and selected formal documents.
