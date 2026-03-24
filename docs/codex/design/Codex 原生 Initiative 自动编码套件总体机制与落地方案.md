# Codex 原生 Initiative 自动编码套件总体机制与落地方案

## 封面信息卡

| 项目 | 内容 |
| --- | --- |
| 文档名称 | Codex 原生 Initiative 自动编码套件总体机制与落地方案 |
| 文档层级 | Codex 落地方案层 |
| 文档定位 | 上位宪法与 Codex 原生机制之间的总体映射与运行说明文档 |
| 适用范围 | 需要以 Initiative 为主入口、以 Milestone 为阶段收敛边界、以 Task 为内部原子的 Agent 自动编码体系 |
| 非目标 | 不定义上位宪法；不展开数据模型、状态机、artifact 合同细节；不展开逐 PR 实施计划 |

## 0. 文档定位

本文档只回答一个问题：

> 如何把上位宪法层的对象模型、角色边界、Gate / Review 体系，映射为一套符合 Codex 原生机制的 Initiative 自动编码套件，并说明其总体运行方式。

本文档是**总体机制文档**，不是技术定义文档，也不是实施排期文档。
它的职责是把下列问题一次性说清：

- 用户入口究竟是什么
- 主线程在 Codex 中承担什么正式责任
- Task、Milestone、Initiative 分别如何在 Codex 原生机制中落位
- 为什么某些外部方法只能被局部吸收，而不能上升为总框架
- 用户如何使用这套系统
- 系统内部如何从一个 Initiative 持续推进到阶段收口与交付收口

本文档不承担以下职责：

- 不重定义 Initiative / Milestone / Task 的法位
- 不给出完整数据模型、状态机与 artifact 合同定义
- 不给出函数级算法与实现接口细节
- 不给出逐 PR 的专项实施排期
- 不替代技术设计说明书与专项实施作战计划书

因此，本文档与后续两篇文档的关系固定如下：

- 本文档负责**机制、映射、流程、约束**
- 技术设计说明书负责**模型、状态、工件、接口、算法**
- 专项实施作战计划书负责**阶段、PR、验收、推进**

---

## 1. 上位法继承与下位裁决边界

### 1.1 继承的上位文档

本方案直接继承以下六篇上位宪法文档，不在下位重新定义其法位：

- `Agent 编程项目核心术语表`
- `Agent 编程项目执行模型法典`
- `Agent 编程项目规划模型`
- `Agent 编程项目 Planner 协议`
- `Agent 编程项目 Coder 协议`
- `Agent 编程项目 Reviewer 协议`

因此，本方案并不重新回答以下问题：

- Initiative / Milestone / Task 是什么
- G1 / G2 / G3 与 R1 / R2 / R3 的法位是什么
- Planner / Coder / Reviewer 的边界是什么
- 总任务文档为什么是合法执行总图

这些都已由上位文档封板。

### 1.2 本文档新增的下位裁决

在不改写上位宪法的前提下，本文档补充下列 **Codex 落地级裁决**：

第一，**Initiative 是用户与正式调度的唯一默认主入口。**  
用户启动的是一个 Initiative，而不是一个 Task。Task 只在系统内部作为最小执行原子被调度。

第二，**Milestone 是正式阶段收敛与用户断点的默认边界。**  
Milestone 不只是规划层对象，还决定了系统何时开 PR、何时进入 G2 / R2、何时向用户请求阶段裁决。

第三，**Task Loop 采用“局部委派执行模板”，但它不构成整个系统的上位框架。**  
也就是说，Task 内可以吸收 implement -> spec check -> quality check 的局部收口模式；但系统整体仍然是 Initiative-first，而不是 task-first delegate framework。

第四，**Task 内部检查不进入 formal review 法位。**  
规范符合性检查与代码质量检查，只是 anchor 前的局部收口机制；只有 anchor commit 形成后，G1 / R1 才成立。

第五，**主线程不是空壳 dispatch agent。**  
主线程必须保留 Initiative 调度、Milestone frontier、Ready Task 选择、升级裁决汇总、用户断点沟通与正式收口衔接职责。

