# 修复、Branch 与集成协议

## 修复循环

任一轴 `REPAIR_REQUIRED` 都返回原 Coder，并同时传递两轴 Findings。两个旧 Verdict 在代码变化后失效；两名原 Reviewer 对新 Head 的完整累计 Diff 重新签发。

- 首次失败提升相关轴推理强度；重复失败升至最高能力。
- 同一 Finding 经两次修复仍存在，追加 `RUN_PAUSED`。
- 同一 Ticket 累计三次评审失败，追加 `RUN_PAUSED`。
- 两轴要求冲突、合约不可实现、Scope 不足或需要改 Spec/ADR 时转 `CONTRACT_BLOCKER`，不消耗普通修复预算。
- 用户可修改合约或记录正式例外，但不能把 `REPAIR_REQUIRED` 改写为 PASS。

## Branch 策略

默认每 Ticket 独立 Branch。只有 Ticket Graph 预先声明 Wide Refactor、不可独立绿色迁移或原子交付时共享 Spec Integration Branch；共享模式必须有最终 `integrate-and-verify` Ticket。Coder 不得临时切换。

## Integration Policy

- `auto-merge`：双 PASS、Base/Head 未变、现有 Required Checks、保护规则和权限满足后集成。自动集成不包含部署、发布、数据迁移执行或其他不可逆外部动作。
- `human-merge`：追加 `READY_FOR_HUMAN_MERGE` 等待 Event，保留 Branch/PR/MR 和 Ticket Open；刷新 Git/平台事实后继续。PR/MR 关闭但未合并不得关闭 Ticket。
- 配置缺失时禁止自动合并。单次覆盖需用户明确确认并记录 Event。

共享分支下 Ticket 集成到 Integration Branch 后可以完成，最终目标分支由 `integrate-and-verify` 负责。

## 合并冲突

调用 `$resolving-merge-conflicts` 恢复双方意图。意图不兼容返回结构性 Blocker，不自行选边，不执行破坏性 reset、丢弃或 abort。冲突解决、rebase、Base 更新或任何代码变化都使旧 Verdict 失效，重新进入 Coder 验证与双 Reviewer。
