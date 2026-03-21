"""base — Codex CLI 适配器合同（内部接口层）。

这是设计方案 §6.2 的合同定义：业务层不应直接散落 subprocess.run()，
而应通过一个稳定抽象与 Codex CLI 交互。

本模块只定义合同（Protocol + 配置/结果/错误类型），不包含实现。
实现在 P6_codex_adapter 阶段落地。

四个核心方法：
| 方法               | 说明                         |
|-------------------|----------------------------|
| exec(...)         | 新开一次非交互运行                  |
| resume(...)       | 续跑已有线程                     |
| parse_events(...) | 解析 JSONL 仅供日志与调试           |
| read_final_output | 读取 schema 约束后的最终结果         |

稳定依赖与刻意不依赖：
- 稳定依赖：最终 schema 输出（read_final_output）
- 弱依赖：JSONL 事件流（parse_events，仅观测用）
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

# ═══════════════════════════════════════════════════
# 错误类型
# ═══════════════════════════════════════════════════


class AdapterErrorKind(StrEnum):
    """适配器错误分类 — 结构化、可机读。"""

    INVOCATION_FAILED = "invocation_failed"  # CLI 调用失败（进程启动失败）
    TIMEOUT = "timeout"  # 执行超时
    NON_ZERO_EXIT = "non_zero_exit"  # 进程返回非零 exit code
    OUTPUT_MISSING = "output_missing"  # 期望的输出文件不存在
    OUTPUT_PARSE_ERROR = "output_parse_error"  # 输出文件解析失败（不符合 schema）
    RESUME_FAILED = "resume_failed"  # 续跑失败（线程不存在或状态不可续）
    EVENT_PARSE_ERROR = "event_parse_error"  # JSONL 事件解析失败（弱依赖）


@dataclass(frozen=True)
class AdapterError:
    """适配器结构化错误 — 不用 Exception，而是作为 result 的一部分返回。

    设计原则：错误对象必须结构化、可机读。
    业务层根据 kind 做分支处理，detail 仅供人类诊断。
    """

    kind: AdapterErrorKind
    detail: str
    exit_code: int | None = None
    stderr_tail: str = ""


# ═══════════════════════════════════════════════════
# 运行配置
# ═══════════════════════════════════════════════════


class SandboxMode(StrEnum):
    """Codex sandbox 模式。

    对应设计方案 §7.4 默认安全配置。
    """

    READ_ONLY = "read-only"
    WORKSPACE_WRITE = "workspace-write"


class ApprovalMode(StrEnum):
    """Codex approval 模式。"""

    NEVER = "never"
    ON_REQUEST = "on-request"


class AgentRole(StrEnum):
    """执行角色 — 决定默认安全配置。"""

    CODER = "coder"
    REVIEWER = "reviewer"


@dataclass(frozen=True)
class CodexRunConfig:
    """单次 Codex CLI 运行的配置。

    设计方案 §10.3 原则：显式传关键参数，不依赖全局默认。
    """

    role: AgentRole
    task_id: str
    round_no: int
    prompt: str

    # ── 路径 ──
    working_dir: Path = field(default_factory=lambda: Path("."))
    output_schema_path: Path | None = None
    output_dir: Path | None = None

    # ── 模型与推理 ──
    model: str = ""
    config_overrides: dict[str, str] = field(default_factory=lambda: dict[str, str]())

    # ── 安全 ──
    sandbox: SandboxMode = SandboxMode.READ_ONLY
    approval: ApprovalMode = ApprovalMode.NEVER

    # ── 超时 ──
    timeout_seconds: int | None = None


# ═══════════════════════════════════════════════════
# 运行结果
# ═══════════════════════════════════════════════════


@dataclass(frozen=True)
class CodexRunResult:
    """单次 Codex CLI 运行的结果。

    无论成功/失败，都返回此对象（而非抛异常）。
    业务层通过 error 是否为 None 判断成功与否。
    """

    exit_code: int
    stdout: str = ""
    stderr: str = ""
    output_file: Path | None = None
    duration_seconds: float = 0.0
    thread_id: str | None = None
    error: AdapterError | None = None

    @property
    def success(self) -> bool:
        """运行是否成功：exit_code == 0 且无结构化错误。"""
        return self.exit_code == 0 and self.error is None


# ═══════════════════════════════════════════════════
# JSONL 事件（弱依赖，仅观测用）
# ═══════════════════════════════════════════════════


@dataclass(frozen=True)
class CodexEvent:
    """单条 JSONL 事件 — 弱依赖，仅供日志与调试。

    业务裁决不应依赖事件内容。
    """

    event_type: str
    data: dict[str, Any] = field(default_factory=lambda: dict[str, Any]())
    raw_line: str = ""


# ═══════════════════════════════════════════════════
# 解析结果
# ═══════════════════════════════════════════════════


@dataclass(frozen=True)
class ParsedOutput:
    """read_final_output 的返回类型 — 解析结果 + 可能的错误。

    独立于 CodexRunResult（frozen，不可追加错误），
    让解析阶段拥有自己的结果对象。

    不变式（__post_init__ 执法）：
    - 成功: value 非 None 且 error 为 None
    - 失败: value 为 None 且 error 非 None
    - 禁止: 空对象（两者皆 None）或矛盾态（两者皆非 None）
    """

    value: Any = None
    error: AdapterError | None = None

    def __post_init__(self) -> None:
        if self.value is None and self.error is None:
            raise ValueError("ParsedOutput 不允许空对象（value 和 error 不能同时为 None）")
        if self.value is not None and self.error is not None:
            raise ValueError("ParsedOutput 不允许矛盾态（value 和 error 不能同时非 None）")

    @property
    def success(self) -> bool:
        """解析是否成功：有值且无错误。"""
        return self.value is not None and self.error is None


# ═══════════════════════════════════════════════════
# 适配器 Protocol（合同）
# ═══════════════════════════════════════════════════


@runtime_checkable
class CodexAdapter(Protocol):
    """Codex CLI 适配器合同 — 内部接口层。

    业务层通过此 Protocol 与 Codex CLI 交互，
    不直接接触 subprocess / 命令拼接。

    实现者必须满足以下约束：
    - exec / resume 返回 CodexRunResult，不抛异常
    - read_final_output 返回 ParsedOutput（独立结果对象），不修改传入的 CodexRunResult
    - parse_events 是弱依赖，允许降级返回空列表
    """

    def exec(self, config: CodexRunConfig) -> CodexRunResult:
        """新开一次非交互运行（codex exec）。

        输入: CodexRunConfig（包含 prompt、schema、安全配置等）
        输出: CodexRunResult（包含 exit_code、输出文件路径、可能的错误）
        """
        ...

    def resume(self, config: CodexRunConfig, *, thread_id: str) -> CodexRunResult:
        """续跑已有线程（codex exec resume）。

        输入: CodexRunConfig + 之前运行的 thread_id
        输出: CodexRunResult
        """
        ...

    def read_final_output(self, result: CodexRunResult, *, schema_type: type) -> ParsedOutput:
        """读取并解析 schema 约束后的最终结果。

        这是稳定依赖 — 业务裁决的唯一输入来源。

        输入: CodexRunResult（需要 output_file 存在）+ 期望的 Pydantic schema 类型
        输出: ParsedOutput
          - 成功: value 为解析后的 Pydantic 模型实例，error 为 None
          - 失败: value 为 None，error 记录 AdapterError（OUTPUT_MISSING / OUTPUT_PARSE_ERROR）

        不修改传入的 CodexRunResult（frozen），错误信息在 ParsedOutput.error 中独立承载。

        NOTE: value 的具体类型在 P6 实现时会用泛型收紧。
              当前合同阶段用 Any 表达意图。
        """
        ...

    def parse_events(self, stdout: str) -> list[CodexEvent]:
        """解析 JSONL 事件流 — 弱依赖，仅供日志与调试。

        业务裁决不应依赖此方法的输出。
        解析失败时返回空列表（降级而非报错）。

        输入: codex exec 的 stdout（--json 模式下为 JSONL）
        输出: 事件列表
        """
        ...
