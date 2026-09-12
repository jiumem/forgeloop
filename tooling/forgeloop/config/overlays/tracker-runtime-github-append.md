## Integration Policy

`Integration policy: <auto-merge|human-merge>`. Automatic integration is prohibited when it is missing. Branch protection, Required Checks, and permissions take precedence; do not fall back to Local when authentication or permission checks fail.

## Delivery Runtime Operations

- **Delivery unit**: Read the selected large Ticket, Spec, or bounded Initiative and its current comments, relationships, state, and target before writing. Do not infer delivery state from labels alone.
- **Branches and commits**: Use one branch per large Ticket or Spec. A Spec's Tickets are Slices on that branch; they do not receive their own branches or PRs. Keep unrelated work out of each logical Slice Commit.
- **Review evidence**: Append the frozen Base/Head and both complete one-time Reviewer reports as a plain Issue Comment on the large Ticket or current Spec. Append every Finding disposition, repair Commit, validation reference, and resulting Head in a second plain Comment before the final Gate. These Comments are recovery evidence, not Events or Verdicts.
- **Integration**: Let the Delivery Worker own push, the single PR, checks, and merge for the current delivery branch. Execute `auto-merge` only when the final Gate, current PR checks, branch protection, and permissions satisfy repository policy. Under `human-merge`, preserve the ready PR and wait for user action.
- **Closure**: Close a large Ticket only after its PR is merged. For a Spec, verify every Ticket's logical Commit or `NO_CHANGE_REQUIRED` evidence and acceptance outcome after the Spec PR is merged, then close its Tickets and the Spec. For a bounded Initiative, finish member Specs in dependency order and close the Initiative only after every member Spec is delivered.
- **Recovery**: Recover from the selected Issue, Review and disposition Comments, branch, Commits, PR, and current checks. Authentication, permission, protection, target, or external-check failure leaves the delivery unit Open and returns a recoverable diagnostic.
