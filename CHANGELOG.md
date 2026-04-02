# Changelog

## 0.7.0 - 2026-04-02

- changed `run-planning` from a stage-by-stage launcher into a same-activation planning runner that rereads formal state and loops across Design, Gap, and Total Task when routing stays legal
- made planning minimal packets explicit by default and forbade ordinary planner/reviewer packets from depending on supervisor skill docs as authoritative payload
- tightened planning worker prompts so `planner`, `design_reviewer`, `gap_reviewer`, and `plan_reviewer` consume stage-local refs, contracts, selectors, and same-source slices instead of dispatcher workflow narration
- strengthened planning recovery law by requiring `planner_slot` and `round` to be written back into the `Planning State Doc` as soon as they are formally recoverable
- added planning-side regression checks for same-activation planning loop-back and packet-lint enforcement, and refreshed token benchmark fixtures and baselines around the slimmer planning hot paths
- kept runtime token gates passing while improving planning hot-path reductions to 58.2% and planning total reduction to 66.6%

## 0.6.0 - 2026-04-02

- tightened planning and runtime control-plane contracts without widening the workflow surface
- aligned planning durable refs and routing semantics around repo-root-relative truth plus explicit stage control
- added planning-side control and anchor requirements so anchor-addressed packets now have a documented landing surface
- tightened reviewer prompt contracts around canonical snake_case YAML keys
- corrected runtime loop initialization wording so `round` remains owned by the `Global State Doc`
- updated the formal loops bundle to include the planning-state control reference

## 0.5.0

- first repo-local Codex plugin package release
