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

只有在以下条件全部满足时，Scheduler 才能自动合并：

1. Spec Reviewer 与 Standards Reviewer 均为 `PASS`；
2. 候选 Head 没有变化；
3. 分支保护与 Required Checks 满足；
4. 当前身份拥有所需权限；
5. PR 仍然指向经过评审的 Base/Head。

代码导致的检查失败返回原 Coder，并计入共享修复预算。权限、基础设施或无关检查失败时暂停并提供可恢复诊断。

## Tracker Runtime Operations

- Frontier：查询 Spec 下 Open 子 Issue，排除仍被阻塞、已有有效 Claim 或超出授权 Scope 的项；每次推进后重新查询。
- Claim：在 Spec 或 Initiative 根 Issue 发布 `RUN_CLAIMED`；最早的有效服务端 Claim 获胜。获胜 Scheduler 每次只能认领一个当前 Ticket。
- Checkpoint：使用 Issue Comment 追加最小、幂等的运行记录。两个 Reviewer 结论独立收集后，合并写入一个 `REVIEW_RESULT`。
- 修正：不修改已经发布的事件；使用 `EVENT_SUPERSEDED` 追加修正。
- Candidate：记录 Ticket Branch、Commit 和 PR。关闭但未合并的 PR 不算完成。
- Integration：Scheduler 独占 push、PR、检查与合并操作。
- Closure：确认原生合并事实后写入 `INTEGRATION_RESULT`，再关闭 Ticket。
- Multi-Spec：成员 Spec 在 Initiative Acceptance 前保持 Open；通过后先关闭成员 Spec，最后关闭父 Initiative。
- Failure：认证、权限、分支保护或外部检查阻塞时，工作项保持 Open，并返回可定位、可恢复的诊断。
