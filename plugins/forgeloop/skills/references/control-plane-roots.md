# Initiative Control-Plane Root Contract

<!-- forgeloop:anchor document-role -->
## Document Role

- Plane: shared repo-local placement rule
- Applies to: planning and runtime control-plane docs for one Initiative
- Primary readers: `run-planning`, `run-initiative`, `Total Task Doc` authors, and recovery flows
- Primary purpose: define the one legal repo-local control-plane root and the canonical repo-root-relative refs that live under it

<!-- forgeloop:anchor root-law -->
## Root Law

- When an Initiative is represented by repo-local planning artifacts, the only legal repo-local control-plane root is a sibling `.forgeloop/` directory under the Initiative document directory.
- If the bound Initiative artifact is `docs/initiatives/active/live-gmail-lane/design.md`, the legal control-plane root is `docs/initiatives/active/live-gmail-lane/.forgeloop/`.
- All repo-local planning and runtime control-plane refs for that Initiative must stay under this one root.
- Do not bind a repo-local planning or runtime control-plane ref outside this root.
- Durable refs under this root must stay repo-root-relative.
- Materialize absolute paths only after the active workspace or dispatch target is already bound.
- Cold start or legal recovery must derive this root directly from the bound Initiative artifact directory. Do not search for alternate repo-local control-plane roots elsewhere in the repository.

<!-- forgeloop:anchor human-entry-law -->
## Human Entry Law

- Each Initiative-local `.forgeloop/` root should include a lightweight `README.md` that points humans to `planning-state.md`, the planning rolling docs, `global-state.md`, and the runtime review roots.
- This `README.md` is a navigation aid only. It must not redefine refs, stages, routing, or formal state.
- Initiative-facing docs may link to that control-plane README, but must not restate the same control-plane refs as a parallel truth source.

<!-- forgeloop:anchor planning-defaults -->
## Canonical Planning Refs

- `planning_state_doc_ref` -> `<initiative_dir>/.forgeloop/planning-state.md`
- `design_rolling_doc_ref` -> `<initiative_dir>/.forgeloop/design-rolling.md`
- `gap_rolling_doc_ref` -> `<initiative_dir>/.forgeloop/gap-rolling.md`
- `total_task_doc_rolling_doc_ref` -> `<initiative_dir>/.forgeloop/total-task-doc-rolling.md`

`run-planning` must derive these refs from the bound Initiative artifact directory for repo-local Initiatives.

<!-- forgeloop:anchor runtime-defaults -->
## Canonical Runtime Refs

- `global_state_doc_ref` -> `<initiative_dir>/.forgeloop/global-state.md`
- `task_review_rolling_doc_root_ref` -> `<initiative_dir>/.forgeloop/task-review/`
- `milestone_review_rolling_doc_root_ref` -> `<initiative_dir>/.forgeloop/milestone-review/`
- `initiative_review_rolling_doc_ref` -> `<initiative_dir>/.forgeloop/initiative-review.md`

`Total Task Doc` reference assignment must use these runtime refs for repo-local Initiatives.

<!-- forgeloop:anchor single-root-consequences -->
## Single-Root Consequences

- Repo-root `.forgeloop/<initiative_key>/...` layouts are not legal control-plane roots for repo-local Initiatives.
- Explicit repo-root-relative refs remain authoritative only when they resolve under the same Initiative-local `.forgeloop/` root.
- Do not maintain parallel control-plane roots for one Initiative.
