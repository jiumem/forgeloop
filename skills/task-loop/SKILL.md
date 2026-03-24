---
name: task-loop
description: Use when one bounded implementation task is ready to enter a subagent-driven implement-review-fix loop
---

# Task Loop

Execute exactly one bounded task packet through a fresh `implementer`, then ordered `spec_reviewer` and `code_reviewer` loops, until the task is complete or explicitly blocked.

If you are reading this skill body, the workflow has already reached the point where subagents are required to move the task forward. Do not ask the user whether to enable subagents; start the task loop.

**Boundary rule:** `task-loop` does not read a whole plan, does not schedule multiple tasks, and does not finish the development branch. The main agent or upstream workflow owns plan parsing, task ordering, milestone tracking, and final branch completion. `task-loop` owns only one task at a time.

**Why subagents:** You delegate one task to specialized agents with isolated context. By precisely crafting the task packet, you keep them focused on the bounded work instead of rediscovering requirements from your session history.

**Core principle:** One task packet + fresh implementer context + ordered review loops = reliable task closure

**Codex-native orchestration rule:** `implementer` is a long-lived task-local subagent. Spawn it once, save its `agent_id`, and reuse it for fix rounds via `send_input`. `spec_reviewer` and `code_reviewer` are fresh short-lived reviewers. Spawn a new reviewer each round. Unless there is a specific reason to fork history, all three agents should be spawned with `fork_context=false`.

## The Process

### Step 1: Build the Task Packet

Before dispatching, assemble the exact packet for this one task:

- Full task text
- Acceptance criteria
- Relevant repo and module context
- Related files, APIs, or prior tasks this task depends on
- Constraints, non-goals, and migration notes
- Required verification commands
- Source anchor, if the main agent or upstream workflow supplied one

Also establish the task-local review boundary before the implementer starts work:

- Record the starting commit or equivalent task-local base point
- Treat this task-local boundary as the only scope reviewers should inspect
- Do not let task-local review drift into unrelated branch changes

Do not make the implementer rediscover the task from a whole plan file if you can provide the bounded packet directly.

### Step 2: Dispatch `implementer`

Spawn the `implementer` custom agent with the full task packet.

Codex control-plane requirements:
- Use `spawn_agent` once for the implementer
- Set `fork_context=false` unless you have a specific reason to fork history
- Save the returned `agent_id`
- Treat that `agent_id` as the task's implementation thread for the rest of the loop

The implementer should handle:
- Implementation
- Test updates or additions
- Local verification
- Self-review before handing work back

### Step 3: Handle Implementer Status

Use `wait_agent` when you are blocked on the implementer's result.

Implementer subagents report one of four statuses. Handle each deliberately:

**DONE:** Proceed to spec review.

**DONE_WITH_CONCERNS:** Read the concerns before proceeding. If the concern affects correctness, scope, migration safety, or verification, resolve it before review. If that concern cannot be resolved within the current task packet, do not continue as if the task is healthy - convert the situation into `NEEDS_CONTEXT` or `BLOCKED` and stop the loop until the issue is handled.

**NEEDS_CONTEXT:** Provide the missing context to the same implementer via `send_input`, then `wait_agent` on that same `agent_id` again. Do not spawn a replacement implementer just because more context is needed.

**BLOCKED:** Stop the loop and assess the blocker:
1. Provide missing context and retry
2. Re-dispatch only if you intentionally restart the implementer thread
3. Split the task if the task packet is too large
4. Escalate to the human if the plan or requirement is wrong

Before leaving this step with a healthy implementation result, capture the task-local review inputs:
- touched files for this task
- task-local head point after the implementer round
- verification evidence the implementer produced

### Step 4: Run the Spec Review Loop First

Dispatch a fresh `spec_reviewer` with:
- the original task packet
- the source anchor, if present
- the task-local review boundary
- the task-local touched files
- the task-local verification evidence
- the implementer result

Codex control-plane requirements:
- Spawn a new `spec_reviewer` each review round
- Set `fork_context=false`
- Do not reuse prior reviewer threads
- `wait_agent` for the review result before proceeding

