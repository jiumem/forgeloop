---
name: rebuild-runtime
description: 当 runtime 控制面缺失、冲突或无法唯一恢复当前下一步时使用；该 skill 读取静态法源、Global State Doc、review rolling docs 与必要 Git facts，重建最小可继续调度的控制面
---

# Rebuild Runtime

`rebuild-runtime` 只做恢复，不做编码、不做审查、不替代 `run-initiative` 继续调度。你在这里扮演恢复态 `Supervisor`：从正式法源和工程事实重建最小 runnable control plane，并把系统交回上游。

## 真理源与硬边界

正式输入面只有：Initiative 静态法源三件套 `design_ref`、`gap_analysis_ref`、`total_task_doc_ref`（其中 `gap_analysis_ref` 可按专项类型为 `N/A`）、`Global State Doc`、三层 review rolling docs、必要的 Git / PR / commit / test 事实。

硬边界：
- 只恢复逻辑 `coder_slot`，不恢复物理 `agent_id`
- 只在必要时写 `Global State Doc`
- 若 `Global State Doc` 不存在，可初始化 `global_state_header`
- 若现有 `global_state_header` 与静态法源绑定冲突，可先修正 `global_state_header`
- 可更新的块只有 `global_state_header`、`current_snapshot`、`next_action`、`last_transition`
- 不写任何 rolling doc 正文
- 不改静态法源，不造 JSON / notes / hidden memory 第二套状态

## 何时触发

只在以下场景触发：
- `Global State Doc` 缺失，但已有 rolling docs
- `Global State Doc` 与总任务文档或 rolling docs 明显冲突
- `task-loop`、`milestone-loop`、`initiative-loop` 在绑定对象时发现控制面无法唯一恢复
- 原 thread 不可继续，但正式文档与 Git 事实仍足以恢复

以下场景不由本 skill 处理：
- 新专项冷启动，且没有任何 runtime 文档
- 只是需要实现环境，应交给 `using-git-worktrees`
- 当前下一步已经清楚，无需恢复

## 工作流

1. 绑定恢复面
- 读取 `total_task_doc_ref`、现有 `Global State Doc` 与三层 rolling docs
- 若静态法源缺失，或 Initiative 绑定不能唯一确认，直接停止并问用户
- 若没有任何 rolling doc 且没有 `Global State Doc`，判定为 cold start，交回上游，不写运行时状态

2. 确认当前 formal frontier
- 优先尊重与更新较新的正式事实一致的 waiting / blocked / done 信号
- 否则，以最新且尚未闭合的正式 frontier 为 active 候选
- 多个候选并存时，优先级固定为：active Task repair / coder round > active Milestone review / repair > active Initiative review / repair > frontier selection after last clean object
- 聊天总结、缓存和会话记忆都不参与裁决

3. 判定 active object 与 next action
- `coder_slot` 恢复规则：
  - 若现有 `Global State Doc` 中的 `current_snapshot.coder_slot` 仍与最新正式事实一致，直接复用
  - 若 `Global State Doc` 缺失或失真，则从被判定为 active 的 rolling doc header 恢复 `coder_slot`
  - 若 active rolling doc header 缺少 `coder_slot`，或多个候选给出互相冲突的 `coder_slot`，直接停止并问用户
- Task 候选：
  - 只有 `coder_update`，或最新 `g1_result=fail`：继续当前 Task coder 回合
  - `g1_result=pass` 且已有合法 `anchor/fixup` 但没有 `r1_result`：进入 `R1`
  - `r1_result=changes_requested`：继续当前 Task repair
  - `r1_result=clean`：进入 `task_done` 或 `select_next_ready_object`
- Milestone 候选：
  - `g2_result=repair_required` 或 `r2_result=changes_requested` 且仍在当前 Milestone 半径内：继续当前 Milestone repair
  - 若 repair task 已被正式对象化：active plane 回到 Task
  - `g2_result=pass` 且没有 `r2_result`：进入 `R2`
  - `r2_result=clean`：进入 frontier selection 或 Initiative review entry
- Initiative 候选：
  - `g3_result=repair_required` 或 `r3_result=changes_requested` 且仍在当前 Initiative 半径内：继续当前 Initiative repair
  - 若 repair task 已被正式对象化：active plane 回到 Task
  - `g3_result=pass` 且没有 `r3_result`：进入 `R3`
  - `r3_result=clean`：进入 Initiative done / delivery complete
- 若 active plane、active object 或 next action 仍无法唯一判定，直接停止并问用户

4. 重写最小控制面
- 若 `Global State Doc` 不存在，先初始化 `global_state_header`
- 若现有 `global_state_header` 与 Initiative 绑定或 planning doc ref 冲突，先修正 `global_state_header`
- 将 `current_snapshot` 写成唯一恢复出的 active plane / active object / `coder_slot`
- 将 `next_action` 写成唯一恢复出的下一步
- 将 `last_transition` 写成一次 recovery transition，说明为何重建控制面
- 写完后立即交回 `run-initiative`，由上游重新确认并继续调度

## 停止条件

直接停止并交回上游或用户：
- Initiative 绑定或静态法源无法唯一确认
- 多个 active 候选并存且 Git / 正式文档仍不能打破平局
- rolling docs 彼此冲突，无法判定哪一侧更新
- 没有 runtime 文档，应按 cold start 处理
- 事实显示应等待用户，但等待原因无法被正式说明

## 红线

绝不能：
- 写 rolling doc 正文
- 恢复物理 owner / thread id 作为正式状态
- 把过时的 `Global State Doc` 压过更新的 rolling doc 事实
- 把聊天记忆、缓存或本地派生提示当成正式真理源
- 静默猜测 active object、`coder_slot` 或 next action

## 完成标志

正确结束时，应满足：
- 当前 active plane、active object 与 `coder_slot` 已可唯一恢复
- `Global State Doc` 已存在，且 `current_snapshot`、`next_action`、`last_transition` 自洽
- 上游可重新进入 `run-initiative` 继续调度，而不依赖隐藏上下文
- 四份正式 runtime 文档之外没有新增第二套运行时真理源
