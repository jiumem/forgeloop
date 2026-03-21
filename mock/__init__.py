"""mock — 测试 fixtures 与脚本化场景。

职责：
- 提供标准 TaskPacket / CoderResult / ReviewResult 样例实例
- 提供结构化 mock 场景（Scenario），可直接用于状态机测试
- 提供 JSON fixture 文件供非 Python 消费方使用

目录结构：
- sample_task_packets.py   — 样例 TaskPacket（最小 + 完整）
- sample_coder_results.py  — 样例 CoderResult（clean / partial / failed_checks）
- sample_review_results.py — 样例 ReviewResult（5 种场景）
- scenarios.py             — 结构化场景定义（3 类 Scenario）
- fixtures/                — JSON 格式的样例文件（由 Python 实例序列化生成）

边界：
- 不包含真实外部调用
- 不包含测试断言（断言在 tests/ 中）
- 不依赖 Codex CLI 运行
"""
