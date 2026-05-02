# Forgeloop

[Chinese README](README.zh-CN.md)

Forgeloop is a Codex-native agentic software engineering system for moving a software project forward over the long term with stability and quality.

It is not a project management tool, and it is not a bundle of prompt templates. Forgeloop focuses on the hard parts of agentic coding: choosing the next piece of development work that is actually worth doing, compressing a goal into an executable plan, keeping Coder delivery moving, giving Reviewer real authority, and preserving direction, quality, and token discipline across multi-turn sessions, long-running development, and interrupted work.

Forgeloop's core workflow is short:

```text
Candidate -> DESIGN.md -> PLAN.md -> LEDGER.md -> DELIVERY.md
```

An Initiative is the user entrypoint and the top-level unit of work. It can be roughly compared to an Epic in traditional project management, but in Forgeloop it is not a loose requirements label. It is an engineering loop that must be decided by `DESIGN.md`, carried by `PLAN.md`, delivered across Milestones, reviewed by Reviewer, and finally archived. An Initiative can be a new feature, an architectural refactor, test-system hardening, performance optimization, API / Schema governance, documentation and examples, a migration effort, or any development goal that needs sustained progress across multiple phases.

## Value And Vision

Large models can already write increasingly complex code, but long-running agentic coding still tends to fail in a few recurring ways:

- The next best step is unclear, so the Agent burns context on low-value work.
- Requirements are not compressed into a staged plan, so Coder jumps straight into local implementation.
- Code that runs is not necessarily complete, and there is no stable review protocol.
- Tests, Schema boundaries, architecture boundaries, second paths, and duplicate state often surface only at the end.
- After an interrupted session, recovery depends on chat memory and drifts easily.
- In multi-agent collaboration, scheduling, implementation, and review responsibilities blur together, and token usage becomes hard to control.

Forgeloop's goal is to give Codex a loop that is light enough to use and strict enough to hold:

- Use `recommend-initiatives` to find the next development units that are most worth doing.
- Use `grill-initiative` to pressure-test, investigate, and decide a candidate Initiative into `DESIGN.md`.
- Use `plan-initiative` to compress `DESIGN.md` into an executable `PLAN.md` and `LEDGER.md`.
- Use `run-initiative` to make long-running progress by Milestone.
- Use `run-initiative-sequences` to serially advance multiple consecutive Initiatives in the active queue.
- Use Coder to implement, self-check, and produce evidence through the Construction Loop.
- Use Reviewer to decide from product, test, and architecture perspectives.
- Use `LEDGER.md` and Git to leave recoverable, reviewable, and revertible evidence.

This system is designed for durable forward motion: not to make an Agent complete a one-off demo, but to let it keep working in a real codebase one phase at a time, with acceptance, review, and recovery points in every phase, while keeping quality and token cost stable.

## Codex-native Experience

Forgeloop is designed for Codex plugins and skills. It treats Codex as the Scheduler by default: Scheduler reads the plan, maintains progress, sends task entrypoints, and coordinates Coder and Reviewer according to their role protocols.

In practice, one useful model setup is:

- Scheduler: GPT-5.5 medium
- Coder: GPT-5.5 high
- Reviewer: GPT-5.5 high

This setup has been stable for instruction following, repair loops, and review quality on complex development tasks, while keeping final token usage reasonably controlled.

If you want to reduce token usage further, you can try:

- GPT-5.4 medium as Scheduler or Reviewer
- GPT-5.3 Codex high as Coder
- Lower reasoning effort for low-risk Milestones, while keeping high reasoning effort for high-risk Milestones

Forgeloop does not require a fixed model set. Its more important constraint is separation of responsibilities: Scheduler does not hand all of its context to Coder, Coder does not approve itself, and Reviewer decides only from the real diff and acceptance criteria.

## Core Model

### Initiative Is The General Development Unit

Initiative is the user entrypoint and the top-level development unit in Forgeloop. It can help people familiar with traditional project management think of it as Epic-sized work, but in Forgeloop it has a stronger execution position: a high-risk or ambiguous effort must first become `DESIGN.md`, then be compressed into `PLAN.md`, split into Milestones, given verifiable completion standards, and finally closed through delivery archival.

