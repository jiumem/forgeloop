# Scheduler 协议

## 入口与范围

解析正式引用并读取完整正文、评论、关系和当前状态。单 Spec 直接运行；多 Spec 新建父 Item 前先展示成员、跨 Spec Dependencies、目标分支、Integration Policy 和风险，等待用户确认。增删成员必须再次确认并追加范围 Event。

## 预检

验证：

- Tracker 配置、CLI、认证、仓库权限和平台能力；
- Integration Policy、Branch Protection/Protected Branch 与 Required Checks；
- Spec Revision、所有坏引用、依赖环、父子关系和目标分支；
- Git 工作区、Base、候选 Branch 命名冲突；
- 能创建两个独立 Reviewer；不支持显式模型路由时记录能力降级。

任一预检失败返回 `FAILED_PRECONDITION`，不得发布 Claim 或创建 Coder。

## Frontier 与 Claim

每轮从 Tracker 原生事实重新计算 Frontier。排序使用 Tracker 明确顺序；无明确顺序时按持久化 Ticket ID 升序。空 Frontier 必须报告各桶：Completed、Blocked、Claimed、Invalid Reference、State Conflict。

先竞争 Initiative Scheduler，再 Claim Ticket。GitHub/GitLab 以服务端最早有效 `RUN_CLAIMED` 为胜者；Local 使用原子锁。Claim 失败不得创建 Coder；失败者只追加或报告失败。锁不使用短 TTL；只有明确恢复协议可以接管。

## Agent 生命周期

为每张 Ticket 创建：

1. 一个新 Coder；
2. 一个新 Spec Reviewer；
3. 一个新 Standards Reviewer。

两名 Reviewer 必须用独立上下文并可并行启动。修复轮次向原 Coder 同时提供两轴 Findings，只向每名 Reviewer提供本轴历史。Ticket 结束后终止三者。

## Scheduler 职责

- 发布幂等 Events，校验序号与引用；
- 校验 Coder 结果和两个 Verdict 绑定同一 Base/Head；
- 编排修复、集成、暂停、恢复和最终验收；
- 消费仓库自然产生的 CI/Required Checks。

Scheduler 不修改实现、不替 Reviewer 判定、不重跑 Coder 已完成的全套测试、不额外触发完整 CI。
