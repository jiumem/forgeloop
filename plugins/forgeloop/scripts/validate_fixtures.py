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
    cumulative_audit = data.get("kind") == "cumulative-audit"
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
        if cumulative_audit:
            errors.extend(validate_cumulative_audit_case(case))
    for group, group_cases in groups.items():
        if len(group_cases) == 1:
            continue
        trackers = {case["tracker"] for case in group_cases}
        expected_trackers = {"github", "gitlab"} if cumulative_audit else TRACKERS
        if trackers != expected_trackers:
            errors.append(f"{group}: Tracker 覆盖不完整 {sorted(trackers)}")
            continue
        states = {json.dumps(case["domain_state"], sort_keys=True, ensure_ascii=False) for case in group_cases}
        terminals = {case["terminal_state"] for case in group_cases}
        if len(states) != 1 or len(terminals) != 1:
            errors.append(f"{group}: 三 Tracker 领域终态不等价")
    if runtime and "evidence_cases" in data:
        errors.extend(validate_evidence_cases(data["evidence_cases"], ids, cases))
    return errors


CUMULATIVE_PROJECTION_FIELDS = {
    "Spec",
    "Delivery range",
    "Target",
    "Tickets",
    "Commit mapping",
    "Review",
    "Invariants",
    "Checks",
    "Limitations",
}
CUMULATIVE_MERGE_LIFECYCLE = [
    "DELIVERY_HEAD",
    "PR_IDENTITY",
    "REQUIRED_CHECKS",
    "PROJECTION_REFRESH",
    "LITERAL_WRITE",
    "EXACT_READBACK",
    "MERGE",
    "SPEC_ACCEPTANCE",
]
CUMULATIVE_HUMAN_READY_LIFECYCLE = [
    *CUMULATIVE_MERGE_LIFECYCLE[:-2],
    "READY_FOR_HUMAN_MERGE",
]
SHARED_REASONS = {
    "WIDE_REFACTOR",
    "NON_GREEN_MIGRATION",
    "ATOMIC_DELIVERY",
    "CUMULATIVE_AUDIT",
}


