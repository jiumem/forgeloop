# fresh Coder 拥有修复耗尽后的语义诊断

每个修复周期耗尽后，由 fresh Coder 阅读有效契约、累计 Candidate、完整两轴 Findings、历次诊断和验证证据，语义判断工作是否仍在 Scope 内、是否存在可信的新机制、是否取得真实进展，并建议自动继续、`IMPLEMENTATION_BLOCKED` 或 `CONTRACT_BLOCKER`。Scheduler 以 Agent 方式核验诊断与事实证据的整体一致性并按声明结果路由，但不自行发明修复机制或用 parser 重新分类；两名 fresh Reviewer 仍只对随后形成的实际 Candidate 执行正式双审，不增加新的诊断 Reviewer 类型。
