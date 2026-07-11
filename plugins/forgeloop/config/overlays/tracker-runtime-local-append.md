## Integration Policy

`Integration policy: <auto-merge|human-merge>`。缺失时禁止自动集成。Local 仍通过 Git Branch/Commit 表达候选实现，不把 Markdown 状态当作代码已集成的证明。

## Tracker Runtime Operations

- **Frontier**：扫描授权 Spec 的 Open Ticket 文件，排除未解决 blocker 和已有 Claim；每次推进后重新扫描，按编号确定性选择。
- **Claim**：在 Tracker 目录用原子创建的 `scheduler.lock` 竞争 Initiative Scheduler，再为 Ticket 原子创建 `<ticket>.claim`；锁记录 `run_id`，不使用短 TTL。失败者不得创建 Coder。
- **Events**：在 Ticket 的 `## Agent Run Events` 下追加结构化事件；每项带 Schema Version、Run ID、序号和幂等键。重复幂等键不得再次写入，纠错追加 `EVENT_SUPERSEDED`。
- **候选实现**：关联 Ticket Branch 与 Commit；不得用 `claimed` 或 Reviewer PASS 伪装集成完成。
- **集成**：`auto-merge` 仅在双 PASS 且 Base/Head 未变时集成；`human-merge` 记录 `READY_FOR_HUMAN_MERGE` 并等待用户操作后刷新 Git 事实。
- **关闭**：验证 Commit 已进入目标分支后记录 `INTEGRATION_RESULT`，最后把 Ticket 标记为 `resolved`。脏工作区、锁冲突或 Git 状态不一致时保持 Open 并报告恢复步骤。
