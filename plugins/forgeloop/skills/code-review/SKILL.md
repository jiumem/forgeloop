---
name: code-review
description: Load when implemented code needs review against its intended behavior and repository standards; do not load for exploratory code investigation, impact analysis, or debugging.
---

# Code Review

Review implemented code on two independent axes:

- **Standards** — does the code follow this repository's documented standards?
- **Spec** — does the code implement its intended behavior without omissions, mistakes, or scope creep?

This Skill reviews a bounded implementation. It does not perform open-ended codebase investigation, impact analysis, debugging, or architecture discovery.

## Process

### 1. Freeze the review scope

Use the narrowest scope already established by the caller:

- **change scope** — a pull request, fixed Base/Head, commit range, staged changes, unstaged changes, or both worktree sets;
- **snapshot scope** — explicit files, directories, or a module at its current contents;
- **upstream scope** — the exact frozen candidate and Spec supplied by another Agent or Workflow.

Record the scope type, exact refs or paths, exclusions, and the command or entry point that reproduces the evidence. Reuse an upstream frozen scope exactly. Do not choose `main`, review the whole repository, or expand the scope by assumption. If the context does not identify one scope, ask one question whose answer will fix it.

Validate the scope before creating child Agents. Stop with a locatable error when a ref or path is invalid, the scope is empty or unreadable, or the requested worktree set is ambiguous.

### 2. Find the Spec

Use, in order:

1. the Spec, PRD, or acceptance contract supplied by the caller;
2. an Issue or PR linked by the frozen scope, read through `docs/agents/issue-tracker.md` when configured;
3. a matching document under `docs/`, `specs/`, or `.scratch/`.

Tracker configuration is needed only to fetch a linked Spec. Do not start `$setup-forgeloop` automatically. If no Spec is available, skip the Spec Reviewer and report `SPEC: NOT_AVAILABLE`.

### 3. Find the Standards

Load repository instructions and relevant standards such as `AGENTS.md`, `CONTRIBUTING.md`, ADRs, or coding guides. Apply Fowler's Mysterious Name, Duplicated Code, Feature Envy, Data Clumps, Primitive Obsession, Repeated Switches, Shotgun Surgery, Divergent Change, Speculative Generality, Message Chains, Middle Man, and Refused Bequest as judgement-only smell heuristics.

Repository rules override heuristics. Skip rules already enforced reliably by tooling. Report only evidence inside the frozen review scope.

### 4. Review in isolated contexts

When a Spec exists, create two independent child Agents from self-contained prompts and run them in parallel without inheriting the current conversation. Without a Spec, create only the Standards Reviewer.

Give both Reviewers the frozen scope, reproduction command or evidence entry point, exact refs or paths, exclusions, and relevant source files.

The **Standards Reviewer** reports actionable violations and possible smells with exact file/line or Diff hunk evidence. It cites the repository rule for hard violations, labels smells as judgement calls, and ignores tooling-enforced or out-of-scope issues.

The **Spec Reviewer** reports missing, partial, incorrect, or unrequested behavior. Every Finding cites the requirement. For present code, cite the exact file/line or Diff hunk; for missing behavior, cite the inspected entry point and absence evidence. Do not infer requirements absent from the Spec.

Each Reviewer returns Findings only; when none exist, it returns `PASS`. Keep each report under 400 words.

### 5. Report

State the frozen review scope first. Present the reports under `## Standards` and `## Spec`; use `SPEC: NOT_AVAILABLE` when applicable. Keep the axes separate and do not merge or rerank their Findings.

End with the Finding count for each axis.

## Authorization

The entire review is read-only. Do not modify code, tests, Commits, Branches, Specs, Tickets, PRs/MRs, or Tracker state.
