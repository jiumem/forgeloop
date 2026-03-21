# Agent 编程项目执行模型法典
## 对象 × 提交 × 验证 × 审查 × 触发时机

> **状态**：Sealed / v1  
> **定位**：Agent 原生时代的软件工程执行法典  
> **适用范围**：需要持续集成、分阶段收敛、正式审查、可发布交付的软件项目  
> **不适用范围**：一次性脚本、短期实验、无需主干收敛与发布纪律的临时代码  
> **核心目标**：建立一套**语义清晰、法位稳定、证据充分、可映射到 Git / CI / Review / Release 的执行模型**

---

## 0. 文档定位

本文档封板五部分内容：

1. **对象模型**
2. **提交模型**
3. **验证模型**
4. **审查模型**
5. **触发时机模型**

本文档**不讨论**以下主题：

- Prompt / Skill 设计
- 具体 CI 平台与工具链选型
- 具体 package scripts 命名
- 具体仓库目录结构
- 具体断言 catalog 结构
- 具体产品领域法与协议法
- 具体项目映射样板

这些内容应在仓库级规则、专项设计文档或实现文档中继续展开，而不应污染本法的上位结构。

---

## 1. 核心结论

整套模型可以压缩为一句话：

> **Task 用 commit 收敛差异，Milestone 用 PR 收敛状态，Initiative 用 release / flag / deployment 收敛交付。**  
> **对应地，验证体系分为 G1 / G2 / G3 三层阻断门，另设 Shadow 作为非阻断预警层；审查体系分为 R1 / R2 / R3 三层正式审查，另设 SR 作为非阻断预警审查。**

这套模型之所以成立，不是因为术语好看，而是因为它同时满足三件事：

| 目标 | 含义 |
|---|---|
| **高吞吐** | Task 级开发不能被重型 CI 拖死 |
| **高收敛** | Milestone 合入前必须证明阶段状态闭环成立 |
| **高可信** | Initiative 发布前必须证明目标兑现且具备回退能力 |

---

## 2. 第一性原则

### 2.1 规划对象与物理动作必须解耦

规划对象回答的是**系统如何被理解**。  
物理动作回答的是**差异如何被保存、集成与交付**。

因此：

| 规划对象 | 物理动作 |
|---|---|
| Initiative / Milestone / Task | commit / push / PR / release |

它们不能做僵硬的一一映射。  
一旦把对象与动作强行绑定，系统就会重新长出错误语义，例如：

- 把 `push` 误当成阶段成立信号
- 把 `PR` 误当成专项本体
- 把 `commit` 误当成任务完成证明

---

### 2.2 验证资源必须分层

在 Agent 时代，最便宜的是代码生成，最昂贵的是：

- **CI 算力**
- **主干收敛性证明**
- **审查注意力**
- **真实环境发布成本**

因此，验证不能做成一锅粥，而必须分层：

> **把快验证留给 Task，把集成验证留给 Milestone，把交付验证留给 Initiative。**

---

### 2.3 审查必须按对象分层

审查不是把验证再跑一遍，也不是统一用一种视角扫所有改动。

| 审查层 | 核心问题 |
|---|---|
| **Task** | 当前锚点是否可信 |
| **Milestone** | 当前阶段是否收敛 |
| **Initiative** | 当前专项是否可交付 |

如果三个层级都在重复讨论同样的问题，审查体系必然失焦。

---

### 2.4 命名必须法位化

只要 Assertion、Profile、Execution Surface 再次混名，系统就会重新长出第二套语义系统。

因此必须坚持：

> **L1 负责声明。**  
> **L2 负责编排。**  
> **L3 负责执行。**

三者不得互相代位。

---

## 3. 三层对象模型

对象模型只保留三层，不再继续扩张。

| 层级 | 正式名称 | 中文 | 本质定义 |
|---|---|---|---|
| L1 | **Initiative** | 专项 | 一次完整目标闭环，来源可为产品、架构、治理、性能、质量等 |
| L2 | **Milestone** | 里程碑 | 一个阶段状态首次成立的收敛边界 |
| L3 | **Task** | 任务 | 最小可实现、可验证、可继续推进的工程闭环 |

