# 领域与状态契约

## 领域对象

- **Initiative**：一次用户授权范围。单 Spec 不创建额外父对象；多 Spec 必须持久化父 Tracker Item。
- **Spec**：完整交付合约，记录当前 Revision、目标分支、Scope 与 Acceptance Criteria。
- **Ticket**：可在新鲜上下文中完成并通过公共 Seam 验证的最小垂直切片。
- **Frontier**：授权范围内所有 Open、Unblocked、Unclaimed Tickets。
- **Agent Run**：一张 Ticket 的 Coder、双 Reviewer、候选实现、证据和修复历史。
- **Review Verdict**：明确绑定 Base/Head 和 Spec Revision 的单轴 `PASS` 或 `REPAIR_REQUIRED`。

## 唯一真理源

- 术语：`CONTEXT.md`；长期决定：ADR。
- Spec、Ticket、成员关系、阻塞、讨论与实时状态：配置的 Tracker。
- 候选实现与集成：Branch、Commit、PR/MR 和 Git 事实。
- 可执行行为：代码与测试。
- 临时续接：OS 临时目录 Handoff。

追加 Events 解释 Agent Run，但不覆盖 Tracker 原生 Open/Closed、Dependencies、Assignee/Claim、Commit 与 Merge 事实。二者冲突时停止恢复，不选择更方便的一方。

## 状态不变量

1. 一个 Initiative 同时最多一张活动 Ticket、一个有效 Scheduler Run。
2. 每张 Ticket 独立 Coder 与两名独立 Reviewer；跨 Ticket 不复用上下文。
3. 同一 Ticket 修复复用原三者；Reviewer 不读另一轴结论。
4. Coder 验证，Reviewer 审查，Scheduler 编排；职责不重复。
5. 代码、Base、Head、Spec Revision 或最终目标变化会使相关 Verdict 失效。
6. Ticket Close 只能发生在实现集成后；Spec/Initiative Close 只能发生在对应 Acceptance PASS 后。
7. `PAUSED` 保持 Open；`CANCELLED` 不伪装 `COMPLETED`。

## 禁止的第二真理源

不创建 `PLAN.md`、`LEDGER.md` 或 `CODING/REVIEW/REPAIR` 执行标签，不把 Tracker 状态复制进仓库文件。Local Markdown 本身是正式 Tracker，不是镜像。
