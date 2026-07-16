# 契约修订后旧 Candidate 只作为输入保留

Spec Revision 变化后，既有 Branch、Commit、Findings 与验证证据永久保留，但旧 Candidate 及其 Reviewer Verdict 不再证明新契约已经满足。被保留或更新的 Ticket 必须由新 Coder 基于旧 Head 重新形成绑定新 Revision 的 Candidate，并接受完整双审；被替代 Ticket 的提交只能由新 Ticket Coder 在 Scope 校验后选择性复用，不得由 Scheduler 直接转记为新 Ticket 已完成。该规则在避免丢失已有工作的同时，防止旧契约资格泄漏到新契约。
