---
name: run-initiative-sequences
description: Use when the user asks to run multiple consecutive active Initiatives under docs/initiatives/active as a sequence; wraps run-initiative without replacing it.
---
# run-initiative-sequences
Rules:
1. Enumerate `docs/initiatives/active/*` lexicographically by initiative code; if no sequence is specified, ask whether to run all active initiatives or an inclusive range.
2. Accept explicit initiative names, paths, or inclusive code ranges; preserve order and do not assume continuous numbers.
3. Before starting, require `PLAN.md` and `LEDGER.md` for every selected initiative.
4. Keep one Scheduler in the main thread; run exactly one initiative at a time; never parallelize initiatives.
5. For each initiative, invoke the normal `run-initiative` workflow and obey its Coder / Reviewer / PASS / repair / delivery rules.
6. Use fresh Coder and Reviewer subagents per initiative, reused only within that initiative; use `fork_context=false` with file-grounded task packets.
7. Create one branch checkpoint per initiative; each next branch starts from the previous completed initiative head.
8. Commit and push during the sequence, but do not open PRs mid-sequence.
9. Move completed initiatives to `docs/initiatives/completed` through `run-initiative`.
10. Stop on dirty baseline risk, missing credentials, destructive-risk approval, blocked initiative, repair-budget stop, or next initiative needing replan.
Output:
- sequence queue
- current initiative transition
- final aggregate PR summary; final PR is a merge vehicle, not a replacement for per-initiative Reviewer PASS
