# Codex 原生 Initiative 自动编码套件专项实施作战计划书

> 状态说明：本文为历史设计稿，用于追溯演进，不代表 0.9.0 当前发布面。当前发布面以 `README*`、`docs/forgeloop/*`、`plugins/forgeloop/skills/*` 与 `plugins/forgeloop/agents/*` 为准。文中出现的 `task-loop`、`g1-task-gate`、`r2-milestone-review`、`replay-runtime` 等旧名称，均应视为历史方案。

## 封面信息卡

| 项目 | 内容 |
| --- | --- |
| 文档名称 | Codex 原生 Initiative 自动编码套件专项实施作战计划书 |
| 文档层级 | Codex 落地方案层 / 专项规划层 |
| 文档定位 | 将总体机制与技术设计拆解为可发版路线、能力包矩阵与 PR 序列的实施计划文档 |
| 适用范围 | 当前仓库的 Codex 原生 Initiative 自动编码套件建设专项 |
| 非目标 | 不充当上位宪法；不充当技术定义文档；不写 prompt 细节 |

## 0. 文档定位

本文档只回答一个问题：

> 这套 Codex 原生 Initiative 自动编码套件，应该按什么发版节奏、能力切片和 PR 序列推进，才能以产品标准而不是功能堆砌的方式落地。

本文档默认承接：

- 上位宪法层六篇文档
- `Codex 原生 Initiative 自动编码套件总体机制与落地方案`
- `Codex 原生 Initiative 自动编码套件技术设计说明书`

因此，本文档不再解释：

- 为什么 Initiative 是主入口
- 为什么 Task 只是内部原子
- 为什么内部检查不等于 formal review
- 为什么 runtime cache 必须可重建

本文档只处理三类问题：

- 每一版究竟要交付什么能力
- 每一版由哪些正交能力包组成
- 这些能力包如何落成可执行 PR 序列

## 1. 规划原则与专项边界

### 1.1 专项目标

本专项的目标不是“补齐几个技能”，而是逐版交付一套真正可运行的 Initiative 自动编码产品。

交付目标按最终形态可压缩为一句话：

> 用户给出一份 Initiative 总任务文档，系统能够以 Initiative 为主入口持续推进，在 Task、Milestone、Initiative 三层对象上完成正式收口。

### 1.2 发版优先于功能堆叠

本文档采用 **release-first** 规划法，而不是 feature-first 规划法。

其含义是：

- 每一版都必须能对用户说清楚“现在这版能做什么”
- 每一版都必须有明确验收线、演示路径和回退点
- 不把尚未形成用户价值的中间态包装成“版本完成”

因此，本文档中的第一优先级不是“功能点完整”，而是“版本能力闭环成立”。

### 1.3 借鉴正交 skills，而不照搬外部总框架

本专项吸收的核心方法是：

- 外层按可发版产品能力规划
- 内层按正交 skill / capability module 拆分

这意味着：

- release 回答“这一版系统能不能用”
- capability module 回答“这版由哪些稳定能力包组成”
- PR 回答“代码应该按什么顺序落地”

因此，本计划不会照搬任何 task-first 总体方法，但会主动采用“单一职责、低耦合、可独立验收”的 skill 拆法。

### 1.4 明确非目标

本专项当前阶段的非目标如下：

- 不做多 milestone 并发写入
- 不做分布式 worker 或队列
- 不做 dashboard 与可视化系统
- 不做 GitHub 深度自动化编排中心
- 不把 Automations 升格为 blocking 主链
- 不先做大规模 prompt 工程，再反向补状态机

## 2. 当前基线与前置条件

### 2.1 当前仓库基线

当前仓库已经具备两条可复用基线：

第一条是旧主线的 Task-first 结构化视图与结果合同基础：

- `schemas/task_packet.py`（旧结构化投影视图原型）
- `schemas/review_result.py`
- `schemas/task_state.py`
- `automation/controller/transitions.py`

这条线已经证明：

- 多个核心模型有清晰业务真值地位
- controller 规则可以 deterministic 化
- 合同优先、mock 优先的实施方法可行

