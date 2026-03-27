## Forgeloop Agent Manifests

This directory is the source-of-truth manifest layer for the Forgeloop suite's custom agents.

- `skills/` dispatch these agents by name
- `scripts/install.sh --project-dir <path>` copies these manifests into `<path>/.codex/agents/`
- the source repository itself intentionally does not keep a repo-local `.codex/`
