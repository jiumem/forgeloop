# Design Doc 参考模板

<!-- forgeloop:anchor document-position -->
## 文档定位

- 阶段：`Design Doc`
- 平面：planning 正式成果文档
- 主要读者：`planner`、`design_reviewer`、下游 `gap_reviewer` 或 `total_task_doc_reviewer`，以及后续通过 sealed 引用进入 runtime 的 `coder` / reviewers
- 主要目的：为当前 Initiative 定义目标态、范围边界与关键结构裁决

这份文档不是迁移账本，不是任务计划，也不是实现教程。
文档是否进入评审、修复、或 sealed lifecycle，以 rolling doc 为准。

<!-- forgeloop:anchor questions-this-doc-must-answer -->
## 这份文档必须回答什么

- 为什么要做这个 Initiative
- 系统应当达到什么目标态
- 哪些内容在范围内，哪些内容明确不在范围内
- 在进入 `Total Task Doc` 之前，是否形式上必须先有 `Gap Analysis Doc`
- 哪些设计裁决已经 sealed
- 下游角色必须守住哪些正确性边界

<!-- forgeloop:anchor required-structure -->
## 必需结构

只能使用下列一级和二级标题。二级标题才是下游 `coder` 与 `reviewer` 阅读时真正稳定的合同。除非 workflow 明确要求临时例外，否则不要另外发明一套平行结构。

默认保留所有二级标题。如果某节确实不适用，也要保留标题，并用一句简短理由标记为 `N/A`，不要直接删掉。

