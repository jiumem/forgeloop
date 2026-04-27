# run-initiative

## Trigger

Use this skill when the user asks to execute, continue, resume, or deliver an initiative from a `PLAN.md`.

## Goal

Run one initiative by Milestone. The Scheduler coordinates one reusable Coder and one reusable Reviewer through explicit task packets, records minimal recovery facts in `LEDGER.md`, and advances only when the Reviewer returns `PASS`.

## Read First

1. Locate the initiative root:
   - active initiative: `docs/initiatives/active/<initiative-slug>/`
   - completed initiative: read-only unless the user explicitly reopens it or creates a follow-up
2. `<initiative-root>/PLAN.md`
3. `<initiative-root>/LEDGER.md`
4. `git status`
5. recent `git log --oneline` for the working branch
6. reference inputs listed in PLAN as needed

Completed initiatives are read-only by default. Prefer creating a follow-up initiative with a new slug such as `<initiative-slug>-v2` or `<initiative-slug>-followup`. For a direct reopen, move the completed record back to `docs/initiatives/active/<initiative-slug>/`; do not keep the same slug in both `active/` and `completed/`.

## Runtime Roles

Use generic Codex subagents by task packet, not static custom agent manifests.

- Scheduler: the main thread; coordinates, records, and packages work
- Coder: usually a reusable `default` or `worker` subagent with high reasoning effort
- Reviewer: usually a reusable `default` subagent with high reasoning effort

When delegating, send a self-contained packet and do not rely on parent conversation history. Request `fork_context=false` when the tool supports it.

## Subagent Reuse Rule

- At initiative start, create at most one Coder subagent and one Reviewer subagent.
- Prefer stable task names when the tool supports them:
  - `coder_<initiative_slug_snake>`
  - `reviewer_<initiative_slug_snake>`
- Normalize `<initiative_slug_snake>` for `task_name`: lowercase; replace any character outside `[a-z0-9_]` with `_`; example `saaskit-ui-v1` becomes `saaskit_ui_v1`.
- Reuse those subagents across Milestones with `send_input` when available.
- Spawn a replacement only if the previous subagent is closed, unavailable, or no longer suitable.
- Do not spawn a fresh Reviewer for every Milestone by default.
- Record unavailable subagent tools or replacements in `LEDGER.md` notes when they affect review provenance.

If subagent tools are unavailable, continue only when the user asked to continue or the environment makes subagents impossible. Record the run as `explicit solo best-effort` in `LEDGER.md`. A solo best-effort review may produce a provisional `PASS` for packaging or archive delivery, but it must not be described as subagent review.

## Milestone Status Values

Allowed Milestone statuses are:

```text
TODO
CODING
REVIEW
REPAIR
PASS
PAUSED
CANCELLED
```

Only `PASS` advances to the next Milestone. `CANCELLED` is skipped only when the user explicitly cancels that Milestone or the initiative. `PAUSED` does not complete an initiative.

## Dirty Worktree Rule

Before coding, inspect `git status`.

If unrelated dirty changes exist:

- do not include them in Milestone commits
- do not revert, overwrite, or “clean up” unrelated user changes
- either ask the user, create a safe branch from the current state, or record the dirty baseline and restrict the diff range
- make the Coder and Reviewer packets explicit about the intended diff range

## Write Ownership

Scheduler owns `LEDGER.md` status updates, reviewer verdict/provenance updates, and final movement between `active/` and `completed/`.

Coder may write:

```text
source, test, docs, and config files needed by the active Milestone
<initiative-root>/evidence/
```

Coder must not modify `PLAN.md` unless the Milestone explicitly asks for a planning-document update and the Scheduler says so. If `PLAN.md` appears wrong or incomplete, Coder must report the mismatch to Scheduler instead of silently rewriting the PLAN.

Coder must not mark Milestone status, reviewer verdict, or reviewer provenance in `LEDGER.md`.

Reviewer must not modify code, `PLAN.md`, `LEDGER.md`, or repo-tracked evidence files. Reviewer returns a verdict report only. Reviewer may capture or inspect temporary screenshots for review; if those screenshots must be preserved, Scheduler records or copies them into `evidence/` after the verdict.

Scheduler-owned `LEDGER.md`, `DELIVERY.md`, and evidence updates must be committed when Git is available. Prefer either a small Scheduler commit after each Milestone verdict or include the ledger/evidence updates in the Milestone commit range before push. Do not leave recovery-critical `LEDGER.md` updates only in the local worktree after a Milestone `PASS`.

