# Gap Analysis Doc 参考模板

## 文档定位

- 阶段：`Gap Analysis Doc`
- 平面：planning 正式成果文档
- 主要读者：`planner`、`gap_reviewer`、下游 `plan_reviewer`，以及后续通过 sealed 引用进入 runtime 的 `coder` / reviewers
- 主要目的：定义当前态与目标态之间真实存在的差距，以及下游 planning 必须遵守的收敛切法

这份文档不是第二篇设计长文，不是任务计划，也不是实现教程。

## 这份文档必须回答什么

- 为什么这个 Initiative 需要 gap analysis
- 相关当前态实际上是什么
- 当前态与目标态之间有哪些有绑定力的差距
- 哪种收敛切法会胜出
- 哪些差距必须在 `Total Task Doc` 之前被解决
- 下游角色必须守住哪些迁移、兼容与回滚边界

## 必需结构

只能使用下列一级和二级标题。二级标题才是下游 `coder` 与 `reviewer` 阅读时真正稳定的合同。除非 workflow 明确要求临时例外，否则不要另外发明一套平行结构。

默认保留所有二级标题。如果某节确实不适用，也要保留标题，并用一句简短理由标记为 `N/A`，不要直接删掉。

```markdown
# <Initiative / Topic Name> 差距分析文档（Gap Analysis Doc）

## 1. 文档卡片（Document Card）
### 1.1 状态与阶段（Status And Stage）
### 1.2 为什么需要 Gap Analysis（Why Gap Analysis Exists）
### 1.3 主要读者（Primary Readers）

## 2. 基线与范围（Baseline And Scope）
### 2.1 目标态引用（Target-State Reference）
### 2.2 纳入范围的目标态切片（Target-State Slice In Scope）
### 2.3 当前态覆盖范围（Current-State Coverage）
### 2.4 差距闭合目标（Gap-Closure Goal）
### 2.5 硬约束（Hard Constraints）

## 3. 差距裁决摘要（Gap Verdict Summary）
### 3.1 当前态裁决（Current-State Verdict）
### 3.2 主要差距（Primary Gaps）
### 3.3 胜出收敛切法（Winning Convergence Cut）

## 4. 当前态快照（Current-State Snapshot）
### 4.1 现有拓扑（Existing Topology）
### 4.2 现有关键表面（Existing Critical Surfaces）
### 4.3 现有约束与历史包袱（Existing Constraints And Legacy Burdens）
### 4.4 证据边界与未知项（Evidence Boundary And Unknowns）

## 5. 差距账本（Gap Ledger）
### 5.1 边界与职责差距（Boundary And Ownership Gaps）
### 5.2 状态与契约差距（State And Contract Gaps）
### 5.3 兼容与迁移差距（Compatibility And Migration Gaps）
### 5.4 不得泄漏到下游的阻塞差距（Blocking Gaps That Must Not Leak Downstream）

## 6. 收敛策略（Convergence Strategy）
### 6.1 桥接形态（Bridge Shape）
### 6.2 切换与共存规则（Cutover And Coexistence Rules）
### 6.3 回滚与安全红线（Rollback And Safety Lines）
### 6.4 下游绑定影响（Downstream Binding Effects）

## 7. 正确性表面（Correctness Surface）
### 7.1 迁移不变量（Migration Invariants）
### 7.2 数据与兼容红线（Data And Compatibility Red Lines）
### 7.3 允许的实现变体（Allowed Implementation Variation）
### 7.4 回流触发器（Reroute Triggers）

## 8. 残余风险与后续事项（Residual Risks And Follow-Ups）
### 8.1 可接受残余风险（Accepted Residual Risks）
### 8.2 延后清理项（Deferred Cleanups）
```

## 分节合同

### 1. 文档卡片（Document Card）

- `1.1 状态与阶段（Status And Stage）`：标明当前文档状态，例如 `draft`、`review-ready` 或 `sealed`，并确认这是 `Gap Analysis Doc` 阶段
- `1.2 为什么需要 Gap Analysis（Why Gap Analysis Exists）`：说明触发 gap analysis 的原因，例如 migration、replacement、refactor 或 governance convergence
- `1.3 主要读者（Primary Readers）`：当这有助于避免误用时，写明当前主要读者

### 2. 基线与范围（Baseline And Scope）

- `2.1 目标态引用（Target-State Reference）`：指向要桥接到的 sealed `Design Doc` 或权威设计区块
- 被引用的 sealed `Design Doc` 必须显式写明 `Gap Analysis Requirement: required`；如果它写的是 `not_required`，这个阶段就是非法的，不应继续
- `2.2 纳入范围的目标态切片（Target-State Slice In Scope）`：概括与本次 gap analysis 相关的目标态切片，让下游读者无需先重建整份设计文档就能判断差距
- `2.3 当前态覆盖范围（Current-State Coverage）`：说明当前系统中哪些部分真正处于分析范围内
- `2.4 差距闭合目标（Gap-Closure Goal）`：说明在安全撰写 `Total Task Doc` 之前，必须先让哪些条件成立
- `2.5 硬约束（Hard Constraints）`：说明收敛过程中不得违反的约束

### 3. 差距裁决摘要（Gap Verdict Summary）

- `3.1 当前态裁决（Current-State Verdict）`：说明对当前态所能做出的最小可靠判断
- `3.2 主要差距（Primary Gaps）`：概括哪些差距对下游 planning 最关键
- `3.3 胜出收敛切法（Winning Convergence Cut）`：用压缩形式写出收敛策略
- 必须让下游 `coder` 或 `gap_reviewer` 在不读完整篇文档的情况下，也能理解收敛图景

