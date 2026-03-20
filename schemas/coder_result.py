"""coder_result — 执行结果模型。

coder_result 不是"任务是否通过"的证明，而是当前这一轮执行客观做了什么的记录。
它覆盖五个面：代码面、法位面、清理面、验证面、边界面。

设计依据：设计方案 §5.2
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class CheckStatus(StrEnum):
    """单项检查的执行状态。"""

    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


def _check_result_json_schema_extra(schema: dict[str, Any]) -> None:
    """注入 if/then 条件约束: status=skipped|error 时 message 必须非空。

    这确保 codex exec --output-schema 产出的 JSON 也受此规则约束，
    而不仅仅依赖 Pydantic 运行时 validator。
    """
    schema["allOf"] = [
        {
            "if": {
                "properties": {"status": {"enum": ["skipped", "error"]}},
                "required": ["status"],
            },
            "then": {
                "properties": {"message": {"minLength": 1}},
                "required": ["message"],
            },
        }
    ]


class CheckResult(BaseModel):
    """单项检查的执行结果。"""

    model_config = ConfigDict(json_schema_extra=_check_result_json_schema_extra)

    check_name: str = Field(..., min_length=1, description="检查名称")
    status: CheckStatus = Field(..., description="执行状态")
    message: str = Field(default="", description="附加说明，skipped/error 时必须填原因")

    @model_validator(mode="after")
    def _require_message_when_skipped_or_error(self) -> CheckResult:
        """设计方案 §5.2: 未执行的检查必须显式写明原因。"""
        if self.status in {CheckStatus.SKIPPED, CheckStatus.ERROR} and not self.message.strip():
            msg = f"status={self.status.value} 时 message 不能为空（必须写明原因）"
            raise ValueError(msg)
        return self


class CoderResult(BaseModel):
    """执行结果模型 — 四个核心模型之一。

    关键裁决:
    - coder_result 可以声明"我完成了什么"，不能宣布"任务已通过"
    - 未执行的检查必须显式写明原因
    - 相邻内容未做不是缺陷，而是合同的一部分

    五个面:
    - 代码面: files_changed
    - 法位面: contracts_addressed
    - 清理面: cleanups_done
    - 验证面: check_results
    - 边界面: out_of_scope_notes
    """

    task_id: str = Field(
        ..., min_length=1, pattern=r"^[A-Za-z0-9_-]+$", description="关联的任务 ID"
    )
    round_no: int = Field(..., ge=1, description="第几轮执行")

    # ── 代码面 ──
    files_changed: list[str] = Field(
        default_factory=list,
        description="变更的文件路径列表",
    )

    # ── 法位面 ──
    contracts_addressed: list[str] = Field(
        default_factory=list,
        description="收正的接口 / seam / contract 列表",
    )

    # ── 清理面 ──
    cleanups_done: list[str] = Field(
        default_factory=list,
        description="删除或清理的旧代码 / 旧命名 / 旧路径",
    )

    # ── 验证面 ──
    check_results: list[CheckResult] = Field(
        default_factory=lambda: list[CheckResult](),
        description="各项检查的执行结果",
    )

    # ── 边界面 ──
    out_of_scope_notes: list[str] = Field(
        default_factory=list,
        description="刻意未做的相邻内容说明",
    )

    # ── 执行摘要 ──
    summary: str = Field(
        default="",
        description="本轮执行的自然语言摘要（解释用，非业务真值）",
    )
