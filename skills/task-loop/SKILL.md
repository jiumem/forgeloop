---
name: task-loop
description: Use when the `Global State Doc` has uniquely confirmed that current progress is at a ready or active Task; this skill uses single coder ownership to drive the current Task through formal `implement/repair -> G1 -> anchor/fixup -> fresh R1` closure
---

# Task Loop

`task-loop` handles only one confirmed Task. Here you act as the Task-layer `Supervisor`: maintain the minimum control plane, keep a single `coder_slot`, dispatch the same `coder` and a fresh `task_reviewer` each round, and use the facts from `G1`, `anchor / fixup`, and `R1` to decide whether to continue repair, declare formal clean closure, escalate, or stop.

`coder_slot` is the logical owner identifier, not the physical `agent_id`; the current `agent_id` may change, but `coder_slot` does not.

You are not responsible for writing code, writing `r1_result`, rewriting Milestone / Initiative dispatch, finishing the development branch, or maintaining any parallel state.

## Truth Sources And Hard Boundaries

The formal input surface contains only the Initiative static truth trio `design_ref`, `gap_analysis_ref`, and `total_task_doc_ref` (`gap_analysis_ref` may be `N/A` for some Initiative types), the `Global State Doc`, the current `Task Review Rolling Doc`, and the necessary Git / test / commit facts.

Hard boundaries:
- `G1` may be run only by the coder in the current implementation round, and it must be written into the `Task Review Rolling Doc`
- `anchor_ref` or `fixup_ref` may be written only after `G1 pass`
- `R1` may be run only by a fresh reviewer against the formal anchor
- a round closes only when `r1_result` is written; `G1 fail` stays in the same round
- the `Global State Doc` may contain only `current_snapshot`, `next_action`, and `last_transition`
- if `next_action` changes the active object or active plane, `current_snapshot` must be updated at the same time; only when still advancing within the same Task may you update only `next_action` and `last_transition`
- if only a bounded task brief exists and the rolling doc does not, it may be used to initialize the header, including object identity and `coder_slot`, plus `task_contract_snapshot`; after initialization, the rolling doc becomes the only collaboration surface

## Workflow

1. Bind the current Task
- Read the Task definition, the `Global State Doc`, the current `Task Review Rolling Doc`, and the necessary engineering facts
- Confirm that the active task is unique, the workspace is executable, the rolling doc matches the active task, and `coder_slot` is unique
- If the `Global State Doc` conflicts with the rolling doc, hand control back to `rebuild-runtime`
- If the current Task cannot be confirmed uniquely, the contract is missing, or the facts show the system should wait for the user, stop
- If the rolling doc does not exist, initialize only the header, including object identity and `coder_slot`, plus `task_contract_snapshot`

2. Update the minimum control plane
- `current_snapshot` points to the current active task and `coder_slot`
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
- If the latest `g1_result=fail`, or there is only `coder_update`: the same coder continues in the same round
- If `g1_result=pass` but there is no valid `anchor_ref/fixup_ref`: return to the same coder to complete the formal anchor
- If `g1_result=pass` and a valid anchor already exists: switch `next_action` to entering `R1`
- If the coder requests more context, human judgment, or exposes a real blocker: write waiting/blocked into the `Global State Doc`, then stop

5. Dispatch a fresh `task_reviewer`
- Every `R1` round uses a freshly spawned reviewer, with `fork_context=false` by default
- The reviewer reads `design_ref`, `gap_analysis_ref`, `total_task_doc_ref`, the `Global State Doc`, the current `Task Review Rolling Doc`, the current `anchor/fixup`, and the necessary spec refs
- The reviewer returns its result to the `Task Review Rolling Doc` according to the contract

6. Handle `r1_result`
- `R1 clean`: update `last_transition`; if the current Task is a repair task formally objectized from an upper-layer object and the `Global State Doc` clearly records its source object and return-hook rolling doc, then first switch `current_snapshot` back to that source Milestone / Initiative and switch `next_action` to re-entering that upper loop; otherwise, if the next ready object is uniquely confirmed, move `current_snapshot` forward to that object; otherwise switch `current_snapshot` to a frontier-selection snapshot no longer bound to the current Task, then switch `next_action` to `task_done` or `select_next_ready_object`, and hand control back upstream
- `R1 changes_requested` and still within Task radius: switch `next_action` to continuing current Task repair, and let the same `coder_slot` enter the next round
- If `R1` requests escalation, waiting for the user, or identifies a real blocker: the reviewer writes only the recommendation, the `Supervisor` updates only the `Global State Doc`, then hands control back upstream

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
