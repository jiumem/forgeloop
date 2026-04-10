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
- Legacy packet: 22814 tok approx | 91255 chars | 1424 lines | 10097 words
- Minimal packet: 3167 tok approx | 12668 chars | 256 lines | 1180 words
- Reduction: 86.1%
- Legacy docs read set: docs/initiatives/active/anchor-sliced-dispatch-optimization/design.md, docs/initiatives/active/anchor-sliced-dispatch-optimization/gap-analysis.md, docs/initiatives/active/anchor-sliced-dispatch-optimization/total-task-doc.md, plugins/forgeloop/skills/run-initiative/SKILL.md, plugins/forgeloop/skills/run-initiative/references/runtime-cutover.md, plugins/forgeloop/skills/run-initiative/references/global-state.md
- Minimal docs read set: docs/initiatives/active/anchor-sliced-dispatch-optimization/design.md#requirement-baseline, docs/initiatives/active/anchor-sliced-dispatch-optimization/design.md#target-state-design, docs/initiatives/active/anchor-sliced-dispatch-optimization/gap-analysis.md#baseline-and-scope, docs/initiatives/active/anchor-sliced-dispatch-optimization/total-task-doc.md#input-baseline-and-sealed-decisions, docs/initiatives/active/anchor-sliced-dispatch-optimization/total-task-doc.md#task-ledger, plugins/forgeloop/skills/run-initiative/references/runtime-cutover.md#current-mode, plugins/forgeloop/skills/run-initiative/references/runtime-cutover.md#default-read-law, plugins/forgeloop/skills/run-initiative/references/global-state.md#durable-rules, plugins/forgeloop/skills/run-initiative/references/global-state.md#bootstrap-law
- Fallback points: cold start may still promote individual reads to full documents on selector legality failure

### Runtime Resume Into Active Task

- Bucket: `hot_path`
- Scope: `runtime`
- Gating: `gating`
- Description: Resume a running Task from thin control state plus the current rolling-doc frontier.
- Legacy packet: 27958 tok approx | 111832 chars | 1920 lines | 12492 words
- Minimal packet: 2021 tok approx | 8082 chars | 262 lines | 667 words
- Reduction: 92.8%
- Legacy docs read set: docs/initiatives/active/anchor-sliced-dispatch-optimization/design.md, docs/initiatives/active/anchor-sliced-dispatch-optimization/gap-analysis.md, docs/initiatives/active/anchor-sliced-dispatch-optimization/total-task-doc.md, plugins/forgeloop/skills/run-initiative/SKILL.md, plugins/forgeloop/skills/code-loop/SKILL.md, plugins/forgeloop/skills/code-loop/references/runtime-object-modes.md, plugins/forgeloop/skills/run-initiative/references/runtime-cutover.md, plugins/forgeloop/skills/run-initiative/references/task-review-rolling-doc.md, tests/codex/token-benchmark/fixtures/global-state-active-task.md, tests/fixtures/anchor-slicing/task-review-sample.md
- Minimal docs read set: docs/initiatives/active/anchor-sliced-dispatch-optimization/total-task-doc.md#task-ledger, docs/initiatives/active/anchor-sliced-dispatch-optimization/total-task-doc.md#acceptance-matrix, plugins/forgeloop/skills/run-initiative/references/runtime-cutover.md#current-mode, plugins/forgeloop/skills/code-loop/references/runtime-object-modes.md#task-mode, plugins/forgeloop/skills/run-initiative/references/task-review-rolling-doc.md#review-handoff-law, tests/codex/token-benchmark/fixtures/global-state-active-task.md#current-snapshot, tests/codex/token-benchmark/fixtures/global-state-active-task.md#next-action, tests/fixtures/anchor-slicing/task-review-sample.md::current-effective.md
- Fallback points: selector legality failure, global-state and rolling-doc conflict

### Same-Task Same-Round Coder Continue

