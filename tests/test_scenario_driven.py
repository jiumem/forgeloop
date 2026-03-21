"""tests/test_scenario_driven.py — P5 场景驱动状态机测试。

用 P4 mock/scenarios.py 的结构化 fixture 参数化驱动：
- decide_after_review() 裁决输出
- apply_transition() 跃迁合法性 + 台账完整性
- approve_human_review() 人工批准
- 端到端多步骤生命周期
"""

from __future__ import annotations

import pytest

from automation.controller.transitions import (
    apply_transition,
    approve_human_review,
    coder_done,
    decide_after_review,
    enter_human_review,
    needs_fix_to_coding,
    start_task,
)
from mock.scenarios import (
    APPROVAL_SCENARIOS,
    LIFECYCLE_SCENARIOS,
    REVIEW_SCENARIOS,
    ApprovalScenario,
    FullLifecycleScenario,
    ReviewScenario,
)
from schemas.review_result import ReviewResult

# ═══════════════════════════════════════════════════
# decide_after_review 参数化测试
# ═══════════════════════════════════════════════════

_REVIEW_IDS = list(REVIEW_SCENARIOS.keys())


class TestDecideAfterReviewScenarios:
    """用 P4 ReviewScenario 参数化验证 decide_after_review() 裁决。"""

    @pytest.fixture(params=_REVIEW_IDS)
    def scenario(self, request: pytest.FixtureRequest) -> ReviewScenario:
        return REVIEW_SCENARIOS[request.param]

    def test_new_status(self, scenario: ReviewScenario) -> None:
        """裁决产出的 new_status 与场景期望一致。"""
        result = decide_after_review(
            scenario.task_packet, scenario.task_state, scenario.review_result
        )
        assert result.new_status == scenario.expected_status, (
            f"{scenario.name}: expected {scenario.expected_status}, got {result.new_status}"
        )

    def test_cause(self, scenario: ReviewScenario) -> None:
        """裁决产出的 cause 与场景期望一致。"""
        result = decide_after_review(
            scenario.task_packet, scenario.task_state, scenario.review_result
        )
        assert result.cause == scenario.expected_cause, (
            f"{scenario.name}: expected {scenario.expected_cause}, got {result.cause}"
        )

    def test_notification(self, scenario: ReviewScenario) -> None:
        """裁决产出的 notification 与场景期望一致。"""
        result = decide_after_review(
            scenario.task_packet, scenario.task_state, scenario.review_result
        )
        assert result.notification == scenario.expected_notification, (
            f"{scenario.name}: expected {scenario.expected_notification!r}, "
            f"got {result.notification!r}"
        )

    def test_reviewer_result_always_expected(self, scenario: ReviewScenario) -> None:
        """decide_after_review 所有路径都标记 reviewer_result_expected=True。"""
        result = decide_after_review(
            scenario.task_packet, scenario.task_state, scenario.review_result
        )
        assert result.reviewer_result_expected is True, (
            f"{scenario.name}: reviewer_result_expected should be True"
        )


# ═══════════════════════════════════════════════════
# decide + apply 完整跃迁链
# ═══════════════════════════════════════════════════


class TestDecideAndApplyScenarios:
    """decide_after_review → apply_transition 全链路：跃迁合法 + 台账完整。"""

    @pytest.fixture(params=_REVIEW_IDS)
    def scenario(self, request: pytest.FixtureRequest) -> ReviewScenario:
        return REVIEW_SCENARIOS[request.param]

    def test_apply_succeeds(self, scenario: ReviewScenario) -> None:
        """decide 产出能被 apply_transition 接受（跃迁合法）。"""
        result = decide_after_review(
            scenario.task_packet, scenario.task_state, scenario.review_result
        )
        new_state = apply_transition(
            scenario.task_state,
            result,
            reviewer_result_ref=f"runs/{scenario.task_packet.task_id}/review.json",
        )
        assert new_state.current_status == scenario.expected_status

    def test_reviewer_ref_bound(self, scenario: ReviewScenario) -> None:
        """apply 后最后一轮的 reviewer_result_ref 已绑定。"""
        result = decide_after_review(
            scenario.task_packet, scenario.task_state, scenario.review_result
        )
        ref = f"runs/{scenario.task_packet.task_id}/review.json"
        new_state = apply_transition(scenario.task_state, result, reviewer_result_ref=ref)
        last_round = new_state.rounds[-1]
        assert last_round.reviewer_result_ref == ref

    def test_round_closed(self, scenario: ReviewScenario) -> None:
        """从 REVIEWING 出去的跃迁应关闭当前轮次。"""
        result = decide_after_review(
            scenario.task_packet, scenario.task_state, scenario.review_result
        )
        new_state = apply_transition(
            scenario.task_state,
            result,
            reviewer_result_ref=f"runs/{scenario.task_packet.task_id}/review.json",
        )
        last_round = new_state.rounds[-1]
        assert last_round.finished_at is not None, (
            f"{scenario.name}: round should be closed after leaving REVIEWING"
        )

    def test_pending_notification_set(self, scenario: ReviewScenario) -> None:
        """apply 后 pending_notification 应与 TransitionResult.notification 一致。"""
        result = decide_after_review(
            scenario.task_packet, scenario.task_state, scenario.review_result
        )
        new_state = apply_transition(
            scenario.task_state,
            result,
            reviewer_result_ref=f"runs/{scenario.task_packet.task_id}/review.json",
        )
        assert new_state.pending_notification == scenario.expected_notification


