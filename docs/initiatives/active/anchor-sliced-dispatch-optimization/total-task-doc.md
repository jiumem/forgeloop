# Anchor-Sliced Dispatch Optimization 总任务文档（Total Task Doc）

<!-- forgeloop:anchor input-baseline -->
## 1. 前置输入与决策基线（Input Baseline And Sealed Decisions）
### 1.1 需求摘要（Requirement Summary）
- 本 Initiative 的执行目标是在不新增第二真理源的前提下，把 Forgeloop 的 planning / runtime 热路径从默认整文读取收缩为 `authoritative repo-root-relative refs + anchor selectors + 最小必要切片`。
- 执行必须保留 cold start、runtime rebuild、anchor legality failure、anchor conflict 时的整文恢复能力，且不得改写现有 `round`、`handoff_id`、`review_target_ref`、freshness law、或 repo-root-relative durable ref 语义。
- 执行切片固定为三个 Milestone：`ASDO-M1` anchor / slicing infrastructure、`ASDO-M2` runtime dispatch contract shrink、`ASDO-M3` rolling-doc slimming / derived views / validation / migration。

### 1.2 设计引用（Design Refs）
- sealed `Design Doc`: `docs/initiatives/active/anchor-sliced-dispatch-optimization/design.md`

### 1.3 差距分析引用（Gap Analysis Refs, if applicable）
- sealed `Gap Analysis Doc`: `docs/initiatives/active/anchor-sliced-dispatch-optimization/gap-analysis.md`
- sealed `Design Doc` 已显式声明 `Gap Analysis Requirement: required`，本节与该路由保持一致。

### 1.4 已封板决策（Sealed Decisions）
- 正式 planning artifacts、`Planning State Doc`、`Global State Doc`、以及 planning/runtime rolling docs 继续是唯一权威源；anchor、slice、derived view 只能建立在这些表面之上。
- 默认 dispatch packet 必须收缩为 anchor-addressed minimal packet；整文读取只保留给 cold start、runtime rebuild、anchor legality failure、anchor conflict。
- rolling docs 必须支持 handoff-scoped / attempt-aware / current-effective derived views，但 freshness / supersede law 仍以既有 append-only contracts 为准。
- 执行不得在 `Total Task Doc` 里重新裁决 anchor 语法、parser 落点、projection materialization 形式；这些保持在 sealed upstream planning 允许的实现自由度内。

### 1.5 执行边界（Execution Boundary）
- 本文档承载的唯一权威内容是：Initiative / Milestone / Task 对象切分、依赖顺序、法定 durable refs、Milestone/Task/Initiative 验收线、分支与 PR 集成路径、以及 evidence entrypoints。
- 本文档不承载：设计 reopen、Gap blocker 再裁决、迁移分析长文、实现教程、review verdict、或 runtime 进度日志。
- 下游 coder / reviewer 可在不重建隐藏意图的前提下，直接从本文档恢复第一可执行 Task、Milestone handoff 边界、以及 Initiative delivery 入口。

### 1.6 Initiative 法定引用指派（Initiative Reference Assignment）
| Ref Slot | Durable Ref | 用途 |
| --- | --- | --- |
| `design_ref` | `docs/initiatives/active/anchor-sliced-dispatch-optimization/design.md` | sealed 设计真理源 |
| `gap_analysis_ref` | `docs/initiatives/active/anchor-sliced-dispatch-optimization/gap-analysis.md` | sealed gap 真理源 |
| `total_task_doc_ref` | `docs/initiatives/active/anchor-sliced-dispatch-optimization/total-task-doc.md` | sealed 执行地图真理源 |
| `global_state_doc_ref` | `docs/initiatives/active/anchor-sliced-dispatch-optimization/.forgeloop/global-state.md` | runtime control spine |
| `task_review_rolling_doc_root_ref` | `docs/initiatives/active/anchor-sliced-dispatch-optimization/.forgeloop/task-review/` | Task `G1 / anchor / fixup / R1` 根目录 |
| `milestone_review_rolling_doc_root_ref` | `docs/initiatives/active/anchor-sliced-dispatch-optimization/.forgeloop/milestone-review/` | Milestone `G2 / R2` 根目录 |
| `initiative_review_rolling_doc_ref` | `docs/initiatives/active/anchor-sliced-dispatch-optimization/.forgeloop/initiative-review.md` | Initiative `G3 / R3` 唯一 rolling doc |

<!-- forgeloop:anchor initiative-overview -->
## 2. Initiative 总览（Initiative）
### 2.1 背景（Background）
- 当前 repo 已有 planning/runtime 正式合同与 object-level review loops，但热路径仍主要靠整文或整份 rolling doc 读取。
- sealed upstream planning 已把本 Initiative 固定为一次收敛工程：先建立稳定地址层，再收缩 dispatch packet，最后补齐 derived views、validation、migration。

