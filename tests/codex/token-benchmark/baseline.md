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

- Hot path reduction: 69.9% (122089 -> 36802 tok approx)
- Cold path reduction: 89.8% (64597 -> 6588 tok approx)
- Total reduction: 76.8% (186686 -> 43390 tok approx)
- Task hot path average reduction: 70.3%
- Gate mode: gating

## Planning Aggregate

- Hot path reduction: 52.1% (27764 -> 13292 tok approx)
- Cold path reduction: 79.0% (23244 -> 4883 tok approx)
- Total reduction: 64.4% (51008 -> 18175 tok approx)
- Gate mode: report-only

## Scenario Baseline

| Scenario | Scope | Gating | Bucket | Legacy | Minimal | Reduction |
| --- | --- | --- | --- | ---: | ---: | ---: |
| Runtime Cold Start | runtime | gating | cold_path | 25152 | 3303 | 86.9% |
| Runtime Resume Into Active Task | runtime | gating | hot_path | 29584 | 1874 | 93.7% |
| Same-Task Same-Round Coder Continue | runtime | gating | hot_path | 8246 | 3848 | 53.3% |
| Same-Task Reviewer Entry | runtime | gating | hot_path | 9392 | 3812 | 59.4% |
| Milestone Review | runtime | gating | hot_path | 16050 | 3536 | 78.0% |
| Initiative Review | runtime | gating | hot_path | 15862 | 3367 | 78.8% |
| Rebuild Runtime | runtime | gating | cold_path | 19805 | 1603 | 91.9% |
| Waiting Or Blocked Resume | runtime | gating | cold_path | 19640 | 1682 | 91.4% |
| same-task warm-path delta legal | runtime | gating | hot_path | 15489 | 3888 | 74.9% |
| same-task warm-path delta illegal -> full packet fallback | runtime | gating | hot_path | 15519 | 8251 | 46.8% |
| selector legality failure -> full-doc fallback | runtime | gating | hot_path | 11947 | 8226 | 31.1% |
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
