---
name: task-loop
description: Use when the `Global State Doc` has uniquely confirmed that current progress is at a ready or active Task; this skill uses single coder ownership to drive the current Task through formal `implement/repair -> G1 -> anchor/fixup -> fresh R1` closure
---

# Task Loop

`task-loop` handles only one confirmed Task. Here you act as the Task-layer `Supervisor`: maintain the minimum control plane, keep a single `coder_slot`, dispatch the same `coder` and a fresh `task_reviewer` each round, and use the facts from `G1`, `anchor / fixup`, and `R1` to decide whether the Task stays in the current round, enters `R1`, returns clean upstream, escalates, or stops.

`coder_slot` is the logical owner identifier, not the physical `agent_id`; the current `agent_id` may change, but `coder_slot` does not.

You are not responsible for writing code, writing `r1_result`, rewriting Milestone / Initiative dispatch, finishing the development branch, or maintaining any parallel state.

## Task-Local Vocabulary

- `g1_result.next_action` must be one of: `continue_task_coder_round`, `request_reviewer_handoff`, `wait_for_user`, `stop_on_blocker`
- `r1_result.next_action` must be one of: `continue_task_repair`, `return_to_source_object`, `select_next_ready_object`, `task_done`, `escalate_to_milestone`, `wait_for_user`, `stop_on_blocker`

## Truth Sources And Hard Boundaries

The formal input surface contains only the Initiative static truth trio `design_ref`, `gap_analysis_ref`, and `total_task_doc_ref` (`gap_analysis_ref` may be `N/A` for some Initiative types), the `Global State Doc`, the current `Task Review Rolling Doc`, and the necessary Git / test / commit facts.

Hard boundaries:
- `G1` may be run only by the coder in the current implementation round, and it must be written into the `Task Review Rolling Doc`
- `anchor_ref` or `fixup_ref` may be written only after `G1 pass`
- `R1` may be run only by a fresh reviewer against the formal anchor
- `round` is Task-local and owned by the `Supervisor` through the `Global State Doc`; coder and reviewer echo it in the rolling doc but do not advance it themselves
- a round closes only when `r1_result` is written; `G1 fail` stays in the same round
- a new round opens only on first entry into the Task or after `r1_result.next_action=continue_task_repair`
- the `Global State Doc` may contain only `current_snapshot`, `next_action`, and `last_transition`
- if `next_action` changes the active object or active plane, `current_snapshot` must be updated at the same time; only when still advancing within the same Task may you update only `next_action` and `last_transition`
- the current Task review handoff is the latest `anchor_ref` or `fixup_ref` in the current round
- each Task handoff block must carry `handoff_id` and `review_target_ref`; `r1_result` is actionable only when its `round`, `handoff_id`, and `review_target_ref` match that current handoff exactly, and if multiple `r1_result` blocks match one current handoff, only the latest matching block is actionable
- if only a bounded task brief exists and the rolling doc does not, it may be used to initialize the header, including object identity and `coder_slot`, plus `task_contract_snapshot`; after initialization, the rolling doc becomes the only collaboration surface

## Workflow

1. Bind the current Task
- Read the Task definition, the `Global State Doc`, the current `Task Review Rolling Doc`, and the necessary engineering facts
- Confirm that the active task is unique, the workspace is executable, the rolling doc matches the active task, `coder_slot` is unique, and the current Task-local `round` is unique when it already exists
- If the `Global State Doc` conflicts with the rolling doc, hand control back to `rebuild-runtime`
- If the current Task cannot be confirmed uniquely, the contract is missing, or the facts show the system should wait for the user, stop
- If the rolling doc does not exist, initialize only the header, including object identity and `coder_slot`, plus `task_contract_snapshot`; write `coder_slot=coder` into the header and `current_snapshot`, and write `round=1` into the `Global State Doc` before dispatching the first coder round

2. Update the minimum control plane
- `current_snapshot` points to the current active task, `coder_slot`, and the current Task-local `round`
- `next_action` points to continuing the current Task coder round
- Record entering the current round, resuming the current round, or coder succession in `last_transition` when needed
- Do not write implementation details, review body text, or full test output into the `Global State Doc`