- Bucket: `hot_path`
- Scope: `runtime`
- Gating: `gating`
- Description: Continue the same Task coder slot inside the current round without replaying full history.
- Legacy packet: 8683 tok approx | 34732 chars | 836 lines | 4095 words
- Minimal packet: 4270 tok approx | 17079 chars | 418 lines | 2128 words
- Reduction: 50.8%
- Legacy docs read set: plugins/forgeloop/skills/code-loop/SKILL.md, plugins/forgeloop/skills/code-loop/references/runtime-object-modes.md, plugins/forgeloop/skills/run-initiative/references/runtime-cutover.md, plugins/forgeloop/skills/run-initiative/references/task-review-rolling-doc.md, tests/fixtures/anchor-slicing/task-review-sample.md, tests/codex/token-benchmark/fixtures/global-state-active-task.md
- Minimal docs read set: plugins/forgeloop/agents/coder.toml, plugins/forgeloop/skills/code-loop/references/runtime-object-modes.md#task-mode, plugins/forgeloop/skills/run-initiative/references/task-review-rolling-doc.md#round-shape-law, plugins/forgeloop/skills/run-initiative/references/task-review-rolling-doc.md#review-handoff-law, tests/codex/token-benchmark/fixtures/global-state-active-task.md#current-snapshot, tests/codex/token-benchmark/fixtures/global-state-active-task.md#next-action, tests/fixtures/anchor-slicing/task-review-sample.md::round-scoped/round-2.md
- Fallback points: round ambiguity, handoff mismatch

### Same-Task Reviewer Entry

- Bucket: `hot_path`
- Scope: `runtime`
- Gating: `gating`
- Description: Dispatch the current Task reviewer against only the current handoff surface.
- Legacy packet: 9917 tok approx | 39666 chars | 974 lines | 4935 words
- Minimal packet: 4016 tok approx | 16061 chars | 427 lines | 1740 words
- Reduction: 59.5%
- Legacy docs read set: plugins/forgeloop/skills/code-loop/SKILL.md, plugins/forgeloop/skills/code-loop/references/runtime-object-modes.md, plugins/forgeloop/skills/run-initiative/references/runtime-cutover.md, plugins/forgeloop/skills/run-initiative/references/task-review-rolling-doc.md, tests/fixtures/anchor-slicing/task-review-sample.md, plugins/forgeloop/agents/task_reviewer.toml
- Minimal docs read set: plugins/forgeloop/agents/task_reviewer.toml, docs/initiatives/active/anchor-sliced-dispatch-optimization/total-task-doc.md#task-ledger/task-definitions/asdo-t5, docs/initiatives/active/anchor-sliced-dispatch-optimization/total-task-doc.md#acceptance-matrix/task-acceptance-index/asdo-t5, docs/initiatives/active/anchor-sliced-dispatch-optimization/total-task-doc.md#acceptance-matrix/evidence-entrypoints, plugins/forgeloop/skills/code-loop/references/runtime-object-modes.md#task-mode, plugins/forgeloop/skills/run-initiative/references/task-review-rolling-doc.md#review-handoff-law, tests/fixtures/anchor-slicing/task-review-sample.md::current-effective.md
- Fallback points: reviewer packet must still be self-sufficient, derived view invalidation

### Milestone Review

