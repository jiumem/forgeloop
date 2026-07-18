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

### 2. Explore the relevant codebase

Explore the code relevant to this Spec and retain locatable evidence for design decisions. Complete this exploration before drafting or risk screening. Ticket titles and descriptions should use the project's domain glossary vocabulary and respect relevant ADRs.

Look for necessary prefactoring only when code evidence shows it makes the approved current result easier to deliver. Keep necessary prefactoring inside the first vertical Ticket that consumes it unless it independently provides a currently required and observable system guarantee.

### 3. Draft vertical slices

Map every Ticket to one or more stable Delivery Acceptance references before drafting. Together, the Tickets must cover every parent reference while retaining their own Ticket Acceptance criteria. Keep `Release Boundary` Post-delivery actions and Tracking references outside the Ticket Frontier, Spec Scope, and Initiative membership; never create a parallel parent completion standard.

When the parent states `None — no Cross-seam Invariants.`, retain `Invariant ownership: None`. Otherwise assign every invariant to exactly one Owning Ticket. That Ticket must deliver the complete parent `Contract`; its Acceptance criteria cite the invariant `ID` and parent `Proof` mapping and require evidence from every Validation Entry named in the parent `Proof`. Record references only; do not copy or reinterpret the parent Contract. Other Tickets may provide prerequisites through normal blocking edges, but there are no Contributing Tickets, shared ownership, or special invariant Ticket type.

If no proposed ordinary vertical slice can own the complete Contract, reshape the slices or add an ordinary vertical Ticket that closes the real behavior. Never create a Ticket that only adds an integration test. Later integration, cumulative audit, or Final Acceptance may re-run or inspect the owner's Proof on a bound Head but gains no ownership. If decomposition reveals a required invariant absent from the approved Spec, or requires changing a parent Contract or Proof mapping, return `CONTRACT_BLOCKER`; do not invent or write back the contract, and keep Tracker writes at zero.

Apply Ticket Minimality to the complete candidate graph before sizing or approval. This is a thin decomposition gate: implement the approved Spec faithfully and do not reopen the approved solution design or repeat its Necessity Review.

- Default to one to three minimal complete vertical Tickets. This is a strong default, not a hard limit.
- Every Ticket must produce a current observable user or system result when integrated. Do not publish a future-only infrastructure Ticket, an internal helper with no current consumer, or work justified only by possible later use.
- Keep an enabling change with its current consumer as one acceptable vertical result unless the enabling change independently provides a currently required and observable system guarantee.
- For more than three Tickets, explain what current result every extra Ticket closes and which approved Delivery Acceptance outcome, Cross-seam Invariant, or required failure behavior would fail if that Ticket were omitted. Evidence-backed structural work remains valid.
- If the smallest honest Ticket graph requires changing the approved Problem, Actor, Scope, Delivery Acceptance, Cross-seam Invariant, ADR, product behavior, or public interface, return `CONTRACT_BLOCKER`; do not hide the change in decomposition.

Judge these rules from the complete Spec, code evidence, and candidate graph. Do not use a fixed count, keyword, field-presence check, or score as a substitute for semantic judgment.

Break the work into **tracer bullet** tickets.

<vertical-slice-rules>

- Each slice cuts a narrow but COMPLETE path through every layer (schema, API, UI, tests) — vertical, NOT a horizontal slice of one layer
- A completed slice is demoable or verifiable on its own
- Each slice is sized to fit in a single fresh context window
- Apply Ticket Minimality to necessary prefactoring; do not add a separate prefactoring step

</vertical-slice-rules>

Give each ticket its **blocking edges** — the other tickets that must complete before it can start. A ticket with no blockers can start immediately.

**Wide refactors are the exception to vertical slicing.** A **wide refactor** is one mechanical change — rename a column, retype a shared symbol — whose **blast radius** fans across the whole codebase, so a single edit breaks thousands of call sites at once and no vertical slice can land green. Don't force it into a tracer bullet; sequence it as **expand–contract**. First expand: add the new form beside the old so nothing breaks. Then migrate the call sites over in batches sized by blast radius (per package, per directory), each batch its own ticket blocked by the expand, keeping CI green batch to batch because the old form still exists. Finally contract: delete the old form once no caller remains, in a ticket blocked by every migrate batch. When even the batches can't stay green alone, keep the sequence on one approved Spec Integration Branch; the Spec root Final Integration Gate proves the final green delivery.

