# Testing Forgeloop In Codex

Run all checks from the repository root.

For `0.9.0`, the release gate is the Codex workflow checks below. There is no Python package build, lint, or typecheck gate for this version.

## 1. P0 validation closure

```bash
bash tests/codex/p0-validation.sh
```

This is the single recommended validation entry point for the anchor-sliced dispatch P0 closure.

It runs, in order:

- `tests/codex/anchor-slice-smoke.sh`
- `tests/codex/token-benchmark/run.sh`
- `tests/codex/token-benchmark/run.sh --compare-baseline tests/codex/token-benchmark/baseline.json`

`tests/codex/anchor-slice-smoke.sh` and `tests/codex/token-benchmark/run.sh` both print the current runtime cutover mode from `plugins/forgeloop/skills/run-initiative/references/runtime-cutover.md`.
The runtime benchmark gate still enforces `total >= 45%` and `task hot path >= 50%` while the runtime cutover mode remains minimal-first.
Planning scenarios are reported separately and do not currently gate.

## 2. Plugin package smoke test

```bash
bash tests/codex/plugin-smoke.sh
```

This verifies the plugin manifest, repo marketplace manifest, packaged skill and agent mirrors, and the plugin-side `materialize-agents.sh` flow against both a temporary global Codex home and a temporary target project.

## 3. Codex-only repository check

```bash
bash tests/codex/verify-codex-only.sh
```

This fails if removed platform files come back, if the packaged skill or agent manifests drift from the declared release surface, or if the remaining runtime docs and skills still contain obvious non-Codex terminology.

It also checks that the packaged custom agent manifests under `plugins/forgeloop/agents/` are present and declare the required fields.
It also checks that every shipped workflow dispatch file points at a declared packaged custom agent, so new agent roles cannot be added half-way.
It also runs the planning-side regressions:

- `tests/codex/planning-runner-regression.sh` keeps `run-planning` on same-activation loop-back semantics instead of regressing to stage-by-stage stop behavior
- `tests/codex/planning-packet-lint.sh` keeps planning worker packets stage-local and prevents ordinary planner/reviewer packets from depending on `run-planning/SKILL.md` or `planning-loop/SKILL.md`
- `tests/codex/control-plane-root-lint.sh` keeps the Initiative-local sibling `.forgeloop/` path as the only legal repo-local control-plane root and prevents drift back to legacy path semantics
