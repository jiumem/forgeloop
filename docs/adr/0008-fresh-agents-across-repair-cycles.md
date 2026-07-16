# 修复周期内复用 Agent，跨周期使用 fresh Agent

同一组三轮修复继续复用该周期的 Coder 与两名隔离 Reviewer，以保留连续上下文；三轮耗尽并进入新的自动修复周期时，保留同一 Ticket、Run、Branch 和 Candidate 历史，但创建 fresh Coder 与 fresh 双 Reviewer。新 Coder 先从 Tracker 与 Git 的持久证据执行只读 Exhaustion Diagnosis，只有找到 Scope 内且可证伪的新机制才进入实现；需要改变契约时转 `CONTRACT_BLOCKER`，没有新机制时转 `IMPLEMENTATION_BLOCKED`。该选择复用既有角色，同时降低失败机制和旧对话对新周期的锚定。