### 2.2 范围（Scope）
- 为 planning docs、runtime control docs、review baselines 建立稳定 text-anchor 覆盖、解析、合法性检查与 namespace 边界。
- 把 planning/runtime dispatch 与 reviewer admission 改为默认消费最小 authoritative packet，并保留显式整文 fallback。
- 交付 rolling-doc derived views、validation、migration/cutover、以及与现有 runtime admission 兼容的执行入口。

### 2.3 非目标（Non-Goals）
- 不把 packet、projection cache、或 slim views 升格为新的 durable source。
- 不在本 Initiative 内重写 `G1 / G2 / G3`、`R1 / R2 / R3` 或 `Global State Doc` / planning-state 语义。
- 不把 parser 具体实现、anchor 具体 markdown 语法、或 projection materialization 形式写死成新的设计裁决。

### 2.4 成功标准（Success Criteria）
本节是 Initiative 成功标准的唯一权威来源。

| Criterion | Success Standard |
| --- | --- |
| `IC-1` | `ASDO-M1` 到 `ASDO-M3` 全部 clean 通过各自 Milestone acceptance，且 `ASDO-T1` 到 `ASDO-T9` 全部完成，无孤儿 Task 或额外执行对象。 |
| `IC-2` | `run-initiative` 可仅依赖 `1.6` 中的 canonical refs 完成 planning admission；若 runtime docs 尚未 materialize，也能唯一确认 cold-start durable refs。 |
| `IC-3` | planning/runtime 热路径默认读取 authoritative refs + anchor selectors + 最小必要切片；anchor 缺失、冲突、或 legality 无法证明时，整文 fallback 仍显式合法。 |
| `IC-4` | derived current-effective / handoff-scoped / attempt-aware 视图可从正式 rolling docs 重建，且不会改变 `round`、`handoff_id`、`review_target_ref`、freshness、或 repo-root-relative durable refs 的现有法律语义。 |
| `IC-5` | `docs/initiatives/active/anchor-sliced-dispatch-optimization/.forgeloop/initiative-review.md` 能基于三个 Milestone review docs 与其 evidence 完成 clean `R3` 判断并支持 `mark_initiative_delivered`，且 residual risks 只剩法律允许保留的非阻塞项。 |

<!-- forgeloop:anchor milestone-master-table -->
## 3. Milestone 总表（Milestone Master Table）
### 3.1 Milestone 列表（Milestone List）
| Milestone Key | Slice | Task Keys | Planned PR Model |
| --- | --- | --- | --- |
| `ASDO-M1` | anchor / slicing infrastructure | `ASDO-T1`, `ASDO-T2`, `ASDO-T3` | `Single PR` |
| `ASDO-M2` | runtime dispatch contract shrink | `ASDO-T4`, `ASDO-T5`, `ASDO-T6` | `Single PR` |
| `ASDO-M3` | rolling-doc slimming / derived views / validation / migration | `ASDO-T7`, `ASDO-T8`, `ASDO-T9` | `Single PR` |

### 3.2 Milestone 依赖（Milestone Dependencies）
- 依赖顺序固定为 `ASDO-M1 -> ASDO-M2 -> ASDO-M3`；不计划并行 Milestone 执行。
- `ASDO-M1` 先锁定 anchor coverage、namespace、resolution、legality 与 formal-surface 暴露面。
- `ASDO-T1` 是唯一的首个可执行 Task；在没有 runtime state 的 cold start 下，`run-initiative` 应从该 Task 开始绑定执行。
- `ASDO-M2` 只能在 `ASDO-M1` clean 后进入，因为 dispatch shrink 依赖已存在的 anchor address 与 legality contract。
- `ASDO-M3` 只能在 `ASDO-M2` clean 后进入，因为 derived views、validation、migration/cutover 依赖新的 dispatch contract 已固定。

### 3.3 Milestone 验收（Milestone Acceptance）
本节是 Milestone acceptance 的唯一权威来源。

| Milestone Key | Acceptance |
| --- | --- |
| `ASDO-M1` | `ASDO-T1` 到 `ASDO-T3` 全部完成，且 required formal surfaces 已有稳定 text-anchor coverage 与 namespace 边界；text anchors 与现有 Task `anchor_ref` / `fixup_ref` 语义分离明确；下游仍只写 repo-root-relative durable refs。 |
| `ASDO-M2` | `ASDO-T4` 到 `ASDO-T6` 全部完成，且 planning/runtime dispatch 默认面已收缩为 authoritative refs + anchor selectors + 必要切片；fallback 升级条件明确；现有 routing vocabulary 与 freshness law 未被改写。 |
| `ASDO-M3` | `ASDO-T7` 到 `ASDO-T9` 全部完成，且 rolling-doc derived views、validation、migration/cutover 已可支撑 `run-initiative` planning admission 与 runtime review；整文 fallback 仍合法，residual risks 仅剩可接受余量。 |

