"""test_interfaces — 接口合同测试。

P3_interfaces_contract 的测试基线：
- 锁住内部适配器合同（CodexAdapter Protocol）的类型结构
- 锁住外部自动化 API 合同（AutomationAPI Protocol）的类型结构
- 验证判别型结果对象（StateResult / NotifyResult / ParsedOutput）的闭合不变式
- 确认 Protocol 可被 mock 实现满足

设计依据：任务规划 §5.2 M2-4 / 设计方案 §6.1-6.2
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path
from typing import Any

import pytest

from automation.adapters.base import (
    AdapterError,
    AdapterErrorKind,
    AgentRole,
    ApprovalMode,
    CodexAdapter,
    CodexEvent,
    CodexRunConfig,
    CodexRunResult,
    ParsedOutput,
    SandboxMode,
)
from automation.api import (
    AutomationAPI,
    NotifyResult,
    OperationError,
    OperationErrorCode,
    OperationStatus,
    StateResult,
)
from schemas.task_state import TaskState

# ═══════════════════════════════════════════════════
# 内部适配器合同测试
# ═══════════════════════════════════════════════════


class TestAdapterErrorKind:
    """AdapterErrorKind 枚举覆盖。"""

    def test_all_kinds_exist(self) -> None:
        expected = {
            "invocation_failed",
            "timeout",
            "non_zero_exit",
            "output_missing",
            "output_parse_error",
            "resume_failed",
            "event_parse_error",
        }
        actual = {k.value for k in AdapterErrorKind}
        assert actual == expected

    def test_string_identity(self) -> None:
        assert AdapterErrorKind.TIMEOUT == "timeout"
        assert AdapterErrorKind.NON_ZERO_EXIT == "non_zero_exit"


class TestAdapterError:
    """AdapterError 结构化错误。"""

    def test_minimal(self) -> None:
        err = AdapterError(kind=AdapterErrorKind.TIMEOUT, detail="超时")
        assert err.kind == AdapterErrorKind.TIMEOUT
        assert err.detail == "超时"
        assert err.exit_code is None
        assert err.stderr_tail == ""

    def test_full(self) -> None:
        err = AdapterError(
            kind=AdapterErrorKind.NON_ZERO_EXIT,
            detail="进程返回 1",
            exit_code=1,
            stderr_tail="error: something failed",
        )
        assert err.exit_code == 1
        assert "something failed" in err.stderr_tail

    def test_frozen(self) -> None:
        err = AdapterError(kind=AdapterErrorKind.TIMEOUT, detail="x")
        with pytest.raises(FrozenInstanceError):
            err.kind = AdapterErrorKind.OUTPUT_MISSING  # type: ignore[misc]


class TestSandboxAndApprovalModes:
    """安全配置枚举。"""

    def test_sandbox_values(self) -> None:
        assert SandboxMode.READ_ONLY == "read-only"
        assert SandboxMode.WORKSPACE_WRITE == "workspace-write"

    def test_approval_values(self) -> None:
        assert ApprovalMode.NEVER == "never"
        assert ApprovalMode.ON_REQUEST == "on-request"

    def test_role_values(self) -> None:
        assert AgentRole.CODER == "coder"
        assert AgentRole.REVIEWER == "reviewer"


class TestCodexRunConfig:
    """运行配置。"""

    def test_minimal(self) -> None:
        cfg = CodexRunConfig(
            role=AgentRole.CODER,
            task_id="T1",
            round_no=1,
            prompt="实现功能 A",
        )
        assert cfg.role == AgentRole.CODER
        assert cfg.task_id == "T1"
        assert cfg.round_no == 1
        assert cfg.prompt == "实现功能 A"
        # 默认值
        assert cfg.working_dir == Path(".")
        assert cfg.output_schema_path is None
        assert cfg.output_dir is None
        assert cfg.model == ""
        assert cfg.config_overrides == {}
        assert cfg.sandbox == SandboxMode.READ_ONLY
        assert cfg.approval == ApprovalMode.NEVER
        assert cfg.timeout_seconds is None

    def test_full(self) -> None:
        cfg = CodexRunConfig(
            role=AgentRole.REVIEWER,
            task_id="T2",
            round_no=3,
            prompt="审查代码",
            working_dir=Path("/tmp/work"),
            output_schema_path=Path("schemas/review_result.schema.json"),
            output_dir=Path("/tmp/output"),
            model="o3",
            config_overrides={"reasoning": "high"},
            sandbox=SandboxMode.READ_ONLY,
            approval=ApprovalMode.NEVER,
            timeout_seconds=300,
        )
        assert cfg.role == AgentRole.REVIEWER
        assert cfg.timeout_seconds == 300
        assert cfg.model == "o3"

    def test_frozen(self) -> None:
        cfg = CodexRunConfig(role=AgentRole.CODER, task_id="T1", round_no=1, prompt="x")
        with pytest.raises(FrozenInstanceError):
            cfg.task_id = "T2"  # type: ignore[misc]

    def test_coder_default_security(self) -> None:
        """coder 默认安全配置 — 只读 sandbox + never approval。

        实际执行时 coder 需要 workspace-write，但合同默认从最小权限开始，
        由调用方显式提升。
        """
        cfg = CodexRunConfig(role=AgentRole.CODER, task_id="T1", round_no=1, prompt="x")
        assert cfg.sandbox == SandboxMode.READ_ONLY
        assert cfg.approval == ApprovalMode.NEVER


class TestCodexRunResult:
    """运行结果。"""

    def test_success(self) -> None:
        r = CodexRunResult(exit_code=0, output_file=Path("/tmp/out.json"))
        assert r.success is True
        assert r.error is None

    def test_failure_by_exit_code(self) -> None:
        r = CodexRunResult(exit_code=1, stderr="boom")
        assert r.success is False

    def test_failure_by_error(self) -> None:
        err = AdapterError(kind=AdapterErrorKind.OUTPUT_MISSING, detail="文件不存在")
        r = CodexRunResult(exit_code=0, error=err)
        assert r.success is False

    def test_thread_id(self) -> None:
        r = CodexRunResult(exit_code=0, thread_id="thread_abc123")
        assert r.thread_id == "thread_abc123"

    def test_frozen(self) -> None:
        r = CodexRunResult(exit_code=0)
        with pytest.raises(FrozenInstanceError):
            r.exit_code = 1  # type: ignore[misc]


class TestCodexEvent:
    """JSONL 事件。"""

    def test_minimal(self) -> None:
        e = CodexEvent(event_type="turn.started")
        assert e.event_type == "turn.started"
        assert e.data == {}
        assert e.raw_line == ""

    def test_with_data(self) -> None:
        e = CodexEvent(
            event_type="item.created",
            data={"item_id": "abc"},
            raw_line='{"type":"item.created","item_id":"abc"}',
        )
        assert e.data["item_id"] == "abc"


class TestParsedOutput:
    """ParsedOutput — read_final_output 的闭合返回类型。"""

    def test_success(self) -> None:
        p = ParsedOutput(value={"task_id": "T1"})
        assert p.success is True
        assert p.value is not None
        assert p.error is None

    def test_failure(self) -> None:
        err = AdapterError(kind=AdapterErrorKind.OUTPUT_PARSE_ERROR, detail="schema 不匹配")
        p = ParsedOutput(error=err)
        assert p.success is False
        assert p.error is not None
        assert p.error.kind == AdapterErrorKind.OUTPUT_PARSE_ERROR

    def test_missing_file(self) -> None:
        err = AdapterError(kind=AdapterErrorKind.OUTPUT_MISSING, detail="文件不存在")
        p = ParsedOutput(error=err)
        assert p.success is False
        assert p.value is None

    def test_frozen(self) -> None:
        p = ParsedOutput(value="x")
        with pytest.raises(FrozenInstanceError):
            p.value = "y"  # type: ignore[misc]

    # ── 闭合不变式 ──

    def test_empty_object_rejected(self) -> None:
        """空对象（value 和 error 都为 None）被拒绝。"""
        with pytest.raises(ValueError, match="不允许空对象"):
            ParsedOutput()

    def test_both_value_and_error_rejected(self) -> None:
        """矛盾态（value 和 error 同时非 None）被拒绝。"""
        err = AdapterError(kind=AdapterErrorKind.OUTPUT_PARSE_ERROR, detail="x")
        with pytest.raises(ValueError, match="不允许矛盾态"):
            ParsedOutput(value={"data": 1}, error=err)

    def test_explicit_none_value_with_none_error_rejected(self) -> None:
        """显式传 value=None, error=None 也被拒绝。"""
        with pytest.raises(ValueError, match="不允许空对象"):
            ParsedOutput(value=None, error=None)


class TestCodexAdapterProtocol:
    """Protocol 结构性验证。"""

    def test_mock_satisfies_protocol(self) -> None:
        """一个最小 mock 实现能满足 CodexAdapter Protocol。"""

        class _MockAdapter:
            def exec(self, config: CodexRunConfig) -> CodexRunResult:
                return CodexRunResult(exit_code=0)

            def resume(self, config: CodexRunConfig, *, thread_id: str) -> CodexRunResult:
                return CodexRunResult(exit_code=0, thread_id=thread_id)

            def read_final_output(
                self, result: CodexRunResult, *, schema_type: type
            ) -> ParsedOutput:
                return ParsedOutput(value={"mock": True})

            def parse_events(self, stdout: str) -> list[CodexEvent]:
                return []

        adapter = _MockAdapter()
        assert isinstance(adapter, CodexAdapter)

    def test_incomplete_impl_fails_protocol(self) -> None:
        """缺少方法的实现不满足 Protocol。"""

        class _Incomplete:
            def exec(self, config: CodexRunConfig) -> CodexRunResult:
                return CodexRunResult(exit_code=0)

        assert not isinstance(_Incomplete(), CodexAdapter)


# ═══════════════════════════════════════════════════
# 外部自动化 API 合同测试
# ═══════════════════════════════════════════════════


class TestOperationErrorCode:
    """OperationErrorCode 枚举覆盖。"""

    def test_all_codes_exist(self) -> None:
        expected = {
            "task_not_found",
            "task_already_exists",
            "invalid_state",
            "transition_error",
            "adapter_error",
            "validation_error",
            "store_error",
            "notification_error",
        }
        actual = {c.value for c in OperationErrorCode}
        assert actual == expected


class TestOperationError:
    """OperationError 结构化错误。"""

    def test_minimal(self) -> None:
        err = OperationError(
            code=OperationErrorCode.TASK_NOT_FOUND,
            message="任务不存在",
        )
        assert err.code == OperationErrorCode.TASK_NOT_FOUND
        assert err.message == "任务不存在"
        assert err.details == {}

    def test_with_details(self) -> None:
        err = OperationError(
            code=OperationErrorCode.INVALID_STATE,
            message="当前状态不允许此操作",
            details={"current_status": "DONE", "expected": "HUMAN_REVIEW"},
        )
        assert err.details["current_status"] == "DONE"

    def test_frozen(self) -> None:
        err = OperationError(code=OperationErrorCode.STORE_ERROR, message="x")
        with pytest.raises(FrozenInstanceError):
            err.code = OperationErrorCode.TASK_NOT_FOUND  # type: ignore[misc]


class TestStateResult:
    """StateResult — 携带 task_state 的操作结果。"""

    def test_success_with_state(self) -> None:
        state = TaskState(task_id="T1")
        r = StateResult(
            status=OperationStatus.SUCCESS,
            task_state=state,
            message="任务已创建",
        )
        assert r.success is True
        assert r.task_state is not None
        assert r.task_state.task_id == "T1"
        assert r.error is None

    def test_no_op_with_state(self) -> None:
        state = TaskState(task_id="T1")
        r = StateResult(status=OperationStatus.NO_OP, task_state=state, message="已存在")
        assert r.success is True
        assert r.task_state is not None

    def test_failed(self) -> None:
        err = OperationError(
            code=OperationErrorCode.TASK_NOT_FOUND,
            message="任务不存在",
        )
        r = StateResult(status=OperationStatus.FAILED, error=err)
        assert r.success is False
        assert r.error is not None
        assert r.error.code == OperationErrorCode.TASK_NOT_FOUND
        assert r.task_state is None

    def test_frozen(self) -> None:
        state = TaskState(task_id="T1")
        r = StateResult(status=OperationStatus.SUCCESS, task_state=state)
        with pytest.raises(FrozenInstanceError):
            r.status = OperationStatus.FAILED  # type: ignore[misc]

    # ── 闭合不变式 ──

    def test_success_without_state_rejected(self) -> None:
        """SUCCESS 时 task_state 不能为 None。"""
        with pytest.raises(ValueError, match="task_state 不能为 None"):
            StateResult(status=OperationStatus.SUCCESS)

    def test_no_op_without_state_rejected(self) -> None:
        """NO_OP 时 task_state 不能为 None。"""
        with pytest.raises(ValueError, match="task_state 不能为 None"):
            StateResult(status=OperationStatus.NO_OP)

    def test_failed_without_error_rejected(self) -> None:
        """FAILED 时 error 不能为 None。"""
        with pytest.raises(ValueError, match="FAILED.*error 不能为 None"):
            StateResult(status=OperationStatus.FAILED)

    def test_failed_with_state_rejected(self) -> None:
        """FAILED 时 task_state 必须为 None。"""
        err = OperationError(code=OperationErrorCode.STORE_ERROR, message="x")
        state = TaskState(task_id="T1")
        with pytest.raises(ValueError, match="FAILED.*task_state 必须为 None"):
            StateResult(status=OperationStatus.FAILED, error=err, task_state=state)

    def test_success_with_error_rejected(self) -> None:
        """SUCCESS 时 error 必须为 None。"""
        err = OperationError(code=OperationErrorCode.STORE_ERROR, message="x")
        state = TaskState(task_id="T1")
        with pytest.raises(ValueError, match="error 必须为 None"):
            StateResult(status=OperationStatus.SUCCESS, task_state=state, error=err)


class TestNotifyResult:
    """NotifyResult — 纯副作用操作结果。"""

    def test_success(self) -> None:
        r = NotifyResult(status=OperationStatus.SUCCESS, message="通知已发送")
        assert r.success is True
        assert r.error is None

    def test_no_op(self) -> None:
        r = NotifyResult(status=OperationStatus.NO_OP, message="已发送")
        assert r.success is True

    def test_failed(self) -> None:
        err = OperationError(
            code=OperationErrorCode.NOTIFICATION_ERROR,
            message="通知失败",
        )
        r = NotifyResult(status=OperationStatus.FAILED, error=err)
        assert r.success is False
        assert r.error is not None

    def test_frozen(self) -> None:
        r = NotifyResult(status=OperationStatus.SUCCESS)
        with pytest.raises(FrozenInstanceError):
            r.status = OperationStatus.FAILED  # type: ignore[misc]

    # ── 闭合不变式 ──

    def test_failed_without_error_rejected(self) -> None:
        with pytest.raises(ValueError, match="FAILED.*error 不能为 None"):
            NotifyResult(status=OperationStatus.FAILED)

    def test_success_with_error_rejected(self) -> None:
        err = OperationError(code=OperationErrorCode.NOTIFICATION_ERROR, message="x")
        with pytest.raises(ValueError, match="error 必须为 None"):
            NotifyResult(status=OperationStatus.SUCCESS, error=err)

    def test_no_task_state_attribute(self) -> None:
        """NotifyResult 没有 task_state 字段。"""
        r = NotifyResult(status=OperationStatus.SUCCESS)
        assert not hasattr(r, "task_state")


class TestAutomationAPIProtocol:
    """Protocol 结构性验证。"""

    def test_mock_satisfies_protocol(self) -> None:
        """一个最小 mock 实现能满足 AutomationAPI Protocol。"""
        _state = TaskState(task_id="T1")

        class _MockAPI:
            def create_task(self, task_packet: Any) -> StateResult:
                return StateResult(status=OperationStatus.SUCCESS, task_state=_state)

            def run_coder(self, task_id: str, round_no: int) -> StateResult:
                return StateResult(status=OperationStatus.SUCCESS, task_state=_state)

            def run_reviewer(self, task_id: str, round_no: int) -> StateResult:
                return StateResult(status=OperationStatus.SUCCESS, task_state=_state)

            def advance_state(self, task_id: str) -> StateResult:
                return StateResult(status=OperationStatus.SUCCESS, task_state=_state)

            def approve_human_review(
                self, task_id: str, *, closure_summary: str = ""
            ) -> StateResult:
                return StateResult(status=OperationStatus.SUCCESS, task_state=_state)

            def send_notification(self, task_id: str, *, event: str) -> NotifyResult:
                return NotifyResult(status=OperationStatus.SUCCESS)

        api = _MockAPI()
        assert isinstance(api, AutomationAPI)

    def test_incomplete_impl_fails_protocol(self) -> None:
        """缺少方法的实现不满足 Protocol。"""

        class _Incomplete:
            def create_task(self, task_packet: Any) -> StateResult:
                return StateResult(
                    status=OperationStatus.SUCCESS, task_state=TaskState(task_id="T1")
                )

        assert not isinstance(_Incomplete(), AutomationAPI)


# ═══════════════════════════════════════════════════
# 跨层一致性测试
# ═══════════════════════════════════════════════════


class TestCrossLayerConsistency:
    """两层接口之间的一致性约束。"""

    def test_adapter_error_can_map_to_state_result_error(self) -> None:
        """适配器错误可被映射为 StateResult 的 OperationError。"""
        adapter_err = AdapterError(
            kind=AdapterErrorKind.NON_ZERO_EXIT,
            detail="exit code 1",
            exit_code=1,
        )
        op_err = OperationError(
            code=OperationErrorCode.ADAPTER_ERROR,
            message=f"Codex CLI 失败: {adapter_err.detail}",
            details={
                "adapter_error_kind": adapter_err.kind.value,
                "exit_code": adapter_err.exit_code,
            },
        )
        r = StateResult(status=OperationStatus.FAILED, error=op_err)
        assert r.error is not None
        assert r.error.code == OperationErrorCode.ADAPTER_ERROR
        assert r.error.details["adapter_error_kind"] == "non_zero_exit"

    def test_state_result_success_always_has_task_state(self) -> None:
        """StateResult 成功时必定包含 task_state 快照。"""
        state = TaskState(task_id="T1")
        r = StateResult(status=OperationStatus.SUCCESS, task_state=state)
        assert r.task_state is not None
        assert r.task_state.current_status.value == "NEW"

    def test_notify_result_never_has_task_state(self) -> None:
        """NotifyResult 永远不携带 task_state。"""
        r = NotifyResult(status=OperationStatus.SUCCESS)
        assert not hasattr(r, "task_state")
