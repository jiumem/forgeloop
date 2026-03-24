from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .models import (
    InitiativePlan,
    InitiativeRuntimeState,
    InitiativeStatus,
    MilestoneRuntimeState,
    MilestoneStatus,
    TaskRuntimeState,
    TaskStatus,
)
from .utils import ensure_gitignore_entry, find_repo_root, read_json, safe_git_log, write_json


ANCHOR_PATTERN = re.compile(r"^(anchor|fixup|revert)\((?P<milestone>[^/]+)/(?P<task>[^)]+)\):\s*(?P<summary>.+)$")


def runtime_root(repo_root: str | Path | None = None) -> Path:
    repo_root = find_repo_root(repo_root)
    root = Path(repo_root) / ".initiative-runtime"
    root.mkdir(parents=True, exist_ok=True)
    ensure_gitignore_entry(repo_root, ".initiative-runtime/")
    gitignore = root / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text("*\n!.gitignore\n", encoding="utf-8")
    return root


def initiative_dir(initiative_key: str, repo_root: str | Path | None = None) -> Path:
    path = runtime_root(repo_root) / initiative_key
    for sub in ["packets", "reports", "facts", "drafts", "observations", "decisions"]:
        (path / sub).mkdir(parents=True, exist_ok=True)
    return path


def state_path(initiative_key: str, repo_root: str | Path | None = None) -> Path:
    return initiative_dir(initiative_key, repo_root) / "state.json"


def report_path(initiative_key: str, name: str, repo_root: str | Path | None = None) -> Path:
    return initiative_dir(initiative_key, repo_root) / "reports" / name


def packet_path(initiative_key: str, name: str, repo_root: str | Path | None = None) -> Path:
    return initiative_dir(initiative_key, repo_root) / "packets" / name


def observation_path(initiative_key: str, name: str, repo_root: str | Path | None = None) -> Path:
    return initiative_dir(initiative_key, repo_root) / "observations" / name


def decision_path(initiative_key: str, name: str, repo_root: str | Path | None = None) -> Path:
    return initiative_dir(initiative_key, repo_root) / "decisions" / name


def fact_path(initiative_key: str, name: str, repo_root: str | Path | None = None) -> Path:
    return initiative_dir(initiative_key, repo_root) / "facts" / name


def save_state(state: InitiativeRuntimeState, repo_root: str | Path | None = None) -> Path:
    return write_json(state_path(state.initiative_key, repo_root), state.to_dict())


def load_state(initiative_key: str, repo_root: str | Path | None = None) -> InitiativeRuntimeState | None:
    path = state_path(initiative_key, repo_root)
    if not path.exists():
        return None
    raw = read_json(path)
    task_states = {
        key: TaskRuntimeState(
            key=value["key"],
            milestone=value["milestone"],
            workstream=value["workstream"],
            state=TaskStatus(value["state"]),
            depends_on=list(value.get("depends_on", []) or []),
            last_anchor_commit=value.get("last_anchor_commit"),
            latest_packet_ref=value.get("latest_packet_ref"),
            latest_observation_ref=value.get("latest_observation_ref"),
            latest_decision_ref=value.get("latest_decision_ref"),
            latest_g1_ref=value.get("latest_g1_ref"),
            latest_r1_ref=value.get("latest_r1_ref"),
            probe_count=int(value.get("probe_count", 0)),
            stall_count=int(value.get("stall_count", 0)),
            blocked_reason=value.get("blocked_reason", ""),
        )
        for key, value in raw.get("task_states", {}).items()
    }
    milestone_states = {
        key: MilestoneRuntimeState(
            key=value["key"],
            state=MilestoneStatus(value["state"]),
            task_keys=list(value.get("task_keys", []) or []),
            latest_pr_ref=value.get("latest_pr_ref"),
            latest_g2_ref=value.get("latest_g2_ref"),
            latest_r2_ref=value.get("latest_r2_ref"),
            blocked_reason=value.get("blocked_reason", ""),
        )
        for key, value in raw.get("milestone_states", {}).items()
    }
    return InitiativeRuntimeState(
        initiative_key=raw["initiative_key"],
        title=raw["title"],
        state=InitiativeStatus(raw["state"]),
        current_frontier=raw.get("current_frontier"),
        task_states=task_states,
        milestone_states=milestone_states,
        latest_g3_ref=raw.get("latest_g3_ref"),
        latest_r3_ref=raw.get("latest_r3_ref"),
        notes=list(raw.get("notes", []) or []),
    )


def scan_git_anchors(repo_root: str | Path | None = None) -> dict[str, dict[str, str]]:
    anchors: dict[str, dict[str, str]] = {}
    for sha, subject in safe_git_log(find_repo_root(repo_root)):
        match = ANCHOR_PATTERN.match(subject)
        if not match:
            continue
        milestone = match.group("milestone").strip().upper()
        task = match.group("task").strip().upper()
        anchors.setdefault(milestone, {})
        anchors[milestone].setdefault(task, sha)
    return anchors


