# Testing Forgeloop In Codex

Run all checks from the repository root.

## 1. Install script smoke test

```bash
bash tests/codex/install-script-smoke.sh
```

This verifies local-source installation, `--doctor`, and the generated Codex skills symlink against temporary directories.

## 2. Codex-only repository check

```bash
bash tests/codex/verify-codex-only.sh
```

This fails if removed platform files come back or if the remaining runtime docs and skills still contain obvious non-Codex terminology.

It also checks that the project-scoped custom agents under `.codex/agents/` are present and declare the required fields.

## 3. Brainstorm server integration test

```bash
cd tests/brainstorm-server
pnpm install
node server.test.js
```

This verifies the browser companion server still serves pages, injects helper code, records user events, and broadcasts reloads.
