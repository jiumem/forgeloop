## Integration Policy

`Integration policy: <auto-merge|human-merge>`. Automatic integration is prohibited when it is missing. Protected Branch, pipeline requirements, and permissions take precedence; do not fall back to Local when authentication or permission checks fail.

## Delivery Runtime Operations

- **Delivery unit**: Read the selected large Ticket, Spec, or bounded Initiative and its current Notes, relationships, state, and target before writing. Do not infer delivery state from labels alone.
- **Branches and commits**: Use one branch per large Ticket or Spec. A Spec's Tickets are Slices on that branch; they do not receive their own branches or MRs. Keep unrelated work out of each logical Slice Commit.
- **Review evidence**: Append the frozen Base/Head and both complete one-time Reviewer reports as a plain Issue Note on the large Ticket or current Spec. Append every Finding disposition, repair Commit, validation reference, and resulting Head in a second plain Note before the final Gate. These Notes are recovery evidence, not Events or Verdicts.
- **Integration**: Let the Delivery Worker own push, the single MR, pipelines, and merge for the current delivery branch. Execute `auto-merge` only when the final Gate, current pipeline requirements, Protected Branch policy, and permissions are satisfied. Under `human-merge`, preserve the ready MR and wait for user action.
- **Closure**: Close a large Ticket only after its MR is merged. For a Spec, verify every Ticket's logical Commit or `NO_CHANGE_REQUIRED` evidence and acceptance outcome after the Spec MR is merged, then close its Tickets and the Spec. For a bounded Initiative, finish member Specs in dependency order and close the Initiative only after every member Spec is delivered.
- **Recovery**: Recover from the selected Issue, Review and disposition Notes, branch, Commits, MR, and current pipelines. Authentication, permission, protection, target, or external-pipeline failure leaves the delivery unit Open and returns a recoverable diagnostic.