### 3.4 Milestone 法定引用指派（Milestone Reference Assignment）
| Milestone Key | Milestone Review Rolling Doc Ref | Review Target Ref Pattern | Task Scope |
| --- | --- | --- | --- |
| `ASDO-M1` | `docs/initiatives/active/anchor-sliced-dispatch-optimization/.forgeloop/milestone-review/ASDO-M1.md` | `milestone-rounds/asdo-m1/r<round>` | `ASDO-T1`, `ASDO-T2`, `ASDO-T3` |
| `ASDO-M2` | `docs/initiatives/active/anchor-sliced-dispatch-optimization/.forgeloop/milestone-review/ASDO-M2.md` | `milestone-rounds/asdo-m2/r<round>` | `ASDO-T4`, `ASDO-T5`, `ASDO-T6` |
| `ASDO-M3` | `docs/initiatives/active/anchor-sliced-dispatch-optimization/.forgeloop/milestone-review/ASDO-M3.md` | `milestone-rounds/asdo-m3/r<round>` | `ASDO-T7`, `ASDO-T8`, `ASDO-T9` |

<!-- forgeloop:anchor task-ledger -->
## 4. Task 账本（Task Ledger）
### 4.1 Task 列表（Task List）
| Task Key | Milestone | Summary | Dependencies |
| --- | --- | --- | --- |
| `ASDO-T1` | `ASDO-M1` | 锁定 text-anchor coverage matrix、namespace law、与 required formal surfaces 清单 | `none` |
| `ASDO-T2` | `ASDO-M1` | 实现 anchor resolution / legality contract 与 failure taxonomy | `ASDO-T1` |
| `ASDO-T3` | `ASDO-M1` | 将 planning/runtime formal surfaces anchorize 到可消费边界 | `ASDO-T2` |
| `ASDO-T4` | `ASDO-M2` | 收缩 planning-stage dispatch packet 与 reviewer handoff 读取面 | `ASDO-T3` |
| `ASDO-T5` | `ASDO-M2` | 收缩 runtime admission / dispatch / rebuild 读取面 | `ASDO-T4` |
| `ASDO-T6` | `ASDO-M2` | 同步 coder / reviewer / mirror consumers 到最小 packet 合同 | `ASDO-T5` |
| `ASDO-T7` | `ASDO-M3` | 交付 rolling-doc current-effective / handoff-scoped / attempt-aware derived views | `ASDO-T6` |
| `ASDO-T8` | `ASDO-M3` | 建立 validation matrix、fixtures、与 legality / fallback / supersede 证据 | `ASDO-T7` |
| `ASDO-T9` | `ASDO-M3` | 完成 coexistence、migration/cutover、admission 收尾与 Initiative delivery candidate | `ASDO-T8` |

### 4.2 Task 定义（Task Definitions）
本节是 Task acceptance 的唯一权威来源。`4.1` 中每个 `Task Key` 在此恰好对应一个定义。

**Task Definition: `ASDO-T1`**
- `任务键（Task Key）`: `ASDO-T1`
- `设计引用（Design Refs）`: `docs/initiatives/active/anchor-sliced-dispatch-optimization/design.md`
- `差距引用（Gap Refs）`: `docs/initiatives/active/anchor-sliced-dispatch-optimization/gap-analysis.md`
- `规范引用（Spec Refs）`: `plugins/forgeloop/skills/planning-loop/SKILL.md`, `plugins/forgeloop/skills/run-initiative/SKILL.md`, `plugins/forgeloop/skills/run-initiative/references/task-review-rolling-doc.md`
- `输入（Input）`: sealed upstream planning truth、现有 planning/runtime contracts、以及所有必须被 anchor 化的正式表面。
- `动作（Action）`: 固定 text-anchor coverage matrix、namespace 规则、以及 text anchors 与现有 Task handoff anchors 的法律边界。
- `输出（Output）`: 一个可执行的 coverage / ownership 基线，使后续任务可以唯一判断哪些正式表面暴露 anchors、哪些只消费 anchors。
- `非目标（Non-Goals）`: 不锁定 anchor 具体 markdown 语法，不实现 parser。
- `依赖（Dependencies）`: `none`
- `验收（Acceptance）`: required formal surfaces 的 coverage 与 ownership 明确；text anchors 与 Task `anchor_ref` / `fixup_ref` 不再混义；不存在需要留给下游猜测的 coverage 缺口。
- `Task 局部风险 / 备注（Task-local Risks / Notes）`: 若 coverage matrix 无法覆盖必要正式表面，则必须停在当前层并回流上游，而不是继续执行。

