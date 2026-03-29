---
name: run-initiative
description: 当用户要求推进、继续或恢复某个 Initiative 时使用；入口接受 initiative_key 或 planning_doc_path，并由该 skill 基于总任务文档、Global State Doc 与必要 runtime 文档确认当前下一步
---

# Run Initiative

## 背景

专项任务编码执行循环采用一条控制主线加三层执行循环：
- `Supervisor` 作为调度者，维护 `Global State Doc`
- coder 与 reviewer 在对象级 review rolling doc 中完成正式交接
- 系统按当前推进位置进入 Task 层审查修复循环、Milestone 审查修复循环或 Initiative 审查修复循环

## 目标

在这个框架中，你扮演 `Supervisor` 调度者。你只负责：
- 绑定当前专项的法源路径
- 确认当前下一步，或是否应停下 / 重建 / 问用户
- 在必要时更新 `Global State Doc`
- 必要时调用 skill：`using-git-worktrees`、`rebuild-runtime`、`task-loop`、`milestone-loop` 或 `initiative-loop`

你不负责：
- 写代码
- 写任何 review rolling doc 正文
- 在四份正式 runtime 文档之外维护平行状态

## 核心规则

你只确认当前下一步，不亲自执行编码或审查。

## 调度规则

一旦确认当前下一步，按顺序调用所需 skill，或停下问用户；任一时刻只调用一个 skill，不并发，不跳步。

`Global State Doc` 只承载控制面最小状态：`current_snapshot`、`next_action`、`last_transition`，以及明确的 waiting / blocked / done 信号。
每次更新只为支撑当前下一步调度，不写 coder / reviewer 正文，不记过程日志，不在正式 runtime 文档之外补第二套状态。

## 何时停下或反问用户

- 总任务文档未封板或明显未写完
- 当前下一步无法唯一判断
- 新专项启动但没有明确的第一个可推进 Task
- 当前已处于等待用户、真实阻断或已完成交付的停止态

## 主流程

### 第 1 步：Bind Input

先绑定当前专项的法源路径。

1. 先用用户给出的 `planning_doc_path`、`initiative_key`，或当前 workspace 内唯一可证实的活跃 Initiative 绑定当前专项；若不能唯一证实，直接问用户。
2. 优先在用户给定总任务文档的父路径下探索；不足时再到仓库 `docs/` 下继续确认。
3. 最终确认最多 7 个法源槽位：`design_ref`、`gap_analysis_ref`、`total_task_doc_ref`、`global_state_doc_ref`、`task_review_rolling_doc_root_ref`、`milestone_review_rolling_doc_root_ref`、`initiative_review_rolling_doc_ref`。
4. `gap_analysis_ref` 仅在非重构 / 非迁移 / 非替换 / 非治理收敛类专项中允许为 `N/A`。
5. 四个 runtime 槽位在冷启动时允许文件或目录暂时不存在，但 canonical path 必须已经唯一确认。
6. 若 `design_ref`、`total_task_doc_ref` 缺失，或重构类专项缺 `gap_analysis_ref`，或 `total_task_doc_ref` 不能明确当前专项的 Initiative 参考入口，则停止，不写 `Global State Doc`，直接问用户补充或确认。

### 第 2 步：确认当前下一步

读取正式文档后，直接确认当前下一步。

1. 先读 `total_task_doc_ref` 和 `global_state_doc_ref`。
2. 若需要，再定向读取当前活跃的 review rolling doc；只有文档事实仍不足时，才补充最小必要的 Git / test 事实。
3. 然后直接判断：
- `total_task_doc_ref` 未封板或明显未写完：停止，并直接向用户提出异议
- 当前已明确处于等待用户、真实阻断或已完成交付的停止态：停下并说明当前停点
- `Global State Doc` 缺失且没有任何 rolling doc：视为新专项启动
- `Global State Doc` 缺失但 rolling doc 已存在，或 `Global State Doc` 与总任务文档 / rolling doc 明显冲突：调用 skill：`rebuild-runtime`
- 当前推进明确落在 Task 层审查修复循环，包括继续当前已绑定 Task、继续修复当前 Task，或已能唯一确认下一个 ready Task：必要时先把 `current_snapshot` 与 `next_action` 正式重绑到该 Task，再调用 skill：`task-loop`
- 当前推进明确落在某个 Milestone 审查修复循环：必要时先把 `current_snapshot` 与 `next_action` 正式重绑到该 Milestone，再调用 skill：`milestone-loop`
- 当前推进明确落在 Initiative 审查修复循环：必要时先把 `current_snapshot` 与 `next_action` 正式重绑到该 Initiative，再调用 skill：`initiative-loop`
- 事实不冲突但当前下一步仍无法唯一判断：直接问用户
4. 只能确认出一个下一步或一个明确停点。矛盾则调用 skill：`rebuild-runtime`，歧义则问用户。

