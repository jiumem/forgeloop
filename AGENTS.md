# Forgeloop Repository Rules

## Worktrees

- Default worktree root: `~/.codex/worktrees/<project-name>/`
- When creating a new worktree without a user override, use the global Codex worktree root above
- If the user explicitly requests another location, follow the user
- Valid user overrides include:
  - project-local `.worktrees/`
  - project-local `worktrees/`
  - a custom absolute or `~/`-prefixed root directory

When a custom root directory is provided, create the worktree at:

```text
<custom-root>/<project-name>/<branch-name>
```

Project-local worktree directories must still be ignored by Git before use.
