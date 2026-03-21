"""api — 外部自动化接口合同（外部接口层）。

这是设计方案 §6.1 的合同定义：系统如何被任务调度器、命令行工具、CI 或人类用户调用。

本模块只定义合同（Protocol + 操作结果/错误类型），不包含实现。
实现在 M3 阶段（P7/P8）落地。

最小接口集（设计方案 §6.1）：
| 接口                              | 作用                     | 返回类型         |
|----------------------------------|------------------------|---------------|
| create_task(task_packet)         | 初始化任务与 task_state      | StateResult   |
| run_coder(task_id, round_no)     | 触发 coder 执行            | StateResult   |
| run_reviewer(task_id, round_no)  | 触发 reviewer 审查         | StateResult   |
| advance_state(task_id)           | 应用 controller 规则推进     | StateResult   |
| approve_human_review(task_id)    | 人工签字并结案               | StateResult   |
| send_notification(task_id, event)| 发送关键事件通知              | NotifyResult  |

两个约束：幂等可设计、返回结构化对象。

结果类型体系：
- StateResult：操作成功时必须携带 task_state 快照
- NotifyResult：纯副作用操作，不携带 task_state
- 两者共享 OperationStatus / OperationError / OperationErrorCode
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Protocol, runtime_checkable

from schemas.task_state import TaskState

# ═══════════════════════════════════════════════════
# 共享类型
# ═══════════════════════════════════════════════════


class OperationStatus(StrEnum):
    """操作结果状态。"""

    SUCCESS = "success"
    FAILED = "failed"
    NO_OP = "no_op"  # 幂等调用：操作已生效，无需重复


class OperationErrorCode(StrEnum):
    """操作错误码 — 结构化、可机读。"""

    TASK_NOT_FOUND = "task_not_found"
    TASK_ALREADY_EXISTS = "task_already_exists"
    INVALID_STATE = "invalid_state"  # 当前状态不允许此操作
    TRANSITION_ERROR = "transition_error"  # 状态跃迁违规
    ADAPTER_ERROR = "adapter_error"  # Codex CLI 适配器层错误
    VALIDATION_ERROR = "validation_error"  # 输入校验失败
    STORE_ERROR = "store_error"  # 持久化层错误
    NOTIFICATION_ERROR = "notification_error"  # 通知发送失败


@dataclass(frozen=True)
class OperationError:
    """操作结构化错误。

    业务层根据 code 做分支处理，message 仅供人类诊断。
    """

    code: OperationErrorCode
    message: str
    details: dict[str, Any] = field(default_factory=lambda: dict[str, Any]())


# ═══════════════════════════════════════════════════
# StateResult — 携带 task_state 的操作结果
# ═══════════════════════════════════════════════════


@dataclass(frozen=True)
class StateResult:
    """携带 task_state 快照的操作结果。

    用于 create_task / run_coder / run_reviewer / advance_state / approve_human_review。

    不变式（__post_init__ 执法）：
    - SUCCESS → error 为 None，task_state 非 None
    - NO_OP → error 为 None，task_state 非 None
    - FAILED → error 非 None，task_state 为 None
    """

    status: OperationStatus
    task_state: TaskState | None = None
    error: OperationError | None = None
    message: str = ""

    def __post_init__(self) -> None:
        if self.status == OperationStatus.FAILED:
            if self.error is None:
                raise ValueError("status=FAILED 时 error 不能为 None")
            if self.task_state is not None:
                raise ValueError("status=FAILED 时 task_state 必须为 None")
        else:
            if self.error is not None:
                raise ValueError(f"status={self.status.value} 时 error 必须为 None")
            if self.task_state is None:
                raise ValueError(f"status={self.status.value} 时 task_state 不能为 None")

    @property
    def success(self) -> bool:
        """操作是否成功（含幂等无操作）。"""
        return self.status in {OperationStatus.SUCCESS, OperationStatus.NO_OP}


# ═══════════════════════════════════════════════════
# NotifyResult — 纯副作用操作结果
# ═══════════════════════════════════════════════════


@dataclass(frozen=True)
class NotifyResult:
    """纯副作用操作结果（不携带 task_state）。

    用于 send_notification。

    不变式（__post_init__ 执法）：
    - SUCCESS / NO_OP → error 为 None
    - FAILED → error 非 None
    """

    status: OperationStatus
    error: OperationError | None = None
    message: str = ""

    def __post_init__(self) -> None:
        if self.status == OperationStatus.FAILED:
            if self.error is None:
                raise ValueError("status=FAILED 时 error 不能为 None")
        else:
            if self.error is not None:
                raise ValueError(f"status={self.status.value} 时 error 必须为 None")

    @property
    def success(self) -> bool:
        """操作是否成功（含幂等无操作）。"""
        return self.status in {OperationStatus.SUCCESS, OperationStatus.NO_OP}


# 联合类型 — 需要泛化处理时使用
OperationResult = StateResult | NotifyResult


# ═══════════════════════════════════════════════════
# 外部自动化 API Protocol（合同）
# ═══════════════════════════════════════════════════


@runtime_checkable
class AutomationAPI(Protocol):
    """外部自动化接口合同 — 系统对外的唯一操作入口。

    实现者必须满足以下约束：
    - 所有方法返回判别型结果对象（StateResult 或 NotifyResult），不抛业务异常
    - 操作尽可能幂等（重复调用不产生副作用或返回 NO_OP）
    - task_state 变更必须持久化后再返回
    - 状态推进必须经过 transitions 模块，不自行绕过
    """

    def create_task(self, task_packet: Any) -> StateResult:
        """初始化任务与 task_state。

        前置条件: task_id 不存在
        后置条件: task_state 创建并持久化，状态为 NEW
        幂等: task_id 已存在时返回 NO_OP（附带已有 task_state）

        输入: TaskPacket 实例
        输出: StateResult（含初始 task_state）
        """
        ...

    def run_coder(self, task_id: str, round_no: int) -> StateResult:
        """触发 coder 执行。

        前置条件: task_state.current_status == CODING, round_no 匹配
        后置条件:
          - 调用 CodexAdapter.exec() 执行 coder
          - 解析 coder_result 并绑定到 task_state（coder_done）
          - task_state 推进到 REVIEWING
          - 持久化

        输入: task_id + round_no
        输出: StateResult（含更新后的 task_state）
        """
        ...

    def run_reviewer(self, task_id: str, round_no: int) -> StateResult:
        """触发 reviewer 审查。

        前置条件: task_state.current_status == REVIEWING, round_no 匹配
        后置条件:
          - 调用 CodexAdapter.exec() 执行 reviewer
          - 解析 review_result 并持久化到磁盘
          - 将 reviewer_result_ref 写入 task_state.rounds[-1].reviewer_result_ref
          - 不自行推进状态（由 advance_state 负责）
          - 持久化 task_state

        数据流: reviewer_result_ref 通过 RoundRecord 在 run_reviewer() 与
        advance_state() 之间传递。advance_state() 从 task_state.rounds[-1]
        读取 reviewer_result_ref，加载 review_result，再调用 decide_after_review()
        和 apply_transition()。

        输入: task_id + round_no
        输出: StateResult（含更新后的 task_state，
              其中 rounds[-1].reviewer_result_ref 已绑定）
        """
        ...

    def advance_state(self, task_id: str) -> StateResult:
        """应用 controller 规则推进状态。

        前置条件: task_state.current_status == REVIEWING（有 review_result 可裁决）
        后置条件:
          - 调用 decide_after_review() 获取跃迁结果
          - 调用 apply_transition() 应用跃迁
          - 若结果为 NEEDS_FIX，继续调用 needs_fix_to_coding() 开新轮
          - 若结果为 REVIEW_CLEAN，继续调用 enter_human_review()
          - 持久化
          - 触发法定通知

        输入: task_id
        输出: StateResult（含更新后的 task_state）
        """
        ...

    def approve_human_review(self, task_id: str, *, closure_summary: str = "") -> StateResult:
        """人工签字并结案。

        前置条件: task_state.current_status == HUMAN_REVIEW
        后置条件:
          - task_state 推进到 DONE
          - closure_summary 写入
          - 持久化
          - 触发 task_done 通知

        输入: task_id + 可选结案摘要
        输出: StateResult（含最终 task_state）
        """
        ...

    def send_notification(self, task_id: str, *, event: str) -> NotifyResult:
        """发送关键事件通知。

        法定通知事件（设计方案 §10.2）：
        - needs_human_ruling
        - review_clean_ready_for_human
        - task_done

        输入: task_id + 事件名
        输出: NotifyResult（通知发送结果，无 task_state）

        NOTE: v1 的通知实现可以是最小的（如打印到 stdout），
              但合同必须先定义，后续可替换为 webhook / email 等。
        """
        ...