---

### 3.1 Initiative

Initiative 不是 Epic 的别名，也不是产品需求的替身。  
它代表的是一次完整战役，而不是一个页面、一个票据、一个 PR，或者几条待办事项。

它可以来自：

- 产品能力建设
- 架构演进
- 技术债治理
- 稳定性 / 性能专项
- 安全 / 合规整改
- 基础设施与治理收敛

因此，Initiative 的法定结束条件不是“某个 PR 合并”，而是：

> **目标兑现，具备发布、全量、交付或结项资格。**

---

### 3.2 Milestone

Milestone 不是时间阶段，也不是施工阶段。  
它的本质是：

> **某个系统状态、某个能力闭环、或某个不变量组合，第一次可以被正式宣布成立。**

它不是“做了多少事情”，而是“现在是否已经形成一个自洽状态”。

因此，Milestone 是：

- 阶段收敛边界
- 状态成立断点
- 验收的法定坐标系

它不是：

- 开发进度条
- 目录组织手段
- Git 对象本体

---

### 3.3 Task

Task 是最小工程闭环，而不是随意待办项。  
一个合法 Task 至少同时满足四个条件：

| 条件 | 含义 |
|---|---|
| **明确输入** | 依赖哪些契约、文档、接口、前置状态 |
| **明确动作** | 到底要改什么，不能写成“顺手优化一下” |
| **明确输出** | 代码、测试、脚本、迁移、配置、文档等 |
| **明确边界** | 哪些内容不在本任务范围内 |

Task 不直接对主干负责，它只对**局部实现闭环**负责。

---

## 4. 三层正式命名体系

当前正式命名体系固定如下：

| 层级 | 正式名称 | 中文 | 职责 |
|---|---|---|---|
| L1 | **Assertion Plane** | 断言层 | 定义 Gate Family / Gate / Gate Suite / Gate Catalog / Formal Entrypoint Contract |
| L2 | **Profile Plane** | 编排层 | 定义 Gate Profile 与 Review Profile；定义 blocking / non-blocking 协议 |
| L3 | **Execution Surface** | 执行面 | 映射到 package scripts、CLI、CI、PR checks、release pipeline、external targets |

---

### 4.1 命名铁律

#### 铁律 1
**凡属于 L2 的对象，正式名称必须显式包含 `Profile`。**

#### 铁律 2
**凡属于 L1 的对象，正式名称不得包含 `Profile`。**

#### 铁律 3
**L1 只负责声明，不得携带阻断策略、执行时机、环境目标。**

#### 铁律 4
**L2 只负责编排，不得重新定义断言内容。**

#### 铁律 5
**L3 只负责执行映射，不得成为真理源。**

---

## 5. 提交模型

提交模型不按“对象 = Git 动作”做僵硬映射，而是明确每个物理动作的法定职责。

| 物理动作 | 法定职责 |
|---|---|
| **Commit** | 为 Task 打差异锚点 |
| **Push** | 将当前分支状态同步为远端快照，可触发预警检查 |
| **PR** | 作为 Milestone 收敛容器，承载正式集成 |
| **Release / Flag / Deployment** | 作为 Initiative 交付动作 |

---

### 5.1 Commit 的正式地位

Commit 的职责不是表示“任务完成”，而是：

> **为验证、审查、回滚、归因提供精确差异锚点。**

因此，Task 与 commit 的关系正式定义为：

> **每个 Task 至少必须沉淀一个 anchor commit。**

这并不意味着一个 Task 只能有一个 commit。  
探索性提交可以很多，但最终必须收敛为一个可定位、可审查、可验证的任务锚点。

---

### 5.2 Push 的正式地位

Push 不是状态边界，也不是阶段完成标志。  
它只是：

> **当前连续工作上下文的远端快照同步动作。**

它的价值在三处：

1. 形成远端可恢复快照
2. 供并行 worktree / Agent / 云端环境接续
3. 触发 Shadow Checks，尽早发现系统性漂移

所以：

> **Push 只承担同步与预警语义，不承担准入语义。**

---

### 5.3 PR 的正式地位

