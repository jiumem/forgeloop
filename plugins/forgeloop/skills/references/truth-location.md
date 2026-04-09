# Forgeloop Truth Location Contract

## Document Role

- Plane: shared runtime reference
- Applies to: `Supervisor`, runtime `coder`, runtime reviewers, and any worker packet that must recover current-object truth without creating a second source
- Primary purpose: define the legal order for locating current-object truth before coding, review, routing, or recovery

This document defines read-order law. It is not itself a required selector-addressed packet payload unless a stricter local contract explicitly binds one of its sections.

## Truth Location Precedence

When current-object context must be located, first obey any bound runtime cutover contract.

- If that contract makes minimal reads the default, use this order and stop at the first sufficient layer:
  1. authoritative bound refs plus `doc_ref + anchor_selector`
  2. `rg` keyword discovery only when the needed selector or exact local section has not yet been bound clearly
  3. sealed full-document reading only when the current packet or bound contract still cannot prove the needed truth through legal slices
- If the bound runtime cutover contract is `full_doc_default`, authoritative full-document reads may be the supervisor default, but worker packets should still prefer the smallest lawful object-local slices.

Do not widen the read surface beyond what the bound contract or the current proof gap requires.

## Authoritative Slices First

- Default first read is the authoritative packet basis already bound for the current object.
- Prefer exact object-local slices such as Task definition, acceptance index, evidence entrypoints, Milestone acceptance, Initiative success criteria, current `review_handoff`, and current `review_result`.
- If the current packet already proves the necessary truth with lawful slices, do not widen the read surface.
- A disposable derived view may help on the hot path, but it never outranks the authoritative rolling doc or the authoritative `doc_ref + anchor_selector` basis.

## `rg` Discovery Law

- Use `rg` only as a discovery tool to find candidate anchors, section names, or object-local locations when the packet does not already bind them clearly.
- `rg` results are not a new truth source.
- After `rg` finds the likely location, bind or reread the authoritative source before acting on it.
- Do not treat a keyword hit, filename hit, or chat memory as sufficient proof of current-object truth.

## Full-Document Fallback

- Read the sealed planning full documents only when lawful slices and bounded discovery are still insufficient.
- Escalate only as far as needed:
  - first the current object's local authority surface
  - then the smallest sufficient surrounding section
  - only then broader sealed planning docs such as `Design Doc`, `Gap Analysis Doc`, or `Total Task Doc`
- Do not default to rereading the entire planning truth trio on every runtime round.
- Full-document reading is legal fallback and context recovery, not the default hot path.

## Truth Boundaries

- Formal truth remains in the sealed planning docs, the `Global State Doc`, and the review rolling docs.
- Chat summaries, inferred memory, `rg` output, and disposable views may help locate truth, but they do not become truth themselves.
- If the current packet cannot prove enough after lawful fallback, stop and surface the missing or contradictory truth instead of guessing.
