"""task_packet — 任务真值模型。

task_packet 是整个系统的源头。它定义当前任务的身份、法源、范围、依赖与验证。
它不记录执行日志，不承载审查结论，也不保存运行态状态。
它只保留机器推进所需的最小边界信息。

设计依据：设计方案 §5.1
"""

from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints

# 任务 ID 引用约束：与实体 task_id 保持一致
TaskIdRef = Annotated[str, StringConstraints(min_length=1, pattern=r"^[A-Za-z0-9_-]+$")]


class PromotionPolicy(BaseModel):
    """晋级策略：定义任务完成后如何推进到下一阶段。"""

    auto_promote: bool = Field(
        default=False,
        description="是否在 review clean 后自动推进（仍需人工签字）",
    )
    max_review_rounds: int = Field(
        default=3,
        ge=1,
        description="review loop 最大轮次上限",
    )


class TaskPacket(BaseModel):
    """任务真值模型 — 四个核心模型之一。

    设计原则：尽量少，但必须足够执法。

    字段分层:
    - 身份层: task_id / title / phase / chain
    - 法源层: entry_docs
    - 范围层: must_do / must_not_do / done_criteria
    - 依赖层: depends_on / related_tasks
    - 验证层: required_checks
    - 推进层: promotion_policy
    """

    # ── 身份层 ──
    task_id: str = Field(
        ...,
        min_length=1,
        pattern=r"^[A-Za-z0-9_-]+$",
        description="任务唯一标识，如 P1_schema_baseline（仅限字母、数字、下划线、连字符）",
    )
    title: str = Field(
        ...,
        min_length=1,
        description="任务标题，人类可读",
    )
    phase: str = Field(
        default="",
        description="所属阶段，如 M1",
    )
    chain: str = Field(
        default="",
        description="所属任务链标识",
    )

    # ── 法源层 ──
    entry_docs: list[str] = Field(
        default_factory=list,
        description="依据的文档路径列表",
    )

    # ── 范围层 ──
    must_do: list[str] = Field(
        ...,
        min_length=1,
        description="必须交付的内容列表（至少一项）",
    )
    must_not_do: list[str] = Field(
        default_factory=list,
        description="明确不做的内容列表",
    )
    done_criteria: list[str] = Field(
        ...,
        min_length=1,
        description="完成标准列表（至少一项）",
    )

    # ── 依赖层 ──
    depends_on: list[TaskIdRef] = Field(
        default_factory=list,
        description="前置依赖任务 ID 列表",
    )
    related_tasks: list[TaskIdRef] = Field(
        default_factory=list,
        description="相关任务 ID 列表（不构成硬依赖）",
    )

    # ── 验证层 ──
    required_checks: list[str] = Field(
        default_factory=list,
        description="必须执行的验证命令列表",
    )

    # ── 推进层 ──
    promotion_policy: PromotionPolicy = Field(
        default_factory=PromotionPolicy,
        description="晋级策略",
    )
