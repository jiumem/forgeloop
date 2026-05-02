# Forgeloop

[English README](README.md)

Forgeloop 是一套 Codex 原生的 Agent 自动编程开发系统，用来把一个软件项目长期、稳定、高质量地向前推进。

它不是项目管理工具，也不是一组提示词模板。Forgeloop 关注的是 Agent 编程真正困难的部分：如何选择下一段最值得做的开发工作，如何把目标压成可执行计划，如何让 Coder 持续交付，如何让 Reviewer 严格把关，以及如何在多轮会话、长周期开发和中断恢复中保持方向不丢、质量不散、Token 消耗可控。

Forgeloop 的核心工作流很短：

```text
Candidate -> DESIGN.md -> PLAN.md -> LEDGER.md -> DELIVERY.md
```

其中 Initiative 是用户入口和顶层专项对象，可以粗略类比传统项目管理中的 Epic，但在 Forgeloop 中不是需求聚合标签，而是必须能被 `DESIGN.md` 裁决、被 `PLAN.md` 承载、被 Milestone 分段交付、被 Reviewer 审查并最终归档的工程闭环。它可以是一个新功能、一组架构改造、一次测试体系加固、一轮性能优化、一段 API/Schema 治理、一次文档和示例完善、一个迁移工程，或者任何需要拆成多个阶段持续推进的开发目标。

## 价值和愿景

大模型已经能写出越来越复杂的代码，但长期 Agent 自动编程仍然容易卡在几个问题上：

- 下一步做什么不清楚，Agent 容易在低价值任务上消耗上下文；
- 需求没有被压成阶段计划，Coder 一上来就进入局部实现；
- 代码能跑不等于真的完成，缺少稳定的审查协议；
- 测试、Schema、架构边界、第二路径和状态重复经常在最后才暴露；
- 会话中断后，恢复依赖聊天记忆，容易跑偏；
- 多 Agent 协作时，调度、实现、审查职责混在一起，Token 消耗不可控。

Forgeloop 的目标是给 Codex 一个足够轻、足够硬的工程闭环：

- 用 `recommend-initiatives` 找到接下来最值得做的开发单元；
- 用 `grill-initiative` 把候选 Initiative 拷打、调研、裁决成 `DESIGN.md`；
- 用 `plan-initiative` 把 `DESIGN.md` 压成可执行的 `PLAN.md` 和 `LEDGER.md`；
- 用 `run-initiative` 按 Milestone 长时间推进；
- 用 `run-initiative-sequences` 串行推进 active 队列中的多个连续专项；
- 用 Coder 按 Construction Loop 负责实现、自检和证据产出；
- 用 Reviewer 从产品、测试、架构三个角度裁决；
- 用 `LEDGER.md` 和 Git 留下可恢复、可审查、可回滚的证据。

这套系统追求的是长期推送能力：不是让 Agent 完成一次演示，而是让它能在一个真实代码库里一段一段地做下去，每段都有验收、有审查、有恢复点，并且能在质量和 Token 成本之间保持稳定。

## Codex 原生体验

Forgeloop 为 Codex 的插件和技能系统设计。它默认把 Codex 当作调度者，由调度者读取计划、维护进度、分发任务入口，并协调 Coder 和 Reviewer 按各自角色协议工作。

实测中，一个很好用的组合是：

- 调度者：GPT-5.5 medium；
- Coder：GPT-5.5 high；
- Reviewer：GPT-5.5 high。

这个组合在复杂开发任务里的指令遵循、修复循环和审查质量都比较稳定，最终 Token 消耗也较可控。

如果你希望进一步降低 Token 消耗，可以尝试：

- GPT-5.4 medium 作为调度者或 Reviewer；
- GPT-5.3 Codex high 作为 Coder；
- 对低风险 Milestone 使用较低 reasoning effort，对高风险 Milestone 保持 high。

Forgeloop 不要求固定模型。它更重要的约束是职责分离：Scheduler 不直接把自己的上下文全部交给 Coder，Coder 不自我放行，Reviewer 只按真实 diff 和验收标准裁决。

## 核心模型

