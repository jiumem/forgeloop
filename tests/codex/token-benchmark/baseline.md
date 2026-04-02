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

- Hot path reduction: 49.9% (103459 -> 51808 tok approx)
- Cold path reduction: 70.1% (53927 -> 16148 tok approx)
- Total reduction: 56.8% (157386 -> 67956 tok approx)
- Task hot path average reduction: 60.7%
- Gate mode: gating

## Planning Aggregate

- Hot path reduction: 58.4% (26441 -> 10998 tok approx)
- Cold path reduction: 77.3% (20754 -> 4718 tok approx)
- Total reduction: 66.7% (47195 -> 15716 tok approx)
- Gate mode: report-only

## Scenario Baseline

| Scenario | Scope | Gating | Bucket | Legacy | Minimal | Reduction |
| --- | --- | --- | --- | ---: | ---: | ---: |
| Runtime Cold Start | runtime | gating | cold_path | 20790 | 10106 | 51.4% |
| Runtime Resume Into Active Task | runtime | gating | hot_path | 24893 | 7726 | 69.0% |
| Same-Task Same-Round Coder Continue | runtime | gating | hot_path | 7599 | 3815 | 49.8% |
| Same-Task Handoff To Fresh Reviewer | runtime | gating | hot_path | 9038 | 4391 | 51.4% |
| Milestone Review | runtime | gating | hot_path | 13924 | 5645 | 59.5% |
| Initiative Review | runtime | gating | hot_path | 13890 | 5212 | 62.5% |
| Rebuild Runtime | runtime | gating | cold_path | 17845 | 3995 | 77.6% |
| Waiting Or Blocked Resume | runtime | gating | cold_path | 15292 | 2047 | 86.6% |
| same-task warm-path delta legal | runtime | gating | hot_path | 12585 | 3450 | 72.6% |
| same-task warm-path delta illegal -> full packet fallback | runtime | gating | hot_path | 12615 | 12640 | -0.2% |
| selector legality failure -> full-doc fallback | runtime | gating | hot_path | 8915 | 8929 | -0.2% |
| planning cold entry | planning | report_only | cold_path | 20754 | 4718 | 77.3% |
| same-stage planner continue | planning | report_only | hot_path | 7435 | 2619 | 64.8% |
| fresh planning reviewer handoff | planning | report_only | hot_path | 9130 | 4506 | 50.6% |
| review changes requested -> reopen next round | planning | report_only | hot_path | 9876 | 3873 | 60.8% |

## Notes

- Runtime cutover mode is `minimal_preferred`.
- Runtime gate remains `total >= 45%` and `task hot path >= 50%` only while runtime cutover mode stays in a minimal-first state.
- Planning scenarios are tracked in a separate report-only block and do not currently gate the run.
- Packet dumps, when requested, expose the exact compared text for each scenario so the baseline remains auditable.
- Full-document fallback remains explicit in the packet text; it is measured, not hidden.
