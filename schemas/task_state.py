"""task_state — 编排运行态模型。

task_state 是 controller 的工作台对象。
它不定义法律，不记录代码细节，而是记录运行态：
- 任务现在在哪个状态
- 已经回环多少轮
- 当前绑定了哪一轮 coder/reviewer 结果
- controller 下一步准备做什么
- 是否要通知人类
- 当前 closure summary

没有 task_state，系统就只有一堆静态对象；
有了 task_state，系统才真正变成状态机。

设计依据：设计方案 §5.4 + §4.4-4.5
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field, model_validator


class TaskStatus(StrEnum):
    """任务状态枚举 — 状态机的全部合法状态。

    正常流:
        NEW -> CODING -> REVIEWING -> REVIEW_CLEAN -> HUMAN_REVIEW -> DONE
    修复回环:
        REVIEWING -> NEEDS_FIX -> CODING
    异常出口:
        ANY -> NEEDS_HUMAN_RULING
        ANY -> BLOCKED
    """

    NEW = "NEW"
    CODING = "CODING"
    REVIEWING = "REVIEWING"
    NEEDS_FIX = "NEEDS_FIX"
    REVIEW_CLEAN = "REVIEW_CLEAN"
    HUMAN_REVIEW = "HUMAN_REVIEW"
    DONE = "DONE"
    NEEDS_HUMAN_RULING = "NEEDS_HUMAN_RULING"
    BLOCKED = "BLOCKED"


class NextAction(StrEnum):
    """Controller 下一步动作枚举。"""

    RUN_CODER = "run_coder"
    RUN_REVIEWER = "run_reviewer"
    WAIT_HUMAN_REVIEW = "wait_human_review"
    WAIT_HUMAN_RULING = "wait_human_ruling"
    RESOLVE_BLOCKED = "resolve_blocked"
    NONE = "none"  # 任务已结案


# ── schema 级合同常量 ──

# status 与 next_action 严格 1:1 绑定。
# 违反此绑定意味着状态对象本身自相矛盾。
STATUS_NEXT_ACTION: dict[TaskStatus, NextAction] = {
    TaskStatus.NEW: NextAction.RUN_CODER,
    TaskStatus.CODING: NextAction.RUN_CODER,
    TaskStatus.REVIEWING: NextAction.RUN_REVIEWER,
    TaskStatus.NEEDS_FIX: NextAction.RUN_CODER,
    TaskStatus.REVIEW_CLEAN: NextAction.WAIT_HUMAN_REVIEW,
    TaskStatus.HUMAN_REVIEW: NextAction.WAIT_HUMAN_REVIEW,
    TaskStatus.DONE: NextAction.NONE,
    TaskStatus.NEEDS_HUMAN_RULING: NextAction.WAIT_HUMAN_RULING,
    TaskStatus.BLOCKED: NextAction.RESOLVE_BLOCKED,
}

# 允许 round_no == 0 的状态。
# NEW: 尚未开轮。BLOCKED / NEEDS_HUMAN_RULING: 可从 NEW 直接早退。
# 其他工作状态必须经过 start_task 开轮，round_no >= 1。
ALLOW_ZERO_ROUND_STATUSES: frozenset[TaskStatus] = frozenset(
    {TaskStatus.NEW, TaskStatus.BLOCKED, TaskStatus.NEEDS_HUMAN_RULING}
)

# 允许 closure_summary 非空的状态。只有 DONE 允许。
ALLOW_CLOSURE_SUMMARY_STATUSES: frozenset[TaskStatus] = frozenset({TaskStatus.DONE})


class RoundRecord(BaseModel):
    """单轮记录：绑定该轮的 coder/reviewer 结果引用。"""

    round_no: int = Field(..., ge=1, description="轮次编号")
    coder_result_ref: str | None = Field(
        default=None,
        description="该轮 coder_result 持久化路径或标识",
    )
    reviewer_result_ref: str | None = Field(
        default=None,
        description="该轮 review_result 持久化路径或标识",
    )
    started_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="该轮开始时间",
    )
    finished_at: datetime | None = Field(
        default=None,
        description="该轮结束时间",
    )


def _utcnow() -> datetime:
    return datetime.now(UTC)


class TaskState(BaseModel):
    """编排运行态模型 — 四个核心模型之一。

    这是 controller 的工作台：记录任务当前在哪个状态、
    已回环多少轮、下一步做什么、是否需要人类介入。
    """

    task_id: str = Field(
        ..., min_length=1, pattern=r"^[A-Za-z0-9_-]+$", description="关联的任务 ID"
    )
    current_status: TaskStatus = Field(
        default=TaskStatus.NEW,
        description="当前状态",
    )
    round_no: int = Field(
        default=0,
        ge=0,
        description="当前轮次编号（0 表示尚未开始）",
    )
    next_action: NextAction = Field(
        default=NextAction.RUN_CODER,
        description="controller 下一步动作",
    )

    # ── 轮次记录 ──
    rounds: list[RoundRecord] = Field(
        default_factory=lambda: list[RoundRecord](),
        description="历史轮次记录",
    )

    # ── 通知与结案 ──
    pending_notification: str | None = Field(
        default=None,
        description="待发送的通知事件（如 needs_human_ruling）",
    )
    closure_summary: str = Field(
        default="",
        description="结案摘要",
    )

    # ── 时间戳 ──
    created_at: datetime = Field(
        default_factory=_utcnow,
        description="task_state 创建时间",
    )
    updated_at: datetime = Field(
        default_factory=_utcnow,
        description="最后更新时间",
    )

    @model_validator(mode="after")
    def _enforce_state_contract(self) -> TaskState:
        """TaskState 全局合同 — schema 级不变式。

        任何时候构造该状态都必须满足，无论来源路径。
        合同矩阵定义在模块级常量中，此处统一执法。

        1. rounds 台账一致性：len(rounds) == round_no，编号连续
        2. status ↔ next_action：严格 1:1 绑定
        3. status ↔ round_no：NEW 必须 0，工作状态 >= 1，早退状态 >= 0
        4. closure_summary：仅 DONE 允许非空
        """
        # ── 1. rounds 台账一致性 ──
        if len(self.rounds) != self.round_no:
            msg = (
                f"rounds 长度（{len(self.rounds)}）与 round_no（{self.round_no}）不一致。"
                f"台账必须完整：len(rounds) == round_no"
            )
            raise ValueError(msg)
        for i, r in enumerate(self.rounds):
            expected = i + 1
            if r.round_no != expected:
                msg = f"rounds[{i}].round_no={r.round_no}，期望 {expected}"
                raise ValueError(msg)

        # ── 2. status ↔ next_action 严格 1:1 绑定 ──
        expected_action = STATUS_NEXT_ACTION[self.current_status]
        if self.next_action != expected_action:
            msg = (
                f"状态 {self.current_status} 的 next_action 必须为 "
                f"{expected_action.value}，实际为 {self.next_action.value}"
            )
            raise ValueError(msg)

        # ── 3. status ↔ round_no ──
        if self.current_status == TaskStatus.NEW and self.round_no != 0:
            msg = f"NEW 状态 round_no 必须为 0，实际为 {self.round_no}"
            raise ValueError(msg)
        if self.current_status not in ALLOW_ZERO_ROUND_STATUSES and self.round_no < 1:
            msg = f"工作状态（{self.current_status}）round_no 必须 >= 1，实际为 {self.round_no}"
            raise ValueError(msg)

        # ── 4. closure_summary 仅 DONE 允许非空 ──
        if self.closure_summary and self.current_status not in ALLOW_CLOSURE_SUMMARY_STATUSES:
            msg = f"状态 {self.current_status} 不允许非空 closure_summary，仅 DONE 可设置结案摘要"
            raise ValueError(msg)

        return self