Typical Initiatives include:

- Implementing a group of product capabilities
- Splitting an oversized module
- Migrating an old API
- Cleaning up a data model or Schema
- Completing critical test paths
- Hardening performance, stability, or observability
- Refactoring build, release, or plugin structure
- Improving documentation, examples, and developer experience

A good Initiative is not just "doing some things". It has clear product or engineering value and can be delivered in phases.

### Milestone Is The Delivery Unit

Milestone is the progress unit consumed by `run-initiative`. Each Milestone should produce a reviewable delivery, not just a task list.

Forgeloop continues to use Milestone as the unit of progress, commit, and review instead of making small Tasks the default scheduling object. Strong models can already deliver fairly complex phase-level work. Overly fine task granularity wastes context, increases review cost, and drags Reviewer attention from phase closure back into component checklists. Work Items only serve execution checks inside a Milestone; they are not formal lifecycle objects.

Milestones should prefer vertical slices: a reviewable phase state becomes true across the necessary layers, rather than being split into horizontal construction batches such as schema-only, API-only, UI-only, tests-only, or docs-only. A horizontal Milestone is appropriate only when the Initiative is explicitly scoped as horizontal governance, documentation cleanup, or mechanical migration.

A good Milestone usually includes:

- 3 to 5 Work Items
- One clear Expected Inspectable State
- Clear acceptance criteria
- Necessary validation methods
- Risks that Reviewer should focus on
- Clear non-goals so Coder does not expand scope

An Initiative usually works best with 3 to 8 Milestones. For high-risk capabilities, add an Acceptance & Hardening Milestone after feature Milestones to handle acceptance, test hardening, architecture cleanup, large-file splitting, and second-path cleanup.

### Coder Is Responsible For Implementation

Coder is not a code generator that mechanically translates PLAN, and it is not the formal Reviewer. Coder is responsible for delivering a correct, convergent, verifiable implementation within existing boundaries, and for completing a lightweight self-check before commit.

Coder's Construction Loop includes:

```text
Repository Orientation
Behavior Intent Snapshot
Public Seam Selection
Behavior-First Red-Green Loop
Contract And Source-of-Truth Delta Control
Completeness And Edge Surface
Validation And Evidence Ladder
Self-Diff Hygiene Gate
Repair And Risk Discipline
```

This loop does not turn TDD into a separate entrypoint, and it does not force every task to be test-first. It requires Coder to translate the Milestone into observable behavior first, prefer public seams that prove real behavior, implement in thin behavior slices, protect contracts and sources of truth, check edges and re-entry, report validation evidence that Scheduler / Reviewer can reuse, and inspect its own diff before committing.

### Reviewer Is The Quality Core

Forgeloop's core is not letting Coder approve itself. It is having Coder complete implementation self-checks first, then giving Reviewer real release authority.

Reviewer must review each Milestone from three perspectives:

1. Product Manager: whether the feature is actually usable, whether the user path holds, and whether key states are covered.
2. Test Engineer: whether tests and validation genuinely cover the acceptance criteria, and whether there are shallow smoke tests, weak assertions, skipped tests, or fake validation.
3. Architect: whether core Schema changes are sound, whether large files need splitting, and whether there are second paths, duplicate state, duplicate schema, shadow logic, or wrong module boundaries.

Reviewer can end with only:

```text
PASS
REPAIR_REQUIRED
```

Only `PASS` advances to the next Milestone.

### Git Is Evidence, Not Approval

Commit and push record diffs, create recovery points, and support review and rollback. They are not proof of completion, and they are not phase approval. Forgeloop defaults to Milestone-granularity commits: one Milestone forms one reviewable primary implementation commit; Reviewer-driven repairs may form fixup commits, but final review still considers the cumulative Milestone diff.

Forgeloop advances on Reviewer `PASS`, not on:

- Code committed
- Branch pushed
- Build passing
- Tests passing
- Zip packaging
- Coder saying it is done

## Five Skill Entrypoints

Forgeloop exposes only five core skills.

The documents produced by these five skills default to the language of the user's request. File paths, commands, code identifiers, branch names, status values, and protocol tokens remain unchanged, such as `PASS`, `REPAIR_REQUIRED`, `TODO`, and `CODING`.

### 1. `recommend-initiatives`

Recommend the next 3 to 5 Initiatives that are most worth doing from the current source baseline.

It inspects project structure, docs, tests, key source areas, and existing Initiative records, then ranks candidates by product value, engineering leverage, risk reduction, and execution readiness. It does not start coding, and it does not write `DESIGN.md` or a full PLAN for every candidate.

Common usage:

```text
Use Forgeloop to inspect the current project baseline and recommend the next 3-5 Initiatives that are most worth doing.
```

Output is usually written to:

```text
docs/initiatives/recommendations/<date>-<topic>.md
```

### 2. `grill-initiative`

Before a candidate Initiative, ambiguous requirement, refactor idea, migration plan, or architecture direction enters PLAN, use this skill to pressure-test it into a document-first `DESIGN.md` draft.

`DESIGN.md` is the only working artifact for design body content; chat is used only for short progress updates, decision batches, blockers, and sealing confirmation. `grill-initiative` does not write code, issues, `PLAN.md`, or `LEDGER.md`. It creates or updates:

```text
docs/initiatives/active/<initiative-code>-<initiative-slug>/DESIGN.md
```

A new `DESIGN.md` defaults to:

```text
Status: Draft
```

The Draft includes a Value Question Directory Tree, stable `Lxxx` Leaf IDs, Focused Context Findings, Leaf Resolution Matrix, Decision Records, Scope / Non-Goals, Selected Design, Design Details, Activation Blockers, Follow-ups, and Residual Risks.

Every retained leaf must be closed exactly once in the Leaf Resolution Matrix. Questions that can be answered from code, tests, configuration, or existing docs are answered from the repository first; the user is asked only for product intent, business priority, external constraints, irreversible trade-offs, or missing authority. Terminology conflicts that affect implementation, validation, review, or downstream planning must be explicitly found, decided, blocked, or listed as open questions in `DESIGN.md`.

When there are no Activation Blockers, `grill-initiative` asks whether to seal the draft. Sealing may only change `Status: Draft` to `Status: Sealed` and update sealing metadata. It must not rewrite the body, reorder sections, renumber IDs, or invent new decisions.

Common usage:

```text
Use Forgeloop grill-initiative to pressure-test this candidate: I want to refactor the auth module.
```

Possible dispositions include:

```text
Ready for sealing
Keep as draft
Split required
Defer to research
Reject
Superseded
```

### 3. `plan-initiative`

Write the selected Initiative or `DESIGN.md` into an executable `PLAN.md` and initial `LEDGER.md`. If blocking design disagreement remains, use `grill-initiative` first.

Only `DESIGN.md` with `Status: Sealed` is a formal design source that `plan-initiative` may consume. `Status: Draft`, `Status: Superseded`, missing status, unknown status, or conflicting status markers are hard stops; return to `grill-initiative` first to repair, restore, or seal the design.

`plan-initiative` also runs a read-only intake gate: Activation Blockers, Leaf Resolution Matrix, Decision Records, Design Impact, Downstream Constraint, remaining placeholders, and core terminology consistency. If intake fails, it does not write `PLAN.md` / `LEDGER.md`, and it does not repair `DESIGN.md` during planning.

`PLAN.md` is the execution contract consumed by `run-initiative`. `plan-initiative` does not re-decide evidence-backed design directions from a sealed `DESIGN.md`. Instead, it compresses Downstream Constraints, terminology constraints, scope, acceptance criteria, and validation methods into executable Milestones. Milestones are preferably organized as vertical slices that form independently reviewable Expected Inspectable States.

Common usage:

```text
Use Forgeloop to write a PLAN.md for this Initiative so it can later be executed by Milestone.
```

