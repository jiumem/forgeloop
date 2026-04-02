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

- Hot path reduction: 52.7% (99946 -> 47240 tok approx)
- Cold path reduction: 70.2% (54722 -> 16313 tok approx)
- Total reduction: 58.9% (154668 -> 63553 tok approx)
- Task hot path average reduction: 63.8%
- Gate mode: gating

## Planning Aggregate

- Hot path reduction: 58.3% (26735 -> 11140 tok approx)
- Cold path reduction: 77.4% (21042 -> 4757 tok approx)
- Total reduction: 66.7% (47777 -> 15897 tok approx)
- Gate mode: report-only

## Scenario Baseline

| Scenario | Scope | Gating | Bucket | Legacy | Minimal | Reduction |
| --- | --- | --- | --- | ---: | ---: | ---: |
| Runtime Cold Start | runtime | gating | cold_path | 21038 | 10160 | 51.7% |
| Runtime Resume Into Active Task | runtime | gating | hot_path | 24686 | 7354 | 70.2% |
| Same-Task Same-Round Coder Continue | runtime | gating | hot_path | 7164 | 3039 | 57.6% |
| Same-Task Handoff To Fresh Reviewer | runtime | gating | hot_path | 8602 | 4151 | 51.7% |
| Milestone Review | runtime | gating | hot_path | 13124 | 4492 | 65.8% |
| Initiative Review | runtime | gating | hot_path | 13061 | 4081 | 68.8% |
| Rebuild Runtime | runtime | gating | cold_path | 18150 | 4105 | 77.4% |
| Waiting Or Blocked Resume | runtime | gating | cold_path | 15534 | 2048 | 86.8% |
| same-task warm-path delta legal | runtime | gating | hot_path | 12167 | 2941 | 75.8% |
| same-task warm-path delta illegal -> full packet fallback | runtime | gating | hot_path | 12197 | 12223 | -0.2% |
| selector legality failure -> full-doc fallback | runtime | gating | hot_path | 8945 | 8959 | -0.2% |
| planning cold entry | planning | report_only | cold_path | 21042 | 4757 | 77.4% |
| same-stage planner continue | planning | report_only | hot_path | 7533 | 2690 | 64.3% |
| fresh planning reviewer handoff | planning | report_only | hot_path | 9228 | 4528 | 50.9% |
| review changes requested -> reopen next round | planning | report_only | hot_path | 9974 | 3922 | 60.7% |

## Notes

- Runtime cutover mode is `minimal_preferred`.
- Runtime gate remains `total >= 45%` and `task hot path >= 50%` only while runtime cutover mode stays in a minimal-first state.
- Planning scenarios are tracked in a separate report-only block and do not currently gate the run.
- Packet dumps, when requested, expose the exact compared text for each scenario so the baseline remains auditable.
- Full-document fallback remains explicit in the packet text; it is measured, not hidden.
