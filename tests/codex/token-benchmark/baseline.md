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

- Hot path reduction: 67.8% (116939 -> 37688 tok approx)
- Cold path reduction: 78.7% (62807 -> 13408 tok approx)
- Total reduction: 71.6% (179746 -> 51096 tok approx)
- Task hot path average reduction: 67.9%
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
| Runtime Resume Into Active Task | runtime | gating | hot_path | 28630 | 3730 | 87.0% |
| Same-Task Same-Round Coder Continue | runtime | gating | hot_path | 7927 | 3771 | 52.4% |
| Same-Task Reviewer Entry | runtime | gating | hot_path | 8996 | 3735 | 58.5% |
| Milestone Review | runtime | gating | hot_path | 15632 | 3458 | 77.9% |
| Initiative Review | runtime | gating | hot_path | 15555 | 3289 | 78.9% |
| Rebuild Runtime | runtime | gating | cold_path | 19283 | 2997 | 84.5% |
| Waiting Or Blocked Resume | runtime | gating | cold_path | 19006 | 2364 | 87.6% |
| same-task warm-path delta legal | runtime | gating | hot_path | 14535 | 3812 | 73.8% |
| same-task warm-path delta illegal -> full packet fallback | runtime | gating | hot_path | 14566 | 7959 | 45.4% |
| selector legality failure -> full-doc fallback | runtime | gating | hot_path | 11098 | 7934 | 28.5% |
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
