# Forgeloop Derived View Contract

<!-- forgeloop:anchor document-role -->
## Document Role

- Plane: shared planning/runtime reference
- Applies to: planning rolling docs and runtime review rolling docs
- Primary readers: `run-planning`, `planning-loop`, `run-initiative`, `rebuild-runtime`, loop skills, reviewers, validation tooling
- Primary purpose: define non-authoritative derived projections that may shrink hot-path reads without changing authority or freshness law

Its anchors, when present, are navigation aids or optional selector targets. This document is not a mandatory machine-addressed payload surface unless a local contract explicitly binds one of its sections.

<!-- forgeloop:anchor authority-line -->
## Authority Line

- Formal rolling docs remain the only authority for current `round`, current handoff identity, review-target identity, runtime `compare_base_ref` linkage when present, freshness, and supersede semantics.
- Every derived view is disposable and rebuildable.
- A derived view never outranks or overwrites its source rolling doc.
- If any disagreement appears, invalidate the derived view and reread the formal rolling doc.

<!-- forgeloop:anchor view-types -->
## View Types

- `current-effective`
  - one synthesized current-frontier view built from the latest legally actionable formal blocks
  - for planning: current handoff plus only the latest matching actionable review result for that handoff
  - for runtime: latest round `review_handoff`, the same round's `review_result` when present, and the addressed prior `review_result` when `addresses_review_result_id` is present
- `round-scoped`
  - one projection per `round` containing that round's formal blocks in append order
  - it is the default helper when one complete round must be read without unrelated history
- `attempt-aware`
  - planning-only
  - one projection per planning `round` that isolates same-stage repair history within that round
- `handoff-scoped`
  - planning-only
  - one projection per `handoff_id` containing only the formal blocks relevant to that handoff
  - it is the default helper for fresh reviewer entry when the authoritative rolling-doc ref is still bound in the packet

<!-- forgeloop:anchor materialization -->
## Materialization

- Recommended location: `<initiative_dir>/.forgeloop/derived/<plane>/<object>/...`
- For repo-local Initiatives, derived views must live under the same Initiative-local `.forgeloop/` root as the authoritative rolling doc they derive from.
- Do not place repo-local Initiative derived views under repo-root `.forgeloop/<initiative_key>/...`.
- Materialized files must state clearly that they are non-authoritative derived views.
- Materialization may be skipped entirely; consumers can always fall back to direct anchored reads from the formal document.
- A derived view should be cheap to delete and cheap to rebuild.

<!-- forgeloop:anchor invalidation -->
## Invalidation Rules

Invalidate the relevant derived view immediately when:

- a newer formal block is appended to the source rolling doc
- the source rolling doc now exposes an illegal duplicate current-round handoff or result
- the latest current frontier no longer matches what the view materialized
- the source packet can no longer prove selector legality for the formal inputs the view depends on
- a referenced prior result no longer resolves uniquely
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
