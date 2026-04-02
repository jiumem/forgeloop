---
name: run-planning
description: Top-level planning dispatcher. Use it to start, resume, or repair planning for one Initiative. It binds the requirement baseline or design draft, the `Planning State Doc`, and existing planning artifacts, then decides the next planning step.
---

# Run Planning

<!-- forgeloop:anchor background -->
## Background

The planning side uses one control spine plus one internal stage skill:

- `Supervisor` acts as the dispatcher and maintains the `Planning State Doc`
- `planner` and stage reviewers perform formal handoff inside stage-specific planning rolling docs
- `planning-loop` is the internal second-layer stage skill that handles exactly one confirmed planning stage per dispatch

The `Planning State Doc` control contract lives at `references/planning-state.md`.
The repo-local control-plane root contract lives at `../references/control-plane-roots.md`.

The default planning packet is anchor-addressed: authoritative refs first, doc-local selectors second, optional minimal slices third, and full-document fallback only on legality failure or cold-start recovery.
This minimal packet default is the planning-side law. Planning does not wait for a separate runtime-style cutover contract to become minimal-first.
Planning packets must remain self-sufficient for the current stage and round. Do not rely on previous-packet memory, packet hashes, or delta-only continuation assumptions.

<!-- forgeloop:anchor delegation-contract -->
## Delegation Contract

`run-planning` is a multi-agent dispatch skill.

If this skill has been invoked, treat that invocation itself as user authorization for the `Supervisor` to dispatch the required planning subagents through `planning-loop` for the current stage. Do not stop only to re-ask for ordinary planner / reviewer delegation.

If the current environment still prevents that downstream delegation, or if you will not actually continue with delegated planning execution in this activation, stop immediately and ask the user. Never treat that situation as permission for the `Supervisor` to continue by personally doing `planner` or stage-reviewer work.

<!-- forgeloop:anchor goal -->
## Goal

In this framework, you act as the planning-layer `Supervisor` dispatcher. Your job is to bind the Initiative, recover or update the minimum planning control plane, and keep driving the confirmed planning stages until planning reaches a formal stop. You do not write planning artifacts, review text, or runtime-execution state yourself.

You are responsible only for:

- binding the formal planning source paths for the current Initiative
- recovering the minimum planning control plane when the `Planning State Doc` is missing or distorted but planning truth is still recoverable
- determining the current active planning stage, or whether planning should stop
- updating the `Planning State Doc` when needed
- calling skill: `planning-loop` when the current planning stage should continue, then rereading state and explicitly rebinding the next stage when cross-stage routing says planning should keep advancing

You are not responsible for:

- writing any planning artifact body content
- writing any planning review body content
- deciding runtime admission or entering execution

`run-planning` is the planning-side top entry. `planning-loop` is its internal one-stage skill. When `planning-loop` records a cross-stage route, reread the `Planning State Doc`, explicitly bind the new active stage, and continue only from refreshed formal planning truth. Do not carry planning across stage boundaries on cached assumptions.

<!-- forgeloop:anchor dispatch-rules -->
## Dispatch Rules

Once the next planning step is clear, dispatch exactly one downstream skill for that decision point, or stop and ask the user. Sequential redispatch after `planning-loop` returns is allowed only after rereading the `Planning State Doc` and current planning truth; parallel dispatch and speculative skipped stages are forbidden.

The `Planning State Doc` holds only the minimum planning control plane: `current_snapshot`, `next_action`, `last_transition`, plus explicit waiting / blocked / sealed-output signals. Do not put planner or reviewer body content there, and do not create a second planning state model outside the formal planning artifacts, rolling docs, and the `Planning State Doc`.

<!-- forgeloop:anchor when-to-stop -->
## When To Stop Or Ask The User

