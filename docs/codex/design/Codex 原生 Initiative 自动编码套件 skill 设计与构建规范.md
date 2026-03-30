# Codex 原生 Initiative 自动编码套件 skill 设计与构建规范

## 封面信息卡

| 项目 | 内容 |
| --- | --- |
| 文档名称 | Codex 原生 Initiative 自动编码套件 skill 设计与构建规范 |
| 文档层级 | Codex 落地方案层 / skill 体系设计规范 |
| 文档定位 | 约束本项目后续 skills 的法位、拆分、合同、目录结构与验收方法 |
| 适用范围 | `.agents/skills/` 下的 repo-local skills 以及与其协作的 scripts / references / assets / custom agents |
| 非目标 | 不替代单个 skill 的 `SKILL.md`；不替代总体机制文档；不替代技术设计说明书 |

## 0. 文档定位

本文档只回答一个问题：

> 在本项目的 Initiative-first 自动编码体系里，skill 应该如何被设计、拆分、实现、验证与维护，才能既保持正交，又不长成失控的超级总控器。

本文档是**项目级 skill 设计规范**，不是通用 skill 教程。
它不负责解释“为什么要有 Initiative-first 体系”，也不负责替代每个 skill 的具体说明，而是固定以下项目级问题：

- 什么应该做成 skill
- 什么不该做成 skill
- skill、script、custom agent、automation 的法位如何切分
- 每个 skill 必须具备哪些合同
- 本项目的 skill 标准目录与命名应该是什么
- 一个 skill 设计完成之前必须通过哪些验证

本文档默认继承：

- [总体机制与落地方案](/Users/nuc8/project/forgeloop/docs/codex/design/Codex%20原生%20Initiative%20自动编码套件总体机制与落地方案.md)
- [技术设计说明书](/Users/nuc8/project/forgeloop/docs/codex/design/Codex%20原生%20Initiative%20自动编码套件技术设计说明书.md)
- [专项实施作战计划书](/Users/nuc8/project/forgeloop/docs/codex/planning/Codex%20原生%20Initiative%20自动编码套件专项实施作战计划书.md)

## 1. 上位关系与基本裁决

### 1.1 skill 的法位

在本项目中，skill 的正式法位固定为：

> **workflow plane 的承载物。**

skill 不是对象层，不是业务真值层，也不是运行态存储层。
它的职责是把已经在上位文档和技术设计中被封板的流程，组织为可复用、可触发、可组合的工作流单元。

因此，skill 适合承载：

- Initiative 入口 workflow
- Task loop workflow
- formal gate / review workflow
- runtime fact 收集与恢复 workflow
- shadow monitoring workflow

skill 不适合承载：

- 状态机真值
- 正式对象定义
- 长期运行态
- 需要高度确定性的底层逻辑本体

### 1.2 本项目的四层分工

本项目后续设计必须长期遵守如下分层：

- `AGENTS.md`：治理层，定义规则、边界、优先级与行为约束
- `skill`：workflow plane，承载工作流与路由
- `custom agent`：角色面，承载 worker / reviewer / observer 等角色能力
- `script`：确定性执行核，承载 parser、state rebuild、artifact projection builder、gate executor 等可测试逻辑

额外操作面分工固定如下：

- App：主控制台
- CLI：调试与窄范围执行入口
- GitHub：PR 协作与辅助审查面
- Automations：shadow 层调度面

### 1.3 skill 不得越权

每个 skill 必须接受以下硬约束：

- 不得自行定义新的 formal gate / review 法位
- 不得把内部检查伪装成 `R1 / R2 / R3`
- 不得把 runtime cache 当真理源
- 不得隐式改变上层调度策略
- 不得把 task-level workflow 偷偷扩大成 initiative-level orchestrator

## 2. 什么该做成 skill，什么不该

### 2.1 应做成 skill 的能力

以下类型通常应做成 skill：

- 稳定且会重复触发的多步骤 workflow
- 需要把 script、reference、asset 和 agent 组合起来的能力
- 需要清晰触发条件与固定输入输出的流程节点
- 用户或主线程会高频调用的编排动作

