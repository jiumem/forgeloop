# Forgeloop Token Benchmark

## Runtime Cutover

- Contract: `plugins/forgeloop/skills/run-initiative/references/runtime-cutover.md`
- Runtime scope: `runtime_only`
- Planning scope: `out_of_scope`
- Current mode: `minimal_preferred`

## Runtime Scenarios

### Runtime Cold Start

- Bucket: `cold_path`
- Scope: `runtime`
- Gating: `gating`
- Description: Bind durable refs, admit planning truth, and initialize runtime without an existing active rolling doc.
- Legacy packet: 21719 tok approx | 86876 chars | 1295 lines | 10057 words
- Minimal packet: 10633 tok approx | 42532 chars | 576 lines | 4630 words
- Reduction: 51.0%
- Legacy docs read set: docs/initiatives/active/anchor-sliced-dispatch-optimization/design.md, docs/initiatives/active/anchor-sliced-dispatch-optimization/gap-analysis.md, docs/initiatives/active/anchor-sliced-dispatch-optimization/total-task-doc.md, plugins/forgeloop/skills/run-initiative/SKILL.md, plugins/forgeloop/skills/run-initiative/references/runtime-cutover.md, plugins/forgeloop/skills/run-initiative/references/global-state.md
- Minimal docs read set: docs/initiatives/active/anchor-sliced-dispatch-optimization/design.md#requirement-baseline, docs/initiatives/active/anchor-sliced-dispatch-optimization/design.md#target-state-design, docs/initiatives/active/anchor-sliced-dispatch-optimization/gap-analysis.md#baseline-and-scope, docs/initiatives/active/anchor-sliced-dispatch-optimization/total-task-doc.md#input-baseline, docs/initiatives/active/anchor-sliced-dispatch-optimization/total-task-doc.md#task-ledger, plugins/forgeloop/skills/run-initiative/references/runtime-cutover.md#current-mode, plugins/forgeloop/skills/run-initiative/references/runtime-cutover.md#default-read-law, plugins/forgeloop/skills/run-initiative/SKILL.md#canonical-ref-semantics, plugins/forgeloop/skills/run-initiative/SKILL.md#dispatch-rules, plugins/forgeloop/skills/run-initiative/SKILL.md#main-flow, plugins/forgeloop/skills/run-initiative/references/global-state.md#durable-rules, plugins/forgeloop/skills/run-initiative/references/global-state.md#bootstrap-law
- Fallback points: cold start may still promote individual reads to full documents on selector legality failure

### Runtime Resume Into Active Task

- Bucket: `hot_path`
- Scope: `runtime`
- Gating: `gating`
- Description: Resume a running Task from thin control state plus the current rolling-doc frontier.
- Legacy packet: 25721 tok approx | 102881 chars | 1743 lines | 12026 words
- Minimal packet: 7404 tok approx | 29616 chars | 491 lines | 2928 words
- Reduction: 71.2%
- Legacy docs read set: docs/initiatives/active/anchor-sliced-dispatch-optimization/design.md, docs/initiatives/active/anchor-sliced-dispatch-optimization/gap-analysis.md, docs/initiatives/active/anchor-sliced-dispatch-optimization/total-task-doc.md, plugins/forgeloop/skills/run-initiative/SKILL.md, plugins/forgeloop/skills/code-loop/SKILL.md, plugins/forgeloop/skills/code-loop/references/runtime-object-modes.md, plugins/forgeloop/skills/run-initiative/references/runtime-cutover.md, plugins/forgeloop/skills/run-initiative/references/task-review-rolling-doc.md, tests/codex/token-benchmark/fixtures/global-state-active-task.md, tests/fixtures/anchor-slicing/task-review-sample.md
- Minimal docs read set: docs/initiatives/active/anchor-sliced-dispatch-optimization/total-task-doc.md#task-ledger, docs/initiatives/active/anchor-sliced-dispatch-optimization/total-task-doc.md#acceptance-matrix, plugins/forgeloop/skills/run-initiative/references/runtime-cutover.md#current-mode, plugins/forgeloop/skills/run-initiative/SKILL.md#main-flow, plugins/forgeloop/skills/code-loop/SKILL.md#truth-sources-boundaries, plugins/forgeloop/skills/code-loop/SKILL.md#workflow, plugins/forgeloop/skills/code-loop/references/runtime-object-modes.md#task-mode, plugins/forgeloop/skills/run-initiative/references/task-review-rolling-doc.md#handoff-law, tests/codex/token-benchmark/fixtures/global-state-active-task.md#current-snapshot, tests/codex/token-benchmark/fixtures/global-state-active-task.md#next-action, tests/fixtures/anchor-slicing/task-review-sample.md::current-effective.md
- Fallback points: selector legality failure, global-state and rolling-doc conflict

