---
name: milestone-loop
description: Use when the `Global State Doc` has uniquely confirmed that current progress is at a ready or active Milestone; this skill uses single coder ownership to drive the current Milestone through formal `review/repair -> G2 -> fresh R2` closure
---

# Milestone Loop

`milestone-loop` handles only one confirmed Milestone. Here you act as the Milestone-layer `Supervisor`: maintain the minimum control plane, keep a single `coder_slot`, dispatch the same `coder` and a fresh `milestone_reviewer` each round, and use the facts from `G2`, `R2`, and objectized repair tasks when needed to decide whether to continue stage review, repair within the current layer, declare formal clean closure, escalate, or stop.

`coder_slot` is the logical owner identifier, not the physical `agent_id`; the current `agent_id` may change, but `coder_slot` does not.

You are not responsible for writing code, writing `r2_result`, directly repairing Task code, rewriting Initiative-layer dispatch, finishing the development branch, or maintaining any parallel state.

## Truth Sources And Hard Boundaries

The formal input surface contains only the Initiative static truth trio `design_ref`, `gap_analysis_ref`, and `total_task_doc_ref` (`gap_analysis_ref` may be `N/A` for some Initiative types), the `Global State Doc`, the current `Milestone Review Rolling Doc`, the Task anchors / Task review docs included in the current Milestone review, and the necessary Git / PR / merge-base / test facts.

Hard boundaries:
- `G2` may be run only by the coder in the current stage round, and it must be written into the `Milestone Review Rolling Doc`
- `R2` may be run only by a fresh reviewer against the current formal Milestone object
- the current Milestone round closes only when `r2_result` is written; if the coder still needs repair inside the current Milestone during `G2`, it stays in the same round
- the `Milestone Review Rolling Doc` is the only formal document for `G2 / R2`; the `Global State Doc` may contain only `current_snapshot`, `next_action`, and `last_transition`
- if `next_action` changes the active object or active plane, `current_snapshot` must be updated at the same time; only when still advancing within the same Milestone may you update only `next_action` and `last_transition`
- if `G2` or `R2` finds a code problem, the default is for the same `coder_slot` to continue repair inside the current Milestone and rerun `G2`; only when the repair needs an independent Task contract, a clearly new object boundary, or obviously exceeds the current Milestone closure radius should it be objectized into a repair task through the `Global State Doc` and fall back to `task-loop`
- if a repair task has already been objectized, after the repair completes it must return to the same `Milestone Review Rolling Doc` to append the next round
- if the rolling doc does not exist, initialize the header, including object identity and `coder_slot`, plus `milestone_contract_snapshot`; after initialization, the rolling doc becomes the only collaboration surface

## Workflow

1. Bind the current Milestone
- Read the Milestone definition, the `Global State Doc`, the current `Milestone Review Rolling Doc`, relevant Task anchors / Task review docs, and the necessary engineering facts
- Confirm that the active milestone is unique, the workspace is executable, the rolling doc matches the active milestone, and `coder_slot` is unique
- Confirm that the Milestone has entered the stage-review window: required Tasks are already `DONE`, and there is no higher-priority blocker
- If the `Global State Doc` conflicts with the rolling doc, hand control back to `rebuild-runtime`
- If the current Milestone cannot be confirmed uniquely, the contract is missing, the stage-review window has not opened, or the facts show the system should wait for the user, stop
- If the rolling doc does not exist, initialize only the header, including object identity and `coder_slot`, plus `milestone_contract_snapshot`

2. Update the minimum control plane
- `current_snapshot` points to the current active milestone and `coder_slot`
- `next_action` points to continuing the current Milestone coder round
- Record entering the current round, resuming the current round, or coder succession in `last_transition` when needed
- Do not write implementation details, review body text, or full test output into the `Global State Doc`

3. Dispatch the coder
- Continue reusing the same logical `coder_slot` for the current Milestone
- Reuse the current `agent_id` while the physical thread is alive; if it is lost, you may assign a successor `agent_id`, but you must reuse the original `coder_slot` and record the succession
- Default to `fork_context=false`
- The coder input only needs to locate the current formal input surface: current Milestone identity, `design_ref`, `gap_analysis_ref`, `total_task_doc_ref`, the `Global State Doc` path, the current `Milestone Review Rolling Doc` path, and the entry points for the Task anchors / Task review docs included in the Milestone
- The coder returns its result to the `Milestone Review Rolling Doc` according to the contract

