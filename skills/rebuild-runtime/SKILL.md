---
name: rebuild-runtime
description: Use when the runtime control plane is missing, conflicting, or cannot uniquely recover the current next step; this skill reads the static truth sources, the Global State Doc, review rolling docs, and necessary Git facts to rebuild the minimum control plane needed to continue dispatch
---

# Rebuild Runtime

`rebuild-runtime` does recovery only. It does not code, it does not review, and it does not replace `run-initiative` for ongoing dispatch. Here you act as a recovery-state `Supervisor`: rebuild the minimum runnable control plane from the formal truth sources and engineering facts, then hand the system back upstream.

## Truth Sources And Hard Boundaries

The formal input surface contains only the Initiative static truth trio `design_ref`, `gap_analysis_ref`, and `total_task_doc_ref` (`gap_analysis_ref` may be `N/A` for some Initiative types), the `Global State Doc`, the three layers of review rolling docs, and the necessary Git / PR / commit / test facts.

Hard boundaries:
- recover only the logical `coder_slot`, never the physical `agent_id`
- write to the `Global State Doc` only when necessary
- if the `Global State Doc` does not exist, you may initialize `global_state_header`
- if the existing `global_state_header` conflicts with static truth-source bindings, you may correct `global_state_header` first
- the only updatable blocks are `global_state_header`, `current_snapshot`, `next_action`, and `last_transition`
- do not write any rolling doc body content
- do not modify the static truth sources and do not create a second state model in JSON / notes / hidden memory

## When To Trigger

Trigger only in the following situations:
- the `Global State Doc` is missing, but rolling docs already exist
- the `Global State Doc` clearly conflicts with the total task doc or the rolling docs
- `task-loop`, `milestone-loop`, or `initiative-loop` finds that the control plane cannot be recovered uniquely when binding an object
- the original thread cannot continue, but the formal docs and Git facts are still sufficient for recovery

This skill does not handle the following:
- a new Initiative cold start with no runtime docs at all
- cases that only need an implementation environment and should call skill: `using-git-worktrees`
- cases where the current next step is already clear and recovery is unnecessary

## Workflow

1. Bind the recovery surface
- Read `total_task_doc_ref`, the existing `Global State Doc`, and the three rolling docs
- If the static truth sources are missing, or the Initiative binding cannot be confirmed uniquely, stop and ask the user directly
- If there is no rolling doc at all and no `Global State Doc`, treat it as a cold start, hand control back upstream, and do not write runtime state

2. Determine the current formal frontier
- First respect waiting / blocked / done signals that are consistent with the newer formal facts
- Otherwise, use the newest formal frontier that has not yet closed as the active candidate
- If multiple candidates coexist, the fixed priority is: active Task repair / coder round > active Milestone review / repair > active Initiative review / repair > frontier selection after the last clean object
- Chat summaries, cache, and session memory never participate in adjudication

3. Determine the active object and next action
- Read the latest formal block's explicit `next_action` first. If it does not conflict with object facts and the intended next step is clear enough, recover from that `next_action` first.
- If the current active task is a repair task objectized from an upper-layer object, and `last_transition` still clearly records its source Milestone / Initiative, return-hook rolling doc, and callback round semantics, treat that callback information as the primary basis for recovering the upper loop. Do not misread it as an ordinary standalone Task that already ended.
- `coder_slot` recovery rules:
  - if `current_snapshot.coder_slot` in the existing `Global State Doc` is still consistent with the newest formal facts, reuse it directly
  - if the `Global State Doc` is missing or distorted, recover `coder_slot` from the header of the rolling doc judged to be active
  - if the active rolling doc header lacks `coder_slot`, or multiple candidates provide conflicting `coder_slot` values, stop and ask the user directly
- Task candidates:
  - if the latest `r1_result.next_action` clearly says to continue current Task repair, that the Task is complete, to select the next ready object, to wait for the user, or that there is a blocker, recover from it first
  - if the current Task is a repair task with callback information and `r1_result=clean`, prefer recovering the next step of its source Milestone / Initiative rather than ordinary frontier selection
  - if there is only `coder_update`, or the latest `g1_result=fail`: continue the current Task coder round
  - if `g1_result=pass` and a valid `anchor/fixup` exists but there is no `r1_result`: enter `R1`
  - if `r1_result=changes_requested`: continue current Task repair
  - if `r1_result=clean`: enter `task_done` or `select_next_ready_object`
- Milestone candidates:
  - if the latest `g2_result.next_action` or `r2_result.next_action` clearly says to continue current Milestone repair, objectize a repair task, enter `R2`, enter the higher-level review entry, select the next ready object, wait for the user, or identifies a blocker, recover from it first
  - if `g2_result=repair_required` or `r2_result=changes_requested` and the issue is still inside the current Milestone radius: continue current Milestone repair
  - if a repair task has already been formally objectized: the active plane returns to Task
  - if `g2_result=pass` and there is no `r2_result`: enter `R2`
  - if `r2_result=clean`: enter frontier selection or Initiative review entry
- Initiative candidates:
  - if the latest `g3_result.next_action` or `r3_result.next_action` clearly says to continue current Initiative repair, objectize a repair task, enter `R3`, that the Initiative is complete, to wait for the user, or identifies a blocker, recover from it first
  - if `g3_result=repair_required` or `r3_result=changes_requested` and the issue is still inside the current Initiative radius: continue current Initiative repair
  - if a repair task has already been formally objectized: the active plane returns to Task
  - if `g3_result=pass` and there is no `r3_result`: enter `R3`
  - if `r3_result=clean`: enter Initiative done / delivery complete
- Only if the newer formal block lacks `next_action`, or the `next_action` wording is still insufficient to determine the next step uniquely, should you fall back to inference from the old `verdict` plus surrounding formal facts. If that still conflicts or is still not unique, stop and ask the user directly.
- If the active plane, active object, or next action still cannot be determined uniquely, stop and ask the user directly.

4. Rewrite the minimum control plane
- If the `Global State Doc` does not exist, initialize `global_state_header` first
- If the existing `global_state_header` conflicts with the Initiative binding or the planning doc ref, correct `global_state_header` first
- Write `current_snapshot` as the uniquely recovered active plane / active object / `coder_slot`
- Write `next_action` as the uniquely recovered next step
- Write `last_transition` as a recovery transition explaining why the control plane was rebuilt
- After writing, immediately hand control back to skill: `run-initiative` so the upstream dispatcher can reconfirm and continue

## Stop Conditions

Stop immediately and hand control back upstream or to the user when:
- the Initiative binding or static truth sources cannot be confirmed uniquely
- multiple active candidates coexist and Git / formal docs still cannot break the tie
- the rolling docs conflict with each other and it is impossible to tell which side is newer
- there are no runtime docs and the case should be handled as a cold start
- the facts show the system should wait for the user, but the waiting reason cannot be stated formally

## Red Lines

Never:
- write rolling doc body content
- recover a physical owner / thread id as formal state
- let an outdated `Global State Doc` override newer rolling-doc facts
- treat chat memory, cache, or local derived hints as formal truth sources
- silently guess the active object, `coder_slot`, or next action

## Completion Criteria

On correct completion, all of the following should be true:
- the current active plane, active object, and `coder_slot` can be recovered uniquely
- the `Global State Doc` exists, and `current_snapshot`, `next_action`, and `last_transition` are self-consistent
- the upstream dispatcher can re-enter `run-initiative` and continue without hidden context
- no second runtime truth source has been created outside the four formal runtime docs
