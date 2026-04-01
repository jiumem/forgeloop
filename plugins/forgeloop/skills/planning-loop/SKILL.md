---
name: planning-loop
description: Internal planning stage skill used by `run-planning` when one confirmed stage needs formal authoring or repair of a `Design Doc`, optional `Gap Analysis Doc`, or `Total Task Doc`; this skill dispatches the `planner` for the active planning stage and maintains the minimum planning control plane
---

# Planning Loop

<!-- forgeloop:anchor role -->
`planning-loop` is the internal planning-stage skill under `run-planning`. It handles one confirmed planning stage for one Initiative. Here you act as the planning-stage `Supervisor`: maintain the minimum control plane, keep one `planner_slot`, dispatch the same `planner` across authoring rounds, and decide only whether the current stage should continue repair, hand off for review, escalate for judgment, or stop.

This skill is single-stage per dispatch. If a clean review routes the Initiative to another planning stage, write that cross-stage route into the `Planning State Doc`, stop, and let the next `run-planning` activation bind the new active stage explicitly. Do not continue across stage boundaries inside the same activation.

This v0 skill establishes the formal dispatch surface for `planner`, `design_reviewer`, `gap_reviewer`, and `plan_reviewer`.

<!-- forgeloop:anchor stage-reference-binding -->
## Stage Reference Binding

Each planning stage must bind exactly one canonical `stage_reference_ref`.

- `Design Doc` -> `references/design-doc.md`
- `Gap Analysis Doc` -> `references/gap-analysis.md`
- `Total Task Doc` -> `references/total-task-doc.md`

The formal value of `stage_reference_ref` should be a path relative to the current skill root. Do not store it as a shell-cwd-relative path or a repository-root-relative path. If a concrete dispatch mechanism needs an absolute filesystem path at send time, it may materialize one from the same canonical skill-root-relative ref, but the rolling doc contract should keep the skill-root-relative form as the durable truth.

`stage_reference_ref` belongs to the active planning rolling doc's contract snapshot, not to the `Planning State Doc`.

The active rolling doc contract snapshot is the formal bridge between the workflow layer and subagents. `planner` and the current stage reviewer must receive `stage_reference_ref` explicitly in every dispatch packet; they must not rely on discovering references from directory layout or session memory.

<!-- forgeloop:anchor shared-rolling-doc-contract -->
## Shared Rolling Doc Contract

Every planning stage also binds the same canonical `rolling_doc_contract_ref`.

- shared planning rolling-doc contract -> `references/planning-rolling-doc.md`

The formal value of `rolling_doc_contract_ref` should be a path relative to the current skill root.

`rolling_doc_contract_ref` belongs to the active planning rolling doc's contract snapshot, not to the `Planning State Doc`.

The stage reference controls artifact shape and stage-local judgment. The shared rolling-doc contract controls communication-plane shape, block legality, round law, handoff law, and stale-result handling.

<!-- forgeloop:anchor stage-reviewer-binding -->
## Stage Reviewer Binding

- `Design Doc` -> `design_reviewer`
- `Gap Analysis Doc` -> `gap_reviewer`
- `Total Task Doc` -> `plan_reviewer`

<!-- forgeloop:anchor stage-local-vocabulary -->
## Stage-Local Vocabulary

- `Design Doc` uses handoff block `design_doc_ref`, review-result block `design_review_result`, and same-stage repair action `continue_design_repair`
- `Gap Analysis Doc` uses handoff block `gap_analysis_ref`, review-result block `gap_review_result`, and same-stage repair action `continue_gap_repair`
- `Total Task Doc` uses handoff block `total_task_doc_ref`, review-result block `plan_review_result`, and same-stage repair action `continue_plan_repair`

<!-- forgeloop:anchor truth-sources-boundaries -->
## Truth Sources And Hard Boundaries

The formal planning input surface contains only:

- the current requirement baseline or `design draft`
- the `Planning State Doc`
- the active planning rolling doc for the current stage
- the current formal planning artifact, if it already exists
- any already sealed upstream planning artifacts for the same Initiative
- repo facts, implementation facts, constraint facts, and the stage-specific reference required by the current stage
- the shared anchor-addressing contract at `../references/anchor-addressing.md`

