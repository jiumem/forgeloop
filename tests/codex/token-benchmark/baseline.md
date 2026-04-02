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

- Hot path reduction: 50.0% (103006 -> 51494 tok approx)
- Cold path reduction: 70.2% (53619 -> 15972 tok approx)
- Total reduction: 56.9% (156625 -> 67466 tok approx)
- Task hot path average reduction: 60.7%
- Gate mode: gating

## Planning Aggregate

- Hot path reduction: 58.2% (26297 -> 10998 tok approx)
- Cold path reduction: 77.2% (20705 -> 4718 tok approx)
- Total reduction: 66.6% (47002 -> 15716 tok approx)
- Gate mode: report-only

## Scenario Baseline

| Scenario | Scope | Gating | Bucket | Legacy | Minimal | Reduction |
| --- | --- | --- | --- | ---: | ---: | ---: |
| Runtime Cold Start | runtime | gating | cold_path | 20636 | 10018 | 51.5% |
| Runtime Resume Into Active Task | runtime | gating | hot_path | 24780 | 7638 | 69.2% |
| Same-Task Same-Round Coder Continue | runtime | gating | hot_path | 7599 | 3815 | 49.8% |
| Same-Task Handoff To Fresh Reviewer | runtime | gating | hot_path | 9038 | 4391 | 51.4% |
| Milestone Review | runtime | gating | hot_path | 13924 | 5645 | 59.5% |
| Initiative Review | runtime | gating | hot_path | 13890 | 5212 | 62.5% |
| Rebuild Runtime | runtime | gating | cold_path | 17845 | 3995 | 77.6% |
| Waiting Or Blocked Resume | runtime | gating | cold_path | 15138 | 1959 | 87.1% |
| same-task warm-path delta legal | runtime | gating | hot_path | 12471 | 3450 | 72.3% |
| same-task warm-path delta illegal -> full packet fallback | runtime | gating | hot_path | 12502 | 12527 | -0.2% |
| selector legality failure -> full-doc fallback | runtime | gating | hot_path | 8802 | 8816 | -0.2% |
| planning cold entry | planning | report_only | cold_path | 20705 | 4718 | 77.2% |
| same-stage planner continue | planning | report_only | hot_path | 7387 | 2619 | 64.5% |
| fresh planning reviewer handoff | planning | report_only | hot_path | 9082 | 4506 | 50.4% |
| review changes requested -> reopen next round | planning | report_only | hot_path | 9828 | 3873 | 60.6% |

## Notes

- Runtime cutover mode is `minimal_preferred`.
- Runtime gate remains `total >= 45%` and `task hot path >= 50%` only while runtime cutover mode stays in a minimal-first state.
- Planning scenarios are tracked in a separate report-only block and do not currently gate the run.
- Packet dumps, when requested, expose the exact compared text for each scenario so the baseline remains auditable.
- Full-document fallback remains explicit in the packet text; it is measured, not hidden.