### Same-Task Same-Round Coder Continue

- Bucket: `hot_path`
- Scope: `runtime`
- Gating: `gating`
- Description: Continue the same Task coder slot inside the current round without replaying full history.
- Legacy packet: 7895 tok approx | 31578 chars | 781 lines | 3790 words
- Minimal packet: 4199 tok approx | 16796 chars | 388 lines | 2118 words
- Reduction: 46.8%
- Legacy docs read set: plugins/forgeloop/skills/code-loop/SKILL.md, plugins/forgeloop/skills/code-loop/references/runtime-object-modes.md, plugins/forgeloop/skills/run-initiative/references/runtime-cutover.md, plugins/forgeloop/skills/run-initiative/references/task-review-rolling-doc.md, tests/fixtures/anchor-slicing/task-review-sample.md, tests/codex/token-benchmark/fixtures/global-state-active-task.md
- Minimal docs read set: plugins/forgeloop/agents/coder.toml, plugins/forgeloop/skills/code-loop/references/runtime-object-modes.md#task-mode, plugins/forgeloop/skills/run-initiative/references/task-review-rolling-doc.md#canonical-task-vocabulary, plugins/forgeloop/skills/run-initiative/references/task-review-rolling-doc.md#handoff-law, tests/codex/token-benchmark/fixtures/global-state-active-task.md#current-snapshot, tests/codex/token-benchmark/fixtures/global-state-active-task.md#next-action, tests/fixtures/anchor-slicing/task-review-sample.md::attempt-aware/round-2.md
- Fallback points: round ambiguity, handoff mismatch

### Same-Task Handoff To Fresh Reviewer

- Bucket: `hot_path`
- Scope: `runtime`
- Gating: `gating`
- Description: Dispatch a fresh Task reviewer against only the current handoff surface.
- Legacy packet: 9347 tok approx | 37387 chars | 921 lines | 4777 words
- Minimal packet: 2674 tok approx | 10694 chars | 299 lines | 1402 words
- Reduction: 71.4%
- Legacy docs read set: plugins/forgeloop/skills/code-loop/SKILL.md, plugins/forgeloop/skills/code-loop/references/runtime-object-modes.md, plugins/forgeloop/skills/run-initiative/references/runtime-cutover.md, plugins/forgeloop/skills/run-initiative/references/task-review-rolling-doc.md, tests/fixtures/anchor-slicing/task-review-sample.md, plugins/forgeloop/agents/task_reviewer.toml
- Minimal docs read set: plugins/forgeloop/agents/task_reviewer.toml, plugins/forgeloop/skills/code-loop/references/runtime-object-modes.md#task-mode, plugins/forgeloop/skills/run-initiative/references/task-review-rolling-doc.md#handoff-law, tests/fixtures/anchor-slicing/task-review-sample.md::handoff-scoped/sample-r2-a1.md
- Fallback points: fresh reviewer first packet must still be self-sufficient, derived view invalidation

### Milestone Review

- Bucket: `hot_path`
- Scope: `runtime`
- Gating: `gating`
- Description: Hand off Milestone evidence without replaying all included Task history.
- Legacy packet: 13858 tok approx | 55432 chars | 980 lines | 6162 words
- Minimal packet: 4750 tok approx | 18997 chars | 408 lines | 2179 words
- Reduction: 65.7%
- Legacy docs read set: docs/initiatives/active/anchor-sliced-dispatch-optimization/total-task-doc.md, plugins/forgeloop/skills/code-loop/SKILL.md, plugins/forgeloop/skills/code-loop/references/runtime-object-modes.md, plugins/forgeloop/skills/run-initiative/references/runtime-cutover.md, plugins/forgeloop/skills/run-initiative/references/milestone-review-rolling-doc.md, tests/codex/token-benchmark/fixtures/milestone-review-sample.md
- Minimal docs read set: docs/initiatives/active/anchor-sliced-dispatch-optimization/total-task-doc.md#milestone-master-table, docs/initiatives/active/anchor-sliced-dispatch-optimization/total-task-doc.md#acceptance-matrix, plugins/forgeloop/agents/milestone_reviewer.toml, plugins/forgeloop/skills/code-loop/references/runtime-object-modes.md#milestone-mode, plugins/forgeloop/skills/run-initiative/references/milestone-review-rolling-doc.md#handoff-law, tests/codex/token-benchmark/fixtures/milestone-review-sample.md::current-effective.md
- Fallback points: multiple actionable results, selector legality failure

