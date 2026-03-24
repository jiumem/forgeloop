---
name: flat-tasks-loop
description: Use when you have a written implementation plan and need to execute it as a single milestone through a serial flattened task list
---

# Flat Tasks Loop

## Overview

Load a written plan, flatten its executable tasks into one serial list, execute them as a single milestone, and report when complete.

**Announce at start:** "I'm using the flat-tasks-loop skill to implement this plan."

**Note:** If Codex subagents are available, prefer `forgeloop:task-loop`. This skill exists for inline execution when you intentionally stay in one session.

**Core rule:** Treat the input plan as one milestone. Do not preserve nested phases, batches, or internal hierarchy while executing. Extract the actionable tasks, flatten them into one ordered sequence, and run them serially from top to bottom.

## The Process

### Step 1: Load and Review Plan
1. Read plan file
2. Review critically - identify any questions or concerns about the plan
3. Flatten all executable tasks into one ordered task list
4. Ignore internal grouping for execution purposes - phases and sections are reference only
5. If concerns: Raise them with your human partner before starting
6. If no concerns: create `update_plan` checklist from the flattened list and proceed

### Step 2: Execute Tasks

For each flattened task in order:
1. Mark as in_progress
2. Follow each step exactly (plan has bite-sized steps)
3. Run verifications as specified
4. Mark as completed

Do not parallelize. Do not jump ahead. Do not reopen plan structure mid-run unless blocked.

### Step 3: Complete Development

After the full flattened task list is complete and verified:
- Announce: "I'm using the finishing-a-development-branch skill to complete this work."
- **REQUIRED SUB-SKILL:** Use forgeloop:finishing-a-development-branch
- Follow that skill to verify tests, present options, execute choice

## When to Stop and Ask for Help

**STOP executing immediately when:**
- Hit a blocker (missing dependency, test fails, instruction unclear)
- Plan has critical gaps preventing starting
- You don't understand an instruction
- Verification fails repeatedly
- The plan cannot be flattened into an unambiguous serial task list

**Ask for clarification rather than guessing.**

## When to Revisit Earlier Steps

**Return to Review (Step 1) when:**
- Partner updates the plan based on your feedback
- Fundamental approach needs rethinking

**Don't force through blockers** - stop and ask.

## Remember
- Review plan critically first
- Flatten tasks into one ordered list before starting
- Follow flattened task order exactly
- Don't skip verifications
- Reference skills when plan says to
- Stop when blocked, don't guess
- Never start implementation on main/master branch without explicit user consent

## Integration

**Required workflow skills:**
- **forgeloop:using-git-worktrees** - REQUIRED: Set up isolated workspace before starting
- **forgeloop:writing-plans** - Creates the plan this skill executes
- **forgeloop:finishing-a-development-branch** - Complete development after all tasks
