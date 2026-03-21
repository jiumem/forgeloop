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
from enum import StrEnum
from typing import Any, NamedTuple

from schemas.review_result import ReviewResult, TaskVerdict
from schemas.task_packet import TaskPacket
from schemas.task_state import NextAction, RoundRecord, TaskState, TaskStatus


class TransitionCause(StrEnum):
    """跃迁原因 — 纯业务语义。

    cause 只表达"为什么发生这次跃迁"，不决定工件合同。
    reviewer_result_ref 是否必填由 TransitionResult.reviewer_result_expected 决定，
    这是独立的正交维度。
    """

    # reviewer 驱动
    REVIEW_FINDINGS = "review_findings"  # 有 blocking findings
    REVIEW_CLEAN = "review_clean"  # 无阻断，晋级条件满足
    REVIEWER_ESCALATION = "reviewer_escalation"  # reviewer 无法可靠裁决

    # controller / external / human 驱动
    LOOP_LIMIT = "loop_limit"  # review loop 超限
    EXTERNAL_BLOCK = "external_block"  # 外部阻塞 / 法律冲突
    CONTROLLER_START = "controller_start"  # controller 首次调度
    RETURN_TO_CODER = "return_to_coder"  # 回 coder 修复
    HUMAN_APPROVAL = "human_approval"  # 人工批准


# ═══════════════════════════════════════════════════
# 统一跃迁规则表 — 单一真相源（Single Source of Truth）
# ═══════════════════════════════════════════════════
#
# 所有状态机约束都从这张表推导，不再手写多份独立映射。
# 一条 TransitionRule = 一个合法业务跃迁。
# cause=None 表示 helper-only 路径（无 TransitionCause，不走 apply_transition）。


class TransitionRule(NamedTuple):
    """一条合法业务跃迁。"""

    from_status: TaskStatus
    to_status: TaskStatus
    cause: TransitionCause | None
    reviewer_result_expected: bool
    required_notification: str | None = None


_S = TaskStatus
_C = TransitionCause

# 非终态集合：外部阻塞可从任意非终态触发
_NON_TERMINAL: tuple[TaskStatus, ...] = (
    _S.NEW,
    _S.CODING,
    _S.REVIEWING,
    _S.NEEDS_FIX,
    _S.REVIEW_CLEAN,
    _S.HUMAN_REVIEW,
)

TRANSITION_RULES: tuple[TransitionRule, ...] = (
    # ── controller 调度 ──
    TransitionRule(_S.NEW, _S.CODING, _C.CONTROLLER_START, False),
    TransitionRule(_S.NEEDS_FIX, _S.CODING, _C.RETURN_TO_CODER, False),
    # ── helper-only: coder 产出（coder_done）──
    TransitionRule(_S.CODING, _S.REVIEWING, None, False),
    # ── reviewer 产出路径（decide_after_review）──
    TransitionRule(_S.REVIEWING, _S.NEEDS_FIX, _C.REVIEW_FINDINGS, True),
    TransitionRule(
        _S.REVIEWING, _S.REVIEW_CLEAN, _C.REVIEW_CLEAN, True, "review_clean_ready_for_human"
    ),
    TransitionRule(
        _S.REVIEWING, _S.NEEDS_HUMAN_RULING, _C.REVIEWER_ESCALATION, True, "needs_human_ruling"
    ),
    TransitionRule(_S.REVIEWING, _S.NEEDS_HUMAN_RULING, _C.LOOP_LIMIT, True, "needs_human_ruling"),
    # ── helper-only: 进入人工审查（enter_human_review）──
    TransitionRule(_S.REVIEW_CLEAN, _S.HUMAN_REVIEW, None, False),
    # ── 人工批准 ──
    TransitionRule(_S.HUMAN_REVIEW, _S.DONE, _C.HUMAN_APPROVAL, False, "task_done"),
    # ── 外部阻塞 → BLOCKED: 任意非终态 ──
    *(TransitionRule(s, _S.BLOCKED, _C.EXTERNAL_BLOCK, False) for s in _NON_TERMINAL),
    # ── 外部阻塞 → NEEDS_HUMAN_RULING: 任意非终态 ──
    *(
        TransitionRule(s, _S.NEEDS_HUMAN_RULING, _C.EXTERNAL_BLOCK, False, "needs_human_ruling")
        for s in _NON_TERMINAL
    ),
)


