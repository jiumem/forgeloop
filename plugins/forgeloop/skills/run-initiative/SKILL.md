---
name: run-initiative
description: Use when the user asks to execute, continue, resume, repair, or deliver an Initiative from PLAN.md; coordinates Coder/Reviewer Milestone loops and advances only after Reviewer PASS.
---

# run-initiative

## Trigger

Use this skill when the user asks to execute, continue, resume, or deliver an initiative from a `PLAN.md`.

## Goal

Run one initiative by Milestone. Codex in the current main thread is the Scheduler. Scheduler coordinates one reusable Coder subagent and one reusable Reviewer subagent through explicit task entrypoints and role protocols, records minimal recovery facts in `LEDGER.md`, and advances only when the Reviewer returns `PASS`.

Invoking this skill is explicit user approval to delegate milestone implementation and review to subagents. Do not skip Coder or Reviewer subagent delegation merely to conserve user tokens. Use solo execution only when subagent tools are unavailable, fail, or the user explicitly forbids subagents.

## Read First

1. Locate the initiative root:
   - active initiative: `docs/initiatives/active/<initiative-code>-<initiative-slug>/`
   - completed initiative: read-only unless the user explicitly reopens it or creates a follow-up
2. `<initiative-root>/DESIGN.md` when present
3. `<initiative-root>/PLAN.md`
4. `<initiative-root>/LEDGER.md`
5. `git status`
6. recent `git log --oneline` for the working branch
7. reference inputs listed in PLAN as needed

Completed initiatives are read-only by default. Prefer creating a follow-up initiative with a new coded slug such as `002-<initiative-slug>-v2` or `002-<initiative-slug>-followup`. For a direct reopen, move the completed record back to `docs/initiatives/active/<initiative-code>-<initiative-slug>/`; do not keep the same coded slug in both `active/` and `completed/`.

## Runtime Roles

Use generic Codex subagents by task entrypoint and role protocol, not static custom agent manifests.

- Scheduler: Codex itself in the current main thread; not a subagent; coordinates, records, and packages work
- Coder: usually a reusable `default` or `worker` subagent with high reasoning effort
- Reviewer: usually a reusable `default` subagent with high reasoning effort

The Scheduler must remain in the main thread. Do not spawn a Scheduler subagent.

When delegating, send a self-contained task-entry packet and do not rely on parent conversation history. Request `fork_context=false` when the tool supports it. "Self-contained" means the task entry includes complete paths, boundaries, diff ranges, and evidence pointers; it does not mean copying or rewriting the role protocol.

## Delegation Packet Rule

Scheduler packets are task entrypoints, not extracted role manuals.

When delegating to Coder or Reviewer, the Scheduler must provide only:

- role protocol path: `plugins/forgeloop/skills/run-initiative/references/coder-protocol.md` or `reviewer-protocol.md`
- initiative root, `DESIGN.md` when present, `PLAN.md`, and `LEDGER.md`
- current Milestone ID and intended scope boundary
- branch, base commit, dirty baseline, and relevant evidence paths
- for Reviewer: Coder report, diff range, repair diff when applicable, and preview targets or screenshots when relevant

The Scheduler must not replace the role protocol with a rewritten summary of Coder or Reviewer responsibilities. The subagent must read its role protocol directly, then independently locate and read the source-of-truth repository documents needed for the task.

## Subagent Reuse Rule

- Treat a user request to run this skill as permission to spawn or reuse the Coder and Reviewer subagents required by the workflow.
- At initiative start, create at most one Coder subagent and one Reviewer subagent.
- Prefer stable task names when the tool supports them:
  - `coder_<initiative-code>`
  - `reviewer_<initiative-code>`
- Extract `<initiative-code>` from the three-digit prefix in the initiative directory name, for example `001-auth-hardening` uses `coder_001` and `reviewer_001`.
- If an older initiative has no three-digit prefix, fall back to `coder_<initiative_slug_snake>` and `reviewer_<initiative_slug_snake>`.
- Normalize fallback `<initiative_slug_snake>` for `task_name`: lowercase; replace any character outside `[a-z0-9_]` with `_`; example `saaskit-ui-v1` becomes `saaskit_ui_v1`.
- Reuse those subagents across Milestones with `send_input` when available.
- Spawn a replacement only if the previous subagent is closed, unavailable, or no longer suitable.
- Do not spawn a fresh Reviewer for every Milestone by default.
- Record unavailable subagent tools or replacements in `LEDGER.md` notes when they affect review provenance.

