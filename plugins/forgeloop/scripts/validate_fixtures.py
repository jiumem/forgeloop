#!/usr/bin/env python3
"""校验 Fixture 字段、三 Tracker 等价性与公开协议不变量。"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REQUIRED = {
    "id", "group", "tracker", "initial_state", "entry_prompt", "expected_writes",
    "forbidden_writes", "terminal_state", "failure_diagnostic", "domain_state",
}
RUNTIME_REQUIRED = {"event_trace", "final_native_state"}
TRACKERS = {"github", "gitlab", "local"}
RUNTIME_EVENTS = {
    "RUN_CLAIMED",
    "CODER_RESULT",
    "REVIEW_RESULT",
    "INTEGRATION_RESULT",
    "ACCEPTANCE_RESULT",
    "RUN_PAUSED",
    "RUN_CANCELLED",
    "RUN_RESUMED",
    "EVENT_SUPERSEDED",
}
REVIEW_PASS = re.compile(r"^(?:[A-Z0-9]+_)*DUAL_PASS$")
ACCEPTANCE_PASS = re.compile(r"^(?:SPEC_PASS(?:_[A-Z0-9]+)*|INITIATIVE_PASS)$")
REPAIR_ROUND = re.compile(r"^(?:[A-Z]+_)*REPAIR_([1-9][0-9]*)")


def event_payload(event: str, event_name: str) -> str | None:
    prefix = f"{event_name}:"
    return event[len(prefix):] if event.startswith(prefix) else None


def validate(path: Path) -> list[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    runtime = data.get("kind") == "run-initiative-runtime"
    checkpoint_transport = data.get("kind") == "checkpoint-transport"
    errors: list[str] = []
    cases = data.get("cases", [])
    ids: set[str] = set()
    groups: dict[str, list[dict]] = {}
    for case in cases:
        missing = REQUIRED - set(case)
        if missing:
            errors.append(f"{case.get('id', '<unknown>')}: 缺失字段 {sorted(missing)}")
            continue
        if case["id"] in ids:
            errors.append(f"重复 Fixture ID：{case['id']}")
        ids.add(case["id"])
        groups.setdefault(case["group"], []).append(case)
        if not case["expected_writes"] or not case["forbidden_writes"]:
            errors.append(f"{case['id']}: 必须同时声明预期写入和禁止写入")
        if runtime:
            runtime_missing = RUNTIME_REQUIRED - set(case)
            if runtime_missing:
                errors.append(f"{case['id']}: 缺失运行轨迹字段 {sorted(runtime_missing)}")
                continue
            errors.extend(validate_runtime_case(case))
        if checkpoint_transport:
            errors.extend(validate_checkpoint_transport_case(case))
    for group, group_cases in groups.items():
        if len(group_cases) == 1:
            continue
        trackers = {case["tracker"] for case in group_cases}
        if trackers != TRACKERS:
            errors.append(f"{group}: Tracker 覆盖不完整 {sorted(trackers)}")
            continue
        states = {json.dumps(case["domain_state"], sort_keys=True, ensure_ascii=False) for case in group_cases}
        terminals = {case["terminal_state"] for case in group_cases}
        if len(states) != 1 or len(terminals) != 1:
            errors.append(f"{group}: 三 Tracker 领域终态不等价")
    if runtime and "evidence_cases" in data:
        errors.extend(validate_evidence_cases(data["evidence_cases"], ids, cases))
    return errors


def validate_evidence_cases(
    evidence_cases: object, case_ids: set[str], cases: list[dict]
) -> list[str]:
    """校验目标漂移 Fixture 的不可变绑定、线性化刷新与精确回读。"""

    if not isinstance(evidence_cases, list):
        return ["evidence_cases 必须是列表"]
    errors: list[str] = []
    states = {case["id"]: case["domain_state"] for case in cases if "id" in case}
    seen: set[str] = set()
    integration_fields = {
        "candidate_head", "target_before", "target_after", "integration_method", "native_ref"
    }
    seal_fields = {
        "acceptance_level", "subject_revision", "membership", "final_target_commit",
        "idempotency_key", "native_checkpoint_ref", "integration_target_afters",
        "all_in_final_history", "eligibility_refresh", "native_readback",
    }
    for evidence in evidence_cases:
        if not isinstance(evidence, dict):
            errors.append("evidence_cases 条目必须是对象")
            continue
        case_id = evidence.get("id")
        if not isinstance(case_id, str) or case_id not in case_ids:
            errors.append(f"{case_id or '<unknown>'}: 证据必须引用已有 Fixture")
            continue
        if case_id in seen:
            errors.append(f"{case_id}: 重复结构化证据")
            continue
        seen.add(case_id)
        integrations = evidence.get("integrations")
        if not isinstance(integrations, list):
            errors.append(f"{case_id}: integrations 必须是列表")
            continue
        for index, binding in enumerate(integrations):
            missing = integration_fields - set(binding) if isinstance(binding, dict) else integration_fields
            if missing or not all(isinstance(binding.get(field), str) and binding[field] for field in integration_fields):
                errors.append(f"{case_id}: Integration binding {index} 缺失非空字段 {sorted(missing)}")
        if case_id == "already-present-current-target" and integrations:
            binding = integrations[0]
            if binding.get("integration_method") != "already_present" or binding.get("target_before") != binding.get("target_after"):
                errors.append(f"{case_id}: ALREADY_PRESENT 必须绑定相同当前目标")

        seal = evidence.get("seal")
        if seal is not None:
            missing = seal_fields - set(seal) if isinstance(seal, dict) else seal_fields
            if missing:
                errors.append(f"{case_id}: Acceptance Seal 缺失字段 {sorted(missing)}")
                continue
            scalar_fields = seal_fields - {
                "membership", "integration_target_afters", "all_in_final_history",
                "eligibility_refresh", "native_readback",
            }
            if not all(isinstance(seal.get(field), str) and seal[field] for field in scalar_fields):
                errors.append(f"{case_id}: Acceptance Seal 标量绑定必须非空")
            if not isinstance(seal.get("membership"), list) or not seal["membership"]:
                errors.append(f"{case_id}: Acceptance Seal 必须绑定 confirmed membership")
            expected_afters = [binding.get("target_after") for binding in integrations]
            if seal.get("integration_target_afters") != expected_afters or seal.get("all_in_final_history") is not True:
                errors.append(f"{case_id}: Seal 必须验证全部 Integration target_after")
            refresh = seal.get("eligibility_refresh", {})
            if refresh.get("final_target_commit") != seal.get("final_target_commit") or refresh.get("observed_target") != seal.get("final_target_commit"):
                errors.append(f"{case_id}: Seal eligibility refresh 必须命中 final target Commit")
            readback = seal.get("native_readback", {})
            if readback.get("exact_match") is not True or readback.get("native_ref") != seal.get("native_checkpoint_ref"):
                errors.append(f"{case_id}: Acceptance Seal 必须精确原生回读")
        if states.get(case_id, {}).get("seal_confirmed") and seal is None:
            errors.append(f"{case_id}: seal_confirmed 缺失结构化 Seal")

        invalidated = evidence.get("invalidated_refresh")
        if invalidated is not None and (
            invalidated.get("reviewed_commit") == invalidated.get("observed_target")
            or invalidated.get("payload_published") is not False
        ):
            errors.append(f"{case_id}: 漂移后的旧 Acceptance 不得发布")
        acceptance_check = evidence.get("acceptance_check")
        if acceptance_check is not None:
            required = {
                "final_target_commit", "integration_target_afters",
                "all_in_final_history", "behavior_pass",
            }
            if not isinstance(acceptance_check, dict) or required - set(acceptance_check):
                errors.append(f"{case_id}: Acceptance check 缺失结构化字段")
            elif acceptance_check["integration_target_afters"] != [
                binding.get("target_after") for binding in integrations
            ]:
                errors.append(f"{case_id}: Acceptance check 未绑定全部 target_after")
        after_refresh = evidence.get("drift_after_eligibility_refresh")
        if after_refresh is not None and (
            seal is None
            or after_refresh.get("observed_later_target") == seal.get("final_target_commit")
            or states.get(case_id, {}).get("acceptance_rerun") is not False
        ):
            errors.append(f"{case_id}: eligibility refresh 后漂移不得废弃精确确认的 Seal")
    return errors


def validate_checkpoint_transport_case(case: dict) -> list[str]:
    """校验字面量传输 Fixture 的确认与副作用声明。"""

    errors: list[str] = []
    case_id = case["id"]
    state = case["domain_state"]
    required = {"writes", "payload_equal", "advance"}
    missing = required - set(state)
    if missing:
        return [f"{case_id}: Checkpoint transport 缺失领域字段 {sorted(missing)}"]
    if not isinstance(state["writes"], int) or state["writes"] < 0:
        errors.append(f"{case_id}: writes 必须是非负整数")
    terminal = case["terminal_state"]
    if terminal == "CONFIRMED" and (
        state["payload_equal"] is not True or state["advance"] is not True
    ):
        errors.append(f"{case_id}: CONFIRMED 必须完整匹配 Payload 后才可推进")
    if terminal in {"UNCONFIRMED", "RECOVERY_CONFLICT"} and state["advance"] is not False:
        errors.append(f"{case_id}: 未确认或冲突的 Checkpoint 不得推进")
    if state.get("sentinel_effects", 0) != 0 or state.get("worktree_unchanged", True) is not True:
        errors.append(f"{case_id}: 攻击性 Payload 不得产生副作用或改变 worktree")
    return errors


def validate_runtime_case(case: dict) -> list[str]:
    """校验声明轨迹自身满足 run-initiative 的完成与恢复不变量。"""

    errors: list[str] = []
    case_id = case["id"]
    trace = case["event_trace"]
    final = case["final_native_state"]
    if not isinstance(trace, list) or not all(isinstance(event, str) for event in trace):
        return [f"{case_id}: event_trace 必须是字符串列表"]
    if not isinstance(final, dict):
        return [f"{case_id}: final_native_state 必须是对象"]

    event_names = [event.split(":", 1)[0] for event in trace]
    unknown_events = sorted(set(event_names) - RUNTIME_EVENTS)
    if unknown_events:
        errors.append(f"{case_id}: 包含未声明的运行事件 {unknown_events}")

    repair_rounds = []
    for event in trace:
        payload = event_payload(event, "CODER_RESULT")
        if payload is None or (match := REPAIR_ROUND.match(payload)) is None:
            continue
        repair_rounds.append(int(match.group(1)))
    if any(round_number > 3 for round_number in repair_rounds):
        errors.append(f"{case_id}: 不得超过三轮普通修复")
    if "RUN_PAUSED:REPAIR_BUDGET" in trace and (
        not repair_rounds or max(repair_rounds) != 3
    ):
        errors.append(f"{case_id}: REPAIR_BUDGET 必须在第三轮修复后")
    if case["domain_state"].get("repair_budget_used") is False and repair_rounds:
        errors.append(f"{case_id}: 声明未消耗预算但存在修复结果")
    state = case["domain_state"]
    if (
        state.get("target_drift")
        and state.get("review_inputs_unchanged")
        and state.get("review_rerun") is not False
    ):
        errors.append(f"{case_id}: 目标漂移不得使未变 Candidate Review 失效")
    if state.get("seal_confirmed") and state.get("post_seal_drift"):
        if state.get("acceptance_rerun") is not False:
            errors.append(f"{case_id}: Seal 后漂移不得重跑 Acceptance")

    terminal = case["terminal_state"]
    if terminal == "COMPLETED":
        acceptance_passes = [
            event
            for event in trace
            if (
                (payload := event_payload(event, "ACCEPTANCE_RESULT")) is not None
                and ACCEPTANCE_PASS.fullmatch(payload)
            )
        ]
        if not acceptance_passes:
            errors.append(f"{case_id}: COMPLETED 必须包含 ACCEPTANCE_RESULT PASS")
        if "initiative_acceptance" in case["domain_state"] and not any(
            "INITIATIVE_PASS" in event for event in acceptance_passes
        ):
            errors.append(f"{case_id}: 多 Spec COMPLETED 必须包含 Initiative Acceptance PASS")
        integration_count = event_names.count("INTEGRATION_RESULT")
        if integration_count == 0:
            errors.append(f"{case_id}: COMPLETED 必须包含 INTEGRATION_RESULT")
        dual_pass_count = sum(
            (payload := event_payload(event, "REVIEW_RESULT")) is not None
            and REVIEW_PASS.fullmatch(payload) is not None
            for event in trace
        )
        if dual_pass_count < integration_count:
            errors.append(f"{case_id}: 每个 Integration Result 前必须有一个合并后的双轴 PASS")
        expected_tickets = case["domain_state"].get("tickets_complete")
        if isinstance(expected_tickets, int) and integration_count != expected_tickets:
            errors.append(
                f"{case_id}: 声明完成 {expected_tickets} 张 Ticket，"
                f"但只有 {integration_count} 个 Integration Result"
            )
        if case["domain_state"].get("shared_final_commit"):
            last_integration = max(
                index for index, name in enumerate(event_names)
                if name == "INTEGRATION_RESULT"
            )
            first_acceptance = min(
                index for index, name in enumerate(event_names)
                if name == "ACCEPTANCE_RESULT"
            )
            if first_acceptance <= last_integration:
                errors.append(f"{case_id}: 多 Spec Acceptance 必须在所有 Ticket 集成后开始")
            spec_acceptances = [
                event for event in trace
                if event.startswith("ACCEPTANCE_RESULT:SPEC_PASS")
            ]
            if not spec_acceptances or not all("_FINAL" in event for event in spec_acceptances):
                errors.append(f"{case_id}: 所有 Spec Acceptance 必须绑定同一最终 Commit")
        if case["domain_state"].get("delayed_member_closure"):
            if final.get("member_specs_open") is not False:
                errors.append(f"{case_id}: Initiative PASS 后成员 Specs 必须关闭")
            if final.get("closure_order") != ["member_specs", "initiative"]:
                errors.append(f"{case_id}: 必须先关闭成员 Specs，最后关闭 Initiative")
        if "ticket_claim_active" in final or "root_claim_active" in final:
            if final.get("ticket_claim_active") is not False:
                errors.append(f"{case_id}: Local 完成后 Ticket Claim 必须失效")
            if final.get("root_claim_active") is not False:
                errors.append(f"{case_id}: Local 完成后 root Claim 必须失效")
        if final.get("root_open") is not False:
            errors.append(f"{case_id}: COMPLETED 后根 Item 必须关闭")
        if final.get("claim_active") is not False:
            errors.append(f"{case_id}: COMPLETED 后 Claim 必须失效")
    elif terminal == "CANCELLED":
        if "RUN_CANCELLED" not in trace:
            errors.append(f"{case_id}: CANCELLED 必须包含 RUN_CANCELLED")
        if final.get("claim_active") is not False:
            errors.append(f"{case_id}: CANCELLED 后 Claim 必须失效")
        if final.get("root_open") is not True:
            errors.append(f"{case_id}: CANCELLED 不得关闭根 Item")
    elif terminal in {"PAUSED", "CONTRACT_BLOCKER"}:
        if final.get("root_open") is not True:
            errors.append(f"{case_id}: {terminal} 必须保持根 Item Open")
        if case["domain_state"].get("member_specs_open") and final.get("member_specs_open") is not True:
            errors.append(f"{case_id}: Initiative 暂停时成员 Specs 必须保持 Open")
    elif terminal == "FAILED_PRECONDITION" and "RUN_CLAIMED" in trace:
        errors.append(f"{case_id}: FAILED_PRECONDITION 不得发布 Claim")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()
    errors: list[str] = []
    for path in args.paths:
        errors.extend(f"{path}: {error}" for error in validate(path))
    if errors:
        print("\n".join(f"错误：{error}" for error in errors), file=sys.stderr)
        return 1
    print(f"Fixture 校验通过：{len(args.paths)} 个矩阵文件")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
