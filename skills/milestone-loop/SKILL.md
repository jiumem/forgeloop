---
name: milestone-loop
description: 当 `Global State Doc` 已唯一确认当前推进位置落在某个 ready 或 active Milestone 时使用；该 skill 以单一 coder ownership 推进当前 Milestone 的 `review/repair -> G2 -> fresh R2` 正式收口
---

# Milestone Loop

`milestone-loop` 只处理一个已确认的 Milestone。你在这里扮演 Milestone 层 `Supervisor`：维护最小控制面、维持单一 `coder_slot`、派发同一个 `coder` 与每轮 fresh `milestone_reviewer`，并根据 `G2`、`R2` 与必要时对象化的 repair task 事实决定继续阶段审查、当前层修补、正式 clean、升级或停下。

`coder_slot` 是逻辑 owner 标识，不等于物理 `agent_id`；当前 `agent_id` 可以更换，但 `coder_slot` 不变。

不负责写代码、写 `r2_result`、直接修 Task 代码、改写 Initiative 层调度、结束开发分支或维护任何平行状态。

## 真理源与硬边界

正式输入面只有：Initiative 静态法源三件套 `design_ref`、`gap_analysis_ref`、`total_task_doc_ref`（其中 `gap_analysis_ref` 可按专项类型为 `N/A`）、`Global State Doc`、当前 `Milestone Review Rolling Doc`、当前 Milestone 已纳入审查的 Task anchors / Task review docs、必要的 Git / PR / merge-base / test 事实。

硬边界：
- `G2` 只能由 coder 在当前阶段轮执行，并写进 `Milestone Review Rolling Doc`
- `R2` 只能由 fresh reviewer 针对当前 Milestone 正式对象执行
- `Milestone Review Rolling Doc` 是 `G2 / R2` 的唯一正式文档；`Global State Doc` 只写 `current_snapshot`、`next_action`、`last_transition`
- 若 `next_action` 会改变 active object 或 active plane，必须同步更新 `current_snapshot`；只有仍在同一 Milestone 内推进时，才允许只更新 `next_action` 与 `last_transition`
- 若 `G2` 或 `R2` 发现代码问题，默认由同一 `coder_slot` 在当前 Milestone 内继续修补并重跑 `G2`；只有修补需要独立 Task 合同、明确新对象边界或明显超出当前 Milestone 收口半径时，才通过 `Global State Doc` 对象化为 repair task，再回落 `task-loop`
- 若已对象化为 repair task，回修完成后，必须回到同一份 `Milestone Review Rolling Doc` 追加下一 round
- 若 rolling doc 不存在，可初始化 header（含对象身份与 `coder_slot`）与 `milestone_contract_snapshot`；初始化后 rolling doc 成为唯一协作面

## 工作流

1. 绑定当前 Milestone
- 读取 Milestone 定义、`Global State Doc`、当前 `Milestone Review Rolling Doc`、相关 Task anchors / Task review docs 与必要工程事实
- 确认当前 active milestone 唯一、workspace 可执行、rolling doc 与 active milestone 一致、`coder_slot` 唯一
- 确认该 Milestone 已进入阶段审查窗口：所需 Task 已 `DONE`，且当前没有更高优先级 blocker
- 若 `Global State Doc` 与 rolling doc 冲突，交回 `rebuild-runtime`
- 若当前 Milestone 不能唯一确认、合同缺失、尚未进入阶段审查窗口、事实显示应等待用户，则停止
- 若 rolling doc 不存在，仅初始化 header（含对象身份与 `coder_slot`）与 `milestone_contract_snapshot`

2. 更新最小控制面
- `current_snapshot` 指向当前 active milestone 与 `coder_slot`
- `next_action` 指向继续当前 Milestone 的 coder 回合
- 必要时在 `last_transition` 记录进入当前 round、恢复当前 round 或 coder 继任
- 不要把实现细节、review 主文、测试全文写进 `Global State Doc`

3. 派发 coder
- 对当前 Milestone 继续复用同一个逻辑 `coder_slot`
- 物理 thread 存活时复用当前 `agent_id`；丢失时可派继任 `agent_id`，但必须复用原 `coder_slot` 并记录继任关系
- 默认 `fork_context=false`
- 派给 coder 的输入只需要定位当前正式输入面：当前 Milestone 身份、`design_ref`、`gap_analysis_ref`、`total_task_doc_ref`、`Global State Doc` 路径、当前 `Milestone Review Rolling Doc` 路径、当前纳入 Milestone 的 Task anchors / Task review docs 入口
- coder 完成工作后会按照约定返回结果到 `Milestone Review Rolling Doc`

