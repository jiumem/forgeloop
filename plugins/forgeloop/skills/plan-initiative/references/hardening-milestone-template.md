### MXX: Acceptance & Hardening

Language note: this template defines structure only. Write headings and prose in the primary language of the user's request, while preserving technical identifiers, paths, commands, and protocol tokens.

Purpose:
- Consolidate the preceding business capability before expanding scope.

Work Items:
1. Review the delivered user flow against product acceptance criteria.
2. Strengthen tests for real user behavior, edge states, and regressions.
3. Review schema, component boundaries, module placement, and data contracts.
4. Split oversized or mixed-responsibility files where needed.
5. Remove duplicate state, duplicate schema, duplicate rendering, duplicate data fetching, shadow logic, or other second paths.

Acceptance Criteria:
- Main user flows work end to end.
- Tests cover acceptance behavior, not only implementation details.
- No unjustified skipped tests, weakened assertions, or deleted coverage.
- No unresolved second path around core state, schema, rendering, or data fetching.
- Large files introduced or worsened by the preceding work are split or explicitly justified.
- Residual risks are documented.

Validation:
- <project-specific commands>

Visual / UX Checks:
- Preview target:
- Viewports:
- Required states:
- Screenshot evidence:

Schema / Architecture Notes:
- Core schema impact:
- Large file risk:
- Second path risk:

Reviewer Focus:
- Product: usability of the completed capability and important edge states.
- Test: coverage and truthfulness of the validation.
- Architecture: schema changes, file boundaries, dependency direction, maintainability, and second paths.

Non-Goals:
- Do not add new product scope unless required to fix acceptance, validation, or architecture blockers.