Hard boundaries:

- only `planner` may write the current planning artifact and append planner-owned blocks to the active planning rolling doc
- `planning-loop` may update only the `Planning State Doc`, plus rolling-doc header / contract-snapshot initialization when the current stage rolling doc does not yet exist
- do not write review body text, code, or runtime control-plane state from this skill
- if the active stage, active artifact, or active owner changes, record that transition in the `Planning State Doc`
- if the active planning rolling doc does not exist, initialize only the header, including object identity and `planner_slot`, plus `planning_contract_snapshot`
- on first entry into a stage with no rolling doc yet, initialize the stage as `planner_slot=planner` and `round=1` before the first `planner` dispatch
- if `last_transition` records a reopen into the current stage, preserve or recover the existing `planner_slot` and open the next stage-local round instead of resuming the previously sealed round
- `planning_contract_snapshot` must include at least: `stage`, `artifact_ref`, `stage_reference_ref`, `rolling_doc_contract_ref`, and the relevant upstream planning artifact refs
- every `planner` dispatch and every formalized stage-reviewer dispatch must carry the same bound `stage_reference_ref` and `rolling_doc_contract_ref` explicitly
- every planning dispatch packet must also carry the doc-local anchor selectors needed for the current consumer, and may inline only the minimal slices rebuilt from those same authoritative refs
- if any selector is missing, duplicated, or otherwise illegal, planning dispatch must promote that read to an explicit full-document fallback instead of guessing
- planning packets must stay self-sufficient for the current stage and round; do not send or rely on delta-only packets that require a previous packet to reconstruct legality
- `Gap Analysis Requirement` becomes single-source planning truth only after `Design Doc` seals; once sealed, downstream planning must route from that line instead of re-inferring requirement from chat memory or loose Initiative labels
- if the planning inputs conflict or the current stage cannot be confirmed uniquely, stop and ask for clarification instead of improvising a new planning object

<!-- forgeloop:anchor workflow -->
## Workflow

1. Bind the current planning stage
- Read the requirement or `design draft`, the `Planning State Doc`, the active planning rolling doc when it exists, the current stage artifact when it exists, and the minimum repo facts needed to confirm the stage boundary
- Bind the canonical `stage_reference_ref` for the active stage before dispatch
- Bind the canonical `rolling_doc_contract_ref` before dispatch
- Confirm that the Initiative and active stage are unique, the formal artifact path is known, the rolling doc path is known or can be initialized uniquely, `stage_reference_ref` is uniquely confirmed, and `rolling_doc_contract_ref` is uniquely confirmed
- If the active planning rolling doc already exists, also confirm that `planner_slot` is unique and the current stage-local `round` is unique
- If the active planning rolling doc does not yet exist, it is legal to initialize the stage here with `planner_slot=planner` and `round=1`
- If `last_transition` records an explicit reopen into this stage, recover `planner_slot` from the rolling doc when possible and open the next integer `round` instead of resuming the previously sealed round
- If the active stage has no canonical stage reference formalized in the repository yet, stop and surface that blocker explicitly
- If the `Planning State Doc` conflicts with the rolling doc, the active artifact, the bound `stage_reference_ref`, or the bound `rolling_doc_contract_ref`, stop and hand control back to the caller
- If the rolling doc does not exist, initialize only the header, including object identity and `planner_slot`, plus `planning_contract_snapshot`; write `planner_slot=planner` into the header and `current_snapshot`, and write `round=1` into the `Planning State Doc` before dispatching `planner`

2. Update the minimum planning control plane
- `current_snapshot` points to the current Initiative, active stage, active artifact path, rolling doc path, `planner_slot`, and the current stage-local `round`; on first entry into a fresh stage with no prior rolling doc, use `planner_slot=planner` and `round=1`
- `next_action` must stay inside the formal planning-stage state space for this Initiative: planner repair, reviewer handoff, supervisor routing between planning stages, sealed planning output, or waiting / blocked stop states
- `last_transition` records entering, resuming, or reassigning the current planning stage when needed
- `round` is stage-local and supervisor-owned through the `Planning State Doc`; `planner` and reviewers only echo it in the rolling doc and must not advance it on their own
- open a new round only when entering a stage for the first time, re-entering the same stage after review-requested changes, or reopening an earlier sealed stage; determine reopen from the durable transition already recorded in the `Planning State Doc`, not from chat memory
- Do not write planner body text into the `Planning State Doc`

