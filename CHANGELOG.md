# Changelog

## 0.7.1 - 2026-04-02

- formalized one shared Initiative-local control-plane root contract so new planning and runtime control docs default to a sibling `.forgeloop/` directory next to the Initiative documents
- taught `run-planning` to prefer the Initiative-local `.forgeloop/` root before wider repo recovery when `planning_state_doc_ref` is not already bound
- taught `run-initiative` and the `Total Task Doc` reference-assignment contract to use the same Initiative-local `.forgeloop/` default for runtime control refs
- documented the recommended placement directly in `Planning State Doc`, `Planning Rolling Doc`, and `Global State Doc` contracts while keeping explicit sealed repo-root-relative refs authoritative
- kept legacy repo-root `.forgeloop/<initiative_key>/...` layouts legal only when already explicitly bound, instead of silently making them the default for new Initiatives
- updated the formal loops bundle export to include the shared control-plane root contract

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
