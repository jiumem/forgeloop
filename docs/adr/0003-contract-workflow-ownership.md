# 由契约所有者发布修订并由运行协调器编排

同一 Spec 的正式 Revision 只能由 `to-spec` 的 Revision Mode 在完整校验和精确回读后发布，经用户确认的 ADR 变更仍由 `domain-modeling` 维护，受影响 Open Tickets 由 `to-tickets` 调和；`run-initiative` 只记录 `CONTRACT_BLOCKER`、编排已经一次性获批的事务并在全部原生事实验证通过后恢复原 Run，不得直接编辑 Spec 或 ADR。该边界复用现有工作流的事实所有权，同时避免一次契约裁决演变成多次用户批准。
