---
name: resolving-merge-conflicts
description: Resolve an in-progress Git merge or rebase only after recovering both sides' intent. Use when conflicts exist and compatible intent can be preserved; pause for a structural blocker when product, schema, or architecture decisions conflict.
---

# 解决合并冲突

1. 检查当前 merge/rebase 状态、历史和冲突文件。
2. 读取双方 Commit、Spec、Ticket、ADR、PR/MR 和评审记录，恢复每项改动的原始意图。
3. 仅当双方意图兼容时解决冲突；保留双方意图，不发明新行为。
4. 若产品行为、Schema、架构决策或合约互不兼容，停止并返回结构性 `CONTRACT_BLOCKER`，列出冲突决定、证据和所需裁决。不得自行选边。
5. 不自动执行破坏性重置、丢弃提交、`merge --abort`、`rebase --abort` 或其他放弃操作。
6. 运行项目既有的针对性检查。冲突解决改变候选代码时，明确使旧 Verdict 失效，并要求 Coder 验证与 Spec/Standards 双 Reviewer 重新评审。
7. 只有用户原始授权包含完成 merge/rebase 时才暂存并继续；否则报告已解决文件、验证结果和剩余手动步骤。
