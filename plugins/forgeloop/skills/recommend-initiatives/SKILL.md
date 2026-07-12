---
name: recommend-initiatives
description: Load when the user explicitly asks what evidence-backed engineering initiative the repository should tackle next.
---

# Recommend Engineering Initiatives

Return a small set of verifiable candidates in the conversation so the user can choose the next piece of work worth designing. Remain read-only. Do not create repository files, Tracker Items, Specs, Tickets, or implementation branches.

## Investigate

1. Read the repository instructions, `CONTEXT.md`, relevant ADRs, and user-stated goals.
2. Investigate the code, tests, CI configuration, recent changes, and existing Tracker requests. When a Tracker is configured, query it read-only according to `docs/agents/issue-tracker.md`. Report authentication, permission, or network failures explicitly; never present them as "no requests found."
3. Collect locatable evidence: files and line numbers, failure output, repeated patterns, open requests, ADR constraints, or a missing public seam.
4. Search across categories, considering at least product value, reliability, architectural depth, testing/developer experience, and operational risk. Cross-category means considering every category, not forcing category quotas; the final candidates may cluster in the category with the strongest evidence.

## Filter

Keep only 1–3 candidates that satisfy all of the following:

- Address a real user or maintenance goal rather than generic cleanup.
- Require enough coordinated steps to justify an Initiative rather than one directly actionable Ticket.
- Have at least two independent pieces of repository evidence, or one repository fact plus one stated user goal.
- Do not duplicate an open Initiative or violate an ADR.
- Support a clear success signal, primary risk, and next entry point.

Put small changes that can be completed safely in one session under "Not recommended: suitable as a direct task" instead of inflating them into Initiatives. When product goals are missing, engineering candidates may still be reported, but set product-value confidence to low and state that the evidence comes only from repository health. Never invent a roadmap, user demand, or business priority.

## Output

Report the investigation coverage and inaccessible sources first, then list each candidate in recommendation order:

```text
Candidate: <outcome-oriented name>
Category: <product value | reliability | architecture | testing/developer experience | operations>
Problem: <currently observable problem>
Evidence: <at least two reviewable references>
Value: <result for users or maintainers>
Boundary: <what is explicitly excluded>
Success signal: <executable or observable measure>
Risk: <highest risk and unknowns>
Deduplication: VERIFIED | UNVERIFIED (<reason>)
Confidence: HIGH | MEDIUM | LOW (<reason>)
Suggested entry: $grill-with-docs | $wayfinder
```

When the Tracker is unavailable, mark every candidate's deduplication as `UNVERIFIED` and lower its confidence. Restore read-only Tracker access and deduplicate again before entering a later Workflow.

End with the preferred candidate and the reason for choosing it. Recommend the next entry point only; do not automatically start another user-only Workflow.

## Terminal states

- `COMPLETE`: Return 1–3 well-supported candidates.
- `EMPTY`: Evidence is insufficient to form a candidate. List the sources checked and the minimum additional information needed without inventing recommendations.
- `PARTIAL`: A source is unavailable because of missing configuration, failed authentication, insufficient permission, or a network error. Keep verifiable candidates and report the failed source, error kind, original diagnostic, completed scope, recovery action, and safe retry point. When the Tracker is unavailable, use `UNVERIFIED` deduplication and reduced confidence; restore access and recheck before entering a later Workflow.
- `CANCELLED`: Stop immediately when the user cancels and write no artifacts.

Never write to `docs/initiatives/recommendations/**`, create a Spec or Ticket, or modify production code.
