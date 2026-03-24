from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .models import InitiativePlan, MilestonePlan, PRPlan, RequirementSummary, TaskPlan, WorkstreamPlan
from .utils import path_from_ref, read_text


MACHINE_BLOCK_PATTERN = re.compile(
    r"```initiative-plan\s*(?P<body>\{.*?\})\s*```",
    re.DOTALL,
)


def extract_machine_block(markdown: str) -> dict[str, Any]:
    match = MACHINE_BLOCK_PATTERN.search(markdown)
    if not match:
        raise ValueError("initiative-plan fenced block not found")
    body = match.group("body")
    try:
        return json.loads(body)
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON inside initiative-plan block: {exc}") from exc


def _require_non_empty(mapping: dict[str, Any], key: str, errors: list[str], context: str) -> Any:
    value = mapping.get(key)
    if value is None or value == "" or value == []:
        errors.append(f"{context}: missing or empty field `{key}`")
    return value


def validate_plan_dict(plan_dict: dict[str, Any], repo_root: Path) -> list[str]:
    errors: list[str] = []
    initiative = plan_dict.get("initiative")
    if not isinstance(initiative, dict):
        return ["top-level `initiative` object is required"]

    for key in [
        "key",
        "title",
        "requirement_summary",
        "design_refs",
        "sealed_decisions",
        "execution_boundary",
        "initiative_reference_assignment",
        "background",
        "scope",
        "non_goals",
        "success_criteria",
    ]:
        _require_non_empty(initiative, key, errors, "initiative")

    requirement_summary = initiative.get("requirement_summary", {})
    if not isinstance(requirement_summary, dict):
        errors.append("initiative.requirement_summary must be an object")
    else:
        _require_non_empty(requirement_summary, "problem", errors, "initiative.requirement_summary")
        _require_non_empty(requirement_summary, "goal", errors, "initiative.requirement_summary")

    milestones = plan_dict.get("milestones", [])
    workstreams = plan_dict.get("workstreams", [])
    tasks = plan_dict.get("tasks", [])
    if not milestones:
        errors.append("at least one milestone is required")
    if not workstreams:
        errors.append("at least one workstream is required")
    if not tasks:
        errors.append("at least one task is required")

    milestone_keys: set[str] = set()
    workstream_keys: set[str] = set()
    task_keys: set[str] = set()

    for idx, item in enumerate(milestones):
        context = f"milestones[{idx}]"
        if not isinstance(item, dict):
            errors.append(f"{context}: must be an object")
            continue
        for key in ["key", "goal", "acceptance", "reference_assignment"]:
            _require_non_empty(item, key, errors, context)
        key = item.get("key")
        if key in milestone_keys:
            errors.append(f"{context}: duplicate milestone key `{key}`")
        if key:
            milestone_keys.add(key)

    for idx, item in enumerate(workstreams):
        context = f"workstreams[{idx}]"
        if not isinstance(item, dict):
            errors.append(f"{context}: must be an object")
            continue
        for key in ["key", "responsibility", "recommended_executor"]:
            _require_non_empty(item, key, errors, context)
        key = item.get("key")
        if key in workstream_keys:
            errors.append(f"{context}: duplicate workstream key `{key}`")
        if key:
            workstream_keys.add(key)

    for idx, item in enumerate(tasks):
        context = f"tasks[{idx}]"
        if not isinstance(item, dict):
            errors.append(f"{context}: must be an object")
            continue
        for key in ["key", "milestone", "workstream", "summary", "action", "output", "acceptance"]:
            _require_non_empty(item, key, errors, context)
        key = item.get("key")
        if key in task_keys:
            errors.append(f"{context}: duplicate task key `{key}`")
        if key:
            task_keys.add(key)

    for idx, item in enumerate(tasks):
        context = f"tasks[{idx}]"
        if not isinstance(item, dict):
            continue
        milestone = item.get("milestone")
        workstream = item.get("workstream")
        if milestone and milestone not in milestone_keys:
            errors.append(f"{context}: unknown milestone `{milestone}`")
        if workstream and workstream not in workstream_keys:
            errors.append(f"{context}: unknown workstream `{workstream}`")
        for dep in item.get("dependencies", []) or []:
            if dep not in task_keys:
                errors.append(f"{context}: unknown task dependency `{dep}`")

    for category in [
        ("initiative.design_refs", initiative.get("design_refs", []) or []),
        ("initiative.gap_refs", initiative.get("gap_refs", []) or []),
        ("initiative.initiative_reference_assignment", [initiative.get("initiative_reference_assignment", "")]),
    ]:
        label, refs = category
        for ref in refs:
            ref_path = path_from_ref(ref, repo_root)
            if ref_path and not ref_path.exists():
                errors.append(f"{label}: missing referenced file `{ref_path}`")

    for idx, item in enumerate(milestones):
        if not isinstance(item, dict):
            continue
        ref = item.get("reference_assignment", "")
        ref_path = path_from_ref(ref, repo_root)
        if ref and ref_path and not ref_path.exists():
            errors.append(f"milestones[{idx}].reference_assignment: missing referenced file `{ref_path}`")

    for idx, item in enumerate(tasks):
        if not isinstance(item, dict):
            continue
        for ref_group in ["design_refs", "gap_refs", "spec_refs"]:
            for ref in item.get(ref_group, []) or []:
                ref_path = path_from_ref(ref, repo_root)
                if ref_path and not ref_path.exists():
                    errors.append(f"tasks[{idx}].{ref_group}: missing referenced file `{ref_path}`")

    return errors