在本项目中，典型应做成 skill 的包括：

- `run-planning`
- `run-initiative`
- `task-loop`
- `g1-task-gate`
- `cut-anchor`
- `r1-task-review`
- `g2-milestone-gate`
- `r2-milestone-review`
- `g3-initiative-gate`
- `r3-initiative-review`
- `collect-runtime-facts`
- `replay-runtime`

### 2.2 应做成 script 的能力

以下类型通常不应单独做成 skill，而应做成 script，由 skill 调用：

- 结构化解析
- state rebuild
- frontier 计算
- artifact 投影视图构建
- report 正规化
- gate 命令执行
- Git 索引扫描

判断标准很简单：

> 如果这件事的核心价值是“确定性、可重复、可测试”，优先做成 script。  
> 如果核心价值是“工作流组织与触发”，优先做成 skill。

### 2.3 应做成 custom agent 的能力

以下类型应做成 custom agent，而不是 skill：

- 有明确角色边界的实现者
- 有明确角色边界的正式审查者
在本项目中，当前推荐角色是：

- `task_worker`
- `reviewer`

如需补充上下文读取，应由当前执行中的 Agent 自行完成，而不是额外抽出独立只读角色。

skill 负责组织这些角色，角色本身不应反向替代 skill。

### 2.4 不应单独做成 skill 的情况

以下情况不应单独建 skill：

- 只是一次性 glue logic
- 没有稳定输入输出合同
- 只是某个大 skill 的一步，且无法独立复用
- 只是 prompt 片段，没有明确工作流边界
- 只是把一个 shell 命令包装成一个目录
- 只是某个 control-plane skill 内部的一段 admission / validation 检查，例如 `run-initiative` 内部的 planning admission check

## 3. skill 分类体系

### 3.1 控制面 skills

职责：

- 读取 Initiative 总图
- 校验规划
- 重建主状态
- 选择 frontier 与 ready task
- 恢复中断执行

典型 skills：

- `run-planning`
- `run-initiative`
- `rebuild-runtime`
- `select-frontier`
- `replay-runtime`

### 3.2 Task Core skills

职责：

- 驱动 Task 内局部闭环
- 构建 `task brief` 或其派生视图
- 调度 `task_worker` / `reviewer`
- 在局部收口后衔接 formal Task seal

典型 skills：

- `task-loop`
- `g1-task-gate`
- `cut-anchor`
- `r1-task-review`

### 3.3 Milestone Seal skills

职责：

- 从 Task `DONE` 汇总到 Milestone `READY_FOR_PR`
- 组织 PR、G2、R2

典型 skills：

- `open-milestone-pr`
- `g2-milestone-gate`
- `r2-milestone-review`

### 3.4 Initiative Seal skills

职责：

- 从全部 Milestone `MERGED` 汇总到 Initiative `DONE`
- 组织 candidate、G3、R3

典型 skills：

- `g3-initiative-gate`
- `r3-initiative-review`

### 3.5 Ops / Recovery skills

职责：

- 补采运行事实
- 恢复 runtime
- 执行 shadow monitoring

典型 skills：

- `collect-runtime-facts`
- `replay-runtime`
- `shadow-monitor`

## 4. 本项目的 skill 设计原则

### 4.1 单一职责

每个 skill 只解决一个稳定问题。

正确例子：

- `g1-task-gate` 只做 G1
- `cut-anchor` 只做正式 `anchor / fixup` 封口
- `replay-runtime` 只做恢复

错误例子：

- 一个 `task-loop` skill 同时负责 implement、review、anchor、G1、R1、frontier 前移、Milestone seal

### 4.2 正交拆分

skill 边界应按职责拆，而不是按“为了少建几个目录”硬合并。

正交拆分的标准是：

- 它有独立输入
- 它有独立输出
- 它能被单独测试
- 它的失败不会让其它 skill 的职责失真

### 4.3 显式输入输出

每个 skill 都必须有清晰的输入输出，不允许依赖“上下文里大概有”。

输入优先级：

- object key
- artifact ref
- derived-view ref