PR 不是 Initiative 的容器，而是：

> **Milestone 的收敛容器。**

一个 PR 的合法职责只有一个：

> **承载一个 Milestone 进入主干前的正式集成、验证与收敛过程。**

因此默认法则是：

> **一个 Milestone 默认对应一个 PR。**  
> **一个打开中的 PR 允许持续 push、持续 review、持续修补，直到满足合并条件。**

PR 不是一次性快照，而是一个**持续演化的阶段收敛容器**。

---

### 5.4 Branch 的正式地位

Branch 不是对象层级本身，而是：

> **连续工作上下文的容器。**

因此，Branch 不应被法定绑定到 Initiative 或 Milestone。  
实践上存在两种都合法的形态：

| 形态 | 说明 |
|---|---|
| **Initiative 长分支** | 用于承载长期语义连续性 |
| **Milestone 分支 / worktree** | 用于承载更强隔离与更清晰集成边界 |

无论采用哪一种，**PR 的法定对象仍然是 Milestone**。

---

### 5.5 Initiative 前缀规则

Initiative 前缀不应成为默认宗教，它是**规模化追踪开关**。

推荐启用场景：

- 并行多个 Initiative
- 同一 Initiative 下连续存在多个 Milestone PR
- 多 worktree / 多 Agent 并行

不推荐强制启用场景：

- 仓库长期只推进一个 Initiative
- 团队规模小，Milestone 名本身已足够唯一

因此正式规则是：

> **Initiative 前缀用于跨阶段索引，不作为默认必须项。**

它最适合出现的位置是：

- 分支名
- PR 标题
- worktree 名
- 专项审查报告
- 发布记录

它**不应**进入 commit 标题。

---

## 6. Commit 结构化文本规范 v1

### 6.1 定位

本规范定义 **Task 级 commit，尤其是 anchor commit** 的正式文本格式。  
目标不是美化 Git 历史，而是保证每个差异锚点都能最小成本回答四个问题：

> **这次改了什么？**  
> **为什么现在改？**  
> **边界在哪里？**  
> **验证做到哪一步了？**

---

### 6.2 第一原则

Commit 不是日记，而是：

> **差异锚点说明书。**

一个合法的 anchor commit 必须同时承载三类信息：

| 信息类型 | 作用 |
|---|---|
| **Intent** | 告诉 reviewer 这次差异的目标 |
| **Boundary** | 告诉 reviewer 这次差异的边界与非目标 |
| **Verification** | 告诉 reviewer 这次差异跑过哪些检查 |

---

### 6.3 Commit 类型分层

| 类型 | 正式用途 | 是否可作为审查锚点 |
|---|---|---|
| `wip` | 探索性中间提交 | 否 |
| `anchor` | Task 正式锚点提交 | 是 |
| `fixup` | 针对 review / gate 失败的修补提交 | 是 |
| `revert` | 明确撤销某个已存在锚点或范围 | 是 |

正式审查默认只围绕：

> **anchor / fixup / revert**

`wip` 只服务开发过程，不进入正式审查。

---

### 6.4 标题格式

正式格式固定为：

```text
<kind>(<milestone-key>/<task-key>): <imperative summary>
````

例如：

```text
anchor(m1/t023): establish PhraseAsset v1 schema
fixup(m1/t023): normalize empty source before dedupe
revert(m2/t041): roll back unsafe legacy read-path bypass
wip(m1/t024): draft import normalization pipeline
```

---

### 6.5 标题硬规则

#### 规则 A

**标题必须表达动作，不得表达情绪或模糊状态。**

正确：

* establish schema
* add idempotency guard
* remove legacy adapter

错误：

* fix stuff
* update logic
* improve flow
* final patch

#### 规则 B

**标题必须聚焦单一主动作。**

#### 规则 C

**标题不得重复写 Initiative 前缀。**

---

### 6.6 正文模板

对于 `anchor / fixup / revert`，正文模板固定为：

```text
Intent: <本次提交的核心目标>
Scope: <本次提交触达的责任边界>
Non-Goals: <明确不在本次范围内的内容>
Checks: <本次已执行的检查>
Risk: <当前残余风险，可选>
Follow-Up: <后续任务或依赖，可选>
```

必要时可增加：

```text
Spec-Refs: <规范切片索引>
Cause: <fixup / revert 的原因>
Reverts: <被撤销的 commit sha 或锚点>
Initiative: <可选索引字段，不进标题>
```

---

### 6.7 示例

```text
anchor(m1/t023): establish PhraseAsset v1 schema

