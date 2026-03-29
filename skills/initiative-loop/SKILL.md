---
name: initiative-loop
description: Use when the `Global State Doc` has uniquely confirmed that current progress is at a ready or active Initiative; this skill uses single coder ownership to drive the current Initiative through formal `review/repair -> G3 -> fresh R3` closure
---

# Initiative Loop

`initiative-loop` handles only one confirmed Initiative. Here you act as the Initiative-layer `Supervisor`: maintain the minimum control plane, keep a single `coder_slot`, dispatch the same `coder` and a fresh `initiative_reviewer` each round, and use the facts from `G3`, `R3`, and objectized repair tasks when needed to decide whether to continue delivery review, repair within the current layer, declare formal clean closure, wait for the user, or stop.

`coder_slot` is the logical owner identifier, not the physical `agent_id`; the current `agent_id` may change, but `coder_slot` does not.

You are not responsible for writing code, writing `r3_result`, directly repairing Task code, rewriting any higher-level dispatch, performing governance actions outside finishing the development branch, or maintaining any parallel state.

## Truth Sources And Hard Boundaries

The formal input surface contains only the Initiative static truth trio `design_ref`, `gap_analysis_ref`, and `total_task_doc_ref` (`gap_analysis_ref` may be `N/A` for some Initiative types), the `Global State Doc`, the current `Initiative Review Rolling Doc`, the Milestone review docs / supporting evidence included in the current Initiative delivery candidate, and the necessary release / rollout / deployment / flag / readiness / test facts.

Hard boundaries:
- `G3` may be run only by the coder in the current delivery round, and it must be written into the `Initiative Review Rolling Doc`
- `R3` may be run only by a fresh reviewer against the current formal Initiative object
- the current Initiative round closes only when `r3_result` is written; if the coder still needs repair inside the current Initiative during `G3`, it stays in the same round
- the `Initiative Review Rolling Doc` is the only formal document for `G3 / R3`; the `Global State Doc` may contain only `current_snapshot`, `next_action`, and `last_transition`
- if `next_action` changes the active object or active plane, `current_snapshot` must be updated at the same time; only when still advancing within the same Initiative may you update only `next_action` and `last_transition`
- if `G3` or `R3` finds a code problem, the default is for the same `coder_slot` to continue repair inside the current Initiative and rerun `G3`; only when the repair needs an independent Task contract, a clearly new object boundary, or obviously exceeds the current Initiative closure radius should it be objectized into a repair task through the `Global State Doc` and fall back to `task-loop`
- if a repair task has already been objectized, after the repair completes it must return to the same `Initiative Review Rolling Doc` to append the next round
- if the rolling doc does not exist, initialize the header, including object identity and `coder_slot`, plus `initiative_contract_snapshot`; after initialization, the rolling doc becomes the only collaboration surface

## Workflow

1. Bind the current Initiative
- Read the Initiative definition, the `Global State Doc`, the current `Initiative Review Rolling Doc`, relevant Milestone review docs / supporting evidence, and the necessary engineering facts
- Confirm that the active initiative is unique, the workspace is executable, the rolling doc matches the active initiative, and `coder_slot` is unique
- Confirm that the Initiative has entered the delivery-review window: required Milestones are already clean, and there is no higher-priority blocker
- If the `Global State Doc` conflicts with the rolling doc, hand control back to `rebuild-runtime`
- If the current Initiative cannot be confirmed uniquely, the contract is missing, the delivery-review window has not opened, or the facts show the system should wait for the user, stop
- If the rolling doc does not exist, initialize only the header, including object identity and `coder_slot`, plus `initiative_contract_snapshot`

2. Update the minimum control plane
- `current_snapshot` points to the current active initiative and `coder_slot`
- `next_action` points to continuing the current Initiative coder round
- Record entering the current round, resuming the current round, or coder succession in `last_transition` when needed
- Do not write implementation details, review body text, or full test output into the `Global State Doc`

3. Dispatch the coder
- Continue reusing the same logical `coder_slot` for the current Initiative
- Reuse the current `agent_id` while the physical thread is alive; if it is lost, you may assign a successor `agent_id`, but you must reuse the original `coder_slot` and record the succession
- Default to `fork_context=false`
- The coder input only needs to locate the current formal input surface: current Initiative identity, `design_ref`, `gap_analysis_ref`, `total_task_doc_ref`, the `Global State Doc` path, the current `Initiative Review Rolling Doc` path, and the entry points for the Milestone review docs / supporting evidence included in the Initiative candidate
- The coder returns its result to the `Initiative Review Rolling Doc` according to the contract