输出优先级：

- artifact 路径
- 结构化结果引用
- 可供 controller 消费的标准状态更新

### 4.4 薄 skill，厚 script

本项目默认采用：

> **skill 负责 workflow，script 负责 deterministic core。**

因此：

- parser 放 script
- state rebuild 放 script
- bundle builder 放 script
- gate executor 放 script
- report renderer 放 script

skill 只保留：

- 什么时候触发
- 调谁
- 读哪些 brief / note / report
- 产出哪些 artifact
- 出错后如何退出

### 4.5 progressive disclosure

每个 skill 都必须控制上下文负载。

要求：

- `SKILL.md` 只放核心流程和选择规则
- 详细 schema、示例、边界案例放 `references/`
- 大段实现细节放 `scripts/`
- 不在 `SKILL.md` 重复技术设计说明书中的大量内容

### 4.6 正确设置自由度

应根据能力脆弱度决定自由度：

- 高自由度：探索、分析、摘要类
- 中自由度：有推荐路径但允许局部判断的 workflow
- 低自由度：formal gate、artifact 正规化、state rebuild 之类脆弱流程

Task Core 与 formal seal skills 默认应偏低自由度。

### 4.7 validation integrity

一个 skill 是否可用，应靠：

- 结构化输出
- 合同测试
- mock 场景
- 最小 smoke test

而不是靠“这次对话里模型看起来懂了”。

## 5. 标准目录结构

### 5.1 repo-local skill 目录

本项目推荐的 repo-local skill 根目录为：

```text
.agents/
└─ skills/
   └─ <skill-name>/
      ├─ SKILL.md
      ├─ agents/
      │  └─ openai.yaml
      ├─ scripts/
      ├─ references/
      └─ assets/
```

custom agents 定义应放在：

```text
.codex/
└─ agents/
```

### 5.2 `SKILL.md` 的法位

`SKILL.md` 只负责：

- 描述 skill 是什么
- 说明何时触发
- 说明如何工作
- 指向需要时再读的 references 和 scripts

`SKILL.md` 不应承担：

- 大段背景介绍
- 重复的技术设计文档摘抄
- 详细测试指南
- 项目变更日志

### 5.3 `scripts/` 的法位

`scripts/` 负责：

- 可重复执行的确定性逻辑
- 高频被重写、应固化的步骤
- skill 难以可靠口头完成的脆弱流程

### 5.4 `references/` 的法位

`references/` 负责：

- schema 摘要
- brief / report 示例
- artifact 规范
- variant-specific 规则
- 边界场景说明

### 5.5 `assets/` 的法位

`assets/` 只放最终输出可能要使用、但不应直接加载进上下文的资源。

### 5.6 不应出现的文件

默认不应在 skill 目录中出现：

- `README.md`
- `CHANGELOG.md`
- `INSTALLATION_GUIDE.md`
- `QUICK_REFERENCE.md`

除非它们本身是 workflow 必需资产，否则都属于噪音。

## 6. 每个 skill 必须具备的合同

### 6.1 最小设计卡

每个 skill 在进入实现前，必须先有一张设计卡。
推荐模板如下：

```markdown
## Skill Design Card

- Skill Name:
- Layer:
- Purpose:
- Trigger Conditions:
- Inputs:
- Outputs:
- Canonical Sources Read:
- Runtime Cache Read/Write:
- Write Scope:
- Allowed Custom Agents:
- Owned Scripts:
- Failure Modes:
- Escalation Rules:
- Non-goals:
- Validation Plan:
```

### 6.2 必填合同项解释

`Skill Name`

- 使用小写、连字符命名
- 名称应直接体现动作，不要抽象空泛

`Layer`

- 只能从以下枚举中选：
  - `control-plane`
  - `task-core`
  - `milestone-seal`
  - `initiative-seal`
  - `ops-recovery`

`Purpose`

- 一句话说明 skill 解决什么问题

`Trigger Conditions`

- 说明是显式触发、状态驱动触发，还是 automation 定时触发

`Inputs`

- 必须精确到 object key / artifact ref / derived-view ref

