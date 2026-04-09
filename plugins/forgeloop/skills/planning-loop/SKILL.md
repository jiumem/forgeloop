---
name: planning-loop
description: Internal planning stage skill used by `run-planning` when one confirmed stage needs formal authoring or repair of a `Design Doc`, optional `Gap Analysis Doc`, or `Total Task Doc`; this skill dispatches the `planner` for the active planning stage and maintains the minimum planning control plane
---

# Planning Loop

<!-- forgeloop:anchor role -->
`planning-loop` is the one-stage planning executor under `run-planning`.

You act as the stage `Supervisor`: keep the minimum control plane, preserve one durable `planner_slot`, maintain one session-local reusable `planner` binding plus one session-local reusable stage-reviewer binding for the current stage, and route only within the current stage.

If review sends the Initiative to another planning stage, record that cross-stage route in the `Planning State Doc` and stop. `run-planning` must then reread state, explicitly bind the new stage, and decide whether to continue in the same activation.

<!-- forgeloop:anchor stage-reference-binding -->
## Stage Reference Binding

Each planning stage must bind exactly one canonical `stage_reference_ref`.

- `Design Doc` -> `plugins/forgeloop/skills/planning-loop/references/design-doc.md`
- `Gap Analysis Doc` -> `plugins/forgeloop/skills/planning-loop/references/gap-analysis.md`
- `Total Task Doc` -> `plugins/forgeloop/skills/planning-loop/references/total-task-doc.md`

Bind `stage_reference_ref` as a repo-root-relative path. Materialize an absolute path only at dispatch time when needed. Keep the repo-root-relative form as the durable truth in the rolling-doc contract snapshot.

`stage_reference_ref` belongs to the active planning rolling doc's contract snapshot, not to the `Planning State Doc`.

The active rolling doc contract snapshot is the formal bridge between the workflow layer and subagents. `planner` and the current stage reviewer must receive `stage_reference_ref` explicitly in every dispatch packet; they must not rely on discovering references from directory layout or session memory.

<!-- forgeloop:anchor shared-rolling-doc-contract -->
## Shared Rolling Doc Contract

Every planning stage also binds the same canonical `rolling_doc_contract_ref`.

- shared planning rolling-doc contract -> `plugins/forgeloop/skills/planning-loop/references/planning-rolling-doc.md`

Bind `rolling_doc_contract_ref` the same way: repo-root-relative as durable truth, absolute only as an ephemeral dispatch value.

`rolling_doc_contract_ref` belongs to the active planning rolling doc's contract snapshot, not to the `Planning State Doc`.

The stage reference controls artifact shape and stage judgment. The shared rolling-doc contract controls communication-plane shape, block legality, round law, handoff law, and stale-result handling.
Framework contract refs and Initiative repo refs follow the same durable-path rule: repo-root-relative. Do not persist workspace-specific absolute paths in planning truth.

<!-- forgeloop:anchor stage-reviewer-binding -->
## Stage Reviewer Binding

- `Design Doc` -> `design_reviewer`
- `Gap Analysis Doc` -> `gap_reviewer`
- `Total Task Doc` -> `total_task_doc_reviewer`

<!-- forgeloop:anchor stage-local-vocabulary -->
## Stage-Local Vocabulary

- `Design Doc` uses handoff block `design_doc_ref`, review-result block `design_review_result`, and same-stage repair action `continue_design_repair`
- `Gap Analysis Doc` uses handoff block `gap_analysis_ref`, review-result block `gap_review_result`, and same-stage repair action `continue_gap_repair`
- `Total Task Doc` uses handoff block `total_task_doc_ref`, review-result block `total_task_doc_review_result`, and same-stage repair action `continue_total_task_doc_repair`

<!-- forgeloop:anchor truth-sources-boundaries -->
## Truth Sources And Hard Boundaries

The formal planning input surface is limited to the requirement baseline or design draft, the `Planning State Doc`, the active rolling doc, the current artifact when it exists, sealed upstream planning artifacts, relevant repo facts, and the bound reference docs.

Within that surface, keep four boundaries separate:

- write authority
- control-plane ownership
- packet legality
- downstream routing truth

Formal inputs:

- the current requirement baseline or `design draft`
- the `Planning State Doc`
- the active planning rolling doc for the current stage
- the current formal planning artifact, if it already exists
- any already sealed upstream planning artifacts for the same Initiative
- repo facts, implementation facts, constraint facts, and the stage-specific reference required by the current stage
- the shared anchor-addressing contract at `../references/anchor-addressing.md`
- the shared planning-state control reference at `../run-planning/references/planning-state.md`

Hard boundaries:

