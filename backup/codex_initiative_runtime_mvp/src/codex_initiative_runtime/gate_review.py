from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import GateCommandResult, GateResult, InitiativePlan, ReviewReport
from .review_packet import build_review_bundle
from .state_store import fact_path, report_path
from .utils import find_repo_root, read_json, run_command, write_json, write_text


def run_gate_commands(profile: str, object_key: str, commands: list[str], repo_root: str | Path | None = None) -> GateResult:
    repo_root = find_repo_root(repo_root)
    command_results: list[GateCommandResult] = []
    passed = True
    for command in commands:
        return_code, stdout, stderr = run_command(command, repo_root)
        command_results.append(
            GateCommandResult(
                command=command,
                return_code=return_code,
                stdout=stdout,
                stderr=stderr,
            )
        )
        if return_code != 0:
            passed = False
    summary = "all commands passed" if passed else "at least one command failed"
    return GateResult(profile=profile, object_key=object_key, passed=passed, commands=command_results, summary=summary)


def commands_for_task(plan: InitiativePlan, task_key: str) -> list[str]:
    task = plan.tasks[task_key]
    return task.g1_commands or ["python -m unittest -q"]


def commands_for_milestone(plan: InitiativePlan, milestone_key: str) -> list[str]:
    commands: list[str] = []
    for task in plan.tasks.values():
        if task.milestone == milestone_key:
            commands.extend(task.g1_commands)
    return commands or ["python -m unittest -q"]


def commands_for_initiative(plan: InitiativePlan) -> list[str]:
    return plan.g3_commands or ["python -m unittest -q"]


def persist_gate_result(
    initiative_key: str,
    result: GateResult,
    *,
    repo_root: str | Path | None = None,
) -> Path:
    path = report_path(initiative_key, f"{result.profile.lower()}-{result.object_key}.json", repo_root)
    write_json(path, result.to_dict())
    return path


def prepare_review_bundle_for_task(plan: InitiativePlan, task_key: str, initiative_key: str, repo_root: str | Path | None = None) -> Path:
    task = plan.tasks[task_key]
    evidence = [
        str(report_path(initiative_key, f"g1-{task_key}.json", repo_root)),
    ]
    bundle = build_review_bundle("R1", task_key, task.design_refs + task.gap_refs + task.spec_refs, evidence, repo_root)
    path = report_path(initiative_key, f"r1-{task_key}-bundle.json", repo_root)
    write_json(path, bundle)
    return path


def prepare_review_bundle_for_milestone(plan: InitiativePlan, milestone_key: str, initiative_key: str, repo_root: str | Path | None = None) -> Path:
    milestone = plan.milestones[milestone_key]
    evidence = [
        str(report_path(initiative_key, f"g2-{milestone_key}.json", repo_root)),
    ]
    bundle = build_review_bundle("R2", milestone_key, [milestone.reference_assignment], evidence, repo_root)
    path = report_path(initiative_key, f"r2-{milestone_key}-bundle.json", repo_root)
    write_json(path, bundle)
    return path


def prepare_review_bundle_for_initiative(plan: InitiativePlan, initiative_key: str, repo_root: str | Path | None = None) -> Path:
    evidence = [
        str(report_path(initiative_key, f"g3-{initiative_key}.json", repo_root)),
    ]
    refs = [plan.initiative_reference_assignment] + plan.design_refs + plan.gap_refs
    bundle = build_review_bundle("R3", initiative_key, refs, evidence, repo_root)
    path = report_path(initiative_key, f"r3-{initiative_key}-bundle.json", repo_root)
    write_json(path, bundle)
    return path


def finalize_review_report(
    initiative_key: str,
    profile: str,
    object_key: str,
    raw_input_path: str | Path,
    *,
    repo_root: str | Path | None = None,
) -> tuple[Path, Path]:
    data = read_json(raw_input_path)
    required = ["verdict", "summary", "findings", "residual_risks", "escalations", "evidence"]
    missing = [key for key in required if key not in data]
    if missing:
        raise ValueError(f"review report missing fields: {', '.join(missing)}")
    report = ReviewReport(
        profile=profile,
        object_key=object_key,
        verdict=data["verdict"],
        summary=data["summary"],
        findings=list(data.get("findings", []) or []),
        residual_risks=list(data.get("residual_risks", []) or []),
        escalations=list(data.get("escalations", []) or []),
        evidence=list(data.get("evidence", []) or []),
    )
    json_path = report_path(initiative_key, f"{profile.lower()}-{object_key}.json", repo_root)
    md_path = report_path(initiative_key, f"{profile.lower()}-{object_key}.md", repo_root)
    write_json(json_path, report.to_dict())
    write_text(md_path, render_review_markdown(report))
    return json_path, md_path


def render_review_markdown(report: ReviewReport) -> str:
    lines = [
        f"# {report.profile} Review · {report.object_key}",
        "",
        f"**Verdict**: {report.verdict}",
        "",
        "## Summary",
        report.summary,
        "",
        "## Findings",
    ]
    if report.findings:
        lines.extend([f"- {item}" for item in report.findings])
    else:
        lines.append("- None")
    lines.extend(["", "## Residual Risks"])
    if report.residual_risks:
        lines.extend([f"- {item}" for item in report.residual_risks])
    else:
        lines.append("- None")
    lines.extend(["", "## Escalations"])
    if report.escalations:
        lines.extend([f"- {item}" for item in report.escalations])
    else:
        lines.append("- None")
    lines.extend(["", "## Evidence"])
    if report.evidence:
        lines.extend([f"- {item}" for item in report.evidence])
    else:
        lines.append("- None")
    lines.append("")
    return "\n".join(lines)
