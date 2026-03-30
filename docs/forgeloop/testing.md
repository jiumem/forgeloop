# Testing Forgeloop In Codex

Run all checks from the repository root.

For `0.3.0`, the release gate is the Codex workflow checks below. There is no Python package build, lint, or typecheck gate for this version.

## 1. Plugin package smoke test

```bash
bash tests/codex/plugin-smoke.sh
```

This verifies the plugin manifest, repo marketplace manifest, packaged skill and agent mirrors, and the plugin-side `materialize-agents.sh` flow against both a temporary global Codex home and a temporary target project.

## 2. Codex-only repository check

```bash
bash tests/codex/verify-codex-only.sh
```

This fails if removed platform files come back, if the packaged skill or agent manifests drift from the declared release surface, or if the remaining runtime docs and skills still contain obvious non-Codex terminology.

It also checks that the packaged custom agent manifests under `plugins/forgeloop/agents/` are present and declare the required fields.
It also checks that every shipped workflow dispatch file points at a declared packaged custom agent, so new agent roles cannot be added half-way.