def validate_cumulative_audit_case(case: dict) -> list[str]:
    """校验共享交付门禁，以及累计审计的附加约束。"""

    errors: list[str] = []
    case_id = case["id"]
    state = case["domain_state"]
    selected = state.get("cumulative_selected") is True
    if case["tracker"] == "local" and (selected or state.get("native_pr_claimed")):
        errors.append(f"{case_id}: Local 不得提供或伪造累计 PR/MR")
    if state.get("topology") == "SHARED":
        blocked_reason = state.get("blocked_reason")
        if state.get("reason") not in SHARED_REASONS:
            errors.append(f"{case_id}: SHARED topology 必须声明一个已批准 reason")
        if state.get("integration_policy") not in {"auto-merge", "human-merge"}:
            errors.append(f"{case_id}: SHARED reason 不得替代 Integration Policy")
        if state.get("approved") is not True:
            errors.append(f"{case_id}: SHARED 声明必须随完整草案获得用户批准")
        if blocked_reason == "LEGACY_DECLARATION":
            if state.get("tracker_writes") != 0:
                errors.append(f"{case_id}: 旧声明必须以零 Tracker writes 拒绝")
        else:
            if state.get("gate_owner") != "SPEC_ROOT":
                errors.append(f"{case_id}: SHARED Spec 必须声明 SPEC_ROOT Final Integration Gate")
            if state.get("ceremony_ticket_count", 0) != 0:
                errors.append(f"{case_id}: 不得创建 ceremony-only final Ticket")

        gate_active = any(
            state.get(field) is True
            for field in ("gate_started", "ready_for_human_merge", "merge_attempted")
        )
        if gate_active:
            if state.get("ordinary_tickets_closed") != state.get("implementation_tickets"):
                errors.append(f"{case_id}: 普通 Ticket 全部关闭前不得进入 Final Integration Gate")
            if state.get("ticket_integration_results") != state.get("implementation_tickets"):
                errors.append(f"{case_id}: Ticket Integration Result 不完整时不得进入 Final Integration Gate")

        if blocked_reason == "FINAL_GATE_FINDING":
            required = ("finding_id", "evidence_ref", "owning_scope")
            for field in required:
                if not isinstance(state.get(field), str) or not state[field]:
                    errors.append(f"{case_id}: Final Gate Finding 缺失 {field}")
            if state.get("run_paused") is not True:
                errors.append(f"{case_id}: Final Gate Finding 必须发布 RUN_PAUSED")
            finding_id = state.get("finding_id")
            expected_key = (
                f"final-gate:{state.get('spec_ref')}:{state.get('spec_revision')}:{finding_id}"
            )
            if state.get("repair_key") != expected_key:
                errors.append(f"{case_id}: Final Gate Finding 的 repair_key 不稳定")
            if state.get("scheduler_created_ticket") is not False:
                errors.append(f"{case_id}: Scheduler 不得为 Final Gate Finding 创建 Ticket")

        implementation_ticket = state.get("final_implementation_ticket")
        if implementation_ticket is not None:
            required = {
                "ordinary", "implementation_scope", "parent_da_refs", "acceptance_criteria",
                "owned_csi", "risk_classification",
            }
            if not isinstance(implementation_ticket, dict) or required - set(implementation_ticket):
                errors.append(f"{case_id}: 最终实现工作必须是结构完整的普通 Ticket")
            else:
                if implementation_ticket.get("ordinary") is not True:
                    errors.append(f"{case_id}: 最终实现工作不得成为特殊 Ticket 类型")
                if not isinstance(implementation_ticket.get("implementation_scope"), str) or not implementation_ticket["implementation_scope"]:
                    errors.append(f"{case_id}: 最终实现 Ticket 必须有真实 Scope")
                if (
                    not isinstance(implementation_ticket.get("parent_da_refs"), list)
                    or not implementation_ticket["parent_da_refs"]
                    or not all(isinstance(ref, str) and ref for ref in implementation_ticket["parent_da_refs"])
                ):
                    errors.append(f"{case_id}: 最终实现 Ticket 必须引用 Parent Delivery Acceptance")
                if (
                    not isinstance(implementation_ticket.get("acceptance_criteria"), list)
                    or not implementation_ticket["acceptance_criteria"]
                    or not all(isinstance(criterion, str) and criterion for criterion in implementation_ticket["acceptance_criteria"])
                ):
                    errors.append(f"{case_id}: 最终实现 Ticket 必须有可验证 Acceptance criteria")
                if implementation_ticket.get("risk_classification") not in {"STANDARD", "HIGH_RISK"}:
                    errors.append(f"{case_id}: 最终实现 Ticket 风险分类无效")
                owned_csi = implementation_ticket.get("owned_csi")
                if not (
                    (isinstance(owned_csi, str) and owned_csi)
                    or (
                        isinstance(owned_csi, list) and owned_csi
                        and all(isinstance(csi, str) and csi for csi in owned_csi)
                    )
                ):
                    errors.append(f"{case_id}: 最终实现 Ticket 必须声明适用的 CSI ownership")

        if blocked_reason == "UNATTRIBUTED_COMMIT":
            if not state.get("unattributed_commits") or state.get("delivery_range_valid") is not False:
                errors.append(f"{case_id}: 额外 Commit Finding 必须绑定未归属 Commit 与无效范围")
            if state.get("merge_attempted") is not False:
                errors.append(f"{case_id}: 存在未归属 Commit 时不得合并")
        if blocked_reason == "MISSING_APPROVED_COMMIT":
            if not state.get("missing_ticket_commits") or state.get("delivery_range_valid") is not False:
                errors.append(f"{case_id}: 缺失 Commit Finding 必须绑定 Ticket 与无效范围")
            if state.get("merge_attempted") is not False:
                errors.append(f"{case_id}: 缺失已批准 Commit 时不得合并")
        if blocked_reason == "MISSING_TICKET_DELIVERY":
            if not isinstance(state.get("ticket_integration_results"), int) or state["ticket_integration_results"] >= state.get("implementation_tickets", 0):
                errors.append(f"{case_id}: 缺失交付证据必须对应不完整 Ticket Integration Result")
            if state.get("gate_started") is not False or state.get("merge_attempted") is not False:
                errors.append(f"{case_id}: Gate 前置条件缺失时不得启动 Gate 或合并")
        if state.get("repair_ticket_reused"):
            if state.get("explicit_to_tickets") is not True or state.get("matching_unfinished_tickets") != 1:
                errors.append(f"{case_id}: repair Ticket 仅可在显式调用且唯一未完成匹配时复用")
            if not isinstance(state.get("repair_key"), str) or not state["repair_key"]:
                errors.append(f"{case_id}: repair Ticket 复用必须绑定 repair_key")
        if (
            state.get("explicit_to_tickets") is True
            and state.get("matching_unfinished_tickets") == 1
            and state.get("repair_ticket_reused") is not True
        ):
            errors.append(f"{case_id}: 唯一匹配的未完成 repair Ticket 必须复用")
        affected_scopes = state.get("affected_scopes")
        if isinstance(affected_scopes, int) and affected_scopes > 1:
            if state.get("repair_ticket_count") != affected_scopes:
                errors.append(f"{case_id}: 多 Scope Finding 必须分别路由普通 repair Ticket")
            if state.get("miscellaneous_ticket") is not False:
                errors.append(f"{case_id}: 多 Scope Finding 不得创建杂项 Ticket")
        if state.get("target_drift") and state.get("target_refreshed") is not True:
            errors.append(f"{case_id}: target drift 后必须刷新当前目标事实")
        if state.get("target_refreshed"):
            if state.get("delivery_head_unchanged") is not True or state.get("pr_identities") != 1:
                errors.append(f"{case_id}: target drift 必须保持 delivery Head 与原 PR/MR identity")
            if state.get("repair_budget_used") is not False:
                errors.append(f"{case_id}: target drift 刷新不得消耗 Repair Budget")
        if blocked_reason == "PROJECTION_DRIFT":
            if state.get("projection_matches_native") is not False or state.get("exact_readback") is not False:
                errors.append(f"{case_id}: 投影漂移必须由原生不一致与回读失败证明")
            if state.get("merge_attempted") is not False:
                errors.append(f"{case_id}: 投影漂移时不得合并")
    if not selected:
        return errors
    if state.get("topology") != "SHARED" or state.get("reason") != "CUMULATIVE_AUDIT":
        errors.append(f"{case_id}: 累计审计必须是 SHARED topology reason")
    if state.get("integration_policy") not in {"auto-merge", "human-merge"}:
        errors.append(f"{case_id}: 累计审计不得成为 Integration Policy")
    if state.get("native_pr_runtime") is not True:
        errors.append(f"{case_id}: CUMULATIVE_AUDIT 需要原生 PR/MR runtime")
    if not isinstance(state.get("implementation_tickets"), int) or state["implementation_tickets"] < 2:
        errors.append(f"{case_id}: CUMULATIVE_AUDIT 需要至少两张实现 Ticket")
    if state.get("approved") is not True:
        errors.append(f"{case_id}: CUMULATIVE_AUDIT 需要用户批准完整草案")

    blocked_reason = state.get("blocked_reason")
    member_specs = state.get("member_specs", 1)
    if member_specs == 1 and state.get("pr_identities", 0) > 1:
        errors.append(f"{case_id}: 单 Spec 最多一个累计 PR/MR identity")
    if member_specs > 1:
        if state.get("cross_spec_prs") != 0:
            errors.append(f"{case_id}: 不得创建跨 Spec 累计 PR/MR")
        if state.get("per_spec_pr_identities") != [1] * member_specs:
            errors.append(f"{case_id}: 每个适用成员 Spec 必须独立拥有一个 PR/MR")

    if state.get("ready_for_human_merge"):
        if state.get("pr_identities") != member_specs:
            errors.append(f"{case_id}: human-merge 必须绑定每个 Spec 唯一 PR/MR identity")
        if state.get("lifecycle") != CUMULATIVE_HUMAN_READY_LIFECYCLE:
            errors.append(f"{case_id}: human-merge 准备时序不完整")
        for field in (
            "gate_validation_pass", "delivery_head_unchanged", "delivery_range_valid",
            "required_checks_pass",
            "protection_pass", "permissions_pass", "projection_matches_native",
            "exact_readback",
        ):
            if state.get(field) is not True:
                errors.append(f"{case_id}: READY_FOR_HUMAN_MERGE 缺失门槛 {field}")
        if state.get("ordinary_tickets_closed") != state.get("implementation_tickets"):
            errors.append(f"{case_id}: 普通 Ticket 完成前不得进入 human-merge")
        if state.get("ticket_integration_results") != state.get("implementation_tickets"):
            errors.append(f"{case_id}: Ticket Integration Result 不完整时不得进入 human-merge")
    if state.get("merge_attempted"):
        if state.get("pr_identities") != member_specs:
            errors.append(f"{case_id}: 合并必须绑定每个 Spec 唯一 PR/MR identity")
        if state.get("lifecycle") != CUMULATIVE_MERGE_LIFECYCLE:
            errors.append(f"{case_id}: 累计 PR/MR 生命周期顺序不完整")
        fields = set(state.get("projection_fields", []))
        missing = CUMULATIVE_PROJECTION_FIELDS - fields
        if missing:
            errors.append(f"{case_id}: 累计审计字段不完整 {sorted(missing)}")
        if state.get("projection_matches_native") is not True:
            errors.append(f"{case_id}: 审计投影与原生事实不一致时不得合并")
        if state.get("exact_readback") is not True:
            errors.append(f"{case_id}: 合并前必须完成正文精确回读")
        if state.get("required_checks_pass") is not True:
            errors.append(f"{case_id}: 合并前 Required Checks 必须通过")
        if state.get("gate_validation_pass") is not True:
            errors.append(f"{case_id}: 合并前必须完成 Final Integration Gate 验证")
        if state.get("delivery_range_valid") is not True:
            errors.append(f"{case_id}: 合并前完整 delivery range 必须有效")
        if state.get("delivery_head_unchanged") is not True:
            errors.append(f"{case_id}: 合并前 delivery_head 必须保持固定")
        if state.get("protection_pass") is not True or state.get("permissions_pass") is not True:
            errors.append(f"{case_id}: 合并前保护规则与权限必须通过")
        if state.get("ordinary_tickets_closed") != state.get("implementation_tickets"):
            errors.append(f"{case_id}: 普通 Ticket 完成前不得最终合并")
        if state.get("ticket_integration_results") != state.get("implementation_tickets"):
            errors.append(f"{case_id}: Ticket Integration Result 不完整时不得最终合并")
    if case["terminal_state"] == "COMPLETED":
        if state.get("merge_attempted") is not True:
            errors.append(f"{case_id}: COMPLETED 必须先完成累计 PR/MR 合并")
        if state.get("fresh_spec_acceptance") is not True:
            errors.append(f"{case_id}: 累计合并后必须通过 fresh Spec Acceptance 才能完成")
        integration_results = state.get("spec_integration_results")
        required = {
            "subject_ref", "result", "spec_delivery_base", "delivery_head",
            "target_before", "target_after", "integration_method", "native_ref",
            "evidence_refs",
        }
        if not isinstance(integration_results, list) or len(integration_results) != member_specs:
            errors.append(f"{case_id}: 每个 Spec 必须有一个结构化 Spec Integration Result")
        else:
            for result in integration_results:
                if not isinstance(result, dict) or required - set(result):
                    errors.append(f"{case_id}: Spec Integration Result 字段不完整")
                    continue
                if not str(result.get("subject_ref", "")).startswith("spec:"):
                    errors.append(f"{case_id}: Spec Integration Result 必须以 Spec 为 subject_ref")
                scalar_fields = required - {"evidence_refs"}
                if not all(isinstance(result.get(field), str) and result[field] for field in scalar_fields):
                    errors.append(f"{case_id}: Spec Integration Result 标量字段必须非空")
                if (
                    not isinstance(result.get("evidence_refs"), list)
                    or not result["evidence_refs"]
                    or not all(isinstance(ref, str) and ref for ref in result["evidence_refs"])
                ):
                    errors.append(f"{case_id}: Spec Integration Result 必须绑定最终证据")
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
        integration_payloads = [
            payload
            for event in trace
            if (payload := event_payload(event, "INTEGRATION_RESULT")) is not None
        ]
        integration_count = len(integration_payloads)
        if integration_count == 0:
            errors.append(f"{case_id}: COMPLETED 必须包含 INTEGRATION_RESULT")
        integration_results = case["domain_state"].get("integration_results")
        if integration_results is None:
            ticket_integration_count = integration_count
        elif not isinstance(integration_results, list) or len(integration_results) != integration_count:
            errors.append(f"{case_id}: 结构化 Integration Results 必须与事件数量一致")
            ticket_integration_count = 0
        else:
            invalid_results = [
                result for result in integration_results
                if not isinstance(result, dict)
                or not isinstance(result.get("subject_ref"), str)
                or not result["subject_ref"]
                or not isinstance(result.get("result"), str)
                or not result["result"]
            ]
            if invalid_results:
                errors.append(f"{case_id}: Integration Result 必须结构化绑定 subject_ref 与 result")
            ticket_integration_count = sum(
                isinstance(result, dict)
                and result.get("subject_ref", "").startswith("ticket:")
                for result in integration_results
            )
        dual_pass_count = sum(
            (payload := event_payload(event, "REVIEW_RESULT")) is not None
            and REVIEW_PASS.fullmatch(payload) is not None
            for event in trace
        )
        if dual_pass_count < ticket_integration_count:
            errors.append(f"{case_id}: 每个 Integration Result 前必须有一个合并后的双轴 PASS")
        expected_tickets = case["domain_state"].get("tickets_complete")
        if isinstance(expected_tickets, int) and ticket_integration_count != expected_tickets:
            errors.append(
                f"{case_id}: 声明完成 {expected_tickets} 张 Ticket，"
                f"但只有 {ticket_integration_count} 个 Ticket Integration Result"
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