Output is usually written to:

```text
docs/initiatives/active/<initiative-code>-<initiative-slug>/PLAN.md
docs/initiatives/active/<initiative-code>-<initiative-slug>/LEDGER.md
```

New Initiative directory names should start with a three-digit code prefix, for example:

```text
docs/initiatives/active/001-auth-hardening/PLAN.md
docs/initiatives/active/001-auth-hardening/LEDGER.md
```

### 4. `run-initiative`

Execute an Initiative from `PLAN.md`. Execution proceeds by Milestone. Each Milestone goes through Coder delivery and Reviewer review.

Common usage:

```text
Use Forgeloop to execute docs/initiatives/active/<initiative-code>-<initiative-slug>/PLAN.md until the Initiative is complete.
```

Recommended execution flow:

```text
Read DESIGN.md when present, PLAN.md, and LEDGER.md
Confirm or create branch codex/<initiative-code>-<initiative-slug>
Locate the first non-PASS Milestone
Send Coder a task entrypoint and require it to read the Coder role protocol
Coder reads docs, follows the Construction Loop, implements, validates, records screenshots or evidence, commits and pushes at Milestone granularity
Scheduler updates LEDGER.md to REVIEW
Send Reviewer a task entrypoint and require it to read the Reviewer role protocol
Reviewer reviews the real diff from product, test, and architecture perspectives
REPAIR_REQUIRED returns to Coder for repair
PASS records the verdict and advances to the next Milestone
Run final validation after all Milestones pass
Write DELIVERY.md, prepare PR summary, and move the Initiative to completed/
```

### 5. `run-initiative-sequences`

Serially run user-specified consecutive Initiatives under `docs/initiatives/active/`.

It is a thin scheduling wrapper around `run-initiative`: it enumerates the active queue, confirms the requested range, calls the standard `run-initiative` workflow for each Initiative, and outputs an aggregated PR summary after all work is complete. It does not duplicate Milestone, Reviewer, repair, or DELIVERY rules.

Common usage:

```text
Use Forgeloop run-initiative-sequences to run active Initiatives 003 through 006.
```

If the user does not specify a range, it should first ask whether to run all active Initiatives or a specific range.

Before running a long Initiative sequence, consider increasing the subagent thread limit in Codex TOML, for example:

```toml
[agents]
max_threads = 100
```

## Runtime Storage Structure

Forgeloop separates plugin code from project execution records.

Plugin code lives in:

```text
plugins/forgeloop/
```

Project instance data is created by skills in the target repository as needed:

```text
docs/initiatives/
  recommendations/
    <date>-<topic>.md
  handoff/
    index.md
    <initiative-code>-<initiative-slug>.md
  active/
    <initiative-code>-<initiative-slug>/
      DESIGN.md
      PLAN.md
      LEDGER.md
      evidence/
  completed/
    <initiative-code>-<initiative-slug>/
      DESIGN.md
      PLAN.md
      LEDGER.md
      DELIVERY.md
      evidence/
  archived/
    <initiative-code>-<initiative-slug>/
```

Where:

- `<initiative-code>` is a three-digit code prefix, such as `001`.
- `DESIGN.md` is the design decision source; only DESIGN with `Status: Sealed` can be formally consumed by `plan-initiative`.
- `PLAN.md` is the execution planning contract.
- `LEDGER.md` is the minimal recovery ledger.
- `evidence/` stores optional screenshots, validation records, and review evidence.
- `DELIVERY.md` is the final delivery summary and PR summary basis.
- `handoff/` stores cross-Initiative findings and future opportunities after Initiative completion, maintained by Scheduler; even when there are no findings, an explicit empty record is kept.
- Recommendation files are snapshots, not execution contracts.

## Installation

Forgeloop is a repo-local Codex plugin. It is not a Python package and does not need npm / pnpm installation.

### Option 1: Use This Repository Directly

1. Clone or download this repository locally.
2. Confirm that the repository root contains:

