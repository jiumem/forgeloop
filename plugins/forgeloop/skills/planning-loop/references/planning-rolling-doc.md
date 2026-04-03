# Planning Rolling Doc Contract Reference

<!-- forgeloop:anchor document-role -->
## Document Role

- Plane: planning communication artifact
- Applies to: `Design Rolling Doc`, `Gap Rolling Doc`, and `Total Task Doc Rolling Doc`
- Primary readers: planning-layer `Supervisor`, `planner`, and the current stage reviewer
- Primary purpose: define the shared communication-surface contract for planning rounds, reviewer handoff, seal history, and reopen history
- For repo-local Initiatives, required placement is the Initiative-local `.forgeloop/` root, using `design-rolling.md`, `gap-rolling.md`, or `total-task-doc-rolling.md`

This reference governs the planning communication plane, not artifact shape. Stage-specific references still control the structure and judgment standard of `Design Doc`, `Gap Analysis Doc`, and `Total Task Doc`.

<!-- forgeloop:anchor contract-questions -->
## What This Contract Must Answer

- what identity every planning rolling doc must bind
- which role may append which formal blocks
- how `round` works
- how reviewer handoff works
- how stale review results are rejected without rewriting history
- how a clean seal, same-stage repair, or upstream reopen recommendation is represented

<!-- forgeloop:anchor required-header -->
## Required Header And Contract Snapshot

- each rolling doc must bind one Initiative, one planning stage, one active `artifact_ref`, and one logical `planner_slot`
- when the rolling doc does not yet exist, `planning-loop` may initialize only the header plus one `planning_contract_snapshot`
- `planning_contract_snapshot` must include at least:
  - `kind`
  - `created_at`
  - `stage`
  - `artifact_ref`
  - `stage_reference_ref`
  - `rolling_doc_contract_ref`
  - the relevant upstream planning artifact refs for the current stage
- the rolling doc owns this snapshot; the `Planning State Doc` remains control-plane-only

<!-- forgeloop:anchor legal-machine-blocks -->
## Legal Machine Blocks

- `planning_rolling_header`
- `planning_contract_snapshot`
- `planner_update`
- `design_doc_ref`
- `gap_analysis_ref`
- `total_task_doc_ref`
- `design_review_result`
- `gap_review_result`
- `total_task_doc_review_result`

Header and contract snapshot are initialized once. All later formal facts append only.

<!-- forgeloop:anchor round-law -->
## Round Law

- `round` is stage-local, monotonically increasing, and owned by the `Supervisor` through the `Planning State Doc`
- `planner` and reviewers must echo the current round in every formal block they append; they do not advance it themselves
- a new round opens only when:
  - the `Supervisor` enters a planning stage for the first time
  - the `Supervisor` re-enters the same stage after a reviewer has requested changes
  - the `Supervisor` reopens an earlier sealed stage through an explicit cross-stage route
- multiple planner updates may occur inside one round
- reviewer freshness is per round: each review dispatch belongs to one current round, and a later same-stage repair must move to the next round before the next reviewer dispatch

<!-- forgeloop:anchor append-only-ownership -->
## Append-Only Ownership

- `planning-loop` may write only the initial header and `planning_contract_snapshot` when creating the rolling doc
- `planner` may append only:
  - `planner_update`
  - `design_doc_ref` in `Design Rolling Doc`
  - `gap_analysis_ref` in `Gap Rolling Doc`
  - `total_task_doc_ref` in `Total Task Doc Rolling Doc`
- the current stage reviewer may append only:
  - `design_review_result`
  - `gap_review_result`
  - `total_task_doc_review_result`
- no role may rewrite or delete prior formal blocks

<!-- forgeloop:anchor planner-update-law -->
## Planner Update Law

- every `planner_update` block must include at least:
  - `kind`
  - `round`
  - `author_role`
  - `created_at`
  - `next_action`
- `author_role` on a `planner_update` block must stay `planner`
- the latest `planner_update` in the current round is the current planner intent
- planner-side `next_action` vocabulary is shared across planning stages:
  - `continue_stage_repair`: keep repairing inside the current stage and current round
  - `request_reviewer_handoff`: the artifact is review-ready for this round and the rolling doc must expose a current stage-local handoff block
  - `wait_for_upstream_judgment`: stop for upstream or user judgment
  - `stop_on_blocker`: stop for a real blocker that cannot be repaired inside the current round
- artifact-level `review-ready` remains artifact truth under the stage reference; reviewer dispatch becomes legal only when the latest `planner_update` uses `next_action=request_reviewer_handoff` and the current handoff block is present

