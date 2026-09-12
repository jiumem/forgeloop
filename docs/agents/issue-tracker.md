# Issue Tracker：GitHub

本仓库 `jiumem/forgeloop` 使用 GitHub Issues 管理 Issue、Spec、Ticket、依赖和运行状态。所有操作使用已认证的 `gh` CLI。

## 基本操作

- 创建：`gh issue create --title "..." --body "..."`
- 读取：`gh issue view <number> --comments`
- 查询：`gh issue list --state open --json number,title,body,labels,comments`
- 评论：`gh issue comment <number> --body "..."`
- 标签：`gh issue edit <number> --add-label "..."` 或 `--remove-label "..."`
- 关闭：`gh issue close <number> --comment "..."`

多行正文使用 Heredoc。读取工作项时同时获取正文、评论、标签、状态和关系。

## Pull Request 是否作为 Triage 请求入口

PRs as a request surface：`no`。

外部 PR 不自动进入 Issue Triage 队列。GitHub 的 Issue 与 PR 共用编号空间；遇到裸引用 `#42` 时，先运行 `gh pr view 42`，失败后再运行 `gh issue view 42`。

## 发布到 Tracker

当 Skill 要求“发布到 Issue Tracker”时，创建 GitHub Issue。

当 Skill 要求获取相关 Ticket 或 Spec 时，使用 `gh issue view <number> --comments` 读取完整内容。

## Wayfinding Operations

`$wayfinder` 使用一个带 `wayfinder:map` 标签的 Issue 作为 Map，其子 Issue 作为调查 Ticket。

- Map：一个包含 Destination、Notes、Decisions-so-far 和 Fog 的 Issue。
- Child Ticket：优先使用 GitHub Sub-issues；不可用时，在 Map Task List 和 Ticket 正文中记录父子关系。
- Blocking：优先使用 GitHub 原生 Issue Dependencies；不可用时，使用正文中的 `Blocked by: #<n>`。
- Frontier：Map 下所有 Open、Unblocked、Unclaimed 的子 Issue。
- Claim：`gh issue edit <n> --add-assignee @me`，并作为该任务的第一次写入。
- Resolve：先写入结论评论，再关闭 Ticket，最后在 Map 的 Decisions-so-far 中追加摘要和链接。

不得因为平台能力、认证或权限失败而回退到 Local Tracker。

## Integration Policy

- Integration policy：`auto-merge`
- 目标分支：`main`
- `main` 强制通过 Pull Request 合并，并且保护规则对管理员生效。
- 当前没有 Required Status Checks；每次集成时仍需重新读取保护规则和检查状态。
- Branch Protection、Required Checks 和仓库权限始终优先。
- 缺少 Integration Policy 时禁止自动集成。

只有在以下条件全部满足时，Delivery Worker 才能自动合并：

1. 当前交付分支的 Findings 已逐项处置并写入 Issue Comment；
2. 实际待合并 Head 已通过最终 Gate；
3. 分支保护与 Required Checks 满足；
4. 当前身份拥有所需权限；
5. PR 仍然指向当前交付分支和目标分支。

代码导致的检查失败由 Delivery Worker 诊断并修复，不重新启动双轴 Review。权限、基础设施或无关检查失败时暂停并提供可恢复诊断。

## Delivery Runtime Operations

- Delivery unit：启动前完整读取所选大 Ticket、Spec 或有界 Initiative 的正文、评论、关系、状态和目标；不得只从标签推断运行状态。
- Branches and commits：每个大 Ticket 或 Spec 使用一个分支。Spec 的 Tickets 是该分支上的实现 Slices，不各自创建分支或 PR；每个 Slice Commit 排除无关改动。
- Review evidence：在大 Ticket 或当前 Spec 上追加普通 Issue Comment，保存冻结 Base/Head 和两份完整的一次性 Reviewer 报告。Finding 处置、修复 Commit、验证引用和结果 Head 在最终 Gate 前写入第二条普通 Comment。它们是恢复证据，不是 Event 或 Verdict。
- Integration：Delivery Worker 负责当前交付分支的 push、单一 PR、检查和合并。`auto-merge` 仅在最终 Gate、当前 PR 检查、分支保护和权限都符合仓库策略时执行；`human-merge` 保留就绪 PR 并等待用户操作。
- Closure：大 Ticket 只在 PR 合并后关闭。Spec PR 合并后，验证每个 Ticket 的逻辑 Commit 或 `NO_CHANGE_REQUIRED` 证据及验收结果，再关闭 Tickets 和 Spec。有界 Initiative 按依赖顺序完成成员 Specs，全部交付后才关闭 Initiative。
- Recovery：从所选 Issue、Review 与处置 Comments、分支、Commits、PR 和当前 Checks 恢复。认证、权限、保护规则、目标或外部检查失败时保持工作项 Open，并返回可定位、可恢复的诊断。
