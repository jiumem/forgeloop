# Forgeloop Token Benchmark Baseline

Generated from:

```bash
bash tests/codex/token-benchmark/run.sh \
  --json-out tests/codex/token-benchmark/baseline.json \
  --markdown-out tests/codex/token-benchmark/baseline.md
```

Method:

- legacy packet = representative full-document packet for the scenario
- minimal packet = representative minimal dispatch packet after anchor slices / derived views / legal fallback are fully materialized as text
- selected fallback scenarios also carry executable preconditions that must prove the triggering failure before fallback packet comparison
- packet size proves `packet-shape + read-surface shrink`, not provider token counts
- approx tokens = `ceil(characters / 4)`
- runtime cutover mode = `minimal_preferred`

## Runtime Aggregate

- Hot path reduction: 46.3% (109889 -> 59041 tok approx)
- Cold path reduction: 64.2% (55755 -> 19941 tok approx)
- Total reduction: 52.3% (165644 -> 78982 tok approx)
- Task hot path average reduction: 56.6%
- Gate mode: gating

## Planning Aggregate

- Hot path reduction: 47.0% (26601 -> 14102 tok approx)
- Cold path reduction: 73.4% (20691 -> 5499 tok approx)
- Total reduction: 58.6% (47292 -> 19601 tok approx)
- Gate mode: report-only

## Scenario Baseline

| Scenario | Scope | Gating | Bucket | Legacy | Minimal | Reduction |
| --- | --- | --- | --- | ---: | ---: | ---: |
| Runtime Cold Start | runtime | gating | cold_path | 21305 | 10517 | 50.6% |
| Runtime Resume Into Active Task | runtime | gating | hot_path | 26406 | 10588 | 59.9% |
| Same-Task Same-Round Coder Continue | runtime | gating | hot_path | 7713 | 4096 | 46.9% |
| Same-Task Handoff To Fresh Reviewer | runtime | gating | hot_path | 9506 | 5013 | 47.3% |
| Milestone Review | runtime | gating | hot_path | 13960 | 5789 | 58.5% |
| Initiative Review | runtime | gating | hot_path | 13978 | 5362 | 61.6% |
| Rebuild Runtime | runtime | gating | cold_path | 18643 | 4819 | 74.2% |
| Waiting Or Blocked Resume | runtime | gating | cold_path | 15807 | 4605 | 70.9% |
| same-task warm-path delta legal | runtime | gating | hot_path | 14098 | 3926 | 72.2% |
| same-task warm-path delta illegal -> full packet fallback | runtime | gating | hot_path | 14128 | 14153 | -0.2% |
| selector legality failure -> full-doc fallback | runtime | gating | hot_path | 10100 | 10114 | -0.1% |
| planning cold entry | planning | report_only | cold_path | 20691 | 5499 | 73.4% |
| same-stage planner continue | planning | report_only | hot_path | 7333 | 4159 | 43.3% |
| fresh planning reviewer handoff | planning | report_only | hot_path | 9518 | 5768 | 39.4% |
| review changes requested -> reopen next round | planning | report_only | hot_path | 9750 | 4175 | 57.2% |

## Notes

- Runtime cutover mode is `minimal_preferred`.
- Runtime gate remains `total >= 45%` and `task hot path >= 50%` only while runtime cutover mode stays in a minimal-first state.
- Planning scenarios are tracked in a separate report-only block and do not currently gate the run.
- Packet dumps, when requested, expose the exact compared text for each scenario so the baseline remains auditable.
- Full-document fallback remains explicit in the packet text; it is measured, not hidden.