Complete the full draft set before risk screening, including every ordinary implementation Ticket and the shared-branch declaration required by the selected Branch topology. When the final stage has independent implementation work, draft it as an ordinary vertical Ticket with real Scope; validation, audit, PR/MR creation, or integration alone never justifies a Ticket. Classify every draft and show `Ticket → STANDARD | HIGH_RISK → evidence`. Use `HIGH_RISK` only when correctness, failure semantics, or evidence credibility materially depends on one or more of these properties:

- interpretation of dynamic, untrusted, or extensible input;
- concurrency, ordering, cancellation, retry, timeout, re-entry, or resource lifecycle;
- multi-step state changes requiring atomicity, rollback, recovery, or finalization;
- authority, permission, ownership, or another trust relationship;
- versioning, compatibility, migration, or recovery of old state;
- cross-stage identity, provenance, or evidence.

Do not classify by syntax, fields, dependencies, paths, project names, or technology labels. A merely mentioned property remains `STANDARD` when it does not materially affect correctness, failure semantics, or evidence credibility.

For each `HIGH_RISK` draft add a complete section with no `TBD`, placeholders, or unresolved branches:

```markdown
## Adversarial Design

Risk surface:
<input, state, timing, or authority that could break correctness>

Bounded model:
<finite and falsifiable grammar, state, transaction, lock, ownership, or compatibility rules>

Invariants:
<references to existing Spec/ADR invariants plus Ticket-internal constraints within Scope>

Adversarial cases:
<counterexamples directly related to the identified risk>

Proof:
<expected result observed through a real public behavior seam>
```

The model must bound applicable inputs, states, transitions, ordering, or ownership; claims such as “handle every case” are not finite and falsifiable. Cases target the identified risk rather than mechanically covering every category. Proof through only a helper, internal field, or intermediate projection is insufficient. This Proof is Ticket-level adversarial design evidence, not another `Delivery Acceptance` source. It may narrow checks for Ticket-internal constraints; if it claims a parent Cross-seam Invariant, cite its existing Validation Entry/Proof mapping. Reference the Spec and ADRs; do not copy or reinterpret the parent contract.

Implementation design may only refine approved behavior. If exploration exposes an unapproved high-risk product behavior, invariant, or failure semantics, or the design must change the Spec, `Delivery Acceptance`, product behavior, Scope, an ADR, or an approved public interface, return `CONTRACT_BLOCKER` and keep Tracker writes at zero. Approved implementation design cannot replace a missing product contract.

### 4. Quiz the user

Show the complete Ticket bodies, the `Ticket → STANDARD | HIGH_RISK → evidence` classification, and the complete `Invariant → Owning Ticket` mapping; when the parent declares `None`, show `Invariant ownership: None`. Then summarize each Ticket:

- **Title**: short descriptive name
- **Blocked by**: which other tickets (if any) must complete first
- **What it delivers**: the end-to-end behaviour this ticket makes work

Ask the user:

- Does the granularity feel right? (too coarse / too fine)
- Are the blocking edges correct — does each ticket only depend on tickets that genuinely gate it?
- Should any tickets be merged or split further?

Validate the mapping before asking for approval: every parent invariant has exactly one Owning Ticket, and that Ticket closes the complete Contract and will submit every assertion in the parent Proof through its named public behavior seam. With no owner, multiple owners, or an Owning Ticket whose planned evidence uses only a helper or internal seam, publish no Tickets and ask the user to adjust the ordinary vertical slices. Ask the user to approve the complete drafts, including risk classification, blocking edges, invariant mapping, and every applicable `Adversarial Design`. If the user changes any of them, update and reapprove the complete set. Every invariant gate runs before the first Tracker write. On failure, create no Ticket, change no Tracker state, and add no `ready-for-agent` label. Ownership IDs and references are Agent-readable planning traceability, not Tracker state, a parser, or a workflow.

