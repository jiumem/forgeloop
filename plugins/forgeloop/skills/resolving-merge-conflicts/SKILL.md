---
name: resolving-merge-conflicts
description: Load when a Git merge or rebase has conflicts and both sides' intended behavior must be recovered before resolution.
---

# Resolve Merge Conflicts

1. Inspect the current merge/rebase state, history, and conflicted files.
2. Read both sides' Commits, Specs, Tickets, ADRs, PRs/MRs, and review records to recover the original intent of each change.
3. Resolve conflicts only when both sides' intentions are compatible; preserve both intentions and do not invent new behavior.
4. If product behavior, Schema, architectural decisions, or contracts are incompatible, stop and return a structural `CONTRACT_BLOCKER` that lists the conflicting decisions, evidence, and required ruling. Do not choose a side independently.
5. Do not automatically perform destructive resets, discard commits, run `merge --abort` or `rebase --abort`, or take any other abandonment action.
6. Run the project's existing targeted checks. When conflict resolution changes candidate code, explicitly invalidate the old Verdicts and require Coder verification plus fresh review by both the Spec and Standards Reviewers.
7. Stage changes and continue only when the user's original authorization includes completing the merge/rebase; otherwise report the resolved files, verification results, and remaining manual steps.
