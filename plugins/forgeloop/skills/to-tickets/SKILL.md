---
name: to-tickets
description: Load when the user explicitly wants an approved Spec split into implementation-ready vertical Tickets.
---

# To Tickets

In normal decomposition mode, break one approved formal Tracker Spec into **tickets** — tracer-bullet vertical slices, each declaring the tickets that **block** it. A plan or conversation may clarify the Spec but never replaces the formal parent. The explicit repair and reconciliation modes below use their own formal inputs.

A configured Issue Tracker must already exist before any read or write. If `docs/agents/issue-tracker.md` is missing, return `FAILED_PRECONDITION`, identify the missing configuration, and instruct the user to invoke `$setup-forgeloop` explicitly. Do not invoke it, invent a Tracker, fall back to Local, or publish Tickets.

## Process

### 1. Gather context

Require a reference to one approved formal Tracker Spec, fetch it, and read its full body, comments, revision, state, and existing child Tickets. Conversation context may supply clarifications but cannot serve as the parent contract. Require valid `Delivery Acceptance` with unique stable local references; it is the single source of truth for parent completion. Also require the parent Spec's explicit `Cross-seam Invariants` form and the Validation Entries referenced by every `Proof`. An invalid or internal-only parent `Proof` is a malformed parent contract: return `FAILED_PRECONDITION` without drafting or publishing Tickets. If the reference is missing, ambiguous, not a Spec, not approved, or lacks valid `Delivery Acceptance`, return `FAILED_PRECONDITION` without drafting or publishing Tickets.

### 2. Explore the codebase (optional)

If you have not already explored the codebase, do so to understand the current state of the code. Ticket titles and descriptions should use the project's domain glossary vocabulary, and respect ADRs in the area you're touching.

Look for opportunities to prefactor the code to make the implementation easier. "Make the change easy, then make the easy change."

### 3. Draft vertical slices

Map every Ticket to one or more stable Delivery Acceptance references before drafting. Together, the Tickets must cover every parent reference while retaining their own Ticket Acceptance criteria. Keep `Release Boundary` Post-delivery actions and Tracking references outside the Ticket Frontier, Spec Scope, and Initiative membership; never create a parallel parent completion standard.

When the parent states `None — no Cross-seam Invariants.`, retain `Invariant ownership: None`. Otherwise assign every invariant to exactly one Owning Ticket. That Ticket must deliver the complete parent `Contract`; its Acceptance criteria cite the invariant `ID` and parent `Proof` mapping and require evidence from every Validation Entry named in the parent `Proof`. Record references only; do not copy or reinterpret the parent Contract. Other Tickets may provide prerequisites through normal blocking edges, but there are no Contributing Tickets, shared ownership, or special invariant Ticket type.

If no proposed ordinary vertical slice can own the complete Contract, reshape the slices or add an ordinary vertical Ticket that closes the real behavior. Never create a Ticket that only adds an integration test. Later integration, cumulative audit, or Final Acceptance may re-run or inspect the owner's Proof on a bound Head but gains no ownership. If decomposition reveals a required invariant absent from the approved Spec, or requires changing a parent Contract or Proof mapping, return `CONTRACT_BLOCKER`; do not invent or write back the contract, and keep Tracker writes at zero.

Break the work into **tracer bullet** tickets.

<vertical-slice-rules>

- Each slice cuts a narrow but COMPLETE path through every layer (schema, API, UI, tests) — vertical, NOT a horizontal slice of one layer
- A completed slice is demoable or verifiable on its own
- Each slice is sized to fit in a single fresh context window
- Any prefactoring should be done first

</vertical-slice-rules>

Give each ticket its **blocking edges** — the other tickets that must complete before it can start. A ticket with no blockers can start immediately.

