# Forgeloop Token Benchmark Baseline

Generated from:

```bash
bash tests/codex/token-benchmark/run.sh
```

Method:

- legacy packet = representative full-document packet for the scenario
- minimal packet = representative anchor-addressed packet plus any legal derived views
- packet size includes packet wrapper metadata plus referenced body content
- approx tokens = `ceil(characters / 4)`

## Aggregate

- Hot path reduction: `58.8%` (`59012 -> 24308` approx tokens)
- Cold path reduction: `66.5%` (`48709 -> 16317` approx tokens)
- Total reduction: `62.3%` (`107721 -> 40625` approx tokens)
- Task hot-path average reduction: `51.6%`

## Representative Paths

| Scenario | Bucket | Legacy | Minimal | Reduction |
| --- | --- | ---: | ---: | ---: |
| Runtime Cold Start | cold | 18826 | 9010 | 52.1% |
| Runtime Resume Into Active Task | hot | 23206 | 9214 | 60.3% |
| Same-Task Same-Round Coder Continue | hot | 5379 | 2790 | 48.1% |
| Same-Task Handoff To Fresh Reviewer | hot | 7144 | 3835 | 46.3% |
| Milestone Review | hot | 11637 | 4453 | 61.7% |
| Initiative Review | hot | 11646 | 4016 | 65.5% |
| Rebuild Runtime | cold | 16477 | 3643 | 77.9% |
| Waiting Or Blocked Resume | cold | 13406 | 3664 | 72.7% |

## Notes

- The Task hot path in this baseline lands between roughly `46%` and `60%` reduction, depending on whether the scenario is fresh-reviewer entry, coder-continue, or task-resume.
- Full-document fallback remains explicit and legal for cold start, rebuild, legality failure, and anchor conflict.
- These numbers are deterministic approximations from tracked fixtures and should be compared revision-to-revision rather than treated as provider telemetry.