**Task Definition: `ASDO-T2`**
- `任务键（Task Key）`: `ASDO-T2`
- `设计引用（Design Refs）`: `docs/initiatives/active/anchor-sliced-dispatch-optimization/design.md`
- `差距引用（Gap Refs）`: `docs/initiatives/active/anchor-sliced-dispatch-optimization/gap-analysis.md`
- `规范引用（Spec Refs）`: `plugins/forgeloop/skills/planning-loop/SKILL.md`, `plugins/forgeloop/skills/run-initiative/SKILL.md`, `plugins/forgeloop/skills/rebuild-runtime/SKILL.md`
- `输入（Input）`: `ASDO-T1` 的 coverage / namespace 基线，以及现有 repo-root-relative ref 与 fallback law。
- `动作（Action）`: 建立 `doc_ref + anchor selector` 的 resolution / legality contract，并定义唯一目标、冲突、缺失、漂移时的处理边界。
- `输出（Output）`: 可被 planning/runtime consumers 复用的 anchor resolution 与 legality 机制，以及 failure taxonomy。
- `非目标（Non-Goals）`: 不在本任务内改变 dispatch packet 或 derived view 行为。
- `依赖（Dependencies）`: `ASDO-T1`
- `验收（Acceptance）`: resolution 结果只能是唯一目标、显式冲突、或显式缺失；legality failure 会触发整文 fallback 或显式阻塞；repo-root-relative durable ref 语义保持不变。
- `Task 局部风险 / 备注（Task-local Risks / Notes）`: 若 legality 机制需要额外 durable state 才能成立，应视为超出 sealed design 边界。

**Task Definition: `ASDO-T3`**
- `任务键（Task Key）`: `ASDO-T3`
- `设计引用（Design Refs）`: `docs/initiatives/active/anchor-sliced-dispatch-optimization/design.md`
- `差距引用（Gap Refs）`: `docs/initiatives/active/anchor-sliced-dispatch-optimization/gap-analysis.md`
- `规范引用（Spec Refs）`: `plugins/forgeloop/skills/planning-loop/references/planning-rolling-doc.md`, `plugins/forgeloop/skills/run-initiative/references/global-state.md`, `plugins/forgeloop/skills/run-initiative/references/task-review-rolling-doc.md`, `plugins/forgeloop/skills/run-initiative/references/milestone-review-rolling-doc.md`, `plugins/forgeloop/skills/run-initiative/references/initiative-review-rolling-doc.md`
- `输入（Input）`: `ASDO-T2` 的 resolution / legality contract，现有 planning/runtime 正式合同 refs。
- `动作（Action）`: 在 planning docs、runtime control docs、review rolling-doc contracts、以及 review baselines 上暴露稳定可消费的 anchor surfaces，同时保留现有 block shape 与 freshness law。
- `输出（Output）`: anchor-addressable formal surfaces，可供 planning/runtime packet、reviewer admission、以及 review baseline 消费面精确读取。
- `非目标（Non-Goals）`: 不直接缩小 dispatch packet，不新增 derived views。
- `依赖（Dependencies）`: `ASDO-T2`
- `验收（Acceptance）`: required formal surfaces 都有可解析的 anchor 暴露面，其中包含 review baselines；现有 `round` / `handoff_id` / `review_target_ref` 法律语义未变；runtime cold-start refs 仍保持 repo-root-relative durable form。
- `Task 局部风险 / 备注（Task-local Risks / Notes）`: 若某个正式表面只能通过覆写合同语义才可 anchorize，必须停止并建议 reopen 上游。

**Task Definition: `ASDO-T4`**
- `任务键（Task Key）`: `ASDO-T4`
- `设计引用（Design Refs）`: `docs/initiatives/active/anchor-sliced-dispatch-optimization/design.md`
- `差距引用（Gap Refs）`: `docs/initiatives/active/anchor-sliced-dispatch-optimization/gap-analysis.md`
- `规范引用（Spec Refs）`: `plugins/forgeloop/skills/planning-loop/SKILL.md`, `plugins/forgeloop/skills/planning-loop/references/planning-rolling-doc.md`, `plugins/forgeloop/agents/planner.toml`, `plugins/forgeloop/agents/design_reviewer.toml`, `plugins/forgeloop/agents/gap_reviewer.toml`, `plugins/forgeloop/agents/plan_reviewer.toml`
- `输入（Input）`: `ASDO-T3` 产出的 planning-side anchor surfaces。
- `动作（Action）`: 将 planning-stage planner / reviewer dispatch packet 改为默认消费 authoritative refs + anchor selectors + 必要切片。
- `输出（Output）`: 更新后的 planning-loop dispatch 输入面与 reviewer handoff 读取面。
- `非目标（Non-Goals）`: 不处理 runtime admission，不交付 rolling-doc derived views。
- `依赖（Dependencies）`: `ASDO-T3`
- `验收（Acceptance）`: planning-stage hot path 不再默认整文重读；current handoff 仍由 rolling-doc contract 选择；selector 非法或冲突时会升级为整文读取而非猜测继续。
- `Task 局部风险 / 备注（Task-local Risks / Notes）`: 必须避免让 prompt mirror 或 dispatch 摘要变成新的真理源。