```markdown
# <Initiative / Topic Name> 设计文档（Design Doc）

<!-- forgeloop:anchor document-card -->
## 1. 文档卡片（Document Card）
<!-- forgeloop:anchor document-card/status-and-stage -->
### 1.1 状态与阶段（Status And Stage）
<!-- forgeloop:anchor document-card/initiative-type -->
### 1.2 Initiative 类型（Initiative Type）
<!-- forgeloop:anchor document-card/primary-readers -->
### 1.3 主要读者（Primary Readers）
<!-- forgeloop:anchor document-card/gap-analysis-requirement -->
### 1.4 Gap Analysis Requirement

<!-- forgeloop:anchor requirement-baseline -->
## 2. 需求基线（Requirement Baseline）
<!-- forgeloop:anchor requirement-baseline/problem-statement -->
### 2.1 问题陈述（Problem Statement）
<!-- forgeloop:anchor requirement-baseline/intended-outcome -->
### 2.2 目标结果（Intended Outcome）
<!-- forgeloop:anchor requirement-baseline/success-criteria -->
### 2.3 成功标准（Success Criteria）
<!-- forgeloop:anchor requirement-baseline/hard-constraints -->
### 2.4 硬约束（Hard Constraints）

<!-- forgeloop:anchor design-verdict-summary -->
## 3. 设计裁决摘要（Design Verdict Summary）
<!-- forgeloop:anchor design-verdict-summary/primary-contradiction -->
### 3.1 主要矛盾（Primary Contradiction）
<!-- forgeloop:anchor design-verdict-summary/winning-cut -->
### 3.2 胜出切法（Winning Cut）
<!-- forgeloop:anchor design-verdict-summary/downstream-binding-effects -->
### 3.3 下游绑定影响（Downstream Binding Effects）

<!-- forgeloop:anchor scope-and-non-goals -->
## 4. 范围与非目标（Scope And Non-Goals）
<!-- forgeloop:anchor scope-and-non-goals/in-scope -->
### 4.1 范围内（In Scope）
<!-- forgeloop:anchor scope-and-non-goals/out-of-scope -->
### 4.2 范围外（Out Of Scope）
<!-- forgeloop:anchor scope-and-non-goals/explicit-non-goals -->
### 4.3 明确非目标（Explicit Non-Goals）

<!-- forgeloop:anchor target-state-design -->
## 5. 目标态设计（Target-State Design）
<!-- forgeloop:anchor target-state-design/core-topology -->
### 5.1 核心拓扑（Core Topology）
<!-- forgeloop:anchor target-state-design/key-surfaces -->
### 5.2 关键表面（Key Surfaces）
<!-- forgeloop:anchor target-state-design/critical-paths-and-transitions -->
### 5.3 关键路径与转换（Critical Paths And Transitions）
<!-- forgeloop:anchor target-state-design/boundary-allocation-and-implementation-freedom -->
### 5.4 边界划分与实现自由度（Boundary Allocation And Implementation Freedom）

<!-- forgeloop:anchor key-decisions-and-rejected-alternatives -->
## 6. 关键决策与被否定方案（Key Decisions And Rejected Alternatives）
<!-- forgeloop:anchor key-decisions-and-rejected-alternatives/sealed-decisions -->
### 6.1 已封板决策（Sealed Decisions）
<!-- forgeloop:anchor key-decisions-and-rejected-alternatives/rejected-alternatives -->
### 6.2 被否定方案（Rejected Alternatives）
<!-- forgeloop:anchor key-decisions-and-rejected-alternatives/why-the-winning-cut-wins -->
### 6.3 为什么胜出切法会赢（Why The Winning Cut Wins）

<!-- forgeloop:anchor correctness-surface -->
## 7. 正确性表面（Correctness Surface）
<!-- forgeloop:anchor correctness-surface/invariants -->
### 7.1 不变量（Invariants）
<!-- forgeloop:anchor correctness-surface/contract-boundaries -->
### 7.2 契约边界（Contract Boundaries）
<!-- forgeloop:anchor correctness-surface/failure-and-safety-lines -->
### 7.3 失败与安全红线（Failure And Safety Lines）
<!-- forgeloop:anchor correctness-surface/allowed-implementation-variation -->
### 7.4 允许的实现变体（Allowed Implementation Variation）

<!-- forgeloop:anchor residual-risks-and-follow-ups -->
## 8. 残余风险与后续事项（Residual Risks And Follow-Ups）
<!-- forgeloop:anchor residual-risks-and-follow-ups/accepted-residual-risks -->
### 8.1 可接受残余风险（Accepted Residual Risks）
<!-- forgeloop:anchor residual-risks-and-follow-ups/follow-ups -->
### 8.2 后续事项（Follow-Ups）
<!-- forgeloop:anchor residual-risks-and-follow-ups/escalation-triggers -->
### 8.3 升级触发器（Escalation Triggers）
```

<!-- forgeloop:anchor text-anchor-requirement -->
## 稳定锚点要求（Text Anchor Requirement）

下游读取不得依赖标题文本、行号或目录结构。本文所有一级标题，以及所有会被下游直接引用的二级标题，都必须使用固定语义 selector 的文本锚点。

- 所有一级标题，以及所有会被下游直接引用的二级标题，必须带稳定文本锚点。
- 若某个权威区块内部承载多个法定对象，该对象自己的 block 也必须带 object-local 锚点。
- selector 命名、合法字符集与完整规则遵循 `plugins/forgeloop/skills/references/anchor-addressing.md`。
- 锚点属于正式合同，不是排版装饰。

<!-- forgeloop:anchor section-contracts -->
## 分节合同

> 本文凡标注为“唯一权威区块”的小节，其他小节只能引用，不得重裁决；若需概括，只能做索引，不得改写边界。

<!-- forgeloop:anchor document-card -->
### 1. 文档卡片（Document Card）

- `1.1 状态与阶段（Status And Stage）`：标明当前文档状态，例如 `draft`、`review-ready` 或 `sealed`，并确认当前阶段。这是文档自身的正式状态标记。`round`、`handoff` 与 `review history` 仍以控制状态文档和 rolling doc 为准；若两者不一致，`Supervisor` 必须先修正文档状态，不能让下游自行推断。
- `1.2 Initiative 类型（Initiative Type）`：只写 Initiative 类型；当 Initiative 类型会实质影响下游 planning 时，明确写出其类型，例如 greenfield feature、refactor、migration、replacement、governance convergence
- `1.3 主要读者（Primary Readers）`：当这有助于避免误用时，写明当前主要读者
- `1.4 Gap Analysis Requirement`：必须明确写 `required | not_required`；这是 planning 是否必须进入 `Gap Analysis Doc` 的唯一正式路由信号