Only after approval, create one fresh, isolated, read-only Design Reviewer for each approved `HIGH_RISK` Ticket; skip Design Reviewers for `STANDARD` Tickets. Bind each Reviewer to the parent Spec revision, relevant ADRs, complete Ticket draft, blocking edges, code evidence, and referenced invariants. It must not modify files, the Spec, ADRs, draft Tickets, or Tracker state, and must not propose unapproved product behavior. Ask it to use counterexamples to check that the model is finite, facts have one authoritative source, failure and recovery close the loop, no hidden caller constraints remain, and Proof is credible.

Require `PASS | DESIGN_GAPS | REVIEW_BLOCKED`. Every Finding contains `evidence`, `counterexample`, `missing_decision`, `required_proof`, and `contract_impact: NONE | SPEC | ADR`. Return PASS only with no Findings. A PASS binds only its exact fixed inputs. If that Ticket body, blocking edges, Spec revision, or referenced ADR changes, discard the affected PASS and run a new Reviewer.

All bound high-risk verdicts must be PASS before publication. If any Finding has `SPEC` or `ADR` impact, return `CONTRACT_BLOCKER` without changing the contract. Otherwise, for `DESIGN_GAPS`, keep Tracker writes at zero, return locatable Findings, and name the design clarification entry point. Do not create an automatic design repair loop. For `REVIEW_BLOCKED`, report the unreadable or invalid fixed input; do not treat missing evidence as PASS. Any failed, blocked, stale, or contract-conflicting review keeps Tracker writes at zero. Do not publish `STANDARD` Tickets early. These classifications and verdicts are Agent-readable design judgment and evidence, not Tracker fields, a parser, a state machine, or a workflow DSL.

### 5. Publish the tickets to the configured tracker

After every applicable Design Reviewer returns a bound PASS, publish the complete Ticket set in one batch. Build every new Ticket's canonical tracker title as `[Ticket] <outcome-oriented title>` and render the `[Ticket]` prefix exactly once, even when the supplied title already contains a canonical or legacy prefix. Use that canonical title for conflict checks, duplicate queries, and publication. **How** depends on the tracker `/setup-forgeloop` configured — the tickets are the same either way, only the shape of the blocking edges changes:

- **Local files** → write one file per ticket under `.scratch/<feature-slug>/issues/<NN>-<slug>.md`, numbered from `01` in dependency order (blockers first). Each file's "Blocked by" lists the numbers/titles it depends on. Use the per-ticket file template below — one ticket per file, never a single combined file.
- **A real issue tracker (GitHub, Linear, …)** → publish one issue per ticket in dependency order (blockers first) so each ticket's blocking edges can reference real identifiers. Use the platform's native blocking / sub-issue relationship where it has one; otherwise set each ticket's "Blocked by" to the blocking issues. Apply the `ready-for-agent` triage label unless instructed otherwise — the tickets are agent-grabbable by construction.

Work the **frontier**: any ticket whose blockers are all done. For a purely linear chain that means top to bottom.

Do NOT close or modify any parent issue.

<local-ticket-template>

# <NN> — <Ticket title>

**What to build:** the end-to-end behaviour this ticket makes work, from the user's perspective — not a layer-by-layer implementation list.

**Parent Delivery Acceptance references:** <stable parent references covered by this Ticket>

**Owned Cross-seam Invariants:** <invariant IDs or None; for each ID, reference the parent Contract and Proof without copying them>

**Adversarial Design:** <omit for STANDARD; for HIGH_RISK include Risk surface, Bounded model, Invariants, Adversarial cases, and Proof>

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

## Adversarial Design

Omit this section for `STANDARD`. For `HIGH_RISK`, include complete Risk surface, Bounded model, Invariants, Adversarial cases, and Proof fields.

## Acceptance criteria

- [ ] Criterion 1
- [ ] Criterion 2

## Blocked by

- A reference to each blocking ticket, or "None — can start immediately".

</issue-template>

In either form, avoid specific file paths or code snippets — they go stale fast. Exception: if a prototype produced a snippet that encodes a decision more precisely than prose can (state machine, reducer, schema, type shape), inline it and note briefly that it came from a prototype. Trim to the decision-rich parts — not a working demo, just the important bits.

