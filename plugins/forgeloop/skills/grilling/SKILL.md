---
name: grilling
description: Load when a plan or design needs focused adversarial questioning without the document-maintenance workflow.
---

Interview the user relentlessly until you reach a shared understanding. Map this as a **design tree**: every decision branches into the decisions that hang off it.

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already settled — the questions you can ask _now_ without guessing at answers you have not heard yet. Ask a bounded slice of the frontier in each round: normally 3–5 independent questions, never more than 5. Ask fewer when a question is high-impact, hard to reverse, or cognitively heavy; ask it alone when its answer is needed to frame the others. Number every question, give your recommended answer, then wait for the user's answers before the next round.

Each question should be formatted like so:

```
❓ **Q1** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>
```

Each round the user answers reshapes the tree — settled decisions push the frontier outward and unblock questions that depended on them. Summarize the decisions just settled, recompute the frontier, and ask the next bounded round. A question whose answer depends on another question still open in this round belongs to a _later_ round, not this one. Make recommendations explicit enough that the user can answer in bulk, for example: `accept all recommendations except Q3`. If the user asks for lower density, return to one question at a time.

Finding _facts_ is your job, never the user's. When a frontier question needs a fact from the environment, look it up directly or delegate only when doing so is useful and authorized; do not ask the user for anything you can discover yourself. Treat any unfinished exploration as an unsettled prerequisite, so dependent questions wait while the rest of the bounded frontier may proceed. The _decisions_ are the user's — put each to them and wait.

The session is done when the remaining uncertainty no longer changes the smallest complete design, or when the frontier is empty. Do not continue into low-value preferences merely to exhaust the theoretical tree. Do not act on the result until the user confirms you have reached a shared understanding.
