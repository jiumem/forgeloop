# Total Task Doc 参考模板

## 文档定位

- 阶段：`Total Task Doc`
- 平面：planning 正式成果文档
- 主要读者：`planner`、`plan_reviewer`、下游 runtime `coder` / reviewers，以及后续 admission 或 control 角色通过 sealed 引用读取
- 主要目的：把上游已经 sealed 的 planning 决策压缩成一张轻薄、强索引、可直接执行的执行地图，而不是重新打开设计裁决

这份文档不是第二篇设计长文，不是迁移账本，不是 reviewer verdict，也不是实现教程。

## 这份文档必须回答什么

- 这张执行地图继承了哪些已经 sealed 的上游 planning artifact 与决策
- Initiative 的边界与成功标准是什么
- Initiative 如何被切成 Milestone、Task 与集成路径
- 每个 Task 属于哪个 Milestone，依赖关系和验收标准分别是什么
- 分支与 PR 应如何收敛，而不是反过来替代对象切法
- 下游角色应从哪里寻找验收与证据入口
- sealed 之后哪些 residual risk 可以保留，哪些 follow-up 被有意延后

## 必需结构

只能使用下列一级和二级标题。二级标题才是下游 `coder` 与 `reviewer` 阅读时真正稳定的合同。除非 workflow 明确要求临时例外，否则不要另外发明一套平行结构。

默认保留所有二级标题。如果某节确实不适用，也要保留标题，并用一句简短理由标记为 `N/A`，不要直接删掉。

```markdown
# <Initiative Name> 总任务文档（Total Task Doc）

## 1. 前置输入与决策基线（Input Baseline And Sealed Decisions）
### 1.1 需求摘要（Requirement Summary）
### 1.2 设计引用（Design Refs）
### 1.3 差距分析引用（Gap Analysis Refs, if applicable）
### 1.4 已封板决策（Sealed Decisions）
### 1.5 执行边界（Execution Boundary）
### 1.6 Initiative 法定引用指派（Initiative Reference Assignment）

## 2. Initiative 总览（Initiative）
### 2.1 背景（Background）
### 2.2 范围（Scope）
### 2.3 非目标（Non-Goals）
### 2.4 成功标准（Success Criteria）

## 3. Milestone 总表（Milestone Master Table）
### 3.1 Milestone 列表（Milestone List）
### 3.2 Milestone 依赖（Milestone Dependencies）
### 3.3 Milestone 验收（Milestone Acceptance）
### 3.4 Milestone 法定引用指派（Milestone Reference Assignment）

## 4. Task 账本（Task Ledger）
### 4.1 Task 列表（Task List）
### 4.2 Task 定义（Task Definitions）

## 5. 分支与 PR 集成路径（Branch & PR Integration Path）
### 5.1 默认集成模型（Default Integration Model）
### 5.2 分支计划（Branch Plan）
### 5.3 PR 计划（PR Plan）
### 5.4 PR 依赖顺序（PR Dependency Order）

## 6. 验收矩阵（Acceptance Matrix）
### 6.1 Task 验收索引（Task Acceptance Index）
### 6.2 Milestone 验收索引（Milestone Acceptance Index）
### 6.3 Initiative 验收索引（Initiative Acceptance Index）
### 6.4 证据入口（Evidence Entrypoints）

## 7. 全局残余风险与后续事项（Global Residual Risks & Follow-Ups）
### 7.1 全局残余风险（Global Residual Risks）
### 7.2 后续事项（Follow-Ups）
```

## 分节合同

### 1. 前置输入与决策基线（Input Baseline And Sealed Decisions）

- `1.1 需求摘要（Requirement Summary）`：说明这张执行地图所满足的最小需求摘要
- `1.2 设计引用（Design Refs）`：指向这份文档继承的 sealed `Design Doc` 或权威设计区块
- `1.3 差距分析引用（Gap Analysis Refs, if applicable）`：当 sealed `Design Doc` 写明 `Gap Analysis Requirement: required` 时，指向 sealed `Gap Analysis Doc`；否则标记为 `N/A`
- `1.4 已封板决策（Sealed Decisions）`：只概括那些已经 sealed、并且实质影响执行地图的上游决策
- `1.5 执行边界（Execution Boundary）`：这是说明当前 `Total Task Doc` 承载什么、不承载什么的唯一权威区块
- `1.6 Initiative 法定引用指派（Initiative Reference Assignment）`：这是下游使用的 Initiative 层法定参考入口的唯一权威区块
- 这一节要证明执行地图继承的是 sealed 上游真值，而不是本地临时即兴推导

