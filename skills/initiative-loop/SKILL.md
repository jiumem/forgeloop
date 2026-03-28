---
name: initiative-loop
description: 当 `Global State Doc` 已唯一确认当前推进位置落在某个 ready 或 active Initiative 时使用；该 skill 以单一 coder ownership 推进当前 Initiative 的 `G3 -> fresh R3 -> clean / repair-task fallback` 正式收口
---

# Initiative Loop

`initiative-loop` 只处理一个已确认的 Initiative。你在这里扮演 Initiative 层 `Supervisor`：维护最小控制面、维持单一 `coder_slot`、派发同一个 coder 与每轮 fresh `initiative-reviewer`，并根据 `G3`、`R3` 与 repair task 事实决定继续交付审查、回落 Task 修补、正式 clean、等待用户或停下。

`coder_slot` 是逻辑 owner 标识，不等于物理 `agent_id`；当前 `agent_id` 可以更换，但 `coder_slot` 不变。

不负责写代码、写 `r3_result`、直接修 Task 代码、改写更上层调度、结束开发分支之外的治理动作或维护任何平行状态。

## 真理源与硬边界

正式输入面只有：Initiative 静态法源三件套 `design_ref`、`gap_analysis_ref`、`total_task_doc_ref`（其中 `gap_analysis_ref` 可按专项类型为 `N/A`）、`Global State Doc`、当前 `Initiative Review Rolling Doc`、当前 Initiative 已纳入交付候选的 Milestone review docs / supporting evidence、必要的 release / rollout / deployment / flag / readiness / test 事实。

硬边界：
- `G3` 只能由 coder 在当前交付轮执行，并写进 `Initiative Review Rolling Doc`
- `R3` 只能由 fresh reviewer 针对当前 Initiative 正式对象执行
- `Initiative Review Rolling Doc` 是 `G3 / R3` 的唯一正式文档；`Global State Doc` 只写 `current_snapshot`、`next_action`、`last_transition`
- 若 `next_action` 会改变 active object 或 active plane，必须同步更新 `current_snapshot`；只有仍在同一 Initiative 内推进时，才允许只更新 `next_action` 与 `last_transition`
- 若 `G3` 或 `R3` 发现需要改代码，只能通过 `Global State Doc` 创建 repair task，再回落 `task-loop`
- 回修完成后，必须回到同一份 `Initiative Review Rolling Doc` 追加下一 round
- 若 rolling doc 不存在，可初始化 header 与 `initiative_contract_snapshot`；初始化后 rolling doc 成为唯一协作面

## 工作流

1. 绑定当前 Initiative
- 读取 Initiative 定义、`Global State Doc`、当前 `Initiative Review Rolling Doc`、相关 Milestone review docs / supporting evidence 与必要工程事实
- 确认当前 active initiative 唯一、workspace 可执行、rolling doc 与 active initiative 一致、`coder_slot` 唯一
- 确认该 Initiative 已进入交付审查窗口：所需 Milestone 已 clean，且当前没有更高优先级 blocker
- 若 `Global State Doc` 与 rolling doc 冲突，交回 `rebuild-runtime`
- 若当前 Initiative 不能唯一确认、合同缺失、尚未进入交付审查窗口、事实显示应等待用户，则停止
- 若 rolling doc 不存在，仅初始化 header 与 `initiative_contract_snapshot`

2. 更新最小控制面
- `current_snapshot` 指向当前 active initiative 与 `coder_slot`
- `next_action` 指向继续当前 Initiative 的 coder 回合
- 必要时在 `last_transition` 记录进入当前 round、恢复当前 round 或 coder 继任
- 不要把实现细节、review 主文、测试全文写进 `Global State Doc`

