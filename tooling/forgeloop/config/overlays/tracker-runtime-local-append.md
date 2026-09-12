## Integration Policy

`Integration policy: <auto-merge|human-merge>`. Automatic integration is prohibited when it is missing. Local still represents Candidate implementations through Git Branches and Commits; do not treat Markdown state as proof that code has been integrated.

## Delivery Runtime Operations

- **Delivery unit**: Read the selected large Ticket, Spec, or bounded Initiative file and its relationships, state, and target before writing.
- **Branches and commits**: Use one branch per large Ticket or Spec. A Spec's Tickets are Slices on that branch; they do not receive their own branches. Keep unrelated work out of each logical Slice Commit.
- **Review evidence**: Append the frozen Base/Head and both complete one-time Reviewer reports under the selected large Ticket or current Spec's existing Agent Run section. Append every Finding disposition, repair Commit, validation reference, and resulting Head in a second record before the final Gate. These records are recovery evidence, not Events or Verdicts.
- **Integration**: Let the Delivery Worker own the final Gate and integration of the current delivery branch. Under `auto-merge`, integrate only after the final Gate passes and Git facts are current. Under `human-merge`, preserve the ready branch and wait for user action.
- **Closure**: Resolve a large Ticket only after its branch is integrated. For a Spec, verify every Ticket's logical Commit or `NO_CHANGE_REQUIRED` evidence and acceptance outcome after integration, then resolve its Tickets and the Spec. For a bounded Initiative, finish member Specs in dependency order and resolve the Initiative only after every member Spec is delivered.
- **Recovery**: Recover from the selected Markdown item, its Review and disposition records, branch, Commits, and current Git facts. A dirty worktree, file conflict, target drift, or inconsistent Git state leaves the delivery unit Open and returns a recoverable diagnostic.
