# Forgeloop Derived View Contract

<!-- forgeloop:anchor document-role -->
## Document Role

- Plane: runtime reference
- Applies to: Task / Milestone / Initiative runtime review rolling docs
- Primary readers: `run-initiative`, `rebuild-runtime`, runtime loop skills, reviewers, validation tooling
- Primary purpose: define non-authoritative `current-effective` and `round-scoped` projections that may shrink hot-path reads without changing freshness law

<!-- forgeloop:anchor authority-line -->
## Authority Line

- Runtime review rolling docs remain the only authority for `round`, `review_target_ref`, `compare_base_ref`, prior-review linkage, freshness, and closure semantics.
- Every derived view is disposable and rebuildable.
- A derived view never outranks or overwrites its source rolling doc.
- If any disagreement appears, invalidate the derived view and reread the formal rolling doc.

<!-- forgeloop:anchor view-types -->
## View Types

- `current-effective`
  - one synthesized view of the latest runtime round
  - it should expose the latest round's `review_handoff`, the same round's `review_result` when present, and the addressed prior `review_result` when `addresses_review_result_id` is present
  - it must not surface superseded or duplicate current-round blocks because those are illegal in v2
- `round-scoped`
  - one projection per `round` containing every formal runtime block for that round in append order
  - it is the default hot-path helper for reading one complete runtime cycle without scanning unrelated history

Planning rolling docs use their own derived-view contract under `plugins/forgeloop/skills/planning-loop/references/planning-derived-views.md`.

<!-- forgeloop:anchor materialization -->
## Materialization

- Recommended location: `<initiative_dir>/.forgeloop/derived/<plane>/<object>/...`
- Derived views for a repo-local Initiative must live under the same Initiative-local `.forgeloop/` root as the authoritative rolling doc they derive from.
- Do not place repo-local Initiative derived views under repo-root `.forgeloop/<initiative_key>/...`.
- Materialized files must state clearly that they are non-authoritative derived views.
- Materialization may be skipped entirely; consumers can always fall back to direct anchored reads from the formal document.
- A derived view should be cheap to delete and cheap to rebuild.

<!-- forgeloop:anchor invalidation -->
## Invalidation Rules

Invalidate the relevant derived view immediately when:

- a newer formal block is appended to the source rolling doc
- the source rolling doc now exposes an illegal duplicate `review_handoff` or `review_result` for one round
- the latest round no longer matches what the view materialized
- the source packet can no longer prove selector legality for the formal inputs the view depends on
- an addressed prior `review_result_id` no longer resolves uniquely
- an anchor selector in the projection input becomes missing, duplicated, or illegal

Invalidation never changes formal truth. It only changes whether the projection may still be consumed.

<!-- forgeloop:anchor consumer-law -->
## Consumer Law

- Consumers may prefer derived views on the hot path only when the formal source ref is still bound explicitly in the packet.
- Consumers must be able to recover by rereading the formal rolling doc if the derived view is missing or invalid.
- Consumers must not persist decisions that depend only on a derived view without also persisting the authoritative `doc_ref + anchor_selector` basis for recovery.

<!-- forgeloop:anchor builder-hook -->
## Builder Hook

`python3 plugins/forgeloop/scripts/anchor_slices.py derive --doc <rolling-doc> --out <dir>` is the canonical repository helper for rebuilding disposable projections from formal rolling docs.
