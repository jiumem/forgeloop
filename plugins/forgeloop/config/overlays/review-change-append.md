## Forgeloop 授权边界

默认只读。不得修改代码、Commit、Branch、Spec、Ticket、PR/MR 或 Tracker 状态。固定点无效或累计 Diff 为空时，在创建两个 Reviewer 前失败；找不到 Spec 时保留 Standards 轴并明确报告 `SPEC: NOT_AVAILABLE`，不得伪造 Spec Verdict。