### Initiative 是通用开发单元

Initiative 是用户入口，也是 Forgeloop 的顶层开发单元。它可以帮助熟悉传统项目管理的人粗略理解为 Epic 级工作，但在 Forgeloop 里拥有更强的执行法位：高风险或模糊专项必须先被写成 `DESIGN.md`，再被压成 `PLAN.md`，必须能拆成多个 Milestone，必须有可验证的完成标准，并且最终必须通过交付归档收口。

典型 Initiative 可以是：

- 实现一组产品能力；
- 拆分过大的模块；
- 迁移一套旧 API；
- 整理数据模型和 Schema；
- 补齐关键测试路径；
- 做性能、稳定性或可观测性加固；
- 改造构建、发布或插件结构；
- 完成文档、示例和开发者体验升级。

一个好的 Initiative 不只是“做一些事”，而是有明确业务或工程收益，并且能被分阶段交付。

### Milestone 是交付单元

Milestone 是 `run-initiative` 的推进单位。每个 Milestone 都应该能形成一次可审查的交付，不只是任务列表。

Forgeloop 继续以 Milestone 作为推进、提交和审查单元，而不是把小 Task 变成默认调度对象。强模型已经能独立完成相当复杂的阶段性交付，过细的任务颗粒度会浪费上下文、增加复查成本，并把 Reviewer 的注意力从阶段闭环拖回零件清单。Work Items 只服务于 Milestone 内部执行检查，不成为正式生命周期对象。

Milestone 应优先是 vertical slice：让一个可审查的阶段状态在必要层面上成立，而不是按 schema-only、API-only、UI-only、tests-only 或 docs-only 这类横向施工批次拆分。只有 Initiative 明确就是横向治理、文档整理或机械迁移时，才应采用对应的横向 Milestone。

一个好的 Milestone 通常包含：

- 3 到 5 个 Work Items；
- 一个明确的 Expected Inspectable State；
- 明确的验收标准；
- 必要的验证方式；
- Reviewer 需要重点看的风险点；
- 清楚的非目标，避免 Coder 扩大范围。

一个 Initiative 通常建议 3 到 8 个 Milestone。对高风险能力，可以在功能 Milestone 后增加 Acceptance & Hardening Milestone，专门处理验收、测试补强、架构整理、大文件拆分和第二路径清理。

### Coder 是实现责任承担者

Coder 不是机械翻译 PLAN 的代码生成器，也不是正式 Reviewer。它负责在既有边界内交付正确、收敛、可验证的实现，并在提交前完成一轮轻量自检。

Coder 的 Construction Loop 包括：

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

这套内循环不把 TDD 变成独立入口，也不强制所有任务测试先行。它要求 Coder 先把 Milestone 翻译成可观察行为，优先通过 public seam 验证真实行为，薄切片实现，守住契约和真理源，检查边界和重入，报告能被 Scheduler / Reviewer 复用的验证证据，并在提交前看自己的 diff。

### Reviewer 是质量核心

Forgeloop 的核心不是让 Coder 自我放行，而是让 Coder 先完成实现自检，再让 Reviewer 真正拥有放行权。

Reviewer 必须从三个角度审查 Milestone：

1. 产品经理角度：功能是否真的可用，用户路径是否成立，关键状态是否覆盖；
2. 测试工程师角度：测试和验证是否真实覆盖验收标准，有没有浅层 smoke test、弱断言、跳过测试或伪验证；
3. 架构师角度：核心 Schema 变更是否合理，大文件是否需要拆分，是否出现第二路径、重复状态、重复 schema、影子逻辑或错误的模块边界。

Reviewer 最终只能给出：

```text
PASS
REPAIR_REQUIRED
```

只有 `PASS` 才能进入下一个 Milestone。

### Git 是证据，不是放行

Commit 和 push 用于记录差异、形成恢复点、支持审查和回滚。它们不是完成证明，也不是阶段放行信号。Forgeloop 默认采用 Milestone 粒度提交：一个 Milestone 形成一个可审查的主实现 commit；Reviewer 驱动的修复可以形成 fixup commit，但最终审查仍然看该 Milestone 的累计 diff。