- the requirement baseline or `design draft` is missing, illegal, or ambiguous
- the current Initiative or planning stage cannot be confirmed uniquely
- the `Planning State Doc` and planning artifacts conflict and the active stage, `planner_slot`, or stage `round` cannot be recovered uniquely
- the repository is missing the canonical stage reference or rolling-doc contract needed for the active stage
- the confirmed next planning step requires entering `planning-loop`, but the required downstream planner / reviewer delegation is unavailable, blocked, or will not actually be performed in this activation
- planning is already in `sealed_planning_docs_ready`, or it is in a waiting / blocked stop state that this activation does not clearly resolve

<!-- forgeloop:anchor main-flow -->
## Main Flow

### Step 1: Bind Input

First bind the formal planning sources for the current Initiative.

1. Use the user-provided requirement baseline, `design draft`, planning `artifact_ref`, `planning_state_doc_ref`, `initiative_key`, or the only verifiable active planning object in the current workspace to bind the current Initiative. If it cannot be verified uniquely, ask the user.
2. When the bound Initiative is represented by a repo-local planning artifact, derive the one legal planning control-plane root from `../references/control-plane-roots.md`: sibling `.forgeloop/` under the Initiative document directory. Bind `planning-state.md`, `design-rolling.md`, `gap-rolling.md`, and `plan-rolling.md` there directly. Do not search for alternate repo-local planning control-plane roots elsewhere in the repository.
3. Read the `Planning State Doc` first when it exists.
4. Read only the minimum planning artifacts and planning rolling docs needed to confirm the active stage.
5. If the active stage is already bound or the `Planning State Doc` looks distorted, read the active planning rolling doc deeply enough to recover `planner_slot` and the stage `round` when they already exist.
6. If downstream routing depends on `Gap Analysis Requirement`, read the sealed `Design Doc` directly rather than inferring from loose Initiative labels.
7. If there is no `Planning State Doc`, you may still continue only when the current planning stage can be recovered uniquely from the requirement baseline, current planning artifacts, and the canonical planning rolling docs under that same Initiative-local `.forgeloop/` root.

### Step 2: Determine The Current Planning Next Step

After reading the formal planning sources, decide whether planning should enter `planning-loop`, continue after a returned cross-stage route, stop, or ask the user.

1. If no `Planning State Doc` exists and no planning artifact or rolling doc exists yet, treat the case as a cold planning start at `Design Doc`.
2. If the `Planning State Doc` already records `sealed_planning_docs_ready`, stop at that state.
3. If the `Planning State Doc` already records `waiting` or `blocked`, first check whether this activation clearly resolves that stop reason:
- if not, stop at that state
- if yes, record that resume in `last_transition`, then continue from formal planning truth instead of treating the stop as terminal
4. Treat the `Planning State Doc` plus the active planning rolling doc as formal stage truth. Artifact prose status may help human reading, but it must not override rolling state. If the `Planning State Doc` is missing, or if it conflicts with newer planning artifacts or rolling docs, first try to recover the minimum planning control plane directly from formal planning truth instead of stopping immediately.
5. Recover state only when one active stage, one `planner_slot`, and one stage `round` can be proven.
- If the existing `Planning State Doc` is still consistent, preserve `planner_slot` and `round`.
- If it is missing or stale, recover them from the active rolling doc.
- If this is a fresh cross-stage entry and no rolling doc exists yet, bind only the target stage and paths here; let `planning-loop` initialize `planner_slot=planner` and `round=1`.
- If any of `stage`, `planner_slot`, or `round` still has multiple legal answers, stop and ask the user.
6. Once state is consistent, decide the route.
- Resolved `waiting` / `blocked`: clear the stop state, rewrite the minimum `Planning State Doc`, and continue.
- Recorded `advance_*` or `reopen_*`: bind the target stage, keep the route in `last_transition`, and enter `planning-loop` in the same activation after state refresh.
- Existing in-stage repair / reviewer handoff / review-result state: keep the same stage and enter `planning-loop`.
- Recovered active stage from artifact + rolling doc: rewrite the minimum `Planning State Doc` around that stage and continue.
7. If the stage cannot be recovered uniquely, or the planning sources conflict in a way that no single stage can legally be chosen, stop and ask the user.

