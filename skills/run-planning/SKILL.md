---
name: run-planning
description: Use when the user asks to create, continue, repair, or resume formal planning for an Initiative; this is the planning-side top entry and uses the requirement baseline or design draft, the Planning State Doc, and current planning artifacts to determine the current planning next step
---

# Run Planning

## Background

The planning side uses one control spine plus one internal stage skill:

- `Supervisor` acts as the dispatcher and maintains the `Planning State Doc`
- `planner` and stage reviewers perform formal handoff inside stage-specific planning rolling docs
- `planning-loop` is the internal second-layer stage skill that handles exactly one confirmed planning stage per dispatch

## Goal

In this framework, you act as the planning-layer `Supervisor` dispatcher. You are responsible only for:

- binding the formal planning source paths for the current Initiative
- recovering the minimum planning control plane when the `Planning State Doc` is missing or distorted but planning truth is still recoverable
- determining the current active planning stage, or whether planning should stop
- updating the `Planning State Doc` when needed
- calling skill: `planning-loop` when the current planning stage should continue

You are not responsible for:

- writing any planning artifact body content
- writing any planning review body content
- deciding runtime admission or entering execution

## Core Rule

You decide only the current planning next step. You do not author planning docs or formal review text yourself.

`run-planning` is the planning-side top entry. `planning-loop` is its internal one-stage skill. Once `planning-loop` records a cross-stage route, stop there and let the next `run-planning` activation bind the new active stage explicitly. Do not carry planning across stage boundaries inside one activation.

## Dispatch Rules

Once the current planning next step is clear, either call skill: `planning-loop`, or stop and ask the user. Only one skill may be called at a time.

The `Planning State Doc` holds only the minimum planning control plane: `current_snapshot`, `next_action`, `last_transition`, plus explicit waiting / blocked / sealed-output signals. Do not put planner or reviewer body content there, and do not create a second planning state model outside the formal planning artifacts, rolling docs, and the `Planning State Doc`.

## When To Stop Or Ask The User

- the requirement baseline or `design draft` is missing, illegal, or ambiguous
- the current Initiative or planning stage cannot be confirmed uniquely
- the `Planning State Doc` and planning artifacts conflict and the active stage, `planner_slot`, or current stage-local `round` cannot be recovered uniquely
- the repository is missing the canonical stage reference or rolling-doc contract needed for the active stage
- planning is already in `sealed_planning_docs_ready`, or it is in a waiting / blocked stop state that this activation does not clearly resolve

## Main Flow

### Step 1: Bind Input

First bind the formal planning sources for the current Initiative.

1. Use the user-provided requirement baseline, `design draft`, planning artifact path, planning state path, `initiative_key`, or the only verifiable active planning object in the current workspace to bind the current Initiative. If it cannot be verified uniquely, ask the user directly.
2. Read the `Planning State Doc` first when it exists.
3. Read only the minimum current planning artifacts and planning rolling docs needed to confirm the current active stage.
4. If the current stage is already active or the `Planning State Doc` looks distorted, read the active planning rolling doc deeply enough to recover the current `planner_slot` and current stage-local `round` when they already exist.
5. If downstream routing depends on `Gap Analysis Requirement`, read the sealed `Design Doc` directly rather than inferring from loose Initiative labels.
6. If there is no `Planning State Doc`, you may still continue only when the current planning stage can be recovered uniquely from the requirement baseline, current planning artifacts, and planning rolling docs.

### Step 2: Determine The Current Planning Next Step

After reading the formal planning sources, decide whether planning should enter `planning-loop`, stop, or ask the user.