### 2. Initiative 总览（Initiative）

- `2.1 背景（Background）`：只写执行所需的最小项目背景
- `2.2 范围（Scope）`：定义 Initiative 层面的执行边界
- `2.3 非目标（Non-Goals）`：定义这个 Initiative 以后不得悄悄吞进来的内容
- `2.4 成功标准（Success Criteria）`：定义 Initiative 层面的成功与交付标准
- 本节保持轻薄；不要在这里重述设计长文

### 3. Milestone 总表（Milestone Master Table）

- `3.1 Milestone 列表（Milestone List）`：列出整个 Initiative 的全部 Milestone，而不是只写当前 frontier
- `3.2 Milestone 依赖（Milestone Dependencies）`：定义 Milestone 之间的串行、并行与收敛关系
- `3.3 Milestone 验收（Milestone Acceptance）`：定义每个 Milestone 的验收线
- `3.4 Milestone 法定引用指派（Milestone Reference Assignment）`：这是每个 Milestone 法定参考入口的唯一权威区块
- `Milestone List` 中的 `Planned PR Model` 默认应为 `Single PR`；只有当某个 Milestone 必须保持为单一状态边界、且无法合理切成新 Milestone 时，才使用 `多 PR 例外（Multi-PR Exception）`

### 4. Task 账本（Task Ledger）

- `4.1 Task 列表（Task List）`：列出所有 Task，并写出稳定的 `Task Key`、所属 Milestone、摘要与依赖
- `4.2 Task 定义（Task Definitions）`：这是 Task 层字段定义的唯一权威区块
- `4.1` 与 `4.2` 必须通过 `Task Key` 一一对应：每个 Task 行都必须有且只有一个匹配定义，`4.2` 中也不得出现孤儿 Task 区块
- 每个 Task 定义至少必须包含：
  - `任务键（Task Key）`
  - `设计引用（Design Refs）`
  - `差距引用（Gap Refs）`
  - `规范引用（Spec Refs）`
  - `输入（Input）`
  - `动作（Action）`
  - `输出（Output）`
  - `非目标（Non-Goals）`
  - `依赖（Dependencies）`
  - `验收（Acceptance）`
  - `Task 局部风险 / 备注（Task-local Risks / Notes）`
- `Refs` 是必填字段，不是装饰
- `Action` 应说明“改什么”，而不是把实现步骤按行教程式展开
- 下游 `coder` 不应该为了重建基本 Task 边界而被迫重新通读整份文档

### 5. 分支与 PR 集成路径（Branch & PR Integration Path）

- `5.1 默认集成模型（Default Integration Model）`：这是默认 `one Milestone -> one PR` 规则及其 `Multi-PR Exception` 的唯一权威区块
- `5.2 分支计划（Branch Plan）`：以 planning 层粒度定义计划中的分支模型与命名方式
- `5.3 PR 计划（PR Plan）`：定义计划中的 PR 对象、覆盖范围与验收清单
- `5.4 PR 依赖顺序（PR Dependency Order）`：定义 PR 之间的串行、并行与收敛顺序
- 分支与 PR 规划必须服务于 Milestone 与 Task 的切法，而不能反过来取代它们

### 6. 验收矩阵（Acceptance Matrix）

- `6.1 Task 验收索引（Task Acceptance Index）`：索引 Task 验收及其通常的首个证据入口，但不要重新定义 Task 验收；`4.2 Task 定义（Task Definitions）` 仍是权威来源
- `6.2 Milestone 验收索引（Milestone Acceptance Index）`：索引 Milestone 验收及其通常的首个证据入口，但不要重新定义 Milestone 验收；`3.3 Milestone 验收（Milestone Acceptance）` 仍是权威来源
- `6.3 Initiative 验收索引（Initiative Acceptance Index）`：索引 Initiative 验收及其通常的首个证据入口，但不要重新定义 Initiative 成功标准；`2.4 成功标准（Success Criteria）` 仍是权威来源
- `6.4 证据入口（Evidence Entrypoints）`：这是下游验证与审查应当优先查看哪些证据入口的唯一权威区块
- 这个矩阵是控制面索引，不是散文式复述

