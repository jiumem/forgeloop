---
name: spec-standards-review
description: Load when implemented code needs review against its intended behavior and repository standards; do not load for exploratory code investigation, impact analysis, or debugging.
---

Two-axis review of implemented code within a fixed scope:

- **Standards** — does the code conform to this repo's documented coding standards?
- **Spec** — does the code faithfully implement the originating issue / PRD / spec?

Both axes run as **parallel sub-agents** so they don't pollute each other's context, then this skill aggregates their findings.

Treat the caller-supplied review scope as authoritative. It may be a PR or diff, an explicit Base/Head pair, staged changes, unstaged changes, both, or another concrete change set; it may also be a snapshot of explicit files, directories, or a module. Resolve and validate it once. If the context cannot determine a unique scope, ask one question whose answer would change the scope; if the resolved scope is empty or unreadable, fail before spawning reviewers. Pass the same frozen scope to both reviewers, and do not replace an explicitly supplied Head with the local `HEAD`. If another Agent or Workflow supplies a frozen scope and Spec, use them exactly. For a snapshot review, later references to the diff command and commit list mean the exact paths and current revision, and hunk evidence means file/line evidence; include this substitution in both self-contained Reviewer prompts.

Issue tracker configuration is only required when the review must fetch its Spec from the configured tracker. If `docs/agents/issue-tracker.md` is missing, do not run `$setup-forgeloop` automatically: use any Spec or PRD the caller supplied, otherwise continue to step 2 without starting another Workflow.

## Process

### 1. Pin the review scope

For a fixed-point change review, whatever the caller identifies is the fixed point — a commit SHA, branch name, tag, `main`, `HEAD~5`, etc. If they didn't specify one, ask for it.

For a fixed-point change review, capture the diff command once: `git diff <fixed-point>...HEAD` (three-dot, so the comparison is against the merge-base). Also note the list of commits via `git log <fixed-point>..HEAD --oneline`.

For a fixed-point change review, confirm the fixed point resolves (`git rev-parse <fixed-point>`) and the diff is non-empty. A bad ref or empty diff should fail here — not inside two parallel sub-agents.

For a snapshot review, resolve the exact paths, record the current revision, and confirm the scope exists, is readable, and contains code. A missing, unreadable, or empty scope should fail here. If no review scope is specified, ask for it; do not default to the whole repository.

### 2. Identify the spec source

Look for the originating spec, in this order:

1. A Spec, PRD, or acceptance contract the caller or upstream Workflow supplied.
2. Issue references in the commit messages for a change review (`#123`, `Closes #45`, GitLab `!67`, etc.) — fetch via the workflow in `docs/agents/issue-tracker.md`.
3. A PRD/spec file under `docs/`, `specs/`, or `.scratch/` matching the branch, feature, or snapshot scope.
4. If nothing is found, ask the caller where the spec is. If they say there isn't one, skip the **Spec** sub-agent and report `SPEC: NOT_AVAILABLE`.

### 3. Identify the standards sources

Anything in the repo that documents how code should be written, such as `CODING_STANDARDS.md` or `CONTRIBUTING.md`.

On top of whatever the repo documents, the Standards axis always carries the **smell baseline** below — a fixed set of Fowler code smells (_Refactoring_, ch.3) that applies even when a repo documents nothing. Two rules bind it:

- **The repo overrides.** A documented repo standard always wins; where it endorses something the baseline would flag, suppress the smell.
- **Always a judgement call.** Each smell is a labelled heuristic ("possible Feature Envy"), never a hard violation — and, like any standard here, skip anything tooling already enforces.

Each smell reads *what it is* → *how to fix*; match it against the diff:

- **Mysterious Name** — a function, variable, or type whose name doesn't reveal what it does or holds. → rename it; if no honest name comes, the design's murky.
- **Duplicated Code** — the same logic shape appears in more than one hunk or file in the change. → extract the shared shape, call it from both.
- **Feature Envy** — a method that reaches into another object's data more than its own. → move the method onto the data it envies.
- **Data Clumps** — the same few fields or params keep travelling together (a type wanting to be born). → bundle them into one type, pass that.
- **Primitive Obsession** — a primitive or string standing in for a domain concept that deserves its own type. → give the concept its own small type.
- **Repeated Switches** — the same `switch`/`if`-cascade on the same type recurs across the change. → replace with polymorphism, or one map both sites share.
- **Shotgun Surgery** — one logical change forces scattered edits across many files in the diff. → gather what changes together into one module.
- **Divergent Change** — one file or module is edited for several unrelated reasons. → split so each module changes for one reason.
- **Speculative Generality** — abstraction, parameters, or hooks added for needs the spec doesn't have. → delete it; inline back until a real need shows.
- **Message Chains** — long `a.b().c().d()` navigation the caller shouldn't depend on. → hide the walk behind one method on the first object.
- **Middle Man** — a class or function that mostly just delegates onward. → cut it, call the real target direct.
- **Refused Bequest** — a subclass or implementer that ignores or overrides most of what it inherits. → drop the inheritance, use composition.

### 4. Spawn both sub-agents in parallel

Create two independent child Agents from self-contained prompts and let them run in parallel without inheriting the current conversation.

**Standards sub-agent prompt** — include:

- The frozen review scope and its evidence entry: the diff command and commit list for a Git change, or the exact paths and current revision for a snapshot.
- The list of standards-source files you found in step 3, **plus the smell baseline from step 3** pasted in full — the sub-agent has no other access to it.
- The brief: "Report — per file/hunk where relevant — (a) every place the diff violates a documented standard: cite the standard (file + the rule); and (b) any baseline smell you spot: name it and quote the hunk. Distinguish hard violations from judgement calls — documented-standard breaches can be hard, but baseline smells are always judgement calls, and a documented repo standard overrides the baseline. Skip anything tooling enforces. Cite file/line or diff-hunk evidence for every finding, and do not report outside the frozen scope. Under 400 words."

**Spec sub-agent prompt** — include:

- The frozen review scope and its evidence entry: the diff command and commit list for a Git change, or the exact paths and current revision for a snapshot.
- The path or fetched contents of the spec.
- The brief: "Report: (a) requirements the spec asked for that are missing or partial; (b) behaviour in the diff that wasn't asked for (scope creep); (c) requirements that look implemented but where the implementation looks wrong. Quote the spec line for each finding. Also cite file/line or diff-hunk evidence, and do not report outside the frozen scope. Under 400 words."

If the spec is missing, skip the Spec sub-agent and note this in the final report.

### 5. Aggregate

First state the scope type, resolved Git IDs or paths, exclusions, and evidence entry. Then present the two reports under `## Standards` and `## Spec` headings, verbatim or lightly cleaned. Do **not** merge or rerank findings — the two axes are deliberately separate (see _Why two axes_).

End with a one-line summary: total findings per axis, and the worst issue _within each axis_ (if any). Don't pick a single winner across axes — that's the reranking the separation exists to prevent.

## Why two axes

A change can pass one axis and fail the other:

- Code that follows every standard but implements the wrong thing → **Standards pass, Spec fail.**
- Code that does exactly what the issue asked but breaks the project's conventions → **Spec pass, Standards fail.**

Reporting them separately stops one axis from masking the other.

## Forgeloop Authorization Boundaries

Read-only by default. Do not modify code, Commits, Branches, Specs, Tickets, PRs/MRs, or Tracker state.
