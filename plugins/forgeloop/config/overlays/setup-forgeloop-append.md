## Forgeloop 扩展配置

在 Section A 后一次只询问一个额外问题：仓库 Integration Policy。推荐遵循仓库现有保护策略；让用户选择 `auto-merge` 或 `human-merge`，并把结果写入 `docs/agents/issue-tracker.md`。缺失策略时 `$run-initiative` 不得自动集成；认证、权限或平台能力检查失败时明确停止，不得回退到另一 Tracker。

重跑时只更新既有 `## Agent skills` 块和 `docs/agents/*.md` 配置，不重复追加。写入前验证所选 CLI 可用且身份/仓库可读；只在用户确认草稿后写入，避免权限失败产生部分配置。

若发现 `docs/initiatives/**`，只报告旧历史入口并链接迁移说明，不读取其内容作为新运行状态，不移动、不删除、不自动转换。完成、归档、Handoff 和 Recommendations 保持只读；活动 Initiative 必须由用户选择固定 `2.5.0` 完成，或预览后重新生成正式 Spec/Tickets。

生成 `docs/agents/issue-tracker.md` 时，把所选模板的 `Tracker Runtime Operations` 与 Integration Policy 一并保留。
