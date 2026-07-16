# 以问题、主要参与者和交付结果界定 Spec 身份

Spec 是否可以通过新 Revision 延续，由核心 Problem、主要 Actor 与预期的可观察交付结果共同决定。三者保持不变时，Scope、Acceptance、Schema、公开 Seam 或 ADR 的调整仍属于同一 Spec，可在调和受影响 Tickets 后恢复原 Run；核心 Problem、主要 Actor 或可观察交付结果被替换时，必须取消旧 Run、保留既有历史并创建新 Spec，避免把不同交付目标伪装成同一条版本历史。服务于同一结果的次要 Actor 变化不单独改变 Spec 身份。