**Task Definition: `ASDO-T5`**
- `任务键（Task Key）`: `ASDO-T5`
- `设计引用（Design Refs）`: `docs/initiatives/active/anchor-sliced-dispatch-optimization/design.md`
- `差距引用（Gap Refs）`: `docs/initiatives/active/anchor-sliced-dispatch-optimization/gap-analysis.md`
- `规范引用（Spec Refs）`: `plugins/forgeloop/skills/run-initiative/SKILL.md`, `plugins/forgeloop/skills/rebuild-runtime/SKILL.md`, `plugins/forgeloop/skills/task-loop/SKILL.md`, `plugins/forgeloop/skills/milestone-loop/SKILL.md`, `plugins/forgeloop/skills/initiative-loop/SKILL.md`, `plugins/forgeloop/skills/run-initiative/references/global-state.md`
- `输入（Input）`: `ASDO-T4` 已收缩的 planning-side packet 边界，以及 runtime formal surfaces 的 anchor 暴露面。
- `动作（Action）`: 把 `run-initiative`、`rebuild-runtime`、以及三层 runtime loop 的默认读取面改为最小 authoritative packet，并保留整文 fallback。
- `输出（Output）`: runtime admission、dispatch、rebuild 的一致最小输入面。
- `非目标（Non-Goals）`: 不交付 agent mirror 清理，不引入 slim/derived rolling views。
- `依赖（Dependencies）`: `ASDO-T4`
- `验收（Acceptance）`: runtime hot path 默认读取最小 packet；`Global State Doc` 与 review rolling docs 的法律语义不变；conflict / legality failure 时可退回整文恢复。
- `Task 局部风险 / 备注（Task-local Risks / Notes）`: 若 runtime shrink 需要改写 routing vocabulary 或新增 state 字段，则必须视为上游 fracture。

**Task Definition: `ASDO-T6`**
- `任务键（Task Key）`: `ASDO-T6`
- `设计引用（Design Refs）`: `docs/initiatives/active/anchor-sliced-dispatch-optimization/design.md`
- `差距引用（Gap Refs）`: `docs/initiatives/active/anchor-sliced-dispatch-optimization/gap-analysis.md`
- `规范引用（Spec Refs）`: `plugins/forgeloop/skills/planning-loop/SKILL.md`, `plugins/forgeloop/skills/run-initiative/SKILL.md`, `plugins/forgeloop/agents/coder.toml`, `plugins/forgeloop/agents/task_reviewer.toml`, `plugins/forgeloop/agents/milestone_reviewer.toml`, `plugins/forgeloop/agents/initiative_reviewer.toml`, `plugins/forgeloop/agents/README.md`
- `输入（Input）`: `ASDO-T5` 已固定的 planning/runtime dispatch contract shrink。
- `动作（Action）`: 对 coder / reviewer executable manifests 与 mirror consumers 做最小 packet contract 对齐，确保运行时消费面与正式 skills/contracts 一致。
- `输出（Output）`: 已对齐的 executable manifests，以及不再依赖整文默认输入面的 consumer mirrors 与相关说明。
- `非目标（Non-Goals）`: 不改写 sealed planning truth，不引入新的 agent control plane。
- `依赖（Dependencies）`: `ASDO-T5`
- `验收（Acceptance）`: consumer-facing mirrors 与正式 skills/contracts 不冲突；最小 packet 与 fallback 规则均可从正式 refs 恢复；不存在平行 prompt truth。
- `Task 局部风险 / 备注（Task-local Risks / Notes）`: 仅 mirror-only 文档更新不足以证明 runtime ready，必须与正式 contract 变更同步验证。

**Task Definition: `ASDO-T7`**
- `任务键（Task Key）`: `ASDO-T7`
- `设计引用（Design Refs）`: `docs/initiatives/active/anchor-sliced-dispatch-optimization/design.md`
- `差距引用（Gap Refs）`: `docs/initiatives/active/anchor-sliced-dispatch-optimization/gap-analysis.md`
- `规范引用（Spec Refs）`: `plugins/forgeloop/skills/planning-loop/references/planning-rolling-doc.md`, `plugins/forgeloop/skills/run-initiative/references/task-review-rolling-doc.md`, `plugins/forgeloop/skills/run-initiative/references/milestone-review-rolling-doc.md`, `plugins/forgeloop/skills/run-initiative/references/initiative-review-rolling-doc.md`
- `输入（Input）`: `ASDO-T6` 完成后的最小 packet 消费边界与 anchorized rolling-doc surfaces。
- `动作（Action）`: 交付 current-effective、handoff-scoped、attempt-aware derived views 与 rolling-doc slimming surface，并固定它们的 authority / invalidation line。
- `输出（Output）`: 可丢弃、可重建、非权威的 rolling-doc projections，供 hot path 使用。
- `非目标（Non-Goals）`: 不完成 migration/cutover，不决定最终长期缓存策略。
- `依赖（Dependencies）`: `ASDO-T6`
- `验收（Acceptance）`: derived views 能从正式 rolling docs 重建；freshness / supersede law 仍由正式 rolling docs 决定；derived views 失效时可安全回退整文读取。
- `Task 局部风险 / 备注（Task-local Risks / Notes）`: 若 derived view 需要抢占正式 rolling docs 的恢复优先级，则该任务失败。

