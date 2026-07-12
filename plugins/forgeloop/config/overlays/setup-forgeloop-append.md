## Extended Forgeloop Configuration

After Section A, ask only one additional question at a time: the repository Integration Policy. Recommend following the repository's existing protection policy; ask the user to choose `auto-merge` or `human-merge`, and write the result to `docs/agents/issue-tracker.md`. When the policy is missing, `$run-initiative` must not integrate automatically. Stop explicitly when authentication, permission, or platform-capability checks fail; do not fall back to another Tracker.

On rerun, update only the existing `## Agent skills` block and `docs/agents/*.md` configuration; do not append duplicates. Before writing, verify that the selected CLI is available and that the identity and repository are readable. Write only after the user confirms the draft, avoiding partial configuration caused by permission failures.

If `docs/initiatives/**` is found, only report the legacy historical entry point and link to migration instructions. Do not read its contents as new runtime state, and do not move, delete, or automatically convert it. Completed, archived, Handoff, and Recommendations content remains read-only. For an active Initiative, the user must choose either to finish it pinned to `2.5.0` or to regenerate formal Specs/Tickets after a preview.

When generating `docs/agents/issue-tracker.md`, preserve both the selected template's `Tracker Runtime Operations` and its Integration Policy.