- Bucket: `hot_path`
- Scope: `runtime`
- Gating: `gating`
- Description: Hand off Milestone evidence without replaying all included Task history.
- Legacy packet: 16528 tok approx | 66111 chars | 1217 lines | 6873 words
- Minimal packet: 3735 tok approx | 14940 chars | 397 lines | 1562 words
- Reduction: 77.4%
- Legacy docs read set: docs/initiatives/active/anchor-sliced-dispatch-optimization/total-task-doc.md, plugins/forgeloop/skills/code-loop/SKILL.md, plugins/forgeloop/skills/code-loop/references/runtime-object-modes.md, plugins/forgeloop/skills/run-initiative/references/runtime-cutover.md, plugins/forgeloop/skills/run-initiative/references/milestone-review-rolling-doc.md, tests/codex/token-benchmark/fixtures/milestone-review-sample.md
- Minimal docs read set: plugins/forgeloop/agents/milestone_reviewer.toml, docs/initiatives/active/anchor-sliced-dispatch-optimization/total-task-doc.md#milestone-master-table/milestone-acceptance/asdo-m2, docs/initiatives/active/anchor-sliced-dispatch-optimization/total-task-doc.md#milestone-master-table/milestone-reference-assignment/asdo-m2, docs/initiatives/active/anchor-sliced-dispatch-optimization/total-task-doc.md#acceptance-matrix/milestone-acceptance-index/asdo-m2, docs/initiatives/active/anchor-sliced-dispatch-optimization/total-task-doc.md#acceptance-matrix/evidence-entrypoints, plugins/forgeloop/skills/code-loop/references/runtime-object-modes.md#milestone-mode, plugins/forgeloop/skills/run-initiative/references/milestone-review-rolling-doc.md#review-handoff-law, tests/codex/token-benchmark/fixtures/milestone-review-sample.md::current-effective.md
- Fallback points: multiple actionable results, selector legality failure

### Initiative Review

- Bucket: `hot_path`
- Scope: `runtime`
- Gating: `gating`
- Description: Review the delivery candidate against Milestone evidence and current initiative handoff only.
- Legacy packet: 16289 tok approx | 65156 chars | 1198 lines | 6794 words
- Minimal packet: 3554 tok approx | 14213 chars | 380 lines | 1523 words
- Reduction: 78.2%
- Legacy docs read set: docs/initiatives/active/anchor-sliced-dispatch-optimization/total-task-doc.md, plugins/forgeloop/skills/code-loop/SKILL.md, plugins/forgeloop/skills/code-loop/references/runtime-object-modes.md, plugins/forgeloop/skills/run-initiative/references/runtime-cutover.md, plugins/forgeloop/skills/run-initiative/references/initiative-review-rolling-doc.md, tests/codex/token-benchmark/fixtures/initiative-review-sample.md
- Minimal docs read set: plugins/forgeloop/agents/initiative_reviewer.toml, docs/initiatives/active/anchor-sliced-dispatch-optimization/total-task-doc.md#initiative/success-criteria/ic-5, docs/initiatives/active/anchor-sliced-dispatch-optimization/total-task-doc.md#acceptance-matrix/initiative-acceptance-index/ic-5, docs/initiatives/active/anchor-sliced-dispatch-optimization/total-task-doc.md#acceptance-matrix/evidence-entrypoints, plugins/forgeloop/skills/code-loop/references/runtime-object-modes.md#initiative-mode, plugins/forgeloop/skills/run-initiative/references/initiative-review-rolling-doc.md#review-handoff-law, tests/codex/token-benchmark/fixtures/initiative-review-sample.md::current-effective.md
- Fallback points: initiative handoff drift, review target mismatch

### Rebuild Runtime

- Bucket: `cold_path`
- Scope: `runtime`
- Gating: `gating`
- Description: Recover the control plane from thin durable truth plus the newest actionable rolling-doc frontier.
- Legacy packet: 19264 tok approx | 77055 chars | 1289 lines | 7779 words
- Minimal packet: 1678 tok approx | 6710 chars | 201 lines | 554 words
- Reduction: 91.3%
- Legacy docs read set: docs/initiatives/active/anchor-sliced-dispatch-optimization/design.md, docs/initiatives/active/anchor-sliced-dispatch-optimization/gap-analysis.md, docs/initiatives/active/anchor-sliced-dispatch-optimization/total-task-doc.md, plugins/forgeloop/skills/rebuild-runtime/SKILL.md, plugins/forgeloop/skills/run-initiative/references/runtime-cutover.md, tests/codex/token-benchmark/fixtures/global-state-waiting.md, tests/codex/token-benchmark/fixtures/initiative-review-sample.md, tests/codex/token-benchmark/fixtures/milestone-review-sample.md
- Minimal docs read set: docs/initiatives/active/anchor-sliced-dispatch-optimization/total-task-doc.md#input-baseline-and-sealed-decisions, plugins/forgeloop/skills/run-initiative/references/runtime-cutover.md#current-mode, plugins/forgeloop/skills/run-initiative/references/runtime-cutover.md#fallback-law, tests/codex/token-benchmark/fixtures/global-state-waiting.md#current-snapshot, tests/codex/token-benchmark/fixtures/global-state-waiting.md#next-action, tests/codex/token-benchmark/fixtures/global-state-waiting.md#last-transition, tests/codex/token-benchmark/fixtures/initiative-review-sample.md::current-effective.md
- Fallback points: multiple active candidates coexist, derived view legality drift