`Outputs`

- 必须精确到 artifact / result ref / state update

`Canonical Sources Read`

- 说明依赖哪些正式真理源

`Derived State Read/Write`

- 说明会生成或消费哪些派生视图、临时缓存或局部索引

`Write Scope`

- 必须说明是否允许写仓库、允许改哪些目录

`Allowed Custom Agents`

- 说明是否允许调 `task_worker`、`reviewer` 等

`Owned Scripts`

- 说明哪些脚本属于这个 skill 的确定性内核

`Failure Modes`

- 列出已知失败出口，不要只写 happy path

`Escalation Rules`

- 说明何时必须升级人工或上层对象

`Non-goals`

- 说明本 skill 明确不负责什么

`Validation Plan`

- 说明如何通过测试、mock 和 smoke 验收

## 7. 本项目 skill 的标准写法

### 7.1 `SKILL.md` 推荐结构

每个 `SKILL.md` 建议采用以下结构：

```markdown
---
name: <skill-name>
description: <what it is + when to use it>
---

# <Display Title>

## Purpose

## Use When

## Inputs

## Workflow

## Outputs

## Failure / Escalation

## Read More
```

### 7.2 description 的写法

`description` 是 skill 被选中的主要触发元数据，必须同时回答两件事：

- 这是什么 skill
- 在什么场景下应触发

错误写法：

- “用于各种任务处理”
- “帮助自动化工作流”

正确写法应包含：

- 对象
- 动作
- 适用场景

例如：

- `Run the task-local loop for a ready Task: build the task brief, dispatch the task worker, require G1 before anchor / fixup, then hand off to R1 or escalation.`

### 7.3 Workflow 的写法

Workflow 段落必须：

- 用步骤写
- 明确读什么、调谁、产出什么
- 明确停止条件

不要写成：

- 大段理念说明
- 口号式提醒
- 对技术背景的长篇复述

### 7.4 references 的组织

当一个 skill 支持多个变体时，应把变体细节放到 `references/`，并在 `SKILL.md` 中明确说明何时读取。

例如：

- `references/task-brief.md`
- `references/review-brief.md`
- `references/failure-modes.md`
- `references/smoke-scenarios.md`

## 8. skill 与 agent / script / automation 的接缝

### 8.1 与 custom agents 的接缝

每个 skill 必须显式声明可调用的 custom agents。

规则如下：

- 调 `task_worker` 类 agent 时，必须给出经过裁剪的 `task brief` 或其派生视图
- 调 `reviewer` 类 agent 时，必须给出 `review brief` 或必要的正式证据 ref
- 不允许让 subagent 自己回头漫游全仓库拼主要法源

### 8.2 与 scripts 的接缝

skill 调 script 时，应尽量做到：

- 参数显式
- 返回值结构化
- 出错信息可被 controller 读取

不允许把关键业务规则藏在“某个脚本大概会处理”里却不在设计卡中声明。

### 8.3 与 Automations 的接缝

只有 shadow 类或重复巡检类 skill 才应进入 automation。

硬约束：

- automation 定义 schedule
- skill 定义 method
- automation 不得成为 formal gate / review 唯一入口

### 8.4 与本地派生缓存的接缝

skill 可以生成或消费本地派生缓存，但必须遵守：

- cache 只是派生层
- 所有关键状态都必须可重建
- skill 不得以“本地缓存里有”替代正式证据

## 9. 反模式清单

### 9.1 超级总控 skill

反模式：

- 一个 skill 同时负责规划、调度、执行、审查、收口、恢复

后果：

- 无法测试
- 无法复用
- 一改全崩

### 9.2 skill 越权裁决

反模式：

- `g1-task-gate` 直接把 Task 设为 `DONE`
- `g2-milestone-gate` 直接更新 frontier

正确做法：

- skill 只输出结构化结果
- controller 决定状态推进

### 9.3 以自然语言代替结构化输出

反模式：

- “看起来没问题，可以继续”

正确做法：

- 输出 artifact path
- 输出 result ref
- 输出结构化 verdict

### 9.4 以隐式上下文代替工件合同