def parse_initiative_doc(path: str | Path) -> InitiativePlan:
    path = Path(path)
    markdown = read_text(path)
    plan_dict = extract_machine_block(markdown)
    errors = validate_plan_dict(plan_dict, path.parent.parent.parent.resolve())
    if errors:
        raise ValueError("planning preflight failed:\n- " + "\n- ".join(errors))

    initiative = plan_dict["initiative"]
    milestones = {
        item["key"]: MilestonePlan(
            key=item["key"],
            goal=item["goal"],
            depends_on=list(item.get("depends_on", []) or []),
            planned_pr_model=item.get("planned_pr_model", "Single PR"),
            acceptance=list(item.get("acceptance", []) or []),
            reference_assignment=item["reference_assignment"],
        )
        for item in plan_dict.get("milestones", [])
    }
    workstreams = {
        item["key"]: WorkstreamPlan(
            key=item["key"],
            responsibility=item["responsibility"],
            parallelizable=bool(item.get("parallelizable", True)),
            depends_on=list(item.get("depends_on", []) or []),
            recommended_executor=item.get("recommended_executor", "Shared"),
        )
        for item in plan_dict.get("workstreams", [])
    }
    tasks = {
        item["key"]: TaskPlan(
            key=item["key"],
            milestone=item["milestone"],
            workstream=item["workstream"],
            summary=item["summary"],
            design_refs=list(item.get("design_refs", []) or []),
            gap_refs=list(item.get("gap_refs", []) or []),
            spec_refs=list(item.get("spec_refs", []) or []),
            input=item.get("input", ""),
            action=item.get("action", ""),
            output=item.get("output", ""),
            non_goals=list(item.get("non_goals", []) or []),
            dependencies=list(item.get("dependencies", []) or []),
            acceptance=list(item.get("acceptance", []) or []),
            local_risks=list(item.get("local_risks", []) or []),
            recommended_executor=item.get("recommended_executor", "Shared"),
            execution_mode=item.get("execution_mode", "write"),
            g1_commands=list(item.get("g1_commands", []) or []),
        )
        for item in plan_dict.get("tasks", [])
    }
    pr_plan = [
        PRPlan(
            key=item["key"],
            milestone=item["milestone"],
            covers=list(item.get("covers", []) or []),
            goal=item.get("goal", ""),
            depends_on=list(item.get("depends_on", []) or []),
            acceptance_checklist=list(item.get("acceptance_checklist", []) or []),
        )
        for item in plan_dict.get("pr_plan", [])
    ]

    return InitiativePlan(
        key=initiative["key"],
        title=initiative["title"],
        requirement_summary=RequirementSummary(
            problem=initiative["requirement_summary"]["problem"],
            goal=initiative["requirement_summary"]["goal"],
        ),
        design_refs=list(initiative.get("design_refs", []) or []),
        gap_refs=list(initiative.get("gap_refs", []) or []),
        sealed_decisions=list(initiative.get("sealed_decisions", []) or []),
        execution_boundary=initiative["execution_boundary"],
        initiative_reference_assignment=initiative["initiative_reference_assignment"],
        background=initiative["background"],
        scope=list(initiative.get("scope", []) or []),
        non_goals=list(initiative.get("non_goals", []) or []),
        success_criteria=list(initiative.get("success_criteria", []) or []),
        milestones=milestones,
        workstreams=workstreams,
        tasks=tasks,
        pr_plan=pr_plan,
        global_residual_risks=list(plan_dict.get("global_residual_risks", []) or []),
        follow_ups=list(plan_dict.get("follow_ups", []) or []),
        g3_commands=list(plan_dict.get("g3_commands", []) or []),
    )