- only `planner` may write substantive current-stage planning content and append planner-owned blocks to the active planning rolling doc
- `planning-loop` may update only the `Planning State Doc`, rolling-doc header / contract-snapshot initialization when the current stage rolling doc does not yet exist, and the top-of-document `状态` line for planning artifacts whose lifecycle state the supervisor is materializing
- do not write review body text, code, or runtime control-plane state from this skill
- if the active stage, active artifact, or active owner changes, record that transition in the `Planning State Doc`
- if the active planning rolling doc does not exist, initialize only the header, including object identity and `planner_slot`, plus `planning_contract_snapshot`
- on first entry into a stage with no rolling doc yet, initialize the stage as `planner_slot=planner` and `round=1` before the first `planner` dispatch
- if `last_transition` records a reopen into the current stage, preserve or recover the existing `planner_slot` and open the next stage `round` instead of resuming the previously sealed round
- `planning_contract_snapshot` must include at least: `stage`, `artifact_ref`, `stage_reference_ref`, `rolling_doc_contract_ref`, and the relevant upstream planning artifact refs
- every `planner` dispatch and every formalized stage-reviewer dispatch must carry the same bound `stage_reference_ref` and `rolling_doc_contract_ref` explicitly
- stage-reviewer reuse is session-local only; reviewer identity and physical `agent_id` never become formal planning truth
- `Gap Analysis Requirement` becomes single-source planning truth only after `Design Doc` seals; once sealed, downstream planning must route from that line instead of re-inferring requirement from chat memory or loose Initiative labels
- if the planning inputs conflict or the current stage cannot be confirmed uniquely, stop and ask for clarification instead of improvising a new planning object

<!-- forgeloop:anchor planning.packet-law -->
## Planning Worker Packet Law

Obey the shared packet law in `../references/anchor-addressing.md`.
Do not restate packet completeness, selector legality, or supervisor-doc exclusion here unless this file adds a true local exception.

Local exceptions for planning worker packets:

- every planner and stage-reviewer packet must explicitly carry the bound `stage_reference_ref` and `rolling_doc_contract_ref`
- planner packets must additionally carry active stage identity, `planning_state_doc_ref`, `artifact_ref`, `rolling_doc_ref`, current `round`, and the necessary sealed upstream refs for the current round
- reviewer packets must additionally carry the current handoff tuple plus the same bound refs for the current handoff

<!-- forgeloop:anchor workflow -->
## Workflow

1. Bind the current planning stage
- Read the requirement or `design draft`, the `Planning State Doc`, the active planning rolling doc when it exists, the current stage artifact when it exists, and the minimum repo facts needed to confirm the stage boundary
- Bind the canonical `stage_reference_ref` for the active stage before dispatch
- Bind the canonical `rolling_doc_contract_ref` before dispatch
- Confirm that the Initiative and active stage are unique, the formal `artifact_ref` is known, the `rolling_doc_ref` is known or can be initialized uniquely, `stage_reference_ref` is uniquely confirmed, and `rolling_doc_contract_ref` is uniquely confirmed
- If the active planning rolling doc already exists, also confirm that `planner_slot` is unique and the stage `round` is unique
- If the active planning rolling doc does not yet exist, it is legal to initialize the stage here with `planner_slot=planner` and `round=1`
- If `last_transition` records an explicit reopen into this stage, recover `planner_slot` from the rolling doc when possible and open the next integer `round` instead of resuming the previously sealed round
- If the active stage has no canonical stage reference formalized in the repository yet, stop and surface that blocker explicitly
- If the `Planning State Doc` conflicts with the rolling doc, the active artifact, the bound `stage_reference_ref`, or the bound `rolling_doc_contract_ref`, stop and hand control back to the caller
- If the rolling doc does not exist, initialize only the header, including object identity and `planner_slot`, plus `planning_contract_snapshot`; write `planner_slot=planner` into the header and `current_snapshot`, and write `round=1` into the `Planning State Doc` before dispatching `planner`

2. Update the minimum planning control plane
- `current_snapshot` must carry the current Initiative, stage, `artifact_ref`, `rolling_doc_ref`, `planner_slot`, and `round` whenever they are known; only a fresh stage with no rolling doc may omit `planner_slot` and `round` temporarily
- `next_action` records only current-stage dispatch or terminal stop for the bound stage: `enter_planning_loop`, `waiting`, `blocked`, or `sealed_planning_docs_ready`
- cross-stage routing never lives in `next_action`; it lives in `last_transition`
- `last_transition` records entering, resuming, or reassigning the current planning stage when needed
- `round` is stage-local and supervisor-owned through the `Planning State Doc`; `planner` and reviewers only echo it in the rolling doc and must not advance it on their own
- open a new round only when entering a stage for the first time, re-entering the same stage after review-requested changes, or reopening an earlier sealed stage; determine reopen from the durable transition already recorded in the `Planning State Doc`, not from chat memory
- Do not write planner body text into the `Planning State Doc`

3. Determine the current in-stage frontier
- If the current round exposes one valid current handoff and no matching current review result, keep the same `planner_slot` and `round`, then dispatch the current stage reviewer directly.
- If the current round already exposes one matching current review result, do not redispatch `planner`; handle that review result directly.
- Otherwise dispatch `planner` for the current round.
- If the current round exposes more than one legal current handoff, or more than one latest matching review result, stop and surface the rolling-doc contract violation explicitly.