第二条是 Initiative Runtime MVP 原型线：

- `codex_initiative_runtime_mvp/`

这条线已经证明：

- Initiative 文档可被 parse 为结构化 plan
- runtime state 可从 plan 与 Git/报告回建
- frontier / ready task 选择已有可运行原型

### 2.2 现有可复用资产

本专项可直接继承以下资产：

- 四个核心模型的合同意识
- 旧 controller 的显式跃迁思路
- initiative plan / runtime state 的雏形
- state rebuild、artifact projection builder、gate/review bundle builder 的原型脚手架

### 2.3 当前主要缺口

当前缺口集中在五点：

- 旧四模型与 Initiative Runtime 尚未统一成正式对象层
- Task loop 还没有固化为 `implement / repair -> G1 -> anchor / fixup -> R1`
- Milestone / Initiative formal seal 仍停留在原型与文档层
- Codex-native skills / custom agents 还未按正交能力包正式接线
- replay / resume、shadow automation、readonly observer 等运维能力仍未正式化

## 3. 发版路线图总览

### 3.1 版本总览

本专项建议拆成四个版本：

| 版本 | 版本定位 | 用户承诺 | 不是这一版要解决的问题 |
| --- | --- | --- | --- |
| `R0 / MVP Alpha` | Initiative Task Core | 能以 Initiative 为入口，自动推进单 frontier 下的单写入 Task，完成到 `R1` 的正式 Task 收口 | 不要求 Milestone / Initiative 全自动正式收口 |
| `R1 / Beta` | Milestone Ready | 能在 Task 正式收口基础上完成 Milestone 级 `PR -> G2 -> R2` | 不要求 Initiative 级交付候选与 `G3 / R3` |
| `R2 / v1.0` | Initiative Ready | 能从 Initiative 启动一路推进到 `G3 / R3` 与交付候选 | 不要求 shadow automation 与只读并行观测成为正式能力 |
| `R3 / v1.1` | Operations Hardening | 补齐 replay / resume 强化、shadow automation、readonly observer、worktree 硬化 | 不做分布式与多 milestone 并发 |

### 3.2 为什么第一版要减重

若把以下能力全部塞进第一版：

- Task loop
- Milestone seal
- Initiative seal
- replay / resume
- automations
- readonly parallel observers

那么第一版会同时承担：

- 对象层重构
- 状态机重构
- workflow plane 建设
- formal seal 三层接线
- 运维层补齐

这会显著拉高首次交付门槛，导致版本定义失焦。

因此，第一版必须只证明最核心的新价值：

> Initiative 作为主入口是可运行的，而不是纸面架构；Task 内闭环与 formal Task 收口是可自动推进的，而不是人工串联的。

### 3.3 各版本依赖关系

版本依赖固定如下：

```text
R0 / MVP Alpha
  -> R1 / Beta
      -> R2 / v1.0
          -> R3 / v1.1
```

硬约束：

- 不允许跳过 R0 直接做 Milestone 自动收口
- 不允许在 R1 未稳定前推进 Initiative 级 `G3 / R3`
- R3 属于运维强化，不得反向阻塞 `v1.0`

## 4. 正交能力包矩阵

### 4.1 能力包总表

本专项将实现拆成五组正交能力包：

| 能力组 | 目标 | 典型 skills / 组件 |
| --- | --- | --- |
| 控制面 | 规划侧调度、规划输入准入、解析、重建、调度、恢复 | `run-planning`、`planning-loop`、`run-initiative`、`rebuild-runtime`、`select-frontier` |
| Task Core | Task 内执行与正式 Task 收口 | `task-loop`、`g1-task-gate`、`cut-anchor`、`r1-task-review` |
| Milestone Seal | PR 与阶段正式收口 | `open-milestone-pr`、`g2-milestone-gate`、`r2-milestone-review` |
| Initiative Seal | 交付候选与总体正式收口 | `g3-initiative-gate`、`r3-initiative-review` |
| Ops / Recovery | 运行事实补采、恢复、自动巡检 | `collect-runtime-facts`、`replay-runtime`、`shadow-monitor` |

