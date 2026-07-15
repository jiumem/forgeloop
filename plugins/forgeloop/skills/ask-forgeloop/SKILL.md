---
name: ask-forgeloop
description: Load when the user explicitly asks which Forgeloop skill or workflow fits their current engineering situation.
---

# Ask Forgeloop

First identify the user's current stage, then recommend one primary entry point and at most one alternative. Explain the rationale and expected output, but do not start another user-only Workflow on the user's behalf.

## User Entry Points

- Configure the Tracker, integration policy, and domain documentation for the first time: `$setup-forgeloop`.
- Find 1–3 candidates for what to tackle next from repository evidence: `$recommend-initiatives`.
- Clarify a design one item at a time within a single session while maintaining domain documentation: `$grill-with-docs`.
- For a large ambiguous problem spanning multiple sessions, first create an exploration Map: `$wayfinder`.
- Publish sufficiently discussed context as a Spec: `$to-spec`.
- Split an approved Spec into independently verifiable vertical Tickets: `$to-tickets`.
- Execute Tracker-driven delivery from a formal Spec or persisted Initiative: `$run-initiative`.
- Route external Issues, PRs, or MRs: `$triage`.
- Perform a focused scan for genuine Deepening Opportunities: `$improve-codebase-architecture`.
- Hand the temporary context required for continuation to a new session: `$handoff`.

`$ask-forgeloop` is itself a user entry point, but it only performs routing.

## Model-Level Capabilities

Recommend `$code-review` when implemented code needs review against its intended behavior or repository standards, and recommend `$diagnosing-bugs` when a difficult defect needs diagnosis. Other Primitives (`$grilling`, `$domain-modeling`, `$primary-source-research`, `$prototype`, `$tdd`, `$codebase-design`, and `$resolving-merge-conflicts`) are normally invoked by the workflows above within their existing authorization boundaries, but may also be used when the task requires the corresponding capability.

## Routing Rules

1. When there is no formal Spec reference, do not recommend running `$run-initiative` directly; complete the design, Spec, or Tickets first.
2. Do not expand a problem that can be understood in a single session into a `$wayfinder` Map.
3. When the user requests only a read-only investigation, diagnosis, or review, do not recommend a write-oriented entry point.
4. When configuration is missing, recommend `$setup-forgeloop` first; do not assume a Tracker or Integration Policy.
5. If no entry point fits, state the boundary clearly and do not invent an unpublished Skill.

Output `RECOMMENDED`, `ALTERNATIVE`, `WHY`, and `REQUIRED_INPUT`. If information is insufficient, ask only one high-impact question whose answer would change the routing result.
