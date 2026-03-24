from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import DecisionAction, InitiativeRuntimeState, TaskStatus, TransitionDecision, Trend
from .utils import read_json


FUNC_RANK = {"MISSING": 0, "PARTIAL": 1, "COMPLETE": 2}
REV_RANK = {"MISSING": 0, "PARTIAL": 1, "COMPLETE": 2, "NOT_APPLICABLE": 2}
TEST_RANK = {"MISSING": 0, "WEAK": 1, "ADEQUATE": 2, "STRONG": 3}
HARD_ENTROPY = {
    "DOUBLE_SOURCE_OF_TRUTH",
    "SHADOW_STATE",
    "IMPLICIT_FALLBACK",
    "NO_EXIT_COMPAT_LOGIC",
    "LEAKY_ABSTRACTION",
}


def load_observation(path: str | Path) -> dict[str, Any]:
    data = read_json(path)
    required = [
        "gate_status",
        "gate_reason",
        "closure_state",
        "entropy_signals",
        "baseline_adherence",
        "mandatory_fixes",
        "suggested_action",
    ]
    missing = [key for key in required if key not in data]
    if missing:
        raise ValueError(f"observation missing required fields: {', '.join(missing)}")
    return data


def _closure_score(observation: dict[str, Any]) -> int:
    closure = observation.get("closure_state", {})
    return (
        FUNC_RANK.get(closure.get("functional_completeness", "MISSING"), 0)
        + REV_RANK.get(closure.get("reverse_path_completeness", "MISSING"), 0)
        + TEST_RANK.get(closure.get("test_proof_strength", "MISSING"), 0)
    )


def _confirmed_p0s(observation: dict[str, Any]) -> list[dict[str, Any]]:
    fixes = observation.get("mandatory_fixes", []) or []
    return [
        item
        for item in fixes
        if item.get("severity") == "P0" and item.get("evidence_type") in {"CONFIRMED_BY_RUNTIME_FACT", "CONFIRMED_BY_CODE"}
    ]


def _hard_entropy_signals(observation: dict[str, Any]) -> set[str]:
    return set(observation.get("entropy_signals", []) or []).intersection(HARD_ENTROPY)


def _fix_count(observation: dict[str, Any]) -> int:
    return len(observation.get("mandatory_fixes", []) or [])


def _baseline_deviation_count(observation: dict[str, Any]) -> int:
    contracts = observation.get("baseline_adherence", {}).get("contracts", []) or []
    return sum(1 for item in contracts if item.get("status") in {"DEVIATED", "BASELINE_NEEDS_UPDATE"})


def _ready_for_anchor(observation: dict[str, Any]) -> bool:
    closure = observation.get("closure_state", {})
    return (
        observation.get("gate_status") == "PROCEED"
        and closure.get("functional_completeness") == "COMPLETE"
        and closure.get("reverse_path_completeness") in {"COMPLETE", "NOT_APPLICABLE"}
        and closure.get("test_proof_strength") in {"ADEQUATE", "STRONG"}
        and not observation.get("entropy_signals")
        and not observation.get("mandatory_fixes")
    )


def _has_baseline_needs_update(observation: dict[str, Any]) -> bool:
    contracts = observation.get("baseline_adherence", {}).get("contracts", []) or []
    return any(item.get("status") == "BASELINE_NEEDS_UPDATE" for item in contracts)


def compare_observations(previous: dict[str, Any] | None, current: dict[str, Any]) -> Trend:
    if previous is None:
        return Trend.INITIAL

    previous_p0 = len(_confirmed_p0s(previous))
    current_p0 = len(_confirmed_p0s(current))
    if current_p0 > previous_p0:
        return Trend.DIVERGING
    if current_p0 < previous_p0:
        return Trend.CONVERGING

    previous_hard_entropy = len(_hard_entropy_signals(previous))
    current_hard_entropy = len(_hard_entropy_signals(current))
    if current_hard_entropy > previous_hard_entropy:
        return Trend.DIVERGING
    if current_hard_entropy < previous_hard_entropy:
        return Trend.CONVERGING

    previous_closure = _closure_score(previous)
    current_closure = _closure_score(current)
    if current_closure > previous_closure:
        if current.get("entropy_signals"):
            return Trend.CONVERGING_WITH_DEBT
        return Trend.CONVERGING

    previous_fixes = _fix_count(previous)
    current_fixes = _fix_count(current)
    if current_fixes < previous_fixes:
        return Trend.CONVERGING

    previous_baseline = _baseline_deviation_count(previous)
    current_baseline = _baseline_deviation_count(current)
    if current_baseline > previous_baseline:
        return Trend.DIVERGING
    if current_baseline < previous_baseline:
        return Trend.CONVERGING

    if current == previous:
        return Trend.STALLED

    return Trend.STALLED