<!-- forgeloop:anchor requirement-baseline -->
### 2. 需求基线（Requirement Baseline）

- `2.1 问题陈述（Problem Statement）`：用最小必要信息说明当前问题或压力
- `2.2 目标结果（Intended Outcome）`：说明这个 Initiative 期望达成的结果
- `2.3 成功标准（Success Criteria）`：说明设计必须满足的成功标准；这样下游 `coder` 与 `reviewer` 会有明确判断目标，而不是被迫自行猜测
- `2.4 硬约束（Hard Constraints）`：说明设计不得违反的约束
- 本节保持简短；它不是背景长文

<!-- forgeloop:anchor design-verdict-summary -->
### 3. 设计裁决摘要（Design Verdict Summary）

- `3.1 主要矛盾（Primary Contradiction）`：指出这份设计要解决的主要矛盾
- `3.2 胜出切法（Winning Cut）`：用压缩形式写出选定的设计切法
- `3.3 下游绑定影响（Downstream Binding Effects）`：概括从现在开始对下游 planning 与 coding 生效的绑定项，不重复裁决实现自由度。
- 要让下游 `coder` 或 `design_reviewer` 在不读完整篇文档的情况下，也能理解目标态
- 优先使用少量明确的裁决要点或短段落，而不是长篇铺陈

<!-- forgeloop:anchor scope-and-non-goals -->
### 4. 范围与非目标（Scope And Non-Goals）

- `4.1 范围内（In Scope）`：说明这个 Initiative 会改什么
- `4.2 范围外（Out Of Scope）`：说明它不覆盖什么
- `4.3 明确非目标（Explicit Non-Goals）`：说明哪些内容以后不得被悄悄吸进这个 Initiative
- 边界必须写得足够清楚，避免下游 planning 悄悄扩边

<!-- forgeloop:anchor target-state-design -->
### 5. 目标态设计（Target-State Design）

- `5.1 核心拓扑（Core Topology）`：定义目标态的主要对象、职责切法与结构布局
- `5.2 关键表面（Key Surfaces）`：定义下游角色必须理解的重要行为、状态与契约表面
- `5.3 关键路径与转换（Critical Paths And Transitions）`：定义让这份设计成立的关键流转、转换或路径
- `5.4 边界划分与实现自由度（Boundary Allocation And Implementation Freedom）`：这是设计层面对“哪些已固定、哪些仍可由 coder 自主决定”的唯一权威区块
- 聚焦于下游角色必须守住的结构
- 内容应围绕 Initiative 的主要矛盾与胜出切法来组织
- 只写足以消除执行或审查歧义的最小必要文字

<!-- forgeloop:anchor key-decisions-and-rejected-alternatives -->
### 6. 关键决策与被否定方案（Key Decisions And Rejected Alternatives）

- `6.1 已封板决策（Sealed Decisions）`：记录已封板决策；涉及实现自由度时直接引用 `5.4`，不再复述
- `6.2 被否定方案（Rejected Alternatives）`：只记录那些下游角色可能会重新打开的现实备选方案
- `6.3 为什么胜出切法会赢（Why The Winning Cut Wins）`：解释为什么当前切法是在当前主要矛盾下最好的结构选择
- 不要保留前期讨论历史或纯风格偏好争论

<!-- forgeloop:anchor correctness-surface -->
### 7. 正确性表面（Correctness Surface）

