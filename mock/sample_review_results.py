"""mock 样例 review_result — 覆盖 P4 六个最低场景所需的 reviewer 产出。

用法::

    from mock.sample_review_results import (
        CLEAN_REVIEW, BLOCKING_FINDING_REVIEW,
        FAILED_CHECKS_REVIEW, NEEDS_HUMAN_RULING_REVIEW,
    )

场景映射:
- CLEAN_REVIEW: verdict=clean, ready=True → 进入人工审查
- BLOCKING_FINDING_REVIEW: verdict=needs_fix, 有 in-scope blocking finding → 回 coder
- FAILED_CHECKS_REVIEW: verdict=needs_fix, 检查不通过 finding → 回 coder
- NEEDS_HUMAN_RULING_REVIEW: verdict=needs_human_ruling → 升级人工
- LOOP_LIMIT_REVIEW: verdict=needs_fix（正常场景），但配合 round_no >= max 触发 loop limit
"""

from __future__ import annotations

from schemas.review_result import (
    Finding,
    NextTaskRecommendation,
    PromotionReadiness,
    ReviewResult,
    Severity,
    TaskVerdict,
)

# ── 场景 1: 完全通过，具备晋级条件 ──
CLEAN_REVIEW = ReviewResult(
    task_id="MOCK_minimal",
    round_no=1,
    findings=[],
    current_task_verdict=TaskVerdict.CLEAN,
    promotion_readiness=PromotionReadiness(
        ready=True,
        rationale="所有 must-do 已完成，全部检查通过，无阻断 finding。",
    ),
    next_task_recommendations=[
        NextTaskRecommendation(
            task_id="P3_interfaces_contract",
            rationale="状态机已就绪，建议进入接口合同定义。",
        ),
    ],
    summary="代码质量良好，任务完整完成，建议晋级。",
)

# ── 场景 2: 有 in-scope blocking finding ──
BLOCKING_FINDING_REVIEW = ReviewResult(
    task_id="MOCK_minimal",
    round_no=1,
    findings=[
        Finding(
            finding_key="missing-blocked-path",
            severity=Severity.P1,
            summary="跃迁表缺少 BLOCKED 路径",
            why_it_matters="设计方案要求 ANY -> BLOCKED 跃迁，当前实现未覆盖。",
            in_scope=True,
            scope_basis="must_do[2]: 实现跃迁规则表",
            blocks_promotion=True,
        ),
    ],
    current_task_verdict=TaskVerdict.NEEDS_FIX,
    promotion_readiness=PromotionReadiness(
        ready=False,
        rationale="存在 P1 阻断 finding，不具备晋级条件。",
    ),
    summary="跃迁表缺少 BLOCKED 路径，需要修复后重新审查。",
)

# ── 场景 3: 检查未通过导致回环 ──
FAILED_CHECKS_REVIEW = ReviewResult(
    task_id="MOCK_minimal",
    round_no=1,
    findings=[
        Finding(
            finding_key="pytest-failures",
            severity=Severity.P0,
            summary="pytest 有 2 个测试失败",
            why_it_matters="required_checks 要求 uv run pytest 全绿，当前有失败。",
            in_scope=True,
            scope_basis="required_checks[0]: uv run pytest",
            blocks_promotion=True,
        ),
    ],
    current_task_verdict=TaskVerdict.NEEDS_FIX,
    promotion_readiness=PromotionReadiness(
        ready=False,
        rationale="required_checks 未全部通过。",
    ),
    summary="测试失败，需要修复后重新运行。",
)

# ── 场景 4: reviewer 无法可靠裁决 ──
NEEDS_HUMAN_RULING_REVIEW = ReviewResult(
    task_id="MOCK_minimal",
    round_no=1,
    findings=[
        Finding(
            finding_key="ambiguous-scope",
            severity=Severity.P2,
            summary="无法确定 task_state 持久化是否在 scope 内",
            why_it_matters="task_packet 的 must_do 未明确提及持久化，但 done_criteria 暗示需要。",
            in_scope=True,
            scope_basis="done_criteria[2] 暗示但 must_do 未明确",
            blocks_promotion=False,
        ),
    ],
    current_task_verdict=TaskVerdict.NEEDS_HUMAN_RULING,
    promotion_readiness=PromotionReadiness(
        ready=False,
        rationale="scope 判定存在歧义，无法自动裁决。",
    ),
    summary="scope 边界不明确，需要人工裁决。",
)

# ── 场景 5: 配合 loop limit 使用（本身是 needs_fix，但 round_no >= max 时触发 loop limit）──
LOOP_LIMIT_REVIEW = ReviewResult(
    task_id="MOCK_minimal",
    round_no=5,
    findings=[
        Finding(
            finding_key="recurring-test-failure",
            severity=Severity.P1,
            summary="反复出现的测试失败",
            why_it_matters="经过多轮修复仍未解决，可能需要人工介入。",
            in_scope=True,
            scope_basis="required_checks[0]: uv run pytest",
            blocks_promotion=True,
        ),
    ],
    current_task_verdict=TaskVerdict.NEEDS_FIX,
    promotion_readiness=PromotionReadiness(
        ready=False,
        rationale="仍有阻断 finding，且已达回环上限。",
    ),
    summary="多轮修复未能解决测试失败，建议人工介入。",
)