# ── 从 TRANSITION_RULES 推导的合同常量 ──
# 对外接口不变，但数据来源统一。


def _derive_valid_transitions() -> dict[TaskStatus, set[TaskStatus]]:
    result: dict[TaskStatus, set[TaskStatus]] = {s: set() for s in TaskStatus}
    for rule in TRANSITION_RULES:
        result[rule.from_status].add(rule.to_status)
    return result


def _derive_cause_to_statuses() -> dict[TransitionCause, frozenset[TaskStatus]]:
    tmp: dict[TransitionCause, set[TaskStatus]] = {}
    for rule in TRANSITION_RULES:
        if rule.cause is not None:
            tmp.setdefault(rule.cause, set()).add(rule.to_status)
    return {c: frozenset(s) for c, s in tmp.items()}


def _derive_cause_from_statuses() -> dict[TransitionCause, frozenset[TaskStatus]]:
    tmp: dict[TransitionCause, set[TaskStatus]] = {}
    for rule in TRANSITION_RULES:
        if rule.cause is not None:
            tmp.setdefault(rule.cause, set()).add(rule.from_status)
    return {c: frozenset(s) for c, s in tmp.items()}


def _derive_reviewer_result_sets() -> tuple[frozenset[TransitionCause], frozenset[TransitionCause]]:
    requiring: set[TransitionCause] = set()
    without: set[TransitionCause] = set()
    for rule in TRANSITION_RULES:
        if rule.cause is None:
            continue
        (requiring if rule.reviewer_result_expected else without).add(rule.cause)
    overlap = requiring & without
    if overlap:
        msg = f"reviewer_result_expected 冲突: {overlap}"
        raise ValueError(msg)
    return frozenset(requiring), frozenset(without)


def _derive_required_notification() -> dict[TaskStatus, str]:
    result: dict[TaskStatus, str] = {}
    for rule in TRANSITION_RULES:
        if rule.required_notification is not None:
            existing = result.get(rule.to_status)
            if existing is not None and existing != rule.required_notification:
                msg = (
                    f"to_status={rule.to_status} 法定通知冲突: "
                    f"{existing!r} vs {rule.required_notification!r}"
                )
                raise ValueError(msg)
            result[rule.to_status] = rule.required_notification
    return result


def _derive_rule_index() -> frozenset[tuple[TaskStatus, TransitionCause, TaskStatus]]:
    """(from_status, cause, to_status) 三元组索引，用于 apply_transition 精确查找。"""
    return frozenset(
        (r.from_status, r.cause, r.to_status) for r in TRANSITION_RULES if r.cause is not None
    )