**Task Definition: `ASDO-T8`**
- `任务键（Task Key）`: `ASDO-T8`
- `设计引用（Design Refs）`: `docs/initiatives/active/anchor-sliced-dispatch-optimization/design.md`
- `差距引用（Gap Refs）`: `docs/initiatives/active/anchor-sliced-dispatch-optimization/gap-analysis.md`
- `规范引用（Spec Refs）`: `plugins/forgeloop/skills/run-initiative/SKILL.md`, `plugins/forgeloop/skills/rebuild-runtime/SKILL.md`, `plugins/forgeloop/skills/planning-loop/references/planning-rolling-doc.md`
- `输入（Input）`: `ASDO-T7` 的 derived views 与 prior milestones 的 contract changes。
- `动作（Action）`: 建立 validation matrix、fixtures、与回归证据，覆盖 anchor legality、supersede/current-effective 选择、dispatch shrink、fallback、以及 rebuild。
- `输出（Output）`: 可在 Task / Milestone / Initiative review docs 中复用的验证入口与证据集。
- `非目标（Non-Goals）`: 不做 cutover 执行，不把测试输出写成新的 durable state。
- `依赖（Dependencies）`: `ASDO-T7`
- `验收（Acceptance）`: 关键场景均有明确验证入口；证据足以支持 `ASDO-M1` 到 `ASDO-M3` 的 reviewer 判断；未验证区域被明确缩小为非阻塞残余。
- `Task 局部风险 / 备注（Task-local Risks / Notes）`: 本 Initiative 当前无 runtime 实例样本，验证必须证明合同层正确性，而不是虚构业务 trace。

**Task Definition: `ASDO-T9`**
- `任务键（Task Key）`: `ASDO-T9`
- `设计引用（Design Refs）`: `docs/initiatives/active/anchor-sliced-dispatch-optimization/design.md`
- `差距引用（Gap Refs）`: `docs/initiatives/active/anchor-sliced-dispatch-optimization/gap-analysis.md`
- `规范引用（Spec Refs）`: `plugins/forgeloop/skills/run-initiative/SKILL.md`, `plugins/forgeloop/skills/rebuild-runtime/SKILL.md`, `plugins/forgeloop/skills/run-initiative/references/global-state.md`, `docs/codex/agents/README.md`
- `输入（Input）`: `ASDO-T8` 的 validation 结果、以及所有已完成的 milestone outputs。
- `动作（Action）`: 完成 coexistence law 落地、migration/cutover、runtime admission 收尾、及 Initiative delivery candidate 组装。
- `输出（Output）`: 一个可进入 `G3 / R3` 的 Initiative candidate，包含里程碑级证据入口、fallback 保证、与残余风险登记。
- `非目标（Non-Goals）`: 不继续扩大 scope 到新的 milestones 或额外 refactor。
- `依赖（Dependencies）`: `ASDO-T8`
- `验收（Acceptance）`: `run-initiative` planning admission 能接受新的 planning truth；migration 失败时仍可回滚到整文路径；三个 milestone review docs 与 initiative review doc 的 evidence chain 连续完整。
- `Task 局部风险 / 备注（Task-local Risks / Notes）`: 若 cutover 仍依赖未决 authority line 或隐式人工步骤，则必须停在当前任务并修复，而不是伪装为 follow-up。

<!-- forgeloop:anchor branch-and-pr -->
## 5. 分支与 PR 集成路径（Branch & PR Integration Path）
### 5.1 默认集成模型（Default Integration Model）
- 默认规则是 `one Milestone -> one branch -> one PR -> one Milestone Review Rolling Doc`。
- 本 Initiative 不预设 `Multi-PR Exception`；若执行中发现某个 Milestone 无法在单 PR 内保持清晰状态边界，应先修复计划对象切法，而不是临时用多 PR 掩盖过厚 Milestone。
- Task 不是独立 PR 对象；Task 在对应 Milestone branch 内完成，并通过 Task review rolling docs 提供 `G1 / anchor / fixup / R1` 证据。