**Wide refactors are the exception to vertical slicing.** A **wide refactor** is one mechanical change — rename a column, retype a shared symbol — whose **blast radius** fans across the whole codebase, so a single edit breaks thousands of call sites at once and no vertical slice can land green. Don't force it into a tracer bullet; sequence it as **expand–contract**. First expand: add the new form beside the old so nothing breaks. Then migrate the call sites over in batches sized by blast radius (per package, per directory), each batch its own ticket blocked by the expand, keeping CI green batch to batch because the old form still exists. Finally contract: delete the old form once no caller remains, in a ticket blocked by every migrate batch. When even the batches can't stay green alone, keep the sequence but let them share an integration branch that all block a final integrate-and-verify ticket — green is promised only there.

### 4. Quiz the user

Present the proposed breakdown as a numbered list. Then show the complete `Invariant → Owning Ticket` mapping; when the parent declares `None`, show `Invariant ownership: None`. For each ticket, show:

- **Title**: short descriptive name
- **Blocked by**: which other tickets (if any) must complete first
- **What it delivers**: the end-to-end behaviour this ticket makes work

Ask the user:

- Does the granularity feel right? (too coarse / too fine)
- Are the blocking edges correct — does each ticket only depend on tickets that genuinely gate it?
- Should any tickets be merged or split further?

Validate the mapping before asking for approval: every parent invariant has exactly one Owning Ticket, and that Ticket closes the complete Contract and will submit every assertion in the parent Proof through its named public behavior seam. With no owner, multiple owners, or an Owning Ticket whose planned evidence uses only a helper or internal seam, publish no Tickets and ask the user to adjust the ordinary vertical slices. Iterate until the user approves both the breakdown and the mapping. Every invariant gate runs before the first Tracker write. On failure, create no Ticket, change no Tracker state, and add no `ready-for-agent` label. Ownership IDs and references are Agent-readable planning traceability, not Tracker state, a parser, or a workflow.

### 5. Publish the tickets to the configured tracker

Publish the approved tickets. Build every new Ticket's canonical tracker title as `[Ticket] <outcome-oriented title>` and render the `[Ticket]` prefix exactly once, even when the supplied title already contains a canonical or legacy prefix. Use that canonical title for conflict checks, duplicate queries, and publication. **How** depends on the tracker `/setup-forgeloop` configured — the tickets are the same either way, only the shape of the blocking edges changes:

- **Local files** → write one file per ticket under `.scratch/<feature-slug>/issues/<NN>-<slug>.md`, numbered from `01` in dependency order (blockers first). Each file's "Blocked by" lists the numbers/titles it depends on. Use the per-ticket file template below — one ticket per file, never a single combined file.
- **A real issue tracker (GitHub, Linear, …)** → publish one issue per ticket in dependency order (blockers first) so each ticket's blocking edges can reference real identifiers. Use the platform's native blocking / sub-issue relationship where it has one; otherwise set each ticket's "Blocked by" to the blocking issues. Apply the `ready-for-agent` triage label unless instructed otherwise — the tickets are agent-grabbable by construction.

Work the **frontier**: any ticket whose blockers are all done. For a purely linear chain that means top to bottom.

Do NOT close or modify any parent issue.

<local-ticket-template>

# <NN> — <Ticket title>

**What to build:** the end-to-end behaviour this ticket makes work, from the user's perspective — not a layer-by-layer implementation list.

**Parent Delivery Acceptance references:** <stable parent references covered by this Ticket>

**Owned Cross-seam Invariants:** <invariant IDs or None; for each ID, reference the parent Contract and Proof without copying them>

**Blocked by:** the numbers/titles of the tickets that gate this one, or "None — can start immediately".

**Status:** ready-for-agent

- [ ] Acceptance criterion 1
- [ ] Acceptance criterion 2

</local-ticket-template>

<issue-template>

## Parent

A reference to the approved parent Spec on the configured Tracker. This section is mandatory.

## What to build

The end-to-end behaviour this ticket makes work, from the user's perspective — not layer-by-layer implementation.

## Parent Delivery Acceptance references

- <stable parent reference covered by this Ticket>

## Owned Cross-seam Invariants

- <invariant ID or None; for each ID, reference the parent Contract and Proof without copying them>

