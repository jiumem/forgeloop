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

- Hot path reduction: 67.1% (111867 -> 36819 tok approx)
- Cold path reduction: 79.3% (61432 -> 12723 tok approx)
- Total reduction: 71.4% (173299 -> 49542 tok approx)
- Task hot path average reduction: 66.6%
- Gate mode: gating

## Planning Aggregate

- Hot path reduction: 51.5% (26849 -> 13035 tok approx)
- Cold path reduction: 79.6% (22957 -> 4677 tok approx)
- Total reduction: 64.4% (49806 -> 17712 tok approx)
- Gate mode: report-only

## Scenario Baseline

| Scenario | Scope | Gating | Bucket | Legacy | Minimal | Reduction |
| --- | --- | --- | --- | ---: | ---: | ---: |
| Runtime Cold Start | runtime | gating | cold_path | 23851 | 7528 | 68.4% |
| Runtime Resume Into Active Task | runtime | gating | hot_path | 27701 | 3510 | 87.3% |
| Same-Task Same-Round Coder Continue | runtime | gating | hot_path | 7500 | 3735 | 50.2% |
| Same-Task Handoff To Fresh Reviewer | runtime | gating | hot_path | 8519 | 3689 | 56.7% |
| Milestone Review | runtime | gating | hot_path | 15204 | 3379 | 77.8% |
| Initiative Review | runtime | gating | hot_path | 15127 | 3209 | 78.8% |
| Rebuild Runtime | runtime | gating | cold_path | 19242 | 2973 | 84.5% |
| Waiting Or Blocked Resume | runtime | gating | cold_path | 18339 | 2222 | 87.9% |
| same-task warm-path delta legal | runtime | gating | hot_path | 13606 | 3776 | 72.2% |
| same-task warm-path delta illegal -> full packet fallback | runtime | gating | hot_path | 13636 | 7773 | 43.0% |
| selector legality failure -> full-doc fallback | runtime | gating | hot_path | 10574 | 7748 | 26.7% |
| planning cold entry | planning | report_only | cold_path | 22957 | 4677 | 79.6% |
| same-stage planner continue | planning | report_only | hot_path | 7596 | 3666 | 51.7% |
| fresh planning reviewer handoff | planning | report_only | hot_path | 9214 | 5356 | 41.9% |
| review changes requested -> reopen next round | planning | report_only | hot_path | 10039 | 4013 | 60.0% |

## Notes

- Runtime cutover mode is `minimal_preferred`.
- Runtime gate remains `total >= 45%` and `task hot path >= 50%` only while runtime cutover mode stays in a minimal-first state.
- Planning scenarios are tracked in a separate report-only block and do not currently gate the run.
- Packet dumps, when requested, expose the exact compared text for each scenario so the baseline remains auditable.
- Full-document fallback remains explicit in the packet text; it is measured, not hidden.