### 5.2 分支计划（Branch Plan）
| Branch | Covers | Base | Merge Condition |
| --- | --- | --- | --- |
| `initiative/anchor-sliced-dispatch-optimization/m1-anchor-slicing` | `ASDO-M1` / `ASDO-T1`-`ASDO-T3` | `main` | `ASDO-M1` 达到 `3.3` 验收并有 `ASDO-M1` Milestone review evidence |
| `initiative/anchor-sliced-dispatch-optimization/m2-dispatch-shrink` | `ASDO-M2` / `ASDO-T4`-`ASDO-T6` | `initiative/anchor-sliced-dispatch-optimization/m1-anchor-slicing` 或 `main` 上已合入的 `ASDO-M1` | `ASDO-M2` 达到 `3.3` 验收并有 `ASDO-M2` Milestone review evidence |
| `initiative/anchor-sliced-dispatch-optimization/m3-slim-validate-migrate` | `ASDO-M3` / `ASDO-T7`-`ASDO-T9` | `initiative/anchor-sliced-dispatch-optimization/m2-dispatch-shrink` 或 `main` 上已合入的 `ASDO-M2` | `ASDO-M3` 达到 `3.3` 验收并有 `ASDO-M3` Milestone review evidence |

### 5.3 PR 计划（PR Plan）
| PR | Scope | Acceptance Source | Review Handoff |
| --- | --- | --- | --- |
| `PR-1 / ASDO-M1` | anchor coverage、namespace、resolution、formal-surface anchorization | `3.3 / ASDO-M1` | `docs/initiatives/active/anchor-sliced-dispatch-optimization/.forgeloop/milestone-review/ASDO-M1.md` |
| `PR-2 / ASDO-M2` | planning/runtime dispatch shrink 与 consumer contract alignment | `3.3 / ASDO-M2` | `docs/initiatives/active/anchor-sliced-dispatch-optimization/.forgeloop/milestone-review/ASDO-M2.md` |
| `PR-3 / ASDO-M3` | rolling-doc derived views、validation、migration/cutover、delivery candidate | `3.3 / ASDO-M3` | `docs/initiatives/active/anchor-sliced-dispatch-optimization/.forgeloop/milestone-review/ASDO-M3.md` |

### 5.4 PR 依赖顺序（PR Dependency Order）
1. `PR-1 / ASDO-M1`
2. `PR-2 / ASDO-M2`
3. `PR-3 / ASDO-M3`
4. `PR-3` merge 后，以三个 Milestone review docs 作为 Initiative candidate 输入，进入 `docs/initiatives/active/anchor-sliced-dispatch-optimization/.forgeloop/initiative-review.md` 的 `G3 / R3`。

<!-- forgeloop:anchor acceptance-matrix -->
## 6. 验收矩阵（Acceptance Matrix）
### 6.1 Task 验收索引（Task Acceptance Index）
| Task Key | Acceptance Authority Ref | First Evidence Ref |
| --- | --- | --- |
| `ASDO-T1` | `4.2 / ASDO-T1` | `docs/initiatives/active/anchor-sliced-dispatch-optimization/.forgeloop/task-review/ASDO-T1.md` |
| `ASDO-T2` | `4.2 / ASDO-T2` | `docs/initiatives/active/anchor-sliced-dispatch-optimization/.forgeloop/task-review/ASDO-T2.md` |
| `ASDO-T3` | `4.2 / ASDO-T3` | `docs/initiatives/active/anchor-sliced-dispatch-optimization/.forgeloop/task-review/ASDO-T3.md` |
| `ASDO-T4` | `4.2 / ASDO-T4` | `docs/initiatives/active/anchor-sliced-dispatch-optimization/.forgeloop/task-review/ASDO-T4.md` |
| `ASDO-T5` | `4.2 / ASDO-T5` | `docs/initiatives/active/anchor-sliced-dispatch-optimization/.forgeloop/task-review/ASDO-T5.md` |
| `ASDO-T6` | `4.2 / ASDO-T6` | `docs/initiatives/active/anchor-sliced-dispatch-optimization/.forgeloop/task-review/ASDO-T6.md` |
| `ASDO-T7` | `4.2 / ASDO-T7` | `docs/initiatives/active/anchor-sliced-dispatch-optimization/.forgeloop/task-review/ASDO-T7.md` |
| `ASDO-T8` | `4.2 / ASDO-T8` | `docs/initiatives/active/anchor-sliced-dispatch-optimization/.forgeloop/task-review/ASDO-T8.md` |
| `ASDO-T9` | `4.2 / ASDO-T9` | `docs/initiatives/active/anchor-sliced-dispatch-optimization/.forgeloop/task-review/ASDO-T9.md` |