Forgeloop 的推进条件是 Reviewer `PASS`，不是：

- 代码已经 commit；
- 分支已经 push；
- build 通过；
- 测试通过；
- zip 已经打包；
- Coder 自己说完成。

## 五个技能入口

Forgeloop 只暴露五个核心技能。

五个技能生成的交付文档默认跟随用户输入语言。文件路径、命令、代码标识、分支名、状态值和协议 token 保持原文，例如 `PASS`、`REPAIR_REQUIRED`、`TODO`、`CODING`。

### 1. `recommend-initiatives`

基于当前源码基线，推荐后续最值得做的 3 到 5 个 Initiative。

它会查看项目结构、文档、测试、关键源码区域和已有 Initiative 记录，然后按产品价值、工程杠杆、风险降低和执行就绪度排序。它不会开始编码，也不会为每个候选 Initiative 写 `DESIGN.md` 或完整 PLAN。

常见用法：

```text
请使用 Forgeloop 看一下当前项目源码基线，推荐接下来最值得做的 3-5 个 Initiative。
```

输出通常写入：

```text
docs/initiatives/recommendations/<date>-<topic>.md
```

### 2. `grill-initiative`

在候选 Initiative、模糊需求、重构想法、迁移计划或架构方向进入 PLAN 前，先把它拷打成 document-first 的 `DESIGN.md` 草案。

`DESIGN.md` 是唯一设计正文工作物；聊天只用于简短进度、裁决批次、blocker 和封板确认。`grill-initiative` 不会写代码、issue、`PLAN.md` 或 `LEDGER.md`。它会创建或更新：

```text
docs/initiatives/active/<initiative-code>-<initiative-slug>/DESIGN.md
```

新的 `DESIGN.md` 默认是：

```text
Status: Draft
```

Draft 中会包含 Value Question Directory Tree、稳定的 `Lxxx` Leaf ID、Focused Context Findings、Leaf Resolution Matrix、Decision Records、Scope / Non-Goals、Selected Design、Design Details、Activation Blockers、Follow-ups 和 Residual Risks。

每个 retained leaf 必须在 Leaf Resolution Matrix 中 exactly once 关闭。能通过代码、测试、配置和既有文档回答的问题先查仓库；只有产品意图、业务优先级、外部约束、不可逆 trade-off 或缺失 authority 才问用户。影响实现、验证、审查或下游规划的术语冲突必须在 `DESIGN.md` 中显式发现、裁决、阻塞或列为 open question。

没有 Activation Blockers 时，`grill-initiative` 会询问是否封板。封板只允许把 `Status: Draft` 改为 `Status: Sealed` 并更新封板元数据，不允许借机重写正文、重排章节、重编号或发明新决策。

常见用法：

```text
请使用 Forgeloop grill-initiative 拷打这个候选专项：我想把认证模块重构掉。
```

可能的 disposition 包括：

```text
Ready for sealing
Keep as draft
Split required
Defer to research
Reject
Superseded
```

### 3. `plan-initiative`

把用户选中的 Initiative 或 `DESIGN.md` 写成可执行的 `PLAN.md` 和初始 `LEDGER.md`。如果还存在阻塞设计分歧，应先使用 `grill-initiative`。

只有 `Status: Sealed` 的 `DESIGN.md` 才是 `plan-initiative` 可消费的正式设计法源。`Status: Draft`、`Status: Superseded`、缺失状态、未知状态或冲突状态都会 hard stop，必须先回到 `grill-initiative` 修补、恢复或封板。

`plan-initiative` 还会做只读 intake gate：检查 Activation Blockers、Leaf Resolution Matrix、Decision Records、Design Impact、Downstream Constraint、残留占位符和核心术语一致性。失败时不会写 `PLAN.md` / `LEDGER.md`，也不会在规划阶段修补 `DESIGN.md`。

`PLAN.md` 是 `run-initiative` 消费的执行契约。`plan-initiative` 不重新裁决 sealed `DESIGN.md` 中已经有证据和标准支撑的设计方向，而是把 Downstream Constraints、术语约束、scope、验收标准和验证方式压成可执行 Milestone。Milestone 优先按 vertical slice 组织，形成可独立审查的 Expected Inspectable State。