4. Handle the coder result
- Decide only from the rolling doc and release / rollout / test facts, not from chat summaries
- Read the latest `g3_result.next_action` first
- If it clearly says "continue repair inside the current Initiative and rerun `G3`": do not enter reviewer; let the same `coder_slot` continue Initiative repair
- If it clearly says "objectize a repair task and fall back to the Task layer": create a repair task bound to the same `coder_slot` in the `Global State Doc`; `last_transition` must record that the repair task came from the current Initiative, which `Initiative Review Rolling Doc` it must return to on completion, and whether the callback should continue the current round or enter the next round; then switch `current_snapshot` to that Task, switch `next_action` to Task repair, and hand control back upstream
- If it clearly says "the current Initiative can now enter `R3`", and the candidate scope, Milestone set, and evidence refs are valid: switch `next_action` to entering `R3`
- If it clearly says to wait for the user, request human judgment, or identifies a real blocker: write waiting/blocked into the `Global State Doc`, then stop
- Only if `next_action` is missing or still not explicit enough should you fall back to compatibility judgment from `verdict` plus surrounding formal facts

5. Dispatch a fresh `initiative_reviewer`
- Every `R3` round uses a freshly spawned reviewer, with `fork_context=false` by default
- The reviewer reads `design_ref`, `gap_analysis_ref`, `total_task_doc_ref`, the `Global State Doc`, the current `Initiative Review Rolling Doc`, the current Initiative candidate's Milestone review docs / supporting evidence, and related release / rollout / deployment / flag / readiness / test facts
- The reviewer returns its result to the `Initiative Review Rolling Doc` according to the contract

6. Handle `r3_result`
- Read the latest `r3_result.next_action` first
- If it clearly says "the Initiative is complete and can enter completion handling": update `last_transition`, move `current_snapshot` forward into the Initiative-done state, switch `next_action` to completion handling, then hand control back upstream
- If it clearly says "continue current Initiative repair": switch `next_action` to continuing current Initiative repair and let the same `coder_slot` enter the next round
- If it clearly says "objectize a repair task": create a repair task bound to the same `coder_slot` only through the `Global State Doc`; `last_transition` must record that the repair task came from the current Initiative, which `Initiative Review Rolling Doc` it must return to on completion, and that the callback should enter the next round; then switch `current_snapshot` to that Task, switch `next_action` to Task repair, and hand control back upstream
- If it clearly says to wait for the user, request human judgment, or identifies a real blocker: the reviewer writes only the recommendation, the `Supervisor` updates only the `Global State Doc`, then hands control back upstream
- Only if `next_action` is missing or still not explicit enough should you fall back to compatibility judgment from `verdict` plus surrounding formal facts

## Stop Conditions

Stop immediately and hand control back upstream or to the user when:
- the active initiative cannot be confirmed uniquely
- the Initiative contract is missing, the Milestone candidate set is missing, or the `Global State Doc` conflicts with the rolling doc
- the Initiative has not entered the delivery-review window yet
- the workspace is not an executable implementation environment, or current facts show the system should wait for the user
- the coder or reviewer exposes a real blocker

## Red Lines

Never:
- enter `R3` without a valid `g3_result`
- silently replace the logical `coder_slot`
- keep a bounded brief, temporary commentary, or chat summary as a second collaboration truth source
- write coder / reviewer body content into the `Global State Doc`
- dispatch multiple coders concurrently for the same Initiative
- let the reviewer repair code
- skip `G3 -> R3`
- forcibly split repair into a repair task when it can still close within the current Initiative
- force repair to stay in the Initiative layer when it should be objectized into a repair task
- claim delivery completion while the Initiative still has an active repair task
- claim the Initiative is clean without `r3_result: clean`

## Completion Criteria

On correct completion, all of the following should be true:
- the current Initiative state can be recovered uniquely from the `Global State Doc` and the `Initiative Review Rolling Doc`
- `coder_slot` continuity is unambiguous
- if the Initiative is clean, the rolling doc already contains a valid `g3_result` and `r3_result`
- if the Initiative is not yet clean, the system is either clearly stopped in current Initiative repair, or has objectized a clear repair task and fallen back to the Task layer when needed
- no second runtime truth source has been created outside the four formal runtime docs