4. Handle the coder result
- Decide only from the rolling doc and Git / PR facts, not from chat summaries
- Read the latest `g2_result.next_action` first
- If it clearly says "continue repair inside the current Milestone and rerun `G2`": do not enter reviewer; let the same `coder_slot` continue Milestone repair
- If it clearly says "objectize a repair task and fall back to the Task layer": create a repair task bound to the same `coder_slot` in the `Global State Doc`; `last_transition` must record that the repair task came from the current Milestone, which `Milestone Review Rolling Doc` it must return to on completion, and whether the callback should continue the current round or enter the next round; then switch `current_snapshot` to that Task, switch `next_action` to Task repair, and hand control back upstream
- If it clearly says "the current Milestone can now enter `R2`", and the object scope, anchor set, and evidence refs are valid: switch `next_action` to entering `R2`
- If it clearly says to wait for the user, request human judgment, or identifies a real blocker: write waiting/blocked into the `Global State Doc`, then stop
- Only if `next_action` is missing or still not explicit enough should you fall back to compatibility judgment from `verdict` plus surrounding formal facts

5. Dispatch a fresh `milestone_reviewer`
- Every `R2` round uses a freshly spawned reviewer, with `fork_context=false` by default
- The reviewer reads `design_ref`, `gap_analysis_ref`, `total_task_doc_ref`, the `Global State Doc`, the current `Milestone Review Rolling Doc`, the current Milestone anchor set, necessary Task review docs, and relevant PR / merge-base / test facts
- The reviewer returns its result to the `Milestone Review Rolling Doc` according to the contract

6. Handle `r2_result`
- Read the latest `r2_result.next_action` first
- If it clearly says "enter the higher-level review entry" or "select the next ready object": update `last_transition`, move `current_snapshot` forward to the corresponding entry point, then hand control back upstream
- If it clearly says "continue current Milestone repair": switch `next_action` to continuing current Milestone repair and let the same `coder_slot` enter the next round
- If it clearly says "objectize a repair task": create a repair task bound to the same `coder_slot` only through the `Global State Doc`; `last_transition` must record that the repair task came from the current Milestone, which `Milestone Review Rolling Doc` it must return to on completion, and that the callback should enter the next round; then switch `current_snapshot` to that Task, switch `next_action` to Task repair, and hand control back upstream
- If it clearly says to wait for the user, request human judgment, or identifies a real blocker: the reviewer writes only the recommendation, the `Supervisor` updates only the `Global State Doc`, then hands control back upstream
- Only if `next_action` is missing or still not explicit enough should you fall back to compatibility judgment from `verdict` plus surrounding formal facts

## Stop Conditions

Stop immediately and hand control back upstream or to the user when:
- the active milestone cannot be confirmed uniquely
- the Milestone contract is missing, the anchor set is missing, or the `Global State Doc` conflicts with the rolling doc
- the Milestone has not entered the stage-review window yet
- the workspace is not an executable implementation environment, or current facts show the system should wait for the user
- the current problem clearly exceeds Milestone radius and must escalate to Initiative
- the coder or reviewer exposes a real blocker

## Red Lines

Never:
- enter `R2` without a valid `g2_result`
- silently replace the logical `coder_slot`
- keep a bounded brief, temporary commentary, or chat summary as a second collaboration truth source
- write coder / reviewer body content into the `Global State Doc`
- dispatch multiple coders concurrently for the same Milestone
- let the reviewer repair code
- skip `G2 -> R2`
- forcibly split repair into a repair task when it can still close within the current Milestone
- force repair to stay in the Milestone layer when it should be objectized into a repair task
- switch to Initiative closure while the Milestone still has an active repair task
- claim the Milestone is clean without `r2_result: clean`

## Completion Criteria

On correct completion, all of the following should be true:
- the current Milestone state can be recovered uniquely from the `Global State Doc` and the `Milestone Review Rolling Doc`
- `coder_slot` continuity is unambiguous
- if the Milestone is clean, the rolling doc already contains a valid `g2_result` and `r2_result`
- if the Milestone is not yet clean, the system is either clearly stopped in current Milestone repair, or has objectized a clear repair task and fallen back to the Task layer when needed
- no second runtime truth source has been created outside the four formal runtime docs
