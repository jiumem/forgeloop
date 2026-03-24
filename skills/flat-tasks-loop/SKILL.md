---
name: flat-tasks-loop
description: Use when you have a written implementation plan and need to execute it as a single milestone through a serial flattened task list
---

# Flat Tasks Loop

## Overview

Load a written plan, flatten its executable tasks into one serial list, dispatch `forgeloop:task-loop` for each task in order, and complete the milestone only after the whole flattened list is done.

**Announce at start:** "I'm using the flat-tasks-loop skill to implement this plan."

**Core rule:** Treat the input plan as one milestone. Do not preserve nested phases, batches, or internal hierarchy while executing. Extract the actionable tasks, flatten them into one ordered sequence, and run them serially from top to bottom.

**Dispatcher rule:** Once you are in this skill, you MUST invoke `forgeloop:task-loop` for each flattened task in sequence. Do not implement flattened tasks directly in this skill. `flat-tasks-loop` is the serial milestone-level dispatcher; `task-loop` is the required atomic adversarial coding loop for each task.

## The Process

### Step 1: Read Plan
1. Read the plan file
2. Identify the executable tasks, task groupings, and stated verification steps
3. Record a lightweight plan identity anchor before doing anything else:
   - plan path
   - plan title
   - a cheap version marker such as git blob identity, file hash, or equivalent
4. Do not start flattening or dispatching yet

### Step 2: Execution Precheck
Before flattening, confirm the plan is execution-ready for this skill:
1. The plan can be flattened into one unambiguous serial task list
2. Each task is bounded enough to become a `task-loop` packet
3. Dependencies and ordering are clear enough to run top-to-bottom
4. Required verification commands and execution prerequisites are present

If any of these checks fail, stop and raise the blocker with your human partner before continuing.

**Boundary of the precheck:**
- Do execution-readiness checking only
- Do not rewrite the plan
- Do not re-open design or planning
- Do not perform milestone-wide review here

### Step 3: Environment Preparation
After the precheck passes, prepare an isolated implementation environment:
1. Invoke `forgeloop:using-git-worktrees` to ensure the implementation environment is ready
2. Let that skill decide whether to reuse the current workspace or create a new worktree
3. Let that skill handle workspace selection, setup, and clean baseline verification
4. In the implementation environment, verify that the plan file still exists and matches the recorded plan identity anchor
5. Do not re-read the whole plan unless the identity check fails
6. Only continue once the implementation environment is ready and the plan identity is confirmed

If the plan file is missing or the identity check does not match, stop and surface the problem. Do not continue with a stale or invisible plan.

From this point on, all flattening, task dispatch, verification, and completion work must happen in the implementation workspace returned by `forgeloop:using-git-worktrees`.

### Step 4: Flatten Tasks
1. Flatten all executable tasks into one ordered task list
2. Ignore internal grouping for execution purposes; phases and sections are reference only
3. For each flattened task, preserve a lightweight source anchor back to the original plan entry:
   - plan path
   - original section or phase
   - original task title or number
   - flattened task label used in `update_plan`
4. Ensure every flattened task label is unique within the milestone; if original task titles collide, prefix them with enough section or phase context to disambiguate them
5. Create an `update_plan` checklist from the flattened list, using the unique flattened task labels as the tracking surface

### Step 5: Execute Tasks

For each flattened task in order:
1. Mark the task as `in_progress`
2. Build a bounded task packet with the task text, acceptance criteria, surrounding context, constraints, verification commands, and the preserved source anchor
3. Invoke `forgeloop:task-loop` for that single task packet
4. Let `task-loop` carry the implement -> spec review -> code review -> fix cycle
5. If `task-loop` returns blocked, stop the milestone and surface the blocker using both the flattened task label and its original source anchor
6. If `task-loop` returns non-blocking concerns, record them at the milestone level alongside the same flattened task label and source anchor
7. If the task completes, confirm the result is real and mark it as completed using the same flattened label and source anchor

Do not parallelize. Do not jump ahead. Do not reopen plan structure mid-run unless blocked.

### Step 6: Complete Development

After the full flattened task list is complete:
- Run any milestone-level verification required by the plan
- Announce: "I'm using the finishing-a-development-branch skill to complete this work."
- **REQUIRED SUB-SKILL:** Use `forgeloop:finishing-a-development-branch`
- Follow that skill to verify tests, present options, and execute the chosen integration path

## When to Stop and Ask for Help

**STOP executing immediately when:**
- Hit a blocker (missing dependency, test fails, instruction unclear)
- Precheck fails or plan has critical gaps preventing starting
- You don't understand an instruction
- Verification fails repeatedly
- The plan cannot be flattened into an unambiguous serial task list

Ask for clarification rather than guessing.

## When to Revisit Earlier Steps

**Return to Review (Step 1) when:**
- Partner updates the plan based on your feedback
- Fundamental approach needs rethinking

Do not force through blockers. Stop and ask.

## Remember

- Review the plan critically first
- Run execution precheck before flattening
- Prepare the isolated environment only after precheck passes
- Carry a lightweight plan identity anchor across environment changes
- Stay in the implementation workspace returned by `using-git-worktrees`
- Flatten tasks into one ordered list before starting
- Preserve a source anchor for every flattened task
- Make every flattened task label unique within the milestone
- Follow flattened task order exactly
- Build a proper packet for each task before invoking `task-loop`
- Record non-blocking task concerns instead of dropping them
- Do not skip verifications
- Reference skills when the plan says to
- Stop when blocked; do not guess
- Never start implementation on main/master branch without explicit user consent
- Do not let `task-loop` take over milestone sequencing or branch finishing

## Integration

**Required workflow skills:**
- **forgeloop:using-git-worktrees** - Set up an isolated workspace before starting
- **forgeloop:task-loop** - Executes each flattened task as the atomic adversarial coding loop
- **forgeloop:finishing-a-development-branch** - Completes development after all tasks
