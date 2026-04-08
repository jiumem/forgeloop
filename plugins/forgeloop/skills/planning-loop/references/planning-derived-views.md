# Planning Derived View Contract

<!-- forgeloop:anchor document-role -->
## Document Role

- Plane: planning reference
- Applies to: `Design Rolling Doc`, `Gap Rolling Doc`, and `Total Task Doc Rolling Doc`
- Primary readers: `run-planning`, `planning-loop`, planning reviewers, planning validation tooling
- Primary purpose: define non-authoritative projections that shrink hot-path reads without changing planning freshness or supersede law

<!-- forgeloop:anchor authority-line -->
## Authority Line

- Planning rolling docs remain the only authority for `round`, `handoff_id`, `review_target_ref`, freshness, and same-round supersede semantics.
- Every derived view is disposable and rebuildable.
- A derived view never outranks or overwrites its source rolling doc.
- If any disagreement appears, invalidate the derived view and reread the formal rolling doc.

<!-- forgeloop:anchor view-types -->
## View Types

- `current-effective`
  - one synthesized view of the current handoff plus only the latest matching actionable result for that handoff
  - it must not surface superseded same-handoff results as current
- `round-scoped`
  - one projection per `round` containing every formal planning block for that round in append order
  - it is a complete round replay helper and may be used when a consumer wants the whole planning attempt in one read
- `attempt-aware`
  - one projection per `round` containing the ordered formal blocks for that planning attempt
  - it is the default hot-path helper for same-stage planning repair recovery
- `handoff-scoped`
  - one projection per `handoff_id` containing the handoff block plus every matching review-result block for the same tuple in append order
  - it is the default hot-path helper for fresh planning reviewer entry when the authoritative rolling doc ref is still bound explicitly in the packet

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
- the source rolling doc now exposes multiple actionable results for what was previously one unique current handoff
- the underlying handoff no longer matches the latest current handoff
- the source packet can no longer prove selector legality for the formal inputs the view depends on
- the source rolling doc no longer exposes one unique actionable result
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