```text
.agents/plugins/marketplace.json
plugins/forgeloop/.codex-plugin/plugin.json
plugins/forgeloop/skills/
```

3. Restart Codex so it reloads the repo-local marketplace.
4. Install `Forgeloop Local` / `forgeloop` from the Codex plugin UI.

### Option 2: Copy Into An Existing Project

If you want to use Forgeloop as a local plugin for another project, copy the following into that project's root:

```text
.agents/plugins/marketplace.json
plugins/forgeloop/
```

Then restart Codex and install the repo-local plugin.

## Repository Structure

This repository intentionally stays minimal and keeps only the core plugin and README files:

```text
.
├── .agents/
│   └── plugins/
│       └── marketplace.json
├── plugins/
│   └── forgeloop/
│       ├── .codex-plugin/
│       │   └── plugin.json
│       └── skills/
│           ├── recommend-initiatives/
│           ├── grill-initiative/
│           ├── plan-initiative/
│           ├── run-initiative/
│           └── run-initiative-sequences/
├── LICENSE
├── README.md
└── README.zh-CN.md
```

## Common Usage Examples

### Grill An Ambiguous Request

```text
Use Forgeloop grill-initiative to pressure-test this candidate: I want to refactor the auth module, but I am not sure about the scope.
```

Use this when the requirement does not yet have clear boundaries, the refactor may be too large, or you want the Agent to produce a document-first Draft DESIGN, Leaf Resolution Matrix, and evidence-backed Decision Records before writing PLAN.

### Recommend Future Initiatives

```text
Use Forgeloop to recommend the next 3-5 Initiatives that are most worth doing from the current source baseline.
```

Use this when you have just taken over a project, completed a version, or want the Agent to help decide what should come next.

### Write PLAN For A Selected Initiative

```text
Use Forgeloop plan-initiative based on docs/initiatives/active/001-auth-hardening/DESIGN.md to write PLAN.md and LEDGER.md. This DESIGN.md is already Status: Sealed. Use Milestone as the delivery unit, keep each Milestone to 3-5 Work Items, prefer vertical-slice Milestones with reviewable Expected Inspectable State, and add an Acceptance & Hardening Milestone after important capabilities.
```

Use this when you already have a sealed DESIGN or clear Initiative but do not yet have an executable structure. If DESIGN is still Draft, has blockers, has an incomplete Leaf Resolution Matrix, or has core terminology conflicts, `plan-initiative` stops and requires repair through `grill-initiative`.

### Execute An Initiative From PLAN

```text
Use Forgeloop to execute docs/initiatives/active/001-auth-hardening/PLAN.md. Reuse one Coder subagent and one Reviewer subagent, do not fork Scheduler context to subagents, use Milestone-granularity commit/push, and continue after Reviewer PASS.
```

Use this when you are ready to enter implementation delivery. Coder reads its role protocol and follows the Construction Loop; Scheduler provides only task entrypoints and boundaries, not a second-hand implementation summary rewritten from PLAN / DESIGN.

### Serially Execute Multiple Active Initiatives

```text
Use Forgeloop run-initiative-sequences to run Initiatives 003 through 006 under docs/initiatives/active.
```

Use this when multiple planned Initiatives need to be advanced in code order while each Initiative still completes its own `run-initiative` review loop independently.

### Resume An Interrupted Initiative

```text
Use Forgeloop to resume docs/initiatives/active/001-auth-hardening/ from the first non-PASS Milestone in LEDGER.md.
```

Forgeloop reads `DESIGN.md` when present, `PLAN.md`, `LEDGER.md`, `git status`, and recent commits instead of relying on chat memory.

### Continue A Review-driven Repair Loop

```text
Use Forgeloop to continue the current Initiative. The last Reviewer verdict was REPAIR_REQUIRED. Fix only blocking issues, then review again.
```

Use this when a Milestone did not pass review and needs continued progress.

## Subagent Usage

Forgeloop does not include custom agent TOML. Coder and Reviewer are defined by role protocols under the `run-initiative` skill. When delegating, Scheduler provides only "role protocol + task truth files + this Milestone's task entrypoint"; it does not rewrite its own digested context into a second-hand task description, and it does not extract or rewrite Coder / Reviewer working rules:

