# Tracker Runtime 路由

始终先读取 `docs/agents/issue-tracker.md` 中由 `$setup-forgeloop` 生成的 `Tracker Runtime Operations`。下列是共享边界，不替代仓库配置。

## GitHub

所有操作使用 `gh`。用原生 Sub-issues/Dependencies 表达关系；能力缺失时只按配置模板中的正文关系回退。Frontier、最早 Claim Comment、结构化 Events、Branch/Commit/PR 关联和关闭均通过 GitHub 事实完成。

认证、Issue/PR 权限、Branch Protection 或 Required Checks 失败时保持 Open、记录可定位错误，不回退 Local。`auto-merge` 与 `human-merge` 均遵循配置。

## GitLab

所有操作使用 `glab`。Premium/Ultimate 优先原生 Blocking；Free 或能力不可用时按配置模板回退。Frontier、最早 Claim Note、Events、Branch/Commit/MR 关联和关闭均通过 GitLab 事实完成。

认证、项目权限、Protected Branch 或流水线门禁失败时保持 Open、记录可定位错误，不回退 Local。

## Local Markdown

Tracker 位于 `.scratch/<feature>/`；Spec、Ticket、阻塞与 Events 只写配置定义的位置。Scheduler 与 Ticket Claim 通过同一文件系统上的原子创建锁竞争，失败者不写 Coder Event。锁保存 Run ID，不使用短 TTL。

Event 追加前检查幂等键；文件冲突、坏引用、脏工作区或 Git 事实不一致时停止。代码候选仍由 Git Branch/Commit 表达，Markdown `resolved` 只能在 Commit 已进入目标分支后最后写入。

## 平台等价状态

三平台必须产生同一领域结果：一个有效 Claim、一个活动 Ticket、四种 Coder 结果、两个独立 Verdict、相同修复预算、明确 Integration Result、分层 Acceptance 与可恢复 Run ID。CLI 命令和物理存储不同不得改变完成语义。
