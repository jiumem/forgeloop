# Forgeloop Anchor Addressing Contract

<!-- forgeloop:anchor document-role -->
## Document Role

- Plane: shared planning/runtime reference
- Applies to: planning artifacts, planning rolling docs, runtime control docs, runtime review rolling docs, and review baselines consumed through minimal packets
- Primary readers: `run-planning`, `planning-loop`, `run-initiative`, `rebuild-runtime`, runtime loop skills, packaged agents, and validation tooling
- Primary purpose: define the legal `doc_ref + anchor_selector` addressing surface, namespace law, resolution outcomes, and minimal-packet fallback boundary

<!-- forgeloop:anchor anchor-syntax -->
## Anchor Syntax

- A stable text anchor is one standalone Markdown comment line:

```text
<!-- forgeloop:anchor <selector> -->
```
- `<selector>` is doc-local and machine-readable.
- Allowed characters are `[a-z0-9._/-]`.
- The anchor comment must appear immediately before the section or block it addresses.
- The addressed slice begins on the next line after the anchor comment and ends at the line before the next anchor comment in the same document, or at end of file.

<!-- forgeloop:anchor namespace-law -->
## Namespace Law

- Text anchors are doc-address selectors only. They are not the same legal object as Task `anchor_ref` or `fixup_ref`.
- Text-anchor namespace is always bound by `doc_ref`.
- A selector must be unique within one document.
- Consumers must persist durable truth as repo-root-relative `doc_ref` plus a doc-local selector. They must not persist absolute paths, line numbers, or parser-specific offsets as durable truth.
- If a surface already uses the word `anchor` for Task handoff semantics, text-anchor references must be labeled explicitly as `text_anchor_selector` or `anchor_selector` in packets to avoid ambiguity.

<!-- forgeloop:anchor coverage-matrix -->
## Required Coverage Matrix

The following surfaces must expose stable text anchors for hot-path consumption:

- sealed planning artifacts: `Design Doc`, `Gap Analysis Doc`, `Total Task Doc`
- planning rolling-doc contract reference
- runtime control-plane contract references: `Global State Doc`, Task/Milestone/Initiative review rolling-doc contracts
- workflow skill sections that define packet shape, fallback law, admission law, or object routing
- Markdown reference mirrors and human-readable contract docs that describe consumer-facing packet expectations

Executable manifests are still part of the formal contract surface, but under the current Markdown-comment anchor syntax they are validated indirectly through the tracked skill docs and reference mirrors that bind their packet semantics. They are not themselves required to embed Markdown text anchors.

Consumers may expose more anchors than this minimum, but they must not rely on hidden or implicit sections outside this coverage set.

<!-- forgeloop:anchor minimal-packet -->
## Minimal Packet Contract

The default packet for planning/runtime dispatch must carry only:

- authoritative repo-root-relative refs
- doc-local anchor selectors for the exact formal surfaces the consumer must read
- inline slices only when the dispatcher has already materialized them from the same authoritative refs
- explicit fallback mode and fallback reason when the dispatcher had to promote the read to a full document
- optional derived-view refs only when they are clearly marked non-authoritative and disposable
- for worker packets, stage or object contract refs instead of supervisor or dispatcher skill docs as authoritative payload

A packet must remain self-sufficient for the current operation. Do not rely on previous-packet state, delta-only continuation, or hidden thread memory as a legality basis.

A packet is illegal if it provides sliced text without the authoritative `doc_ref + anchor_selector` pair that produced it.

Supervisor or dispatcher skill docs are not worker authoritative packet payload. Do not include `run-planning/SKILL.md`, `planning-loop/SKILL.md`, `run-initiative/SKILL.md`, or `code-loop/SKILL.md` in ordinary worker packets; if a validation or exceptional fallback intentionally includes one, mark it as explicit fallback material and state the reason.

<!-- forgeloop:anchor resolution-contract -->
## Resolution Contract

Given one `doc_ref + anchor_selector`, resolution may end in exactly one of these states:

- `resolved_unique_target`
- `missing_anchor`
- `duplicate_anchor`
- `illegal_selector`
- `drift_requires_full_document`

`resolved_unique_target` returns one exact slice.

All other states are failures. The consumer must either:

- promote the read to a full-document fallback, or
- stop on a formal blocker when full-document fallback is not legal for that call site

No consumer may guess past a failed resolution.

<!-- forgeloop:anchor failure-taxonomy -->
## Failure Taxonomy

- `missing_anchor`: the selector does not exist in the addressed document
- `duplicate_anchor`: the selector appears more than once in the same document
- `illegal_selector`: the selector breaks syntax or namespace law
- `drift_requires_full_document`: the selector exists but the caller cannot prove the addressed slice is still a legal minimal read for this operation
- `fallback_not_allowed`: the caller reached a failure state at a surface that legally requires explicit stop instead of full-document promotion

Every failure must become either full-document fallback or explicit stop. Silent downgrade and silent guessing are illegal.

<!-- forgeloop:anchor legality-law -->
## Legality Law

- hot-path consumers must default to anchor-addressed minimal reads
- runtime consumers that bind a cutover contract may use full-document recovery for cold start, runtime rebuild, anchor conflict, and anchor legality failure only when that bound cutover contract allows the fallback for the current call site
- planning consumers, which do not bind a runtime cutover contract, may use full-document recovery for stage recovery, anchor conflict, and anchor legality failure unless a stricter plane-local contract requires explicit stop instead
- when a bound plane-local contract requires explicit disaster-recovery fallback or explicit stop, that stricter contract wins
- full-document fallback is a recovery path, not a convenience default
- derived views may assist resolution, but if they disagree with the formal document, the formal document wins immediately

<!-- forgeloop:anchor validation-hooks -->
## Validation Hooks

- `python3 plugins/forgeloop/scripts/anchor_slices.py check ...` validates anchor syntax, duplicate detection, and empty-slice detection
- `python3 plugins/forgeloop/scripts/anchor_slices.py slice --doc <path> --anchor <selector>` materializes one addressed slice
- `python3 plugins/forgeloop/scripts/anchor_slices.py derive --doc <rolling-doc> --out <dir>` rebuilds disposable rolling-doc views from formal rolling docs
- release validation must also verify that required formal surfaces expose the mandated selector set

These commands are tooling conveniences, not new truth sources.
