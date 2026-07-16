# 契约调和采用不可回滚的前向恢复事务

契约调和按 Spec 或 ADR Revision、缺失 Ticket 创建、Open Ticket 更新、关系重接、覆盖与 Frontier 验证、失效 Ticket 替代、完整原生回读和 `RUN_RESUMED` 的顺序推进。任何已被正式 Tracker 精确确认的写入都不回滚；中途失败时 Run 与 Claims 保持暂停，恢复过程查询并复用等价写入、补齐缺失步骤，发生内容冲突或非唯一结果时进入 `RECOVERY_CONFLICT`。只有全部调和事实验证通过后才能恢复 Run，执行故障不得导致重复询问已经确认的契约决定。