第六，**Codex 原生机制各自承担固定法位。**  
`AGENTS.md` 承担治理层，skills 承担 workflow plane，custom agents 承担角色面，repo 内脚本与 Python 内核承担确定性执行面。

第七，**运行态必须可重建。**  
任何运行时 cache 都只能是派生状态，不得成为正式真理源。

### 1.3 不进入本文档的内容

以下内容不属于本篇职责，应下沉到第二篇技术设计说明书：

- `initiative_plan`、`initiative_state`、`task_packet` 等具体模型
- 状态枚举、跃迁规则、loop phase 细节
- packet / report / bundle / runtime facts 的字段合同
- scripts、skills、agents 的输入输出协议
- 持久化路径、命名规则、工件索引策略
- 错误模型、mock、测试设计

以下内容不属于本篇职责，应下沉到第三篇专项实施作战计划书：

- 当前专项的阶段拆分
- PR 序列与依赖关系
- 每个 PR 的写入范围
- 验收清单与回退点

---

## 2. Codex 原生机制与体系映射前提

### 2.1 Codex 原生机制总览

Codex 当前原生能力已经天然具备分层结构，而不是一个单一 prompt 入口。
在本方案中，真正会被拿来承载体系的机制主要有六类：

- `AGENTS.md`
- `skills`
- `custom agents / subagents`
- App
- CLI
- GitHub / Automations / Worktrees 等配套机制

这些机制并不是平级替代关系，而是各自承担不同法位：

- `AGENTS.md` 负责提供持久、分层、就近覆盖的项目规则；Codex 会在工作前读取相关指令文件，并按 root-to-leaf 的顺序拼接，越接近当前目录的规则优先级越高。[1]
- skills 负责承载可复用 workflow；它们采用 progressive disclosure，只在真正命中时才加载完整 `SKILL.md`，并可携带 `scripts/`、`references/`、`assets/` 与 `agents/openai.yaml`。[2]
- subagents 负责显式委派的局部工作；Codex 只会在你明确要求时才创建 subagent，而且每个 subagent 都会带来额外 token 与工具成本。[3]
- App 原生提供并行任务、内置 Git、worktrees、review pane、automations 等控制台能力，适合作为日常主操作面。[4][5][6]
- GitHub 适合作为 PR 级代码评审面，可用 `@codex review` 或 Automatic reviews 获取辅助审查输入。[7]
- `.codex/config.toml` 用于共享配置默认值，而不是运行态存储；Codex 会叠加用户级和项目级配置，最近目录的项目配置优先。[8]

因此，本方案不是在 Codex 之上另造一套平行控制系统，而是：

> **利用 Codex 已有的原生分层机制，承载上位宪法要求的对象、流程与边界。**

### 2.2 为什么必须做机制映射，而不是直接照搬外部方法

外部方法可以提供局部启发，但它们不能直接成为我们的总框架。

原因在于，上位宪法已经把系统法位固定为：

- Initiative 是最高层执行对象
- Milestone 是正式阶段收敛边界
- Task 是内部最小工程闭环
- Gate / Review 采用三层正式结构

而很多外部方法只解决其中一段问题。
例如：

- 有些方法长于 Task 内的委派执行、局部检查与多轮修补
- 有些方法长于把大任务压成 Initiative-first 的总图
- 有些方法更偏工具编排，不足以承担正式对象层与正式收口层

因此，本方案的态度不是“择一替代”，而是“按法位吸收”：

- Initiative-first 的总体调度逻辑被保留为外层控制面
- Task 内的 delegate mechanics 被吸收为内部执行模板
- Formal Gate / Review 仍严格服从上位宪法

这也是本文档的核心判断：

> **我们不是在三套方案之间做折中平均。**
> **我们是在上位宪法约束下，对 Codex 原生能力做最终取舍与落位。**

### 2.3 本方案对 Codex 原生能力的基本判断

基于官方文档与本仓库目标，本方案对 Codex 原生能力作如下判断：

