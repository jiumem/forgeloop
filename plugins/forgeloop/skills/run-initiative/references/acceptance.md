# 完成与最终验收

## Ticket Gate

只有同时满足才最后关闭：Acceptance Criteria 有实现/验证证据；Coder 在最终 Head 验证；双 Reviewer 对同一 Base/Head PASS；候选实现按策略进入声明目标；既有 Required Checks 满足；Tracker 记录 Branch/PR/MR、Commit、证据、Verdicts 与集成结果。

双 PASS 但未集成仅为 `READY_FOR_MERGE`。PR/MR 关闭未合并不是完成。

## Spec Gate

当前 Scope 全部子 Tickets 通过，且无 Open、Blocked、Repair 或等待人工合并；Scope 变化有确认；代码进入最终目标；取得绑定 Spec Revision 与最终 Commit 的 Acceptance Verdict；记录交付摘要、验证入口、证据、限制和最终引用后，最后关闭 Spec。

简单单 Ticket、常规风险、无修复、独立 Branch 且公共 Seam 证据完整时，Ticket Spec Reviewer 可以同时签发 `TICKET_VERDICT: PASS` 与 `SPEC_ACCEPTANCE: PASS`。

多 Ticket、高风险、发生修复、共享 Integration Branch、跨模块/多步骤或证据不完整时，创建全新 Spec Acceptance Reviewer。失败时 Spec 保持 Open，并创建正式修复 Ticket；不得改写已关闭 Ticket 的历史 Verdict。修复完成并重新验收前不得关闭。

## Initiative Gate

单 Spec 随 Spec 完成。多 Spec 的成员集合及范围变化必须有确认；所有 Specs 独立完成、跨 Spec Dependencies 解决、代码进入最终目标后，创建全新 Initiative Acceptance Reviewer。Verdict 绑定 Initiative Revision 与最终 Commit；记录成员、跨 Spec 证据、限制和最终引用，`INITIATIVE_ACCEPTANCE: PASS` 后最后关闭父 Item。

失败时父 Item 保持 Open 并创建正式修复工作。`PAUSED`、`CANCELLED`、`COMPLETED` 严格区分。

## Spec 修订

首次运行记录 Revision。拼写、排版、链接和不改变行为的澄清可记非实质修改；Problem、Actor、目标、Acceptance Criteria、失败状态、权限、Scope、接口、Schema、迁移、Seam 或交付目标变化属于实质修改。

实质修改需用户确认并进入 `PAUSED_FOR_SPEC_CHANGE`；重新对账 Open Tickets，保留已完成历史，使受影响 Verdict 和最终验收资格失效。核心 Problem、Actor 或交付目标被替换时创建新 Spec，旧 Spec 标为 `SUPERSEDED`。Coder/Reviewer 只能报告 Blocker，不直接改 Spec。
