from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .models import InitiativePlan, InitiativeRuntimeState, MilestoneStatus, TaskStatus


@dataclass
class ReadyTaskSelection:
    write_tasks: list[str]
    readonly_tasks: list[str]


def select_frontier(plan: InitiativePlan, state: InitiativeRuntimeState) -> str | None:
    for milestone_key in plan.milestones.keys():
        milestone_state = state.milestone_states[milestone_key].state
        if milestone_state in {
            MilestoneStatus.READY,
            MilestoneStatus.ACTIVE,
            MilestoneStatus.READY_FOR_PR,
            MilestoneStatus.BLOCKED,
            MilestoneStatus.IN_R2,
        }:
            return milestone_key
    return None


def select_ready_tasks(
    plan: InitiativePlan,
    state: InitiativeRuntimeState,
    frontier: str | None,
    max_write_tasks: int = 1,
) -> ReadyTaskSelection:
    if not frontier:
        return ReadyTaskSelection(write_tasks=[], readonly_tasks=[])

    write_tasks: list[str] = []
    readonly_tasks: list[str] = []
    for task_key, task in plan.tasks.items():
        if task.milestone != frontier:
            continue
        runtime_state = state.task_states[task_key].state
        if runtime_state != TaskStatus.READY:
            continue
        if task.execution_mode == "read-only":
            readonly_tasks.append(task_key)
        elif len(write_tasks) < max_write_tasks:
            write_tasks.append(task_key)
    return ReadyTaskSelection(write_tasks=write_tasks, readonly_tasks=readonly_tasks)


def milestone_is_sealable(plan: InitiativePlan, state: InitiativeRuntimeState, milestone_key: str) -> bool:
    task_keys = [task_key for task_key, task in plan.tasks.items() if task.milestone == milestone_key]
    return bool(task_keys) and all(state.task_states[key].state == TaskStatus.DONE for key in task_keys)


def initiative_is_deliverable(plan: InitiativePlan, state: InitiativeRuntimeState) -> bool:
    if not plan.milestones:
        return False
    return all(runtime.state in {MilestoneStatus.READY_FOR_PR, MilestoneStatus.MERGED} for runtime in state.milestone_states.values())
