# recommend-initiatives

## Trigger

Use this skill when the user asks what the project should do next, asks for a roadmap from the current source baseline, or asks for the next best initiatives before selecting one to plan.

## Goal

Inspect the current repository baseline and recommend a ranked sequence of 3-5 initiatives. The output is a recommendation snapshot, not an execution contract and not a PLAN.

## Read First

Read only what is needed to understand the current baseline:

1. `README.md` and repository entry docs
2. package, workspace, build, or CI configuration files
3. existing `docs/` content, especially `docs/initiatives/`
4. existing `docs/initiatives/recommendations/`, `active/`, `completed/`, and `archived/` entries
5. relevant source, test, component, schema, registry, or app directories
6. `git status` and a short recent commit summary when available

## Write Target

Default write target:

```text
docs/initiatives/recommendations/<yyyy-mm-dd>-<topic>.md
```

Also update:

```text
docs/initiatives/recommendations/index.md
```

Do not create an `active/<slug>/PLAN.md` unless the user explicitly selects an initiative or asks you to write a plan.

## Workflow

1. Establish the baseline: branch, clean/dirty state, important docs, source areas, tests, and known constraints.
2. Check existing recommendations, active initiatives, completed initiatives, and archived initiatives before ranking candidates.
3. Identify current strengths, gaps, risks, and product opportunities.
4. Rank candidate initiatives by product impact, engineering leverage, risk reduction, and execution readiness.
5. Recommend 3-5 initiatives only. Default to 3 when the project does not clearly need more.
6. Present them as an ordered sequence, not a flat wishlist.
7. Do not recommend duplicate active or completed initiatives unless the recommendation is explicitly a follow-up, v2, or replacement with a stated reason.
8. Treat archived initiatives as reusable background only; recommend them again only with an explicit replacement or revival rationale.
9. For each initiative, include expected outcome, suggested size, key risks, read-first files, and whether an acceptance and hardening Milestone is recommended.
10. Include a short `Not Recommended Yet` section for tempting work that should wait.
11. End with the best next action, usually to run `write-plan` for the top initiative.

## Quality Bar

A valid recommendation:

- is grounded in actual repository files and project state
- recommends 3-5 initiatives, never a long backlog
- explains ordering and dependencies
- avoids duplicating existing active or completed initiatives
- avoids generic items like “improve tests” unless tied to concrete source areas and risks
- does not start coding
- does not write a full PLAN for every candidate
- does not create formal document slices or old runtime state

## Output Shape

Use the template in `references/output-template.md` when writing a recommendation file.