## Write Targets

Allowed writes while executing an active initiative:

```text
<initiative-root>/LEDGER.md
<initiative-root>/evidence/
source, test, docs, and config files needed by the active Milestone
```

Allowed writes when finalizing a completed initiative:

```text
<initiative-root>/DELIVERY.md
docs/initiatives/completed/<initiative-slug>/
```

Do not modify recommendation snapshots as part of execution.

## Workflow

1. Confirm or create the working branch, normally `codex/<initiative-slug>`.
2. Locate the active initiative root and read `PLAN.md` and `LEDGER.md`.
3. Resume from the first Milestone whose status is not `PASS` and not `CANCELLED`.
4. Send the Coder a self-contained packet using `references/coder-packet.md`.
5. Coder reads required docs and source, implements the Milestone, runs validation, performs screenshots for UI work, commits, pushes when possible, and reports evidence.
6. Scheduler updates `LEDGER.md` to `REVIEW` with commit range, validation, and evidence paths.
7. Send the Reviewer a self-contained packet using `references/reviewer-packet.md`.
8. Reviewer reads PLAN, references, Coder report, and actual diff; then reviews from product, test, and architecture perspectives.
9. If Reviewer returns `REPAIR_REQUIRED`, send only the blocking issues back to Coder, record repair history, and repeat review.
10. For repairs, Reviewer should inspect the repair diff and, when needed, the cumulative Milestone diff from the last accepted base to current HEAD. A fixup-only review may confirm a narrow blocker is fixed, but final `PASS` must remain compatible with the full Milestone diff.
11. If Reviewer returns `PASS`, Scheduler updates `LEDGER.md`, commits recovery-critical ledger/evidence updates when Git is available, and moves to the next Milestone.
12. Continue directly to the next Milestone after `PASS`; do not stop for a summary unless the user interrupts, a blocking ambiguity or safety issue appears, or the initiative is complete.
13. After all Milestones pass, run final validation.
14. If final validation fails:
    - keep the initiative in `active/`
    - record the final validation failure in `LEDGER.md`
    - create or update a repair entry
    - send the final validation blockers to Coder
    - rerun Reviewer for the affected Milestone, the repair diff, and the cumulative diff when needed
    - do not write completed `DELIVERY.md` or move to `completed/`
15. If final validation passes, write or update `DELIVERY.md` using `references/delivery-template.md`, prepare a PR summary, commit recovery-critical delivery/ledger updates when Git is available, and move the initiative directory from `docs/initiatives/active/<initiative-slug>/` to `docs/initiatives/completed/<initiative-slug>/`.
16. Do not create a second status file for completion. `PLAN.md`, `LEDGER.md`, `DELIVERY.md`, and Git history are sufficient.

## Reviewer Verdict Rule

Reviewer output must end with exactly one of:

```text
PASS
REPAIR_REQUIRED
```

Reviewer `PASS` is required before the initiative advances. Only `PASS` advances the initiative.

Record verdict provenance in `LEDGER.md`: subagent reviewer, human reviewer, or explicit solo best-effort review. Never blur validation success, commit, push, or zip packaging into reviewer approval.

## Recovery Rule

Recovery requires only:

1. locate the initiative in `docs/initiatives/active/<slug>/` or `docs/initiatives/completed/<slug>/`
2. read `PLAN.md`
3. read `LEDGER.md`
4. inspect `git status`
5. inspect recent commits
6. resume from the first non-`PASS`, non-`CANCELLED` Milestone when the initiative is still active

Do not reconstruct execution from chat memory.

## Quality Bar

- Scheduler keeps working through Milestones until the initiative is complete, unless blocked or interrupted.
- Coder must read PLAN and listed reference inputs before implementation.
- Coder should run relevant validation and record evidence.
- For UI work, Coder and Reviewer should both perform screenshot-based confirmation when practical.
- Reviewer must inspect the actual diff range, not just the Coder report.
- Reviewer must not edit code, PLAN, LEDGER, or repo-tracked evidence.
- Commit and push are evidence and recovery checkpoints, not approval.
- Do not skip Reviewer because validation passed.
- Completed initiatives belong in `docs/initiatives/completed/<slug>/` after final validation and delivery notes are recorded.