3. Dispatch the `planner`
- Keep only one logical `planner_slot` for the current planning stage
- Reuse the same `planner` thread when possible; if the physical thread is lost, you may assign a successor agent but must preserve the same `planner_slot`
- Default to `fork_context=false`
- The planner input must explicitly carry: active stage identity, requirement or `design draft`, the `Planning State Doc` path, the active planning rolling doc path, the current artifact path, the current `round`, the bound `stage_reference_ref`, the bound `rolling_doc_contract_ref`, the anchor selectors for the exact planning-artifact and rolling-doc surfaces needed in the round, and any sealed upstream planning artifacts
- The planner reads artifact-shape rules from `stage_reference_ref`, communication-plane rules from `rolling_doc_contract_ref`, and selector legality from `../references/anchor-addressing.md`; do not inline or restate the full reference text in the dispatch packet unless a referenced file is missing, unreadable, or has promoted to explicit full-document fallback

4. Handle the planner result
- Decide only from the active planning rolling doc and formal planning artifacts, not from chat summaries
- The latest `planner_update` in the current round is the current planner intent
- The current reviewer handoff is the latest stage-local handoff block for the current round
- A review result is actionable only when its `round`, `handoff_id`, and `review_target_ref` match that current handoff exactly; stale or mismatched review results remain history and must not drive routing
- If the latest `planner_update` carries `next_action=continue_stage_repair`, keep the same `planner_slot`, map the `Planning State Doc` back to the current stage's repair action, and continue in the same round
- If the latest `planner_update` carries `next_action=request_reviewer_handoff`, the rolling doc must expose one unique current handoff for the same round; if it does, switch `next_action` to reviewer handoff and dispatch the reviewer bound to the current stage with the same `stage_reference_ref`, the same `rolling_doc_contract_ref`, the current `round`, the current `handoff_id`, the current `review_target_ref`, and the selectors for the exact artifact and rolling-doc slices under review
- If the latest `planner_update` carries `next_action=wait_for_upstream_judgment`, update the `Planning State Doc` to a waiting stop state, then stop
- If the latest `planner_update` carries `next_action=stop_on_blocker`, update the `Planning State Doc` to a blocked stop state, then stop
- If the latest `planner_update` uses any other control intent, or tries to drive reviewer dispatch without both `next_action=request_reviewer_handoff` and one unique current handoff block, stop and surface the illegal planner output explicitly

5. Handle the current stage reviewer result
- Decide only from the active stage rolling doc and the formal stage artifact, not from chat summaries
- The current actionable review result is the latest matching stage-local review-result block for the current handoff
- Stop and surface illegal review output explicitly if the rolling doc does not expose one unique actionable review result, if `Design Doc` review emits `upstream_reopen_recommendation`, if `Gap Analysis Doc` review targets any reopen stage other than `Design Doc`, if `Total Task Doc` review targets any reopen stage other than `Design Doc` or `Gap Analysis Doc`, or if `verdict`, `seal_status`, and `next_action` do not form one legal combination below
- Clean sealed result:
  - `Design Doc`: require `verdict=clean`, `seal_status=sealed`, and `next_action=ready_for_supervisor_routing`; keep the sealed `Design Doc` as stage truth, read the explicit `Gap Analysis Requirement` from that sealed document, switch `next_action` to `advance_to_gap_analysis` when it is `required`, otherwise `advance_to_total_task_doc`, then stop so the next `run-planning` activation can bind the next stage explicitly
  - `Gap Analysis Doc`: require `verdict=clean`, `seal_status=sealed`, and `next_action=ready_for_supervisor_routing`; keep the sealed `Gap Analysis Doc` as stage truth, switch `next_action` to `advance_to_total_task_doc`, then stop
  - `Total Task Doc`: require `verdict=clean`, `seal_status=sealed`, and `next_action=ready_for_supervisor_routing`; switch `next_action` to `sealed_planning_docs_ready`, update the `Planning State Doc` to a sealed-planning-output stop state, then stop
