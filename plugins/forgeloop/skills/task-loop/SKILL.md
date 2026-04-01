---
name: task-loop
description: Use when the `Global State Doc` has uniquely confirmed that current progress is at a ready or active Task; this skill uses single coder ownership to drive the current Task through formal `implement/repair -> G1 -> anchor/fixup -> fresh R1` closure
---

# Task Loop

<!-- forgeloop:anchor role -->
`task-loop` handles only one confirmed Task. Here you act as the Task-layer `Supervisor`: maintain the minimum control plane, keep a single `coder_slot`, dispatch the same `coder` and a fresh `task_reviewer` each round, and use the facts from `G1`, `anchor / fixup`, and `R1` to decide whether the Task stays in the current round, enters `R1`, returns clean upstream, escalates, or stops.

`coder_slot` is the logical owner identifier, not the physical `agent_id`; the current `agent_id` may change, but `coder_slot` does not.

You are not responsible for writing code, writing `r1_result`, rewriting Milestone / Initiative dispatch, finishing the development branch, or maintaining any parallel state.

<!-- forgeloop:anchor task-local-vocabulary -->
## Task-Local Vocabulary

- `g1_result.next_action` must be one of: `continue_task_coder_round`, `request_reviewer_handoff`, `wait_for_user`, `stop_on_blocker`
- `r1_result.next_action` must be one of: `continue_task_repair`, `return_to_source_object`, `select_next_ready_object`, `task_done`, `escalate_to_milestone`, `wait_for_user`, `stop_on_blocker`

<!-- forgeloop:anchor canonical-runtime-contract-refs -->
## Canonical Runtime Contract Refs

- shared `Global State Doc` contract -> `../run-initiative/references/global-state.md`
- `Task Review Rolling Doc` contract -> `../run-initiative/references/task-review-rolling-doc.md`
- runtime cutover contract -> `../run-initiative/references/runtime-cutover.md`
- shared anchor-addressing contract -> `../references/anchor-addressing.md`
- shared derived-view contract -> `../references/derived-views.md`

<!-- forgeloop:anchor truth-sources-boundaries -->
## Truth Sources And Hard Boundaries

The formal input surface contains only the Initiative static truth trio `design_ref`, `gap_analysis_ref`, and `total_task_doc_ref` (`gap_analysis_ref` may be `N/A` for some Initiative types), the `Global State Doc`, the current `Task Review Rolling Doc`, and the necessary Git / test / commit facts.

Hard boundaries:
- `G1` may be run only by the coder in the current implementation round, and it must be written into the `Task Review Rolling Doc`
- `anchor_ref` or `fixup_ref` may be written only after `G1 pass`
- `R1` may be run only by a fresh reviewer against the formal anchor
- `round` is Task round and owned by the `Supervisor` through the `Global State Doc`; coder and reviewer echo it in the rolling doc but do not advance it themselves
- a round closes only when `r1_result` is written; `G1 fail` stays in the same round
- a new round opens only on first entry into the Task or after `r1_result.next_action=continue_task_repair`
- the `Global State Doc` may contain only `current_snapshot`, `next_action`, and `last_transition`
- when reading, writing, initializing, or repairing runtime state, the `Global State Doc` and the `Task Review Rolling Doc` must follow the canonical contract refs above; do not improvise block shape or `next_action` spelling from memory or older design examples
- Task dispatch default path is controlled only by the bound runtime cutover contract: `full_doc_default` may default to authoritative full documents, while `minimal_preferred` and `minimal_required` use authoritative refs plus doc-local selectors and only the minimal slices needed for the current Task handoff
- if `next_action` changes the active object or active plane, `current_snapshot` must be updated at the same time; only when still advancing within the same Task may you update only `next_action` and `last_transition`
- the current Task review handoff is the latest `anchor_ref` or `fixup_ref` in the current round
- each Task handoff block must carry `handoff_id` and `review_target_ref`; `r1_result` is actionable only when its `round`, `handoff_id`, and `review_target_ref` match that current handoff exactly, and if multiple `r1_result` blocks match one current handoff, only the latest matching block is actionable
- if only a bounded task brief exists and the rolling doc does not, it may be used to initialize the header, including object identity and `coder_slot`, plus `task_contract_snapshot`, according to the canonical `Task Review Rolling Doc` contract; after initialization, the rolling doc becomes the only collaboration surface

<!-- forgeloop:anchor task.packet-shape -->
## Task Packet Shape

Task coder packets should carry only:

- current Task identity and continuity metadata
- authoritative refs
- current `round` and `coder_slot`
- the current handoff tuple when one already exists
- the Task definition and acceptance selectors plus the exact design/gap/plan/runtime selectors required for this round
- only the minimum inline slices already rebuilt from those refs
- callback information when this Task is an objectized repair task

Task reviewer packets should carry only:

- the same authoritative refs
- current `round`, `handoff_id`, and `review_target_ref`
- the current `anchor` or `fixup`
- only the Task-radius selectors and slices required for this review
- an optional `handoff-scoped` derived view when it is still legal and rebuildable

Neither packet should default to the whole `Total Task Doc`, the whole Task rolling-doc history, or unrelated Milestone or Initiative history.

<!-- forgeloop:anchor task.current-selection -->
## Task Current Selection

- the current Task handoff is always the latest `anchor_ref` or `fixup_ref` in the current round
- the current actionable Task review result is always the latest matching `r1_result` for that handoff
- a stale or mismatched `r1_result` remains history and must not drive routing

<!-- forgeloop:anchor task.warm-path-delta -->
## Task Warm-Path Delta

Same-thread warm-path delta is legal only for the same Task, same workspace, same logical `coder_slot`, and same Task `round`.

It may carry only newly appended formal blocks, selector changes, refreshed slices, or derived-view invalidation reasons.

Return to a full packet immediately on Task change, round change, slot succession, handoff change, selector legality failure, anchor conflict, or first reviewer entry into a handoff.

<!-- forgeloop:anchor task.cutover-mode-law -->
## Task Cutover Mode Law

Bind `../run-initiative/references/runtime-cutover.md` before deciding the Task default read path.

- `full_doc_default`
  - authoritative full-document Task packets remain the default runtime route
  - minimal packets may still be assembled for validation, benchmark, or explicit sidecar use
- `minimal_preferred`
  - minimal Task packets are the default
  - selector legality failure, stale derived views, rolling-doc initialization, or unresolved formal conflict may promote one read to full-document fallback
- `minimal_required`
  - minimal Task packets are required
  - ordinary legality failure should stop unless the cutover contract names a disaster-recovery exception

<!-- forgeloop:anchor workflow -->
## Workflow

1. Bind the current Task
- First read the runtime cutover contract and bind `current_runtime_cutover_mode`.
- If `current_runtime_cutover_mode=full_doc_default`, authoritative full-document reads may be the default bind path; still keep any optional minimal packet self-sufficient.
- If `current_runtime_cutover_mode=minimal_preferred` or `minimal_required`, read in this exact order:
  - the minimum `Global State Doc` control plane needed to confirm active Task identity, `coder_slot`, and Task `round`
  - `current-effective`, `handoff-scoped`, or `attempt-aware` only when the derived view is still legal and rebuildable from the same authoritative `Task Review Rolling Doc`
  - the authoritative `Task Review Rolling Doc` blocks needed to confirm the current handoff, latest matching `r1_result`, or rolling-doc/header continuity
  - full-document fallback only when selector legality fails, the derived view is stale or missing, the rolling doc must be initialized, or a formal conflict still cannot be resolved uniquely
- Read the Task definition and the minimum engineering facts only after that runtime read order still leaves Task identity, acceptance, or execution legality incomplete
- Confirm that the active task is unique, the workspace is executable, the rolling doc matches the active task, `coder_slot` is unique, and the Task `round` is unique when it already exists
- If the `Global State Doc` conflicts with the rolling doc, hand control back to `rebuild-runtime`
- If the current Task cannot be confirmed uniquely, the contract is missing, or the facts show the system should wait for the user, stop
- If the rolling doc does not exist, initialize only the header, including object identity and `coder_slot`, plus `task_contract_snapshot`, according to the canonical `Task Review Rolling Doc` contract; write `coder_slot=coder` into the header and `current_snapshot`, and write `round=1` into the `Global State Doc` according to the canonical `Global State Doc` contract before dispatching the first coder round

2. Update the minimum control plane
- `current_snapshot` points to the active task, `coder_slot`, and the Task `round`
- `next_action.action = continue_task_coder_round`
- Record entering the current round, resuming the current round, or coder succession in `last_transition` when needed
- Do not write implementation details, review body text, or full test output into the `Global State Doc`

3. Dispatch the coder
- Keep only one logical `coder_slot` for the current Task
- Reuse the current `agent_id` while the physical thread is alive; if it is lost, you may assign a successor `agent_id`, but you must reuse the original `coder_slot` and record the succession
- Default to `fork_context=false`
- The coder input only needs to locate the current formal input surface: current Task identity, authoritative refs, the current handoff identifiers, the doc-local selectors for the required design/gap/plan/runtime sections, and any already materialized minimal slices
- The coder returns its result to the `Task Review Rolling Doc` according to the contract

