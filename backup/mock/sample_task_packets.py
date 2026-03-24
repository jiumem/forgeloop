"""mock 样例 task_packet — 可复用的标准测试输入。

提供最小、场景、完整三个等级的样例，供 mock 场景、smoke test、
以及后续 P4/P5/P6 联调复用。

用法::

    from mock.sample_task_packets import MINIMAL_PACKET, SCENARIO_PACKET, FULL_PACKET

    # 直接使用 Pydantic 实例
    state = TaskState(task_id=MINIMAL_PACKET.task_id)

    # 需要 dict / JSON 时
    MINIMAL_PACKET.model_dump()
    MINIMAL_PACKET.model_dump_json(indent=2)
"""

from __future__ import annotations

from schemas.task_packet import PromotionPolicy, TaskPacket

# ── 最小合法 task_packet ──
# 仅包含必填字段，所有可选字段取默认值。
MINIMAL_PACKET = TaskPacket(
    task_id="MOCK_minimal",
    title="最小样例任务",
    must_do=["实现功能 A"],
    done_criteria=["功能 A 测试通过"],
)

# ── 场景级 task_packet ──
# 供 ReviewResult fixtures 的 scope_basis 引用，字段足够丰富。
# 所有 finding.scope_basis 中的索引和内容必须在此 packet 中可查。
SCENARIO_PACKET = TaskPacket(
    task_id="MOCK_scenario",
    title="场景测试任务",
    must_do=[
        "定义 TaskStatus 枚举",
        "定义 NextAction 枚举",
        "实现跃迁规则表",
    ],
    done_criteria=[
        "状态枚举可程序化引用",
        "跃迁表覆盖设计方案所有路径",
        "task_state 可 JSON 序列化/反序列化",
    ],
    required_checks=[
        "uv run pytest",
        "uv run ruff check .",
    ],
    promotion_policy=PromotionPolicy(
        auto_promote=False,
        max_review_rounds=5,
    ),
)

# ── 完整 task_packet ──
# 填满所有字段，展示真实业务场景。
FULL_PACKET = TaskPacket(
    task_id="P2_state_machine",
    title="状态枚举、跃迁表与 task_state 持久化",
    phase="M1",
    chain="v1",
    entry_docs=[
        "docs/Codex 自动任务编码循环设计方案.md",
        "docs/Codex 自动任务编码循环任务规划文档.md",
    ],
    must_do=[
        "定义 TaskStatus 枚举",
        "定义 NextAction 枚举",
        "实现跃迁规则表",
        "实现 task_state 持久化",
    ],
    must_not_do=[
        "不做多任务并行调度",
        "不做 CI/GitHub Actions 集成",
    ],
    done_criteria=[
        "状态枚举可程序化引用",
        "跃迁表覆盖设计方案所有路径",
        "task_state 可 JSON 序列化/反序列化",
        "uv run pytest 全绿",
    ],
    depends_on=["P1_schema_baseline"],
    related_tasks=["P3_interfaces_contract"],
    required_checks=[
        "uv run pytest",
        "uv run ruff check .",
        "uv run ruff format --check .",
        "uv run pyright",
    ],
    promotion_policy=PromotionPolicy(
        auto_promote=False,
        max_review_rounds=5,
    ),
)
