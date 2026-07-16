# 修复预算绑定 Ticket 的有效契约输入

修复预算由 Ticket 与其有效 Spec、Ticket 和 ADR Revision 共同界定，而不是永久绑定 Ticket ID。只有实际改变当前 Ticket 契约输入的实质 Revision 才为受影响 Ticket 开启新的修复预算窗口，旧轮次仍作为历史保留；无关或非实质修改不得重置预算。被替代后新建的 Ticket拥有自己的初始窗口，但必须保留 repair lineage，防止通过更换 Issue 重试同一失败方案。