If the spec reviewer finds issues:
1. Use `send_input` to the same `implementer` `agent_id` with the reviewer findings; the original task packet remains authoritative
2. Fix only the reported gaps or incorrect additions without dropping the original task boundaries
3. `wait_agent` on the same implementer
4. Refresh the task-local review inputs after the implementer finishes the fix round:
   - touched files for this task
   - task-local head point after the fix round
   - verification evidence for the updated implementation
5. Spawn a fresh `spec_reviewer` and review again within the updated task-local boundary

Do not start code quality review until spec compliance is approved.

### Step 5: Run the Code Review Loop Second

After spec review passes, dispatch a fresh `code_reviewer` with:
- the original task packet
- the source anchor, if present
- the task-local review boundary
- the task-local touched files
- the task-local verification evidence
- the implementer result

Codex control-plane requirements:
- Spawn a new `code_reviewer` each review round
- Set `fork_context=false`
- Do not reuse prior reviewer threads
- Interpret the reviewer output as a task-slice readiness assessment, not a whole-branch merge gate
- `wait_agent` for the review result before proceeding

If the code reviewer finds issues:
1. Use `send_input` to the same `implementer` `agent_id` with the reviewer findings; the original task packet remains authoritative
2. Fix the reported quality or risk issues without replacing the original task packet with a narrower reviewer summary
3. `wait_agent` on the same implementer
4. Refresh the task-local review inputs after the implementer finishes the fix round:
   - touched files for this task
   - task-local head point after the fix round
   - verification evidence for the updated implementation
5. Spawn a fresh `code_reviewer` and review again within the updated task-local boundary

Repeat until the task is approved or explicitly blocked.

### Step 6: Record the Task Result in the Main Agent

When the loop finishes, the main agent should record a concise task result:

- Status: complete or blocked
- What changed
- What verification passed
- Any remaining concerns that do not block task completion
- The source anchor from the upstream workflow, unchanged if one was supplied

The main agent then decides whether to mark a milestone task complete, advance to the next task, request wider review, or stop.

## Example Workflow

```
You: I'm using Task Loop for this bounded task.

Task packet:
- Task: Add config validation for invalid enum values
- Acceptance: reject invalid values, surface validation error, cover CLI + config file paths
- Context: parser lives in src/config.ts, current tests in tests/config.test.ts
- Verification: npm test -- config

[Dispatch `implementer` with the task packet]

Implementer: "Before I begin - should invalid values fail closed or fall back to defaults?"

You: "Fail closed and return a validation error."

Implementer: "Got it. Implementing now..."
[Later] Implementer:
  - Implemented config validation
  - Added tests, 5/5 passing
  - Self-review: all good

[Dispatch `spec_reviewer`]
Spec reviewer: ✅ Spec compliant - all requirements met, nothing extra

[Dispatch `code_reviewer`]
Code reviewer: Strengths: Good test coverage, clean. Issues: None. Approved.

You:
- Status: complete
- Changed: src/config.ts, tests/config.test.ts
- Verification: npm test -- config
- Concerns: none
```

## Red Flags

**Never:**
- Start implementation on main/master branch without explicit user consent
- Skip reviews (spec compliance OR code quality)
- Proceed with unfixed issues
- Dispatch multiple implementation subagents for the same task in parallel
- Hand the implementer an entire milestone when one bounded task will do
- Make `task-loop` own milestone sequencing or branch finishing
- Skip scene-setting context
- Ignore subagent questions
- Accept "close enough" on spec compliance
- Skip review loops
- Let implementer self-review replace actual review
- Start code quality review before spec compliance is approved
- Claim the task is done without verification evidence
- Let reviewer findings replace the original task packet during fix rounds
- Re-spawn the implementer for normal fix rounds instead of reusing its `agent_id`
- Spawn reviewers with `fork_context=true` without a specific reason
- Let reviewers inspect branch-wide changes when a task-local review boundary is available

**If subagent asks questions:**
- Answer clearly and completely
- Provide additional context if needed
- Don't rush them into implementation

**If reviewer finds issues:**
- Implementer fixes them
- Reviewer reviews again
- Repeat until approved
- Reuse the same implementer agent via `send_input`, but use a fresh reviewer agent each round

## Used By

- **forgeloop:flat-tasks-loop** - Uses `task-loop` as the required atomic loop for each flattened task
- Direct single-task execution by the main agent - When exactly one bounded task packet is already ready
