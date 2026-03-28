---
name: task-loop
description: 当 `Global State Doc` 已唯一确认当前推进位置落在某个 ready 或 active Task 时使用；该 skill 以单一 coder ownership 推进当前 Task 的 `implement/repair -> G1 -> anchor/fixup -> fresh R1` 正式收口
---

# Task Loop

`task-loop` 只处理一个已确认的 Task。你在这里扮演 Task 层 `Supervisor`：维护最小控制面、维持单一 `coder_slot`、派发同一个 coder 与每轮 fresh `task-reviewer`，并根据 `G1`、`anchor / fixup`、`R1` 的事实决定继续修补、正式 clean、升级或停下。

`coder_slot` 是逻辑 owner 标识，不等于物理 `agent_id`；当前 `agent_id` 可以更换，但 `coder_slot` 不变。

不负责写代码、写 `r1_result`、改写 Milestone / Initiative 调度、结束开发分支或维护任何平行状态。

## 真理源与硬边界

正式输入面只有：Initiative 静态法源三件套 `design_ref`、`gap_analysis_ref`、`total_task_doc_ref`（其中 `gap_analysis_ref` 可按专项类型为 `N/A`）、`Global State Doc`、当前 `Task Review Rolling Doc`、必要的 Git / test / commit 事实。

硬边界：
- `G1` 只能由 coder 在当前实现轮执行，并写进 `Task Review Rolling Doc`
- 只有 `G1 pass` 后才允许写 `anchor_ref` 或 `fixup_ref`
- `R1` 只能由 fresh reviewer 针对正式锚点执行
- round 只有在 `r1_result` 写入后才闭合；`G1 fail` 仍在同一 round
- `Global State Doc` 只写 `current_snapshot`、`next_action`、`last_transition`
- 若只有 bounded task brief 且 rolling doc 不存在，可用它初始化 header 与 `task_contract_snapshot`；初始化后 rolling doc 成为唯一协作面

## 工作流

1. 绑定当前 Task
- 读取 Task 定义、`Global State Doc`、当前 `Task Review Rolling Doc` 与必要工程事实
- 确认当前 active task 唯一、workspace 可执行、rolling doc 与 active task 一致、`coder_slot` 唯一
- 若 `Global State Doc` 与 rolling doc 冲突，交回 `rebuild-runtime`
- 若当前 Task 不能唯一确认、合同缺失、事实显示应等待用户，则停止
- 若 rolling doc 不存在，仅初始化 header 与 `task_contract_snapshot`

2. 更新最小控制面
- `current_snapshot` 指向当前 active task 与 `coder_slot`
- `next_action` 指向继续当前 Task 的 coder 回合
- 必要时在 `last_transition` 记录进入当前 round、恢复当前 round 或 coder 继任
- 不要把实现细节、review 主文、测试全文写进 `Global State Doc`

3. 派发 coder
- 对当前 Task 只保留一个逻辑 `coder_slot`
- 物理 thread 存活时复用当前 `agent_id`；丢失时可派继任 `agent_id`，但必须复用原 `coder_slot` 并记录继任关系
- 默认 `fork_context=false`
- 派给 coder 的输入只需要定位当前正式输入面：当前 Task 身份、`design_ref`、`gap_analysis_ref`、`total_task_doc_ref`、`Global State Doc` 路径、当前 `Task Review Rolling Doc` 路径；若 rolling doc 尚未存在，可附 bounded brief 仅用于初始化 `task_contract_snapshot`
- coder 完成工作后会按照约定返回结果到 `Task Review Rolling Doc`

4. 处理 coder 结果
- 只按 rolling doc 与 Git 事实判断，不按聊天总结判断
- 最新 `g1_result=fail`，或只有 `coder_update`：同一个 coder 在同一 round 继续
- `g1_result=pass` 但没有合法 `anchor_ref/fixup_ref`：退回同一个 coder 补齐正式锚点
- `g1_result=pass` 且已有合法锚点：把 `next_action` 切到进入 `R1`
- coder 请求更多上下文、人工裁决或暴露真实 blocker：在 `Global State Doc` 写明 waiting/blocked，然后停止

5. 派发 fresh `task-reviewer`
- 每轮 `R1` 都 fresh 派生 reviewer，默认 `fork_context=false`
- reviewer 读取 `design_ref`、`gap_analysis_ref`、`total_task_doc_ref`、`Global State Doc`、当前 `Task Review Rolling Doc`、当前 `anchor/fixup` 与必要 spec refs
- reviewer 会按照约定返回结果到 `Task Review Rolling Doc`

6. 处理 `r1_result`
- `R1 clean`：更新 `last_transition`，把 `next_action` 切到 `task_done` 或“选择下一个 ready object”，然后交回上游
- `R1 changes_requested` 且仍在 Task 半径内：把 `next_action` 切到继续当前 Task repair，同一个 `coder_slot` 进入下一 round
- `R1` 要求升级、等待用户或存在真实阻断：reviewer 只写建议，`Supervisor` 只更新 `Global State Doc`，然后交回上游

## 停止条件

直接停止并交回上游或用户：
- active task 不能唯一确认
- Task 合同缺失、必要 spec refs 缺失，或 `Global State Doc` 与 rolling doc 冲突
- workspace 不是可执行实现环境，或当前事实显示应等待用户
- 当前问题明显超出 Task 半径，需要升级到 Milestone
- coder 或 reviewer 暴露真实 blocker

## 红线

绝不能：
- 在 `G1 pass` 之前 cut `anchor / fixup`
- 在没有正式锚点时进入 `R1`
- 把 `G1 fail` 当成一个 round 已闭合
- 静默更换逻辑 `coder_slot`
- 把 bounded brief 长期保留成第二套协作真理源
- 在 `Global State Doc` 里写 coder / reviewer 正文
- 对同一个 Task 并发派发多个 coder
- 让 reviewer 修代码
- 跳过 `G1 -> anchor / fixup -> R1`
- 在 Task 仍有 active repair 时擅自切去 Milestone / Initiative 收口
- 在没有 `r1_result: clean` 的情况下宣称 Task done

## 完成标志

正确结束时，应满足：
- 当前 Task 状态可由 `Global State Doc` 与 `Task Review Rolling Doc` 唯一恢复
- `coder_slot` 连续性没有歧义
- 若 Task clean，rolling doc 中已存在合法的 `g1_result`、`anchor/fixup` 与 `r1_result`
- 四份正式 runtime 文档之外没有新增第二套运行时真理源
