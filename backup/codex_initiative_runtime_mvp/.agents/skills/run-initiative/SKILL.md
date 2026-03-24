---
name: run-initiative
description: Run one Initiative from its total-task document, select the active milestone frontier, and route work into internal task loops.
---

1. Resolve the initiative document from `docs/initiatives/<INIT_KEY>.md`.
2. Run `scripts/planning_preflight.py --initiative-doc <doc>`.
3. Run `scripts/rebuild_state.py --initiative-doc <doc>`.
4. Run `scripts/select_frontier.py --initiative-doc <doc>`.
5. Run `scripts/select_ready_tasks.py --initiative-doc <doc>`.
6. For each selected write task, invoke the internal `task-loop` skill.
7. If the frontier milestone is sealable, invoke `open-milestone-pr`, `g2-milestone-gate`, and `r2-milestone-review`.
8. If the initiative becomes deliverable, invoke `g3-initiative-gate` and `r3-initiative-review`.
9. Stop only at milestone, escalation, or delivery breakpoints.
