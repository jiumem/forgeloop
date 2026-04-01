#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
import math
import pathlib
import re
import shutil
import subprocess
import tempfile
from dataclasses import asdict, dataclass


ROOT = pathlib.Path(__file__).resolve().parents[3]
ANCHOR_SCRIPT = ROOT / "plugins/forgeloop/scripts/anchor_slices.py"
CUTOVER_CONTRACT = ROOT / "plugins/forgeloop/skills/run-initiative/references/runtime-cutover.md"
TOTAL_REDUCTION_FLOOR = 45.0
TASK_HOT_PATH_TARGET = 50.0
SCHEMA_VERSION = 2
VALID_SCOPES = {"runtime", "planning"}
VALID_GATING = {"gating", "report_only"}
VALID_BUCKETS = {"hot_path", "cold_path"}
VALID_PRECONDITION_TYPES = {"command_failure", "derived_view_content", "slice_contains"}
VALID_RUNTIME_CUTOVER_MODES = {"full_doc_default", "minimal_preferred", "minimal_required"}


@dataclass
class TextStats:
    chars: int
    lines: int
    words: int
    approx_tokens: int


def read_text(path: pathlib.Path) -> str:
    return path.read_text()


def write_text(path: pathlib.Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def stats_for_text(text: str) -> TextStats:
    chars = len(text)
    lines = text.count("\n") + (0 if not text else 1)
    words = len(text.split())
    approx_tokens = math.ceil(chars / 4) if chars else 0
    return TextStats(chars=chars, lines=lines, words=words, approx_tokens=approx_tokens)


def pct_reduction(legacy: int, minimal: int) -> float:
    if legacy == 0:
        return 0.0
    return ((legacy - minimal) / legacy) * 100


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "scenario"


def resolve_input_path(value: str) -> pathlib.Path:
    path = pathlib.Path(value)
    if path.is_absolute():
        return path
    return ROOT / path


def extract_contract_value(text: str, field: str) -> str:
    match = re.search(rf"^{re.escape(field)}:\s*(\S+)\s*$", text, re.MULTILINE)
    if not match:
        raise ValueError(f"runtime cutover contract is missing {field}")
    return match.group(1)


def load_runtime_cutover() -> dict[str, str]:
    text = read_text(CUTOVER_CONTRACT)
    scope = extract_contract_value(text, "runtime_cutover_scope")
    planning_scope = extract_contract_value(text, "planning_cutover_scope")
    supported_modes = extract_contract_value(text, "supported_runtime_cutover_modes").split(",")
    current_mode = extract_contract_value(text, "current_runtime_cutover_mode")
    if current_mode not in VALID_RUNTIME_CUTOVER_MODES:
        raise ValueError(f"unsupported runtime cutover mode {current_mode!r}")
    if sorted(supported_modes) != sorted(VALID_RUNTIME_CUTOVER_MODES):
        raise ValueError(
            "runtime cutover contract supported modes drifted from benchmark expectations"
        )
    return {
        "contract_path": str(CUTOVER_CONTRACT.relative_to(ROOT)),
        "runtime_scope": scope,
        "planning_scope": planning_scope,
        "current_mode": current_mode,
    }


def materialize_slice(doc: str, anchor: str) -> str:
    proc = subprocess.run(
        ["python3", str(ANCHOR_SCRIPT), "slice", "--doc", doc, "--anchor", anchor],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return proc.stdout


def materialize_derived(doc: str, view: str, cache_root: pathlib.Path) -> str:
    doc_path = ROOT / doc
    cache_key = hashlib.sha1(doc.encode("utf-8")).hexdigest()[:12]
    derived_root = cache_root / f"{doc_path.stem}-{cache_key}"
    if not derived_root.exists():
        subprocess.run(
            ["python3", str(ANCHOR_SCRIPT), "derive", "--doc", doc, "--out", str(derived_root)],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    return read_text(derived_root / view)


def item_label(item: dict[str, str]) -> str:
    item_type = item["type"]
    if item_type == "full_doc":
        return item["path"]
    if item_type == "slice":
        return f'{item["doc"]}#{item["anchor"]}'
    if item_type == "derived_view":
        return f'{item["doc"]}::{item["view"]}'
    raise ValueError(f"unsupported item type: {item_type}")


def item_text(item: dict[str, str], cache_root: pathlib.Path) -> str:
    item_type = item["type"]
    if item_type == "full_doc":
        return read_text(ROOT / item["path"])
    if item_type == "slice":
        return materialize_slice(item["doc"], item["anchor"])
    if item_type == "derived_view":
        return materialize_derived(item["doc"], item["view"], cache_root)
    raise ValueError(f"unsupported item type: {item_type}")


def validate_scenario(scenario: dict[str, object]) -> None:
    required = {
        "name",
        "scope",
        "gating",
        "bucket",
        "description",
        "legacy_packet",
        "minimal_packet",
        "fallback_points",
    }
    missing = sorted(field for field in required if field not in scenario)
    if missing:
        raise ValueError(f"{scenario.get('name', '<unnamed scenario>')}: missing required field(s): {', '.join(missing)}")
    scope = scenario["scope"]
    gating = scenario["gating"]
    bucket = scenario["bucket"]
    if scope not in VALID_SCOPES:
        raise ValueError(f"{scenario['name']}: unsupported scope {scope!r}")
    if gating not in VALID_GATING:
        raise ValueError(f"{scenario['name']}: unsupported gating {gating!r}")
    if bucket not in VALID_BUCKETS:
        raise ValueError(f"{scenario['name']}: unsupported bucket {bucket!r}")
    if scope == "runtime" and gating != "gating":
        raise ValueError(f"{scenario['name']}: runtime scenarios must currently use gating=gating")
    if scope == "planning" and gating != "report_only":
        raise ValueError(f"{scenario['name']}: planning scenarios must currently use gating=report_only")
    for field in ("legacy_packet", "minimal_packet", "fallback_points"):
        value = scenario[field]
        if not isinstance(value, list) or not value:
            raise ValueError(f"{scenario['name']}: {field} must be a non-empty list")
    if "preconditions" in scenario:
        if not isinstance(scenario["preconditions"], list) or not scenario["preconditions"]:
            raise ValueError(f"{scenario['name']}: preconditions must be a non-empty list when present")
        for precondition in scenario["preconditions"]:
            validate_precondition(scenario["name"], precondition)


def validate_precondition(scenario_name: str, precondition: dict[str, object]) -> None:
    precondition_type = precondition.get("type")
    if precondition_type not in VALID_PRECONDITION_TYPES:
        raise ValueError(f"{scenario_name}: unsupported precondition type {precondition_type!r}")
    if "label" not in precondition:
        raise ValueError(f"{scenario_name}: every precondition must provide a label")
    if precondition_type == "command_failure":
        if not isinstance(precondition.get("command"), list) or not precondition["command"]:
            raise ValueError(f"{scenario_name}: command_failure precondition must provide a non-empty command list")
    if precondition_type == "derived_view_content":
        for field in ("doc", "view"):
            if field not in precondition:
                raise ValueError(f"{scenario_name}: derived_view_content precondition missing {field}")
    if precondition_type == "slice_contains":
        for field in ("doc", "anchor"):
            if field not in precondition:
                raise ValueError(f"{scenario_name}: slice_contains precondition missing {field}")


def render_item_header(item: dict[str, str], label: str) -> list[str]:
    lines = [f"type: {item['type']}", f"ref: {label}"]
    if item["type"] == "full_doc":
        lines.append("selector_mode: full_document")
        lines.append(f"doc_ref: {item['path']}")
    elif item["type"] == "slice":
        lines.append("selector_mode: anchor")
        lines.append(f"doc_ref: {item['doc']}")
        lines.append(f"anchor_selector: {item['anchor']}")
    elif item["type"] == "derived_view":
        lines.append("selector_mode: derived_view")
        lines.append(f"doc_ref: {item['doc']}")
        lines.append(f"derived_view: {item['view']}")
    return lines


def render_packet_text(
    scenario: dict[str, object],
    variant: str,
    items: list[dict[str, str]],
    labels: list[str],
    materialized_texts: list[str],
    fallback_points: list[str],
    runtime_cutover: dict[str, str],
) -> str:
    lines = [
        "# Dispatch Packet",
        "",
        "## Packet Metadata",
        f"name: {scenario['name']}",
        f"scope: {scenario['scope']}",
        f"gating: {scenario['gating']}",
        f"bucket: {scenario['bucket']}",
        f"variant: {variant}",
        f"task_hot_path: {str(bool(scenario.get('task_hot_path', False))).lower()}",
        "proof_target: packet-shape + read-surface shrink",
        "token_method: ceil(chars / 4)",
    ]
    if scenario["scope"] == "runtime":
        lines.extend(
            [
                f"runtime_cutover_contract: {runtime_cutover['contract_path']}",
                f"runtime_cutover_scope: {runtime_cutover['runtime_scope']}",
                f"planning_cutover_scope: {runtime_cutover['planning_scope']}",
                f"current_runtime_cutover_mode: {runtime_cutover['current_mode']}",
            ]
        )
    lines.extend(
        [
            "",
            "## Scenario Description",
            str(scenario["description"]).strip(),
            "",
            "## Read Surface",
        ]
    )
    for index, (item, label) in enumerate(zip(items, labels, strict=True), start=1):
        lines.append(f"- item {index}: {item['type']} -> {label}")
    lines.extend(["", "## Fallback Points"])
    for point in fallback_points:
        lines.append(f"- {point}")
    for index, (item, label, materialized_text) in enumerate(
        zip(items, labels, materialized_texts, strict=True),
        start=1,
    ):
        lines.extend(
            [
                "",
                f"## Item {index}",
                *render_item_header(item, label),
                "materialization_state: included_in_packet",
                "",
                "<<<BEGIN_CONTENT>>>",
                materialized_text.rstrip(),
                "<<<END_CONTENT>>>",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def materialize_packet(
    scenario: dict[str, object],
    variant: str,
    items: list[dict[str, str]],
    cache_root: pathlib.Path,
    fallback_points: list[str],
    runtime_cutover: dict[str, str],
) -> tuple[str, TextStats, list[str]]:
    labels = [item_label(item) for item in items]
    materialized_texts = [item_text(item, cache_root).strip() for item in items]
    packet_text = render_packet_text(
        scenario,
        variant,
        items,
        labels,
        materialized_texts,
        fallback_points,
        runtime_cutover,
    )
    return packet_text, stats_for_text(packet_text), labels


def run_precondition(precondition: dict[str, object], cache_root: pathlib.Path) -> dict[str, object]:
    precondition_type = str(precondition["type"])
    result = {
        "label": precondition["label"],
        "type": precondition_type,
        "passed": False,
    }
    if precondition_type == "command_failure":
        proc = subprocess.run(
            list(precondition["command"]),
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        expected_exit = int(precondition.get("expect_exit", 1))
        stdout = proc.stdout.strip()
        stderr = proc.stderr.strip()
        checks: list[bool] = [proc.returncode == expected_exit]
        if "stderr_contains" in precondition:
            checks.append(str(precondition["stderr_contains"]) in stderr)
        if "stdout_contains" in precondition:
            checks.append(str(precondition["stdout_contains"]) in stdout)
        result.update(
            {
                "passed": all(checks),
                "returncode": proc.returncode,
                "expected_exit": expected_exit,
                "stdout_excerpt": stdout[:200],
                "stderr_excerpt": stderr[:200],
            }
        )
        return result
    if precondition_type == "derived_view_content":
        text = materialize_derived(str(precondition["doc"]), str(precondition["view"]), cache_root)
    elif precondition_type == "slice_contains":
        text = materialize_slice(str(precondition["doc"]), str(precondition["anchor"]))
    else:
        raise ValueError(f"unsupported precondition type: {precondition_type}")
    include_checks = [needle in text for needle in precondition.get("include", [])]
    exclude_checks = [needle not in text for needle in precondition.get("exclude", [])]
    result.update(
        {
            "passed": all(include_checks) and all(exclude_checks),
            "include": list(precondition.get("include", [])),
            "exclude": list(precondition.get("exclude", [])),
        }
    )
    return result


def scenario_key(scenario_name: str, scope: str) -> str:
    return f"{scope}::{scenario_name}"


def render_stat_block(label: str, stat: TextStats) -> str:
    return (
        f"{label}: {stat.approx_tokens} tok approx | {stat.chars} chars | "
        f"{stat.lines} lines | {stat.words} words"
    )


def serialize_report(
    runtime_cutover: dict[str, str],
    scenario_results: list[dict[str, object]],
    aggregates: dict[str, object],
    runtime_gate: dict[str, object],
    compare_baseline: dict[str, object] | None,
) -> dict[str, object]:
    return {
        "schema_version": SCHEMA_VERSION,
        "runtime_cutover": runtime_cutover,
        "method": {
            "proof_target": "packet-shape + read-surface shrink",
            "approx_token_formula": "ceil(chars / 4)",
            "provider_tokenizer": "not_connected",
            "telemetry": "not_connected",
        },
        "thresholds": {
            "runtime_total_reduction_floor_pct": TOTAL_REDUCTION_FLOOR,
            "runtime_task_hot_path_target_pct": TASK_HOT_PATH_TARGET,
        },
        "scenarios": scenario_results,
        "aggregates": aggregates,
        "runtime_gate": runtime_gate,
        "baseline_compare": compare_baseline,
    }


def build_scope_aggregate(results: list[dict[str, object]], scope: str) -> dict[str, object]:
    scoped = [result for result in results if result["scope"] == scope]
    bucket_totals: dict[str, dict[str, int]] = {
        "hot_path": {"legacy": 0, "minimal": 0},
        "cold_path": {"legacy": 0, "minimal": 0},
    }
    task_hot_reductions: list[float] = []
    for result in scoped:
        bucket = str(result["bucket"])
        bucket_totals[bucket]["legacy"] += int(result["legacy"]["stats"]["approx_tokens"])
        bucket_totals[bucket]["minimal"] += int(result["minimal"]["stats"]["approx_tokens"])
        if result.get("task_hot_path"):
            task_hot_reductions.append(float(result["reduction_pct"]))
    hot = bucket_totals["hot_path"]
    cold = bucket_totals["cold_path"]
    total_legacy = hot["legacy"] + cold["legacy"]
    total_minimal = hot["minimal"] + cold["minimal"]
    aggregate = {
        "scenario_count": len(scoped),
        "hot_path": {
            "legacy_approx_tokens": hot["legacy"],
            "minimal_approx_tokens": hot["minimal"],
            "reduction_pct": pct_reduction(hot["legacy"], hot["minimal"]),
        },
        "cold_path": {
            "legacy_approx_tokens": cold["legacy"],
            "minimal_approx_tokens": cold["minimal"],
            "reduction_pct": pct_reduction(cold["legacy"], cold["minimal"]),
        },
        "total": {
            "legacy_approx_tokens": total_legacy,
            "minimal_approx_tokens": total_minimal,
            "reduction_pct": pct_reduction(total_legacy, total_minimal),
        },
    }
    if scope == "runtime":
        aggregate["task_hot_path_average_reduction_pct"] = (
            sum(task_hot_reductions) / len(task_hot_reductions) if task_hot_reductions else 0.0
        )
    return aggregate


def compare_reports(current: dict[str, object], baseline: dict[str, object]) -> dict[str, object]:
    current_scenarios = {
        scenario_key(item["name"], item["scope"]): item for item in current["scenarios"]
    }
    baseline_scenarios = {
        scenario_key(item["name"], item["scope"]): item for item in baseline["scenarios"]
    }
    scenario_diffs: list[dict[str, object]] = []
    for key in sorted(set(current_scenarios) | set(baseline_scenarios)):
        current_item = current_scenarios.get(key)
        baseline_item = baseline_scenarios.get(key)
        if current_item and not baseline_item:
            scenario_diffs.append(
                {
                    "key": key,
                    "name": current_item["name"],
                    "scope": current_item["scope"],
                    "status": "added",
                }
            )
            continue
        if baseline_item and not current_item:
            scenario_diffs.append(
                {
                    "key": key,
                    "name": baseline_item["name"],
                    "scope": baseline_item["scope"],
                    "status": "removed",
                }
            )
            continue
        assert current_item is not None and baseline_item is not None
        scenario_diffs.append(
            {
                "key": key,
                "name": current_item["name"],
                "scope": current_item["scope"],
                "status": "matched",
                "legacy_approx_tokens_delta": (
                    current_item["legacy"]["stats"]["approx_tokens"]
                    - baseline_item["legacy"]["stats"]["approx_tokens"]
                ),
                "minimal_approx_tokens_delta": (
                    current_item["minimal"]["stats"]["approx_tokens"]
                    - baseline_item["minimal"]["stats"]["approx_tokens"]
                ),
                "reduction_pct_delta": round(
                    float(current_item["reduction_pct"]) - float(baseline_item["reduction_pct"]),
                    1,
                ),
            }
        )

    aggregate_diffs: dict[str, object] = {}
    for scope in sorted(set(current["aggregates"]) | set(baseline["aggregates"])):
        current_scope = current["aggregates"].get(scope)
        baseline_scope = baseline["aggregates"].get(scope)
        if current_scope is None or baseline_scope is None:
            aggregate_diffs[scope] = {"status": "scope_added_or_removed"}
            continue
        aggregate_diff = {
            "hot_path_reduction_pct_delta": round(
                float(current_scope["hot_path"]["reduction_pct"]) - float(baseline_scope["hot_path"]["reduction_pct"]),
                1,
            ),
            "cold_path_reduction_pct_delta": round(
                float(current_scope["cold_path"]["reduction_pct"]) - float(baseline_scope["cold_path"]["reduction_pct"]),
                1,
            ),
            "total_reduction_pct_delta": round(
                float(current_scope["total"]["reduction_pct"]) - float(baseline_scope["total"]["reduction_pct"]),
                1,
            ),
        }
        if scope == "runtime":
            aggregate_diff["task_hot_path_average_reduction_pct_delta"] = round(
                float(current_scope["task_hot_path_average_reduction_pct"])
                - float(baseline_scope["task_hot_path_average_reduction_pct"]),
                1,
            )
        aggregate_diffs[scope] = aggregate_diff

    failures: list[str] = []
    current_cutover = current.get("runtime_cutover", {})
    baseline_cutover = baseline.get("runtime_cutover", {})
    if current_cutover != baseline_cutover:
        failures.append(
            "runtime cutover drift detected: "
            f"current={current_cutover.get('current_mode')} baseline={baseline_cutover.get('current_mode')}"
        )
    for item in scenario_diffs:
        if item["status"] != "matched":
            failures.append(f"scenario set drift detected for {item['key']}: {item['status']}")
            continue
        if (
            item["legacy_approx_tokens_delta"] != 0
            or item["minimal_approx_tokens_delta"] != 0
            or item["reduction_pct_delta"] != 0.0
        ):
            failures.append(
                f"scenario drift detected for {item['key']}: "
                f"legacy {item['legacy_approx_tokens_delta']:+d}, "
                f"minimal {item['minimal_approx_tokens_delta']:+d}, "
                f"reduction {item['reduction_pct_delta']:+.1f} pts"
            )
    for scope, aggregate_diff in aggregate_diffs.items():
        if aggregate_diff.get("status"):
            failures.append(f"aggregate scope drift detected for {scope}: {aggregate_diff['status']}")
            continue
        for key, value in aggregate_diff.items():
            if value != 0.0:
                failures.append(f"aggregate drift detected for {scope}.{key}: {value:+.1f}")
    return {"scenario_diffs": scenario_diffs, "aggregate_diffs": aggregate_diffs, "failures": failures}


def render_scope_scenarios(
    lines: list[str],
    title: str,
    results: list[dict[str, object]],
) -> None:
    lines.extend([f"## {title}", ""])
    for result in results:
        lines.extend(
            [
                f"### {result['name']}",
                "",
                f"- Bucket: `{result['bucket']}`",
                f"- Scope: `{result['scope']}`",
                f"- Gating: `{result['gating']}`",
                f"- Description: {result['description']}",
                f"- {render_stat_block('Legacy packet', TextStats(**result['legacy']['stats']))}",
                f"- {render_stat_block('Minimal packet', TextStats(**result['minimal']['stats']))}",
                f"- Reduction: {float(result['reduction_pct']):.1f}%",
                f"- Legacy docs read set: {', '.join(result['legacy']['read_set'])}",
                f"- Minimal docs read set: {', '.join(result['minimal']['read_set'])}",
                f"- Fallback points: {', '.join(result['fallback_points'])}",
            ]
        )
        if result["legacy"].get("packet_path"):
            lines.append(f"- Legacy packet dump: {result['legacy']['packet_path']}")
        if result["minimal"].get("packet_path"):
            lines.append(f"- Minimal packet dump: {result['minimal']['packet_path']}")
        if result.get("preconditions"):
            passed = sum(1 for item in result["preconditions"] if item["passed"])
            lines.append(f"- Executable preconditions: {passed}/{len(result['preconditions'])} passed")
            for item in result["preconditions"]:
                lines.append(
                    f"-   [{ 'pass' if item['passed'] else 'fail' }] {item['label']}"
                )
        lines.append("")


def render_scope_aggregate(lines: list[str], title: str, aggregate: dict[str, object], report_only: bool) -> None:
    lines.extend(
        [
            f"## {title}",
            "",
            f"- Hot path reduction: {aggregate['hot_path']['reduction_pct']:.1f}% "
            f"({aggregate['hot_path']['legacy_approx_tokens']} -> {aggregate['hot_path']['minimal_approx_tokens']} tok approx)",
            f"- Cold path reduction: {aggregate['cold_path']['reduction_pct']:.1f}% "
            f"({aggregate['cold_path']['legacy_approx_tokens']} -> {aggregate['cold_path']['minimal_approx_tokens']} tok approx)",
            f"- Total reduction: {aggregate['total']['reduction_pct']:.1f}% "
            f"({aggregate['total']['legacy_approx_tokens']} -> {aggregate['total']['minimal_approx_tokens']} tok approx)",
        ]
    )
    if "task_hot_path_average_reduction_pct" in aggregate:
        lines.append(f"- Task hot path average reduction: {aggregate['task_hot_path_average_reduction_pct']:.1f}%")
    lines.append(f"- Gate mode: {'report-only' if report_only else 'gating'}")
    lines.append("")


def render_compare_section(lines: list[str], compare: dict[str, object]) -> None:
    lines.extend(["## Baseline Compare", ""])
    for scope, aggregate_diff in compare["aggregate_diffs"].items():
        lines.append(f"### {scope.capitalize()} Aggregate Delta")
        lines.append("")
        if aggregate_diff.get("status"):
            lines.append(f"- Status: {aggregate_diff['status']}")
            lines.append("")
            continue
        lines.append(f"- Hot path reduction delta: {aggregate_diff['hot_path_reduction_pct_delta']:+.1f} pts")
        lines.append(f"- Cold path reduction delta: {aggregate_diff['cold_path_reduction_pct_delta']:+.1f} pts")
        lines.append(f"- Total reduction delta: {aggregate_diff['total_reduction_pct_delta']:+.1f} pts")
        if "task_hot_path_average_reduction_pct_delta" in aggregate_diff:
            lines.append(
                f"- Task hot path average delta: {aggregate_diff['task_hot_path_average_reduction_pct_delta']:+.1f} pts"
            )
        lines.append("")
    lines.append(f"- Drift status: {'fail' if compare['failures'] else 'pass'}")
    if compare["failures"]:
        for failure in compare["failures"]:
            lines.append(f"- {failure}")
        lines.append("")

    lines.extend(["### Scenario Delta", "", "| Scenario | Scope | Status | Legacy Delta | Minimal Delta | Reduction Delta |", "| --- | --- | --- | ---: | ---: | ---: |"])
    for item in compare["scenario_diffs"]:
        if item["status"] != "matched":
            lines.append(f"| {item['name']} | {item['scope']} | {item['status']} | n/a | n/a | n/a |")
            continue
        lines.append(
            f"| {item['name']} | {item['scope']} | matched | "
            f"{item['legacy_approx_tokens_delta']:+d} | {item['minimal_approx_tokens_delta']:+d} | "
            f"{item['reduction_pct_delta']:+.1f} pts |"
        )
    lines.append("")


def render_markdown(report: dict[str, object]) -> str:
    lines = ["# Forgeloop Token Benchmark", ""]
    runtime_cutover = report["runtime_cutover"]
    lines.extend(
        [
            "## Runtime Cutover",
            "",
            f"- Contract: `{runtime_cutover['contract_path']}`",
            f"- Runtime scope: `{runtime_cutover['runtime_scope']}`",
            f"- Planning scope: `{runtime_cutover['planning_scope']}`",
            f"- Current mode: `{runtime_cutover['current_mode']}`",
            "",
        ]
    )
    runtime_results = [item for item in report["scenarios"] if item["scope"] == "runtime"]
    planning_results = [item for item in report["scenarios"] if item["scope"] == "planning"]
    render_scope_scenarios(lines, "Runtime Scenarios", runtime_results)
    render_scope_aggregate(
        lines,
        "Runtime Aggregate",
        report["aggregates"]["runtime"],
        report_only=report["runtime_gate"]["mode"] != "gating",
    )
    if planning_results:
        render_scope_scenarios(lines, "Planning Report-Only Scenarios", planning_results)
        render_scope_aggregate(lines, "Planning Aggregate", report["aggregates"]["planning"], report_only=True)

    gate = report["runtime_gate"]
    lines.extend(["## Runtime Gate", ""])
    if gate["failures"]:
        lines.append("- Status: fail")
        for failure in gate["failures"]:
            lines.append(f"- {failure}")
    else:
        lines.append("- Status: pass")
        if gate["mode"] == "gating":
            lines.append(
                f"- Enforced thresholds: total >= {TOTAL_REDUCTION_FLOOR:.1f}%, task hot path >= {TASK_HOT_PATH_TARGET:.1f}%"
            )
        else:
            lines.append("- Thresholds are report-only in the current runtime cutover mode.")
    lines.append("")

    if report.get("baseline_compare"):
        render_compare_section(lines, report["baseline_compare"])

    return "\n".join(lines).rstrip() + "\n"


def render_baseline_markdown(report: dict[str, object]) -> str:
    lines = [
        "# Forgeloop Token Benchmark Baseline",
        "",
        "Generated from:",
        "",
        "```bash",
        "bash tests/codex/token-benchmark/run.sh \\",
        "  --json-out tests/codex/token-benchmark/baseline.json \\",
        "  --markdown-out tests/codex/token-benchmark/baseline.md",
        "```",
        "",
        "Method:",
        "",
        "- legacy packet = representative full-document packet for the scenario",
        "- minimal packet = representative minimal dispatch packet after anchor slices / derived views / legal fallback are fully materialized as text",
        "- selected fallback scenarios also carry executable preconditions that must prove the triggering failure before fallback packet comparison",
        "- packet size proves `packet-shape + read-surface shrink`, not provider token counts",
        "- approx tokens = `ceil(characters / 4)`",
        f"- runtime cutover mode = `{report['runtime_cutover']['current_mode']}`",
        "",
    ]
    runtime = report["aggregates"]["runtime"]
    planning = report["aggregates"]["planning"]
    render_scope_aggregate(
        lines,
        "Runtime Aggregate",
        runtime,
        report_only=report["runtime_gate"]["mode"] != "gating",
    )
    render_scope_aggregate(lines, "Planning Aggregate", planning, report_only=True)
    lines.extend(["## Scenario Baseline", "", "| Scenario | Scope | Gating | Bucket | Legacy | Minimal | Reduction |", "| --- | --- | --- | --- | ---: | ---: | ---: |"])
    for item in report["scenarios"]:
        lines.append(
            f"| {item['name']} | {item['scope']} | {item['gating']} | {item['bucket']} | "
            f"{item['legacy']['stats']['approx_tokens']} | {item['minimal']['stats']['approx_tokens']} | "
            f"{float(item['reduction_pct']):.1f}% |"
        )
    lines.extend(
        [
            "",
            "## Notes",
            "",
            f"- Runtime cutover mode is `{report['runtime_cutover']['current_mode']}`.",
            "- Runtime gate remains `total >= 45%` and `task hot path >= 50%` only while runtime cutover mode stays in a minimal-first state.",
            "- Planning scenarios are tracked in a separate report-only block and do not currently gate the run.",
            "- Packet dumps, when requested, expose the exact compared text for each scenario so the baseline remains auditable.",
            "- Full-document fallback remains explicit in the packet text; it is measured, not hidden.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Approximate packet benchmark for Forgeloop dispatch packets."
    )
    parser.add_argument("--fixtures", required=True)
    parser.add_argument("--dump-packets")
    parser.add_argument("--json-out")
    parser.add_argument("--markdown-out")
    parser.add_argument("--compare-baseline")
    args = parser.parse_args()

    scenarios = json.loads(resolve_input_path(args.fixtures).read_text())
    if not isinstance(scenarios, list):
        raise SystemExit("fixtures must decode to a scenario list")
    for scenario in scenarios:
        validate_scenario(scenario)
    runtime_cutover = load_runtime_cutover()

    tmpdir = pathlib.Path(tempfile.mkdtemp(prefix="forgeloop-token-benchmark-"))
    dump_root = pathlib.Path(args.dump_packets).resolve() if args.dump_packets else None
    if dump_root is not None:
        dump_root.mkdir(parents=True, exist_ok=True)

    try:
        scenario_results: list[dict[str, object]] = []
        for scenario in scenarios:
            fallback_points = list(scenario["fallback_points"])
            legacy_fallback = list(scenario.get("legacy_fallback_points", []))
            minimal_fallback = list(scenario.get("minimal_fallback_points", fallback_points))
            legacy_text, legacy_stats, legacy_labels = materialize_packet(
                scenario,
                "legacy",
                scenario["legacy_packet"],
                tmpdir,
                legacy_fallback,
                runtime_cutover,
            )
            minimal_text, minimal_stats, minimal_labels = materialize_packet(
                scenario,
                "minimal",
                scenario["minimal_packet"],
                tmpdir,
                minimal_fallback,
                runtime_cutover,
            )
            reduction = pct_reduction(legacy_stats.approx_tokens, minimal_stats.approx_tokens)

            result: dict[str, object] = {
                "name": scenario["name"],
                "scope": scenario["scope"],
                "gating": scenario["gating"],
                "bucket": scenario["bucket"],
                "task_hot_path": bool(scenario.get("task_hot_path", False)),
                "description": scenario["description"],
                "fallback_points": fallback_points,
                "legacy": {
                    "read_set": legacy_labels,
                    "stats": asdict(legacy_stats),
                },
                "minimal": {
                    "read_set": minimal_labels,
                    "stats": asdict(minimal_stats),
                },
                "reduction_pct": round(reduction, 1),
            }
            if scenario.get("preconditions"):
                probes = [run_precondition(precondition, tmpdir) for precondition in scenario["preconditions"]]
                result["preconditions"] = probes

            if dump_root is not None:
                scenario_dir = dump_root / f"{scenario['scope']}-{slugify(scenario['name'])}"
                scenario_dir.mkdir(parents=True, exist_ok=True)
                legacy_path = scenario_dir / "legacy.packet.txt"
                minimal_path = scenario_dir / "minimal.packet.txt"
                write_text(legacy_path, legacy_text)
                write_text(minimal_path, minimal_text)
                result["legacy"]["packet_path"] = str(legacy_path)
                result["minimal"]["packet_path"] = str(minimal_path)

            scenario_results.append(result)

        aggregates = {
            "runtime": build_scope_aggregate(scenario_results, "runtime"),
            "planning": build_scope_aggregate(scenario_results, "planning"),
        }
        contract_failures: list[str] = []
        for result in scenario_results:
            for precondition in result.get("preconditions", []):
                if not precondition["passed"]:
                    contract_failures.append(
                        f"{result['scope']}::{result['name']} precondition failed: {precondition['label']}"
                    )
        runtime_failures: list[str] = []
        runtime_total = float(aggregates["runtime"]["total"]["reduction_pct"])
        runtime_task_hot = float(aggregates["runtime"]["task_hot_path_average_reduction_pct"])
        runtime_gate_mode = (
            "report_only"
            if runtime_cutover["current_mode"] == "full_doc_default"
            else "gating"
        )
        if runtime_gate_mode == "gating":
            if runtime_total < TOTAL_REDUCTION_FLOOR:
                runtime_failures.append(
                    f"total reduction {runtime_total:.1f}% fell below the required {TOTAL_REDUCTION_FLOOR:.1f}% floor"
                )
            if runtime_task_hot < TASK_HOT_PATH_TARGET:
                runtime_failures.append(
                    f"task hot path average reduction {runtime_task_hot:.1f}% fell below the {TASK_HOT_PATH_TARGET:.1f}% target"
                )
        runtime_gate = {
            "scope": "runtime",
            "gating": runtime_gate_mode,
            "mode": runtime_gate_mode,
            "failures": runtime_failures,
        }

        report = serialize_report(runtime_cutover, scenario_results, aggregates, runtime_gate, compare_baseline=None)
        baseline_failures: list[str] = []
        if args.compare_baseline:
            baseline = json.loads(resolve_input_path(args.compare_baseline).read_text())
            report["baseline_compare"] = compare_reports(report, baseline)
            baseline_failures = list(report["baseline_compare"]["failures"])

        markdown = render_markdown(report)
        print(markdown, end="")

        if args.json_out:
            write_text(pathlib.Path(args.json_out).resolve(), json.dumps(report, indent=2) + "\n")
        if args.markdown_out:
            write_text(pathlib.Path(args.markdown_out).resolve(), render_baseline_markdown(report))

        return 1 if runtime_failures or baseline_failures or contract_failures else 0
    finally:
        shutil.rmtree(tmpdir)


if __name__ == "__main__":
    raise SystemExit(main())