If subagent tools are unavailable, fail, or are explicitly forbidden by the user, continue only when the user asked to continue or the environment makes subagents impossible. Record the run as `explicit solo best-effort` in `LEDGER.md`. Solo best-effort is reduced review provenance: it may prepare packaging and delivery notes, but it must not be described as formal independent Reviewer approval or subagent review. Completion records must make the reduced provenance explicit.

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

## Long-Running Autonomy Rule

`run-initiative` is an autonomous, long-running coding loop. Once the user invokes this skill, continue through Coder implementation, Reviewer review, repair cycles, final validation, delivery notes, and completion archival until the whole Initiative is delivered.

Do not stop after a Milestone to summarize, ask whether to continue, or request routine approval. Do not interrupt the user for choices the Scheduler can resolve with established engineering best practices, the existing PLAN, repository conventions, or conservative implementation judgment.

Interrupt the user only for a major blocker that requires human decision, such as destructive data loss risk, missing credentials, conflicting product requirements, legal/security approval, an impossible PLAN, or unrelated dirty worktree changes that cannot be safely isolated. When interrupted, state the blocker and the smallest decision needed to proceed.

## Dirty Worktree Rule

Before coding, inspect `git status`.

If unrelated dirty changes exist:

- do not include them in Milestone commits
- do not revert, overwrite, or “clean up” unrelated user changes
- either ask the user, create a safe branch from the current state, or record the dirty baseline and restrict the diff range
- make the Coder and Reviewer task-entry packets explicit about the intended diff range

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