### 4.2 版本与能力包映射

| 能力包 | R0 | R1 | R2 | R3 |
| --- | --- | --- | --- | --- |
| 控制面 | 全量必须 | 稳定化 | 稳定化 | 运维增强 |
| Task Core | 全量必须 | 稳定化 | 稳定化 | 运维增强 |
| Milestone Seal | 仅保留手动桥接 | 全量必须 | 稳定化 | 运维增强 |
| Initiative Seal | 不做 | 不做 | 全量必须 | 稳定化 |
| Ops / Recovery | 最小 resume | 基本可用 | 强化 | 全量必须 |

### 4.3 正交拆分原则

每个能力包都必须满足以下四条：

- 单一职责
- 输入输出清晰
- 可独立测试
- 不越权决定上层调度

例如：

- `g1-task-gate` 只负责当前实现轮的 G1 运行与结果整理，不负责宣布 Task `DONE`
- `g2-milestone-gate` 只负责 G2，不负责自动 merge PR
- `replay-runtime` 只负责恢复主状态，不负责推进下一 Task

## 5. 各版本详细定义

### 5.1 `R0 / MVP Alpha`：Initiative Task Core

**版本目标**

交付最小可运行主链：

```text
run_initiative
  -> planning admission check
  -> rebuild_runtime
  -> select_frontier
  -> select_ready_tasks
  -> task_loop
  -> G1
  -> anchor / fixup
  -> R1
```

这里的 planning admission check 只是 `run-initiative` 内部的一段执行侧 control plane 准入检查，不是独立 skill，也不是规划循环主链的最后一个 authoring 节点。

**这一版的用户承诺**

用户可以给出一份 Initiative 总任务文档，系统能够：

- 把它解析为 Initiative plan
- 重建当前 frontier
- 选择一个 ready 的写入型 Task
- 自动走完 `implement / repair -> G1 -> anchor / fixup -> R1`
- 在 Task `DONE` 后更新 runtime state

**必须具备的能力**

- `initiative_plan` parser / validator
- `initiative_state` / `milestone_state` / `task_state` 初版
- `gate_evidence_note(profile=G1)` 初版
- `run_task_loop()` 主闭环
- `task_worker`、`reviewer` 两角色接线
- 派生状态视图的基本生成与恢复

**明确非目标**

- 不做 G2 / R2 自动化
- 不做 G3 / R3
- 不做 milestone PR 自动开启
- 不做 automations
- 不做 readonly 并行 observer

**演示路径**

演示一个单 Milestone、单 write Task 的 Initiative，完成从启动到 `R1 clean` 的闭环。

**发布标准**

- 能稳定跑通至少一条真实 smoke path
- Task `DONE` 由结构化 artifacts 证明，不靠会话摘要
- 删除任意本地派生缓存后可重建主状态

### 5.2 `R1 / Beta`：Milestone Ready

**版本目标**

在 R0 基础上补齐 Milestone 正式收口：

```text
all tasks DONE in frontier
  -> open/update milestone PR
  -> G2
  -> R2
  -> milestone MERGED
```

**这一版的用户承诺**

系统能够把一个 Milestone 从内部 Task 完成态推进到阶段收口态，并给出明确 PR、G2、R2 结果。

**必须具备的能力**

- `milestone_state` 完整状态枚举
- milestone branch / PR 索引
- `review_brief / review_report` 在 R2 场景下可用
- `g2-milestone-gate`
- `r2-milestone-review`
- milestone merge 后 frontier 自动前移

**明确非目标**

- 不做 G3 / R3
- 不做 release / rollout candidate
- 不做 shadow automation

**演示路径**

演示一个双 Task 的 Milestone，从两个 Task 分别 `DONE` 到 `PR -> G2 -> R2 -> MERGED`。

**发布标准**

- frontier 可从已收口 Milestone 正确切换到下一个 Milestone
- R2 verdict 与 Milestone state 一致
- PR / G2 / R2 工件在重建后仍能恢复状态

### 5.3 `R2 / v1.0`：Initiative Ready

**版本目标**

在 R1 基础上补齐 Initiative 正式收口：