Intent: Define PhraseAsset v1 fields and invariants for storage baseline.
Scope: Schema/types only; no read-path adapter, no editor integration.
Non-Goals: No migration cleanup; no UI/API behavior changes.
Checks: gate:task, typecheck, test:phrase-asset, snapshot:phrase-asset-v1
Spec-Refs:
- docs/phrase-library.md#phraseasset-schema
- packages/contracts/src/phrase.ts:10-48
Risk: Legacy rows without source normalization are still unsupported.
Follow-Up: t024 read adapter; t025 import normalization.
```

---

### 6.8 与 Gate / Review 的关系

#### 与 G1 的关系

**只有通过 G1 的 anchor commit，才可被认定为合法 Task 锚点。**

#### 与 R1 的关系

**结构化 commit 文本，是 R1 的输入协议，而不是文风装饰。**

---

## 7. 验证模型：三层 Gate 与一层 Shadow

### 7.1 四类正式验证 Profile

| Profile | 正式名称                        | 中文     | 性质           |
| ------- | --------------------------- | ------ | ------------ |
| G1      | **Task Gate Profile**       | 任务门编排  | blocking     |
| G2      | **Milestone Gate Profile**  | 里程碑门编排 | blocking     |
| G3      | **Initiative Gate Profile** | 专项门编排  | blocking     |
| Shadow  | **Shadow Check Profile**    | 影子校验编排 | non-blocking |

特别强调：

> **Shadow 保持为 Check Profile，而不是 Gate Profile。**

---

### 7.2 G1：Task Gate

G1 的本质是：

> **证明当前 Task 对应的 anchor commit，已经具备继续推进的最低工程可信度。**

对象是 Task 锚点，而不是整条分支。

推荐检查项：

| 检查项                             | 目标         |
| ------------------------------- | ---------- |
| Lint / format                   | 清除低级噪音     |
| Type check                      | 锁住接口边界     |
| Affected unit tests             | 验证局部逻辑成立   |
| Contract / snapshot quick check | 锁住结构不变量    |
| Rule scan                       | 阻断已知架构禁忌   |
| Minimal smoke                   | 验证最小主路径可跑通 |

时延预算：

> **30 秒 ～ 5 分钟**

失败语义：

> **该 anchor commit 不得被认定为合法任务锚点。**

---

### 7.3 G2：Milestone Gate

G2 是正式集成闸门，它证明：

> **一组 Task 已共同形成一个可安全进入主干的阶段闭环。**

对象是 Milestone PR，而不是单个 commit。

推荐检查项：

| 检查项                               | 目标                       |
| --------------------------------- | ------------------------ |
| Affected build / package build    | 验证基本组装成立                 |
| Cross-module integration tests    | 验证边界交互无破裂                |
| Contract tests                    | 验证上下游接口无漂移               |
| Migration / compatibility checks  | 防止半迁移与兼容破坏               |
| Core path E2E                     | 验证主链路真实可跑通               |
| Architecture rule checks          | 防止越权调用、双事实源、ownership 泄露 |
| State / idempotency checks        | 防止重复写、乱序写、不可重试           |
| Config / security baseline checks | 防止基础安全与配置退化              |

时延预算：

> **5 分钟 ～ 30 分钟**

失败语义：

> **PR 不允许合并。**

---

### 7.4 G3：Initiative Gate

G3 是交付闸门，它证明：

> **多个已成立 Milestone 的累计效果，已经满足发布、全量或结项条件。**

对象不是 PR，而是：

* release candidate
* feature flag rollout candidate
* deployment candidate
* initiative closeout candidate

推荐检查项：

| 检查项                             | 目标                |
| ------------------------------- | ----------------- |
| Full regression                 | 验证多里程碑叠加后无整体退化    |
| Staging / pre-prod verification | 验证接近真实环境的稳定性      |
| Performance / load tests        | 防止功能成立但系统扛不住      |
| Migration & rollback rehearsal  | 防止只可前进、不可后退       |
| Feature flag on/off checks      | 防止灰度与全量切换失控       |
| Observability checks            | 验证日志、监控、告警、追踪充分可见 |
| Business acceptance             | 验证专项目标真实兑现        |

核心原则：

> **低频、关键、真实。**

失败语义：

> **不允许发布 / 不允许全量 / 不允许专项结项。**

---

### 7.5 Shadow Checks

Shadow Checks 的职责是：

> **把原本会在 G2 / G3 爆炸的问题尽量提前暴露。**

它是预警层，不是准入层。

典型检查项：

| 检查项         | 价值          |
| ----------- | ----------- |
| 受影响模块构建     | 提前发现组装问题    |
| 低成本集成 smoke | 提前发现边界错接    |
| 架构规则扫描      | 提前发现语义漂移    |
| 依赖冲突检查      | 提前发现包图退化    |
| 低优先级全量巡检    | 提前发现系统性回归征兆 |

输出只保留三色：

| 等级     | 含义                          |
| ------ | --------------------------- |
| Green  | 无明显风险                       |
| Yellow | 建议在下一个 Task / Milestone 前处理 |
| Red    | 高概率将在 G2 / G3 爆炸            |

---

## 8. 审查模型：三层 Review 与一层 Shadow Review

### 8.1 四类正式审查 Profile

| Profile | 正式名称                          | 中文      | 性质           |
| ------- | ----------------------------- | ------- | ------------ |
| R1      | **Task Review Profile**       | 任务审查编排  | blocking     |
| R2      | **Milestone Review Profile**  | 里程碑审查编排 | blocking     |
| R3      | **Initiative Review Profile** | 专项审查编排  | blocking     |
| SR      | **Shadow Review Profile**     | 影子审查编排  | non-blocking |

---

### 8.2 R1：Task Review

R1 只回答一个问题：

> **这个 anchor commit / commit range，是否已经是一个可信的 Task 锚点。**

它不是在审系统，也不是在审主干，它只审：

> **这块零件是否足够干净、足够清楚、足够值得继续推进。**

#### R1 输入协议

1. 结构化 commit 文本
2. 相关规范切片（仅当触及契约、字段、接口、状态、迁移时必须加载）
3. G1 结果
4. commit diff
5. 必要时源码上下文

#### R1 审查重点

| 审查项          | 核心问题                      |
| ------------ | ------------------------- |
| Intent 对齐    | 这次改动是不是在做它声称要做的事          |
| Scope 收敛     | 是否越出了声明的责任边界              |
| Non-Goals 清晰 | 是否把“故意不做”误判成“漏做”          |
| 局部正确性        | 控制流、边界条件、异常处理是否站得住        |
| 验证充分性        | 当前 G1 与 Checks 是否真锁住了本次改动 |
| 局部回归风险       | 是否引入明显局部回退                |

#### R1 不审什么

* 全局架构是否完美
* Milestone 是否闭环
* Initiative 是否达标
* 风格偏好式吹毛求疵

#### R1 输出建议

* Verdict
* Findings
* Validation Adequacy
* Escalation

---

### 8.3 R2：Milestone Review

R2 是正式收敛审查，它回答：

> **这个 Milestone PR，是否已经形成了一个可安全并入主干的阶段闭环。**

#### R2 输入协议

1. Milestone Reference Doc
2. PR 内 anchor commits 索引
3. G2 结果
4. PR diff / branch diff against base
5. 必要时相关设计文档章节

#### R2 审查重点

| 审查项    | 核心问题                     |
| ------ | ------------------------ |
| 状态闭环   | 该 Milestone 宣称成立的状态是否真闭环 |
| 事实源收敛  | 是否出现双真值、影子状态、隐式同步        |
| 契约同步   | 下层结构、边界适配、调用方是否同步迁移      |
| 失败语义一致 | 错误、重试、补偿是否逻辑统一           |
| 兼容路径控制 | 过渡层是否可控，是否污染主链           |
| 验证代表性  | G2 是否覆盖主风险面              |
| 架构收敛性  | 这次合并会不会恶化后续演进成本          |

#### R2 输出建议

* Verdict
* Convergence Findings
* Evidence Adequacy
* Residual Risks
* Required Follow-Ups

---

### 8.4 R3：Initiative Review

R3 不再看单个 diff，也不再看单个 PR。
它回答的是：

> **这个 Initiative，作为一个完整专项，是否已经具备正式交付资格。**

#### R3 输入协议

1. Initiative Reference Doc
2. Milestone 完成矩阵
3. G3 结果
4. release / flag / deployment candidate
5. 风险、债务、验收材料

#### R3 审查重点

| 审查项           | 核心问题                                |
| ------------- | ----------------------------------- |
| 目标兑现度         | 原始 Initiative 目标是否真实达成              |
| Milestone 完整性 | 必需里程碑是否都已成立                         |
| 交付可信度         | rollout / release / deployment 是否安全 |
| 回退可信度         | 出问题时是否可降级、回滚、止血                     |
| 残余债务可接受性      | 当前未完成项是否仍允许上线/结项                    |
| 业务接受度         | 产品或技术目标是否被真正验收                      |

#### R3 输出形式

**Initiative Review Report**
而不是普通 PR 评论。

---

### 8.5 SR：Shadow Review

SR 不是正式准入审查，只做一件事：

> **在正式 G2 / G3 之前，尽早发现分支正在累积的漂移征兆。**

#### SR 输入对象

* push 后的 branch 快照
* 自上次正式 review 以来的 commit range
* Shadow Checks 输出

#### SR 关注重点

| 审查项    | 核心问题                     |
| ------ | ------------------------ |
| 语义漂移   | 当前分支是否逐渐偏离原 Milestone 目标 |
| 范围膨胀   | 是否偷偷混入下一个 Milestone 内容   |
| 重复修补征兆 | 是否同类 fixup 已连续复发         |
| 未来爆炸半径 | 是否高概率会在 G2 / G3 才集中爆炸    |

#### SR 输出

* green
* yellow
* red

以及一条行动建议：

* continue
* checkpoint before next task
* open milestone review early

---

## 9. 上位参考文档输入协议

Review 不是对 diff 本身做判断，而是对：

> **diff 与上位参考之间的一致性**

做判断。

因此，三层审查的上位参考文档必须分层存在。

---

### 9.1 Task：规范切片

Task Review 默认不读整篇设计文档，但以下 Task 必须附带规范切片：

* 接口定义调整
* 数据字段新增 / 删除 / 改语义
* DTO / schema / proto 变更
* migration
* 状态流转调整
* 错误语义变化
* 边界 / 所有权迁移

正式规则：

> **凡触及契约、字段、接口、状态、迁移的 Task，R1 必须读取相关规范切片。**

建议用 `Spec-Refs` 显式索引，而不是让 reviewer 自己去猜。

---

### 9.2 Milestone：Milestone Reference Doc

Milestone Review 不能只靠 PR diff 猜阶段目标。
因此，每个 Milestone 必须有一份上位参考页，至少包含：

* Milestone 名称
* 目标闭环
* 范围
* 非目标
* 依赖
* 验收标准
* 风险与后续

正式规则：

> **Milestone Review 必须以 Milestone Reference Doc 为法定上位参考。**

---

### 9.3 Initiative：Initiative Reference Doc

Initiative Review 更必须有正式方案文档。
至少包含：

* 背景与目标
* 范围与非目标
* 成功标准
* Milestone 规划
* 发布 / rollout 策略
* 风险与债务策略

正式规则：

> **Initiative Review 必须以 Initiative Reference Doc 为法定上位参考。**

---

## 10. 触发时机模型

任何提交、验证、审查动作，都必须由**状态触发**或**事件触发**驱动。
禁止使用模糊触发语义，例如：

* 差不多了
* 看起来可以了
* 先审一下
* 顺手跑一下

---

### 10.1 提交触发

| 对象         | 动作                      | 触发时机                             |
| ---------- | ----------------------- | -------------------------------- |
| Task       | anchor commit           | 任务意图稳定、范围收口、差异局部自洽、准备进入正式验证 / 审查 |
| Branch     | push                    | 需要远端快照、协作接续、或触发 Shadow           |
| Milestone  | PR                      | 已形成第一个可集成闭环，开始进入正式收敛期            |
| Initiative | release / flag / deploy | 已形成交付候选，准备进入真实发布动作               |

---

### 10.2 验证触发

| 层级     | 动作              | 触发时机                                       |
| ------ | --------------- | ------------------------------------------ |
| G1     | Task Gate       | anchor / fixup 锚点成立前                       |
| Shadow | Shadow Checks   | push 后、巡检、依赖 / 规则变化后                       |
| G2     | Milestone Gate  | PR 打开、关键更新、合并前                             |
| G3     | Initiative Gate | release / rollout / closeout candidate 形成时 |

---

### 10.3 审查触发

| 层级 | 动作                | 触发时机                                 |
| -- | ----------------- | ------------------------------------ |
| R1 | Task Review       | anchor / fixup 锚点形成时                 |
| SR | Shadow Review     | push 后、漂移征兆出现时                       |
| R2 | Milestone Review  | PR 打开、关键更新、合并前、R1 升级时                |
| R3 | Initiative Review | release / flag / closeout 前，或交付风险重评时 |

---

## 11. 运行节奏

### 11.1 Task 内循环

Task 开始后，Agent 在当前连续工作上下文中推进实现。
探索性 `wip` 可以存在，但在 Task 收口时必须沉淀出一个 `anchor commit`。
此时跑 G1，通过后才允许进入 R1。

于是 Task 的默认节奏是：

> **实现 → anchor commit → G1 → R1 → 继续推进**

---

### 11.2 Branch 快照预警

开发者 / Agent 可以持续 push。
push 后触发 Shadow Checks 与必要时的 Shadow Review，用于尽早发现问题，但不阻断主流程。

于是 push 的节奏是：

> **push → Shadow Checks → Shadow Review（必要时）→ 预警反馈**

---

### 11.3 Milestone 外循环

当一组 Task 已构成一个阶段闭环时，发起 PR。
该 PR 作为 Milestone 收敛容器，持续接受修补、push、验证与审查。

于是 Milestone 的节奏是：

> **开 PR → G2 → R2 → 修补 → push → G2 → R2 → 直到合并**

---

### 11.4 Initiative 收口

多个 Milestone PR 合并入主干后，专项并未自动完成。
只有在 G3 完成并满足 rollout / release 条件后，Initiative 才具备正式交付资格。

于是 Initiative 的节奏是：

> **累计 Milestone → G3 → R3 → release / flag / deployment**

---

## 12. 对齐矩阵

### 12.1 三层对象 × 提交 × 验证

| 对象层            | 收敛动作                        | 正式验证               | 目标     |
| -------------- | --------------------------- | ------------------ | ------ |
| **Task**       | anchor commit               | G1 Task Gate       | 局部零件合格 |
| **Milestone**  | PR                          | G2 Milestone Gate  | 阶段状态闭环 |
| **Initiative** | release / flag / deployment | G3 Initiative Gate | 目标交付兑现 |

辅助层：

| 非正式层                  | 动作   | 验证            | 性质     |
| --------------------- | ---- | ------------- | ------ |
| **Branch Checkpoint** | push | Shadow Checks | 预警，不准入 |

---

### 12.2 三层对象 × 提交 × 审查

| 对象层            | 收敛动作                        | 正式审查                 | 目标   |
| -------------- | --------------------------- | -------------------- | ---- |
| **Task**       | anchor commit               | R1 Task Review       | 锚点可信 |
| **Milestone**  | PR                          | R2 Milestone Review  | 状态收敛 |
| **Initiative** | release / flag / deployment | R3 Initiative Review | 交付可信 |

辅助层：

| 非正式层                  | 动作                   | 审查               | 性质     |
| --------------------- | -------------------- | ---------------- | ------ |
| **Branch Checkpoint** | push / periodic scan | SR Shadow Review | 预警，不放行 |

---

## 13. 升级规则

为了避免审查与验证沦为重复劳动，正式加三条升级规则。

### 规则 1

**R1 发现共享根因或跨层裂缝时，必须升级到 R2。**

### 规则 2

**R2 发现发布级、业务级或 rollout 级风险时，必须升级到 R3。**

### 规则 3

**同类问题连续两轮以上复发时，必须沉淀为规则资产，而不是继续靠人工提醒。**

规则资产的合法承载体包括：

* lint / semgrep
* gate / suite
* regression tests
* snapshot / contract checks
* `AGENTS.md`
* review 指南

---

## 14. 禁止事项

### 14.1 对象层禁止事项

* 把 Branch 直接升格为 Milestone 或 Initiative
* 把 PR 视为专项本体
* 把 push 视为阶段成立证据

### 14.2 提交层禁止事项

* 没有 anchor commit 就进入正式审查
* 让 `wip` 进入正式审查
* 让 commit 标题承担 Initiative 索引职责
* 用模糊标题掩盖真实边界

### 14.3 验证层禁止事项

* 所有检查塞进一个统一 gate
* 把 Shadow 当正式准入门
* 把最重 CI 下沉到 Task 层
* 在 Profile Plane 重新定义断言内容

### 14.4 审查层禁止事项

* 让 R1 重演 R2
* 让 R2 重演 R3
* 让 SR 冒充正式放行
* 让 reviewer 在无上位参考的情况下脑补真理

### 14.5 命名层禁止事项

* L1 对象带 `Profile`
* L2 对象不带 `Profile`
* Execution Surface 反向定义法定对象
* 把索引键写进所有层级名字

---

## 15. 当前范围外内容

本文档有意不展开：

* Prompt / Skill 设计
* 具体 CI 平台与缓存策略
* 具体 package scripts 命名
* 具体仓库目录布局
* 具体 assertion catalog 结构
* 具体产品领域法与协议法
* 具体项目映射样板

这些内容适合在仓库级法、专项样板或附录中继续展开，而不应污染主法。

---

## 16. 封板结论

当前已经达成一致并可封板的体系，可以压缩为以下十二条法则。

### 法则 1

**对象层只保留三层：Initiative、Milestone、Task。**

### 法则 2

**Task 用 commit 收敛差异，Milestone 用 PR 收敛状态，Initiative 用 release / flag / deployment 收敛交付。**

### 法则 3

**Branch 只是连续工作上下文容器，不作为对象层级的法定映射。**

### 法则 4

**Assertion Plane / Profile Plane / Execution Surface 三层正式命名封板，不再变更。**

### 法则 5

**L2 对象必须显式包含 `Profile`；L1 对象不得包含 `Profile`。**

### 法则 6

**每个 Task 至少必须沉淀一个 anchor commit；`wip` 不进入正式审查。**

### 法则 7

**验证体系采用三层 Gate：G1、G2、G3，另设 Shadow 作为非阻断预警层。**

### 法则 8

**G1 验证零件是否合格，G2 验证状态是否闭环，G3 验证价值是否兑现；Shadow 负责早发现，不承担正式准入责任。**

### 法则 9

**审查体系采用三层 Review：R1、R2、R3，另设 SR 作为非阻断预警审查。**

### 法则 10

**R1 审零件可信度，R2 审状态收敛性，R3 审交付可信度，SR 审早期漂移征兆。**

### 法则 11

**Task 读规范切片，Milestone 读阶段文档，Initiative 读专项文档；Review 是对差异与上位参考一致性的裁决。**

### 法则 12

**提交、验证、审查动作都必须由法定状态或法定事件触发，禁止凭感觉触发。**

---

> **最终收口：**
>
> **代码不再是这套系统的中心对象。**
> **对象、锚点、证据、裁决、交付才是中心。**
>
> 在 Agent 时代，真正的工程优雅，不是把代码写得更快，而是让高吞吐生成永远被收敛在一套**可证明、可审查、可交付、可回滚**的结构之内。

