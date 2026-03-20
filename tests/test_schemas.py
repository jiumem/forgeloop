"""tests/test_schemas.py — P1 schema 校验测试。

覆盖：
- 合法对象能通过校验
- 缺关键字段时会失败
- 关键枚举值与边界条件有覆盖
"""

from __future__ import annotations

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
from schemas.task_state import NextAction, TaskState, TaskStatus

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
