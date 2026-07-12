#!/usr/bin/env python3
"""校验 Fixture 字段、三 Tracker 等价性与 run-initiative 状态轨迹不变量。"""

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


def event_payload(event: str, event_name: str) -> str | None:
    prefix = f"{event_name}:"
    return event[len(prefix):] if event.startswith(prefix) else None


def validate(path: Path) -> list[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    runtime = data.get("kind") == "run-initiative-runtime"
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
