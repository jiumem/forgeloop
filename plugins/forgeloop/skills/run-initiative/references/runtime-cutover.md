# Forgeloop Runtime Cutover Contract

<!-- forgeloop:anchor document-role -->
## Document Role

- Plane: runtime-only migration and rollback reference
- Applies to: `run-initiative`, `rebuild-runtime`, `task-loop`, `milestone-loop`, `initiative-loop`, runtime reviewer packets, and runtime validation
- Primary readers: runtime `Supervisor`, runtime coders/reviewers, and repository self-checks
- Primary purpose: define one repository-owned source of truth for the default runtime read path, legal fallback surface, and rollback behavior

<!-- forgeloop:anchor scope -->
## Scope

runtime_cutover_scope: runtime_only
planning_cutover_scope: out_of_scope

- This contract changes only runtime default routing.
- Planning remains report-only for cutover purposes in the current phase.
- Anchors, derived views, benchmark tooling, and validation fixtures may still exist outside runtime cutover scope; this contract only decides what runtime treats as the default path.

<!-- forgeloop:anchor supported-modes -->
## Supported Modes

supported_runtime_cutover_modes: full_doc_default,minimal_preferred,minimal_required

- `full_doc_default`
  - old full-document path is the runtime default
  - anchor selectors, derived views, benchmark, and validation stay available for verification and reporting
  - this is the rollback mode
- `minimal_preferred`
  - anchor-addressed minimal packets are the runtime default
  - selector legality failure, derived-view invalidation, cold start, rebuild, and other explicit recovery triggers may promote one read or packet to explicit full-document fallback
  - this is the current target operating mode
- `minimal_required`
  - anchor-addressed minimal packets are required by default
  - full-document fallback is no longer an ordinary recovery path and is reserved only for explicitly documented disaster-recovery exceptions
  - this mode is defined now for forward compatibility, but is not the current operating target

<!-- forgeloop:anchor current-mode -->
## Current Mode

current_runtime_cutover_mode: minimal_preferred

- Runtime routing should currently default to anchor-addressed minimal packets.
- Explicit full-document fallback remains legal only for the contract-defined recovery cases.
- Planning does not inherit this default.

<!-- forgeloop:anchor default-read-law -->
## Default Read Law

- Every runtime entrypoint must bind this contract before deciding whether the default read path is minimal or full-document.
- In `full_doc_default`, runtime may start from authoritative full-document reads and may still run minimal-path validation or reporting as a sidecar, but minimal is not the default dispatch path.
- In `minimal_preferred`, runtime must start from the minimum control plane plus legal derived views and authoritative rolling-doc slices before escalating.
- In `minimal_required`, runtime must stay on the minimal path unless one explicit disaster-recovery exception in this contract says otherwise.

<!-- forgeloop:anchor fallback-law -->
## Fallback Law

- `full_doc_default`
  - full-document reads are already the default, so fallback is not a special event
  - minimal-path probes may still stop or report legality failure when validation is being exercised explicitly
- `minimal_preferred`
  - full-document fallback is legal only when cold start, runtime rebuild, selector legality failure, anchor conflict, derived-view invalidation, or unresolved formal conflict makes the thinner path insufficient
  - every fallback must be explicit about `mode` and `reason`
- `minimal_required`
  - ordinary legality failure is not enough to silently fall back to full documents
  - the caller must either use one explicitly documented disaster-recovery exception or stop

<!-- forgeloop:anchor rollback-law -->
## Rollback Law

- Rolling back means changing only `current_runtime_cutover_mode`, not deleting anchors, derived views, benchmark fixtures, or validation tooling.
- `full_doc_default` is the one-step rollback target.
- Rollback changes the runtime default read path immediately, but it does not invalidate the benchmark, packet dump tooling, or contract-level tests.
- After rollback, minimal-path validation remains available and should continue to report drift even while runtime defaults to full documents.

<!-- forgeloop:anchor retained-capabilities -->
## Retained Capabilities

- Always retained:
  - text anchors and selector legality checks
  - rolling-doc derived views
  - packet materialization and benchmark reporting
  - baseline comparison and smoke tests
- Disabled only as default behavior in `full_doc_default`:
  - anchor-addressed minimal packet assembly as the runtime default path
  - minimal-path-first recovery order
- Deferred until a future cutover in planning:
  - planning default-path changes
  - planning gating changes driven by this mode

<!-- forgeloop:anchor validation-hook -->
## Validation Hook

- Runtime validation must print `current_runtime_cutover_mode`.
- Smoke tests must prove the runtime entrypoints bind this contract and follow its current-mode law.
- Benchmark reports must surface the current runtime cutover mode and treat runtime gating according to that mode.