### Waiting Or Blocked Resume

- Bucket: `cold_path`
- Scope: `runtime`
- Gating: `gating`
- Description: Resume from an explicit stop state without rescanning unrelated planning and runtime history.
- Legacy packet: 17295 tok approx | 69180 chars | 1084 lines | 7633 words
- Minimal packet: 1390 tok approx | 5559 chars | 170 lines | 471 words
- Reduction: 92.0%
- Legacy docs read set: docs/initiatives/active/anchor-sliced-dispatch-optimization/total-task-doc.md, plugins/forgeloop/skills/run-initiative/SKILL.md, plugins/forgeloop/skills/run-initiative/references/runtime-cutover.md, plugins/forgeloop/skills/run-initiative/references/global-state.md, tests/codex/token-benchmark/fixtures/global-state-waiting.md
- Minimal docs read set: plugins/forgeloop/skills/run-initiative/references/runtime-cutover.md#current-mode, plugins/forgeloop/skills/run-initiative/references/global-state.md#durable-rules, plugins/forgeloop/skills/run-initiative/references/global-state.md#runtime-routing-vocabulary, tests/codex/token-benchmark/fixtures/global-state-waiting.md#current-snapshot, tests/codex/token-benchmark/fixtures/global-state-waiting.md#next-action, tests/codex/token-benchmark/fixtures/global-state-waiting.md#last-transition
- Fallback points: stop reason cannot be stated formally, resume invalidates the parked control state

### same-task warm-path delta legal

- Bucket: `hot_path`
- Scope: `runtime`
- Gating: `gating`
- Description: Continue the same Task on a legal warm path using a self-sufficient delta packet rather than replaying the full packet.
- Legacy packet: 13863 tok approx | 55452 chars | 1080 lines | 7008 words
- Minimal packet: 4254 tok approx | 17015 chars | 397 lines | 2132 words
- Reduction: 69.3%
- Legacy docs read set: plugins/forgeloop/skills/run-initiative/SKILL.md, plugins/forgeloop/skills/code-loop/SKILL.md, plugins/forgeloop/skills/code-loop/references/runtime-object-modes.md, plugins/forgeloop/skills/run-initiative/references/runtime-cutover.md, plugins/forgeloop/skills/run-initiative/references/task-review-rolling-doc.md, tests/codex/token-benchmark/fixtures/global-state-active-task.md, tests/fixtures/anchor-slicing/task-review-sample.md
- Minimal docs read set: plugins/forgeloop/agents/coder.toml, plugins/forgeloop/skills/code-loop/references/runtime-object-modes.md#task-mode, plugins/forgeloop/skills/run-initiative/references/task-review-rolling-doc.md#round-shape-law, plugins/forgeloop/skills/run-initiative/references/task-review-rolling-doc.md#derived-view-usage, tests/codex/token-benchmark/fixtures/global-state-active-task.md#current-snapshot, tests/codex/token-benchmark/fixtures/global-state-active-task.md#next-action, tests/fixtures/anchor-slicing/task-review-sample.md::round-scoped/round-2.md
- Fallback points: delta legality is proven only while the active object, round, slot, and handoff surface stay stable, derived view invalidation

### same-task warm-path delta illegal -> full packet fallback

