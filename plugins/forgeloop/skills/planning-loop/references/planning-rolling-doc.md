# Planning Rolling Doc Contract Reference

<!-- forgeloop:anchor document-role -->
## Document Role

- Plane: planning communication artifact
- Applies to: `Design Rolling Doc`, `Gap Rolling Doc`, and `Plan Rolling Doc`
- Primary readers: planning-layer `Supervisor`, `planner`, and the current stage reviewer
- Primary purpose: define the shared communication-surface contract for planning rounds, reviewer handoff, seal history, and reopen history

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

- each rolling doc must bind one Initiative, one planning stage, one active artifact path, and one logical `planner_slot`
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
- `plan_review_result`

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
  - `total_task_doc_ref` in `Plan Rolling Doc`
- the current stage reviewer may append only:
  - `design_review_result`
  - `gap_review_result`
  - `plan_review_result`
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

- every review-result block must include at least:
  - `kind`
  - `round`
  - `author_role`
  - `created_at`
  - `handoff_id`
  - `review_target_ref`
  - `verdict`
  - `seal_status`
  - `next_action`
- `author_role` on a review-result block must stay `reviewer`
- `handoff_id` and `review_target_ref` must echo the exact current handoff being judged
- `gap_review_result` and `plan_review_result` may additionally carry advisory `upstream_reopen_recommendation` with:
  - `target_stage`
  - `reason`
- `upstream_reopen_recommendation` is advisory only; only the `Supervisor` may route stages
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

- a clean reviewer result with explicit `seal_status=sealed` seals only the current planning stage; only the `Supervisor` may route to another stage afterward
- a reviewer result that requests same-stage repair closes the current handoff and requires the `Supervisor` to open the next round before redispatching `planner`
- an upstream stage may reopen only through an explicit supervisor route recorded in the `Planning State Doc`
- downstream stages must not silently rewrite earlier sealed truth; they may only recommend reopen through the rolling doc and stop