4. 处理 coder 结果
- 只按 rolling doc 与 Git / PR 事实判断，不按聊天总结判断
- 若最新只有阶段级观察，或 `g2_result=repair_required` / 等价结论且仍在当前 Milestone 半径内：不要进入 reviewer；同一个 `coder_slot` 继续当前 Milestone 修补并重跑 `G2`
- 若 `g2_result=repair_required` / 等价结论且已需要独立 Task 合同、明确新对象边界或明显超出当前 Milestone 收口半径：在 `Global State Doc` 中创建绑定同一 `coder_slot` 的 repair task，把 `current_snapshot` 切到该 Task，把 `next_action` 切到 Task 修补，然后交回上游
- `g2_result=pass` 且对象范围、anchor 集合、evidence refs 合法：把 `next_action` 切到进入 `R2`
- coder 请求更多上下文、人工裁决或暴露真实 blocker：在 `Global State Doc` 写明 waiting/blocked，然后停止

5. 派发 fresh `milestone_reviewer`
- 每轮 `R2` 都 fresh 派生 reviewer，默认 `fork_context=false`
- reviewer 读取 `design_ref`、`gap_analysis_ref`、`total_task_doc_ref`、`Global State Doc`、当前 `Milestone Review Rolling Doc`、当前 Milestone anchor 集合、必要 Task review docs 与相关 PR / merge-base / test 事实
- reviewer 会按照约定返回结果到 `Milestone Review Rolling Doc`

6. 处理 `r2_result`
- `R2 clean`：更新 `last_transition`，把 `current_snapshot` 前移到“下一 frontier 选择”或更上层审查入口，再把 `next_action` 切到对应入口，然后交回上游
- `R2 changes_requested` 且仍在当前 Milestone 收口半径内：把 `next_action` 切到继续当前 Milestone repair，同一个 `coder_slot` 进入下一 round
- `R2 changes_requested` 且已需要独立 Task 合同、明确新对象边界或明显超出当前 Milestone 收口半径：只通过 `Global State Doc` 创建绑定同一 `coder_slot` 的 repair task，把 `current_snapshot` 切到该 Task，把 `next_action` 切到 Task 修补，然后交回上游
- `R2` 要求升级、等待用户或存在真实阻断：reviewer 只写建议，`Supervisor` 只更新 `Global State Doc`，然后交回上游

## 停止条件

直接停止并交回上游或用户：
- active milestone 不能唯一确认
- Milestone 合同缺失、anchor 集合缺失，或 `Global State Doc` 与 rolling doc 冲突
- Milestone 尚未进入阶段审查窗口
- workspace 不是可执行实现环境，或当前事实显示应等待用户
- 当前问题明显超出 Milestone 半径，需要升级到 Initiative
- coder 或 reviewer 暴露真实 blocker

## 红线

绝不能：
- 在没有合法 `g2_result` 时进入 `R2`
- 静默更换逻辑 `coder_slot`
- 把 bounded brief、临时评论或聊天总结保留成第二套协作真理源
- 在 `Global State Doc` 里写 coder / reviewer 正文
- 对同一个 Milestone 并发派发多个 coder
- 让 reviewer 修代码
- 跳过 `G2 -> R2`
- 把仍可在当前 Milestone 收口的修补强行拆成 repair task
- 在需要对象化 repair task 时仍强行留在 Milestone 层硬修
- 在 Milestone 仍有 active repair task 时擅自切去 Initiative 收口
- 在没有 `r2_result: clean` 的情况下宣称 Milestone clean

## 完成标志

正确结束时，应满足：
- 当前 Milestone 状态可由 `Global State Doc` 与 `Milestone Review Rolling Doc` 唯一恢复
- `coder_slot` 连续性没有歧义
- 若 Milestone clean，rolling doc 中已存在合法的 `g2_result` 与 `r2_result`
- 若 Milestone 尚未 clean，系统要么清楚停在当前 Milestone repair，要么已在必要时对象化为明确 repair task 并回落 Task 层
- 四份正式 runtime 文档之外没有新增第二套运行时真理源