- Upstream reopen recommendation:
  - `Gap Analysis Doc`: when the actionable result has `verdict=changes_requested`, `seal_status=not_sealed`, a review-local stop action of `wait_for_upstream_judgment` or `stop_on_blocker`, and `upstream_reopen_recommendation.target_stage=Design Doc`, treat the reopen recommendation as the routing signal, switch `next_action` to `reopen_to_design`, record that cross-stage reopen route in the `Planning State Doc`, then stop
  - `Total Task Doc`: when the actionable result has `verdict=changes_requested`, `seal_status=not_sealed`, a review-local stop action of `wait_for_upstream_judgment` or `stop_on_blocker`, and `upstream_reopen_recommendation.target_stage=Gap Analysis Doc` or `Design Doc`, treat the reopen recommendation as the routing signal, switch `next_action` to `reopen_to_gap_analysis` or `reopen_to_design`, record that cross-stage reopen route in the `Planning State Doc`, then stop
- Same-stage repair: when the actionable result has `verdict=changes_requested`, `seal_status=not_sealed`, and the current stage's repair action, increment the stage-local `round` in the `Planning State Doc`, switch `next_action` back to that repair action, keep the same `planner_slot`, and continue
- Waiting or blocked stop:
  - when the actionable result has `verdict=changes_requested`, `seal_status=not_sealed`, and `next_action=wait_for_upstream_judgment`, update the `Planning State Doc` to a waiting stop state, then stop
  - when the actionable result has `verdict=changes_requested`, `seal_status=not_sealed`, and `next_action=stop_on_blocker`, update the `Planning State Doc` to a blocked stop state, then stop
- If the sealed `Design Doc` lacks an explicit `Gap Analysis Requirement` line when clean seal routing depends on it, stop and surface the illegal stage truth explicitly instead of inferring route intent

<!-- forgeloop:anchor stop-conditions -->
## Stop Conditions

Stop immediately and hand control back upstream or to the user when:

- the active planning stage cannot be confirmed uniquely
- the requirement, `design draft`, or required upstream planning artifacts are missing
- the active stage has no canonical `stage_reference_ref`
- the active stage has no canonical `rolling_doc_contract_ref`
- the `Planning State Doc` conflicts with the active rolling doc, current artifact, bound `stage_reference_ref`, or bound `rolling_doc_contract_ref`
- the current stage-local `round` or current open `handoff_id` cannot be confirmed uniquely
- the sealed `Design Doc` lacks an explicit `Gap Analysis Requirement` line when downstream routing depends on it
- the current stage requires a reviewer contract that is not yet formalized in the repository
- the planner exposes a real blocker or requests explicit human judgment

<!-- forgeloop:anchor red-lines -->
## Red Lines

Never:

- dispatch multiple planners concurrently for the same planning stage
- let `planner` or a reviewer discover the stage reference implicitly from folder layout instead of receiving `stage_reference_ref` explicitly
- let `planner` or a reviewer discover the shared rolling-doc contract implicitly from folder layout or memory instead of receiving or binding `rolling_doc_contract_ref`
- let this skill write planner body content into the rolling doc
- re-decide `Gap Analysis Requirement` from chat summaries or loose Initiative labels after `Design Doc` has sealed it
- treat a stale or mismatched review result as the current stage truth
- invent a reviewer contract that does not exist in the repository
- continue into runtime execution from this skill
- create a second planning state model outside the `Planning State Doc` and active planning rolling doc

<!-- forgeloop:anchor completion-criteria -->
## Completion Criteria

On correct completion, all of the following should be true:

- the current planning stage can be recovered uniquely from the `Planning State Doc` and active planning rolling doc
- `planner_slot` continuity is unambiguous
- stage-local `round` continuity is unambiguous
- the current rolling doc contract snapshot binds one unambiguous `stage_reference_ref` and one unambiguous `rolling_doc_contract_ref`
- the current actionable `handoff_id` can be recovered uniquely whenever the stage is in reviewer handoff or review-result state
- the current artifact is either still in repair, formally ready for review handoff, explicitly stopped on upstream judgment, stopped on an explicit cross-stage route to the next planning stage, or formally sealed as planning output
- no second planning truth source has been created outside the formal planning docs
