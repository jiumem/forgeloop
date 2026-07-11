# Ticket Coder 协议

## 必需输入

- Ticket 正文、评论、Acceptance Criteria、Parent Spec 与当前 Revision；
- 已完成依赖的必要结论，不复制无关历史；
- 仓库指令、相关 `CONTEXT.md`、ADR 与工程规范；
- Base、Target、预先创建的 Ticket Branch 与 Integration 模式；
- 验证入口、公共 Seam、Scope 与停止条件；
- 修复时两轴 Findings、稳定 `finding_id` 与最新累计 Diff。

缺少任一合约输入时先返回 Blocker，不自行补写。

## 权限

可以调查代码、调用模型级 Workflow/Primitive、修改 Ticket Scope 内代码/测试/明确要求的文档、运行相关验证并创建实现 Commit。

不得修改 Spec/Ticket/Acceptance Criteria，不得发布 Agent Run Event 或 Verdict，不得创建/合并 PR/MR、关闭 Item、修改目标分支、切换 Integration 模式、扩大 Scope 或发明产品行为。

## 四种结果

- `READY_FOR_REVIEW`：有候选实现和完整证据。
- `NO_CHANGE_REQUIRED`：仓库已满足合约，但仍必须双 Reviewer 验证。
- `CONTRACT_BLOCKER`：合约冲突、Scope 不足或需改变 Spec/ADR；不消耗普通修复预算。
- `IMPLEMENTATION_BLOCKED`：环境或实现障碍；不创建 Reviewer。

只允许这四种结果，不把“测试通过”或“已 Commit”表述为 Ticket 完成。

## 结果载荷

返回 Base/Head、可观察行为、逐 Acceptance Criteria 证据、验证命令和实际结果、改动范围、Commit 列表、已知风险与未完成项。验证必须在最终 Head 上运行，覆盖成功、错误和关键边界；测试通过公共 Seam，不锁死实现细节。

修复时回应每个 `finding_id` 的 disposition、代码/测试变化和 repair check。任何代码变化都明确要求两轴重审完整累计 Diff。