常见用法：

```text
请使用 Forgeloop 为这个 Initiative 写一份 PLAN.md，后续要按 Milestone 执行。
```

输出通常写入：

```text
docs/initiatives/active/<initiative-code>-<initiative-slug>/PLAN.md
docs/initiatives/active/<initiative-code>-<initiative-slug>/LEDGER.md
```

新的 Initiative 目录名应带三位数编码前缀，例如：

```text
docs/initiatives/active/001-auth-hardening/PLAN.md
docs/initiatives/active/001-auth-hardening/LEDGER.md
```

### 4. `run-initiative`

按 `PLAN.md` 执行一个 Initiative。执行过程以 Milestone 为单位，每个 Milestone 都经过 Coder 交付和 Reviewer 审查。

常见用法：

```text
请使用 Forgeloop 执行 docs/initiatives/active/<initiative-code>-<initiative-slug>/PLAN.md，一直推进到 Initiative 完成。
```

推荐执行流：

```text
读取 DESIGN.md（如有）、PLAN.md 和 LEDGER.md
确认或创建分支 codex/<initiative-code>-<initiative-slug>
定位第一个非 PASS Milestone
给 Coder 发送任务入口并要求读取 Coder 角色协议
Coder 读文档，执行 Construction Loop，实现、验证、截图或证据记录、按 Milestone 粒度 commit、push
Scheduler 更新 LEDGER.md 到 REVIEW
给 Reviewer 发送任务入口并要求读取 Reviewer 角色协议
Reviewer 从产品、测试、架构三视角审查真实 diff
REPAIR_REQUIRED 则回到 Coder 修复
PASS 则记录 verdict 并进入下一个 Milestone
全部 Milestone PASS 后跑最终验证
写 DELIVERY.md，准备 PR summary，移动到 completed/
```

### 5. `run-initiative-sequences`

串行运行 `docs/initiatives/active/` 下用户指定的连续多个 Initiative。

它是 `run-initiative` 的薄调度壳：只负责枚举 active 队列、确认用户要跑的范围、逐个调用标准 `run-initiative` 工作流，并在全部完成后输出聚合 PR summary。它不复制 Milestone、Reviewer、repair 或 DELIVERY 规则。

常见用法：

```text
请使用 Forgeloop run-initiative-sequences 跑 active 下 003 到 006 这几个专项。
```

如果用户没有指定范围，它应先反问是运行全部 active Initiative，还是运行一个指定范围。

运行连续专项序列前，建议把 Codex TOML 配置中的 subagent 线程上限调大，例如：

```toml
[agents]
max_threads = 100
```

## 运行时存储结构

Forgeloop 的插件代码和项目运行记录是分开的。

插件代码位于：

```text
plugins/forgeloop/
```

项目实例数据由技能在目标仓库中按需创建：

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

其中：

- `<initiative-code>` 是三位数编码前缀，例如 `001`；
- `DESIGN.md` 是设计裁决法源；只有 `Status: Sealed` 的 DESIGN 才能被 `plan-initiative` 正式消费；
- `PLAN.md` 是执行规划契约；
- `LEDGER.md` 是极简恢复账本；
- `evidence/` 存放可选截图、验证记录和审查证据；
- `DELIVERY.md` 是完成后的交付摘要和 PR summary 基础；
- `handoff/` 存放专项完成后的跨专项问题发现和后续机会，由 Scheduler 汇总维护；即使没有发现，也保留显式空记录；
- recommendation 文件只是推荐快照，不是执行契约。

## 安装

Forgeloop 是 repo-local Codex plugin，不是 Python 包，也不需要 npm/pnpm 安装。

### 方式一：直接使用本仓库

1. 将本仓库 clone 或下载到本地。
2. 确认仓库根目录包含：

```text
.agents/plugins/marketplace.json
plugins/forgeloop/.codex-plugin/plugin.json
plugins/forgeloop/skills/
```