### Initiative Review

- Bucket: `hot_path`
- Scope: `runtime`
- Gating: `gating`
- Description: Review the delivery candidate against Milestone evidence and current initiative handoff only.
- Legacy packet: 13796 tok approx | 55182 chars | 977 lines | 6131 words
- Minimal packet: 4366 tok approx | 17463 chars | 389 lines | 1968 words
- Reduction: 68.4%
- Legacy docs read set: docs/initiatives/active/anchor-sliced-dispatch-optimization/total-task-doc.md, plugins/forgeloop/skills/code-loop/SKILL.md, plugins/forgeloop/skills/code-loop/references/runtime-object-modes.md, plugins/forgeloop/skills/run-initiative/references/runtime-cutover.md, plugins/forgeloop/skills/run-initiative/references/initiative-review-rolling-doc.md, tests/codex/token-benchmark/fixtures/initiative-review-sample.md
- Minimal docs read set: docs/initiatives/active/anchor-sliced-dispatch-optimization/total-task-doc.md#acceptance-matrix, docs/initiatives/active/anchor-sliced-dispatch-optimization/total-task-doc.md#global-residual-risks, plugins/forgeloop/agents/initiative_reviewer.toml, plugins/forgeloop/skills/code-loop/references/runtime-object-modes.md#initiative-mode, plugins/forgeloop/skills/run-initiative/references/initiative-review-rolling-doc.md#handoff-law, tests/codex/token-benchmark/fixtures/initiative-review-sample.md::current-effective.md
- Fallback points: initiative handoff drift, review target mismatch

### Rebuild Runtime

- Bucket: `cold_path`
- Scope: `runtime`
- Gating: `gating`
- Description: Recover the control plane from thin durable truth plus the newest actionable rolling-doc frontier.
- Legacy packet: 18585 tok approx | 74338 chars | 1204 lines | 8182 words
- Minimal packet: 4271 tok approx | 17081 chars | 326 lines | 1853 words
- Reduction: 77.0%
- Legacy docs read set: docs/initiatives/active/anchor-sliced-dispatch-optimization/design.md, docs/initiatives/active/anchor-sliced-dispatch-optimization/gap-analysis.md, docs/initiatives/active/anchor-sliced-dispatch-optimization/total-task-doc.md, plugins/forgeloop/skills/rebuild-runtime/SKILL.md, plugins/forgeloop/skills/run-initiative/references/runtime-cutover.md, tests/codex/token-benchmark/fixtures/global-state-waiting.md, tests/codex/token-benchmark/fixtures/initiative-review-sample.md, tests/codex/token-benchmark/fixtures/milestone-review-sample.md
- Minimal docs read set: docs/initiatives/active/anchor-sliced-dispatch-optimization/total-task-doc.md#input-baseline, plugins/forgeloop/skills/run-initiative/references/runtime-cutover.md#current-mode, plugins/forgeloop/skills/run-initiative/references/runtime-cutover.md#fallback-law, plugins/forgeloop/skills/rebuild-runtime/SKILL.md#truth-sources-boundaries, plugins/forgeloop/skills/rebuild-runtime/SKILL.md#shared-runtime-recovery-law, plugins/forgeloop/skills/rebuild-runtime/SKILL.md#workflow, tests/codex/token-benchmark/fixtures/global-state-waiting.md#current-snapshot, tests/codex/token-benchmark/fixtures/global-state-waiting.md#next-action, tests/codex/token-benchmark/fixtures/global-state-waiting.md#last-transition, tests/codex/token-benchmark/fixtures/initiative-review-sample.md::current-effective.md
- Fallback points: multiple active candidates coexist, derived view legality drift

### Waiting Or Blocked Resume

