"""mock — 测试 fixtures 与脚本化场景。

职责：
- 提供标准 TaskPacket / CoderResult / ReviewResult 样例实例
- 提供 JSON fixture 文件供非 Python 消费方使用
- 后续承载端到端 mock 场景脚本（scripted scenario）

目录结构：
- sample_task_packets.py  — Python 可导入的样例 TaskPacket
- fixtures/               — JSON 格式的样例文件

边界：
- 不包含真实外部调用
- 不包含测试断言（断言在 tests/ 中）
"""
