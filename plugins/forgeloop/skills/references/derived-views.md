# Forgeloop Derived View Contract

<!-- forgeloop:anchor document-role -->
## Document Role

- Plane: shared planning/runtime reference
- Applies to: planning rolling docs and runtime review rolling docs
- Primary readers: `run-initiative`, `rebuild-runtime`, runtime loop skills, reviewers, validation tooling
- Primary purpose: define non-authoritative current-effective, handoff-scoped, and attempt-aware projections that may shrink hot-path reads without changing freshness law

<!-- forgeloop:anchor authority-line -->
## Authority Line

- Formal rolling docs remain the only authority for `round`, `handoff_id`, `review_target_ref`, freshness, and supersede semantics.
- Every derived view is disposable and rebuildable.
- A derived view never outranks or overwrites its source rolling doc.
- If any disagreement appears, invalidate the derived view and reread the formal rolling doc.

<!-- forgeloop:anchor view-types -->
## View Types

- `current-effective`
  - one synthesized view of the current handoff plus only the latest matching actionable result for that handoff
  - it must not surface superseded same-handoff results as current
- `handoff-scoped`
  - one projection per `handoff_id` containing the handoff block plus every matching review-result block for the same tuple in append order
  - it is historical and audit-friendly by design; it is not a latest-only view
  - it is the default hot-path helper for fresh reviewer entry when the authoritative rolling doc ref is still bound in the packet
- `attempt-aware`
  - one projection per `round` containing the ordered formal blocks for that attempt
  - it isolates same-object history within one round without changing durable `round` law

These views may exist for planning rolling docs and runtime review rolling docs. The projection rules change by doc kind, but the authority line does not.

<!-- forgeloop:anchor materialization -->
## Materialization

- Recommended location: `.forgeloop/<initiative_key>/derived/<plane>/<object>/...`
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