第一，Codex 原生机制已经足够承载 v1。  
skills、AGENTS、subagents、App、GitHub review、Automations、Worktrees 组合起来，已经形成可用的治理层、workflow 层、角色层和操作面。

第二，Codex 的主线程不应被削成纯转发器。  
官方文档强调 subagent 是显式触发、可并行但更昂贵的辅助机制；这意味着主线程仍然必须掌握 requirements、decisions 和 final outputs 的主导权，而不能放弃调度与裁决责任。[3]

第三，skills 比 prompt 片段更适合承载正式 workflow。  
因为它们有清晰的 `name / description`、渐进加载机制、repo 范围扫描规则和可附带脚本资源，更适合承载稳定可复用的流程。[2]

第四，Automations 适合 shadow 层，不适合 blocking 主链。  
官方文档明确 Automations 在后台运行，要求 App 保持运行、项目路径在磁盘上可用，并可与 skills 组合；这非常适合预警、巡检、重复分析，但不适合充当 G1 / G2 / G3 或 R1 / R2 / R3 的唯一执行通道。[5]

第五，Worktrees 是并行隔离工具，不是对象层。  
Worktree 可以解决线程隔离、自动化隔离和并行执行隔离，但不能把 branch 或 worktree 误升格为 Milestone 或 Initiative。[6]

---

## 3. 上位宪法与 Codex 原生机制的映射关系

### 3.1 Initiative 作为用户与调度主入口

上位宪法已经明确 Initiative 是最高层执行对象，因此在 Codex 落地时，Initiative 也必须成为：

- 用户默认启动对象
- 主线程默认绑定对象
- 运行态默认索引对象
- 正式调度默认上下文

这意味着用户心智要被压缩成一句话：

> **我启动一个 Initiative。系统围绕这份 Initiative 总任务文档持续推进。**

用户不应日常手动挑 Task，也不应长期停留在“当前是哪一个 patch”的思考模式中。

### 3.2 Milestone 作为正式阶段收敛边界

Milestone 在本方案里承担两类作用：

- 对内：作为 frontier 选择、Ready Task 约束、PR 打开与合并前验证的阶段坐标
- 对外：作为用户最重要的日常断点和阶段裁决对象

因此，本方案不允许把用户体验做成“每个 Task 都来询问一次”。
真正对用户有意义的节奏是：

- 启动 Initiative
- 系统推进当前 Milestone
- 在 Milestone 收口、跨层升级、Initiative 交付候选形成时再打断用户

### 3.3 Task 作为内部最小执行原子

Task 的法位在本方案中保持不变：

- 它是最小可实现、可验证、可继续推进的工程闭环
- 它是 anchor commit 的对应对象
- 它是 G1 / R1 的进入坐标

但它的**交互法位**被进一步明确：

- Task 不是终端用户的默认入口
- Task 不承担系统整体调度
- Task 只在 Initiative Runtime 的内部被构包、执行、检查、收口

换句话说：

> **Task 是内部执行原子，不是外部操作主语。**

### 3.4 Task 内部检查与 Formal Gate / Review 的边界

这是融合方案里必须写死的一条。

Task 内部允许存在两类局部检查：

- 规范符合性检查
- 代码质量检查

它们的作用是：

- 在 anchor 前尽早暴露“是不是那件事”
- 在 anchor 前尽早清理明显工程噪音与局部回归风险
- 降低主线程和实现者的上下文污染

但这两类检查**不进入 formal review 法位**。
它们不产生 R1 通过裁决，也不替代 G1。

正式边界只能是：

```text
Task 内部检查
  -> READY_FOR_ANCHOR
  -> anchor commit
  -> G1
  -> R1
```

因此，本方案吸收的是 Task 内 delegate sandwich 的局部机制，而不是把内部检查层升格成第四层正式审查。

### 3.5 主线程、局部 delegate 与正式裁决的边界

主线程在本方案中承担的正式责任包括：