After publication, return the parent Spec and Ticket references and tell the user they may explicitly invoke `$run-initiative`. Do not start that Workflow automatically.

## Forgeloop Shared Delivery Declaration

Keep three approved facts independent:

- Branch topology: `INDEPENDENT | SHARED`.
- Shared-branch reason: `WIDE_REFACTOR | NON_GREEN_MIGRATION | ATOMIC_DELIVERY | CUMULATIVE_AUDIT`.
- Integration policy: `auto-merge | human-merge`.

Every `SHARED` Spec uses one Spec Root Final Integration Gate. The Gate coordinates final validation and native integration; it is not a Ticket, Reviewer, Acceptance level, Event, state, or fact source. `CUMULATIVE_AUDIT` only extends legal SHARED reasons; it grants no merge authority and changes no other reason. Offer it only for a Spec with a native PR/MR runtime and at least two implementation Tickets. A single-Ticket cumulative delivery remains `INDEPENDENT`. Local does not offer this reason, while its other legal SHARED reasons remain available.

For any proposed `SHARED` topology, show this declaration with the complete Ticket and dependency drafts:

```text
Branch topology: SHARED
Shared-branch reason: <WIDE_REFACTOR | NON_GREEN_MIGRATION | ATOMIC_DELIVERY | CUMULATIVE_AUDIT>
Integration branch: <derived Spec branch>
Target: <declared target>
Final integration gate owner: SPEC_ROOT
Final delivery surface: <configured target integration>
```

Resolve every angle-bracket field before approval. For `CUMULATIVE_AUDIT`, the delivery surface must resolve to one native PR/MR for the Spec revision and target. Require one user approval for the declaration, Ticket bodies, blocking edges, risk classifications, and invariant ownership. Rejection keeps `INDEPENDENT`; `$run-initiative` never switches at runtime.

Do not draft a ceremony Ticket that only re-runs parent Validation Entries, owner Proofs, CI, PR/MR creation, or integration. When the final stage has independent implementation work, use an ordinary vertical Ticket and classify its real risk. Final validation reuses the parent Delivery Acceptance, Validation Entries, and existing invariant Owner Proofs without gaining ownership.

Return `FAILED_PRECONDITION` with zero Tracker writes for a legacy `Final integration owner` field, a missing `Final integration gate owner: SPEC_ROOT`, or a ceremony-only final Ticket. Do not parse, alias, migrate, or fall back to the old declaration.

## Forgeloop Acceptance Repair Mode

Enter this mode only when the user explicitly invokes `$to-tickets` with either formal input: an `ACCEPTANCE_RESULT` with `REPAIR_REQUIRED` and one stable `repair_key` per Finding; or a formal `RUN_PAUSED` from the Final Integration Gate with `finding_id`, evidence references, owning Scope, and stable `repair_key` for every Final Gate Finding. Read the owning Spec, applicable Initiative, final Commit or `delivery_head`, existing Open Tickets, and every Ticket carrying any key.

- Keep the approved parent contract, completed Tickets, and their Checkpoints unchanged. Return `CONTRACT_BLOCKER` instead of drafting repair Tickets when a Finding requires changing the Spec, `Delivery Acceptance`, Cross-seam Invariant, Proof mapping, ADR, Scope, Ticket Acceptance criteria, confirmed Initiative membership, Branch Topology, or target.
- Use the Spec as `owning_spec_ref` for Spec Acceptance or a Final Gate Finding. For Initiative Acceptance, route each repair slice to an existing member Spec whose approved Scope covers it. Never create a repair Ticket directly under the Initiative; return `CONTRACT_BLOCKER` when no member Spec can own the Finding.
- Query every key before drafting. Reuse the unique matching unfinished repair Ticket; stop on an ambiguous or conflicting key. Multiple keys may share a Ticket only when its body lists every key and the Findings form one atomic vertical slice.
- For unmatched keys, draft only the smallest vertical Tickets needed for the Findings; do not decompose the whole Spec again. When a Finding traces to a completed Ticket, record `source_ticket_ref` without reopening or modifying it.
- Record `owning_spec_ref`, applicable Initiative reference, source type, `repair_key`, `finding_id`, final Commit or `delivery_head`, observable repair checks, and genuine blockers in each repair Ticket. Keep it inside approved Scope.
- Preserve the normal user quiz and approval before idempotent publication. After an ambiguous write, query every `repair_key` and verify body and parent relation before retrying; never create a duplicate because the first response was uncertain.