- Bucket: `cold_path`
- Scope: `runtime`
- Gating: `gating`
- Description: Resume from an explicit stop state without rescanning unrelated planning and runtime history.
- Legacy packet: 16215 tok approx | 64860 chars | 956 lines | 7601 words
- Minimal packet: 2139 tok approx | 8554 chars | 215 lines | 843 words
- Reduction: 86.8%
- Legacy docs read set: docs/initiatives/active/anchor-sliced-dispatch-optimization/total-task-doc.md, plugins/forgeloop/skills/run-initiative/SKILL.md, plugins/forgeloop/skills/run-initiative/references/runtime-cutover.md, plugins/forgeloop/skills/run-initiative/references/global-state.md, tests/codex/token-benchmark/fixtures/global-state-waiting.md
- Minimal docs read set: plugins/forgeloop/skills/run-initiative/references/runtime-cutover.md#current-mode, plugins/forgeloop/skills/run-initiative/SKILL.md#when-to-stop, plugins/forgeloop/skills/run-initiative/SKILL.md#main-flow, plugins/forgeloop/skills/run-initiative/references/global-state.md#durable-rules, plugins/forgeloop/skills/run-initiative/references/global-state.md#runtime-routing-vocabulary, tests/codex/token-benchmark/fixtures/global-state-waiting.md#current-snapshot, tests/codex/token-benchmark/fixtures/global-state-waiting.md#next-action, tests/codex/token-benchmark/fixtures/global-state-waiting.md#last-transition
- Fallback points: stop reason cannot be stated formally, resume invalidates the parked control state

### same-task warm-path delta legal

- Bucket: `hot_path`
- Scope: `runtime`
- Gating: `gating`
- Description: Continue the same Task on a legal warm path using a self-sufficient delta packet rather than replaying the full packet.
- Legacy packet: 13202 tok approx | 52806 chars | 1031 lines | 6841 words
- Minimal packet: 4305 tok approx | 17217 chars | 388 lines | 2174 words
- Reduction: 67.4%
- Legacy docs read set: plugins/forgeloop/skills/run-initiative/SKILL.md, plugins/forgeloop/skills/code-loop/SKILL.md, plugins/forgeloop/skills/code-loop/references/runtime-object-modes.md, plugins/forgeloop/skills/run-initiative/references/runtime-cutover.md, plugins/forgeloop/skills/run-initiative/references/task-review-rolling-doc.md, tests/codex/token-benchmark/fixtures/global-state-active-task.md, tests/fixtures/anchor-slicing/task-review-sample.md
- Minimal docs read set: plugins/forgeloop/agents/coder.toml, plugins/forgeloop/skills/code-loop/references/runtime-object-modes.md#task-mode, plugins/forgeloop/skills/run-initiative/references/task-review-rolling-doc.md#canonical-task-vocabulary, plugins/forgeloop/skills/run-initiative/references/task-review-rolling-doc.md#derived-view-usage, tests/codex/token-benchmark/fixtures/global-state-active-task.md#current-snapshot, tests/codex/token-benchmark/fixtures/global-state-active-task.md#next-action, tests/fixtures/anchor-slicing/task-review-sample.md::attempt-aware/round-2.md
- Fallback points: delta legality is proven only while the active object, round, slot, and handoff surface stay stable, derived view invalidation

### same-task warm-path delta illegal -> full packet fallback

- Bucket: `hot_path`
- Scope: `runtime`
- Gating: `gating`
- Description: When the same-task warm-path delta cannot prove legality because the formal frontier has advanced past the candidate round, the packet must fall back to an explicit full packet instead of sending delta-only state.
- Legacy packet: 13232 tok approx | 52927 chars | 1031 lines | 6858 words
- Minimal packet: 8035 tok approx | 32138 chars | 780 lines | 4013 words
- Reduction: 39.3%
- Legacy docs read set: plugins/forgeloop/skills/run-initiative/SKILL.md, plugins/forgeloop/skills/code-loop/SKILL.md, plugins/forgeloop/skills/code-loop/references/runtime-object-modes.md, plugins/forgeloop/skills/run-initiative/references/runtime-cutover.md, plugins/forgeloop/skills/run-initiative/references/task-review-rolling-doc.md, tests/codex/token-benchmark/fixtures/global-state-active-task.md, tests/fixtures/anchor-slicing/task-review-sample.md
- Minimal docs read set: plugins/forgeloop/agents/coder.toml, plugins/forgeloop/skills/code-loop/references/runtime-object-modes.md, plugins/forgeloop/skills/run-initiative/references/runtime-cutover.md, plugins/forgeloop/skills/run-initiative/references/task-review-rolling-doc.md, tests/codex/token-benchmark/fixtures/global-state-active-task.md, tests/fixtures/anchor-slicing/task-review-sample.md
- Fallback points: warm-path delta legality failed, full packet fallback is required before continuing the same Task
- Executable preconditions: 2/2 passed
-   [pass] active snapshot still points at round 2
-   [pass] latest current frontier has already advanced to round 3