- 绑定当前 Initiative 与其总任务文档
- 做 Planning Preflight
- 重建运行态
- 选择 Milestone frontier
- 选择 Ready Tasks
- 执行写入串行 / 只读并行策略
- 汇总升级、阻断、阶段收口与交付收口
- 与用户沟通正式断点

局部 delegate 只承担 bounded work，例如：

- 单个 Task 的实现
- 单个 Task 的规范符合性检查
- 单个 Task 的代码质量检查
- 大范围只读探索、日志分析、差异分析

因此，本方案明确反对两种极端：

- 反对主线程空壳化
- 反对 subagent swarm 取代正式对象层与正式裁决层

---

## 4. 总体机制架构

### 4.1 机制分层总览

整套机制可压缩为四层：

```text
治理层
  -> AGENTS.md / .codex/config.toml / 规则资产

规划真理源层
  -> 方案设计文档 / 差距分析文档 / Initiative 总任务文档

运行控制层
  -> Initiative Runtime / Milestone Frontier / Task Loop

正式证据层
  -> anchor commit / PR / candidate / Gate / Review / 真实环境验证
```

四层之间的职责关系是：

- 治理层定义工作纪律与默认边界
- 规划真理源层提供对象与边界
- 运行控制层负责推进与组织
- 正式证据层负责证明当前对象是否成立

### 4.2 治理层、控制层、执行层、证据层的关系

如果进一步展开，本方案中的关键元素可以这样理解：

| 层 | 承载物 | 正式职责 |
| --- | --- | --- |
| 治理层 | `AGENTS.md`、`.codex/config.toml`、规则资产 | 固定工作纪律、默认配置、禁止事项 |
| 控制层 | `run-initiative`、frontier 选择、状态重建 | 组织当前 Initiative 的推进顺序与节奏 |
| 执行层 | `task-loop`、局部 delegate、repo 脚本 | 推进单个 Task 从局部收口到 formal seal |
| 证据层 | anchor / PR / candidate / gate / review / 真实环境记录 | 为 Task / Milestone / Initiative 的成立提供正式证明 |

必须强调：

> **运行控制层推进状态。**
> **证据层证明状态。**
> **二者不得互相代位。**

### 4.3 用户视角与系统视角的双重结构

从用户视角看，这套系统应该尽量简单：

```text
准备 Initiative 总任务文档
  -> 启动 Initiative
  -> 等待系统持续推进
  -> 在 Milestone / 升级 / 交付断点介入
```

从系统视角看，它是一个持续循环：

```text
Planning Preflight
  -> Rebuild State
  -> Select Frontier
  -> Select Ready Tasks
  -> Run Task Loops
  -> Seal Milestone
  -> Seal Initiative
  -> Request User Only at Formal Breakpoints
```

这两种视角必须同时成立：

- 用户不需要承受系统内部的 Task 编排噪音
- 系统也不能因为隐藏复杂性而失去 formal structure

---

## 5. 用户主路径与使用方式

### 5.1 用户如何启动一个 Initiative

用户在日常使用中，首先需要具备：

- 已封板的方案设计文档
- 差距分析文档（如适用）
- 单篇总任务文档
- 可执行的工程验证命令
- 基本仓库规则与治理资产

具备这些条件后，用户的正式动作不是“开一个 Task”，而是：

> **启动一个 Initiative 的持续推进。**

在 Codex App 中，这通常表现为：

- 打开项目
- 进入合适的工作目录
- 在绑定该项目的线程中显式启动 Initiative workflow

在 CLI 中，这通常表现为：

- 进入仓库工作目录
- 显式运行 Initiative 入口 skill 或对应脚本

### 5.2 用户在日常推进中看到什么

用户日常看到的，应该主要是：

- 当前 Initiative 所处状态
- 当前 Milestone frontier
- 当前一批 Ready Tasks 的推进情况
- 当前是否存在 escalation / blocked / waiting review
- 当前是否接近 Milestone 或 Initiative 收口

用户不应被迫天天盯着：

- 每个 Task 的每一轮修补细节
- 每个局部 delegate 的中间对话
- 每个内部检查的局部噪音

