# Planning State Doc Control Reference

## Document Role

- Plane: planning control spine
- Applies to: the active planning state for one Initiative
- Primary readers: `run-planning` and `planning-loop`
- Primary purpose: keep only the minimum planning control state needed for recovery, dispatch, and legal stop routing

## Legal Blocks

- `current_snapshot`
- `next_action`
- `last_transition`

## Control Law

- `Planning State Doc` is the only planning control spine.
- `current_snapshot` carries only the bound Initiative, active stage, active `artifact_ref`, active `rolling_doc_ref`, and when known `planner_slot` plus `round`.
- `artifact_ref` and `rolling_doc_ref` must use durable repo-root-relative refs. Materialize absolute paths only at dispatch time when needed.
- only a fresh stage with no rolling doc may temporarily omit `planner_slot` and `round`
- `next_action` carries only the current planning route or stop signal
- `last_transition` carries only the most recent bind, recovery, resume, reopen, or cross-stage routing fact

## Red Lines

- do not write planner or reviewer body content here
- do not create a second planning control model outside the formal planning artifacts, rolling docs, and this document
