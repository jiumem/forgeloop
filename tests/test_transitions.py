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

import pytest

from automation.controller.transitions import (
    VALID_TRANSITIONS,
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
from schemas.task_state import NextAction, TaskState, TaskStatus

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
    round_no: int = 1,
) -> TaskState:
    return TaskState(
        task_id="test_task",
        current_status=status,
        round_no=round_no,
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
        assert result.notification == "review_clean_ready_for_human"

    def test_needs_fix_goes_to_needs_fix(self) -> None:
        """verdict=needs_fix → NEEDS_FIX。"""
        packet = _make_packet()
        state = _make_state()
        review = _make_review(verdict=TaskVerdict.NEEDS_FIX, ready=False)

        result = decide_after_review(packet, state, review)

        assert result.new_status == TaskStatus.NEEDS_FIX
        assert result.next_action == NextAction.RUN_CODER

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

    def test_needs_human_ruling_goes_to_needs_human_ruling(self) -> None:
        """verdict=needs_human_ruling → NEEDS_HUMAN_RULING。"""
        packet = _make_packet()
        state = _make_state()
        review = _make_review(verdict=TaskVerdict.NEEDS_HUMAN_RULING, ready=False)

        result = decide_after_review(packet, state, review)

        assert result.new_status == TaskStatus.NEEDS_HUMAN_RULING
        assert result.next_action == NextAction.WAIT_HUMAN_RULING
        assert result.notification == "needs_human_ruling"

    def test_loop_over_limit_goes_to_needs_human_ruling(self) -> None:
        """loop 超限 → NEEDS_HUMAN_RULING（优先级高于 needs_fix）。"""
        packet = _make_packet(max_rounds=2)
        state = _make_state(round_no=2)  # 已达上限
        review = _make_review(verdict=TaskVerdict.NEEDS_FIX, ready=False)

        result = decide_after_review(packet, state, review)

        assert result.new_status == TaskStatus.NEEDS_HUMAN_RULING
        assert "上限" in result.reason

    def test_needs_human_ruling_takes_priority_over_loop_limit(self) -> None:
        """reviewer 主动升级人工的优先级最高。"""
        packet = _make_packet(max_rounds=2)
        state = _make_state(round_no=2)
        review = _make_review(verdict=TaskVerdict.NEEDS_HUMAN_RULING, ready=False)

        result = decide_after_review(packet, state, review)

        assert result.new_status == TaskStatus.NEEDS_HUMAN_RULING
        # reason 应来自 reviewer 升级，而非 loop 超限
        assert "reviewer" in result.reason or "可靠" in result.reason

    def test_clean_but_not_ready_goes_to_human_ruling(self) -> None:
        """clean 但 readiness=false → 兜底升级人工。"""
        packet = _make_packet()
        state = _make_state()
        review = _make_review(verdict=TaskVerdict.CLEAN, ready=False)

        result = decide_after_review(packet, state, review)

        assert result.new_status == TaskStatus.NEEDS_HUMAN_RULING


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
            reason="blocking findings",
        )
        new_state = apply_transition(state, result)
        assert new_state.current_status == TaskStatus.NEEDS_FIX
        assert new_state.next_action == NextAction.RUN_CODER
        # 原 state 不变（不可变验证）
        assert state.current_status == TaskStatus.REVIEWING

    def test_invalid_transition_raises(self) -> None:
        state = _make_state(status=TaskStatus.NEW)
        result = TransitionResult(
            new_status=TaskStatus.DONE,  # NEW -> DONE 非法
            next_action=NextAction.NONE,
        )
        with pytest.raises(TransitionError):
            apply_transition(state, result)

    def test_terminal_state_transition_raises(self) -> None:
        state = _make_state(status=TaskStatus.DONE)
        result = TransitionResult(
            new_status=TaskStatus.CODING,
            next_action=NextAction.RUN_CODER,
        )
        with pytest.raises(TransitionError):
            apply_transition(state, result)


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
            coder_done(state)

    def test_approve_from_non_human_review_raises(self) -> None:
        state = _make_state(status=TaskStatus.REVIEW_CLEAN)
        with pytest.raises(TransitionError):
            approve_human_review(state)

    def test_needs_fix_to_coding_from_wrong_state_raises(self) -> None:
        state = _make_state(status=TaskStatus.REVIEWING)
        with pytest.raises(TransitionError):
            needs_fix_to_coding(state)
