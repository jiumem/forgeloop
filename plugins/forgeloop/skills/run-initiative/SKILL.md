---
name: run-initiative
description: 从正式 Tracker Spec 或持久化多 Spec Initiative 串行运行 Tickets，编排独立 Coder、Spec Reviewer 与 Standards Reviewer，执行修复、集成、恢复和最终验收门禁。仅在用户明确要求执行、继续、恢复或取消正式 Initiative 时使用；没有正式引用或只有旧 PLAN.md 时停止。
---

# 运行 Initiative

把配置的 Issue Tracker 作为 Spec、Ticket、依赖和运行状态的唯一真理源。当前主上下文是 Scheduler；每张 Ticket 创建一个新 Coder 和两个相互隔离的 Reviewer，同一 Ticket 的修复轮次复用三者，完成后结束三者。

## 读取协议

开始前读取全部一层 References：

- [domain-and-state.md](references/domain-and-state.md)：领域模型、真理源和状态不变量。
- [scheduler.md](references/scheduler.md)：入口、Frontier、Claim、串行调度和 Agent 生命周期。
- [coder.md](references/coder.md)：Coder 输入、权限、四种结果和证据。
- [reviewers.md](references/reviewers.md)：双轴隔离、结构化 Verdict 与模型路由。
- [events-and-recovery.md](references/events-and-recovery.md)：追加式 Event、幂等、冲突与崩溃恢复。
- [repair-and-integration.md](references/repair-and-integration.md)：修复预算、Branch、冲突和 Integration Policy。
- [acceptance.md](references/acceptance.md)：Ticket、Spec、Initiative 完成门禁与 Spec 修订。
- [tracker-operations.md](references/tracker-operations.md)：GitHub、GitLab、Local Runtime 路由和失败边界。

不得只读主文件后自行补全协议。

## 入口门禁

接受：

- `run-initiative <spec-ref>`：单 Spec，Spec 本身是运行根；
- `run-initiative <initiative-ref>`：恢复持久化多 Spec Initiative；
- `run-initiative <spec-ref...>`：多 Spec，先预览成员、跨 Spec 约束与目标分支，用户确认后创建父 Item。

开始任何写入前：

1. 读取仓库指令、`docs/agents/issue-tracker.md`、Domain 配置、相关 `CONTEXT.md`/ADR。
2. 确认 Tracker 类型、认证、权限、Integration Policy、正式引用、Spec Revision、目标分支与仓库状态。
3. 缺少正式 Spec、配置、策略、权限或 Reviewer 能力时停止并给出可恢复诊断；不得回退到另一 Tracker。
4. 输入旧 `PLAN.md`/`LEDGER.md` 时只提供迁移或固定 `2.5.0` 的选择，不按新语义解释。
5. 脏工作区与候选 Branch 冲突时停止；不覆盖用户改动。

## 主循环

1. 创建或恢复唯一 Scheduler Run，校验原生 Tracker 事实与追加 Events 一致。
2. 重新查询 Frontier。空 Frontier 时区分：全部完成、仍被阻塞、已被领取、坏依赖或状态冲突。
3. 以 Tracker 的确定性 Claim 规则领取一张 Ticket。Claim 失败不得创建 Coder。
4. 创建新 Coder，提供封板输入；Coder 负责实现、相关验证和候选 Commit。
5. `IMPLEMENTATION_BLOCKED` 直接暂停；`CONTRACT_BLOCKER` 进入合约路径；其余结果创建相互独立的 Spec 与 Standards Reviewer。
6. 两名 Reviewer 针对同一 Base/Head 独立签发 Verdict。Scheduler 只校验绑定关系，不重复运行测试或额外触发完整 CI。
7. 任一 `REPAIR_REQUIRED` 按修复协议返回原 Coder；代码变化使两份旧 Verdict 同时失效，并让两轴对新累计 Diff 重审。
8. 双 `PASS` 且 Head/Base 未变化后按 Integration Policy 集成；`human-merge` 进入可恢复等待态。
9. 通过 Ticket 门禁后记录结果并关闭 Ticket；随后重新查询 Frontier，不复用旧快照。
10. 所有 Tickets 完成后执行 Spec 最终验收；多 Spec 再执行全新 Initiative Acceptance。

## 可观察终态

- `COMPLETED`：所有对应层级 Acceptance 均 PASS，最终 Commit 已集成并最后关闭根 Item。
- `PAUSED`：修复预算耗尽、人工合并、Reviewer 不可用、状态冲突或外部阻塞；根 Item 保持 Open，可沿原 Run ID 恢复。
- `CONTRACT_BLOCKER`：Spec/ADR/Scope 冲突，需要用户裁决，不消耗普通修复预算。
- `CANCELLED`：记录取消 Event，与完成严格区分；不关闭为成功。
- `FAILED_PRECONDITION`：入口、配置、认证、权限、引用或工作区失败，任何候选 Agent 均未启动。

不得创建或更新 `PLAN.md`、`LEDGER.md`、互斥执行状态标签；禁止让 Coder 自批、自合并、自关闭；禁止把 Reviewer PASS 或关闭但未合并的 PR/MR 当作完成。