4. Handle coder output
- `continue_task_coder_round` or `g1_result.verdict=fail`: stay in the same round with the same `coder_slot`.
- `request_reviewer_handoff` without a valid handoff: return to the same coder to finish the formal anchor.
- `request_reviewer_handoff` with a valid current handoff: set `next_action.action = enter_r1`.
- `wait_for_user`: write waiting and stop.
- `stop_on_blocker`: write blocked and stop.
- Anything else is illegal Task coder output.

5. Dispatch a fresh `task_reviewer`
- Every `R1` round uses a freshly spawned reviewer, with `fork_context=false` by default
- The reviewer reads the same authoritative refs, the current handoff identifiers, the doc-local selectors for the review target and supporting spec slices, the current `anchor/fixup`, and only the minimal slices needed for Task-radius review unless fallback is triggered explicitly
- The reviewer returns its result to the `Task Review Rolling Doc` according to the contract

6. Handle `r1_result`
- The current actionable `r1_result` is the latest matching review result for the current handoff
- If the current actionable `r1_result` has `verdict=clean` and `next_action=return_to_source_object`: update `last_transition`, switch `current_snapshot` back to the source Milestone / Initiative recorded in the `Global State Doc`, and hand control back upstream
- If the current actionable `r1_result` has `verdict=clean` and `next_action=select_next_ready_object`: update `last_transition`, move `current_snapshot` forward to the next ready object when it is uniquely confirmed, otherwise switch `current_snapshot` to a frontier-selection snapshot no longer bound to the current Task, then hand control back upstream
- If the current actionable `r1_result` has `verdict=clean` and `next_action=task_done`: update `last_transition`, switch `current_snapshot` to a frontier-selection snapshot no longer bound to the current Task, then hand control back upstream
- If the current actionable `r1_result` has `verdict=changes_requested` and `next_action=continue_task_repair`: increment the Task `round` in the `Global State Doc`, set `next_action.action = continue_task_repair`, and let the same `coder_slot` enter the next round
- If the current actionable `r1_result` has `verdict=changes_requested` and `next_action=escalate_to_milestone`: update `last_transition`, switch `current_snapshot` to the parent Milestone when it is uniquely confirmed, then hand control back upstream
- If the current actionable `r1_result` has `verdict=changes_requested` and `next_action=wait_for_user`: the reviewer writes only the recommendation, the `Supervisor` writes waiting into the `Global State Doc`, then hands control back upstream
- If the current actionable `r1_result` has `verdict=changes_requested` and `next_action=stop_on_blocker`: the reviewer writes only the recommendation, the `Supervisor` writes blocked into the `Global State Doc`, then hands control back upstream
- If the rolling doc does not expose one unique actionable `r1_result`, or if `verdict` and `next_action` do not form one legal combination above, stop and surface the illegal Task review output explicitly

<!-- forgeloop:anchor stop-conditions -->
## Stop Conditions

Stop immediately and hand control back upstream or to the user when:
- the active task cannot be confirmed uniquely
- the Task contract is missing, required spec refs are missing, or the `Global State Doc` conflicts with the rolling doc
- the workspace is not an executable implementation environment, or current facts show the system should wait for the user
- the current problem clearly exceeds Task radius and must escalate to Milestone
- the coder or reviewer exposes a real blocker

<!-- forgeloop:anchor red-lines -->
## Red Lines

Never:
- cut `anchor / fixup` before `G1 pass`
- enter `R1` without a formal anchor
- treat `G1 fail` as if the round were closed
- silently replace the logical `coder_slot`
- keep a bounded brief long-term as a second collaboration truth source
- write coder / reviewer body content into the `Global State Doc`
- dispatch multiple coders concurrently for the same Task
- let the reviewer repair code
- skip `G1 -> anchor / fixup -> R1`
- switch to Milestone / Initiative closure while the Task still has active repair
- claim the Task is done without `r1_result: clean`

<!-- forgeloop:anchor completion-criteria -->
## Completion Criteria

On correct completion, all of the following should be true:
- the current Task state can be recovered uniquely from the `Global State Doc` and the `Task Review Rolling Doc`
- `coder_slot` continuity is unambiguous
- if the Task is clean, the rolling doc already contains a valid `g1_result`, `anchor/fixup`, and `r1_result`
- no second runtime truth source has been created outside the four formal runtime docs
