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
    LifecycleAction,
    ReviewScenario,
)

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

_A = LifecycleAction


class TestLifecycleScenarios:
    """用 P4 FullLifecycleScenario 验证端到端多步骤流程。

    每步是结构化 LifecycleStep，携带 action enum + scenario 绑定的 review_result。
    测试引擎根据 action 分派到对应的 transition 函数，无字符串匹配。
    """

    def _run_lifecycle(self, scenario: FullLifecycleScenario) -> None:
        """执行一个完整生命周期场景并逐步断言。"""
        from schemas.task_state import TaskState

        packet = scenario.task_packet
        state = TaskState(task_id=packet.task_id)

        for step in scenario.steps:
            if step.action == _A.START_TASK:
                state = start_task(state)
            elif step.action == _A.CODER_DONE:
                ref = f"runs/{packet.task_id}/r{state.round_no}_coder.json"
                state = coder_done(state, coder_result_ref=ref)
            elif step.action == _A.DECIDE_AFTER_REVIEW:
                assert step.review_result is not None, (
                    f"{scenario.name}: DECIDE_AFTER_REVIEW 缺少 review_result"
                )
                review = step.review_result.model_copy(
                    update={"task_id": packet.task_id, "round_no": state.round_no}
                )
                decision = decide_after_review(packet, state, review)
                ref = f"runs/{packet.task_id}/r{state.round_no}_review.json"
                state = apply_transition(state, decision, reviewer_result_ref=ref)
            elif step.action == _A.NEEDS_FIX_TO_CODING:
                state = needs_fix_to_coding(state)
            elif step.action == _A.ENTER_HUMAN_REVIEW:
                state = enter_human_review(state)
            elif step.action == _A.APPROVE_HUMAN_REVIEW:
                state = approve_human_review(state, closure_summary="lifecycle test done")
            else:  # pragma: no cover
                raise ValueError(f"Unknown action: {step.action}")

            assert state.current_status == step.expected_status, (
                f"{scenario.name} step {step.action.value}: "
                f"expected {step.expected_status}, got {state.current_status}"
            )

    def test_lifecycle_happy(self) -> None:
        self._run_lifecycle(LIFECYCLE_SCENARIOS["lifecycle_happy"])

    def test_lifecycle_one_fix(self) -> None:
        self._run_lifecycle(LIFECYCLE_SCENARIOS["lifecycle_one_fix"])

    def test_lifecycle_escalation(self) -> None:
        self._run_lifecycle(LIFECYCLE_SCENARIOS["lifecycle_escalation"])
