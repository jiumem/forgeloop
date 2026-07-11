## Integration Policy

`Integration policy: <auto-merge|human-merge>`。缺失时禁止自动集成。Protected Branch、流水线要求和权限优先；不得把认证或权限失败回退为 Local。

## Tracker Runtime Operations

- **Frontier**：查询 Spec 的 Open 子 Issues，排除仍有 Open blocker、已有有效 Claim 或不在授权 Scope 的项；Premium/Ultimate 优先原生 Blocking，Free/不可用时读取正文回退关系。
- **Claim**：先发布带 `run_id` 与幂等键的 `RUN_CLAIMED` Note；服务端最早有效 Claim 获胜，失败者不得创建 Coder。
- **Events**：用结构化 Issue Note 追加事件；发布后不修改，纠错追加 `EVENT_SUPERSEDED`。
- **候选实现**：关联 Ticket Branch、Commit 与 MR；MR 关闭但未合并不等于完成。
- **集成**：`auto-merge` 仅在双 PASS、Head 未变、流水线与权限满足时执行；`human-merge` 写入 `READY_FOR_HUMAN_MERGE` 并等待刷新。
- **关闭**：验证原生合并事实后记录 `INTEGRATION_RESULT`，最后关闭 Ticket。认证、权限或 Protected Branch 失败必须保留 Open 并给出可恢复诊断。
