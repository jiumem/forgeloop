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

- Hot path reduction: 67.9% (118742 -> 38118 tok approx)
- Cold path reduction: 78.7% (63048 -> 13408 tok approx)
- Total reduction: 71.7% (181790 -> 51526 tok approx)
- Task hot path average reduction: 68.6%
- Gate mode: gating

## Planning Aggregate

- Hot path reduction: 52.1% (27764 -> 13292 tok approx)
- Cold path reduction: 79.0% (23244 -> 4883 tok approx)
- Total reduction: 64.4% (51008 -> 18175 tok approx)
- Gate mode: report-only

## Scenario Baseline

| Scenario | Scope | Gating | Bucket | Legacy | Minimal | Reduction |
| --- | --- | --- | --- | ---: | ---: | ---: |
| Runtime Cold Start | runtime | gating | cold_path | 24518 | 8047 | 67.2% |
| Runtime Resume Into Active Task | runtime | gating | hot_path | 28845 | 3730 | 87.1% |
| Same-Task Same-Round Coder Continue | runtime | gating | hot_path | 8141 | 3771 | 53.7% |
| Same-Task Reviewer Entry | runtime | gating | hot_path | 9211 | 3735 | 59.5% |
| Milestone Review | runtime | gating | hot_path | 15945 | 3458 | 78.3% |
| Initiative Review | runtime | gating | hot_path | 15757 | 3289 | 79.1% |
| Rebuild Runtime | runtime | gating | cold_path | 19524 | 2997 | 84.6% |
| Waiting Or Blocked Resume | runtime | gating | cold_path | 19006 | 2364 | 87.6% |
| same-task warm-path delta legal | runtime | gating | hot_path | 14750 | 3812 | 74.2% |
| same-task warm-path delta illegal -> full packet fallback | runtime | gating | hot_path | 14780 | 8174 | 44.7% |
| selector legality failure -> full-doc fallback | runtime | gating | hot_path | 11313 | 8149 | 28.0% |
| planning cold entry | planning | report_only | cold_path | 23244 | 4883 | 79.0% |
| same-stage planner continue | planning | report_only | hot_path | 7883 | 3666 | 53.5% |
| current-stage reviewer entry | planning | report_only | hot_path | 9555 | 5444 | 43.0% |
| review changes requested -> reopen next round | planning | report_only | hot_path | 10326 | 4182 | 59.5% |

## Notes

- Runtime cutover mode is `minimal_preferred`.
- Runtime gate remains `total >= 45%` and `task hot path >= 50%` only while runtime cutover mode stays in a minimal-first state.
- Planning scenarios are tracked in a separate report-only block and do not currently gate the run.
- Packet dumps, when requested, expose the exact compared text for each scenario so the baseline remains auditable.
- Full-document fallback remains explicit in the packet text; it is measured, not hidden.