3. 重启 Codex，让 Codex 重新读取 repo-local marketplace。
4. 在 Codex 的插件界面中安装 `Forgeloop Local` / `forgeloop`。

### 方式二：复制到已有项目

如果你想把 Forgeloop 作为某个项目的本地插件，可以复制以下内容到项目根目录：

```text
.agents/plugins/marketplace.json
plugins/forgeloop/
```

然后重启 Codex 并安装该 repo-local plugin。

## 目录结构

本仓库刻意保持极简，只保留插件核心和 README：

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

## 常见用法示例

### 审问一个模糊需求

```text
请使用 Forgeloop grill-initiative 拷打这个候选专项：我想把认证模块重构掉，但不确定范围。
```

适合在需求还没有边界、重构目标可能过大、或者你希望 Agent 在写 PLAN 前先产出 document-first 的 Draft DESIGN、Leaf Resolution Matrix 和证据化 Decision Records 时使用。

### 推荐后续 Initiative

```text
请使用 Forgeloop 基于当前源码基线推荐后续 3-5 个最值得做的 Initiative。
```

适合在你刚接手一个项目、完成一个版本、或者想让 Agent 帮你判断下一步优先级时使用。

### 为选中的 Initiative 写 PLAN

```text
请使用 Forgeloop plan-initiative 基于 docs/initiatives/active/001-auth-hardening/DESIGN.md 写 PLAN.md 和 LEDGER.md。这个 DESIGN.md 已经 Status: Sealed。以 Milestone 为交付单元，每个 Milestone 3-5 个 Work Items，Milestone 优先按 vertical slice 形成可审查的 Expected Inspectable State，重要能力后加验收与加固 Milestone。
```

适合在你已经有 sealed DESIGN 或清晰 Initiative，但还没有形成可执行结构时使用。若 DESIGN 仍是 Draft、有 blocker、Leaf Resolution Matrix 不闭合或核心术语冲突，`plan-initiative` 会停止并要求先回 `grill-initiative` 修补。

### 按 PLAN 执行 Initiative

```text
请使用 Forgeloop 执行 docs/initiatives/active/001-auth-hardening/PLAN.md。复用一个 Coder subagent 和一个 Reviewer subagent，不要把调度者上下文 fork 给 subagent。每个 Milestone 形成 Milestone 粒度 commit/push，Reviewer PASS 后继续下一个 Milestone。
```

适合直接进入编码交付阶段。Coder 会读取自己的角色协议并执行 Construction Loop；Scheduler 只提供任务入口和边界，不把 PLAN / DESIGN 改写成二手实现说明。

### 串行执行多个 active Initiative

```text
请使用 Forgeloop run-initiative-sequences 跑 docs/initiatives/active 下 003 到 006 的连续专项。
```

适合多个已规划 Initiative 需要按编号顺序连续推进，但仍要求每个 Initiative 独立走完 `run-initiative` 审查闭环时使用。

### 恢复中断的 Initiative

```text
请使用 Forgeloop 恢复 docs/initiatives/active/001-auth-hardening/ 的执行，从 LEDGER.md 里第一个非 PASS Milestone 继续。
```

Forgeloop 会读取 `DESIGN.md`（如有）、`PLAN.md`、`LEDGER.md`、`git status` 和最近提交，而不是依赖聊天记忆。

### 只做审查导向的修复循环

```text
请使用 Forgeloop 继续当前 Initiative。上一轮 Reviewer 给了 REPAIR_REQUIRED，只修复 blocking issues，修复后重新 review。
```

适合在 Milestone 审查未通过时继续推进。

## Subagent 使用方式

Forgeloop 不内置 custom agent TOML。Coder 和 Reviewer 由 `run-initiative` 技能中的角色协议定义；Scheduler 委派时只提供“角色协议 + 任务真值文件 + 本轮任务要求”，不把自己消化后的上下文转述成二手任务说明，也不替 Coder/Reviewer 提取或改写工作规范：