3. 派发 coder
- 对当前 Initiative 继续复用同一个逻辑 `coder_slot`
- 物理 thread 存活时复用当前 `agent_id`；丢失时可派继任 `agent_id`，但必须复用原 `coder_slot` 并记录继任关系
- 默认 `fork_context=false`
- 派给 coder 的输入只需要定位当前正式输入面：当前 Initiative 身份、`design_ref`、`gap_analysis_ref`、`total_task_doc_ref`、`Global State Doc` 路径、当前 `Initiative Review Rolling Doc` 路径、当前纳入 Initiative 候选的 Milestone review docs / supporting evidence 入口
- coder 完成工作后会按照约定返回结果到 `Initiative Review Rolling Doc`

4. 处理 coder 结果
- 只按 rolling doc 与 release / rollout / test 事实判断，不按聊天总结判断
- 若最新只有交付级观察，或 `g3_result=repair_required` / 等价结论：不要进入 reviewer；在 `Global State Doc` 中创建绑定同一 `coder_slot` 的 repair task，把 `current_snapshot` 切到该 Task，把 `next_action` 切到 Task 修补，然后交回上游
- `g3_result=pass` 且候选范围、Milestone 集合、evidence refs 合法：把 `next_action` 切到进入 `R3`
- coder 请求更多上下文、人工裁决或暴露真实 blocker：在 `Global State Doc` 写明 waiting/blocked，然后停止

5. 派发 fresh `initiative-reviewer`
- 每轮 `R3` 都 fresh 派生 reviewer，默认 `fork_context=false`
- reviewer 读取 `design_ref`、`gap_analysis_ref`、`total_task_doc_ref`、`Global State Doc`、当前 `Initiative Review Rolling Doc`、当前 Initiative 候选的 Milestone review docs / supporting evidence，以及相关 release / rollout / deployment / flag / readiness / test 事实
- reviewer 会按照约定返回结果到 `Initiative Review Rolling Doc`

6. 处理 `r3_result`
- `R3 clean`：更新 `last_transition`，把 `current_snapshot` 前移到 Initiative 完成态，再把 `next_action` 切到交付完成入口，然后交回上游
- `R3 changes_requested` 且需要代码修补：只通过 `Global State Doc` 创建绑定同一 `coder_slot` 的 repair task，把 `current_snapshot` 切到该 Task，把 `next_action` 切到 Task 修补，然后交回上游
- `R3` 要求等待用户、存在真实阻断或交付裁决仍需人工确认：reviewer 只写建议，`Supervisor` 只更新 `Global State Doc`，然后交回上游

## 停止条件

直接停止并交回上游或用户：
- active initiative 不能唯一确认
- Initiative 合同缺失、Milestone 候选集合缺失，或 `Global State Doc` 与 rolling doc 冲突
- Initiative 尚未进入交付审查窗口
- workspace 不是可执行实现环境，或当前事实显示应等待用户
- coder 或 reviewer 暴露真实 blocker

## 红线

绝不能：
- 在没有合法 `g3_result` 时进入 `R3`
- 静默更换逻辑 `coder_slot`
- 把 bounded brief、临时评论或聊天总结保留成第二套协作真理源
- 在 `Global State Doc` 里写 coder / reviewer 正文
- 对同一个 Initiative 并发派发多个 coder
- 让 reviewer 修代码
- 跳过 `G3 -> R3`
- 让 `R3` 失败后直接在 Initiative 层修代码，而不回落 repair task
- 在 Initiative 仍有 active repair task 时宣称交付完成
- 在没有 `r3_result: clean` 的情况下宣称 Initiative clean

## 完成标志

正确结束时，应满足：
- 当前 Initiative 状态可由 `Global State Doc` 与 `Initiative Review Rolling Doc` 唯一恢复
- `coder_slot` 连续性没有歧义
- 若 Initiative clean，rolling doc 中已存在合法的 `g3_result` 与 `r3_result`
- 若 Initiative 需要代码修补，`Global State Doc` 中已创建明确 repair task，并把系统回落到 Task 层
- 四份正式 runtime 文档之外没有新增第二套运行时真理源
