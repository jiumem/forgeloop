# Changelog

## 1.0.0 - 2026-04-10

- closed the remaining planning/runtime contract gaps so `Planning State Doc` and `Global State Doc` now act as the only control spines with explicit dispatcher ownership and reread-plus-rebind rules
- finalized the unified runtime object model around `run-initiative`, `code-loop`, `rebuild-runtime`, and `runtime-object-selection.md`, including non-persisted `frontier`, explicit object release semantics, and runtime-only rebinding inside one sealed execution map
- added coder-owned runtime intent blocks, aligned reviewer and supervisor routing vocabulary, and kept formal stop and delivery state distinct between routing facts and terminal actions
- closed anchor-addressing release validation by moving required selector coverage onto one enforced registry shared by `anchor-addressing.md`, `validation-matrix.md`, `anchor_slices.py`, and `anchor-slice-smoke.sh`
- refreshed the formal loops bundle export surface to include the finalized runtime object-selection contract and the current shared tooling/contract set

## 0.9.0 - 2026-04-03

- aligned the public release surface with the packaged runtime architecture by treating `task-loop`, `milestone-loop`, and `initiative-loop` as historical compatibility vocabulary while documenting `code-loop` as the shipped runtime executor
- renamed the remaining public-facing `plan_reviewer` references to `total_task_doc_reviewer` so release docs, active planning artifacts, and packaged agent names now agree
- corrected active Initiative planning artifacts to the current rolling-doc and runtime naming surface, including `total-task-doc-rolling.md` and `code-loop` mode-based runtime execution
- marked legacy design and planning manuscripts as historical so they no longer read like the active 0.9.0 contract surface
- refreshed the token benchmark baselines after the documentation and release-surface cleanup

## 0.8.0 - 2026-04-02

- removed legacy repo-root control-plane path semantics and made the Initiative-local sibling `.forgeloop/` directory the only legal repo-local control-plane root for planning and runtime
- closed planning durable-ref semantics by binding canonical `stage_reference_ref` and `rolling_doc_contract_ref` to real repo-root-relative plugin refs instead of shorthand `references/...`
- clarified that planning rolling docs remain the formal status truth while artifact prose status is only a readability mirror that must be repaired if it drifts
- added light reviewer-first evidence scaffolding for `Gap Analysis Doc` and `Total Task Doc` so high-impact current-state surfaces and minimum evidence entrypoints are harder to omit without turning the templates into rigid schemas
- added `tests/codex/control-plane-root-lint.sh`, wired it into the Codex-only release gate, and refreshed packet benchmark baselines after the doc-contract changes

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
- tightened planning worker prompts so `planner`, `design_reviewer`, `gap_reviewer`, and `total_task_doc_reviewer` consume stage-local refs, contracts, selectors, and same-source slices instead of dispatcher workflow narration
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