- Bucket: `hot_path`
- Scope: `runtime`
- Gating: `gating`
- Description: When the same-task warm-path delta cannot prove legality because the formal frontier has advanced past the candidate round, the packet must fall back to an explicit full packet instead of sending delta-only state.
- Legacy packet: 13894 tok approx | 55573 chars | 1080 lines | 7025 words
- Minimal packet: 9197 tok approx | 36788 chars | 886 lines | 4500 words
- Reduction: 33.8%
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
- Legacy packet: 10758 tok approx | 43030 chars | 828 lines | 5435 words
- Minimal packet: 9172 tok approx | 36688 chars | 887 lines | 4481 words
- Reduction: 14.7%
- Legacy docs read set: plugins/forgeloop/skills/run-initiative/SKILL.md, plugins/forgeloop/skills/run-initiative/references/runtime-cutover.md, plugins/forgeloop/skills/run-initiative/references/task-review-rolling-doc.md, tests/codex/token-benchmark/fixtures/global-state-active-task.md, tests/fixtures/anchor-slicing/task-review-sample.md
- Minimal docs read set: plugins/forgeloop/agents/coder.toml, plugins/forgeloop/skills/code-loop/references/runtime-object-modes.md, plugins/forgeloop/skills/run-initiative/references/runtime-cutover.md, plugins/forgeloop/skills/run-initiative/references/task-review-rolling-doc.md, tests/codex/token-benchmark/fixtures/global-state-active-task.md, tests/fixtures/anchor-slicing/task-review-sample.md
- Fallback points: missing_anchor, duplicate_anchor, illegal_selector
- Executable preconditions: 1/1 passed
-   [pass] illegal selector fixture is rejected by anchor validation

## Runtime Aggregate

- Hot path reduction: 65.9% (117890 -> 40219 tok approx)
- Cold path reduction: 89.5% (59373 -> 6235 tok approx)
- Total reduction: 73.8% (177263 -> 46454 tok approx)
- Task hot path average reduction: 68.1%
- Gate mode: gating

## Planning Report-Only Scenarios

### planning cold entry

- Bucket: `cold_path`
- Scope: `planning`
- Gating: `report_only`
- Description: Bind the current initiative and planning stage from durable references without treating provider token counts as authoritative evidence.
- Legacy packet: 23372 tok approx | 93486 chars | 1401 lines | 10403 words
- Minimal packet: 4855 tok approx | 19417 chars | 313 lines | 2378 words
- Reduction: 79.2%
- Legacy docs read set: docs/initiatives/active/anchor-sliced-dispatch-optimization/design.md, docs/initiatives/active/anchor-sliced-dispatch-optimization/gap-analysis.md, docs/initiatives/active/anchor-sliced-dispatch-optimization/total-task-doc.md, plugins/forgeloop/skills/planning-loop/SKILL.md, plugins/forgeloop/skills/planning-loop/references/planning-rolling-doc.md, plugins/forgeloop/skills/references/anchor-addressing.md
- Minimal docs read set: docs/initiatives/active/anchor-sliced-dispatch-optimization/design.md#requirement-baseline, docs/initiatives/active/anchor-sliced-dispatch-optimization/design.md#scope-and-non-goals, plugins/forgeloop/skills/planning-loop/SKILL.md#stage-reference-binding, plugins/forgeloop/skills/planning-loop/SKILL.md#shared-rolling-doc-contract, plugins/forgeloop/skills/planning-loop/SKILL.md#truth-sources-boundaries, plugins/forgeloop/skills/planning-loop/SKILL.md#workflow, plugins/forgeloop/skills/planning-loop/references/planning-rolling-doc.md#required-header, plugins/forgeloop/skills/planning-loop/references/planning-rolling-doc.md#round-law, plugins/forgeloop/skills/references/anchor-addressing.md#resolution-contract
- Fallback points: selector legality failure, active planning stage cannot be confirmed uniquely

### same-stage planner continue

