# Planning State Doc Control Reference

<!-- forgeloop:anchor document-role -->
## Document Role

- Plane: planning control spine
- Applies to: the active planning state for one Initiative
- Primary readers: `run-planning` and `planning-loop`
- Primary purpose: keep only the minimum planning control state needed for recovery, dispatch, and legal stop routing
- For repo-local Initiatives, required placement is sibling `.forgeloop/planning-state.md` under the Initiative document directory

<!-- forgeloop:anchor legal-blocks -->
## Legal Blocks

- `current_snapshot`
- `next_action`
- `last_transition`

<!-- forgeloop:anchor control-law -->
## Control Law

- `Planning State Doc` is the only planning control spine.
- `current_snapshot` carries only the bound Initiative, active stage, active `artifact_ref`, active `rolling_doc_ref`, and when known `planner_slot` plus `round`.
- `artifact_ref` and `rolling_doc_ref` must use durable repo-root-relative refs. Materialize absolute paths only at dispatch time when needed.
- only a fresh stage with no rolling doc may temporarily omit `planner_slot` and `round`
- once `planner_slot` or `round` is known from the active rolling doc or recovery, write it back into `current_snapshot` immediately; do not leave recoverable values implicit after the stage is in flight
- `next_action` carries only the current planning route or stop signal
- `next_action` carries only the immediate in-stage dispatch or stop signal for the currently bound stage; cross-stage routes such as `advance_*` and `reopen_*` belong in `last_transition`, not as a parallel planning state
- `last_transition` carries only the most recent bind, recovery, resume, reopen, or cross-stage routing fact

<!-- forgeloop:anchor red-lines -->
## Red Lines

- do not write planner or reviewer body content here
- do not create a second planning control model outside the formal planning artifacts, rolling docs, and this document