3. Dispatch the coder
- Keep only one logical `coder_slot` for the current Task
- Reuse the current `agent_id` while the physical thread is alive; if it is lost, you may assign a successor `agent_id`, but you must reuse the original `coder_slot` and record the succession
- Default to `fork_context=false`
- The coder input only needs to locate the current formal input surface: current Task identity, `design_ref`, `gap_analysis_ref`, `total_task_doc_ref`, the `Global State Doc` path, and the current `Task Review Rolling Doc` path
- The coder returns its result to the `Task Review Rolling Doc` according to the contract

4. Handle the coder result
- Decide only from the rolling doc and Git facts, not from chat summaries
- Read the latest `g1_result.next_action` first
- If the latest `g1_result.next_action=continue_task_coder_round`, or there is only `coder_update`, or the latest `g1_result=fail`: the same coder continues in the same round
- If the latest `g1_result.next_action=request_reviewer_handoff` but there is no valid current handoff yet: return to the same coder to complete the formal anchor inside the same round
- If the latest `g1_result.next_action=request_reviewer_handoff` and one valid current handoff exists: switch `next_action` to entering `R1`
- If the latest `g1_result.next_action=wait_for_user`: write waiting into the `Global State Doc`, then stop
- If the latest `g1_result.next_action=stop_on_blocker`: write blocked into the `Global State Doc`, then stop
- Only if the latest `g1_result` lacks `next_action` should you fall back to `pass / fail` plus handoff facts

5. Dispatch a fresh `task_reviewer`
- Every `R1` round uses a freshly spawned reviewer, with `fork_context=false` by default
- The reviewer reads `design_ref`, `gap_analysis_ref`, `total_task_doc_ref`, the `Global State Doc`, the current `Task Review Rolling Doc`, the current `anchor/fixup`, the current `round`, the current `handoff_id`, the current `review_target_ref`, and the necessary spec refs
- The reviewer returns its result to the `Task Review Rolling Doc` according to the contract

6. Handle `r1_result`
- The current actionable `r1_result` is the latest matching review result for the current handoff
- If the current actionable `r1_result` has `verdict=clean` and `next_action=return_to_source_object`: update `last_transition`, switch `current_snapshot` back to the source Milestone / Initiative recorded in the `Global State Doc`, and hand control back upstream
- If the current actionable `r1_result` has `verdict=clean` and `next_action=select_next_ready_object`: update `last_transition`, move `current_snapshot` forward to the next ready object when it is uniquely confirmed, otherwise switch `current_snapshot` to a frontier-selection snapshot no longer bound to the current Task, then hand control back upstream
- If the current actionable `r1_result` has `verdict=clean` and `next_action=task_done`: update `last_transition`, switch `current_snapshot` to a frontier-selection snapshot no longer bound to the current Task, then hand control back upstream
- If the current actionable `r1_result` has `verdict=changes_requested` and `next_action=continue_task_repair`: increment the Task-local `round` in the `Global State Doc`, switch `next_action` back to continuing current Task repair, and let the same `coder_slot` enter the next round
- If the current actionable `r1_result` has `verdict=changes_requested` and `next_action=escalate_to_milestone`: update `last_transition`, switch `current_snapshot` to the parent Milestone when it is uniquely confirmed, then hand control back upstream
- If the current actionable `r1_result` has `verdict=changes_requested` and `next_action=wait_for_user`: the reviewer writes only the recommendation, the `Supervisor` writes waiting into the `Global State Doc`, then hands control back upstream
- If the current actionable `r1_result` has `verdict=changes_requested` and `next_action=stop_on_blocker`: the reviewer writes only the recommendation, the `Supervisor` writes blocked into the `Global State Doc`, then hands control back upstream
- If the rolling doc does not expose one unique actionable `r1_result`, or if `verdict` and `next_action` do not form one legal combination above, stop and surface the illegal Task review output explicitly

## Stop Conditions

Stop immediately and hand control back upstream or to the user when:
- the active task cannot be confirmed uniquely
- the Task contract is missing, required spec refs are missing, or the `Global State Doc` conflicts with the rolling doc
- the workspace is not an executable implementation environment, or current facts show the system should wait for the user
- the current problem clearly exceeds Task radius and must escalate to Milestone
- the coder or reviewer exposes a real blocker

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

## Completion Criteria

On correct completion, all of the following should be true:
- the current Task state can be recovered uniquely from the `Global State Doc` and the `Task Review Rolling Doc`
- `coder_slot` continuity is unambiguous
- if the Task is clean, the rolling doc already contains a valid `g1_result`, `anchor/fixup`, and `r1_result`
- no second runtime truth source has been created outside the four formal runtime docs