### 7. 全局残余风险与后续事项（Global Residual Risks & Follow-Ups）

- `7.1 全局残余风险（Global Residual Risks）`：只记录那些已知、可解释、可追踪、并且在 sealed 后法律上允许保留的 residual risk
- `7.2 后续事项（Follow-Ups）`：记录在不阻塞当前执行地图的前提下，被有意延后的后续工作
- 不要在这里隐藏未解决的设计或 gap 决策

## 写作规则

- 为下游 `coder` 与 `reviewer` 的可执行性而写，不为取悦人类读者而写
- 使用固定字段、强索引、弱叙事
- 在保持轻薄的同时，不能薄到让 `plan_reviewer` 无法在本层单独判断执行地图
- 先建立静态执行对象：`Initiative -> Milestone -> Task`；然后再定义依赖与 PR 集成结构
- 如果多切一个 Milestone 能形成更干净的状态边界，应优先多 Milestone，而不是多 PR
- 每条边界、验收规则与法定引用指派都只保留一个真理源；如果另一个区块才是权威来源，就明确引用，不要在别处重新裁决
- 验收真理必须保持单一来源：`2.4 成功标准（Success Criteria）` 管 Initiative 成功，`3.3 Milestone 验收（Milestone Acceptance）` 管 Milestone 验收，`4.2 Task 定义（Task Definitions）` 管 Task 验收；`6` 只能索引这些区块并指向证据
- 把 `1.5 执行边界（Execution Boundary）`、`1.6 Initiative 法定引用指派（Initiative Reference Assignment）`、`3.4 Milestone 法定引用指派（Milestone Reference Assignment）`、`4.2 Task 定义（Task Definitions）`、`5.1 默认集成模型（Default Integration Model）` 与 `6.4 证据入口（Evidence Entrypoints）` 视为本文档的结构核心，不能退化成模糊散文
- 所谓 full refinement，意味着所有对象、依赖、验收线与集成路径都已经明确，而不是堆一堆教程式实现细节
- 任何未决裁决都不得进入 `Total Task Doc`

## 禁止内容

不要把以下内容写进 `Total Task Doc`：

- 被重新打开的设计争论
- 当前态迁移分析
- 未决问题或 TODO 式裁决占位
- 实现教程细节
- reviewer verdict 原文
- runtime 进度日志
- 用 PR 或分支结构掩盖过厚 Milestone 的写法
- 实际上属于 blocker 级未决问题、却伪装成 residual risk 的表述

这些内容应分别放在 `Design Doc`、`Gap Analysis Doc`、planning rolling doc、runtime control docs，或更上层裁决里。

## Review-Ready 标准

只有满足以下条件，这份文档才算 review-ready：

- 所有要求的二级标题都存在，或者以有效理由明确标记为 `N/A`
- 上游 planning 引用明确
- `1.3 差距分析引用（Gap Analysis Refs）` 与 sealed `Design Doc` 中的 `Gap Analysis Requirement` 保持一致
- `1.5 执行边界（Execution Boundary）` 明确
- Initiative 成功标准明确
- 完整的 Milestone 结构与依赖明确
- Initiative 与 Milestone 的法定引用指派明确
- Task 账本 fully expanded，`4.1` 中的每个 `Task Key` 在 `4.2` 中都恰好有一个匹配定义，且不存在孤儿 Task 定义
- 默认集成模型及任何 `Multi-PR Exception` 的使用都明确
- 验收矩阵与 `6.4` 中的权威证据入口明确
- `6` 不得重新定义已经由 `2.4`、`3.3` 与 `4.2` 拥有的验收线
- 没有把未解决的设计或 gap 问题藏到下游去

## Seal 标准

只有满足以下条件，这份文档才可以 sealed：

- review-ready 条件已经满足
- `plan_reviewer` 能在不重建隐藏意图的前提下完成判断
- 下游 `coder` 能据此行动，而无需重新打开上游设计裁决
- runtime reviewers 能直接从文档中定位法定引用、对象边界、验收线与证据入口
- 这份文档仍然是一张轻薄的执行控制面地图，而不是一篇影子设计长文
- 如果还有未解决问题，它们也必须是真正的 residual，而不是 blocker