def _map_p0_to_action(fix: dict[str, Any]) -> DecisionAction:
    plane = fix.get("plane")
    if plane == "CLOSURE":
        return DecisionAction.COMPLETE_MISSING_SCOPE
    if plane == "TEST_PROOF":
        return DecisionAction.ADD_PROOF_TESTS
    if plane == "ENTROPY":
        return DecisionAction.REWORK_ARCHITECTURE
    return DecisionAction.REWORK_ARCHITECTURE


def step_transition(
    task_key: str,
    task_state: dict[str, Any],
    previous_observation: dict[str, Any] | None,
    current_observation: dict[str, Any],
    *,
    max_probe: int = 2,
    stall_window: int = 2,
) -> TransitionDecision:
    trend = compare_observations(previous_observation, current_observation)

    if _ready_for_anchor(current_observation):
        return TransitionDecision(
            task_key=task_key,
            trend=Trend.CONVERGED_AND_STABLE,
            action=DecisionAction.READY_FOR_ANCHOR,
            why="Task snapshot satisfies local closure, proof, and entropy requirements; ready for formal Task收口。",
        )

    if current_observation.get("gate_status") == "NEED_RUNTIME_FACTS":
        probe_count = int(task_state.get("probe_count", 0))
        required = current_observation.get("required_runtime_facts", []) or []
        if probe_count >= max_probe:
            return TransitionDecision(
                task_key=task_key,
                trend=Trend.STALLED,
                action=DecisionAction.ESCALATE_TO_HUMAN,
                why="多轮仍缺关键运行事实，局部自动循环已失去可观测性。",
                next_required_facts=required,
            )
        return TransitionDecision(
            task_key=task_key,
            trend=trend if trend != Trend.INITIAL else Trend.STALLED,
            action=DecisionAction.REQUEST_RUNTIME_FACTS,
            why="当前阻断判断依赖缺失或过旧的运行事实。",
            next_required_facts=required,
        )

    confirmed_p0s = _confirmed_p0s(current_observation)
    if confirmed_p0s:
        fix = confirmed_p0s[0]
        return TransitionDecision(
            task_key=task_key,
            trend=Trend.DIVERGING,
            action=_map_p0_to_action(fix),
            why=f"存在已证实 P0：{fix.get('id', 'UNKNOWN_P0')}，必须先解除主约束。",
        )

    if _has_baseline_needs_update(current_observation):
        return TransitionDecision(
            task_key=task_key,
            trend=Trend.STALLED,
            action=DecisionAction.ESCALATE_TO_HUMAN,
            why="当前实现可能优于基线，但正式基线待修订，需升级裁决。",
        )

    previous_hard = _hard_entropy_signals(previous_observation or {})
    current_hard = _hard_entropy_signals(current_observation)
    if current_hard - previous_hard:
        return TransitionDecision(
            task_key=task_key,
            trend=Trend.DIVERGING,
            action=DecisionAction.REWORK_ARCHITECTURE,
            why=f"新增硬熵信号：{sorted(current_hard - previous_hard)}。",
        )

    stall_count = int(task_state.get("stall_count", 0))
    if trend == Trend.STALLED and stall_count >= stall_window:
        return TransitionDecision(
            task_key=task_key,
            trend=Trend.STALLED,
            action=DecisionAction.ESCALATE_TO_HUMAN,
            why="连续多轮无实质推进，当前 Task 内控制策略失效。",
        )

    suggested = (current_observation.get("suggested_action") or {}).get("type", "")
    mapping = {
        "PATCH_LOCAL": DecisionAction.PATCH_LOCAL,
        "COMPLETE_MISSING_SCOPE": DecisionAction.COMPLETE_MISSING_SCOPE,
        "ADD_PROOF_TESTS": DecisionAction.ADD_PROOF_TESTS,
        "REMOVE_ENTROPY_SIGNAL": DecisionAction.REMOVE_ENTROPY_SIGNAL,
        "REWORK_ARCHITECTURE": DecisionAction.REWORK_ARCHITECTURE,
        "ESCALATE_TO_HUMAN": DecisionAction.ESCALATE_TO_HUMAN,
    }
    action = mapping.get(suggested, DecisionAction.PATCH_LOCAL)
    why = (current_observation.get("suggested_action") or {}).get("why") or "当前不存在已证实硬阻断，按局部最短路径继续推进。"
    return TransitionDecision(
        task_key=task_key,
        trend=trend,
        action=action,
        why=why,
    )
