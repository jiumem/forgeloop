"""review_result — 审查结果模型。

review_result 是自动回环成立的核心。
它必须能支撑 controller 做三类动作：继续修、允许晋级、升级人工。

设计依据：设计方案 §5.3
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class Severity(StrEnum):
    """Finding 严重级别。"""

    P0 = "P0"  # 致命，必须立即修复
    P1 = "P1"  # 重要，阻断晋级
    P2 = "P2"  # 中等，建议修复但不阻断
    P3 = "P3"  # 轻微，可在后续任务处理


class Finding(BaseModel):
    """结构化 finding — reviewer 产出的单个问题。

    法定字段：设计方案要求一个合格 finding 至少同时包含以下七个字段。
    少任何一项，controller 的自动裁决都会变弱。
    """

    finding_key: str = Field(
        ...,
        min_length=1,
        description="Finding 唯一标识键",
    )
    severity: Severity = Field(
        ...,
        description="严重级别",
    )
    summary: str = Field(
        ...,
        min_length=1,
        description="问题摘要",
    )
    why_it_matters: str = Field(
        ...,
        min_length=1,
        description="为什么重要",
    )
    in_scope: bool = Field(
        ...,
        description="是否在当前任务 scope 内",
    )
    scope_basis: str = Field(
        ...,
        min_length=1,
        description="scope 判定依据（引用 task_packet 的哪条边界）",
    )
    blocks_promotion: bool = Field(
        ...,
        description="是否阻断晋级",
    )


class TaskVerdict(StrEnum):
    """当前任务的总体结论。"""

    CLEAN = "clean"
    NEEDS_FIX = "needs_fix"
    NEEDS_HUMAN_RULING = "needs_human_ruling"


class PromotionReadiness(BaseModel):
    """晋级就绪度评估。"""

    ready: bool = Field(
        ...,
        description="是否具备晋级条件",
    )
    rationale: str = Field(
        default="",
        description="判定理由",
    )


class NextTaskRecommendation(BaseModel):
    """下一任务候选建议（Reviewer 可建议，不可决定）。"""

    task_id: str = Field(
        ...,
        min_length=1,
        description="建议的下一任务 ID",
    )
    rationale: str = Field(
        default="",
        description="推荐理由",
    )


class ReviewResult(BaseModel):
    """审查结果模型 — 四个核心模型之一。

    四个区块:
    - findings: 结构化问题列表
    - current_task_verdict: 当前任务总体结论
    - promotion_readiness: 晋级就绪度
    - next_task_recommendations: 候选下一任务（建议，非命令）

    关键裁决:
    - Reviewer 关注的是实质性问题，不是风格偏好
    - Reviewer 可以建议下一任务，但不能直接决定调度
    - "看不清"必须诚实输出 needs_human_ruling
    """

    task_id: str = Field(..., min_length=1, description="关联的任务 ID")
    round_no: int = Field(..., ge=1, description="第几轮审查")

    # ── 四个区块 ──
    findings: list[Finding] = Field(
        default_factory=lambda: list[Finding](),
        description="结构化 finding 列表",
    )
    current_task_verdict: TaskVerdict = Field(
        ...,
        description="当前任务总体结论",
    )
    promotion_readiness: PromotionReadiness = Field(
        ...,
        description="晋级就绪度评估",
    )
    next_task_recommendations: list[NextTaskRecommendation] = Field(
        default_factory=lambda: list[NextTaskRecommendation](),
        description="下一任务候选建议列表",
    )

    # ── 审查摘要 ──
    summary: str = Field(
        default="",
        description="审查摘要（解释用，非业务真值）",
    )