```text
plugins/forgeloop/skills/run-initiative/references/coder-protocol.md
plugins/forgeloop/skills/run-initiative/references/reviewer-protocol.md
plugins/forgeloop/skills/run-initiative/references/handoff-template.md
plugins/forgeloop/skills/run-initiative/references/handoff-index-template.md
```

Task truth files are usually the current Initiative's `DESIGN.md`, `PLAN.md`, `LEDGER.md`, relevant source / test / design docs, Coder report, real diff range, and evidence paths. Scheduler may state the current Milestone, scope, branch, base commit, dirty baseline, and stopping conditions, but Coder / Reviewer must read their protocols and truth files themselves before implementing or deciding.

Coder's role protocol requires it to establish repository orientation and behavior intent, choose public seams, build through behavior slices, control contract and source-of-truth deltas, check completeness / edge / re-entry, report through a validation evidence ladder, and complete self-diff hygiene before commit. Reviewer's role protocol remains responsible for the formal three-perspective verdict. Coder self-checks cannot replace Reviewer `PASS`.

In Codex environments that support subagents, use generic subagents:

- Coder: `default` or `worker`, high reasoning effort
- Reviewer: `default`, high reasoning effort
- `fork_context=false`
- Reuse one Coder and one Reviewer per Initiative whenever possible
- Prefer a three-digit coded `task_name`; for example, `001-auth-hardening` maps to `coder_001` and `reviewer_001`. Older uncoded Initiatives fall back to snake-normalized names.

When running long `run-initiative-sequences` flows, each Initiative creates its own Coder / Reviewer pair. If Codex TOML `[agents].max_threads` is too low, long sequences may hit the thread limit. Consider raising it to `100` in advance.

If the current environment has no subagent tools, Scheduler may continue when the user allows it, but it must record review provenance as `explicit solo best-effort`. This path is only reduced-provenance execution evidence and must not be described as formal independent Reviewer approval. Completion archival must clearly record the reduced review provenance.

## Suitable And Unsuitable Use Cases

Suitable:

- Product capabilities or features that require sustained delivery
- Architecture refactors, module splitting, dependency migration
- API, Schema, permission, data model, or plugin protocol governance
- Test reality, stability, performance, and observability hardening
- Build, release, CI, and developer-experience work
- Documentation, examples, SDKs, and integration experience
- Existing requirements that need to be compressed into PLAN and delivered continuously

Unsuitable:

- One-off scripts
- Very small bug fixes
- Temporary experiments that do not need planning or review
- Candidate efforts without boundaries when the user also does not want to use `grill-initiative` for upfront design decisions
- Projects that require strict organizational compliance flows but do not allow Agent participation in review

## Design Principles

Forgeloop follows a few principles:

1. Codex-native: designed around Codex plugins, skills, subagents, and Git workflow.
2. Few entrypoints: keep only `recommend-initiatives`, `grill-initiative`, `plan-initiative`, `run-initiative`, and `run-initiative-sequences`.
3. Clear delivery unit: user entrypoint is Initiative; execution advances by Milestone.
4. Clear design authority: only sealed `DESIGN.md` enters planning; Draft cannot be consumed by `plan-initiative`.
5. Strong construction loop: Coder self-checks behavior, seams, contracts, truth sources, edges, validation, and diff hygiene before commit.
6. Strong review protocol: Reviewer's three-perspective verdict matters more than formal status; Coder self-checks cannot replace Reviewer approval.
7. Minimal state: recovery depends only on `DESIGN.md`, `PLAN.md`, `LEDGER.md`, Git, and necessary evidence.
8. Git is not acceptance: commit / push are evidence and recovery points; a push before Reviewer `PASS` is only a review candidate, not approval.
9. Long-term control: separation of responsibilities, task entrypoints, role protocols, and Reviewer approval control quality, context, and token cost.

## License

MIT. See [LICENSE](LICENSE).
