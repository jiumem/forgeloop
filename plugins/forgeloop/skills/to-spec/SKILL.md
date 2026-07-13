---
name: to-spec
description: Load when the user explicitly wants already-discussed and sufficiently resolved context published as a formal Tracker Spec.
---

This skill takes the current conversation context and codebase understanding and produces a spec (you may know this document as a PRD). Do NOT interview the user — just synthesize what you already know.

A configured Issue Tracker must already exist before publication. If `docs/agents/issue-tracker.md` is missing, do not run `$setup-forgeloop` automatically. Return `FAILED_PRECONDITION`, identify the missing configuration, and instruct the user to invoke `$setup-forgeloop` explicitly. Do not write any Spec or Tracker state.

## Process

1. Explore the repo to understand the current state of the codebase, if you haven't already. Use the project's domain glossary vocabulary throughout the spec, and respect any ADRs in the area you're touching.

2. Sketch out the seams at which you're going to test the feature. Existing seams should be preferred to new ones. Use the highest seam possible. If new seams are needed, propose them at the highest point you can. The fewer seams across the codebase, the better - the ideal number is one.

Check with the user that these seams match their expectations.

3. Before writing or publishing, enforce the Forgeloop publication gates:

   - No interview does not mean inventing decisions. If the current context still lacks the Problem, Actor, target behavior, key failure states, user or role permission model, Scope, public Seam, or irreversible constraints, return `CONTEXT_INSUFFICIENT` and list each gap. Do not generate or publish a draft, and do not fill in decisions on the user's behalf.
   - Confirm that the user approved the test Seam from step 2.
   - Read the configured Tracker Operations and, before the first write, verify authentication, Tracker publication permission, and target conflicts. On failure, return `FAILED_PRECONDITION`, leave the Spec unpublished, and do not fall back to another Tracker.

   After all gates pass, write the Spec using the template below and publish it exactly once to the configured project Issue Tracker. Build its canonical title as `[Spec] <outcome-oriented title>` and render the `[Spec]` prefix exactly once, even when the supplied title already contains a canonical or legacy prefix. Use that canonical title for conflict checks, duplicate queries, and publication. Following the upstream publication rule, add `ready-for-agent` to the parent Spec. On the parent item, this label means the Spec is sufficiently defined to proceed to ticket decomposition or execution orchestration; it does not make the parent Spec part of the Ticket Frontier. Execution state for child Tickets remains the responsibility of `$to-tickets`. If the publication result is ambiguous, first query candidates by the expected title and verify their bodies. Retry only after confirming that an identical Spec does not exist, to avoid creating a duplicate parent Spec.

<spec-template>

## Problem Statement

The problem that the user is facing, from the user's perspective.

## Solution

The solution to the problem, from the user's perspective.

## User Stories

A LONG, numbered list of user stories. Each user story should be in the format of:

1. As an <actor>, I want a <feature>, so that <benefit>

<user-story-example>
1. As a mobile bank customer, I want to see balance on my accounts, so that I can make better informed decisions about my spending
</user-story-example>

This list of user stories should be extremely extensive and cover all aspects of the feature.

## Implementation Decisions

A list of implementation decisions that were made. This can include:

- The modules that will be built/modified
- The interfaces of those modules that will be modified
- Technical clarifications from the developer
- Architectural decisions
- Schema changes
- API contracts
- Specific interactions

Do NOT include specific file paths or code snippets. They may end up being outdated very quickly.

Exception: if a prototype produced a snippet that encodes a decision more precisely than prose can (state machine, reducer, schema, type shape), inline it within the relevant decision and note briefly that it came from a prototype. Trim to the decision-rich parts — not a working demo, just the important bits.

## Testing Decisions

A list of testing decisions that were made. Include:

- A description of what makes a good test (only test external behavior, not implementation details)
- Which modules will be tested
- Prior art for the tests (i.e. similar types of tests in the codebase)

## Out of Scope

A description of the things that are out of scope for this spec.

## Further Notes

Any further notes about the feature.

</spec-template>