This mode creates or reuses formal repair Tickets only after the user explicitly invokes `$to-tickets`. It does not resume `$run-initiative`; the user resumes the original Run separately after the Tracker work is valid.

## Forgeloop Spec Revision Reconciliation Mode

Enter this mode either when the user explicitly invokes `$to-tickets` for a formal Spec with a material new Revision and a paused Run, or when `$run-initiative` delegates an exactly read-back approval record and its complete reconciliation package. Read the previous and current Spec Revisions plus every existing child Ticket, including body, comments, status, parent, blockers, and existing Ticket Revision records.

- Preserve every Completed or Closed Ticket and its history unchanged.
- Compare the revised contract only with Open Tickets. Evaluate `retain`, `update`, `supersede`, and `create`, prefer `retain > update > supersede/create`, and form the smallest set of actions that reaches the approved target bodies and relationships.
- In explicit mode, present that set and obtain normal user approval before writing. In delegated mode, require every action and allowed equivalent outcome to be present in the approved package; do not quiz the user or request another approval.
- Reuse an Open Ticket when its delivery goal remains valid. Update only the approved contract fields and blockers. Create only missing vertical slices. Do not delete obsolete Open Tickets; mark them superseded and close them only when the current mode's approval explicitly includes that action.
- For an unfinished ceremony-only Ticket from the replaced shared-delivery protocol, mark it superseded, close it, and remove its native parent relation and blocking edges only after explicit user approval; in delegated mode, the bound package is that approval and must not be requested again. This is approved Tracker reconciliation, not runtime compatibility or automatic migration.
- Before every write, refresh the current Ticket and search for the approved target fact. Reuse a unique equivalent fact, perform the approved action only when its expected predecessor still holds, and stop when current facts exceed the approved equivalent boundary. If a write result is ambiguous, query and verify before retrying.
- Complete create and update actions, then all approved parent and blocking relationships, before reading back each affected Ticket's complete final facts. Only after that read-back render the complete Ticket Revision to a temporary file with a non-interpreting file-writing capability and append it through the configured file-backed Tracker operation; never place dynamic Revision text in an inline body/message argument, shell interpolation, or command substitution. Append or reuse one effective Ticket Revision binding the complete body, relationships, approval record, effective Spec/ADR Revisions, materiality judgment, and Repair Lineage. A missing prior Ticket Revision uses the approved pre-change facts as a baseline and does not reset repair budget.
- Query every successor of the same Ticket predecessor. Reuse equivalent successors and select the smallest immutable native Comment ID, Note ID, or Local append position as canonical; stop with `RECOVERY_CONFLICT` for different successors or missing, equal, or incomparable ordering. Intermediate Ticket states never become an effective Revision, enter the Frontier, reset budget, or certify a Candidate.
- Only a material Revision affecting this Ticket opens a new initial repair cycle; unrelated or non-material changes do not reset its budget, and a legitimately new Ticket preserves Repair Lineage so equivalent failed work cannot be hidden behind a new identity.
- Process obsolete Open Tickets only after every retained, updated, or created Ticket has its approved final facts and canonical effective Revision. Return a complete native read-back of the reconciled Ticket graph and Repair Lineage.
- Stop with `CONTRACT_BLOCKER` when reconciliation requires a different core Problem, Actor, delivery target, expanded Scope, Spec rewrite, ADR change, or Initiative membership change.

Do not modify the Spec, ADRs, parent Initiative, Completed Tickets, Run Claim, or Run checkpoints. This mode reconciles Tracker Tickets only; it does not resume `$run-initiative`. The Scheduler alone decides whether the fully reconciled Run remains paused or competes to resume.