### 5.3 用户在什么断点必须介入

本方案把用户介入点收束为三类正式断点：

第一，**规划输入不合法时**  
例如前置文档缺失、参考入口未指派、关键边界未裁决。

第二，**跨层升级或系统失真时**  
例如 Task 切法失真、Milestone 边界失真、现状理解与前置设计冲突。

第三，**正式收口时**  
包括：

- Milestone 收口前的 G2 / R2 / PR 裁决
- Initiative 交付候选形成后的 G3 / R3 / 真实环境放行裁决

除此之外，用户默认不应被频繁轮询。

### 5.4 用户不应承担什么内部调度负担

用户不应承担以下系统内部负担：

- 手动决定下一条 Ready Task
- 手动协调多个局部 delegate 的上下文
- 手动判断哪些内部检查该先跑
- 手动拼装 Task packet
- 手动把局部 review 意见翻译成正式收口对象

这些都属于系统内部运行责任。

本方案要达成的用户心智，最终应压缩为一句话：

> **我启动一个 Initiative。系统持续推进。只有在正式断点才来找我。**

---

## 6. 系统内部主流程

### 6.1 Planning Preflight

系统进入正式推进前，首先必须验证当前 Initiative 总任务文档是否具备合法输入质量。

它至少要确认：

- 当前 Initiative 是否有合法前置文档
- Milestone / Initiative 的参考入口是否被唯一指派
- 总任务文档是否已经具备执行总图的基本字段
- 是否仍存在未裁决问题

若 preflight 失败，系统不应“先跑起来再说”，而应在入口处直接阻断。

### 6.2 Initiative State Rebuild

正式推进前，系统必须从 canonical sources 重建派生状态，而不是盲信本地 cache。

重建时至少会读：

- 总任务文档
- Git 中的 anchor / fixup / revert 证据
- 当前 PR / branch / candidate 状态
- 最近的 Gate / Review 结果

重建完成后，系统才知道：

- 当前 Initiative 已推进到哪里
- 哪些 Task 已完成
- 哪些 Milestone 已收口
- 当前下一步应该推进什么

### 6.3 Milestone Frontier Selection

系统随后会选择当前可推进的 Milestone frontier。

默认原则是：

- 选择最早的、尚未收口且依赖已满足的 Milestone
- 不越过未成立的前置 Milestone 去做后续 Milestone 的正式写入推进

这样做的目的不是保守，而是维持正式阶段边界与正式证据链的一致性。

### 6.4 Ready Task Selection

在当前 frontier 内，系统根据以下条件选择 Ready Tasks：

- 当前 Milestone 内的依赖关系
- Workstream 之间的耦合关系
- 当前 Task 的状态
- 当前是否允许写入

这里的关键裁决是：

- 只读探索、日志分析、证据整理可以并行
- 同一 Milestone 的写入型推进默认串行

### 6.5 Task Loop

当一个 Task 被选中后，系统进入 Task Loop。

Task Loop 的正式节奏不是“改完就审”，而是：

```text
build task packet
  -> implement
  -> spec check
  -> quality check
  -> READY_FOR_ANCHOR
  -> anchor commit
  -> G1
  -> R1
  -> DONE / BLOCKED / DEFERRED / ESCALATE
```

其中：

- implement、spec check、quality check 都属于 Task 内局部收口
- READY_FOR_ANCHOR 是内部正向终态，不是 formal done
- 只有 anchor / G1 / R1 之后，Task 才能进入正式成立判断

### 6.6 Milestone Seal

当当前 Milestone 所需 Task 已达到阶段收口条件后，系统进入 Milestone seal。

这一步会把局部差异聚合到 Milestone 级容器里，进入：

- PR 打开或更新
- G2
- R2

在这一层，审查对象已经不再是单个 Task 锚点，而是阶段闭环。

### 6.7 Initiative Seal

当必需 Milestone 全部成立后，系统进入 Initiative seal。

这一步会把当前专项推进到交付候选层，进入：

- G3
- R3
- 真实环境验证、灰度、回滚与最终放行