### selector legality failure -> full-doc fallback

- Bucket: `hot_path`
- Scope: `runtime`
- Gating: `gating`
- Description: If selector validation fails on a hot path, the benchmark first proves that failure with an executable probe and then measures the explicit full-document fallback packet.
- Legacy packet: 9563 tok approx | 38251 chars | 738 lines | 4945 words
- Minimal packet: 8010 tok approx | 32038 chars | 781 lines | 3994 words
- Reduction: 16.2%
- Legacy docs read set: plugins/forgeloop/skills/run-initiative/SKILL.md, plugins/forgeloop/skills/run-initiative/references/runtime-cutover.md, plugins/forgeloop/skills/run-initiative/references/task-review-rolling-doc.md, tests/codex/token-benchmark/fixtures/global-state-active-task.md, tests/fixtures/anchor-slicing/task-review-sample.md
- Minimal docs read set: plugins/forgeloop/agents/coder.toml, plugins/forgeloop/skills/code-loop/references/runtime-object-modes.md, plugins/forgeloop/skills/run-initiative/references/runtime-cutover.md, plugins/forgeloop/skills/run-initiative/references/task-review-rolling-doc.md, tests/codex/token-benchmark/fixtures/global-state-active-task.md, tests/fixtures/anchor-slicing/task-review-sample.md
- Fallback points: missing_anchor, duplicate_anchor, illegal_selector
- Executable preconditions: 1/1 passed
-   [pass] illegal selector fixture is rejected by anchor validation

## Runtime Aggregate

- Hot path reduction: 59.0% (106614 -> 43743 tok approx)
- Cold path reduction: 69.8% (56519 -> 17043 tok approx)
- Total reduction: 62.7% (163133 -> 60786 tok approx)
- Task hot path average reduction: 64.2%
- Gate mode: gating

## Planning Report-Only Scenarios

### planning cold entry

- Bucket: `cold_path`
- Scope: `planning`
- Gating: `report_only`
- Description: Bind the current initiative and planning stage from durable references without treating provider token counts as authoritative evidence.
- Legacy packet: 20808 tok approx | 83230 chars | 1268 lines | 9562 words
- Minimal packet: 4579 tok approx | 18315 chars | 318 lines | 2188 words
- Reduction: 78.0%
- Legacy docs read set: docs/initiatives/active/anchor-sliced-dispatch-optimization/design.md, docs/initiatives/active/anchor-sliced-dispatch-optimization/gap-analysis.md, docs/initiatives/active/anchor-sliced-dispatch-optimization/total-task-doc.md, plugins/forgeloop/skills/planning-loop/SKILL.md, plugins/forgeloop/skills/planning-loop/references/planning-rolling-doc.md, plugins/forgeloop/skills/references/anchor-addressing.md
- Minimal docs read set: docs/initiatives/active/anchor-sliced-dispatch-optimization/design.md#requirement-baseline, docs/initiatives/active/anchor-sliced-dispatch-optimization/design.md#scope-and-non-goals, plugins/forgeloop/skills/planning-loop/SKILL.md#stage-reference-binding, plugins/forgeloop/skills/planning-loop/SKILL.md#shared-rolling-doc-contract, plugins/forgeloop/skills/planning-loop/SKILL.md#truth-sources-boundaries, plugins/forgeloop/skills/planning-loop/SKILL.md#workflow, plugins/forgeloop/skills/planning-loop/references/planning-rolling-doc.md#required-header, plugins/forgeloop/skills/planning-loop/references/planning-rolling-doc.md#round-law, plugins/forgeloop/skills/references/anchor-addressing.md#resolution-contract
- Fallback points: selector legality failure, active planning stage cannot be confirmed uniquely