### 6.2 Milestone 验收索引（Milestone Acceptance Index）
| Milestone Key | Acceptance Authority Ref | First Evidence Ref |
| --- | --- | --- |
| `ASDO-M1` | `3.3 / ASDO-M1` | `docs/initiatives/active/anchor-sliced-dispatch-optimization/.forgeloop/milestone-review/ASDO-M1.md` |
| `ASDO-M2` | `3.3 / ASDO-M2` | `docs/initiatives/active/anchor-sliced-dispatch-optimization/.forgeloop/milestone-review/ASDO-M2.md` |
| `ASDO-M3` | `3.3 / ASDO-M3` | `docs/initiatives/active/anchor-sliced-dispatch-optimization/.forgeloop/milestone-review/ASDO-M3.md` |

### 6.3 Initiative 验收索引（Initiative Acceptance Index）
| Initiative Criterion | Acceptance Authority Ref | First Evidence Ref |
| --- | --- | --- |
| `IC-1` | `2.4 / IC-1` | `docs/initiatives/active/anchor-sliced-dispatch-optimization/.forgeloop/initiative-review.md` |
| `IC-2` | `2.4 / IC-2` | `plugins/forgeloop/skills/run-initiative/SKILL.md` |
| `IC-3` | `2.4 / IC-3` | `docs/initiatives/active/anchor-sliced-dispatch-optimization/.forgeloop/milestone-review/ASDO-M2.md` |
| `IC-4` | `2.4 / IC-4` | `docs/initiatives/active/anchor-sliced-dispatch-optimization/.forgeloop/milestone-review/ASDO-M3.md` |
| `IC-5` | `2.4 / IC-5` | `docs/initiatives/active/anchor-sliced-dispatch-optimization/.forgeloop/initiative-review.md` |

### 6.4 证据入口（Evidence Entrypoints）
| Evidence Ref | Why Reviewers Start Here |
| --- | --- |
| `docs/initiatives/active/anchor-sliced-dispatch-optimization/design.md` | 设计不变量、fallback 法位、与 `Gap Analysis Requirement` 唯一真理源 |
| `docs/initiatives/active/anchor-sliced-dispatch-optimization/gap-analysis.md` | `M1` / `M2` / `M3` blocker ledger、coexistence、rollback、reroute rules |
| `docs/initiatives/active/anchor-sliced-dispatch-optimization/total-task-doc.md` | 当前执行地图、法定 refs、acceptance ownership、与 PR path |
| `docs/initiatives/active/anchor-sliced-dispatch-optimization/.forgeloop/global-state.md` | runtime 当前 active object、next action、与 recovery spine |
| `docs/initiatives/active/anchor-sliced-dispatch-optimization/.forgeloop/task-review/` | Task-level `G1 / anchor / fixup / R1` 根目录；单个 Task 的首个证据 ref 见 `6.1` |
| `docs/initiatives/active/anchor-sliced-dispatch-optimization/.forgeloop/milestone-review/ASDO-M1.md` | `ASDO-M1` 的 `G2 / R2` 证据与 anchor/slicing 基线 closure |
| `docs/initiatives/active/anchor-sliced-dispatch-optimization/.forgeloop/milestone-review/ASDO-M2.md` | `ASDO-M2` 的 `G2 / R2` 证据与 dispatch shrink closure |
| `docs/initiatives/active/anchor-sliced-dispatch-optimization/.forgeloop/milestone-review/ASDO-M3.md` | `ASDO-M3` 的 `G2 / R2` 证据与 derived views / validation / migration closure |
| `docs/initiatives/active/anchor-sliced-dispatch-optimization/.forgeloop/initiative-review.md` | Initiative-level `G3 / R3` 交付候选与 residual-risk 最终判断入口 |
| `plugins/forgeloop/skills/run-initiative/SKILL.md` | planning admission、runtime dispatch、与 cold-start / rebuild binding 规则入口 |

<!-- forgeloop:anchor global-residual-risks -->
## 7. 全局残余风险与后续事项（Global Residual Risks & Follow-Ups）
### 7.1 全局残余风险（Global Residual Risks）
- 初版 anchor coverage 与 slice granularity 可能偏粗，导致少量热路径仍暂时升级为整文 fallback；只要 fallback 显式合法，这属于可接受残余。
- 由于当前 Initiative 还没有现成 runtime doc 样本，validation 会先证明合同层 correctness，而不是业务级 trace 完整性。
- derived views 上线初期可能暴露更多 invalidation cases，但只要正式 rolling docs 仍是唯一权威源，这不会阻塞 seal。

### 7.2 后续事项（Follow-Ups）
- 在本 Initiative sealed 后，再依据真实 runtime docs 的使用数据评估是否需要更细的 consumer-specific slice granularity。
- 在 anchor-addressed dispatch 稳定后，进一步统一 reference mirrors 与 agent README 中的术语与示例。
- 若 derived views 的物化方式在真实负载下仍显笨重，可在后续 Initiative 中优化性能，但不得改变本 Initiative 已封板的 authority line。
