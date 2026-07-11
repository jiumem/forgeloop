## Forgeloop 发布门禁

“不采访”不等于发明决定。若当前上下文仍缺少 Problem、Actor、目标行为、关键失败状态、权限、Scope、公共 Seam 或不可逆约束，返回 `CONTEXT_INSUFFICIENT` 并逐项列出缺口；不要发布草稿、不要替用户补写决定。只有用户已确认测试 Seam 且上下文足以完整填写模板时才发布。认证、权限或 Tracker 冲突失败时保持未发布状态并报告可定位诊断，不回退到另一 Tracker。
