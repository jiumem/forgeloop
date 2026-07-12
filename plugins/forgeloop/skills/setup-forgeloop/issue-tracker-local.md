# Issue tracker: Local Markdown

Issues and specs (you may know a spec as a PRD) for this repo live as markdown files in `.scratch/`.

## Conventions

- One feature per directory: `.scratch/<feature-slug>/`
- The spec is `.scratch/<feature-slug>/spec.md`
- Implementation issues are one file per ticket at `.scratch/<feature-slug>/issues/<NN>-<slug>.md`, numbered from `01` — never a single combined tickets file
- Triage state is recorded as a `Status:` line near the top of each issue file (see `triage-labels.md` for the role strings)
- Comments and conversation history append to the bottom of the file under a `## Comments` heading

## When a skill says "publish to the issue tracker"

Create a new file under `.scratch/<feature-slug>/` (creating the directory if needed).

## When a skill says "fetch the relevant ticket"

Read the file at the referenced path. The user will normally pass the path or the issue number directly.

## Wayfinding operations

Used by `/wayfinder`. The **map** is a file with one **child** file per ticket.

- **Map**: `.scratch/<effort>/map.md` — the Notes / Decisions-so-far / Fog body.
- **Child ticket**: `.scratch/<effort>/issues/NN-<slug>.md`, numbered from `01`, with the question in the body. A `Type:` line records the ticket type (`research`/`prototype`/`grilling`/`task`); a `Status:` line records `claimed`/`resolved`.
- **Blocking**: a `Blocked by: NN, NN` line near the top. A ticket is unblocked when every file it lists is `resolved`.
- **Frontier**: scan `.scratch/<effort>/issues/` for files that are open, unblocked, and unclaimed; first by number wins.
- **Claim**: set `Status: claimed` and save before any work.
- **Resolve**: append the answer under an `## Answer` heading, set `Status: resolved`, then append a context pointer (gist + link) to the map's Decisions-so-far in `map.md`.

## Integration Policy

`Integration policy: <auto-merge|human-merge>`. Automatic integration is prohibited when it is missing. Local still represents candidate implementations through Git Branches/Commits; do not treat Markdown state as proof that code has been integrated.

## Tracker Runtime Operations

- **Frontier**: Scan the authorized Spec's Open Ticket files, excluding unresolved blockers and existing Claims; rescan after every advancement and select deterministically by number.
- **Claim**: Compete for the Initiative Scheduler in the Tracker directory by atomically creating `scheduler.lock`, then atomically create `<ticket>.claim` for the Ticket; the lock records `run_id` and does not use a short TTL. Losers must not create a Coder.
- **Checkpoints**: Append minimal records with Run ID and an event-specific idempotency key under the configured Agent Run section. Collect both Ticket Verdicts independently and write one combined `REVIEW_RESULT`. Do not add a parser, sequence chain, or duplicate idempotency key; append `EVENT_SUPERSEDED` to correct an error.
- **Candidate implementation**: Associate the Ticket Branch and Commit; do not use `claimed` or Reviewer PASS to misrepresent integration as complete.
- **Integration**: Integrate with `auto-merge` only when both Verdicts are PASS and Base/Head are unchanged; for `human-merge`, record `READY_FOR_HUMAN_MERGE`, wait for user action, and then refresh Git facts.
- **Closure**: After verifying that the Commit entered the declared branch, record `INTEGRATION_RESULT`, mark the Ticket `resolved`, then atomically remove only its owned Ticket lock. In a multi-Spec Run, keep member Specs Open through Initiative Acceptance; on Initiative PASS, resolve member Specs first and the parent last, then atomically remove only the owned `scheduler.lock`. A stored Run ID mismatch, dirty worktree, lock conflict, or inconsistent Git state must leave the Item Open and provide recovery steps.