<!-- forgeloop:anchor handoff-law -->
## Handoff Law

- the stage-local handoff block is the authoritative reviewer-dispatch anchor for the current round
- every handoff block must include at least:
  - `kind`
  - `round`
  - `author_role`
  - `created_at`
  - `handoff_id`
  - `review_target_ref`
- `author_role` on a handoff block must stay `planner`
- `handoff_id` must be unique within the rolling doc
- `review_target_ref` is the authoritative review target for that handoff
- if `planner` appends a later handoff block in the same round, that later handoff supersedes earlier handoffs in that round without deleting history
- `planner` must not reuse an old `handoff_id` for a new review target

<!-- forgeloop:anchor review-result-law -->
## Review Result Law

- This contract owns the cross-stage minimum for every planning review result.
- Every `*_review_result` block must include:
  - `kind`
  - `round`
  - `author_role`
  - `created_at`
  - `handoff_id`
  - `review_target_ref`
  - `verdict`
  - `seal_status`
  - `next_action`
- Stage reviewer prompts may extend these blocks, but they must not remove or rename the fields listed here.
- Stage-specific fields required for supervisor routing are:
  - `design_review_result` requires: `requirement_fit`, `boundary_correctness`, `structural_soundness`, `downstream_planning_readiness`, `correctness_surface`, `open_issues`, and `findings`
  - `gap_review_result` requires: `current_state_evidence`, `gap_ledger_integrity`, `convergence_strategy`, `downstream_planning_readiness`, `correctness_surface`, `open_issues`, and `findings`
  - `total_task_doc_review_result` requires: `execution_boundary`, `object_map_integrity`, `acceptance_truth_integrity`, `integration_path`, `runtime_readiness`, `residual_risk_boundary`, `open_issues`, and `findings`
- `open_issues` and `findings` may use either inline YAML lists or multi-line YAML list form, but they must remain attached to the same review-result block
- `author_role` on a review-result block must stay `reviewer`
- `handoff_id` and `review_target_ref` must echo the exact current handoff being judged
- review-side `next_action` vocabulary is closed:
  - `design_review_result`: `continue_design_repair`, `ready_for_supervisor_routing`, `wait_for_upstream_judgment`, `stop_on_blocker`
  - `gap_review_result`: `continue_gap_repair`, `ready_for_supervisor_routing`, `wait_for_upstream_judgment`, `stop_on_blocker`
  - `total_task_doc_review_result`: `continue_total_task_doc_repair`, `ready_for_supervisor_routing`, `wait_for_upstream_judgment`, `stop_on_blocker`
- if the real fix belongs upstream, keep `next_action=wait_for_upstream_judgment` and add advisory `upstream_reopen_recommendation` with `target_stage` and `reason`
- never use `upstream_reopen_recommendation` for same-stage repair
- `design_review_result` must not emit `upstream_reopen_recommendation`, because no earlier planning stage exists

<!-- forgeloop:anchor freshness-selection -->
## Freshness And Current-Law Selection

- the `Supervisor` acts only on the current open handoff for the current round
- a review result is actionable only when all of the following match that open handoff:
  - `round`
  - `handoff_id`
  - `review_target_ref`
- if multiple review-result blocks match the same current handoff exactly, only the latest appended matching block is actionable; earlier matching blocks remain history and must not drive current routing
- stale or mismatched review results remain historical facts and must not drive current routing
- if the rolling doc does not expose one unique current handoff for the current round, or one unique latest matching review result, stop and surface a rolling-doc contract violation instead of guessing

<!-- forgeloop:anchor seal-repair-reopen -->
## Seal, Repair, And Reopen Law

- a stage reaches clean-seal in the planning communication plane only when `verdict=clean`, `seal_status=sealed`, and `next_action=ready_for_supervisor_routing`
- any other combination is non-sealing and must be treated as repair, wait, blocker, or reopen advice
- a clean reviewer result with explicit `seal_status=sealed` authorizes only the current planning stage to be finalized; only the `Supervisor` may set the current artifact `状态` to `sealed` and route to another stage afterward
- the rolling doc is planning communication history, not execution admission input; downstream execution reads the planning documents themselves
- the artifact `状态` line is the execution-facing document-status marker for the current stage; if it drifts from the stage lifecycle that the supervisor is materializing, repair it before continuing
- a reviewer result that requests same-stage repair closes the current handoff and requires the `Supervisor` to open the next round before redispatching `planner`
- an upstream stage may reopen only through an explicit supervisor route recorded in the `Planning State Doc`
- upstream reopen must invalidate every downstream planning artifact that is no longer legally sealed; those artifacts must lose `状态：sealed` before they may be reused