```text
plugins/forgeloop/skills/run-initiative/references/coder-protocol.md
plugins/forgeloop/skills/run-initiative/references/reviewer-protocol.md
plugins/forgeloop/skills/run-initiative/references/handoff-template.md
plugins/forgeloop/skills/run-initiative/references/handoff-index-template.md
```

任务真值文件通常是当前 Initiative 的 `DESIGN.md`、`PLAN.md`、`LEDGER.md`、相关源码 / 测试 / 设计文档、Coder 报告、真实 diff range 和证据路径。Scheduler 可以说明本轮 Milestone、范围、分支、base commit、dirty baseline 和停止条件，但 Coder / Reviewer 必须自己读取协议和真值文件后执行或裁决。

Coder 的角色协议要求它先建立 repository orientation 和 behavior intent，选择 public seam，按行为薄切片施工，控制契约和真理源 delta，检查 completeness / edge / re-entry，按验证证据阶梯报告结果，并在提交前完成 self-diff hygiene。Reviewer 的角色协议仍然负责正式三视角裁决，Coder 自检不能替代 Reviewer `PASS`。

在支持 subagent 的 Codex 环境中，推荐使用通用 subagent：

- Coder：`default` 或 `worker`，高 reasoning effort；
- Reviewer：`default`，高 reasoning effort；
- `fork_context=false`；
- 每个 Initiative 尽量复用同一个 Coder 和同一个 Reviewer；
- `task_name` 优先使用三位数编码，例如 `001-auth-hardening` 对应 `coder_001` 和 `reviewer_001`；旧的无编码 Initiative 才退回到 snake-normalized 名称。

运行 `run-initiative-sequences` 这类连续专项序列时，会按 Initiative 创建新的 Coder / Reviewer 组合；如果 Codex TOML 的 `[agents].max_threads` 太低，长序列可能被线程上限卡住。建议提前调到 `100`。

如果当前环境没有 subagent 工具，Scheduler 可以在用户允许的情况下继续执行，但必须把 review provenance 明确记录为 `explicit solo best-effort`。这种路径只能作为降级执行证据，不得伪称为正式独立 Reviewer 放行；完成归档必须清楚记录 reduced review provenance。

## 适合与不适合的场景

适合：

- 需要持续推进的新功能或产品能力；
- 架构改造、模块拆分、依赖迁移；
- API、Schema、权限、数据模型或插件协议治理；
- 测试真实性、稳定性、性能和可观测性加固；
- 构建、发布、CI、开发者体验改造；
- 文档、示例、SDK、集成体验完善；
- 已有需求，需要压成 PLAN 并持续交付的工程工作。

不适合：

- 一次性脚本；
- 极小 bug 修复；
- 不需要计划、不需要审查的临时实验；
- 候选专项还没有边界，且用户也不希望先用 `grill-initiative` 做前置设计裁决的问题；
- 需要严格组织级合规流程但不允许 Agent 参与审查的项目。

## 设计原则

Forgeloop 遵循几个原则：

1. Codex 原生：围绕 Codex plugin、skill、subagent 和 Git 工作流设计。
2. 入口少：只保留 `recommend-initiatives`、`grill-initiative`、`plan-initiative`、`run-initiative`、`run-initiative-sequences`。
3. 交付单元清楚：用户入口是 Initiative，执行推进靠 Milestone。
4. 设计法源明确：只有 sealed `DESIGN.md` 才能进入规划，Draft 不能被 `plan-initiative` 消费。
5. 施工内循环强：Coder 在提交前完成行为、seam、契约、真理源、边界、验证和 diff hygiene 自检。
6. 审查协议强：Reviewer 的三视角裁决比形式化状态更重要，Coder 自检不能替代 Reviewer 放行。
7. 状态极简：恢复只依赖 `DESIGN.md`、`PLAN.md`、`LEDGER.md`、Git 和必要 evidence。
8. Git 不冒充验收：commit / push 只是证据和恢复点；Reviewer `PASS` 前的 push 只是 review candidate，不是放行。
9. 长期可控：通过职责分离、任务入口、角色协议和 Reviewer 放行控制质量、上下文和 Token 成本。

## 许可证

MIT. See [LICENSE](LICENSE).
