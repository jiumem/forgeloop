# Issue tracker: GitLab

Issues and specs for this repo live as GitLab issues. Use the [`glab`](https://gitlab.com/gitlab-org/cli) CLI for all operations.

## Conventions

- **Create an issue**: `glab issue create --title "..." --description "..."`. Use a heredoc for multi-line descriptions. Pass `--description -` to open an editor.
- **Read an issue**: `glab issue view <number> --comments`. Use `-F json` for machine-readable output.
- **List issues**: `glab issue list -F json` with appropriate `--label` filters.
- **Comment on an issue**: `glab issue note <number> --message "..."`. GitLab calls comments "notes".
- **Apply / remove labels**: `glab issue update <number> --label "..."` / `--unlabel "..."`. Multiple labels can be comma-separated or by repeating the flag.
- **Close**: `glab issue close <number>`. `glab issue close` does not accept a closing comment, so post the explanation first with `glab issue note <number> --message "..."`, then close.
- **Merge requests**: GitLab calls PRs "merge requests". Use `glab mr create`, `glab mr view`, `glab mr note`, etc. — the same shape as `gh pr ...` with `mr` in place of `pr` and `note`/`--message` in place of `comment`/`--body`.

Infer the repo from `git remote -v` — `glab` does this automatically when run inside a clone.

## Merge requests as a triage surface

**MRs as a request surface: no.** _(Set to `yes` if this repo treats external merge requests as feature requests; `/triage` reads this flag.)_

When set to `yes`, MRs run through the same labels and states as issues, using the `glab mr` equivalents:

- **Read an MR**: `glab mr view <number> --comments` and `glab mr diff <number>` for the diff.
- **List external MRs for triage**: `glab mr list -F json`, then keep only MRs whose author is not a project member/owner (a contributor's MR, not a maintainer's in-flight work).
- **Comment / label / close**: `glab mr note`, `glab mr update --label`/`--unlabel`, `glab mr close`.

Unlike GitHub, GitLab numbers issues and MRs separately, so `#42` is unambiguous once you know which surface the maintainer means.

## When a skill says "publish to the issue tracker"

Create a GitLab issue.

## When a skill says "fetch the relevant ticket"

Run `glab issue view <number> --comments`.

## Wayfinding operations

Used by `/wayfinder`. The **map** is a single issue with **child** issues as tickets.

- **Map**: a single issue labelled `wayfinder:map`, holding the Notes / Decisions-so-far / Fog body. `glab issue create --label wayfinder:map`. (On GitLab tiers with native epics, an epic may hold the map instead; a labelled issue works everywhere.)
- **Child ticket**: an issue carrying `Part of #<map>` at the top of its description and labels `wayfinder:<type>` (`research`/`prototype`/`grilling`/`task`). Once claimed, the ticket is assigned to the driving dev.
- **Blocking**: GitLab's **native blocking link** — the canonical, UI-visible representation. Add it with the `/blocked_by #<n>` quick action, posted as a note (`glab issue note <child> --message "/blocked_by #<blocker>"`). Native blocking links are a Premium/Ultimate feature; on the free tier (or where unavailable) fall back to a `Blocked by: #<n>, #<n>` line at the top of the description. A ticket is unblocked when every blocker is closed.
- **Frontier query**: `glab issue list -F json` scoped to the map's children, drop any with an open blocker — a native `blocked_by` link to an open issue (`glab api projects/:id/issues/:iid/links`), or an open issue in the `Blocked by` line — or an assignee; first in map order wins.
- **Claim**: `glab issue update <n> --assignee @me` — the session's first write.
- **Resolve**: `glab issue note <n> --message "<answer>"`, then `glab issue close <n>`, then append a context pointer (gist + link) to the map's Decisions-so-far.

## Integration Policy

`Integration policy: <auto-merge|human-merge>`. Automatic integration is prohibited when it is missing. Protected Branch, pipeline requirements, and permissions take precedence; do not fall back to Local when authentication or permission checks fail.

## Delivery Runtime Operations

- **Delivery unit**: Read the selected large Ticket, Spec, or bounded Initiative and its current Notes, relationships, state, and target before writing. Do not infer delivery state from labels alone.
- **Branches and commits**: Use one branch per large Ticket or Spec. A Spec's Tickets are Slices on that branch; they do not receive their own branches or MRs. Keep unrelated work out of each logical Slice Commit.
- **Review evidence**: Append the frozen Base/Head and both complete one-time Reviewer reports as a plain Issue Note on the large Ticket or current Spec. Append every Finding disposition, repair Commit, validation reference, and resulting Head in a second plain Note before the final Gate. These Notes are recovery evidence, not Events or Verdicts.
- **Integration**: Let the Delivery Worker own push, the single MR, pipelines, and merge for the current delivery branch. Execute `auto-merge` only when the final Gate, current pipeline requirements, Protected Branch policy, and permissions are satisfied. Under `human-merge`, preserve the ready MR and wait for user action.
- **Closure**: Close a large Ticket only after its MR is merged. For a Spec, verify every Ticket's logical Commit or `NO_CHANGE_REQUIRED` evidence and acceptance outcome after the Spec MR is merged, then close its Tickets and the Spec. For a bounded Initiative, finish member Specs in dependency order and close the Initiative only after every member Spec is delivered.
- **Recovery**: Recover from the selected Issue, Review and disposition Notes, branch, Commits, MR, and current pipelines. Authentication, permission, protection, target, or external-pipeline failure leaves the delivery unit Open and returns a recoverable diagnostic.