### Step 3: Update The Minimum Planning Control Plane

Before dispatching, make the active planning stage explicit in the `Planning State Doc`.

1. `Planning State Doc` is the only planning control spine. `current_snapshot` carries the bound Initiative, active stage, active `artifact_ref`, active `rolling_doc_ref`, and when known `planner_slot` plus `round`; `next_action` carries only the current planning route or stop signal; `last_transition` carries only the most recent bind, recovery, resume, reopen, or cross-stage routing fact.
2. When resuming an existing stage, preserve `planner_slot` and stage `round`, and write them back immediately when recovery has already proved them.
3. Only a fresh stage with no rolling doc may omit them temporarily; once a stage is in flight and either value is known, `planning-loop` or recovery must write `planner_slot=planner` and the current `round` back into `current_snapshot`.
4. `next_action` records entry into `planning-loop` for the bound stage.
5. `last_transition` records cold start, recovery, rebind, reopen, or resume.
6. If the route is `reopen_to_design` or `reopen_to_gap_analysis`, stay visible as a reopen route in `last_transition`.
7. If the `Planning State Doc` does not exist, initialize only `current_snapshot`, `next_action`, and `last_transition`.

### Step 4: Dispatch The Internal Stage Skill

Call skill: `planning-loop` only after the active planning stage is explicit.

1. `planning-loop` owns the current stage's authoring, review handoff, review-result handling, and stage routing until it reaches a formal stop point.
2. Do not dispatch `planner` or any planning reviewer directly from `run-planning`.
3. Do not restate stage-specific reference contracts here; `planning-loop` owns that layer.

### Step 5: Handle Returned Planning State

After `planning-loop` returns, reread the `Planning State Doc`.

1. If the returned state is `waiting`, `blocked`, or `sealed_planning_docs_ready`, stop.
2. If the returned state records a cross-stage route, reread the `Planning State Doc` and the minimum formal planning truth needed for that route, explicitly bind the target stage from `last_transition`, then go back to Step 2 in the same activation.
3. If the returned state no longer exposes one legal stop point or one recoverable active stage, stop and surface the illegal planning state explicitly.

### Step 6: Loop Back

Keep returning to Step 2 after each completed `planning-loop` dispatch until one of these stop points appears:

- `waiting`
- `blocked`
- `sealed_planning_docs_ready`
- irrecoverable ambiguity that must be surfaced to the user

<!-- forgeloop:anchor red-lines -->
## Red Lines

Never:

- dispatch `planner`, `design_reviewer`, `gap_reviewer`, or `plan_reviewer` directly from this skill
- treat inability or unwillingness to continue with the required delegated planning execution as permission for a single-agent fallback
- continue from one planning stage into the next without rereading the `Planning State Doc` and explicitly rebinding from current formal truth
- overwrite a still-valid `planner_slot` or stage `round` with thinner stage-only state
- guess the active planning stage, `planner_slot`, or current round when formal planning truth does not expose one unique answer
- re-decide `Gap Analysis Requirement` from chat summaries or loose Initiative labels after the sealed `Design Doc` exists
- create a second planning truth source outside the formal planning artifacts, planning rolling docs, and the `Planning State Doc`

<!-- forgeloop:anchor completion-criteria -->
## Completion Criteria

After a correct `run-planning` activation, all of the following should be true:

- the current Initiative is bound uniquely
- the next planning step or stop point is unambiguous
- if the active planning stage was already in flight, `planner_slot` and stage `round` continuity remain unambiguous
- if planning continues, each active stage has been bound explicitly before dispatch to the internal `planning-loop`
- if planning stops, the stop reason is explicit in the `Planning State Doc`
- one activation may legally advance across multiple planning stages, but only through reread plus explicit rebind between stages
- no new planning truth source exists outside the formal planning docs, planning rolling docs, and the `Planning State Doc`