反模式：

- 依赖“模型应该知道现在是哪一个 task”

正确做法：

- 显式传入 `task_brief`、`gate evidence note`、`review_brief` 或对应 object key

### 9.5 skill 过薄或过厚

过薄：

- 只是一个 shell 命令包装

过厚：

- 自己又像 orchestrator，又像 parser，又像 reviewer

正确做法：

- 让 skill 处在“有稳定 workflow、但不吞掉确定性内核”的中间层

## 10. skill 构建流程

### 10.1 第一步：判定是否值得成为 skill

先回答四个问题：

- 这是稳定 workflow 吗
- 这是高频复用的吗
- 它有清晰输入输出吗
- 它需要组合 script / reference / agent 吗

若四问中多数为否，通常不应建新 skill。

### 10.2 第二步：写设计卡

先写设计卡，再建目录。
没有设计卡，不进入实现。

### 10.3 第三步：确定目录与资源

判断这个 skill 是否需要：

- `scripts/`
- `references/`
- `assets/`
- `agents/openai.yaml`

默认原则：

- 能下沉到 script 的，不放进 `SKILL.md`
- 能放 reference 的，不堆进正文

### 10.4 第四步：实现最小版本

最小版本应只覆盖：

- 单一职责主路径
- 最小必要输入输出
- 一个可演示场景

先不要一上来补齐所有边角能力。

### 10.5 第五步：做三层验证

每个 skill 至少经过三层验证：

- 合同验证：输入输出结构成立
- mock 验证：workflow 在受控场景可跑通
- smoke 验证：最小真实场景可跑通

### 10.6 第六步：再决定是否推广为 release 必备能力

只有当 skill：

- 边界稳定
- 输出稳定
- 失败方式稳定

之后，才应把它纳入某个 release 的正式能力包。

## 11. 验收与发布标准

### 11.1 一个 skill 设计完成的最低标准

必须同时满足：

- 已有设计卡
- `SKILL.md` 已成型
- 目录结构符合规范
- 输入输出合同明确
- 脚本与 agent 接缝明确
- 至少有一个 mock 场景

### 11.2 一个 skill 可以进入主线的最低标准

必须同时满足：

- 有对应的合同测试
- 有最小 smoke path
- 不与现有 skill 重叠职责
- 不引入新的双真值

### 11.3 一个 skill 可以进入 release 范围的最低标准

必须同时满足：

- 它所在 capability module 已明确
- 它在 release 中承担清晰职责
- 它的失败不会让上层法位失真
- 它的回退点已定义

## 12. 与发版计划的映射

### 12.1 `R0 / MVP Alpha` 必需 skills

`R0` 只应建设最小核心集：

- `rebuild-runtime`
- `run-initiative`
- `task-loop`
- `g1-task-gate`
- `cut-anchor`
- `r1-task-review`

### 12.2 `R1 / Beta` 新增 skills

- `open-milestone-pr`
- `g2-milestone-gate`
- `r2-milestone-review`

### 12.3 `R2 / v1.0` 新增 skills

- `g3-initiative-gate`
- `r3-initiative-review`
- `replay-runtime` 强化版

### 12.4 `R3 / v1.1` 新增或强化 skills

- `collect-runtime-facts`
- `shadow-monitor`
- readonly observer 相关 skills

## 13. 封板结论

本项目后续的 skill 设计工作，必须以以下裁决为准：

- **skill 是 workflow plane，不是对象层**
- **skill 要正交拆分，不做超级总控器**
- **skill 要薄，确定性逻辑要下沉到 script**
- **skill 只组织角色，不代替 custom agent**
- **skill 可以读写 runtime cache，但不能把 cache 当真理源**
- **每个 skill 必须先有设计卡，再有实现，再进 release**

用一句话概括：

> **本项目的 skill 体系，不追求数量，而追求边界清晰、合同稳定、可测试、可发版。**

planning preflight 应视为 `run-initiative` 内部的 execution control plane step。
它负责接纳或拒绝 sealed planning docs 进入 runtime，不单独建成 skill，也不属于 planning authoring 主链。
