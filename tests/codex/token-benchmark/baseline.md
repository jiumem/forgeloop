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

- Hot path reduction: 58.3% (104727 -> 43665 tok approx)
- Cold path reduction: 70.3% (56387 -> 16720 tok approx)
- Total reduction: 62.5% (161114 -> 60385 tok approx)
- Task hot path average reduction: 63.1%
- Gate mode: gating

## Planning Aggregate

- Hot path reduction: 58.3% (26735 -> 11140 tok approx)
- Cold path reduction: 77.4% (21070 -> 4757 tok approx)
- Total reduction: 66.7% (47805 -> 15897 tok approx)
- Gate mode: report-only

## Scenario Baseline

| Scenario | Scope | Gating | Bucket | Legacy | Minimal | Reduction |
| --- | --- | --- | --- | ---: | ---: | ---: |
| Runtime Cold Start | runtime | gating | cold_path | 21704 | 10492 | 51.7% |
| Runtime Resume Into Active Task | runtime | gating | hot_path | 25464 | 7466 | 70.7% |
| Same-Task Same-Round Coder Continue | runtime | gating | hot_path | 7609 | 4234 | 44.4% |
| Same-Task Handoff To Fresh Reviewer | runtime | gating | hot_path | 9047 | 2653 | 70.7% |
| Milestone Review | runtime | gating | hot_path | 13569 | 4725 | 65.2% |
| Initiative Review | runtime | gating | hot_path | 13507 | 4342 | 67.9% |
| Rebuild Runtime | runtime | gating | cold_path | 18483 | 4180 | 77.4% |
| Waiting Or Blocked Resume | runtime | gating | cold_path | 16200 | 2048 | 87.4% |
| same-task warm-path delta legal | runtime | gating | hot_path | 12945 | 4342 | 66.5% |
| same-task warm-path delta illegal -> full packet fallback | runtime | gating | hot_path | 12975 | 7964 | 38.6% |
| selector legality failure -> full-doc fallback | runtime | gating | hot_path | 9611 | 7939 | 17.4% |
| planning cold entry | planning | report_only | cold_path | 21070 | 4757 | 77.4% |
| same-stage planner continue | planning | report_only | hot_path | 7533 | 2690 | 64.3% |
| fresh planning reviewer handoff | planning | report_only | hot_path | 9228 | 4528 | 50.9% |
| review changes requested -> reopen next round | planning | report_only | hot_path | 9974 | 3922 | 60.7% |

## Notes

- Runtime cutover mode is `minimal_preferred`.
- Runtime gate remains `total >= 45%` and `task hot path >= 50%` only while runtime cutover mode stays in a minimal-first state.
- Planning scenarios are tracked in a separate report-only block and do not currently gate the run.
- Packet dumps, when requested, expose the exact compared text for each scenario so the baseline remains auditable.
- Full-document fallback remains explicit in the packet text; it is measured, not hidden.
