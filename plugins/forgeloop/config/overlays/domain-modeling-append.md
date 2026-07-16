## Forgeloop Approved ADR Revision Mode

Enter this mode only when `$run-initiative` supplies one exactly read-back native approval record and a reconciliation package containing complete target ADR content. The package is the authorization boundary: do not ask the user again, broaden the decision, or substitute a different architectural choice.

Read the current ADRs and Git facts, apply only the approved content, and publish it through the repository's existing Commit and PR/MR policy. The ADR Revision becomes effective only when the exact approved content is present on the package's target branch at an immutable Commit and that target-branch content has been read back. A PR/MR Head, review approval, mergeability, or source-branch Commit is not an effective ADR Revision.

Return the immutable target-branch Commit, affected ADR paths, and exact content read-back. If the approved content is already present on the target branch, reuse that equivalent Git fact. Under `human-merge`, preserve the PR/MR and keep the Run paused until its merge is observed and the target branch is verified; do not request another contract approval. If current content conflicts with the package or publishing would require an unapproved decision, write nothing further and return `RECOVERY_CONFLICT`.

This mode owns ADR content and its Git Revision only. It does not edit the Spec or Tickets, resume the Run, or create a second contract store.