必须明确：

> **多个 Milestone 合并不等于 Initiative 自动成立。**
> **没有 G3 / R3 与真实环境裁决，就没有正式交付。**

---

## 7. Codex 原生能力如何承载该体系

### 7.1 `AGENTS.md` 的法位

`AGENTS.md` 在本方案中承担的是**治理层**，不是运行态。

它应该承载的内容包括：

- 仓库级工作纪律
- 交付模式与禁止事项
- review 指南
- 目录级覆盖规则

官方文档明确指出，Codex 会在工作前读取相关 `AGENTS.md`，并按项目 root 到当前目录的顺序拼接，越近的目录可以覆盖更外层的规则。[1]

因此，本方案的裁决是：

> **`AGENTS.md` 负责约束行为，不负责保存运行状态。**

### 7.2 skills 的法位

skills 在本方案中承担的是**workflow plane**。

它们适合承载：

- Initiative 入口 workflow
- Task Loop workflow
- Gate / Review workflow
- shadow 类 workflow

官方文档说明，skills 是带有 `SKILL.md` 的目录，可以附带 `scripts/`、`references/`、`assets/` 与 `agents/openai.yaml`，并采用 progressive disclosure，仅在被选中时才加载全文。[2]

因此，本方案把 skills 视为：

> **正式 workflow 的主承载物。**

对应地，formal workflow 默认应关闭隐式触发，要求显式调用或明确状态触发，而不是依赖模型“觉得现在应该调用”。[2]

### 7.3 custom agents 的法位

custom agents 在本方案中承担的是**角色面**，而不是对象层。

它们适合表达：

- 当前局部执行者是谁
- 当前局部检查者是谁
- 当前当前只读探索者是谁

官方文档说明，Codex 只会在显式请求时才创建 subagent；subagent 会继承当前 sandbox 策略；项目级 custom agents 可以放在 `.codex/agents/` 下定义。[3]

因此，本方案的裁决是：

- 主线程保留正式调度与汇总职责
- 局部 worker / reviewer / explorer 由 custom agents 承担
- subagent 是 bounded execution unit，不是平行主线程

### 7.4 repo 脚本与 Python 内核的法位

skills 和 agents 可以承载意图、角色与路由，但不能代替确定性执行核。

在本方案中，repo 内脚本与 Python 内核承担：

- 文档解析
- 状态重建
- frontier 选择
- Ready Task 选择
- packet 构建
- Gate / Review bundle 组织
- report 渲染

换句话说：

> **模型负责判断与组织。**
> **脚本负责确定性、可测试、可复现的执行。**

### 7.5 App / CLI / GitHub / Automations 的分工

本方案对 Codex 各操作面的分工如下：

**App**  
作为日常主控制台。官方文档明确 App 支持并行任务、内置 Git、worktrees、skills、automations 与 review pane，适合作为多线程、多阶段推进的主界面。[4][5][6]

**CLI**  
作为专家入口。适合手动重放某个步骤、调试某个 skill、执行恢复操作或做窄范围实验。

**GitHub**  
作为 PR 与协作审查面。可通过 `@codex review` 或 Automatic reviews 获取辅助审查输入；但 GitHub review 不是 R2 / R3 本体。[7]

**Automations**  
作为 shadow 层后台能力。官方文档指出 Automations 在后台运行，要求 App 保持运行，可在本地项目或独立 worktree 中运行，并可与 skills 组合。[5]  
因此，它适合：

- 周期巡检
- 预警校验
- 预警审查
- 重复分析任务

但不适合承担：

- 唯一的正式准入门
- 唯一的正式收口链

---

## 8. Formal Gate / Review 在 Codex 中的承载方式

### 8.1 G1 / R1 映射

Task 级正式收口在 Codex 中的承载方式是：

- 当前 Task 完成局部收口
- 形成 anchor commit
- 运行 G1
- 生成 R1

这里必须保持刚性边界：

- spec check / quality check 不是 R1
- 没有 anchor commit，不进入 G1 / R1