## Acceptance criteria

- [ ] Criterion 1
- [ ] Criterion 2

## Blocked by

- A reference to each blocking ticket, or "None — can start immediately".

</issue-template>

In either form, avoid specific file paths or code snippets — they go stale fast. Exception: if a prototype produced a snippet that encodes a decision more precisely than prose can (state machine, reducer, schema, type shape), inline it and note briefly that it came from a prototype. Trim to the decision-rich parts — not a working demo, just the important bits.

After publication, return the parent Spec and Ticket references and tell the user they may explicitly invoke `$run-initiative`. Do not start that Workflow automatically.

## Forgeloop Acceptance Repair Mode

Enter this mode only when the user explicitly invokes `$to-tickets` for a formal `ACCEPTANCE_RESULT` with `REPAIR_REQUIRED` and one stable `repair_key` per Finding. Read the parent Spec or Initiative, the Acceptance Findings, the final Commit, existing Open Tickets, and every Ticket already carrying any of those keys.

- Keep the approved parent contract and completed Ticket history unchanged. If the Findings require changing Scope, `Delivery Acceptance`, Ticket Acceptance criteria, the Spec, an ADR, or confirmed Initiative membership, stop with `CONTRACT_BLOCKER` instead of drafting repair Tickets.
- For Spec Acceptance, use that Spec as `owning_spec_ref`. For Initiative Acceptance, route each repair slice to an existing member Spec whose approved Scope covers it; use coordinated Tickets under multiple member Specs when necessary. Never create a repair Ticket directly under the Initiative. If no existing member Spec can own a Finding without contract change, return `CONTRACT_BLOCKER`.
- Query every key before drafting. Reuse the unique valid Open repair Ticket carrying each key; stop when one key has ambiguous or conflicting matches. Multiple keys may point to the same Ticket only when its body lists every key and the Findings form one atomic vertical slice. Do not recreate represented work.
- For unmatched keys, draft only the smallest vertical Ticket or Tickets needed to satisfy their named Acceptance Findings. Do not decompose the whole Spec again. Preserve the normal user quiz and approval before publication.
- Put `owning_spec_ref`, the Initiative reference when applicable, Acceptance level, assigned `repair_key` values, final Commit, stable `finding_id` values, observable repair checks, and any genuine blockers in every repair Ticket. Keep each Ticket inside the existing approved Scope and sized for one fresh context.
- Publish idempotently. If a write result is ambiguous, query by every assigned `repair_key` and verify the body and parent relationship before retrying. Never create a second Ticket merely because the first response was uncertain.

This mode creates or reuses formal repair Tickets only after the user's explicit invocation. It does not resume `$run-initiative`; the user resumes the original Run separately after the Tracker work is valid.

## Forgeloop Spec Revision Reconciliation Mode

Enter this mode only when the user explicitly invokes `$to-tickets` for a formal Spec with a material new Revision and a paused Run. Read the previous and current Spec Revisions plus every existing child Ticket, including body, comments, status, parent, and blockers.

- Preserve every Completed or Closed Ticket and its history unchanged.
- Compare the revised contract only with Open Tickets. Present the smallest proposed set of `retain`, `update`, `supersede`, and `create` actions, including dependency changes, and obtain normal user approval before writing.
- Reuse an Open Ticket when its delivery goal remains valid. Update only the approved contract fields and blockers. Create only missing vertical slices. Do not delete obsolete Open Tickets; mark them superseded and close them only after explicit approval.
- Before every write, refresh the current Ticket and search for an already-applied equivalent action. If a write result is ambiguous, query and verify before retrying.
- Stop with `CONTRACT_BLOCKER` when reconciliation requires a different core Problem, Actor, delivery target, expanded Scope, Spec rewrite, ADR change, or Initiative membership change.

Do not modify the Spec, parent Initiative, Completed Tickets, Run Claim, or Run checkpoints. This mode reconciles Tracker Tickets only; it does not resume `$run-initiative`.
