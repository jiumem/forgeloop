# Plan Reviewer Dispatch Template

Use this template when dispatching the `plan_reviewer` custom agent.

**Purpose:** Verify the plan is complete, matches the spec, and has proper task decomposition.

**Dispatch after:** The complete plan is written.

## Input Contract

- `PLAN_FILE_PATH`
- `SPEC_FILE_PATH`

## Review Focus

| Category | What to Look For |
|----------|------------------|
| Completeness | TODOs, placeholders, incomplete tasks, missing steps |
| Spec Alignment | Plan covers spec requirements, no major scope creep |
| Task Decomposition | Tasks have clear boundaries, steps are actionable |
| Buildability | Could an engineer follow this plan without getting stuck? |

## Boundary

- Review the plan against the spec, not against your preferred architecture
- Flag only issues that would materially break implementation
- Approve when the plan is complete, aligned, and actionable

## Output Format

`Plan Review`

- `Status: Approved | Issues Found`
- `Issues (if any): [Task X, Step Y]: [specific issue] - [why it matters for implementation]`
- `Recommendations (advisory, do not block approval)`

**Reviewer returns:** Status, Issues (if any), Recommendations
