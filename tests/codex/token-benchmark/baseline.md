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

- Hot path reduction: 66.4% (120467 -> 40419 tok approx)
- Cold path reduction: 89.4% (61032 -> 6463 tok approx)
- Total reduction: 74.2% (181499 -> 46882 tok approx)
- Task hot path average reduction: 69.1%
- Gate mode: gating

## Planning Aggregate

- Hot path reduction: 53.1% (28323 -> 13274 tok approx)
- Cold path reduction: 79.4% (23605 -> 4855 tok approx)
- Total reduction: 65.1% (51928 -> 18129 tok approx)
- Gate mode: report-only

## Scenario Baseline

| Scenario | Scope | Gating | Bucket | Legacy | Minimal | Reduction |
| --- | --- | --- | --- | ---: | ---: | ---: |
| Runtime Cold Start | runtime | gating | cold_path | 23498 | 3293 | 86.0% |
| Runtime Resume Into Active Task | runtime | gating | hot_path | 28389 | 2021 | 92.9% |
| Same-Task Same-Round Coder Continue | runtime | gating | hot_path | 9035 | 4270 | 52.7% |
| Same-Task Reviewer Entry | runtime | gating | hot_path | 10168 | 4016 | 60.5% |
| Milestone Review | runtime | gating | hot_path | 16779 | 3735 | 77.7% |
| Initiative Review | runtime | gating | hot_path | 16541 | 3554 | 78.5% |
| Rebuild Runtime | runtime | gating | cold_path | 19455 | 1678 | 91.4% |
| Waiting Or Blocked Resume | runtime | gating | cold_path | 18079 | 1492 | 91.7% |
| same-task warm-path delta legal | runtime | gating | hot_path | 14294 | 4254 | 70.2% |
| same-task warm-path delta illegal -> full packet fallback | runtime | gating | hot_path | 14324 | 9297 | 35.1% |
| selector legality failure -> full-doc fallback | runtime | gating | hot_path | 10937 | 9272 | 15.2% |
| planning cold entry | planning | report_only | cold_path | 23605 | 4855 | 79.4% |
| same-stage planner continue | planning | report_only | hot_path | 8069 | 3567 | 55.8% |
| current-stage reviewer entry | planning | report_only | hot_path | 9741 | 5345 | 45.1% |
| review changes requested -> reopen next round | planning | report_only | hot_path | 10513 | 4362 | 58.5% |

## Notes

- Runtime cutover mode is `minimal_preferred`.
- Runtime gate remains `total >= 45%` and `task hot path >= 50%` only while runtime cutover mode stays in a minimal-first state.
- Planning scenarios are tracked in a separate report-only block and do not currently gate the run.
- Packet dumps, when requested, expose the exact compared text for each scenario so the baseline remains auditable.
- Full-document fallback remains explicit in the packet text; it is measured, not hidden.
