"""adapters — 外部工具适配层。

职责：
- 封装 Codex CLI（或其他 code agent）的调用细节
- 将 TaskPacket / TaskState 转为 CLI 输入格式
- 将 CLI 输出解析为 CoderResult / ReviewResult

边界：
- 不持有业务状态（状态归 controller）
- 不做跃迁决策（决策归 controller/transitions）
- 每个适配器是无状态函数或薄 class

当前状态：
- P3 已定义合同（base.py: CodexAdapter Protocol + 配置/结果/错误类型）
- P6 实现具体 Codex CLI adapter
"""