```text
all milestones MERGED
  -> build candidate
  -> G3
  -> R3
  -> initiative DONE
```

**这一版的用户承诺**

系统能够从 Initiative 主入口持续推进到最终交付候选与总体正式收口。

**必须具备的能力**

- `initiative_state` 完整状态枚举
- candidate 索引与 evidence bundle
- `g3-initiative-gate`
- `r3-initiative-review`
- replay / resume 可恢复到 Initiative 级断点

**明确非目标**

- 不做后台巡检自动化
- 不做多 worktree 写入并行
- 不做大规模只读并行分析

**演示路径**

演示一个包含两个 Milestone 的 Initiative，从启动一路推进到 `G3 / R3` 与 `DONE`。

**发布标准**

- Initiative `DONE` 必须具备 `latest_g3_ref` 与 `latest_r3_ref`
- 交付候选与 formal review 证据一致
- 从 crash / 重启恢复后能够回到正确 Initiative 级断点

### 5.4 `R3 / v1.1`：Operations Hardening

**版本目标**

补齐运维强化面，不改变对象法位：

- shadow automation
- readonly runtime observer
- worktree 隔离强化
- 恢复与诊断增强

**这一版的用户承诺**

系统在不改写主链法位的前提下，具备更稳定的长期运行能力。

**必须具备的能力**

- `collect-runtime-facts` 正式化
- `replay-runtime` 与 crash recovery 强化
- 可选 `shadow-monitor`
- 只读并行观测不污染主工作树

**明确非目标**

- 不做对象层升级
- 不做 formal gate / review 新法位
- 不做分布式任务编排

## 6. PR 序列与实施顺序

### 6.1 `R0 / MVP Alpha` 的 PR 序列

`PR-01`：技术模型入主线

- 目标：引入 `initiative_plan`、`initiative_state`、`milestone_state`、扩展版 `task_state`
- 依赖：前两篇文档封板
- 验收：模型与 schema 测试通过

`PR-02`：runtime rebuild 与 scheduler

- 目标：在 `run-initiative` 内部实现 planning admission check，并实现 `rebuild_initiative_state()`、`select_frontier()`、`select_ready_tasks()`
- 依赖：`PR-01`
- 验收：可从 plan 与现有 artifacts 重建 state

`PR-03`：Task loop 子状态机

- 目标：实现 `task_loop_phase` 与 `run_task_loop()` 主循环
- 依赖：`PR-02`
- 验收：mock 场景能走完 `implement -> spec -> quality`

`PR-04`：Task formal seal

- 目标：实现 `cut-anchor`、`G1`、`R1` 与 Task `DONE`
- 依赖：`PR-03`
- 验收：单 Task Initiative 能跑到 `DONE`

`PR-05`：Codex-native 接线与 smoke

- 目标：接入最小 skills / agents 并跑真实 smoke path
- 依赖：`PR-04`
- 验收：最小真实链路可跑通

### 6.2 `R1 / Beta` 的 PR 序列

`PR-06`：Milestone state 与 PR 索引

- 目标：补齐 `READY_FOR_PR / IN_G2 / IN_R2 / MERGED`
- 依赖：`R0` 发布
- 验收：Milestone 状态可由 Task `DONE` 推出

`PR-07`：G2 / R2 briefs、bundles 与 reports

- 目标：实现 milestone review brief、bundle、gate、review 落盘
- 依赖：`PR-06`
- 验收：Milestone seal 结构化结果完备

`PR-08`：frontier 前移与 Beta smoke

- 目标：Milestone merge 后自动推进下一个 frontier
- 依赖：`PR-07`
- 验收：双 Milestone 场景可跑通

### 6.3 `R2 / v1.0` 的 PR 序列

`PR-09`：Initiative candidate 与 G3 / R3

- 目标：实现 Initiative seal 主链
- 依赖：`R1` 发布
- 验收：Initiative 可到 `DONE`

`PR-10`：replay / resume 强化

- 目标：把恢复逻辑提升到 Initiative 级断点恢复
- 依赖：`PR-09`
- 验收：中断恢复不丢正式状态