### 8.2 G2 / R2 映射

Milestone 级正式收口在 Codex 中的承载方式是：

- 打开或更新 Milestone PR
- 运行 G2
- 生成 R2

此时对象不再是单个 commit，而是：

- PR diff
- 阶段性 Task 聚合
- Milestone Reference

GitHub review 可以在这一层提供辅助输入，但不能取代 R2 本体。[7]

### 8.3 G3 / R3 映射

Initiative 级正式收口在 Codex 中的承载方式是：

- 形成 release / rollout / deployment / closeout candidate
- 运行 G3
- 生成 R3
- 进入真实环境验证与最终放行

这一步必须与用户裁决边界显式衔接：

- Codex 可以组织本地证据
- Codex 可以草拟审查报告
- 最终交付裁决仍然归用户

### 8.4 Shadow Check / Shadow Review 映射

Shadow 层在本方案中承担的是**早发现，不准入**。

它可以：

- 在 push 后跑轻量检查
- 周期性发现漂移征兆
- 将发现推送到 App 的 automation inbox

但它不能：

- 冒充正式 Gate
- 冒充正式 R1 / R2 / R3
- 越过正式阶段边界直接给通过裁决

---

## 9. 整体运行必须遵守的关键约束

### 9.1 真理源与运行态分离

正式真理源必须始终是：

- 规划文档
- 代码与 Git 证据
- Gate / Review / 真实环境证据

运行时 cache 只能是派生态。
这意味着任何 `.initiative-runtime/` 一类目录都必须被理解为：

- 可删
- 可丢
- 可重建

而不能成为正式放行依据。

### 9.2 主线程不空壳

主线程必须保留：

- Initiative 状态
- Milestone frontier
- Ready Task 排产
- 正式断点汇总
- 用户沟通

如果把主线程削成“只会转发给子 agent”，系统就会失去真正的调度中枢。

### 9.3 Task 内部检查不升格为 formal review

这是防止系统长出第四层伪审查的关键约束。

内部检查可以非常严格，但它们只能服务于：

- 局部收口
- 早暴露问题
- 降低 formal R1 噪音

它们不能直接产出：

- Task 正式通过
- Milestone 正式通过
- Initiative 正式通过

### 9.4 同一 Milestone 写入串行

官方 worktree 文档明确指出，同一 branch 不能在多个 worktree 中同时 checkout；Git 会把该 branch 视为由某个 worktree 独占，以避免并发写入带来的歧义与竞态。[6]

因此，本方案的正式策略是：

- Initiative 级可并行
- Workstream 级只读工作可并行
- 同一 Milestone 的写入型推进默认串行

### 9.5 正式 Gate / Review 不依赖隐式触发

formal workflow 一旦依赖“模型觉得应该调用”，就会失去可执法性。

因此，本方案要求：

- Formal skill 默认关闭隐式调用
- Formal Gate / Review 由明确状态或明确入口触发
- 隐式 skill 只保留给 helper 型、非正式辅助流程

### 9.6 治理资产与日常交付分离

`AGENTS.md`、`.codex/`、`.agents/` 属于治理层。

日常 delivery run 不应随意改写：

- 根治理规则
- config 默认值
- custom agent 定义
- 正式 skill 资产

这些变更应走专门治理变更路径，而不是混入普通交付流。

---

## 10. 并行、升级与中断策略

### 10.1 Initiative 级并行

允许多个 Initiative 在独立 thread / worktree 中并行推进。

前提是：

- 各自绑定不同的总任务文档
- 各自拥有清晰边界
- 不共享同一写分支

### 10.2 Workstream 级并行

允许的并行类型包括：

- 只读探索
- 日志分析
- runtime facts 收集
- shadow 类检查
- 文档索引与证据整理

不建议默认并行的类型包括：

- 同一 Milestone branch 上的多个写入型 Task
- 未明确边界的大范围子 agent swarm

### 10.3 升级路径

系统内部的升级路径应固定为：

- Task 内局部问题：留在 Task Loop
- Task / Milestone 边界失真：升级到 Planner / 规划层裁决
- 交付级风险：升级到用户与 Initiative 层裁决