### 4. 当前态快照（Current-State Snapshot）

- `4.1 现有拓扑（Existing Topology）`：定义相关的当前对象布局、职责切法与系统形态
- `4.2 现有关键表面（Existing Critical Surfaces）`：定义造成真实迁移压力的行为、状态与契约表面
- `4.3 现有约束与历史包袱（Existing Constraints And Legacy Burdens）`：定义下游 planning 必须尊重的真实约束或遗留力量
- `4.4 证据边界与未知项（Evidence Boundary And Unknowns）`：明确区分已验证的当前态事实、合理推断，以及仍未知的区域，好让 `gap_reviewer` 判断这份 gap ledger 是 grounded 还是 speculative
- 本节保持事实性和边界性；不要重讲产品历史

### 5. 差距账本（Gap Ledger）

- `5.1 边界与职责差距（Boundary And Ownership Gaps）`：识别边界与职责归属的错位
- `5.2 状态与契约差距（State And Contract Gaps）`：识别状态模型、数据形状与契约的不匹配
- `5.3 兼容与迁移差距（Compatibility And Migration Gaps）`：识别共存、兼容与转换上的差距
- `5.4 不得泄漏到下游的阻塞差距（Blocking Gaps That Must Not Leak Downstream）`：这是在 `Total Task Doc` 之前必须先关闭或被显式处理的差距的唯一权威区块

### 6. 收敛策略（Convergence Strategy）

- `6.1 桥接形态（Bridge Shape）`：从结构层定义当前态到目标态的桥接形态
- `6.2 切换与共存规则（Cutover And Coexistence Rules）`：这是旧路径与新路径如何共存、切换或退役的唯一权威区块
- `6.3 回滚与安全红线（Rollback And Safety Lines）`：定义下游实现必须守住的回滚预期与安全线
- `6.4 下游绑定影响（Downstream Binding Effects）`：概括哪些内容从现在开始对下游 planning 与 coding 构成绑定，但相关权威区块仍应以 `5.4` 与 `6.2` 为准

### 7. 正确性表面（Correctness Surface）

- `7.1 迁移不变量（Migration Invariants）`：说明整个收敛过程中必须持续成立的内容
- `7.2 数据与兼容红线（Data And Compatibility Red Lines）`：这是数据完整性与兼容边界的唯一权威区块
- `7.3 允许的实现变体（Allowed Implementation Variation）`：说明下游实现在哪些地方可以变化而不违反 gap strategy
- `7.4 回流触发器（Reroute Triggers）`：这是哪些发现或条件必须强制回到 `Design Doc` 或 `Gap Analysis Doc`，而不能在下游悄悄打补丁的唯一权威区块

### 8. 残余风险与后续事项（Residual Risks And Follow-Ups）

- `8.1 可接受残余风险（Accepted Residual Risks）`：只记录 sealed 后在法律上可以留下的风险
- `8.2 延后清理项（Deferred Cleanups）`：记录不会阻塞收敛规划的清理项或后续工作
- 不要在这里隐藏 blocker 级差距

## 写作规则

- 为下游 `coder` 与 `reviewer` 的理解而写，不为取悦人类读者而写
- 优化目标是当前态判断真实、差距结构清晰、歧义低
- 在可能时保持文档轻薄，但不能薄到让 `gap_reviewer` 无法在本层单独判断收敛策略
- 每条迁移或兼容规则只保留一个真理源；如果另一个区块才是权威来源，就明确引用，不要在别处重新裁决
- 把 `5.4 不得泄漏到下游的阻塞差距（Blocking Gaps That Must Not Leak Downstream）`、`6.2 切换与共存规则（Cutover And Coexistence Rules）`、`7.2 数据与兼容红线（Data And Compatibility Red Lines）` 和 `7.4 回流触发器（Reroute Triggers）` 视为本文件的结构核心，不能退化成模糊废话

## 禁止内容

不要把以下内容写进 `Gap Analysis Doc`：

- 重写一遍产品愿景
- 第二篇完整设计长文
- Milestone 或 Task 拆分
- PR 路径设计
- 实现教程细节
- reviewer verdict 原文
- 把 blocker 级差距伪装成 residual risk

这些内容应分别放在 `Design Doc`、`Total Task Doc`、planning rolling doc，或更上层裁决里。

## Review-Ready 标准

只有满足以下条件，这份文档才算 review-ready：

- 所有要求的二级标题都存在，或者以有效理由明确标记为 `N/A`
- 被引用的 sealed `Design Doc` 明确要求必须做 gap analysis
- 纳入范围的目标态切片明确
- 相关当前态范围明确
- 当前态判断的证据边界明确
- 主要差距明确
- 收敛策略明确
- `5.4` 中 blocker 差距的权威界线明确
- `6.2` 中共存与切换规则的权威界线明确
- `7.2` 中数据与兼容红线的权威界线明确
- `7.4` 中回流规则的权威界线明确
- 没有把 blocker 级差距藏到下游去

## Seal 标准

只有满足以下条件，这份文档才可以 sealed：

- review-ready 条件已经满足
- `gap_reviewer` 能在不重建隐藏意图的前提下完成判断
- 下游 planning 能把它当作权威来源引用
- `coder` 与下游 reviewers 能仅凭这份文档判断，哪些差距必须被处理或被显式带入下游 planning、哪些约束有绑定力、哪些实现自由度仍然存在
- 如果还有未解决问题，它们也必须是真正的 residual，而不是 blocker