Scheduler-owned `LEDGER.md`, `DELIVERY.md`, and evidence updates must be committed when Git is available. Prefer one coherent Milestone implementation commit, plus optional repair fixup commits and optional Scheduler evidence/ledger commits. Do not split the primary implementation by Work Item by default. Do not leave recovery-critical `LEDGER.md` updates only in the local worktree after a Milestone `PASS`.

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
docs/initiatives/completed/<initiative-code>-<initiative-slug>/
docs/initiatives/handoff/<initiative-code>-<initiative-slug>.md
docs/initiatives/handoff/index.md
```

Do not modify recommendation snapshots as part of execution.

## Workflow

1. Confirm or create the working branch, normally `codex/<initiative-code>-<initiative-slug>`.
2. Locate the active initiative root and read `DESIGN.md` when present, `PLAN.md`, and `LEDGER.md`.
3. Resume from the first Milestone whose status is not `PASS` and not `CANCELLED`.
4. Spawn or reuse the Coder subagent, then send a task-entry packet that points it to `references/coder-protocol.md`, the initiative root, the current Milestone, and execution boundaries.
5. Coder reads its role protocol, independently locates source-of-truth docs, follows the Coder Construction Loop, implements the Milestone, runs validation, performs screenshots for UI work, creates a coherent Milestone-level commit, pushes when possible as a review candidate, and reports evidence.
6. Scheduler updates `LEDGER.md` to `REVIEW` with commit range, validation, and evidence paths.
7. Spawn or reuse the Reviewer subagent, then send a task-entry packet that points it to `references/reviewer-protocol.md`, the initiative root, Coder report, actual diff range, and review boundaries.
8. Reviewer reads its role protocol, independently locates source-of-truth docs, inspects the Coder report and actual diff, then reviews from product, test, and architecture perspectives.
9. If Reviewer returns `REPAIR_REQUIRED`, record repair history before any new coding.
10. Apply the repair budget: if the same Milestone receives `REPAIR_REQUIRED` three times, or the same blocking issue survives two repair attempts, pause the initiative, set the Milestone to `PAUSED`, record the structural blocker in `LEDGER.md`, and ask for human architectural decision instead of continuing the loop.
11. If the repair budget has not been exceeded, send only the blocking issues back to Coder and repeat review.
12. For repairs, Reviewer should inspect the repair diff and, when needed, the cumulative Milestone diff from the last accepted base to current HEAD. A fixup-only review may confirm a narrow blocker is fixed, but final `PASS` must remain compatible with the full Milestone diff.
13. If Reviewer returns `PASS`, Scheduler updates `LEDGER.md`, commits recovery-critical ledger/evidence updates when Git is available, and moves to the next Milestone.
14. Continue directly to the next Milestone after `PASS`; do not stop for a summary unless the user interrupts, a blocking ambiguity or safety issue appears, or the initiative is complete.
15. After all Milestones pass, run final validation.
16. If final validation fails:
    - keep the initiative in `active/`
    - record the final validation failure in `LEDGER.md`
    - create or update a repair entry
    - send the final validation blockers to Coder
    - rerun Reviewer for the affected Milestone, the repair diff, and the cumulative diff when needed
    - do not write completed `DELIVERY.md` or move to `completed/`
17. If final validation passes, write or update `DELIVERY.md` using `references/delivery-template.md`, prepare a PR summary, and always write or update handoff using `references/handoff-template.md`. If there are no handoff findings, record `none` / `无` explicitly.
18. Move the initiative directory from `docs/initiatives/active/<initiative-code>-<initiative-slug>/` to `docs/initiatives/completed/<initiative-code>-<initiative-slug>/`, update `docs/initiatives/handoff/index.md` using `references/handoff-index-template.md` when creating it, and commit recovery-critical delivery/ledger/handoff updates when Git is available.
19. Do not create a second status file for completion. `PLAN.md`, `LEDGER.md`, `DELIVERY.md`, handoff, and Git history are sufficient.

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

1. locate the initiative in `docs/initiatives/active/<initiative-code>-<initiative-slug>/` or `docs/initiatives/completed/<initiative-code>-<initiative-slug>/`
2. read `DESIGN.md` when present
3. read `PLAN.md`
4. read `LEDGER.md`
5. inspect `git status`
6. inspect recent commits
7. resume from the first non-`PASS`, non-`CANCELLED` Milestone when the initiative is still active

Do not reconstruct execution from chat memory.

## Language Rule

- Write `LEDGER.md` updates, `DELIVERY.md`, handoff files, and user-facing completion summaries in the primary language of the user's request by default.
- If the request mixes languages, follow the language used for the user's requirements and decisions.
- Preserve technical identifiers, file paths, commands, code symbols, branch names, commit SHAs, status tokens, and tool names as written.
- Keep protocol values such as `TODO`, `CODING`, `REVIEW`, `REPAIR`, `PASS`, `PAUSED`, `CANCELLED`, and `REPAIR_REQUIRED` unchanged.
- Coder and Reviewer report headings from their role protocols must remain fixed for Scheduler parsing; their substantive report content should follow the requested output language when practical.
- If the user explicitly requests a language, that instruction overrides the default.
- Template headings and explanatory text are structural guidance; translate or adapt them to the output language when writing the final document.

## Quality Bar

- Scheduler keeps working through Milestones until the initiative is complete, unless a major blocker requires user decision or the user interrupts.
- Scheduler must not pause for routine progress summaries, permission to continue, or non-blocking implementation choices.
- Coder must read DESIGN when present, PLAN, and listed reference inputs before implementation.
- Coder must independently locate source-of-truth docs instead of relying on Scheduler summaries.
- Coder must follow `coder-protocol.md` as its implementation discipline, including behavior intent, public seam selection, contract / truth-source delta control, validation evidence, self-diff hygiene, and repair discipline.
- Coder should run relevant validation and record evidence.
- For UI work, Coder and Reviewer should both perform screenshot-based confirmation when practical.
- Reviewer must inspect DESIGN when present, PLAN, and the actual diff range, not just the Coder report.
- Reviewer must independently locate source-of-truth docs instead of relying on Scheduler or Coder summaries.
- Reviewer must not edit code, PLAN, LEDGER, or repo-tracked evidence.
- Commit and push are evidence and recovery checkpoints, not approval.
- Coder push before Reviewer `PASS` is only a review candidate. Do not mark a Milestone accepted until Reviewer returns `PASS`.
- Do not skip Reviewer because validation passed.
- Completed initiatives belong in `docs/initiatives/completed/<initiative-code>-<initiative-slug>/` after final validation and delivery notes are recorded.
- Scheduler writes handoff entries from Coder deferred notes, Reviewer non-blocking findings, final validation observations, and Scheduler judgment. Coder and Reviewer provide inputs but do not maintain handoff files.
- Scheduler always writes a handoff file for completed initiatives. If there are no findings, record an explicit empty result instead of skipping the artifact.
- Blocking issues must be fixed in the current initiative and must not be deferred to handoff.