- Bucket: `hot_path`
- Scope: `planning`
- Gating: `report_only`
- Description: Continue an already-open planning round from the active planner surface without replaying the full rolling doc every time.
- Legacy packet: 7836 tok approx | 31341 chars | 497 lines | 4010 words
- Minimal packet: 3567 tok approx | 14267 chars | 361 lines | 1403 words
- Reduction: 54.5%
- Legacy docs read set: plugins/forgeloop/skills/planning-loop/SKILL.md, plugins/forgeloop/skills/planning-loop/references/planning-rolling-doc.md, tests/codex/token-benchmark/fixtures/planning-design-repair-sample.md
- Minimal docs read set: plugins/forgeloop/skills/planning-loop/references/design-doc.md, plugins/forgeloop/skills/planning-loop/references/planning-rolling-doc.md#planner-update-law, plugins/forgeloop/skills/planning-loop/references/planning-rolling-doc.md#seal-repair-reopen, tests/codex/token-benchmark/fixtures/planning-design-repair-sample.md::attempt-aware/round-2.md
- Fallback points: round ambiguity, derived view invalidation

### current-stage reviewer entry

- Bucket: `hot_path`
- Scope: `planning`
- Gating: `report_only`
- Description: Dispatch the current planning reviewer from the current stage-local handoff surface instead of replaying the whole planning history.
- Legacy packet: 9508 tok approx | 38030 chars | 635 lines | 5019 words
- Minimal packet: 5345 tok approx | 21377 chars | 531 lines | 2433 words
- Reduction: 43.8%
- Legacy docs read set: plugins/forgeloop/skills/planning-loop/SKILL.md, plugins/forgeloop/skills/planning-loop/references/planning-rolling-doc.md, plugins/forgeloop/agents/design_reviewer.toml, tests/codex/token-benchmark/fixtures/planning-design-handoff-sample.md
- Minimal docs read set: plugins/forgeloop/skills/planning-loop/references/design-doc.md, plugins/forgeloop/skills/planning-loop/references/planning-rolling-doc.md#handoff-law, plugins/forgeloop/skills/planning-loop/references/planning-rolling-doc.md#current-law-selection, tests/codex/token-benchmark/fixtures/planning-design-handoff-sample.md::handoff-scoped/design-r2-a1.md, plugins/forgeloop/agents/design_reviewer.toml
- Fallback points: reviewer packet must stay self-sufficient, handoff-scoped view invalidation

### review changes requested -> reopen next round

- Bucket: `hot_path`
- Scope: `planning`
- Gating: `report_only`
- Description: Expose review-driven reopen routing explicitly when a planning review requests upstream changes instead of hiding it in human interpretation.
- Legacy packet: 10279 tok approx | 41116 chars | 671 lines | 5084 words
- Minimal packet: 4362 tok approx | 17447 chars | 268 lines | 2073 words
- Reduction: 57.6%
- Legacy docs read set: plugins/forgeloop/skills/planning-loop/SKILL.md, plugins/forgeloop/skills/planning-loop/references/planning-rolling-doc.md, docs/initiatives/active/anchor-sliced-dispatch-optimization/design.md, tests/codex/token-benchmark/fixtures/planning-gap-reopen-sample.md
- Minimal docs read set: plugins/forgeloop/skills/planning-loop/SKILL.md#workflow, plugins/forgeloop/skills/planning-loop/SKILL.md#stop-conditions, plugins/forgeloop/skills/planning-loop/references/planning-rolling-doc.md#review-result-law, plugins/forgeloop/skills/planning-loop/references/planning-rolling-doc.md#seal-repair-reopen, docs/initiatives/active/anchor-sliced-dispatch-optimization/design.md#requirement-baseline, tests/codex/token-benchmark/fixtures/planning-gap-reopen-sample.md::current-effective.md
- Fallback points: upstream reopen recommendation is missing or malformed, stale review result must not drive reopen routing

## Planning Aggregate

- Hot path reduction: 51.9% (27623 -> 13274 tok approx)
- Cold path reduction: 79.2% (23372 -> 4855 tok approx)
- Total reduction: 64.4% (50995 -> 18129 tok approx)
- Gate mode: report-only

## Runtime Gate

- Status: pass
- Enforced thresholds: total >= 45.0%, task hot path >= 50.0%
