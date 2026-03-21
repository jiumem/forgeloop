"""mock 场景定义 — P4_mock_scenarios 的核心产出。

每个 Scenario 把输入（task_packet + task_state + review_result）
与期望输出（new_status + cause + notification）绑定在一起，
形成可直接用于 P5 状态机测试的 fixture。

规划文档 §5.3 M2-1 要求的六个最低剧本：
1. HAPPY_PATH: coder 成功，reviewer clean → REVIEW_CLEAN
2. BLOCKING_FINDING: reviewer 给出 in-scope blocking finding → NEEDS_FIX
3. FAILED_CHECKS: checks 未过导致回环 → NEEDS_FIX
4. NEEDS_HUMAN_RULING: reviewer 输出 needs_human_ruling → NEEDS_HUMAN_RULING
5. LOOP_LIMIT: loop 超限触发人工升级 → NEEDS_HUMAN_RULING
6. HUMAN_APPROVAL: 人工批准后结案 → DONE

边界：
- 不包含真实外部调用
- 不包含测试断言（断言在 tests/ 中）
- 不依赖 Codex CLI 运行
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from automation.controller.transitions import TransitionCause
from mock.sample_review_results import (
    BLOCKING_FINDING_REVIEW,
    CLEAN_REVIEW,
    FAILED_CHECKS_REVIEW,
    LOOP_LIMIT_REVIEW,
    NEEDS_HUMAN_RULING_REVIEW,
)
from mock.sample_task_packets import MINIMAL_PACKET, SCENARIO_PACKET
from schemas.review_result import ReviewResult
from schemas.task_packet import TaskPacket
from schemas.task_state import (
    NextAction,
    RoundRecord,
    TaskState,
    TaskStatus,
)

# ═══════════════════════════════════════════════════
# Scenario 数据结构
# ═══════════════════════════════════════════════════


@dataclass(frozen=True)
class ReviewScenario:
    """一个 decide_after_review 场景。

    包含调用 decide_after_review() 所需的全部输入，
    以及期望的 TransitionResult 关键字段。
    """

    name: str
    description: str

    # ── 输入 ──
    task_packet: TaskPacket
    task_state: TaskState
    review_result: ReviewResult

    # ── 期望输出 ──
    expected_status: TaskStatus
    expected_cause: TransitionCause
    expected_notification: str | None = None


@dataclass(frozen=True)
class ApprovalScenario:
    """一个 approve_human_review 场景。"""

    name: str
    description: str

    # ── 输入 ──
    task_state: TaskState
    closure_summary: str = ""

    # ── 期望输出 ──
    expected_status: TaskStatus = TaskStatus.DONE
    expected_notification: str = "task_done"


class LifecycleAction(StrEnum):
    """生命周期步骤动作枚举。"""

    START_TASK = "start_task"
    CODER_DONE = "coder_done"
    DECIDE_AFTER_REVIEW = "decide_after_review"
    NEEDS_FIX_TO_CODING = "needs_fix_to_coding"
    ENTER_HUMAN_REVIEW = "enter_human_review"
    APPROVE_HUMAN_REVIEW = "approve_human_review"


@dataclass(frozen=True)
class LifecycleStep:
    """生命周期场景的单步。"""

    action: LifecycleAction
    expected_status: TaskStatus
    review_result: ReviewResult | None = None


@dataclass(frozen=True)
class FullLifecycleScenario:
    """一条完整生命周期路径（多步骤）。

    每一步是结构化 LifecycleStep，携带 action enum + 可选 review_result。
    review_result 仅在 action=DECIDE_AFTER_REVIEW 时必填。
    """

    name: str
    description: str
    task_packet: TaskPacket
    steps: tuple[LifecycleStep, ...]


# ═══════════════════════════════════════════════════
# 共享 TaskState fixture 工厂
# ═══════════════════════════════════════════════════


def _reviewing_state(task_id: str, round_no: int) -> TaskState:
    """构造处于 REVIEWING 状态的 TaskState。"""
    rounds = [
        RoundRecord(
            round_no=i + 1,
            coder_result_ref=f"runs/{task_id}/round_{i + 1}/coder_result.json",
        )
        for i in range(round_no)
    ]
    return TaskState(
        task_id=task_id,
        current_status=TaskStatus.REVIEWING,
        next_action=NextAction.RUN_REVIEWER,
        round_no=round_no,
        rounds=rounds,
    )


def _human_review_state(task_id: str, round_no: int) -> TaskState:
    """构造处于 HUMAN_REVIEW 状态的 TaskState。"""
    rounds = [
        RoundRecord(
            round_no=i + 1,
            coder_result_ref=f"runs/{task_id}/round_{i + 1}/coder_result.json",
            reviewer_result_ref=f"runs/{task_id}/round_{i + 1}/review_result.json",
        )
        for i in range(round_no)
    ]
    return TaskState(
        task_id=task_id,
        current_status=TaskStatus.HUMAN_REVIEW,
        next_action=NextAction.WAIT_HUMAN_REVIEW,
        round_no=round_no,
        rounds=rounds,
    )


# ═══════════════════════════════════════════════════
# 六个最低 ReviewScenario
# ═══════════════════════════════════════════════════


HAPPY_PATH = ReviewScenario(
    name="happy_path",
    description="coder 成功，reviewer clean → REVIEW_CLEAN",
    task_packet=MINIMAL_PACKET,
    task_state=_reviewing_state("MOCK_minimal", 1),
    review_result=CLEAN_REVIEW,
    expected_status=TaskStatus.REVIEW_CLEAN,
    expected_cause=TransitionCause.REVIEW_CLEAN,
    expected_notification="review_clean_ready_for_human",
)

BLOCKING_FINDING = ReviewScenario(
    name="blocking_finding",
    description="reviewer 给出 in-scope blocking finding → NEEDS_FIX",
    task_packet=SCENARIO_PACKET,
    task_state=_reviewing_state("MOCK_scenario", 1),
    review_result=BLOCKING_FINDING_REVIEW,
    expected_status=TaskStatus.NEEDS_FIX,
    expected_cause=TransitionCause.REVIEW_FINDINGS,
    expected_notification=None,
)

FAILED_CHECKS = ReviewScenario(
    name="failed_checks",
    description="checks 未过导致回环 → NEEDS_FIX",
    task_packet=SCENARIO_PACKET,
    task_state=_reviewing_state("MOCK_scenario", 1),
    review_result=FAILED_CHECKS_REVIEW,
    expected_status=TaskStatus.NEEDS_FIX,
    expected_cause=TransitionCause.REVIEW_FINDINGS,
    expected_notification=None,
)

NEEDS_HUMAN_RULING = ReviewScenario(
    name="needs_human_ruling",
    description="reviewer 无法可靠裁决 → NEEDS_HUMAN_RULING",
    task_packet=SCENARIO_PACKET,
    task_state=_reviewing_state("MOCK_scenario", 1),
    review_result=NEEDS_HUMAN_RULING_REVIEW,
    expected_status=TaskStatus.NEEDS_HUMAN_RULING,
    expected_cause=TransitionCause.REVIEWER_ESCALATION,
    expected_notification="needs_human_ruling",
)

# 场景 5: SCENARIO_PACKET 已包含 max_review_rounds=5
LOOP_LIMIT = ReviewScenario(
    name="loop_limit",
    description="loop 超限（round_no >= max_review_rounds）→ NEEDS_HUMAN_RULING",
    task_packet=SCENARIO_PACKET,
    task_state=_reviewing_state("MOCK_scenario", 5),
    review_result=LOOP_LIMIT_REVIEW,
    expected_status=TaskStatus.NEEDS_HUMAN_RULING,
    expected_cause=TransitionCause.LOOP_LIMIT,
    expected_notification="needs_human_ruling",
)


# ═══════════════════════════════════════════════════
# 人工批准场景
# ═══════════════════════════════════════════════════


HUMAN_APPROVAL = ApprovalScenario(
    name="human_approval",
    description="人工签字并结案 → DONE",
    task_state=_human_review_state("MOCK_minimal", 1),
    closure_summary="人工确认：任务完成，代码质量合格。",
    expected_status=TaskStatus.DONE,
    expected_notification="task_done",
)


# ═══════════════════════════════════════════════════
# 完整生命周期场景
# ═══════════════════════════════════════════════════


_A = LifecycleAction

LIFECYCLE_HAPPY = FullLifecycleScenario(
    name="lifecycle_happy",
    description="NEW → CODING → REVIEWING → REVIEW_CLEAN → HUMAN_REVIEW → DONE",
    task_packet=MINIMAL_PACKET,
    steps=(
        LifecycleStep(_A.START_TASK, TaskStatus.CODING),
        LifecycleStep(_A.CODER_DONE, TaskStatus.REVIEWING),
        LifecycleStep(_A.DECIDE_AFTER_REVIEW, TaskStatus.REVIEW_CLEAN, CLEAN_REVIEW),
        LifecycleStep(_A.ENTER_HUMAN_REVIEW, TaskStatus.HUMAN_REVIEW),
        LifecycleStep(_A.APPROVE_HUMAN_REVIEW, TaskStatus.DONE),
    ),
)

LIFECYCLE_ONE_FIX = FullLifecycleScenario(
    name="lifecycle_one_fix",
    description=(
        "NEW → CODING → REVIEWING → NEEDS_FIX → CODING"
        " → REVIEWING → REVIEW_CLEAN → HUMAN_REVIEW → DONE"
    ),
    task_packet=SCENARIO_PACKET,
    steps=(
        LifecycleStep(_A.START_TASK, TaskStatus.CODING),
        LifecycleStep(_A.CODER_DONE, TaskStatus.REVIEWING),
        LifecycleStep(_A.DECIDE_AFTER_REVIEW, TaskStatus.NEEDS_FIX, BLOCKING_FINDING_REVIEW),
        LifecycleStep(_A.NEEDS_FIX_TO_CODING, TaskStatus.CODING),
        LifecycleStep(_A.CODER_DONE, TaskStatus.REVIEWING),
        LifecycleStep(_A.DECIDE_AFTER_REVIEW, TaskStatus.REVIEW_CLEAN, CLEAN_REVIEW),
        LifecycleStep(_A.ENTER_HUMAN_REVIEW, TaskStatus.HUMAN_REVIEW),
        LifecycleStep(_A.APPROVE_HUMAN_REVIEW, TaskStatus.DONE),
    ),
)

LIFECYCLE_ESCALATION = FullLifecycleScenario(
    name="lifecycle_escalation",
    description="NEW → CODING → REVIEWING → NEEDS_HUMAN_RULING",
    task_packet=SCENARIO_PACKET,
    steps=(
        LifecycleStep(_A.START_TASK, TaskStatus.CODING),
        LifecycleStep(_A.CODER_DONE, TaskStatus.REVIEWING),
        LifecycleStep(
            _A.DECIDE_AFTER_REVIEW,
            TaskStatus.NEEDS_HUMAN_RULING,
            NEEDS_HUMAN_RULING_REVIEW,
        ),
    ),
)


# ═══════════════════════════════════════════════════
# 汇总导出
# ═══════════════════════════════════════════════════


REVIEW_SCENARIOS: dict[str, ReviewScenario] = {
    s.name: s for s in [HAPPY_PATH, BLOCKING_FINDING, FAILED_CHECKS, NEEDS_HUMAN_RULING, LOOP_LIMIT]
}

APPROVAL_SCENARIOS: dict[str, ApprovalScenario] = {
    HUMAN_APPROVAL.name: HUMAN_APPROVAL,
}

LIFECYCLE_SCENARIOS: dict[str, FullLifecycleScenario] = {
    s.name: s for s in [LIFECYCLE_HAPPY, LIFECYCLE_ONE_FIX, LIFECYCLE_ESCALATION]
}