升级的意义不是把问题“抛给人”，而是把问题送回**正确责任层**。

### 10.4 用户断点

用户断点应尽量少而硬。
本方案只认可三类主要断点：

- Planning blocked
- Escalation required
- Formal seal required

除这三类之外，系统应尽量自行消化局部噪音。

---

## 11. 风险、约束与后续衔接

### 11.1 当前风险

当前最大的风险，不在于机制不够多，而在于机制边界失真。
主要风险包括：

- 把 Task 内部检查误写成 formal review
- 把主线程做空
- 把 runtime cache 偷偷变成真理源
- 把 GitHub review 误当成正式 R2 / R3
- 把 Automations 误当成 blocking 主链

### 11.2 当前约束

本方案成立有若干现实约束：

- 仓库必须拥有可执行的总任务文档
- 仓库必须有基本可跑的验证命令
- Git 必须是正式证据载体之一
- 用户必须接受结构化对象高于自然语言总结
- 项目必须接受真实环境验证仍然由人承担

同时，Codex 原生侧也有实际约束：

- 项目级 config 仅在 trusted project 下加载.[8]
- 默认推荐在 version-controlled 目录使用 `workspace-write + on-request approvals`；默认 writable roots 仍存在受保护路径。[9]
- Automations 在后台运行时要求 App 保持运行、项目在磁盘可用。[5]

### 11.3 与技术设计说明书、专项作战计划书的衔接

本文档完成后，后续文档的边界应固定如下：

第二篇《技术设计说明书》继续回答：

- 具体模型长什么样
- 状态如何编码
- packet / artifact 如何定义
- Runtime 如何重建
- skills / agents / scripts 如何接线

第三篇《专项实施作战计划书》继续回答：

- 当前专项分几阶段落地
- PR 怎么切
- 验收断点怎么设
- 风险与回退点怎么安排

---

## 12. 封板结论

本文档的最终结论可以压缩为下面几条：

第一，**这套系统是 Initiative-first，不是 task-first。**

第二，**Milestone 是正式阶段边界，Task 是内部最小原子。**

第三，**Task 内可以吸收 delegate mechanics，但不能让 delegate framework 升格为总框架。**

第四，**主线程必须保留正式调度与汇总责任，不能空壳化。**

第五，**Codex 原生机制已经足够承载 v1，但每种机制必须放在正确法位上。**

第六，**Formal Gate / Review 仍只认 Task / Milestone / Initiative 三层正式收口。**

第七，**用户体验必须被压缩为：启动一个 Initiative，让系统持续推进，只在正式断点介入。**

最后，用一句话收口：

> **这套 Codex 原生 Initiative 自动编码套件，不是把很多 agent 拼在一起。**
> **它是在上位宪法约束下，把 Codex 原生机制组织成一套可持续推进、可正式收口、可被用户真正使用的 Initiative 级执行系统。**

---

## 参考资料

[1] OpenAI Developers, “Custom instructions with AGENTS.md – Codex”  
<https://developers.openai.com/codex/guides/agents-md>

[2] OpenAI Developers, “Agent Skills – Codex”  
<https://developers.openai.com/codex/skills>

[3] OpenAI Developers, “Subagents – Codex”  
<https://developers.openai.com/codex/subagents>

[4] OpenAI Developers, “App – Codex”  
<https://developers.openai.com/codex/app>

[5] OpenAI Developers, “Automations – Codex app”  
<https://developers.openai.com/codex/app/automations>

[6] OpenAI Developers, “Worktrees – Codex app”  
<https://developers.openai.com/codex/app/worktrees>

[7] OpenAI Developers, “Use Codex in GitHub”  
<https://developers.openai.com/codex/integrations/github>

[8] OpenAI Developers, “Config basics – Codex”  
<https://developers.openai.com/codex/config-basic>

[9] OpenAI Developers, “Agent approvals & security – Codex”  
<https://developers.openai.com/codex/agent-approvals-security>
