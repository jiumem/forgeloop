"""schemas — 四个核心结构化模型，作为系统业务真值。

导出:
- TaskPacket: 任务真值模型
- CoderResult: 执行结果模型
- ReviewResult: 审查结果模型
- TaskState: 编排运行态模型
"""

from schemas.coder_result import CheckResult, CheckStatus, CoderResult
from schemas.review_result import (
    Finding,
    NextTaskRecommendation,
    PromotionReadiness,
    ReviewResult,
    Severity,
    TaskVerdict,
)
from schemas.task_packet import PromotionPolicy, TaskPacket
from schemas.task_state import NextAction, RoundRecord, TaskState, TaskStatus

__all__ = [
    "CheckResult",
    "CheckStatus",
    "CoderResult",
    "Finding",
    "NextAction",
    "NextTaskRecommendation",
    "PromotionPolicy",
    "PromotionReadiness",
    "ReviewResult",
    "RoundRecord",
    "Severity",
    "TaskPacket",
    "TaskState",
    "TaskStatus",
    "TaskVerdict",
]