4. Dispatch the `planner`
- Keep only one durable `planner_slot` for the current planning stage
- `planner_slot` is the only durable owner identity
- For the current planning session, keep at most one reusable `planner` binding and one reusable stage-reviewer binding for the bound stage
- If the bound `planner` already has a live `agent_id` in this session, reuse it with `send_input`; do not call `spawn_agent` again for the same live planner binding
- Only when the stage has no usable planner binding, or the old planner binding is known closed, dead, or unrecoverable, may the supervisor create or rebind that worker with `spawn_agent`
- physical thread reuse is optional and carries no formal meaning
- all recovery must come from the current packet plus the bound formal docs, never from prior-thread memory as the only legality basis
- The planner input must explicitly carry: active stage identity, requirement or `design draft`, the `Planning State Doc` ref or materialized path, the active `rolling_doc_ref`, the active `artifact_ref`, any materialized paths needed for dispatch, the current `round`, the bound `stage_reference_ref`, the bound `rolling_doc_contract_ref`, the anchor selectors for the exact planning-artifact and rolling-doc surfaces needed in the round, and any sealed upstream planning artifacts
- The planner reads artifact-shape rules from `stage_reference_ref` and communication-plane rules from `rolling_doc_contract_ref`

5. Handle planner output
- The latest `planner_update` in the current round is the current planner intent.
- Route only from that latest `planner_update` in the current round.
- `continue_stage_repair`: keep the same `planner_slot` and the same round.
- `request_reviewer_handoff`: require one valid current handoff in the same round, normalize the current artifact `状态` to `review-ready`, then continue to Step 6 using that handoff.
- `wait_for_upstream_judgment`: write `next_action.action=waiting` and stop.
- `stop_on_blocker`: write `next_action.action=blocked` and stop.
- Anything else is illegal planner output.

6. Dispatch the stage reviewer
- Reuse the current stage reviewer binding with `send_input` when it still has a live `agent_id` in this session; otherwise create or rebind exactly one reviewer for this stage with `spawn_agent`.
- Reviewer input must carry only the current handoff tuple, the bound refs, the selectors, and the same-source slices needed for that review.
- Reviewer legality must always come from the current packet plus the rolling doc and formal refs, not from prior-thread memory.

7. Handle reviewer output
- Use only the latest review result whose `round`, `handoff_id`, and `review_target_ref` match the current handoff.
- `clean seal`:
  - first normalize the current planning artifact `状态` to `sealed`
  - `Design Doc` -> route by sealed `Gap Analysis Requirement`
  - `Gap Analysis Doc` -> `advance_to_total_task_doc`
  - `Total Task Doc` -> `sealed_planning_docs_ready`
- `changes_requested + same-stage repair action` -> normalize the current planning artifact `状态` to `draft`, increment the stage `round`, keep the same `planner_slot`, and continue repair.
- `changes_requested + valid upstream reopen recommendation` -> record `reopen_to_*` in the `Planning State Doc`, demote every downstream planning artifact that is no longer legally sealed back to `draft`, and stop.
- `changes_requested + wait_for_upstream_judgment` -> `next_action.action=waiting`.
- `changes_requested + stop_on_blocker` -> `next_action.action=blocked`.
- Any other combination is illegal review output.
- If the sealed `Design Doc` lacks an explicit `Gap Analysis Requirement` line when clean seal routing depends on it, stop and surface the illegal stage truth explicitly instead of inferring route intent.

<!-- forgeloop:anchor stop-conditions -->
## Stop Conditions

Stop immediately and hand control back upstream or to the user when:

- the active planning stage cannot be confirmed uniquely
- the requirement, `design draft`, or required upstream planning artifacts are missing
- the active stage has no canonical `stage_reference_ref`
- the active stage has no canonical `rolling_doc_contract_ref`
- the `Planning State Doc` conflicts with the active rolling doc, current artifact, bound `stage_reference_ref`, or bound `rolling_doc_contract_ref`
- the stage `round` or current open `handoff_id` cannot be confirmed uniquely
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
- persist any session-local planner / reviewer `agent_id` into formal planning truth
- continue into runtime execution from this skill
- create a second planning state model outside the `Planning State Doc` and active planning rolling doc

<!-- forgeloop:anchor completion-criteria -->
## Completion Criteria

On correct completion, all of the following should be true:

- the current planning stage can be recovered uniquely from the `Planning State Doc` and active planning rolling doc
- `planner_slot` continuity is unambiguous
- stage `round` continuity is unambiguous
- the current rolling doc contract snapshot binds one unambiguous `stage_reference_ref` and one unambiguous `rolling_doc_contract_ref`
- the current actionable `handoff_id` can be recovered uniquely whenever the stage is in reviewer handoff or review-result state
- the current artifact is either still in repair, formally ready for review handoff, explicitly stopped on upstream judgment, stopped on an explicit cross-stage route to the next planning stage, or formally sealed as planning output
- every planning artifact that remains eligible for downstream use exposes the correct top-of-document `状态` value for that point in the lifecycle
- no second planning truth source has been created outside the formal planning docs