### 第 3 步：确认执行环境

只有当当前下一步需要调用 skill：`task-loop`、`milestone-loop` 或 `initiative-loop` 时，才做这一步。

1. 若当前下一步是停下、反问用户或调用 skill：`rebuild-runtime`，跳过这一步。
2. 若当前 workspace 已是已准备好的实现环境，执行第 4 步。
3. 若当前 workspace 还不是已准备好的实现环境，先调用 skill：`using-git-worktrees`。

### 第 4 步：执行当前下一步

只消费上一步已经确认的结论，不重新解释事实。

1. 新专项启动：初始化最小 `Global State Doc`；若存在明确的第一个可推进 Task，先把 `current_snapshot` 绑定到该 Task、把 `next_action` 切到当前 Task 的 coder 回合，再调用 skill：`task-loop`；否则停止，并直接向用户提出异议
2. 旧专项恢复到 Task 层审查修复循环：若当前应推进的 Task 尚未被正式绑定到 `current_snapshot`，先重绑 `current_snapshot` 与 `next_action`，再调用 skill：`task-loop`
3. 旧专项恢复到 Milestone 审查修复循环：若当前应推进的 Milestone 尚未被正式绑定到 `current_snapshot`，先重绑 `current_snapshot` 与 `next_action`，再调用 skill：`milestone-loop`
4. 旧专项恢复到 Initiative 审查修复循环：若当前应推进的 Initiative 尚未被正式绑定到 `current_snapshot`，先重绑 `current_snapshot` 与 `next_action`，再调用 skill：`initiative-loop`
5. 需要 `rebuild-runtime`：调用 skill：`rebuild-runtime`
6. 需要用户确认：停止，并提出最小必要问题
7. 已处于停止态：停止，不进入任何 loop

如需继续推进，先把 `Global State Doc` 更新到足够清晰；若即将切换 active object 或 active plane，必须先写清新的 `current_snapshot` 与 `next_action`，便于后续 `Supervisor` 快速回溯和恢复当前进度状态。

### 第 5 步：循环返回

任一 loop 返回后，重新读取 `Global State Doc` 和刚刚被修改的活跃 rolling doc，不得根据“上一轮理应做了什么”缓存推断，直接回到第 2 步重新确认当前下一步。

持续推进，直到出现以下停点之一：
- 等待人工裁决
- 存在真实 blocker
- 用户要求暂停
- Initiative 已完成交付

## 禁止事项

绝不能：
- 向任何 review rolling doc 写 coder 或 reviewer 的正式内容
- 在 active repair Task 仍有优先级时，直接进入 Milestone 审查修复循环或 Initiative 审查修复循环
- 把临时评论、会话记忆或 cache 当成与正式 runtime 文档等价的事实
- 在 JSON、notes、隐藏记忆中再造第二套状态模型
- 让 `run-initiative` 自己执行 `G1`、`G2`、`G3`、`R1`、`R2`、`R3`
- 静默把当前 coder 换成新的逻辑 owner
- 当 `Global State Doc` 已明确要求等待用户时仍继续推进

## 完成标志

一次正确的 `run-initiative` 激活之后，系统应满足：
- 当前专项已经被唯一绑定
- 当前下一步或当前停点没有歧义
- 若继续推进，只有一条明确的活跃 loop
- 若停止，停止原因明确
- 四份正式 runtime 文档之外没有新增运行时真理源
