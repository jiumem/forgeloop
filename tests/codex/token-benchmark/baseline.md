# Forgeloop Token Benchmark Baseline

Generated from:

```bash
bash tests/codex/token-benchmark/run.sh
```

Method:

- legacy packet = representative full-document packet for the scenario
- minimal packet = representative anchor-addressed packet plus any legal derived views
- approx tokens = `ceil(characters / 4)`

## Aggregate

- Hot path reduction: `60.3%` (`58423 -> 23169` approx tokens)
- Cold path reduction: `68.1%` (`48307 -> 15414` approx tokens)
- Total reduction: `63.8%` (`106730 -> 38583` approx tokens)
- Task hot-path average reduction: `53.4%`

## Representative Paths

| Scenario | Bucket | Legacy | Minimal | Reduction |
| --- | --- | ---: | ---: | ---: |
| Runtime Cold Start | cold | 18698 | 8642 | 53.8% |
| Runtime Resume Into Active Task | hot | 23011 | 8899 | 61.3% |
| Same-Task Same-Round Coder Continue | hot | 5284 | 2574 | 51.3% |
| Same-Task Handoff To Fresh Reviewer | hot | 7054 | 3687 | 47.7% |
| Milestone Review | hot | 11533 | 4223 | 63.4% |
| Initiative Review | hot | 11541 | 3786 | 67.2% |
| Rebuild Runtime | cold | 16302 | 3358 | 79.4% |
| Waiting Or Blocked Resume | cold | 13307 | 3414 | 74.3% |

## Notes

- The Task hot path in this baseline lands between roughly `48%` and `61%` reduction, depending on whether the scenario is fresh-reviewer entry, coder-continue, or task-resume.
- Full-document fallback remains explicit and legal for cold start, rebuild, legality failure, and anchor conflict.
- These numbers are deterministic approximations from tracked fixtures and should be compared revision-to-revision rather than treated as provider telemetry.
