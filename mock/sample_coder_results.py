"""mock 样例 coder_result — 覆盖 P4 六个最低场景所需的 coder 产出。

用法::

    from mock.sample_coder_results import CLEAN_CODER, PARTIAL_CODER, FAILED_CHECKS_CODER

场景映射:
- CLEAN_CODER: 所有检查通过，代码变更完整 → 配合 clean review
- PARTIAL_CODER: 部分完成，有 out_of_scope 说明 → 配合 blocking finding review
- FAILED_CHECKS_CODER: 检查未通过 → 配合 checks 未过 review
"""

from __future__ import annotations

from schemas.coder_result import CheckResult, CheckStatus, CoderResult

# ── 场景 1/6: 完整完成，所有检查通过 ──
CLEAN_CODER = CoderResult(
    task_id="MOCK_minimal",
    round_no=1,
    files_changed=[
        "automation/controller/transitions.py",
        "tests/test_transitions.py",
    ],
    contracts_addressed=[
        "状态枚举可程序化引用",
        "跃迁表覆盖设计方案所有路径",
    ],
    cleanups_done=[],
    check_results=[
        CheckResult(check_name="uv run pytest", status=CheckStatus.PASSED),
        CheckResult(check_name="uv run ruff check .", status=CheckStatus.PASSED),
        CheckResult(check_name="uv run ruff format --check .", status=CheckStatus.PASSED),
        CheckResult(check_name="uv run pyright", status=CheckStatus.PASSED),
    ],
    out_of_scope_notes=[],
    summary="所有 must-do 已完成，全部检查通过。",
)

# ── 场景 2/3: 部分完成，有遗留 ──
PARTIAL_CODER = CoderResult(
    task_id="MOCK_scenario",
    round_no=1,
    files_changed=[
        "automation/controller/transitions.py",
    ],
    contracts_addressed=[
        "状态枚举可程序化引用",
    ],
    cleanups_done=[],
    check_results=[
        CheckResult(check_name="uv run pytest", status=CheckStatus.PASSED),
        CheckResult(check_name="uv run ruff check .", status=CheckStatus.PASSED),
        CheckResult(check_name="uv run ruff format --check .", status=CheckStatus.PASSED),
        CheckResult(check_name="uv run pyright", status=CheckStatus.PASSED),
    ],
    out_of_scope_notes=[
        "跃迁表未覆盖 BLOCKED 路径，留待后续任务",
    ],
    summary="完成了状态枚举定义，跃迁表部分完成。",
)

# ── 场景 3: 检查未通过 ──
FAILED_CHECKS_CODER = CoderResult(
    task_id="MOCK_scenario",
    round_no=1,
    files_changed=[
        "automation/controller/transitions.py",
        "tests/test_transitions.py",
    ],
    contracts_addressed=[
        "状态枚举可程序化引用",
        "跃迁表覆盖设计方案所有路径",
    ],
    cleanups_done=[],
    check_results=[
        CheckResult(
            check_name="uv run pytest", status=CheckStatus.FAILED, message="2 tests failed"
        ),
        CheckResult(check_name="uv run ruff check .", status=CheckStatus.PASSED),
        CheckResult(check_name="uv run ruff format --check .", status=CheckStatus.PASSED),
        CheckResult(check_name="uv run pyright", status=CheckStatus.PASSED),
    ],
    out_of_scope_notes=[],
    summary="代码变更完成但有 2 个测试未通过。",
)
