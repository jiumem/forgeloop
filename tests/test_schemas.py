"""tests/test_schemas.py — P1 schema 校验测试。

覆盖：
- 合法对象能通过校验
- 缺关键字段时会失败
- 关键枚举值与边界条件有覆盖
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from schemas.coder_result import CheckResult, CheckStatus, CoderResult
from schemas.review_result import (
    Finding,
    NextTaskRecommendation,
    PromotionReadiness,
    ReviewResult,
    Severity,
    TaskVerdict,
)
from schemas.task_packet import PromotionPolicy, TaskPacket
from schemas.task_state import NextAction, RoundRecord, TaskState, TaskStatus

# ═══════════════════════════════════════════════════
# TaskPacket
# ═══════════════════════════════════════════════════


class TestTaskPacket:
    """task_packet schema 校验。"""

    def test_minimal_valid(self) -> None:
        """最小合法 task_packet。"""
        tp = TaskPacket(
            task_id="P1_schema_baseline",
            title="四个核心 schema 基线",
            must_do=["定义四个 schema"],
            done_criteria=["四个 schema 已存在"],
        )
        assert tp.task_id == "P1_schema_baseline"
        assert tp.phase == ""
        assert tp.promotion_policy.max_review_rounds == 3

    def test_full_valid(self) -> None:
        """完整合法 task_packet。"""
        tp = TaskPacket(
            task_id="P2_state_machine",
            title="状态枚举、跃迁表与 task_state 持久化",
            phase="M1",
            chain="v1",
            entry_docs=["docs/设计方案.md"],
            must_do=["实现状态枚举", "实现跃迁表"],
            must_not_do=["不做多任务并行"],
            done_criteria=["状态枚举可程序化引用", "跃迁表可测试"],
            depends_on=["P1_schema_baseline"],
            related_tasks=["P3_interfaces_contract"],
            required_checks=["uv run pytest", "uv run ruff check ."],
            promotion_policy=PromotionPolicy(auto_promote=False, max_review_rounds=5),
        )
        assert tp.phase == "M1"
        assert tp.promotion_policy.max_review_rounds == 5
        assert len(tp.must_do) == 2

    def test_missing_task_id(self) -> None:
        """缺 task_id 应报错。"""
        with pytest.raises(ValidationError):
            TaskPacket(
                title="no id",  # type: ignore[call-arg]
                must_do=["x"],
                done_criteria=["y"],
            )

    def test_empty_task_id(self) -> None:
        """空 task_id 应报错。"""
        with pytest.raises(ValidationError):
            TaskPacket(
                task_id="",
                title="empty id",
                must_do=["x"],
                done_criteria=["y"],
            )

    def test_missing_must_do(self) -> None:
        """缺 must_do 应报错。"""
        with pytest.raises(ValidationError):
            TaskPacket(
                task_id="test",
                title="no must_do",  # type: ignore[call-arg]
                done_criteria=["y"],
            )

    def test_empty_must_do(self) -> None:
        """空 must_do 列表应报错。"""
        with pytest.raises(ValidationError):
            TaskPacket(
                task_id="test",
                title="empty must_do",
                must_do=[],
                done_criteria=["y"],
            )

    def test_missing_done_criteria(self) -> None:
        """缺 done_criteria 应报错。"""
        with pytest.raises(ValidationError):
            TaskPacket(
                task_id="test",
                title="no done_criteria",  # type: ignore[call-arg]
                must_do=["x"],
            )

    def test_max_review_rounds_ge_1(self) -> None:
        """max_review_rounds 必须 >= 1。"""
        with pytest.raises(ValidationError):
            PromotionPolicy(max_review_rounds=0)

    def test_task_id_rejects_unsafe_characters(self) -> None:
        """task_id 只允许字母、数字、下划线、连字符。"""
        for bad_id in ["../escape", "a/b", "has space", "has.dot", "a\\b"]:
            with pytest.raises(ValidationError):
                TaskPacket(
                    task_id=bad_id,
                    title="bad",
                    must_do=["x"],
                    done_criteria=["y"],
                )

    def test_task_id_accepts_safe_characters(self) -> None:
        """task_id 合法字符：字母、数字、下划线、连字符。"""
        tp = TaskPacket(
            task_id="P1_schema-baseline-v2",
            title="safe",
            must_do=["x"],
            done_criteria=["y"],
        )
        assert tp.task_id == "P1_schema-baseline-v2"

    def test_depends_on_rejects_unsafe_task_id(self) -> None:
        """depends_on 元素也必须符合 task_id 格式约束。"""
        with pytest.raises(ValidationError):
            TaskPacket(
                task_id="P2",
                title="bad dep",
                must_do=["x"],
                done_criteria=["y"],
                depends_on=["a/b"],
            )

    def test_related_tasks_rejects_unsafe_task_id(self) -> None:
        """related_tasks 元素也必须符合 task_id 格式约束。"""
        with pytest.raises(ValidationError):
            TaskPacket(
                task_id="P2",
                title="bad related",
                must_do=["x"],
                done_criteria=["y"],
                related_tasks=["has space"],
            )


# ═══════════════════════════════════════════════════
# CoderResult
# ═══════════════════════════════════════════════════


class TestCoderResult:
    """coder_result schema 校验。"""

    def test_minimal_valid(self) -> None:
        cr = CoderResult(task_id="P1", round_no=1)
        assert cr.task_id == "P1"
        assert cr.round_no == 1
        assert cr.files_changed == []

    def test_full_valid(self) -> None:
        cr = CoderResult(
            task_id="P1",
            round_no=2,
            files_changed=["schemas/task_packet.py"],
            contracts_addressed=["TaskPacket schema"],
            cleanups_done=["removed legacy schema.py"],
            check_results=[
                CheckResult(check_name="pytest", status=CheckStatus.PASSED),
                CheckResult(
                    check_name="integration",
                    status=CheckStatus.SKIPPED,
                    message="no real Codex available",
                ),
            ],
            out_of_scope_notes=["adapter 层不在本任务范围"],
            summary="完成四个 schema 定义",
        )
        assert len(cr.check_results) == 2
        assert cr.check_results[1].status == CheckStatus.SKIPPED

    def test_round_no_must_be_positive(self) -> None:
        with pytest.raises(ValidationError):
            CoderResult(task_id="P1", round_no=0)

    def test_missing_task_id(self) -> None:
        with pytest.raises(ValidationError):
            CoderResult(round_no=1)  # type: ignore[call-arg]

    def test_skipped_check_without_message_rejected(self) -> None:
        """SKIPPED 状态时 message 不能为空（设计方案 §5.2 执法）。"""
        with pytest.raises(ValidationError, match="不能为空"):
            CheckResult(check_name="pytest", status=CheckStatus.SKIPPED)

    def test_skipped_check_with_message_accepted(self) -> None:
        """SKIPPED + 有原因说明应通过。"""
        cr = CheckResult(
            check_name="integration",
            status=CheckStatus.SKIPPED,
            message="no Codex available",
        )
        assert cr.status == CheckStatus.SKIPPED

    def test_error_check_without_message_rejected(self) -> None:
        """ERROR 状态同样必须填原因。"""
        with pytest.raises(ValidationError, match="不能为空"):
            CheckResult(check_name="lint", status=CheckStatus.ERROR)

    def test_passed_check_without_message_accepted(self) -> None:
        """PASSED 状态 message 可为空。"""
        cr = CheckResult(check_name="pytest", status=CheckStatus.PASSED)
        assert cr.message == ""

    def test_json_schema_has_conditional_message_constraint(self) -> None:
        """导出的 JSON Schema 必须包含 if/then 条件约束。"""
        schema = CheckResult.model_json_schema()
        assert "allOf" in schema, "JSON Schema 缺少 allOf 条件约束"
        rule = schema["allOf"][0]
        assert "if" in rule
        assert rule["if"]["properties"]["status"]["enum"] == ["skipped", "error"]
        assert rule["then"]["properties"]["message"]["minLength"] == 1
        assert rule["then"]["properties"]["message"]["pattern"] == "\\S"
        assert "message" in rule["then"]["required"]


# ═══════════════════════════════════════════════════
# ReviewResult
# ═══════════════════════════════════════════════════


class TestReviewResult:
    """review_result schema 校验。"""

    def test_clean_result(self) -> None:
        rr = ReviewResult(
            task_id="P1",
            round_no=1,
            current_task_verdict=TaskVerdict.CLEAN,
            promotion_readiness=PromotionReadiness(ready=True, rationale="all checks pass"),
        )
        assert rr.current_task_verdict == TaskVerdict.CLEAN
        assert rr.promotion_readiness.ready

    def test_needs_fix_with_findings(self) -> None:
        rr = ReviewResult(
            task_id="P1",
            round_no=1,
            findings=[
                Finding(
                    finding_key="missing-field",
                    severity=Severity.P1,
                    summary="task_state 缺少 round_no 字段",
                    why_it_matters="controller 无法追踪轮次",
                    in_scope=True,
                    scope_basis="must_do[0]: 定义四个 schema",
                    blocks_promotion=True,
                ),
            ],
            current_task_verdict=TaskVerdict.NEEDS_FIX,
            promotion_readiness=PromotionReadiness(ready=False),
        )
        assert len(rr.findings) == 1
        assert rr.findings[0].blocks_promotion

    def test_finding_missing_required_field(self) -> None:
        """Finding 缺少法定字段应报错。"""
        with pytest.raises(ValidationError):
            Finding(
                finding_key="x",
                severity=Severity.P1,
                summary="s",
                # missing: why_it_matters, in_scope, scope_basis, blocks_promotion
            )  # type: ignore[call-arg]

    def test_invalid_severity_value(self) -> None:
        """非法严重级别应报错。"""
        with pytest.raises(ValidationError):
            Finding(
                finding_key="x",
                severity="critical",  # type: ignore[arg-type]
                summary="s",
                why_it_matters="w",
                in_scope=True,
                scope_basis="b",
                blocks_promotion=True,
            )

    def test_next_task_recommendation(self) -> None:
        rec = NextTaskRecommendation(task_id="P2_state_machine", rationale="P1 已完成")
        assert rec.task_id == "P2_state_machine"

    def test_next_task_recommendation_rejects_unsafe_id(self) -> None:
        """NextTaskRecommendation.task_id 也必须符合格式约束。"""
        with pytest.raises(ValidationError):
            NextTaskRecommendation(task_id="a/b")


# ═══════════════════════════════════════════════════
# TaskState
# ═══════════════════════════════════════════════════


class TestTaskState:
    """task_state schema 校验。"""

    def test_default_new_state(self) -> None:
        ts = TaskState(task_id="P1")
        assert ts.current_status == TaskStatus.NEW
        assert ts.round_no == 0
        assert ts.next_action == NextAction.RUN_CODER
        assert ts.rounds == []

    def test_all_status_values(self) -> None:
        """所有状态枚举值应可实例化。"""
        expected = {
            "NEW",
            "CODING",
            "REVIEWING",
            "NEEDS_FIX",
            "REVIEW_CLEAN",
            "HUMAN_REVIEW",
            "DONE",
            "NEEDS_HUMAN_RULING",
            "BLOCKED",
        }
        actual = {s.value for s in TaskStatus}
        assert actual == expected

    def test_all_next_action_values(self) -> None:
        """所有动作枚举值应可实例化。"""
        expected = {
            "run_coder",
            "run_reviewer",
            "wait_human_review",
            "wait_human_ruling",
            "resolve_blocked",
            "none",
        }
        actual = {a.value for a in NextAction}
        assert actual == expected

    def test_timestamps_auto_set(self) -> None:
        ts = TaskState(task_id="P1")
        assert ts.created_at is not None
        assert ts.updated_at is not None

    def test_rounds_round_no_inconsistency_rejected(self) -> None:
        """round_no 与 rounds 长度不一致时 schema 应拒绝构造。"""
        with pytest.raises(ValidationError, match="台账必须完整"):
            TaskState(
                task_id="x",
                current_status=TaskStatus.CODING,
                round_no=1,
                rounds=[],  # 应有 1 条但为空
            )

    def test_rounds_extra_record_rejected(self) -> None:
        """rounds 条数多于 round_no 同样被拒。"""
        with pytest.raises(ValidationError, match="台账必须完整"):
            TaskState(
                task_id="x",
                round_no=0,
                rounds=[RoundRecord(round_no=1)],  # 多出一条
            )

    def test_rounds_wrong_round_no_in_record_rejected(self) -> None:
        """rounds 内某条 round_no 与位置不匹配时被拒。"""
        with pytest.raises(ValidationError, match="期望"):
            TaskState(
                task_id="x",
                round_no=2,
                rounds=[
                    RoundRecord(round_no=1),
                    RoundRecord(round_no=5),  # 位置 2 但 round_no=5
                ],
            )

    def test_consistent_rounds_accepted(self) -> None:
        """rounds 与 round_no 一致时正常构造。"""
        ts = TaskState(
            task_id="x",
            current_status=TaskStatus.CODING,
            next_action=NextAction.RUN_CODER,
            round_no=2,
            rounds=[RoundRecord(round_no=1), RoundRecord(round_no=2)],
        )
        assert ts.round_no == 2
        assert len(ts.rounds) == 2

    def test_new_with_nonzero_round_no_rejected(self) -> None:
        """NEW 状态 round_no 必须为 0。"""
        with pytest.raises(ValidationError, match="NEW 状态 round_no 必须为 0"):
            TaskState(
                task_id="x",
                current_status=TaskStatus.NEW,
                round_no=1,
                rounds=[RoundRecord(round_no=1)],
            )

    def test_work_status_with_zero_round_no_rejected(self) -> None:
        """工作状态（CODING 等）round_no 不能为 0。"""
        from schemas.task_state import STATUS_NEXT_ACTION

        for status in (TaskStatus.CODING, TaskStatus.REVIEWING, TaskStatus.DONE):
            with pytest.raises(ValidationError, match="工作状态"):
                TaskState(
                    task_id="x",
                    current_status=status,
                    next_action=STATUS_NEXT_ACTION[status],
                    round_no=0,
                    rounds=[],
                )

    def test_non_new_with_positive_round_no_accepted(self) -> None:
        """非 NEW 状态 + round_no>=1 + 正确 next_action 正常构造。"""
        from schemas.task_state import STATUS_NEXT_ACTION

        for status in (TaskStatus.CODING, TaskStatus.REVIEWING, TaskStatus.DONE):
            ts = TaskState(
                task_id="x",
                current_status=status,
                next_action=STATUS_NEXT_ACTION[status],
                round_no=1,
                rounds=[RoundRecord(round_no=1)],
            )
            assert ts.current_status == status

    def test_early_abort_terminal_with_zero_round_no_accepted(self) -> None:
        """BLOCKED/NEEDS_HUMAN_RULING 可从 NEW 直接到达，round_no==0 合法。"""
        from schemas.task_state import STATUS_NEXT_ACTION

        for status in (TaskStatus.BLOCKED, TaskStatus.NEEDS_HUMAN_RULING):
            ts = TaskState(
                task_id="x",
                current_status=status,
                next_action=STATUS_NEXT_ACTION[status],
                round_no=0,
                rounds=[],
            )
            assert ts.current_status == status
            assert ts.round_no == 0


# ═══════════════════════════════════════════════════
# TaskState 全局合同矩阵测试
# ═══════════════════════════════════════════════════


class TestTaskStateContractMatrix:
    """参数化覆盖 9 个 status × 多字段 的合法/非法组合。

    schema 级不变式：
    1. status ↔ next_action 严格 1:1
    2. status ↔ round_no
    3. closure_summary 仅 DONE 允许非空
    4. 常量完备性
    """

    @staticmethod
    def _valid_state(
        status: TaskStatus,
        *,
        round_no: int | None = None,
        closure_summary: str = "",
    ) -> TaskState:
        """构造给定 status 下最小合法 TaskState。"""
        from schemas.task_state import ALLOW_ZERO_ROUND_STATUSES, STATUS_NEXT_ACTION

        if round_no is None:
            round_no = 0 if status in ALLOW_ZERO_ROUND_STATUSES else 1
        rounds = [RoundRecord(round_no=i + 1) for i in range(round_no)]
        return TaskState(
            task_id="matrix",
            current_status=status,
            next_action=STATUS_NEXT_ACTION[status],
            round_no=round_no,
            rounds=rounds,
            closure_summary=closure_summary,
        )

    # ── 1. status ↔ next_action ──

    @pytest.mark.parametrize("status", list(TaskStatus))
    def test_correct_next_action_accepted(self, status: TaskStatus) -> None:
        """每个 status 配对正确 next_action 可构造。"""
        ts = self._valid_state(status)
        from schemas.task_state import STATUS_NEXT_ACTION

        assert ts.next_action == STATUS_NEXT_ACTION[status]

    @pytest.mark.parametrize("status", list(TaskStatus))
    def test_wrong_next_action_rejected(self, status: TaskStatus) -> None:
        """每个 status 配对错误 next_action 被拒。"""
        from schemas.task_state import ALLOW_ZERO_ROUND_STATUSES, STATUS_NEXT_ACTION

        correct = STATUS_NEXT_ACTION[status]
        # 找一个与正确值不同的 next_action
        wrong = next(a for a in NextAction if a != correct)
        round_no = 0 if status in ALLOW_ZERO_ROUND_STATUSES else 1
        rounds = [RoundRecord(round_no=i + 1) for i in range(round_no)]
        with pytest.raises(ValidationError, match="next_action 必须为"):
            TaskState(
                task_id="matrix",
                current_status=status,
                next_action=wrong,
                round_no=round_no,
                rounds=rounds,
            )

    # ── 2. status ↔ round_no ──

    _WORK_STATUSES = [
        s
        for s in TaskStatus
        if s not in (TaskStatus.NEW, TaskStatus.BLOCKED, TaskStatus.NEEDS_HUMAN_RULING)
    ]

    @pytest.mark.parametrize("status", _WORK_STATUSES)
    def test_work_status_rejects_zero_round(self, status: TaskStatus) -> None:
        """工作状态 round_no=0 被拒。"""
        from schemas.task_state import STATUS_NEXT_ACTION

        with pytest.raises(ValidationError, match="工作状态"):
            TaskState(
                task_id="matrix",
                current_status=status,
                next_action=STATUS_NEXT_ACTION[status],
                round_no=0,
                rounds=[],
            )

    @pytest.mark.parametrize("status", [TaskStatus.BLOCKED, TaskStatus.NEEDS_HUMAN_RULING])
    def test_early_abort_accepts_zero_round(self, status: TaskStatus) -> None:
        """早退状态 round_no=0 合法。"""
        ts = self._valid_state(status, round_no=0)
        assert ts.round_no == 0

    @pytest.mark.parametrize("status", [TaskStatus.BLOCKED, TaskStatus.NEEDS_HUMAN_RULING])
    def test_early_abort_also_accepts_positive_round(self, status: TaskStatus) -> None:
        """早退状态 round_no>=1 也合法（从工作状态异常退出）。"""
        ts = self._valid_state(status, round_no=1)
        assert ts.round_no == 1

    def test_new_rejects_nonzero_round(self) -> None:
        """NEW round_no!=0 被拒。"""
        with pytest.raises(ValidationError, match="NEW 状态 round_no 必须为 0"):
            TaskState(
                task_id="matrix",
                current_status=TaskStatus.NEW,
                next_action=NextAction.RUN_CODER,
                round_no=1,
                rounds=[RoundRecord(round_no=1)],
            )

    # ── 3. closure_summary ──

    _NON_DONE_STATUSES = [s for s in TaskStatus if s != TaskStatus.DONE]

    @pytest.mark.parametrize("status", _NON_DONE_STATUSES)
    def test_non_done_rejects_closure_summary(self, status: TaskStatus) -> None:
        """非 DONE 状态不允许非空 closure_summary。"""
        from schemas.task_state import ALLOW_ZERO_ROUND_STATUSES, STATUS_NEXT_ACTION

        round_no = 0 if status in ALLOW_ZERO_ROUND_STATUSES else 1
        rounds = [RoundRecord(round_no=i + 1) for i in range(round_no)]
        with pytest.raises(ValidationError, match="closure_summary"):
            TaskState(
                task_id="matrix",
                current_status=status,
                next_action=STATUS_NEXT_ACTION[status],
                round_no=round_no,
                rounds=rounds,
                closure_summary="should not be here",
            )

    def test_done_accepts_closure_summary(self) -> None:
        """DONE 允许非空 closure_summary。"""
        ts = self._valid_state(TaskStatus.DONE, closure_summary="task completed")
        assert ts.closure_summary == "task completed"

    def test_done_accepts_empty_closure_summary(self) -> None:
        """DONE 也允许空 closure_summary（人工未填摘要）。"""
        ts = self._valid_state(TaskStatus.DONE, closure_summary="")
        assert ts.closure_summary == ""

    # ── 4. 常量完备性 ──

    def test_status_next_action_covers_all_statuses(self) -> None:
        """STATUS_NEXT_ACTION 覆盖所有 TaskStatus。"""
        from schemas.task_state import STATUS_NEXT_ACTION

        assert set(STATUS_NEXT_ACTION.keys()) == set(TaskStatus)

    def test_allow_zero_round_partition(self) -> None:
        """ALLOW_ZERO_ROUND_STATUSES + 工作状态 = 全部 TaskStatus。"""
        from schemas.task_state import ALLOW_ZERO_ROUND_STATUSES

        work_statuses = set(TaskStatus) - ALLOW_ZERO_ROUND_STATUSES
        assert work_statuses | ALLOW_ZERO_ROUND_STATUSES == set(TaskStatus)
        # 工作状态不应为空
        assert len(work_statuses) >= 6

    def test_allow_closure_summary_only_done(self) -> None:
        """ALLOW_CLOSURE_SUMMARY_STATUSES 仅含 DONE。"""
        from schemas.task_state import ALLOW_CLOSURE_SUMMARY_STATUSES

        assert {TaskStatus.DONE} == ALLOW_CLOSURE_SUMMARY_STATUSES

    # ── 5. 全 status 合法构造烟雾测试 ──

    @pytest.mark.parametrize("status", list(TaskStatus))
    def test_every_status_can_be_constructed(self, status: TaskStatus) -> None:
        """每个 status 都能构造出合法 TaskState（不存在"死状态"）。"""
        ts = self._valid_state(status)
        assert ts.current_status == status


# ═══════════════════════════════════════════════════
# Mock fixture 与 JSON 一致性
# ═══════════════════════════════════════════════════

_FIXTURES_DIR = Path(__file__).resolve().parent.parent / "mock" / "fixtures"


class TestMockFixtureConsistency:
    """mock/ 下 Python 样例实例与 JSON fixture 必须一致。"""

    def test_minimal_packet_matches_json(self) -> None:
        from mock.sample_task_packets import MINIMAL_PACKET

        json_path = _FIXTURES_DIR / "minimal_task_packet.json"
        json_data = json.loads(json_path.read_text(encoding="utf-8"))
        assert MINIMAL_PACKET.model_dump(mode="json") == json_data

    def test_full_packet_matches_json(self) -> None:
        from mock.sample_task_packets import FULL_PACKET

        json_path = _FIXTURES_DIR / "full_task_packet.json"
        json_data = json.loads(json_path.read_text(encoding="utf-8"))
        assert FULL_PACKET.model_dump(mode="json") == json_data

    def test_json_fixtures_roundtrip_as_valid_task_packet(self) -> None:
        """JSON fixture 必须能被 TaskPacket 校验通过（双向锁定）。"""
        for name in ("minimal_task_packet.json", "full_task_packet.json"):
            json_path = _FIXTURES_DIR / name
            data = json.loads(json_path.read_text(encoding="utf-8"))
            tp = TaskPacket(**data)
            assert tp.task_id
