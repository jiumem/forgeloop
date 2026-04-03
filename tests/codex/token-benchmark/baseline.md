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

- Hot path reduction: 59.5% (108296 -> 43840 tok approx)
- Cold path reduction: 69.6% (57140 -> 17358 tok approx)
- Total reduction: 63.0% (165436 -> 61198 tok approx)
- Task hot path average reduction: 64.6%
- Gate mode: gating

## Planning Aggregate

- Hot path reduction: 50.4% (25697 -> 12743 tok approx)
- Cold path reduction: 78.1% (20929 -> 4579 tok approx)
- Total reduction: 62.8% (46626 -> 17322 tok approx)
- Gate mode: report-only

## Scenario Baseline

| Scenario | Scope | Gating | Bucket | Legacy | Minimal | Reduction |
| --- | --- | --- | --- | ---: | ---: | ---: |
| Runtime Cold Start | runtime | gating | cold_path | 22031 | 10905 | 50.5% |
| Runtime Resume Into Active Task | runtime | gating | hot_path | 26088 | 7501 | 71.2% |
| Same-Task Same-Round Coder Continue | runtime | gating | hot_path | 7974 | 4199 | 47.3% |
| Same-Task Handoff To Fresh Reviewer | runtime | gating | hot_path | 9426 | 2674 | 71.6% |
| Milestone Review | runtime | gating | hot_path | 13935 | 4750 | 65.9% |
| Initiative Review | runtime | gating | hot_path | 13872 | 4366 | 68.5% |
| Rebuild Runtime | runtime | gating | cold_path | 18591 | 4271 | 77.0% |
| Waiting Or Blocked Resume | runtime | gating | cold_path | 16518 | 2182 | 86.8% |
| same-task warm-path delta legal | runtime | gating | hot_path | 13563 | 4305 | 68.3% |
| same-task warm-path delta illegal -> full packet fallback | runtime | gating | hot_path | 13593 | 8035 | 40.9% |
| selector legality failure -> full-doc fallback | runtime | gating | hot_path | 9845 | 8010 | 18.6% |
| planning cold entry | planning | report_only | cold_path | 20929 | 4579 | 78.1% |
| same-stage planner continue | planning | report_only | hot_path | 7212 | 3554 | 50.7% |
| fresh planning reviewer handoff | planning | report_only | hot_path | 8830 | 5315 | 39.8% |
| review changes requested -> reopen next round | planning | report_only | hot_path | 9655 | 3874 | 59.9% |

## Notes

- Runtime cutover mode is `minimal_preferred`.
- Runtime gate remains `total >= 45%` and `task hot path >= 50%` only while runtime cutover mode stays in a minimal-first state.
- Planning scenarios are tracked in a separate report-only block and do not currently gate the run.
- Packet dumps, when requested, expose the exact compared text for each scenario so the baseline remains auditable.
- Full-document fallback remains explicit in the packet text; it is measured, not hidden.
