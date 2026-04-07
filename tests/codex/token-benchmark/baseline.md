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

- Hot path reduction: 65.5% (123490 -> 42621 tok approx)
- Cold path reduction: 78.6% (63505 -> 13577 tok approx)
- Total reduction: 69.9% (186995 -> 56198 tok approx)
- Task hot path average reduction: 67.3%
- Gate mode: gating

## Planning Aggregate

- Hot path reduction: 50.6% (26313 -> 13010 tok approx)
- Cold path reduction: 79.5% (22779 -> 4677 tok approx)
- Total reduction: 64.0% (49092 -> 17687 tok approx)
- Gate mode: report-only

## Scenario Baseline

| Scenario | Scope | Gating | Bucket | Legacy | Minimal | Reduction |
| --- | --- | --- | --- | ---: | ---: | ---: |
| Runtime Cold Start | runtime | gating | cold_path | 24314 | 7668 | 68.5% |
| Runtime Resume Into Active Task | runtime | gating | hot_path | 29353 | 3991 | 86.4% |
| Same-Task Same-Round Coder Continue | runtime | gating | hot_path | 9012 | 4421 | 50.9% |
| Same-Task Handoff To Fresh Reviewer | runtime | gating | hot_path | 10634 | 4084 | 61.6% |
| Milestone Review | runtime | gating | hot_path | 16579 | 4294 | 74.1% |
| Initiative Review | runtime | gating | hot_path | 16509 | 4107 | 75.1% |
| Rebuild Runtime | runtime | gating | cold_path | 20390 | 3696 | 81.9% |
| Waiting Or Blocked Resume | runtime | gating | cold_path | 18801 | 2213 | 88.2% |
| same-task warm-path delta legal | runtime | gating | hot_path | 15258 | 4529 | 70.3% |
| same-task warm-path delta illegal -> full packet fallback | runtime | gating | hot_path | 15288 | 8610 | 43.7% |
| selector legality failure -> full-doc fallback | runtime | gating | hot_path | 10857 | 8585 | 20.9% |
| planning cold entry | planning | report_only | cold_path | 22779 | 4677 | 79.5% |
| same-stage planner continue | planning | report_only | hot_path | 7417 | 3653 | 50.7% |
| fresh planning reviewer handoff | planning | report_only | hot_path | 9035 | 5344 | 40.9% |
| review changes requested -> reopen next round | planning | report_only | hot_path | 9861 | 4013 | 59.3% |

## Notes

- Runtime cutover mode is `minimal_preferred`.
- Runtime gate remains `total >= 45%` and `task hot path >= 50%` only while runtime cutover mode stays in a minimal-first state.
- Planning scenarios are tracked in a separate report-only block and do not currently gate the run.
- Packet dumps, when requested, expose the exact compared text for each scenario so the baseline remains auditable.
- Full-document fallback remains explicit in the packet text; it is measured, not hidden.