# ═══════════════════════════════════════════════════
# approve_human_review 参数化测试
# ═══════════════════════════════════════════════════

_APPROVAL_IDS = list(APPROVAL_SCENARIOS.keys())


class TestApprovalScenarios:
    """用 P4 ApprovalScenario 参数化验证 approve_human_review()。"""

    @pytest.fixture(params=_APPROVAL_IDS)
    def scenario(self, request: pytest.FixtureRequest) -> ApprovalScenario:
        return APPROVAL_SCENARIOS[request.param]

    def test_approve_reaches_done(self, scenario: ApprovalScenario) -> None:
        new_state = approve_human_review(
            scenario.task_state, closure_summary=scenario.closure_summary
        )
        assert new_state.current_status == scenario.expected_status

    def test_approve_notification(self, scenario: ApprovalScenario) -> None:
        new_state = approve_human_review(
            scenario.task_state, closure_summary=scenario.closure_summary
        )
        assert new_state.pending_notification == scenario.expected_notification

    def test_approve_closure_summary(self, scenario: ApprovalScenario) -> None:
        new_state = approve_human_review(
            scenario.task_state, closure_summary=scenario.closure_summary
        )
        assert new_state.closure_summary == scenario.closure_summary

    def test_approve_preserves_rounds(self, scenario: ApprovalScenario) -> None:
        """批准不应改变 rounds 台账（轮次已在 REVIEWING 出去时关闭）。"""
        new_state = approve_human_review(
            scenario.task_state, closure_summary=scenario.closure_summary
        )
        assert len(new_state.rounds) == len(scenario.task_state.rounds)


# ═══════════════════════════════════════════════════
# 端到端生命周期场景
# ═══════════════════════════════════════════════════

_LIFECYCLE_IDS = list(LIFECYCLE_SCENARIOS.keys())


def _make_clean_review(task_id: str, round_no: int) -> ReviewResult:
    """为 lifecycle 测试构造 clean review。"""
    from mock.sample_review_results import CLEAN_REVIEW

    return CLEAN_REVIEW.model_copy(update={"task_id": task_id, "round_no": round_no})


def _make_blocking_review(task_id: str, round_no: int) -> ReviewResult:
    """为 lifecycle 测试构造 blocking review。"""
    from mock.sample_review_results import BLOCKING_FINDING_REVIEW

    return BLOCKING_FINDING_REVIEW.model_copy(update={"task_id": task_id, "round_no": round_no})


def _make_escalation_review(task_id: str, round_no: int) -> ReviewResult:
    """为 lifecycle 测试构造 needs_human_ruling review。"""
    from mock.sample_review_results import NEEDS_HUMAN_RULING_REVIEW

    return NEEDS_HUMAN_RULING_REVIEW.model_copy(update={"task_id": task_id, "round_no": round_no})


class TestLifecycleScenarios:
    """用 P4 FullLifecycleScenario 验证端到端多步骤流程。

    每个 lifecycle scenario 的 steps 是 (动作描述, 期望状态) 序列。
    测试引擎根据动作描述分派到对应的 transition 函数。
    """

    def _run_lifecycle(self, scenario: FullLifecycleScenario) -> None:
        """执行一个完整生命周期场景并逐步断言。"""
        from schemas.task_state import TaskState

        packet = scenario.task_packet
        state = TaskState(task_id=packet.task_id)
        round_no = 0

        for step_desc, expected_status in scenario.steps:
            if step_desc == "start_task":
                state = start_task(state)
                round_no = state.round_no
            elif step_desc.startswith("coder_done"):
                ref = f"runs/{packet.task_id}/r{round_no}_coder.json"
                state = coder_done(state, coder_result_ref=ref)
            elif "decide_after_review" in step_desc:
                review = self._pick_review(step_desc, packet.task_id, round_no)
                decision = decide_after_review(packet, state, review)
                ref = f"runs/{packet.task_id}/r{round_no}_review.json"
                state = apply_transition(state, decision, reviewer_result_ref=ref)
            elif step_desc == "needs_fix_to_coding":
                state = needs_fix_to_coding(state)
                round_no = state.round_no
            elif step_desc == "enter_human_review":
                state = enter_human_review(state)
            elif step_desc == "approve_human_review":
                state = approve_human_review(state, closure_summary="lifecycle test done")
            else:
                raise ValueError(f"Unknown step: {step_desc}")

            assert state.current_status == expected_status, (
                f"{scenario.name} step '{step_desc}': "
                f"expected {expected_status}, got {state.current_status}"
            )

    @staticmethod
    def _pick_review(step_desc: str, task_id: str, round_no: int) -> ReviewResult:
        """根据 step 描述选择对应的 ReviewResult。"""
        if "clean" in step_desc:
            return _make_clean_review(task_id, round_no)
        elif "blocking" in step_desc:
            return _make_blocking_review(task_id, round_no)
        elif "needs_human_ruling" in step_desc:
            return _make_escalation_review(task_id, round_no)
        raise ValueError(f"Cannot pick review for: {step_desc}")

    def test_lifecycle_happy(self) -> None:
        self._run_lifecycle(LIFECYCLE_SCENARIOS["lifecycle_happy"])

    def test_lifecycle_one_fix(self) -> None:
        self._run_lifecycle(LIFECYCLE_SCENARIOS["lifecycle_one_fix"])

    def test_lifecycle_escalation(self) -> None:
        self._run_lifecycle(LIFECYCLE_SCENARIOS["lifecycle_escalation"])
