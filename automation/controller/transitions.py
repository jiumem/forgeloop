"""transitions — 状态跃迁表与 advance_state 规则引擎。

这是 P2_state_machine 的核心：把设计文档中的状态图写成明确规则，
而不是散落在 prompt 和自然语言里。

跃迁法则（设计方案 §4.5）：
| 当前状态          | 触发条件                                      | 下一状态              |
|-----------------|----------------------------------------------|---------------------|
| NEW             | controller 首次调度                             | CODING              |
| CODING          | coder_result 产出                              | REVIEWING           |
| REVIEWING       | 有 blocking findings / checks 不通过 / must_do 未完成 | NEEDS_FIX       |
| NEEDS_FIX       | controller 回 coder                           | CODING              |
| REVIEWING       | 无阻断 findings 且晋级条件满足                        | REVIEW_CLEAN        |
| REVIEW_CLEAN    | 需要人工最终审查                                    | HUMAN_REVIEW        |
| HUMAN_REVIEW    | 人工批准                                        | DONE                |
| 任意状态          | 法律冲突 / loop 超限 / reviewer 无法可靠裁决           | NEEDS_HUMAN_RULING  |
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from schemas.review_result import ReviewResult, TaskVerdict
from schemas.task_packet import TaskPacket
from schemas.task_state import NextAction, RoundRecord, TaskState, TaskStatus

# ── 合法跃迁表 ──
# 只有列出的 (from, to) 对才是合法跃迁；其余一律拒绝。
VALID_TRANSITIONS: dict[TaskStatus, set[TaskStatus]] = {
    TaskStatus.NEW: {TaskStatus.CODING, TaskStatus.BLOCKED, TaskStatus.NEEDS_HUMAN_RULING},
    TaskStatus.CODING: {TaskStatus.REVIEWING, TaskStatus.BLOCKED, TaskStatus.NEEDS_HUMAN_RULING},
    TaskStatus.REVIEWING: {
        TaskStatus.NEEDS_FIX,
        TaskStatus.REVIEW_CLEAN,
        TaskStatus.NEEDS_HUMAN_RULING,
        TaskStatus.BLOCKED,
    },
    TaskStatus.NEEDS_FIX: {TaskStatus.CODING, TaskStatus.NEEDS_HUMAN_RULING, TaskStatus.BLOCKED},
    TaskStatus.REVIEW_CLEAN: {TaskStatus.HUMAN_REVIEW, TaskStatus.NEEDS_HUMAN_RULING},
    TaskStatus.HUMAN_REVIEW: {TaskStatus.DONE, TaskStatus.NEEDS_HUMAN_RULING},
    # 终态不可跃迁
    TaskStatus.DONE: set(),
    TaskStatus.NEEDS_HUMAN_RULING: set(),
    TaskStatus.BLOCKED: set(),
}


class TransitionError(Exception):
    """非法状态跃迁。"""

    def __init__(self, from_status: TaskStatus, to_status: TaskStatus, reason: str = "") -> None:
        self.from_status = from_status
        self.to_status = to_status
        self.reason = reason
        msg = f"非法跃迁: {from_status.value} -> {to_status.value}"
        if reason:
            msg += f" ({reason})"
        super().__init__(msg)


@dataclass(frozen=True)
class TransitionResult:
    """跃迁结果：新状态 + 下一动作 + 可选通知。"""

    new_status: TaskStatus
    next_action: NextAction
    notification: str | None = None
    reason: str = ""


def _validate_transition(from_status: TaskStatus, to_status: TaskStatus) -> None:
    """校验跃迁合法性。"""
    allowed = VALID_TRANSITIONS.get(from_status, set())
    if to_status not in allowed:
        raise TransitionError(from_status, to_status, "不在合法跃迁表中")


def _has_blocking_findings(review: ReviewResult) -> bool:
    """是否存在 in-scope 且阻断晋级的 finding。"""
    return any(f.in_scope and f.blocks_promotion for f in review.findings)


def decide_after_review(
    task_packet: TaskPacket,
    task_state: TaskState,
    review: ReviewResult,
) -> TransitionResult:
    """根据 review_result 裁决下一步跃迁 — controller 的核心裁决入口。

    规则优先级（deterministic，无 LLM 参与）：
    1. reviewer 明确说 needs_human_ruling → NEEDS_HUMAN_RULING
    2. loop 超限 → NEEDS_HUMAN_RULING
    3. 有 in-scope blocking findings → NEEDS_FIX
    4. 无阻断 findings 且晋级条件满足 → REVIEW_CLEAN
    5. 其他情况兜底 → NEEDS_HUMAN_RULING
    """
    max_rounds = task_packet.promotion_policy.max_review_rounds

    # 规则 1: reviewer 明确升级人工
    if review.current_task_verdict == TaskVerdict.NEEDS_HUMAN_RULING:
        return TransitionResult(
            new_status=TaskStatus.NEEDS_HUMAN_RULING,
            next_action=NextAction.WAIT_HUMAN_RULING,
            notification="needs_human_ruling",
            reason="reviewer 无法可靠裁决，升级人工",
        )

    # 规则 2: loop 超限
    if task_state.round_no >= max_rounds:
        return TransitionResult(
            new_status=TaskStatus.NEEDS_HUMAN_RULING,
            next_action=NextAction.WAIT_HUMAN_RULING,
            notification="needs_human_ruling",
            reason=f"review loop 已达上限 ({task_state.round_no}/{max_rounds})",
        )

    # 规则 3: 有阻断 findings → 需要修复
    if review.current_task_verdict == TaskVerdict.NEEDS_FIX or _has_blocking_findings(review):
        return TransitionResult(
            new_status=TaskStatus.NEEDS_FIX,
            next_action=NextAction.RUN_CODER,
            reason="存在 in-scope blocking findings，回 coder 修复",
        )

    # 规则 4: clean 且就绪 → 进入人工审查
    if review.current_task_verdict == TaskVerdict.CLEAN and review.promotion_readiness.ready:
        return TransitionResult(
            new_status=TaskStatus.REVIEW_CLEAN,
            next_action=NextAction.WAIT_HUMAN_REVIEW,
            notification="review_clean_ready_for_human",
            reason="review clean，具备晋级条件，等待人工审查",
        )

    # 规则 5: 兜底 → 升级人工
    return TransitionResult(
        new_status=TaskStatus.NEEDS_HUMAN_RULING,
        next_action=NextAction.WAIT_HUMAN_RULING,
        notification="needs_human_ruling",
        reason="无法自动裁决（verdict 与 readiness 不一致），升级人工",
    )


def apply_transition(
    task_state: TaskState,
    result: TransitionResult,
    *,
    reviewer_result_ref: str | None = None,
) -> TaskState:
    """将跃迁结果应用到 task_state，返回新的 task_state。

    此函数：
    1. 校验跃迁合法性
    2. 更新状态、动作、通知
    3. 如果提供了 reviewer_result_ref，绑定到当前轮次
    4. 更新 updated_at 时间戳
    """
    _validate_transition(task_state.current_status, result.new_status)

    now = datetime.now(UTC)
    rounds = list(task_state.rounds)

    # 绑定 reviewer 结果到当前轮
    if reviewer_result_ref and rounds:
        current = rounds[-1]
        rounds[-1] = current.model_copy(update={"reviewer_result_ref": reviewer_result_ref})

    return task_state.model_copy(
        update={
            "current_status": result.new_status,
            "next_action": result.next_action,
            "pending_notification": result.notification,
            "rounds": rounds,
            "updated_at": now,
        }
    )


def start_task(task_state: TaskState) -> TaskState:
    """NEW → CODING：controller 首次调度，创建第一轮 RoundRecord。"""
    _validate_transition(task_state.current_status, TaskStatus.CODING)
    now = datetime.now(UTC)
    first_round = RoundRecord(round_no=1, started_at=now)
    return task_state.model_copy(
        update={
            "current_status": TaskStatus.CODING,
            "next_action": NextAction.RUN_CODER,
            "round_no": 1,
            "rounds": [first_round],
            "updated_at": now,
        }
    )


def coder_done(
    task_state: TaskState,
    *,
    coder_result_ref: str | None = None,
) -> TaskState:
    """CODING → REVIEWING：coder_result 产出后，绑定 coder_result_ref 到当前轮。"""
    _validate_transition(task_state.current_status, TaskStatus.REVIEWING)
    now = datetime.now(UTC)
    rounds = list(task_state.rounds)

    # 绑定 coder 结果到当前轮
    if coder_result_ref and rounds:
        current = rounds[-1]
        rounds[-1] = current.model_copy(update={"coder_result_ref": coder_result_ref})

    return task_state.model_copy(
        update={
            "current_status": TaskStatus.REVIEWING,
            "next_action": NextAction.RUN_REVIEWER,
            "rounds": rounds,
            "updated_at": now,
        }
    )


def enter_human_review(task_state: TaskState) -> TaskState:
    """REVIEW_CLEAN → HUMAN_REVIEW：进入人工最终审查。

    不覆盖 pending_notification —— 文档法定通知 review_clean_ready_for_human
    已由 apply_transition(decide_after_review(...)) 写入，此处仅推进状态。
    """
    _validate_transition(task_state.current_status, TaskStatus.HUMAN_REVIEW)
    now = datetime.now(UTC)
    return task_state.model_copy(
        update={
            "current_status": TaskStatus.HUMAN_REVIEW,
            "next_action": NextAction.WAIT_HUMAN_REVIEW,
            "updated_at": now,
        }
    )


def approve_human_review(task_state: TaskState, closure_summary: str = "") -> TaskState:
    """HUMAN_REVIEW → DONE：人工签字结案，关闭最后一轮。"""
    _validate_transition(task_state.current_status, TaskStatus.DONE)
    now = datetime.now(UTC)
    rounds = list(task_state.rounds)

    # 关闭最后一轮
    if rounds:
        current = rounds[-1]
        rounds[-1] = current.model_copy(update={"finished_at": now})

    return task_state.model_copy(
        update={
            "current_status": TaskStatus.DONE,
            "next_action": NextAction.NONE,
            "closure_summary": closure_summary,
            "pending_notification": "task_done",
            "rounds": rounds,
            "updated_at": now,
        }
    )


def needs_fix_to_coding(task_state: TaskState) -> TaskState:
    """NEEDS_FIX → CODING：关闭当前轮，开启新一轮。"""
    _validate_transition(task_state.current_status, TaskStatus.CODING)
    now = datetime.now(UTC)
    new_round_no = task_state.round_no + 1
    rounds = list(task_state.rounds)

    # 关闭当前轮
    if rounds:
        current = rounds[-1]
        rounds[-1] = current.model_copy(update={"finished_at": now})

    # 开启新一轮
    rounds.append(RoundRecord(round_no=new_round_no, started_at=now))

    return task_state.model_copy(
        update={
            "current_status": TaskStatus.CODING,
            "next_action": NextAction.RUN_CODER,
            "round_no": new_round_no,
            "rounds": rounds,
            "updated_at": now,
        }
    )
