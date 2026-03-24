from __future__ import annotations

from pathlib import Path
from typing import Any

from .models import InitiativePlan, InitiativeRuntimeState, InitiativeStatus, MilestoneStatus, TaskStatus
from .planning_parser import parse_initiative_doc, validate_plan_dict, extract_machine_block
from .scheduler import initiative_is_deliverable, milestone_is_sealable, select_frontier, select_ready_tasks
from .state_store import rebuild_state_from_plan, save_state
from .utils import find_repo_root, read_text


def planning_preflight(doc_path: str | Path, repo_root: str | Path | None = None) -> dict[str, Any]:
    repo_root = find_repo_root(repo_root)
    markdown = read_text(doc_path)
    plan_dict = extract_machine_block(markdown)
    errors = validate_plan_dict(plan_dict, repo_root)
    return {
        "initiative_doc": str(Path(doc_path)),
        "passed": not errors,
        "errors": errors,
    }


def rebuild_state(doc_path: str | Path, repo_root: str | Path | None = None) -> InitiativeRuntimeState:
    plan = parse_initiative_doc(doc_path)
    state = rebuild_state_from_plan(plan, repo_root)
    save_state(state, repo_root)
    return state


def run_initiative(doc_path: str | Path, repo_root: str | Path | None = None, max_write_tasks: int = 1) -> dict[str, Any]:
    repo_root = find_repo_root(repo_root)
    preflight = planning_preflight(doc_path, repo_root)
    if not preflight["passed"]:
        return {
            "initiative_doc": str(Path(doc_path)),
            "status": InitiativeStatus.PLANNING_BLOCKED.value,
            "errors": preflight["errors"],
        }

    plan = parse_initiative_doc(doc_path)
    state = rebuild_state_from_plan(plan, repo_root)
    frontier = select_frontier(plan, state)
    selection = select_ready_tasks(plan, state, frontier, max_write_tasks=max_write_tasks)
    summary = {
        "initiative": {
            "key": plan.key,
            "title": plan.title,
            "state": state.state.value,
            "frontier": frontier,
        },
        "ready": {
            "write_tasks": selection.write_tasks,
            "readonly_tasks": selection.readonly_tasks,
        },
        "milestones": {key: runtime.state.value for key, runtime in state.milestone_states.items()},
        "tasks": {key: runtime.state.value for key, runtime in state.task_states.items()},
        "next_breakpoint": _next_breakpoint(plan, state, frontier),
    }
    save_state(state, repo_root)
    return summary


def _next_breakpoint(plan: InitiativePlan, state: InitiativeRuntimeState, frontier: str | None) -> str:
    if frontier and milestone_is_sealable(plan, state, frontier):
        return f"Milestone {frontier} ready for PR / G2 / R2"
    if initiative_is_deliverable(plan, state):
        return f"Initiative {plan.key} ready for G3 / R3"
    if frontier:
        return f"Continue Milestone {frontier}"
    return "No active frontier"