VALID_TRANSITIONS: dict[TaskStatus, set[TaskStatus]] = _derive_valid_transitions()
CAUSE_ALLOWED_STATUSES: dict[TransitionCause, frozenset[TaskStatus]] = _derive_cause_to_statuses()
CAUSE_ALLOWED_FROM_STATUSES: dict[TransitionCause, frozenset[TaskStatus]] = (
    _derive_cause_from_statuses()
)
_reviewer_sets = _derive_reviewer_result_sets()
CAUSES_REQUIRING_REVIEWER_RESULT: frozenset[TransitionCause] = _reviewer_sets[0]
CAUSES_WITHOUT_REVIEWER_RESULT: frozenset[TransitionCause] = _reviewer_sets[1]
TRANSITION_REQUIRED_NOTIFICATION: dict[TaskStatus, str] = _derive_required_notification()
_RULE_INDEX: frozenset[tuple[TaskStatus, TransitionCause, TaskStatus]] = _derive_rule_index()


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
    """跃迁结果：新状态 + 下一动作 + 跃迁原因 + 工件合同 + 可选通知。

    两个正交维度：
    - cause: 为什么发生这次跃迁（纯业务语义）
    - reviewer_result_expected: 本次跃迁是否来自一次真实 reviewer 输出
      （决定 reviewer_result_ref 是否必填）

    decide_after_review() 返回的所有路径（含 LOOP_LIMIT）都设为 True，
    因为 reviewer 已产出结果。外部 BLOCKED 等非 reviewer 路径设为 False。
    """

    new_status: TaskStatus
    next_action: NextAction
    cause: TransitionCause
    reviewer_result_expected: bool = False
    notification: str | None = None
    reason: str = ""

    def __post_init__(self) -> None:
        # 1. new_status ↔ next_action 严格 1:1（复用 TaskState 合同矩阵）
        from schemas.task_state import STATUS_NEXT_ACTION

        expected_action = STATUS_NEXT_ACTION[self.new_status]
        if self.next_action != expected_action:
            msg = (
                f"new_status={self.new_status} 的 next_action 必须为 "
                f"{expected_action.value}，实际为 {self.next_action.value}"
            )
            raise ValueError(msg)

        # 2. cause ↔ new_status 业务语义绑定
        allowed = CAUSE_ALLOWED_STATUSES.get(self.cause)
        if allowed is not None and self.new_status not in allowed:
            msg = (
                f"cause={self.cause} 不允许产出 new_status={self.new_status}，"
                f"合法目标为 {sorted(s.value for s in allowed)}"
            )
            raise ValueError(msg)

        # 3. cause ↔ reviewer_result_expected
        if self.cause in CAUSES_REQUIRING_REVIEWER_RESULT and not self.reviewer_result_expected:
            msg = f"cause={self.cause} 属于 post-review 路径，reviewer_result_expected 必须为 True"
            raise ValueError(msg)
        if self.cause in CAUSES_WITHOUT_REVIEWER_RESULT and self.reviewer_result_expected:
            msg = f"cause={self.cause} 属于非 reviewer 路径，reviewer_result_expected 必须为 False"
            raise ValueError(msg)

        # 4. new_status → 法定通知：自动填充或拒绝不匹配
        required_notif = TRANSITION_REQUIRED_NOTIFICATION.get(self.new_status)
        if required_notif is not None:
            if self.notification is None:
                object.__setattr__(self, "notification", required_notif)
            elif self.notification != required_notif:
                msg = (
                    f"new_status={self.new_status} 的法定通知为 "
                    f"{required_notif!r}，实际为 {self.notification!r}"
                )
                raise ValueError(msg)