### same-stage planner continue

- Bucket: `hot_path`
- Scope: `planning`
- Gating: `report_only`
- Description: Continue an already-open planning round from the active planner surface without replaying the full rolling doc every time.
- Legacy packet: 7219 tok approx | 28875 chars | 511 lines | 3657 words
- Minimal packet: 3554 tok approx | 14214 chars | 367 lines | 1392 words
- Reduction: 50.8%
- Legacy docs read set: plugins/forgeloop/skills/planning-loop/SKILL.md, plugins/forgeloop/skills/planning-loop/references/planning-rolling-doc.md, tests/codex/token-benchmark/fixtures/planning-design-repair-sample.md
- Minimal docs read set: plugins/forgeloop/skills/planning-loop/references/design-doc.md, plugins/forgeloop/skills/planning-loop/references/planning-rolling-doc.md#planner-update-law, plugins/forgeloop/skills/planning-loop/references/planning-rolling-doc.md#seal-repair-reopen, tests/codex/token-benchmark/fixtures/planning-design-repair-sample.md::attempt-aware/round-2.md
- Fallback points: round ambiguity, derived view invalidation

### fresh planning reviewer handoff

- Bucket: `hot_path`
- Scope: `planning`
- Gating: `report_only`
- Description: Dispatch a fresh planning reviewer from the current stage-local handoff surface instead of replaying the whole planning history.
- Legacy packet: 8837 tok approx | 35347 chars | 647 lines | 4630 words
- Minimal packet: 5315 tok approx | 21260 chars | 535 lines | 2401 words
- Reduction: 39.9%
- Legacy docs read set: plugins/forgeloop/skills/planning-loop/SKILL.md, plugins/forgeloop/skills/planning-loop/references/planning-rolling-doc.md, plugins/forgeloop/agents/design_reviewer.toml, tests/codex/token-benchmark/fixtures/planning-design-handoff-sample.md
- Minimal docs read set: plugins/forgeloop/skills/planning-loop/references/design-doc.md, plugins/forgeloop/skills/planning-loop/references/planning-rolling-doc.md#handoff-law, plugins/forgeloop/skills/planning-loop/references/planning-rolling-doc.md#freshness-selection, tests/codex/token-benchmark/fixtures/planning-design-handoff-sample.md::handoff-scoped/design-r2-a1.md, plugins/forgeloop/agents/design_reviewer.toml
- Fallback points: fresh reviewer packet must stay self-sufficient, handoff-scoped view invalidation

### review changes requested -> reopen next round

- Bucket: `hot_path`
- Scope: `planning`
- Gating: `report_only`
- Description: Expose review-driven reopen routing explicitly when a planning review requests upstream changes instead of hiding it in human interpretation.
- Legacy packet: 9660 tok approx | 38640 chars | 685 lines | 4731 words
- Minimal packet: 3882 tok approx | 15525 chars | 276 lines | 1791 words
- Reduction: 59.8%
- Legacy docs read set: plugins/forgeloop/skills/planning-loop/SKILL.md, plugins/forgeloop/skills/planning-loop/references/planning-rolling-doc.md, docs/initiatives/active/anchor-sliced-dispatch-optimization/design.md, tests/codex/token-benchmark/fixtures/planning-gap-reopen-sample.md
- Minimal docs read set: plugins/forgeloop/skills/planning-loop/SKILL.md#workflow, plugins/forgeloop/skills/planning-loop/SKILL.md#stop-conditions, plugins/forgeloop/skills/planning-loop/references/planning-rolling-doc.md#review-result-law, plugins/forgeloop/skills/planning-loop/references/planning-rolling-doc.md#seal-repair-reopen, docs/initiatives/active/anchor-sliced-dispatch-optimization/design.md#requirement-baseline, tests/codex/token-benchmark/fixtures/planning-gap-reopen-sample.md::current-effective.md
- Fallback points: upstream reopen recommendation is missing or malformed, stale review result must not drive reopen routing

## Planning Aggregate

- Hot path reduction: 50.4% (25716 -> 12751 tok approx)
- Cold path reduction: 78.0% (20808 -> 4579 tok approx)
- Total reduction: 62.8% (46524 -> 17330 tok approx)
- Gate mode: report-only

## Runtime Gate

- Status: pass
- Enforced thresholds: total >= 45.0%, task hot path >= 50.0%
