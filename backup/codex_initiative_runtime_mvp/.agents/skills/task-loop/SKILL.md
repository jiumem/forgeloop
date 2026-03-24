---
name: task-loop
description: Run one internal Task control loop until the task reaches READY_FOR_ANCHOR or BLOCKED.
---

1. Run `scripts/build_task_packet.py --initiative-doc <doc> --task-key <task>`.
2. Spawn `sensor_primary` with the generated packet and save its JSON observation.
3. Run `scripts/step_transition.py --initiative-doc <doc> --task-key <task> --observation <path>`.
4. Read the decision:
   - REQUEST_RUNTIME_FACTS → run `scripts/collect_runtime_facts.py`
   - PATCH_LOCAL / COMPLETE_MISSING_SCOPE / ADD_PROOF_TESTS / REMOVE_ENTROPY_SIGNAL / REWORK_ARCHITECTURE → spawn `task_worker`
   - ESCALATE_TO_HUMAN → stop and bubble up
   - READY_FOR_ANCHOR → invoke `cut-anchor`, `g1-task-gate`, `r1-task-review`
5. Never widen scope beyond the current Task.