def _task_state_from_reports(task_state: TaskRuntimeState, initiative_key: str, repo_root: str | Path) -> TaskStatus:
    task_key = task_state.key
    reports_dir = initiative_dir(initiative_key, repo_root) / "reports"
    g1 = reports_dir / f"g1-{task_key}.json"
    r1 = reports_dir / f"r1-{task_key}.json"
    if r1.exists():
        task_state.latest_r1_ref = str(r1)
        return TaskStatus.DONE
    if g1.exists():
        task_state.latest_g1_ref = str(g1)
        return TaskStatus.IN_R1
    if task_state.last_anchor_commit:
        return TaskStatus.IN_G1
    return task_state.state


def rebuild_state_from_plan(plan: InitiativePlan, repo_root: str | Path | None = None) -> InitiativeRuntimeState:
    repo_root = find_repo_root(repo_root)
    anchors = scan_git_anchors(repo_root)

    task_states: dict[str, TaskRuntimeState] = {}
    for task_key, task in plan.tasks.items():
        anchor = anchors.get(task.milestone.upper(), {}).get(task.key.upper())
        initial = TaskRuntimeState(
            key=task_key,
            milestone=task.milestone,
            workstream=task.workstream,
            state=TaskStatus.NOT_READY,
            depends_on=list(task.dependencies),
            last_anchor_commit=anchor,
        )
        task_states[task_key] = initial

    changed = True
    while changed:
        changed = False
        for task_key, task in plan.tasks.items():
            runtime = task_states[task_key]
            if runtime.state in {TaskStatus.DONE, TaskStatus.IN_G1, TaskStatus.IN_R1}:
                continue
            if runtime.last_anchor_commit:
                runtime.state = _task_state_from_reports(runtime, plan.key, repo_root)
                continue
            dep_states = [task_states[dep].state for dep in task.dependencies]
            new_state = TaskStatus.READY if all(state == TaskStatus.DONE for state in dep_states) else TaskStatus.NOT_READY
            if not task.dependencies:
                new_state = TaskStatus.READY
            if runtime.state != new_state:
                runtime.state = new_state
                changed = True

    milestone_states: dict[str, MilestoneRuntimeState] = {}
    for milestone_key, milestone in plan.milestones.items():
        keys = [task_key for task_key, task in plan.tasks.items() if task.milestone == milestone_key]
        runtime = MilestoneRuntimeState(key=milestone_key, task_keys=keys)
        milestone_states[milestone_key] = runtime

    for milestone_key, runtime in milestone_states.items():
        milestone = plan.milestones[milestone_key]
        if any(milestone_states[dep].state != MilestoneStatus.MERGED for dep in milestone.depends_on if dep in milestone_states):
            runtime.state = MilestoneStatus.NOT_READY
            continue
        task_states_for_milestone = [task_states[key].state for key in runtime.task_keys]
        if runtime.task_keys and all(state == TaskStatus.DONE for state in task_states_for_milestone):
            runtime.state = MilestoneStatus.READY_FOR_PR
        elif any(state in {TaskStatus.READY, TaskStatus.IN_FLIGHT, TaskStatus.READY_FOR_ANCHOR, TaskStatus.IN_G1, TaskStatus.IN_R1} for state in task_states_for_milestone):
            runtime.state = MilestoneStatus.ACTIVE
        elif all(state == TaskStatus.NOT_READY for state in task_states_for_milestone):
            runtime.state = MilestoneStatus.READY if not milestone.depends_on else MilestoneStatus.NOT_READY
        else:
            runtime.state = MilestoneStatus.READY

    current_frontier = None
    for milestone_key in plan.milestones.keys():
        state = milestone_states[milestone_key].state
        if state in {MilestoneStatus.READY, MilestoneStatus.ACTIVE, MilestoneStatus.READY_FOR_PR, MilestoneStatus.BLOCKED, MilestoneStatus.IN_R2}:
            current_frontier = milestone_key
            break

    initiative_state = InitiativeRuntimeState(
        initiative_key=plan.key,
        title=plan.title,
        state=InitiativeStatus.ACTIVE,
        current_frontier=current_frontier,
        task_states=task_states,
        milestone_states=milestone_states,
    )

    if current_frontier is None:
        if all(runtime.state == MilestoneStatus.MERGED for runtime in milestone_states.values()) and milestone_states:
            initiative_state.state = InitiativeStatus.WAITING_R3
        elif milestone_states:
            initiative_state.state = InitiativeStatus.READY
    return initiative_state
