"""tests/test_transitions.py — P2 状态机跃迁测试。

覆盖：
- clean / needs_fix / needs_human_ruling 三条裁决路径
- loop 超限升级人工
- 合法跃迁表校验
- 非法跃迁拒绝
- 便利函数全路径 (start_task → coder_done → ... → approve)
- 终态不可跃迁
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from automation.controller.transitions import (
    VALID_TRANSITIONS,
    TransitionCause,
    TransitionError,
    TransitionResult,
    apply_transition,
    approve_human_review,
    coder_done,
    decide_after_review,
    enter_human_review,
    needs_fix_to_coding,
    start_task,
)
from schemas.review_result import (
    Finding,
    PromotionReadiness,
    ReviewResult,
    Severity,
    TaskVerdict,
)
from schemas.task_packet import PromotionPolicy, TaskPacket
from schemas.task_state import NextAction, RoundRecord, TaskState, TaskStatus

# ═══════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════


def _make_packet(max_rounds: int = 3) -> TaskPacket:
    return TaskPacket(
        task_id="test_task",
        title="Test Task",
        must_do=["implement feature"],
        done_criteria=["tests pass"],
        promotion_policy=PromotionPolicy(max_review_rounds=max_rounds),
    )


def _make_state(
    status: TaskStatus = TaskStatus.REVIEWING,
    round_no: int | None = None,
) -> TaskState:
    """构造一致的 TaskState（rounds + next_action 自动与 status 对齐）。

    round_no 未指定时：NEW → 0，其他 → 1。
    next_action 由 STATUS_NEXT_ACTION 映射自动推导。
    """
    from schemas.task_state import STATUS_NEXT_ACTION

    if round_no is None:
        round_no = 0 if status == TaskStatus.NEW else 1
    rounds = [RoundRecord(round_no=i + 1) for i in range(round_no)]
    return TaskState(
        task_id="test_task",
        current_status=status,
        next_action=STATUS_NEXT_ACTION[status],
        round_no=round_no,
        rounds=rounds,
    )


def _make_review(
    verdict: TaskVerdict = TaskVerdict.CLEAN,
    ready: bool = True,
    blocking_findings: int = 0,
) -> ReviewResult:
    findings = [
        Finding(
            finding_key=f"issue-{i}",
            severity=Severity.P1,
            summary=f"Blocking issue {i}",
            why_it_matters="breaks contract",
            in_scope=True,
            scope_basis="must_do[0]",
            blocks_promotion=True,
        )
        for i in range(blocking_findings)
    ]
    return ReviewResult(
        task_id="test_task",
        round_no=1,
        findings=findings,
        current_task_verdict=verdict,
        promotion_readiness=PromotionReadiness(ready=ready),
    )


# ═══════════════════════════════════════════════════
# decide_after_review 核心裁决
# ═══════════════════════════════════════════════════


class TestDecideAfterReview:
    """controller 核心裁决入口测试。"""

    def test_clean_and_ready_goes_to_review_clean(self) -> None:
        """review clean + ready → REVIEW_CLEAN。"""
        packet = _make_packet()
        state = _make_state()
        review = _make_review(verdict=TaskVerdict.CLEAN, ready=True)

        result = decide_after_review(packet, state, review)

        assert result.new_status == TaskStatus.REVIEW_CLEAN
        assert result.next_action == NextAction.WAIT_HUMAN_REVIEW
        assert result.cause == TransitionCause.REVIEW_CLEAN
        assert result.notification == "review_clean_ready_for_human"

    def test_needs_fix_goes_to_needs_fix(self) -> None:
        """verdict=needs_fix → NEEDS_FIX。"""
        packet = _make_packet()
        state = _make_state()
        review = _make_review(verdict=TaskVerdict.NEEDS_FIX, ready=False)

        result = decide_after_review(packet, state, review)

        assert result.new_status == TaskStatus.NEEDS_FIX
        assert result.next_action == NextAction.RUN_CODER
        assert result.cause == TransitionCause.REVIEW_FINDINGS

    def test_blocking_findings_force_needs_fix(self) -> None:
        """即使 verdict=clean，有 blocking findings 仍应 NEEDS_FIX。"""
        packet = _make_packet()
        state = _make_state()
        # verdict 说 clean 但实际有 blocking finding — 矛盾输入兜底
        review = _make_review(
            verdict=TaskVerdict.CLEAN,
            ready=True,
            blocking_findings=1,
        )

        result = decide_after_review(packet, state, review)

        assert result.new_status == TaskStatus.NEEDS_FIX
        assert result.cause == TransitionCause.REVIEW_FINDINGS

    def test_needs_human_ruling_goes_to_needs_human_ruling(self) -> None:
        """verdict=needs_human_ruling → NEEDS_HUMAN_RULING。"""
        packet = _make_packet()
        state = _make_state()
        review = _make_review(verdict=TaskVerdict.NEEDS_HUMAN_RULING, ready=False)

        result = decide_after_review(packet, state, review)

        assert result.new_status == TaskStatus.NEEDS_HUMAN_RULING
        assert result.next_action == NextAction.WAIT_HUMAN_RULING
        assert result.cause == TransitionCause.REVIEWER_ESCALATION
        assert result.notification == "needs_human_ruling"

    def test_loop_over_limit_goes_to_needs_human_ruling(self) -> None:
        """loop 超限 → NEEDS_HUMAN_RULING（优先级高于 needs_fix）。"""
        packet = _make_packet(max_rounds=2)
        state = _make_state(round_no=2)  # 已达上限
        review = _make_review(verdict=TaskVerdict.NEEDS_FIX, ready=False)

        result = decide_after_review(packet, state, review)

        assert result.new_status == TaskStatus.NEEDS_HUMAN_RULING
        assert result.cause == TransitionCause.LOOP_LIMIT
        assert "上限" in result.reason

    def test_needs_human_ruling_takes_priority_over_loop_limit(self) -> None:
        """reviewer 主动升级人工的优先级最高。"""
        packet = _make_packet(max_rounds=2)
        state = _make_state(round_no=2)
        review = _make_review(verdict=TaskVerdict.NEEDS_HUMAN_RULING, ready=False)

        result = decide_after_review(packet, state, review)

        assert result.new_status == TaskStatus.NEEDS_HUMAN_RULING
        assert result.cause == TransitionCause.REVIEWER_ESCALATION
        # reason 应来自 reviewer 升级，而非 loop 超限
        assert "reviewer" in result.reason or "可靠" in result.reason

    def test_clean_but_not_ready_goes_to_human_ruling(self) -> None:
        """clean 但 readiness=false → 兜底升级人工。"""
        packet = _make_packet()
        state = _make_state()
        review = _make_review(verdict=TaskVerdict.CLEAN, ready=False)

        result = decide_after_review(packet, state, review)

        assert result.new_status == TaskStatus.NEEDS_HUMAN_RULING
        assert result.cause == TransitionCause.REVIEWER_ESCALATION


# ═══════════════════════════════════════════════════
# 跃迁表合法性
# ═══════════════════════════════════════════════════


class TestValidTransitions:
    """跃迁表合法性测试。"""

    def test_all_statuses_have_entries(self) -> None:
        """每个状态在跃迁表中都有定义。"""
        for status in TaskStatus:
            assert status in VALID_TRANSITIONS, f"{status} missing from transition table"

    def test_terminal_states_have_no_transitions(self) -> None:
        """终态不可跃迁。"""
        terminal = {TaskStatus.DONE, TaskStatus.NEEDS_HUMAN_RULING, TaskStatus.BLOCKED}
        for status in terminal:
            assert VALID_TRANSITIONS[status] == set(), f"{status} should be terminal"

    def test_normal_flow_is_valid(self) -> None:
        """正常流路径全部合法。"""
        flow = [
            (TaskStatus.NEW, TaskStatus.CODING),
            (TaskStatus.CODING, TaskStatus.REVIEWING),
            (TaskStatus.REVIEWING, TaskStatus.REVIEW_CLEAN),
            (TaskStatus.REVIEW_CLEAN, TaskStatus.HUMAN_REVIEW),
            (TaskStatus.HUMAN_REVIEW, TaskStatus.DONE),
        ]
        for from_s, to_s in flow:
            assert to_s in VALID_TRANSITIONS[from_s], f"{from_s} -> {to_s} should be valid"

    def test_fix_loop_is_valid(self) -> None:
        """修复回环路径合法。"""
        assert TaskStatus.NEEDS_FIX in VALID_TRANSITIONS[TaskStatus.REVIEWING]
        assert TaskStatus.CODING in VALID_TRANSITIONS[TaskStatus.NEEDS_FIX]

    def test_any_to_needs_human_ruling_is_valid(self) -> None:
        """非终态 → NEEDS_HUMAN_RULING 都合法。"""
        non_terminal = {
            TaskStatus.NEW,
            TaskStatus.CODING,
            TaskStatus.REVIEWING,
            TaskStatus.NEEDS_FIX,
            TaskStatus.REVIEW_CLEAN,
            TaskStatus.HUMAN_REVIEW,
        }
        for status in non_terminal:
            assert TaskStatus.NEEDS_HUMAN_RULING in VALID_TRANSITIONS[status]


# ═══════════════════════════════════════════════════
# apply_transition
# ═══════════════════════════════════════════════════


class TestApplyTransition:
    """apply_transition 测试。"""

    def test_valid_transition_updates_state(self) -> None:
        state = _make_state(status=TaskStatus.REVIEWING)
        result = TransitionResult(
            new_status=TaskStatus.NEEDS_FIX,
            next_action=NextAction.RUN_CODER,
            cause=TransitionCause.REVIEW_FINDINGS,
            reviewer_result_expected=True,
            reason="blocking findings",
        )
        new_state = apply_transition(state, result, reviewer_result_ref="r1_review.json")
        assert new_state.current_status == TaskStatus.NEEDS_FIX
        assert new_state.next_action == NextAction.RUN_CODER
        # 原 state 不变（不可变验证）
        assert state.current_status == TaskStatus.REVIEWING

    def test_invalid_transition_raises(self) -> None:
        state = _make_state(status=TaskStatus.NEW)
        result = TransitionResult(
            new_status=TaskStatus.DONE,  # NEW -> DONE 非法
            next_action=NextAction.NONE,
            cause=TransitionCause.HUMAN_APPROVAL,
        )
        with pytest.raises(TransitionError):
            apply_transition(state, result)

    def test_terminal_state_transition_raises(self) -> None:
        state = _make_state(status=TaskStatus.DONE)
        result = TransitionResult(
            new_status=TaskStatus.CODING,
            next_action=NextAction.RUN_CODER,
            cause=TransitionCause.RETURN_TO_CODER,
        )
        with pytest.raises(TransitionError):
            apply_transition(state, result)

    def test_new_to_blocked_early_abort(self) -> None:
        """NEW → BLOCKED: 未开轮即异常终止，round_no 保持 0。"""
        state = TaskState(task_id="early_block")
        assert state.current_status == TaskStatus.NEW
        assert state.round_no == 0

        result = TransitionResult(
            new_status=TaskStatus.BLOCKED,
            next_action=NextAction.RESOLVE_BLOCKED,
            cause=TransitionCause.EXTERNAL_BLOCK,
        )
        new = apply_transition(state, result)
        assert new.current_status == TaskStatus.BLOCKED
        assert new.round_no == 0
        assert new.rounds == []

    def test_new_to_needs_human_ruling_early_abort(self) -> None:
        """NEW → NEEDS_HUMAN_RULING: 未开轮即需人工裁决，round_no 保持 0。"""
        state = TaskState(task_id="early_ruling")
        assert state.current_status == TaskStatus.NEW
        assert state.round_no == 0

        result = TransitionResult(
            new_status=TaskStatus.NEEDS_HUMAN_RULING,
            next_action=NextAction.WAIT_HUMAN_RULING,
            cause=TransitionCause.EXTERNAL_BLOCK,
        )
        # notification 由 __post_init__ 自动填充
        assert result.notification == "needs_human_ruling"
        new = apply_transition(state, result)
        assert new.current_status == TaskStatus.NEEDS_HUMAN_RULING
        assert new.round_no == 0
        assert new.rounds == []
        assert new.pending_notification == "needs_human_ruling"


# ═══════════════════════════════════════════════════
# 便利函数：完整生命周期
# ═══════════════════════════════════════════════════


class TestLifecycleFunctions:
    """便利函数覆盖完整生命周期路径。"""

    def test_happy_path_lifecycle(self) -> None:
        """NEW → CODING → REVIEWING → REVIEW_CLEAN → HUMAN_REVIEW → DONE。"""
        state = TaskState(task_id="lifecycle_test")
        assert state.current_status == TaskStatus.NEW
        assert state.rounds == []

        # NEW → CODING: 创建第一轮
        state = start_task(state)
        assert state.current_status == TaskStatus.CODING
        assert state.round_no == 1
        assert len(state.rounds) == 1
        assert state.rounds[0].round_no == 1
        assert state.rounds[0].coder_result_ref is None

        # CODING → REVIEWING: 绑定 coder_result_ref
        state = coder_done(state, coder_result_ref="runs/lifecycle_test/r1_coder.json")
        assert state.current_status == TaskStatus.REVIEWING
        assert state.rounds[0].coder_result_ref == "runs/lifecycle_test/r1_coder.json"

        # REVIEWING → REVIEW_CLEAN (via decide_after_review + apply): 绑定 reviewer + 关闭当轮
        packet = _make_packet()
        review = _make_review(verdict=TaskVerdict.CLEAN, ready=True)
        decision = decide_after_review(packet, state, review)
        state = apply_transition(
            state, decision, reviewer_result_ref="runs/lifecycle_test/r1_review.json"
        )
        assert state.current_status == TaskStatus.REVIEW_CLEAN
        assert state.rounds[0].reviewer_result_ref == "runs/lifecycle_test/r1_review.json"
        assert state.rounds[0].finished_at is not None  # 从 REVIEWING 出去即关闭

        # REVIEW_CLEAN → HUMAN_REVIEW
        # 通知不应被覆盖：文档法定事件 review_clean_ready_for_human 保持不变
        state = enter_human_review(state)
        assert state.current_status == TaskStatus.HUMAN_REVIEW
        assert state.pending_notification == "review_clean_ready_for_human"

        # HUMAN_REVIEW → DONE: 轮次已关闭，approve 不再重复关
        state = approve_human_review(state, closure_summary="P1 完成")
        assert state.current_status == TaskStatus.DONE
        assert state.closure_summary == "P1 完成"
        assert state.pending_notification == "task_done"
        assert len(state.rounds) == 1

    def test_fix_loop_lifecycle(self) -> None:
        """REVIEWING → NEEDS_FIX → CODING → REVIEWING（修复回环 + rounds 台账）。"""
        state = TaskState(task_id="fix_loop_test")
        state = start_task(state)
        state = coder_done(state, coder_result_ref="r1_coder.json")
        assert state.current_status == TaskStatus.REVIEWING
        assert len(state.rounds) == 1

        # REVIEWING → NEEDS_FIX (via decide_after_review): 绑定 reviewer + 关闭当轮
        packet = _make_packet()
        review = _make_review(verdict=TaskVerdict.NEEDS_FIX, ready=False, blocking_findings=1)
        decision = decide_after_review(packet, state, review)
        state = apply_transition(state, decision, reviewer_result_ref="r1_review.json")
        assert state.current_status == TaskStatus.NEEDS_FIX
        assert state.rounds[0].reviewer_result_ref == "r1_review.json"
        assert state.rounds[0].finished_at is not None  # 从 REVIEWING 出去即关闭

        # NEEDS_FIX → CODING: 第 1 轮已关闭，只开新轮
        state = needs_fix_to_coding(state)
        assert state.current_status == TaskStatus.CODING
        assert state.round_no == 2
        assert len(state.rounds) == 2
        assert state.rounds[1].round_no == 2
        assert state.rounds[1].finished_at is None  # 第 2 轮进行中

        # 再跑一轮
        state = coder_done(state, coder_result_ref="r2_coder.json")
        assert state.current_status == TaskStatus.REVIEWING
        assert state.rounds[1].coder_result_ref == "r2_coder.json"

    def test_start_task_from_non_new_raises(self) -> None:
        state = _make_state(status=TaskStatus.CODING)
        with pytest.raises(TransitionError):
            start_task(state)

    def test_coder_done_from_non_coding_raises(self) -> None:
        state = _make_state(status=TaskStatus.REVIEWING)
        with pytest.raises(TransitionError):
            coder_done(state, coder_result_ref="dummy.json")

    def test_approve_from_non_human_review_raises(self) -> None:
        state = _make_state(status=TaskStatus.REVIEW_CLEAN)
        with pytest.raises(TransitionError):
            approve_human_review(state)

    def test_needs_fix_to_coding_from_wrong_state_raises(self) -> None:
        state = _make_state(status=TaskStatus.REVIEWING)
        with pytest.raises(TransitionError):
            needs_fix_to_coding(state)

    def test_coder_done_requires_ref(self) -> None:
        """台账合同：coder_done 必须提供 coder_result_ref。"""
        state = TaskState(task_id="ref_test")
        state = start_task(state)
        with pytest.raises(TypeError):
            coder_done(state)  # type: ignore[call-arg]

    def test_apply_transition_from_reviewing_requires_reviewer_ref(self) -> None:
        """台账合同：从 REVIEWING 跃迁时必须提供 reviewer_result_ref。"""
        state = TaskState(task_id="ref_test")
        state = start_task(state)
        state = coder_done(state, coder_result_ref="coder.json")
        packet = _make_packet()
        review = _make_review(verdict=TaskVerdict.CLEAN, ready=True)
        decision = decide_after_review(packet, state, review)
        with pytest.raises(ValueError, match="reviewer_result_ref"):
            apply_transition(state, decision)  # 缺 reviewer_result_ref

    def test_needs_human_ruling_lifecycle(self) -> None:
        """REVIEWING → NEEDS_HUMAN_RULING: reviewer 无法判断，轮次应在此关闭。"""
        state = TaskState(task_id="human_ruling_test")
        state = start_task(state)
        state = coder_done(state, coder_result_ref="r1_coder.json")
        assert state.current_status == TaskStatus.REVIEWING

        # REVIEWING → NEEDS_HUMAN_RULING
        packet = _make_packet()
        review = _make_review(verdict=TaskVerdict.NEEDS_HUMAN_RULING)
        decision = decide_after_review(packet, state, review)
        state = apply_transition(state, decision, reviewer_result_ref="r1_review.json")
        assert state.current_status == TaskStatus.NEEDS_HUMAN_RULING
        assert state.next_action == NextAction.WAIT_HUMAN_RULING
        # 台账完整：reviewer ref 绑定 + 轮次关闭
        assert len(state.rounds) == 1
        assert state.rounds[0].coder_result_ref == "r1_coder.json"
        assert state.rounds[0].reviewer_result_ref == "r1_review.json"
        assert state.rounds[0].finished_at is not None


# ═══════════════════════════════════════════════════
# 回归：transition helpers 必须执法 rounds 不变式
# ═══════════════════════════════════════════════════


class TestTransitionEnforcesInvariant:
    """验证 _validated_copy 让 transition helpers 拦截不一致状态。

    Pydantic v2 的 model_copy(update=...) 不重跑 model_validator，
    所以必须通过 _validated_copy 强制重建。这组测试确保该路径生效。
    """

    def test_coder_done_on_inconsistent_state_raises(self) -> None:
        """round_no=1 + rounds=[] 的 CODING state 经 coder_done 应被拦截。"""
        # 绕过 validator 构造不一致 state（模拟 model_copy 遗留场景）
        now = datetime.now(UTC)
        bad_state = TaskState.model_construct(
            task_id="bad",
            current_status=TaskStatus.CODING,
            round_no=1,
            rounds=[],
            next_action=NextAction.RUN_CODER,
            pending_notification=None,
            closure_summary="",
            created_at=now,
            updated_at=now,
        )
        # coder_done 内部 _validated_copy 应捕获不一致
        with pytest.raises(Exception, match="台账必须完整"):
            coder_done(bad_state, coder_result_ref="coder.json")

    def test_apply_transition_on_inconsistent_state_raises(self) -> None:
        """round_no=1 + rounds=[] 的 REVIEWING state 经 apply_transition 应被拦截。"""
        now = datetime.now(UTC)
        bad_state = TaskState.model_construct(
            task_id="bad",
            current_status=TaskStatus.REVIEWING,
            round_no=1,
            rounds=[],
            next_action=NextAction.RUN_REVIEWER,
            pending_notification=None,
            closure_summary="",
            created_at=now,
            updated_at=now,
        )
        result = TransitionResult(
            new_status=TaskStatus.NEEDS_FIX,
            next_action=NextAction.RUN_CODER,
            cause=TransitionCause.REVIEW_FINDINGS,
            reviewer_result_expected=True,
            reason="test",
        )
        with pytest.raises(Exception, match="台账必须完整"):
            apply_transition(bad_state, result, reviewer_result_ref="r1.json")


# ═══════════════════════════════════════════════════
# reviewer-driven / non-reviewer-driven 矩阵测试
# ═══════════════════════════════════════════════════


class TestReviewerResultExpected:
    """reviewer_result_ref 是否必填由 reviewer_result_expected 决定。

    两个正交维度：
    - cause: 业务语义（为什么跳转）
    - reviewer_result_expected: 是否来自真实 reviewer 输出（决定 ref 合同）

    矩阵覆盖：
    - reviewer_result_expected=True + 缺 ref → 报错（含 LOOP_LIMIT）
    - reviewer_result_expected=True + 有 ref → 通过 + round 关闭
    - reviewer_result_expected=False + 无 ref → 通过 + round 关闭
    """

    def _reviewing_state(self) -> TaskState:
        state = TaskState(task_id="matrix_test")
        state = start_task(state)
        return coder_done(state, coder_result_ref="r1_coder.json")

    # ── expected=True + 缺 ref → 报错 ──

    def test_review_findings_expected_missing_ref_raises(self) -> None:
        state = self._reviewing_state()
        result = TransitionResult(
            new_status=TaskStatus.NEEDS_FIX,
            next_action=NextAction.RUN_CODER,
            cause=TransitionCause.REVIEW_FINDINGS,
            reviewer_result_expected=True,
        )
        with pytest.raises(ValueError, match="reviewer_result_ref"):
            apply_transition(state, result)

    def test_review_clean_expected_missing_ref_raises(self) -> None:
        state = self._reviewing_state()
        result = TransitionResult(
            new_status=TaskStatus.REVIEW_CLEAN,
            next_action=NextAction.WAIT_HUMAN_REVIEW,
            cause=TransitionCause.REVIEW_CLEAN,
            reviewer_result_expected=True,
        )
        with pytest.raises(ValueError, match="reviewer_result_ref"):
            apply_transition(state, result)

    def test_reviewer_escalation_expected_missing_ref_raises(self) -> None:
        state = self._reviewing_state()
        result = TransitionResult(
            new_status=TaskStatus.NEEDS_HUMAN_RULING,
            next_action=NextAction.WAIT_HUMAN_RULING,
            cause=TransitionCause.REVIEWER_ESCALATION,
            reviewer_result_expected=True,
        )
        with pytest.raises(ValueError, match="reviewer_result_ref"):
            apply_transition(state, result)

    def test_loop_limit_expected_missing_ref_raises(self) -> None:
        """LOOP_LIMIT 也来自 decide_after_review，reviewer 工件已存在。"""
        state = self._reviewing_state()
        result = TransitionResult(
            new_status=TaskStatus.NEEDS_HUMAN_RULING,
            next_action=NextAction.WAIT_HUMAN_RULING,
            cause=TransitionCause.LOOP_LIMIT,
            reviewer_result_expected=True,
        )
        with pytest.raises(ValueError, match="reviewer_result_ref"):
            apply_transition(state, result)

    # ── expected=True + 有 ref → 通过 + round 关闭 ──

    def test_review_findings_expected_with_ref_passes(self) -> None:
        state = self._reviewing_state()
        result = TransitionResult(
            new_status=TaskStatus.NEEDS_FIX,
            next_action=NextAction.RUN_CODER,
            cause=TransitionCause.REVIEW_FINDINGS,
            reviewer_result_expected=True,
        )
        new = apply_transition(state, result, reviewer_result_ref="r.json")
        assert new.current_status == TaskStatus.NEEDS_FIX
        assert new.rounds[0].reviewer_result_ref == "r.json"
        assert new.rounds[0].finished_at is not None

    def test_review_clean_expected_with_ref_passes(self) -> None:
        state = self._reviewing_state()
        result = TransitionResult(
            new_status=TaskStatus.REVIEW_CLEAN,
            next_action=NextAction.WAIT_HUMAN_REVIEW,
            cause=TransitionCause.REVIEW_CLEAN,
            reviewer_result_expected=True,
        )
        new = apply_transition(state, result, reviewer_result_ref="r.json")
        assert new.current_status == TaskStatus.REVIEW_CLEAN
        assert new.rounds[0].reviewer_result_ref == "r.json"
        assert new.rounds[0].finished_at is not None

    def test_loop_limit_expected_with_ref_passes(self) -> None:
        """LOOP_LIMIT + reviewer_result_expected=True + 有 ref → 台账完整。"""
        state = self._reviewing_state()
        result = TransitionResult(
            new_status=TaskStatus.NEEDS_HUMAN_RULING,
            next_action=NextAction.WAIT_HUMAN_RULING,
            cause=TransitionCause.LOOP_LIMIT,
            reviewer_result_expected=True,
        )
        new = apply_transition(state, result, reviewer_result_ref="r.json")
        assert new.current_status == TaskStatus.NEEDS_HUMAN_RULING
        assert new.rounds[0].reviewer_result_ref == "r.json"
        assert new.rounds[0].finished_at is not None

    # ── expected=False + 无 ref → 通过 + round 关闭 ──

    def test_external_block_not_expected_no_ref_passes(self) -> None:
        """REVIEWING → BLOCKED，外部阻塞无 reviewer 产出。"""
        state = self._reviewing_state()
        result = TransitionResult(
            new_status=TaskStatus.BLOCKED,
            next_action=NextAction.RESOLVE_BLOCKED,
            cause=TransitionCause.EXTERNAL_BLOCK,
            reviewer_result_expected=False,
        )
        new = apply_transition(state, result)
        assert new.current_status == TaskStatus.BLOCKED
        assert new.rounds[0].reviewer_result_ref is None
        assert new.rounds[0].finished_at is not None

    # ── expected=False + 有 ref → 报错（禁止污染台账） ──

    def test_not_expected_but_ref_provided_raises(self) -> None:
        """non-reviewer 路径传入 reviewer_result_ref 应被拒绝。"""
        state = self._reviewing_state()
        result = TransitionResult(
            new_status=TaskStatus.BLOCKED,
            next_action=NextAction.RESOLVE_BLOCKED,
            cause=TransitionCause.EXTERNAL_BLOCK,
            reviewer_result_expected=False,
        )
        with pytest.raises(ValueError, match="不应提供 reviewer_result_ref"):
            apply_transition(state, result, reviewer_result_ref="invented.json")

    # ── decide_after_review 所有路径都设 expected=True ──

    def test_decide_after_review_always_expects_ref(self) -> None:
        """decide_after_review 的所有裁决路径都标记 reviewer_result_expected=True。"""
        packet = _make_packet(max_rounds=2)
        state = _make_state(round_no=2)  # 触发 LOOP_LIMIT
        review = _make_review(verdict=TaskVerdict.NEEDS_FIX, ready=False)
        result = decide_after_review(packet, state, review)
        assert result.cause == TransitionCause.LOOP_LIMIT
        assert result.reviewer_result_expected is True


# ═══════════════════════════════════════════════════
# TransitionResult 不变式：cause 与 reviewer_result_expected 一致性
# ═══════════════════════════════════════════════════


class TestTransitionResultInvariant:
    """TransitionResult 禁止 cause 与 reviewer_result_expected 矛盾。"""

    # ── post-review cause + expected=False → 报错 ──

    def test_review_findings_with_false_raises(self) -> None:
        with pytest.raises(ValueError, match="post-review"):
            TransitionResult(
                new_status=TaskStatus.NEEDS_FIX,
                next_action=NextAction.RUN_CODER,
                cause=TransitionCause.REVIEW_FINDINGS,
                reviewer_result_expected=False,
            )

    def test_review_clean_with_false_raises(self) -> None:
        with pytest.raises(ValueError, match="post-review"):
            TransitionResult(
                new_status=TaskStatus.REVIEW_CLEAN,
                next_action=NextAction.WAIT_HUMAN_REVIEW,
                cause=TransitionCause.REVIEW_CLEAN,
                reviewer_result_expected=False,
            )

    def test_reviewer_escalation_with_false_raises(self) -> None:
        with pytest.raises(ValueError, match="post-review"):
            TransitionResult(
                new_status=TaskStatus.NEEDS_HUMAN_RULING,
                next_action=NextAction.WAIT_HUMAN_RULING,
                cause=TransitionCause.REVIEWER_ESCALATION,
                reviewer_result_expected=False,
            )

    def test_loop_limit_with_false_raises(self) -> None:
        with pytest.raises(ValueError, match="post-review"):
            TransitionResult(
                new_status=TaskStatus.NEEDS_HUMAN_RULING,
                next_action=NextAction.WAIT_HUMAN_RULING,
                cause=TransitionCause.LOOP_LIMIT,
                reviewer_result_expected=False,
            )

    # ── non-reviewer cause + expected=True → 报错 ──

    def test_external_block_with_true_raises(self) -> None:
        with pytest.raises(ValueError, match="非 reviewer"):
            TransitionResult(
                new_status=TaskStatus.BLOCKED,
                next_action=NextAction.RESOLVE_BLOCKED,
                cause=TransitionCause.EXTERNAL_BLOCK,
                reviewer_result_expected=True,
            )

    def test_controller_start_with_true_raises(self) -> None:
        with pytest.raises(ValueError, match="非 reviewer"):
            TransitionResult(
                new_status=TaskStatus.CODING,
                next_action=NextAction.RUN_CODER,
                cause=TransitionCause.CONTROLLER_START,
                reviewer_result_expected=True,
            )

    # ── 合法组合正常构造 ──

    def test_review_findings_with_true_ok(self) -> None:
        r = TransitionResult(
            new_status=TaskStatus.NEEDS_FIX,
            next_action=NextAction.RUN_CODER,
            cause=TransitionCause.REVIEW_FINDINGS,
            reviewer_result_expected=True,
        )
        assert r.reviewer_result_expected is True

    def test_external_block_with_false_ok(self) -> None:
        r = TransitionResult(
            new_status=TaskStatus.BLOCKED,
            next_action=NextAction.RESOLVE_BLOCKED,
            cause=TransitionCause.EXTERNAL_BLOCK,
            reviewer_result_expected=False,
        )
        assert r.reviewer_result_expected is False

    # ── new_status ↔ next_action 校验 ──

    def test_blocked_with_run_coder_rejected(self) -> None:
        """BLOCKED + RUN_CODER 矛盾，构造时即被拒。"""
        with pytest.raises(ValueError, match="next_action 必须为"):
            TransitionResult(
                new_status=TaskStatus.BLOCKED,
                next_action=NextAction.RUN_CODER,
                cause=TransitionCause.EXTERNAL_BLOCK,
            )

    def test_needs_human_ruling_with_run_coder_rejected(self) -> None:
        """NEEDS_HUMAN_RULING + RUN_CODER 矛盾，构造时即被拒。"""
        with pytest.raises(ValueError, match="next_action 必须为"):
            TransitionResult(
                new_status=TaskStatus.NEEDS_HUMAN_RULING,
                next_action=NextAction.RUN_CODER,
                cause=TransitionCause.EXTERNAL_BLOCK,
            )

    def test_done_with_run_reviewer_rejected(self) -> None:
        """DONE + RUN_REVIEWER 矛盾，构造时即被拒。"""
        with pytest.raises(ValueError, match="next_action 必须为"):
            TransitionResult(
                new_status=TaskStatus.DONE,
                next_action=NextAction.RUN_REVIEWER,
                cause=TransitionCause.HUMAN_APPROVAL,
            )

    # ── notification 自动填充 ──

    def test_needs_human_ruling_auto_fills_notification(self) -> None:
        """NEEDS_HUMAN_RULING 未指定 notification 时自动填充法定通知。"""
        r = TransitionResult(
            new_status=TaskStatus.NEEDS_HUMAN_RULING,
            next_action=NextAction.WAIT_HUMAN_RULING,
            cause=TransitionCause.EXTERNAL_BLOCK,
        )
        assert r.notification == "needs_human_ruling"

    def test_needs_human_ruling_wrong_notification_rejected(self) -> None:
        """NEEDS_HUMAN_RULING 显式指定不匹配通知被拒。"""
        with pytest.raises(ValueError, match="法定通知"):
            TransitionResult(
                new_status=TaskStatus.NEEDS_HUMAN_RULING,
                next_action=NextAction.WAIT_HUMAN_RULING,
                cause=TransitionCause.EXTERNAL_BLOCK,
                notification="task_done",
            )

    def test_needs_human_ruling_correct_notification_accepted(self) -> None:
        """NEEDS_HUMAN_RULING 显式指定法定值通过。"""
        r = TransitionResult(
            new_status=TaskStatus.NEEDS_HUMAN_RULING,
            next_action=NextAction.WAIT_HUMAN_RULING,
            cause=TransitionCause.EXTERNAL_BLOCK,
            notification="needs_human_ruling",
        )
        assert r.notification == "needs_human_ruling"

    def test_review_clean_auto_fills_notification(self) -> None:
        """REVIEW_CLEAN 未指定 notification 时自动填充法定通知。"""
        r = TransitionResult(
            new_status=TaskStatus.REVIEW_CLEAN,
            next_action=NextAction.WAIT_HUMAN_REVIEW,
            cause=TransitionCause.REVIEW_CLEAN,
            reviewer_result_expected=True,
        )
        assert r.notification == "review_clean_ready_for_human"

    def test_review_clean_wrong_notification_rejected(self) -> None:
        """REVIEW_CLEAN 显式指定不匹配通知被拒。"""
        with pytest.raises(ValueError, match="法定通知"):
            TransitionResult(
                new_status=TaskStatus.REVIEW_CLEAN,
                next_action=NextAction.WAIT_HUMAN_REVIEW,
                cause=TransitionCause.REVIEW_CLEAN,
                reviewer_result_expected=True,
                notification="task_done",
            )

    def test_blocked_no_required_notification(self) -> None:
        """BLOCKED 无法定通知，notification 保持 None。"""
        r = TransitionResult(
            new_status=TaskStatus.BLOCKED,
            next_action=NextAction.RESOLVE_BLOCKED,
            cause=TransitionCause.EXTERNAL_BLOCK,
        )
        assert r.notification is None

    def test_blocked_allows_arbitrary_notification(self) -> None:
        """BLOCKED 不在法定映射中，允许自由 notification。"""
        r = TransitionResult(
            new_status=TaskStatus.BLOCKED,
            next_action=NextAction.RESOLVE_BLOCKED,
            cause=TransitionCause.EXTERNAL_BLOCK,
            notification="external_block_info",
        )
        assert r.notification == "external_block_info"

    # ── 两个集合互补穷尽所有 cause ──

    def test_cause_sets_exhaustive(self) -> None:
        """每个 TransitionCause 都必须出现在其中一个集合中。"""
        from automation.controller.transitions import (
            CAUSES_REQUIRING_REVIEWER_RESULT,
            CAUSES_WITHOUT_REVIEWER_RESULT,
        )

        all_causes = set(TransitionCause)
        covered = CAUSES_REQUIRING_REVIEWER_RESULT | CAUSES_WITHOUT_REVIEWER_RESULT
        assert covered == all_causes, f"未覆盖: {all_causes - covered}"
        overlap = CAUSES_REQUIRING_REVIEWER_RESULT & CAUSES_WITHOUT_REVIEWER_RESULT
        assert not overlap, f"重叠: {overlap}"

    # ── cause ↔ new_status 业务语义绑定 ──

    def test_external_block_to_review_clean_rejected(self) -> None:
        """EXTERNAL_BLOCK 不能产出 REVIEW_CLEAN（语义矛盾）。"""
        with pytest.raises(ValueError, match="不允许产出"):
            TransitionResult(
                new_status=TaskStatus.REVIEW_CLEAN,
                next_action=NextAction.WAIT_HUMAN_REVIEW,
                cause=TransitionCause.EXTERNAL_BLOCK,
            )

    def test_human_approval_to_needs_fix_rejected(self) -> None:
        """HUMAN_APPROVAL 不能产出 NEEDS_FIX（语义矛盾）。"""
        with pytest.raises(ValueError, match="不允许产出"):
            TransitionResult(
                new_status=TaskStatus.NEEDS_FIX,
                next_action=NextAction.RUN_CODER,
                cause=TransitionCause.HUMAN_APPROVAL,
            )

    def test_review_findings_to_review_clean_rejected(self) -> None:
        """REVIEW_FINDINGS 只能去 NEEDS_FIX，不能去 REVIEW_CLEAN。"""
        with pytest.raises(ValueError, match="不允许产出"):
            TransitionResult(
                new_status=TaskStatus.REVIEW_CLEAN,
                next_action=NextAction.WAIT_HUMAN_REVIEW,
                cause=TransitionCause.REVIEW_FINDINGS,
                reviewer_result_expected=True,
            )

    def test_cause_allowed_statuses_exhaustive(self) -> None:
        """CAUSE_ALLOWED_STATUSES 覆盖所有 TransitionCause。"""
        from automation.controller.transitions import CAUSE_ALLOWED_STATUSES

        assert set(CAUSE_ALLOWED_STATUSES.keys()) == set(TransitionCause), (
            f"未覆盖: {set(TransitionCause) - set(CAUSE_ALLOWED_STATUSES.keys())}"
        )


# ═══════════════════════════════════════════════════
# cause ↔ from_status 业务语义绑定
# ═══════════════════════════════════════════════════


class TestCauseFromStatusContract:
    """apply_transition 中 cause ↔ from_status 约束。"""

    def test_controller_start_from_needs_fix_rejected(self) -> None:
        """NEEDS_FIX → CODING 用 CONTROLLER_START 是语义错误（应为 RETURN_TO_CODER）。"""
        state = _make_state(status=TaskStatus.NEEDS_FIX)
        result = TransitionResult(
            new_status=TaskStatus.CODING,
            next_action=NextAction.RUN_CODER,
            cause=TransitionCause.CONTROLLER_START,
        )
        with pytest.raises(TransitionError, match="不存在合法规则"):
            apply_transition(state, result)

    def test_loop_limit_from_new_rejected(self) -> None:
        """NEW → NEEDS_HUMAN_RULING 用 LOOP_LIMIT 是语义错误（LOOP_LIMIT 仅从 REVIEWING）。"""
        state = _make_state(status=TaskStatus.NEW)
        result = TransitionResult(
            new_status=TaskStatus.NEEDS_HUMAN_RULING,
            next_action=NextAction.WAIT_HUMAN_RULING,
            cause=TransitionCause.LOOP_LIMIT,
            reviewer_result_expected=True,
        )
        with pytest.raises(TransitionError, match="不存在合法规则"):
            apply_transition(state, result, reviewer_result_ref="r.json")

    def test_human_approval_from_new_rejected(self) -> None:
        """HUMAN_APPROVAL 仅从 HUMAN_REVIEW 触发，NEW 不合法。"""
        state = _make_state(status=TaskStatus.NEW)
        result = TransitionResult(
            new_status=TaskStatus.DONE,
            next_action=NextAction.NONE,
            cause=TransitionCause.HUMAN_APPROVAL,
        )
        with pytest.raises(TransitionError, match="不存在合法规则"):
            apply_transition(state, result)

    def test_return_to_coder_from_new_rejected(self) -> None:
        """RETURN_TO_CODER 仅从 NEEDS_FIX 触发，NEW 不合法。"""
        state = _make_state(status=TaskStatus.NEW)
        result = TransitionResult(
            new_status=TaskStatus.CODING,
            next_action=NextAction.RUN_CODER,
            cause=TransitionCause.RETURN_TO_CODER,
        )
        with pytest.raises(TransitionError, match="不存在合法规则"):
            apply_transition(state, result)

    def test_review_findings_from_needs_fix_rejected(self) -> None:
        """REVIEW_FINDINGS 仅从 REVIEWING 触发，NEEDS_FIX 不合法。"""
        state = _make_state(status=TaskStatus.NEEDS_FIX)
        result = TransitionResult(
            new_status=TaskStatus.NEEDS_FIX,
            next_action=NextAction.RUN_CODER,
            cause=TransitionCause.REVIEW_FINDINGS,
            reviewer_result_expected=True,
        )
        with pytest.raises(TransitionError, match="不存在合法规则"):
            apply_transition(state, result, reviewer_result_ref="r.json")

    def test_external_block_from_reviewing_accepted(self) -> None:
        """EXTERNAL_BLOCK 从 REVIEWING 合法。"""
        state = _make_state(status=TaskStatus.REVIEWING)
        result = TransitionResult(
            new_status=TaskStatus.BLOCKED,
            next_action=NextAction.RESOLVE_BLOCKED,
            cause=TransitionCause.EXTERNAL_BLOCK,
        )
        new = apply_transition(state, result)
        assert new.current_status == TaskStatus.BLOCKED

    def test_cause_allowed_from_statuses_exhaustive(self) -> None:
        """CAUSE_ALLOWED_FROM_STATUSES 覆盖所有 TransitionCause。"""
        from automation.controller.transitions import CAUSE_ALLOWED_FROM_STATUSES

        assert set(CAUSE_ALLOWED_FROM_STATUSES.keys()) == set(TransitionCause), (
            f"未覆盖: {set(TransitionCause) - set(CAUSE_ALLOWED_FROM_STATUSES.keys())}"
        )

    # ── 验收: 以前漏掉的合法路径现在必须通过 ──

    def test_review_clean_to_blocked_accepted(self) -> None:
        """REVIEW_CLEAN → BLOCKED（外部阻塞）必须合法。"""
        state = _make_state(status=TaskStatus.REVIEW_CLEAN)
        result = TransitionResult(
            new_status=TaskStatus.BLOCKED,
            next_action=NextAction.RESOLVE_BLOCKED,
            cause=TransitionCause.EXTERNAL_BLOCK,
        )
        new = apply_transition(state, result)
        assert new.current_status == TaskStatus.BLOCKED

    def test_human_review_to_blocked_accepted(self) -> None:
        """HUMAN_REVIEW → BLOCKED（外部阻塞）必须合法。"""
        state = _make_state(status=TaskStatus.HUMAN_REVIEW)
        result = TransitionResult(
            new_status=TaskStatus.BLOCKED,
            next_action=NextAction.RESOLVE_BLOCKED,
            cause=TransitionCause.EXTERNAL_BLOCK,
        )
        new = apply_transition(state, result)
        assert new.current_status == TaskStatus.BLOCKED


# ═══════════════════════════════════════════════════
# 统一规则表一致性与真值表快照
# ═══════════════════════════════════════════════════


class TestTransitionRulesConsistency:
    """验证 TRANSITION_RULES 是全局唯一真相源，所有导出常量与之一致。"""

    def test_valid_transitions_derived_from_rules(self) -> None:
        """VALID_TRANSITIONS 必须完全等于从规则表推导的 (from, to) 集合。"""
        from automation.controller.transitions import TRANSITION_RULES, VALID_TRANSITIONS

        expected: dict[TaskStatus, set[TaskStatus]] = {s: set() for s in TaskStatus}
        for rule in TRANSITION_RULES:
            expected[rule.from_status].add(rule.to_status)
        assert expected == VALID_TRANSITIONS

    def test_cause_allowed_statuses_derived_from_rules(self) -> None:
        """CAUSE_ALLOWED_STATUSES 必须完全等于从规则表推导的 cause→{to_status}。"""
        from automation.controller.transitions import (
            CAUSE_ALLOWED_STATUSES,
            TRANSITION_RULES,
        )

        expected: dict[TransitionCause, set[TaskStatus]] = {}
        for rule in TRANSITION_RULES:
            if rule.cause is not None:
                expected.setdefault(rule.cause, set()).add(rule.to_status)
        assert {c: frozenset(s) for c, s in expected.items()} == CAUSE_ALLOWED_STATUSES

    def test_cause_allowed_from_statuses_derived_from_rules(self) -> None:
        """CAUSE_ALLOWED_FROM_STATUSES 必须完全等于从规则表推导的 cause→{from_status}。"""
        from automation.controller.transitions import (
            CAUSE_ALLOWED_FROM_STATUSES,
            TRANSITION_RULES,
        )

        expected: dict[TransitionCause, set[TaskStatus]] = {}
        for rule in TRANSITION_RULES:
            if rule.cause is not None:
                expected.setdefault(rule.cause, set()).add(rule.from_status)
        assert {c: frozenset(s) for c, s in expected.items()} == CAUSE_ALLOWED_FROM_STATUSES

    def test_reviewer_result_sets_derived_from_rules(self) -> None:
        """CAUSES_REQUIRING/WITHOUT 必须从规则表推导，且每个 cause 唯一归属。"""
        from automation.controller.transitions import (
            CAUSES_REQUIRING_REVIEWER_RESULT,
            CAUSES_WITHOUT_REVIEWER_RESULT,
            TRANSITION_RULES,
        )

        requiring: set[TransitionCause] = set()
        without: set[TransitionCause] = set()
        for rule in TRANSITION_RULES:
            if rule.cause is None:
                continue
            (requiring if rule.reviewer_result_expected else without).add(rule.cause)
        assert frozenset(requiring) == CAUSES_REQUIRING_REVIEWER_RESULT
        assert frozenset(without) == CAUSES_WITHOUT_REVIEWER_RESULT
        assert not requiring & without, "一个 cause 不能同时要求和不要求 reviewer_result"

    def test_required_notification_derived_from_rules(self) -> None:
        """TRANSITION_REQUIRED_NOTIFICATION 必须从规则表推导，同一 to_status 值唯一。"""
        from automation.controller.transitions import (
            TRANSITION_REQUIRED_NOTIFICATION,
            TRANSITION_RULES,
        )

        expected: dict[TaskStatus, str] = {}
        for rule in TRANSITION_RULES:
            if rule.required_notification is not None:
                existing = expected.get(rule.to_status)
                if existing is not None:
                    assert existing == rule.required_notification, f"{rule.to_status} 法定通知冲突"
                expected[rule.to_status] = rule.required_notification
        assert expected == TRANSITION_REQUIRED_NOTIFICATION

    def test_no_duplicate_rules(self) -> None:
        """同一 (from_status, cause, to_status) 不允许出现多条规则。"""
        from automation.controller.transitions import TRANSITION_RULES

        seen: set[tuple[TaskStatus, TransitionCause | None, TaskStatus]] = set()
        for rule in TRANSITION_RULES:
            key = (rule.from_status, rule.cause, rule.to_status)
            assert key not in seen, f"重复规则: {key}"
            seen.add(key)

    def test_all_causes_covered(self) -> None:
        """每个 TransitionCause 至少出现在一条规则中。"""
        from automation.controller.transitions import TRANSITION_RULES

        covered = {rule.cause for rule in TRANSITION_RULES if rule.cause is not None}
        assert covered == set(TransitionCause), f"未覆盖: {set(TransitionCause) - covered}"

    def test_truth_table_snapshot(self) -> None:
        """真值表快照：(from, cause, to) 的完整集合，漏改即红。"""
        from automation.controller.transitions import TRANSITION_RULES

        actual: set[tuple[str, str | None, str]] = {
            (r.from_status.value, r.cause.value if r.cause else None, r.to_status.value)
            for r in TRANSITION_RULES
        }
        expected: set[tuple[str, str | None, str]] = {
            # controller 调度
            ("NEW", "controller_start", "CODING"),
            ("NEEDS_FIX", "return_to_coder", "CODING"),
            # helper-only: coder 产出
            ("CODING", None, "REVIEWING"),
            # reviewer 产出
            ("REVIEWING", "review_findings", "NEEDS_FIX"),
            ("REVIEWING", "review_clean", "REVIEW_CLEAN"),
            ("REVIEWING", "reviewer_escalation", "NEEDS_HUMAN_RULING"),
            ("REVIEWING", "loop_limit", "NEEDS_HUMAN_RULING"),
            # helper-only: 进入人工审查
            ("REVIEW_CLEAN", None, "HUMAN_REVIEW"),
            # 人工批准
            ("HUMAN_REVIEW", "human_approval", "DONE"),
            # 外部阻塞 → BLOCKED
            ("NEW", "external_block", "BLOCKED"),
            ("CODING", "external_block", "BLOCKED"),
            ("REVIEWING", "external_block", "BLOCKED"),
            ("NEEDS_FIX", "external_block", "BLOCKED"),
            ("REVIEW_CLEAN", "external_block", "BLOCKED"),
            ("HUMAN_REVIEW", "external_block", "BLOCKED"),
            # 外部阻塞 → NEEDS_HUMAN_RULING
            ("NEW", "external_block", "NEEDS_HUMAN_RULING"),
            ("CODING", "external_block", "NEEDS_HUMAN_RULING"),
            ("REVIEWING", "external_block", "NEEDS_HUMAN_RULING"),
            ("NEEDS_FIX", "external_block", "NEEDS_HUMAN_RULING"),
            ("REVIEW_CLEAN", "external_block", "NEEDS_HUMAN_RULING"),
            ("HUMAN_REVIEW", "external_block", "NEEDS_HUMAN_RULING"),
        }
        assert actual == expected, (
            f"差异:\n  多出: {actual - expected}\n  缺失: {expected - actual}"
        )