- `7.1 不变量（Invariants）`：说明实现后必须持续成立的内容
- `7.2 契约边界（Contract Boundaries）`：说明下游角色必须守住哪些边界
- `7.3 失败与安全红线（Failure And Safety Lines）`：说明哪些失败、安全线或红线绝不能被越过
- `7.4 允许的实现变体（Allowed Implementation Variation）`：概括不违反设计的实现变化范围。
- 必须让人一眼看出什么叫“实现正确”，以及什么叫“实现不同但仍合法”

<!-- forgeloop:anchor residual-risks-and-follow-ups -->
### 8. 残余风险与后续事项（Residual Risks And Follow-Ups）

- `8.1 可接受残余风险（Accepted Residual Risks）`：只记录 sealed 后在本层允许保留的风险
- `8.2 后续事项（Follow-Ups）`：记录不会阻塞当前设计 seal 的后续工作
- `8.3 升级触发器（Escalation Triggers）`：说明未来哪些发现必须触发回到设计层，而不是让下游悄悄打补丁
- 不要在这里隐藏阻塞性的设计不确定性
- 不要把未决问题偷运进本节

<!-- forgeloop:anchor writing-rules -->
## 写作规则

- 为下游 `coder` 与 `reviewer` 的理解而写，不为取悦人类读者而写
- 优化目标是边界清晰、结构判断明确、歧义低
- 在可能时保持文档轻薄，但不能薄到让 `design_reviewer` 无法在本层单独完成判断
- 优先写清明确的设计裁决，而不是长篇叙事铺垫
- 每个决策只保留一个真理源；如果另一个文档才是权威来源，就明确引用，不要松散重复
- 把 `5.4 边界划分与实现自由度（Boundary Allocation And Implementation Freedom）` 视为下游实现哪些能决定、哪些不能决定的唯一权威区块
- `3. 设计裁决摘要（Design Verdict Summary）`、`5. 目标态设计（Target-State Design）` 和 `7. 正确性表面（Correctness Surface）` 是本文件的结构核心，不能退化成占位废话

<!-- forgeloop:anchor prohibited-content -->
## 禁止内容

不要把以下内容写进 `Design Doc`：

- 当前态迁移账本
- rollout 时序
- PR 路径设计
- Milestone 或 Task 拆分
- 实现教程细节
- reviewer verdict 原文
- 把未决问题伪装成已经 sealed 的裁决

这些内容应分别放在 `Gap Analysis Doc`、`Total Task Doc`、planning rolling doc，或更上层裁决里。

<!-- forgeloop:anchor review-ready-standard -->
## Review-Ready 标准

只有满足以下条件，这份文档才算 review-ready：

- 所有要求的二级标题都存在，或者以有效理由明确标记为 `N/A`
- 目标态明确
- 成功标准明确
- 范围边界明确
- `1.4 Gap Analysis Requirement` 明确
- 主要设计裁决明确
- `5.4` 中关于“固定与可变”的权威界线明确
- 正确性表面明确
- 没有把阻塞性设计不确定性藏到下游去
- 文档顶部 `状态` 已明确写为 `review-ready`
- `review-ready` 只表示文档已满足 handoff 条件。正式 reviewer dispatch 仅在同 round 最新 `planner_update.next_action=request_reviewer_handoff` 且存在匹配的当前 handoff block 时成立。

<!-- forgeloop:anchor seal-standard -->
## Seal 标准

只有满足以下条件，这份文档才可以 sealed：

- review-ready 条件已经满足
- 文档顶部 `状态` 已明确写为 `sealed`
- `design_reviewer` 能在不重建隐藏意图的前提下完成判断
- 下游 planning 能把它当作权威来源引用
- 下游 planning 能仅凭这份文档判断，在 `Total Task Doc` 之前是否必须先有 `Gap Analysis Doc`
- `coder` 与下游 reviewers 能仅凭这份文档判断，哪些部分对设计有绑定力，哪些部分仍属于实现自由度
- 如果还有未解决问题，它们也必须是真正的 residual，而不是 blocker
