# Issue tracker: GitHub

Issues and PRDs for this repo live as GitHub issues. Use the `gh` CLI for all operations.

## Conventions

- **Create an issue**: `gh issue create --title "..." --body "..."`. Use a heredoc for multi-line bodies.
- **Read an issue**: `gh issue view <number> --comments`, filtering comments by `jq` and also fetching labels.
- **List issues**: `gh issue list --state open --json number,title,body,labels,comments --jq '[.[] | {number, title, body, labels: [.labels[].name], comments: [.comments[].body]}]'` with appropriate `--label` and `--state` filters.
- **Comment on an issue**: `gh issue comment <number> --body "..."`
- **Apply / remove labels**: `gh issue edit <number> --add-label "..."` / `--remove-label "..."`
- **Close**: `gh issue close <number> --comment "..."`

Infer the repo from `git remote -v` — `gh` does this automatically when run inside a clone.

## Pull requests as a triage surface

**PRs as a request surface: no.** _(Set to `yes` if this repo treats external PRs as feature requests; `/triage` reads this flag.)_

When set to `yes`, PRs run through the same labels and states as issues, using the `gh pr` equivalents:

- **Read a PR**: `gh pr view <number> --comments` and `gh pr diff <number>` for the diff.
- **List external PRs for triage**: `gh pr list --state open --json number,title,body,labels,author,authorAssociation,comments` then keep only `authorAssociation` of `CONTRIBUTOR`, `FIRST_TIME_CONTRIBUTOR`, or `NONE` (drop `OWNER`/`MEMBER`/`COLLABORATOR`).
- **Comment / label / close**: `gh pr comment`, `gh pr edit --add-label`/`--remove-label`, `gh pr close`.

GitHub shares one number space across issues and PRs, so a bare `#42` may be either — resolve with `gh pr view 42` and fall back to `gh issue view 42`.

## When a skill says "publish to the issue tracker"

Create a GitHub issue.

## When a skill says "fetch the relevant ticket"

Run `gh issue view <number> --comments`.

## Wayfinding operations

Used by `/wayfinder`. The **map** is a single issue with **child** issues as tickets.

- **Map**: a single issue labelled `wayfinder:map`, holding the Notes / Decisions-so-far / Fog body. `gh issue create --label wayfinder:map`.
- **Child ticket**: an issue linked to the map as a GitHub sub-issue (`gh api` on the sub-issues endpoint). Where sub-issues aren't enabled, add the child to a task list in the map body and put `Part of #<map>` at the top of the child body. Labels: `wayfinder:<type>` (`research`/`prototype`/`grilling`/`task`). Once claimed, the ticket is assigned to the driving dev.
- **Blocking**: GitHub's **native issue dependencies** — the canonical, UI-visible representation. Add an edge with `gh api --method POST repos/<owner>/<repo>/issues/<child>/dependencies/blocked_by -F issue_id=<blocker-db-id>`, where `<blocker-db-id>` is the blocker's numeric **database id** (`gh api repos/<owner>/<repo>/issues/<n> --jq .id`, _not_ the `#number` or `node_id`). GitHub reports `issue_dependencies_summary.blocked_by` (open blockers only — the live gate). Where dependencies aren't available, fall back to a `Blocked by: #<n>, #<n>` line at the top of the child body. A ticket is unblocked when every blocker is closed.
- **Frontier query**: list the map's open children (`gh issue list --state open`, scoped to the map's sub-issues / task list), drop any with an open blocker (`issue_dependencies_summary.blocked_by > 0`, or an open issue in the `Blocked by` line) or an assignee; first in map order wins.
- **Claim**: `gh issue edit <n> --add-assignee @me` — the session's first write.
- **Resolve**: `gh issue comment <n> --body "<answer>"`, then `gh issue close <n>`, then append a context pointer (gist + link) to the map's Decisions-so-far.

## Integration Policy

`Integration policy: <auto-merge|human-merge>`. Automatic integration is prohibited when it is missing. Branch protection, Required Checks, and permissions take precedence; do not fall back to Local when authentication or permission checks fail.

## Tracker Runtime Operations

- **Frontier**: Query the Spec's Open child Issues, excluding items that still have an Open blocker, already have a valid Claim, or fall outside the authorized Scope; query again after every advancement.
- **Claim**: Publish `RUN_CLAIMED` on the Spec or Initiative root; the earliest valid server-side root Claim wins. Only the winner may claim one current Ticket through its native assignee state. Do not duplicate the Ticket Claim as an Event.
- **Checkpoints**: Append minimal idempotent checkpoints through Issue Comments. Collect both Ticket Verdicts independently and write one combined `REVIEW_RESULT`; do not modify published records, and append `EVENT_SUPERSEDED` to correct an error.
- **Candidate implementation**: Associate the Ticket Branch, Commit, and PR; a closed but unmerged PR is not complete.
- **Integration**: Let the Scheduler own push, PR handling, checks, and merge. Execute `auto-merge` only when both Verdicts are PASS, Head is unchanged, and Required Checks and permissions are satisfied. Return a candidate-caused Check failure to the original Coder under the shared repair budget; pause on permissions, infrastructure, or unrelated failures. For `human-merge`, write `READY_FOR_HUMAN_MERGE` and wait for a refresh.
- **Closure**: After verifying native merge facts, record `INTEGRATION_RESULT`, close the Ticket, and treat its assignee Claim as inactive. In a multi-Spec Run, keep member Specs Open through Initiative Acceptance; on Initiative PASS, close member Specs first and the parent last. Treat the closed root's historical Claim as inactive and do not delete Claim Comments. Authentication, permission, Branch Protection, or externally blocked Checks must leave Items Open and provide a recoverable diagnostic.
