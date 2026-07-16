# 自动续配前先持久化修复预算暂停

每组三轮修复耗尽且仍有 Blocking Findings 时，即使 Scheduler 预计可以自动继续，也必须先发布并精确回读 `RUN_PAUSED` reason=`REPAIR_BUDGET`，随后才创建 fresh Coder 执行只读 Exhaustion Diagnosis。新机制通过门禁时，以绑定前一暂停和下一 repair cycle 的 `RUN_RESUMED` 恢复；需要改变契约或没有新机制时继续保持暂停并记录相应诊断。只有恢复 checkpoint 被原生事实确认后才能再次修改 Candidate，从而让短暂暂停、进程崩溃和重复恢复共享同一持久化语义而无需增加 Event 类型。