`PR-11`：v1.0 验收与发布面整理

- 目标：统一 artifacts、报告输出、文档对齐、smoke path
- 依赖：`PR-10`
- 验收：达到 v1.0 发版线

### 6.4 `R3 / v1.1` 的 PR 序列

`PR-12`：runtime facts 与 readonly observer

- 目标：正式化运行事实补采与只读并行分析
- 依赖：`v1.0`
- 验收：不污染主工作树的只读观测可用

`PR-13`：shadow automation 与 worktree hardening

- 目标：补齐长期运行强化
- 依赖：`PR-12`
- 验收：巡检与隔离能力可演示

## 7. 验收线、断点与回退点

### 7.1 `R0 / MVP Alpha` 验收线

必须同时满足：

- Initiative 文档可 preflight
- runtime 可重建
- 单 Task 主链可跑到 `R1 clean`
- Task `DONE` 由结构化 artifacts 证明

回退点：

- 若真实 Codex 接线不稳，允许先保留 mock-first 主链并限制为内部 Alpha

### 7.2 `R1 / Beta` 验收线

必须同时满足：

- Milestone `READY_FOR_PR -> MERGED` 主链成立
- G2 / R2 工件完整
- frontier 可自动前移

回退点：

- 若 PR 接线不稳，允许保留手动开 PR，但 G2 / R2 工件链不能缺失

### 7.3 `R2 / v1.0` 验收线

必须同时满足：

- Initiative `ACTIVE -> DONE` 主链成立
- G3 / R3 工件完整
- replay / resume 达到可恢复发版断点的程度

回退点：

- 若 R3 接线不稳，不发布 v1.0，只维持 Beta

### 7.4 `R3 / v1.1` 验收线

必须同时满足：

- runtime facts 补采可用
- shadow automation 不影响 blocking 主链
- readonly 并行观测不污染主工作树

## 8. 风险、阻塞与降级策略

### 8.1 主要风险

- 旧四模型与新 runtime 对象层整合不当，导致双真值
- Task 内部检查与 formal review 边界写歪，导致状态机混乱
- 过早把 Milestone / Initiative seal 塞进第一版，导致 R0 失焦
- Codex-native 接线先于 deterministic 内核稳定，导致回归难以定位

### 8.2 主要阻塞点

- `review_result` 跨 R1 / R2 / R3 的统一抽象节奏
- `task_state` 向双层状态结构升级时的兼容策略
- `replay_or_resume_runtime()` 对各类 artifact 的索引规则

### 8.3 降级策略

若某版某条能力线不稳定，应采用以下降级原则：

- 优先推迟高层 seal，不回退对象层
- 优先保留 mock / contract path，不强推真实 smoke
- 优先保持 skills 正交拆分，不把多个失稳能力硬糊成一个 skill

## 9. 协作与审查机制

### 9.1 用户裁决点

固定裁决点如下：

- planning blocked
- frontier blocked
- Milestone `R2` 前
- Initiative `R3` 前
- 需要改写 sealed decision 时

### 9.2 审查原则

每个 PR 默认都要回答四件事：

- 它服务于哪个 release
- 它属于哪个 capability module
- 它的结构化合同是什么
- 它的回退点在哪里

### 9.3 smoke test 触发点

真实 Codex smoke test 只在以下断点触发：

- `R0` 末尾
- `R1` 末尾
- `R2` 末尾

R3 以运维演示和恢复演练为主，不再以新增主链 smoke 为中心。

## 10. 封板结论

本专项的最终推进方法固定为：

- 外层按 release 规划
- 中层按正交 capability module 拆分
- 内层按可审查 PR 序列落地

这意味着：

- **不把第一版做成大而全**
- **不把专项计划写成功能清单**
- **不把 skill 目录结构误当产品路线图**

本计划的正式裁决是：

> `R0 / MVP Alpha` 只证明 Initiative 主入口下的 Task Core 主链。  
> `R1 / Beta` 再补 Milestone Seal。  
> `R2 / v1.0` 再补 Initiative Seal。  
> `R3 / v1.1` 负责 Operations Hardening。
