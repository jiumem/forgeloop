# Initiative Control-Plane Root Contract

<!-- forgeloop:anchor document-role -->
## Document Role

- Plane: shared repo-local placement rule
- Applies to: planning and runtime control-plane docs for one Initiative
- Primary readers: `run-planning`, `run-initiative`, `Total Task Doc` authors, and recovery flows
- Primary purpose: define the default repo-local control-plane root and the default repo-root-relative refs that live under it

<!-- forgeloop:anchor default-root-law -->
## Default Root Law

- When an Initiative is represented by repo-local planning artifacts, the default control-plane root is a sibling `.forgeloop/` directory under the Initiative document directory.
- If the bound Initiative artifact is `docs/initiatives/active/live-gmail-lane/design.md`, the default control-plane root is `docs/initiatives/active/live-gmail-lane/.forgeloop/`.
- Durable refs under this root must stay repo-root-relative.
- Materialize absolute paths only after the active workspace or dispatch target is already bound.
- When explicit control-plane refs are absent during cold start or legal recovery, prefer this Initiative-local root before any wider repo search.

<!-- forgeloop:anchor planning-defaults -->
## Planning Defaults

- `planning_state_doc_ref` -> `<initiative_dir>/.forgeloop/planning-state.md`
- `design_rolling_doc_ref` -> `<initiative_dir>/.forgeloop/design-rolling.md`
- `gap_rolling_doc_ref` -> `<initiative_dir>/.forgeloop/gap-rolling.md`
- `plan_rolling_doc_ref` -> `<initiative_dir>/.forgeloop/plan-rolling.md`

`run-planning` may derive these defaults from the bound Initiative artifact directory when no stronger explicit planning refs already exist.

<!-- forgeloop:anchor runtime-defaults -->
## Runtime Defaults

- `global_state_doc_ref` -> `<initiative_dir>/.forgeloop/global-state.md`
- `task_review_rolling_doc_root_ref` -> `<initiative_dir>/.forgeloop/task-review/`
- `milestone_review_rolling_doc_root_ref` -> `<initiative_dir>/.forgeloop/milestone-review/`
- `initiative_review_rolling_doc_ref` -> `<initiative_dir>/.forgeloop/initiative-review.md`

`Total Task Doc` reference assignment should default to these runtime refs unless the Initiative has a real documented reason to override them.

<!-- forgeloop:anchor override-and-legacy-law -->
## Override And Legacy Law

- Explicit repo-root-relative refs already sealed in planning truth override the derived defaults.
- If an older Initiative already binds repo-root-relative refs outside the default Initiative-local root, honor those bound refs instead of rewriting them implicitly.
- Legacy repo-root layouts such as `.forgeloop/<initiative_key>/...` may remain legal when already bound, but they are not the default inference target for new Initiatives.
- Do not maintain parallel control-plane roots for one Initiative.