def _validated_copy(state: TaskState, updates: dict[str, Any]) -> TaskState:
    """model_copy + 强制重跑 validator，确保不变式不被绕过。

    Pydantic v2 的 model_copy(update=...) 跳过 model_validator，
    所以必须通过 model_validate 重建来执法。
    """
    patched = state.model_copy(update=updates)
    return TaskState.model_validate(patched.model_dump())


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

    # 所有路径都设 reviewer_result_expected=True：
    # decide_after_review 只在 reviewer 已产出 review_result 后运行，
    # 无论业务原因（reviewer 升级 / loop 超限 / findings），
    # 本轮 reviewer 工件都已存在，台账必须绑定。

    # 规则 1: reviewer 明确升级人工
    if review.current_task_verdict == TaskVerdict.NEEDS_HUMAN_RULING:
        return TransitionResult(
            new_status=TaskStatus.NEEDS_HUMAN_RULING,
            next_action=NextAction.WAIT_HUMAN_RULING,
            cause=TransitionCause.REVIEWER_ESCALATION,
            reviewer_result_expected=True,
            notification="needs_human_ruling",
            reason="reviewer 无法可靠裁决，升级人工",
        )

    # 规则 2: loop 超限（controller 规则，但 reviewer 工件已存在）
    if task_state.round_no >= max_rounds:
        return TransitionResult(
            new_status=TaskStatus.NEEDS_HUMAN_RULING,
            next_action=NextAction.WAIT_HUMAN_RULING,
            cause=TransitionCause.LOOP_LIMIT,
            reviewer_result_expected=True,
            notification="needs_human_ruling",
            reason=f"review loop 已达上限 ({task_state.round_no}/{max_rounds})",
        )

    # 规则 3: 有阻断 findings → 需要修复
    if review.current_task_verdict == TaskVerdict.NEEDS_FIX or _has_blocking_findings(review):
        return TransitionResult(
            new_status=TaskStatus.NEEDS_FIX,
            next_action=NextAction.RUN_CODER,
            cause=TransitionCause.REVIEW_FINDINGS,
            reviewer_result_expected=True,
            reason="存在 in-scope blocking findings，回 coder 修复",
        )

    # 规则 4: clean 且就绪 → 进入人工审查
    if review.current_task_verdict == TaskVerdict.CLEAN and review.promotion_readiness.ready:
        return TransitionResult(
            new_status=TaskStatus.REVIEW_CLEAN,
            next_action=NextAction.WAIT_HUMAN_REVIEW,
            cause=TransitionCause.REVIEW_CLEAN,
            reviewer_result_expected=True,
            notification="review_clean_ready_for_human",
            reason="review clean，具备晋级条件，等待人工审查",
        )

    # 规则 5: 兜底 → 升级人工（verdict 与 readiness 不一致，仍属 reviewer 产出语境）
    return TransitionResult(
        new_status=TaskStatus.NEEDS_HUMAN_RULING,
        next_action=NextAction.WAIT_HUMAN_RULING,
        cause=TransitionCause.REVIEWER_ESCALATION,
        reviewer_result_expected=True,
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
    2. reviewer_result_expected 为 True 时强制要求 reviewer_result_ref
    3. 更新状态、动作、通知
    4. 从 REVIEWING 跃迁出去时关闭当前轮（coder→reviewer 周期完成）
    5. 更新 updated_at 时间戳
    """
    # 统一规则表精确查找：(from_status, cause, to_status) 必须在规则表中
    key = (task_state.current_status, result.cause, result.new_status)
    if key not in _RULE_INDEX:
        raise TransitionError(
            task_state.current_status,
            result.new_status,
            f"不存在合法规则: cause={result.cause.value}",
        )

    # reviewer_result_ref 是否必填由 reviewer_result_expected 决定。
    # 这是独立于 cause 的正交维度：
    # - decide_after_review() 产出的所有路径（含 LOOP_LIMIT）都为 True
    # - 外部 BLOCKED / 法律冲突等非 reviewer 路径为 False
    if result.reviewer_result_expected and not reviewer_result_ref:
        msg = (
            f"本次跃迁（cause={result.cause}）标记 reviewer_result_expected=True，"
            "必须提供 reviewer_result_ref（台账不允许缺失结果引用）"
        )
        raise ValueError(msg)
    if not result.reviewer_result_expected and reviewer_result_ref:
        msg = (
            f"本次跃迁（cause={result.cause}）标记 reviewer_result_expected=False，"
            "不应提供 reviewer_result_ref（非 reviewer 路径禁止污染台账）"
        )
        raise ValueError(msg)

    now = datetime.now(UTC)
    rounds = list(task_state.rounds)

    if rounds:
        updates: dict[str, str | datetime] = {}
        # 绑定 reviewer 结果到当前轮
        if reviewer_result_ref:
            updates["reviewer_result_ref"] = reviewer_result_ref
        # 从 REVIEWING 跃迁出去 = 该轮 coder→reviewer 周期完成
        if task_state.current_status == TaskStatus.REVIEWING:
            updates["finished_at"] = now
        if updates:
            rounds[-1] = rounds[-1].model_copy(update=updates)

    return _validated_copy(
        task_state,
        {
            "current_status": result.new_status,
            "next_action": result.next_action,
            "pending_notification": result.notification,
            "rounds": rounds,
            "updated_at": now,
        },
    )


def start_task(task_state: TaskState) -> TaskState:
    """NEW → CODING：controller 首次调度，创建第一轮 RoundRecord。"""
    _validate_transition(task_state.current_status, TaskStatus.CODING)
    now = datetime.now(UTC)
    first_round = RoundRecord(round_no=1, started_at=now)
    return _validated_copy(
        task_state,
        {
            "current_status": TaskStatus.CODING,
            "next_action": NextAction.RUN_CODER,
            "round_no": 1,
            "rounds": [first_round],
            "updated_at": now,
        },
    )


def coder_done(
    task_state: TaskState,
    *,
    coder_result_ref: str,
) -> TaskState:
    """​CODING → REVIEWING：coder_result 产出后，绑定 coder_result_ref 到当前轮。

    coder_result_ref 为必填，台账不允许缺失结果引用。
    """
    _validate_transition(task_state.current_status, TaskStatus.REVIEWING)
    now = datetime.now(UTC)
    rounds = list(task_state.rounds)

    # 绑定 coder 结果到当前轮
    if rounds:
        rounds[-1] = rounds[-1].model_copy(update={"coder_result_ref": coder_result_ref})

    return _validated_copy(
        task_state,
        {
            "current_status": TaskStatus.REVIEWING,
            "next_action": NextAction.RUN_REVIEWER,
            "rounds": rounds,
            "updated_at": now,
        },
    )


def enter_human_review(task_state: TaskState) -> TaskState:
    """REVIEW_CLEAN → HUMAN_REVIEW：进入人工最终审查。

    不覆盖 pending_notification —— 文档法定通知 review_clean_ready_for_human
    已由 apply_transition(decide_after_review(...)) 写入，此处仅推进状态。
    """
    _validate_transition(task_state.current_status, TaskStatus.HUMAN_REVIEW)
    now = datetime.now(UTC)
    return _validated_copy(
        task_state,
        {
            "current_status": TaskStatus.HUMAN_REVIEW,
            "next_action": NextAction.WAIT_HUMAN_REVIEW,
            "updated_at": now,
        },
    )


def approve_human_review(task_state: TaskState, closure_summary: str = "") -> TaskState:
    """HUMAN_REVIEW → DONE：人工签字结案。

    不再关闭轮次 —— 当前轮已在 REVIEWING → REVIEW_CLEAN 时由 apply_transition 关闭。
    """
    _validate_transition(task_state.current_status, TaskStatus.DONE)
    now = datetime.now(UTC)
    return _validated_copy(
        task_state,
        {
            "current_status": TaskStatus.DONE,
            "next_action": NextAction.NONE,
            "closure_summary": closure_summary,
            "pending_notification": "task_done",
            "updated_at": now,
        },
    )


def needs_fix_to_coding(task_state: TaskState) -> TaskState:
    """NEEDS_FIX → CODING：开启新一轮。

    不再关闭当前轮 —— 已在 REVIEWING → NEEDS_FIX 时由 apply_transition 关闭。
    """
    _validate_transition(task_state.current_status, TaskStatus.CODING)
    now = datetime.now(UTC)
    new_round_no = task_state.round_no + 1
    rounds = list(task_state.rounds)

    # 开启新一轮
    rounds.append(RoundRecord(round_no=new_round_no, started_at=now))

    return _validated_copy(
        task_state,
        {
            "current_status": TaskStatus.CODING,
            "next_action": NextAction.RUN_CODER,
            "round_no": new_round_no,
            "rounds": rounds,
            "updated_at": now,
        },
    )