1. If no `Planning State Doc` exists and no planning artifact or rolling doc exists yet, treat the case as a cold planning start at `Design Doc`.
2. If the `Planning State Doc` already records `sealed_planning_docs_ready`, stop at that state.
3. If the `Planning State Doc` already records `waiting` or `blocked`, first check whether this activation clearly resolves that stop reason:
- if not, stop at that state
- if yes, record that resume in `last_transition`, then continue from formal planning truth instead of treating the stop as terminal
4. If the `Planning State Doc` is missing, or if it conflicts with newer planning artifacts or rolling docs, first try to recover the minimum planning control plane directly from formal planning truth instead of stopping immediately.
5. You may recover planning state only when one active stage is unique and its control-plane continuity is also unique:
- preserve the existing `planner_slot` and current stage-local `round` whenever the `Planning State Doc` is still consistent with newer planning facts
- if the `Planning State Doc` is missing or distorted, recover the current `planner_slot` and current stage-local `round` from the active planning rolling doc when that rolling doc exposes them uniquely
- if the recovered state is a fresh cross-stage entry into a stage whose rolling doc does not yet exist, bind only the target stage, artifact path, and rolling doc path here; `planning-loop` will open that stage's `planner_slot` and first round during stage initialization
- if the active stage, `planner_slot`, or current round still cannot be confirmed uniquely, stop and ask the user directly
6. Once the control plane is consistent or has been recovered, determine the current planning next step:
- if this activation resolves a prior `waiting` or `blocked` stop and one active stage is now recoverable uniquely, rewrite the minimum `Planning State Doc` around that stage, clear the stop state, and continue
- if the `Planning State Doc` records a cross-stage route such as `advance_to_gap_analysis`, `advance_to_total_task_doc`, `reopen_to_design`, or `reopen_to_gap_analysis`, re-bind the target stage explicitly, preserve that route in `last_transition`, and set `next_action` to entering `planning-loop`; a `reopen_*` route must stay visible as a reopen route, not collapse into an ordinary resume
- if the `Planning State Doc` already records an active stage in repair, reviewer handoff, or review-result state, keep that stage and set `next_action` to entering `planning-loop`
- if the `Planning State Doc` was missing but one active planning stage was recovered uniquely from the current planning artifact and rolling doc, initialize or rewrite the minimum `Planning State Doc` around that recovered stage and continue
7. If the stage cannot be recovered uniquely, or the planning sources conflict in a way that no single stage can legally be chosen, stop and ask the user directly.

### Step 3: Update The Minimum Planning Control Plane

Before dispatching, make the active planning stage explicit in the `Planning State Doc`.

1. `current_snapshot` points to the current Initiative, active planning stage, active artifact path, and rolling doc path.
2. When the current stage is already active or has been recovered from an existing rolling doc, `current_snapshot` must also preserve the active `planner_slot` and current stage-local `round`; do not overwrite them with thinner state.
3. Only on first entry into a fresh stage with no rolling doc yet may `current_snapshot` temporarily omit `planner_slot` and `round`; `planning-loop` must then initialize them as `planner_slot=planner` and stage-local `round=1` before dispatching `planner`.
4. `next_action` points to entering `planning-loop` for the current active stage.
5. `last_transition` records cold start, recovery, stage re-bind, reopen, or resume when needed.
6. When the current entry came from `reopen_to_design` or `reopen_to_gap_analysis`, keep that reopen meaning in `last_transition` so `planning-loop` opens the next round rather than resuming the previously sealed one.
7. If the `Planning State Doc` does not exist yet, initialize only the minimum control-plane blocks needed for continuation: `current_snapshot`, `next_action`, and `last_transition`.
8. Do not write planning artifact body content or review body content into the `Planning State Doc`.

### Step 4: Dispatch The Internal Stage Skill

Call skill: `planning-loop` only after the active planning stage is explicit.

1. `planning-loop` owns the current stage's authoring, review handoff, review-result handling, and stage-local routing until it reaches a formal stop point.
2. Do not dispatch `planner` or any planning reviewer directly from `run-planning`.
3. Do not restate stage-specific reference contracts here; `planning-loop` owns that layer.

### Step 5: Handle Returned Planning State

After `planning-loop` returns, reread the `Planning State Doc`.

1. If the returned state is `waiting`, `blocked`, or `sealed_planning_docs_ready`, stop.
2. If the returned state records a cross-stage route, stop and let the next `run-planning` activation bind the new stage explicitly.
3. If the returned state no longer exposes one legal stop point or one recoverable active stage, stop and surface the illegal planning state explicitly.

## Red Lines

Never:

- dispatch `planner`, `design_reviewer`, `gap_reviewer`, or `plan_reviewer` directly from this skill
- silently continue from one planning stage into the next after `planning-loop` has already recorded a cross-stage route
- overwrite a still-valid `planner_slot` or current stage-local `round` with thinner stage-only state
- guess the active planning stage, `planner_slot`, or current round when formal planning truth does not expose one unique answer
- write planning artifact body text or review body text into the `Planning State Doc`
- re-decide `Gap Analysis Requirement` from chat summaries or loose Initiative labels after the sealed `Design Doc` exists
- create a second planning truth source outside the formal planning artifacts, planning rolling docs, and the `Planning State Doc`
- continue into runtime execution from this skill

## Completion Criteria

After a correct `run-planning` activation, all of the following should be true:

- the current Initiative is bound uniquely
- the current planning next step or stop point is unambiguous
- if the active planning stage was already in flight, `planner_slot` and current stage-local `round` continuity remain unambiguous
- if planning continues, one active stage has been bound explicitly and dispatched to the internal `planning-loop`
- if planning stops, the stop reason or cross-stage route is explicit in the `Planning State Doc`
- no new planning truth source exists outside the formal planning docs, planning rolling docs, and the `Planning State Doc`
