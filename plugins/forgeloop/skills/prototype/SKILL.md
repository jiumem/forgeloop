---
name: prototype
description: Load when a design uncertainty is best resolved with a disposable experiment, interaction mockup, or state-model probe.
---

# Prototype

A prototype is **throwaway code that answers a question**. The question decides the shape.

## Pick a branch

Identify which question is being answered — from the user's prompt, the surrounding code, or by asking if the user is around:

- **"Does this domain logic / state model feel right?"** → [LOGIC.md](LOGIC.md). Build a single shareable HTML file — free-play buttons plus tabbed guided walkthroughs — that pushes the state machine through cases that are hard to reason about on paper, and that a non-developer can drive.
- **"Does this depend on language, concurrency, database, framework, or runtime semantics?"** → Build the smallest host-native executable probe behind one command. Do not translate the behavior into browser JavaScript when that would change what is being tested.
- **"What should this look like?"** → [UI.md](UI.md). Generate several radically different UI variations on a single route, switchable via a URL search param and a floating bottom bar.

The three branches produce very different artifacts — getting this wrong wastes the whole prototype. If the question is genuinely ambiguous and the user is not reachable, choose the host-native probe whenever validity depends on real runtime semantics; otherwise use the domain-logic HTML for a backend state model and the UI branch for a page or component. State the assumption at the top of the prototype.

## Rules that apply to every branch

1. **Throwaway from day one, and clearly marked as such.** Locate the prototype code close to where it will actually be used (next to the module or page it's prototyping for) so context is obvious — but name it so a casual reader can see it's a prototype, not production. For throwaway UI routes, obey whatever routing convention the project already uses; don't invent a new top-level structure.
2. **Trivial to run.** A UI prototype starts from one command in the project's task runner — `pnpm <name>`, `python <path>`, `bun <path>`, etc. A domain-logic demo is a single HTML file the user double-clicks. A runtime-specific probe also starts from one repository-native command and introduces no new runtime or package manager. In every branch, no thinking is required to start it.
3. **No persistence by default.** State lives in memory. Persistence is the thing the prototype is _checking_, not something it should depend on. If the question explicitly involves a database, hit a scratch DB or a local file with a clear "PROTOTYPE — wipe me" name.
4. **Skip the polish.** No tests, no error handling beyond what makes the prototype _runnable_, no abstractions. The point is to learn something fast.
5. **Surface the state.** After every action (domain logic or runtime probe) or on every variant switch (UI), print or render the full relevant state so the user can see what changed.
6. **Capture it when done.** Fold any validated decision into the real code, then capture the prototype itself as a **primary source**: commit it to a throwaway branch, out of main, and leave a context pointer to that branch on the implementation issue. Capture the answer too — the verdict and the question it settled — in the issue or a commit. The main branch keeps only the validated decision.

## Forgeloop Persistence Boundary

Invoking this Skill authorizes only the minimally scoped prototype files needed to answer the named design question. Creating or updating a Branch, Commit, Issue, Ticket, PR/MR, or other durable external state requires separate explicit authorization. Without it, return the prototype path, the question it answered, the current verdict, and a proposed context pointer in the conversation; do not perform the capture step automatically.
