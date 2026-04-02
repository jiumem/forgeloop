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

- Hot path reduction: 49.8% (104076 -> 52224 tok approx)
- Cold path reduction: 70.3% (54545 -> 16199 tok approx)
- Total reduction: 56.9% (158621 -> 68423 tok approx)
- Task hot path average reduction: 60.6%
- Gate mode: gating

## Planning Aggregate

- Hot path reduction: 58.3% (26735 -> 11140 tok approx)
- Cold path reduction: 77.4% (21042 -> 4757 tok approx)
- Total reduction: 66.7% (47777 -> 15897 tok approx)
- Gate mode: report-only

## Scenario Baseline

| Scenario | Scope | Gating | Bucket | Legacy | Minimal | Reduction |
| --- | --- | --- | --- | ---: | ---: | ---: |
| Runtime Cold Start | runtime | gating | cold_path | 20997 | 10132 | 51.7% |
| Runtime Resume Into Active Task | runtime | gating | hot_path | 25103 | 7860 | 68.7% |
| Same-Task Same-Round Coder Continue | runtime | gating | hot_path | 7599 | 3815 | 49.8% |
| Same-Task Handoff To Fresh Reviewer | runtime | gating | hot_path | 9038 | 4391 | 51.4% |
| Milestone Review | runtime | gating | hot_path | 14128 | 5795 | 59.0% |
| Initiative Review | runtime | gating | hot_path | 14094 | 5344 | 62.1% |
| Rebuild Runtime | runtime | gating | cold_path | 18055 | 4019 | 77.7% |
| Waiting Or Blocked Resume | runtime | gating | cold_path | 15493 | 2048 | 86.8% |
| same-task warm-path delta legal | runtime | gating | hot_path | 12584 | 3450 | 72.6% |
| same-task warm-path delta illegal -> full packet fallback | runtime | gating | hot_path | 12615 | 12640 | -0.2% |
| selector legality failure -> full-doc fallback | runtime | gating | hot_path | 8915 | 8929 | -0.2% |
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
