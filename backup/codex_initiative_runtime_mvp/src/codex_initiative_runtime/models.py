from __future__ import annotations

from dataclasses import dataclass, field, asdict, is_dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Optional


class StrEnum(str, Enum):
    def __str__(self) -> str:
        return self.value


class InitiativeStatus(StrEnum):
    PLANNING_BLOCKED = "PLANNING_BLOCKED"
    READY = "READY"
    ACTIVE = "ACTIVE"
    WAITING_R2 = "WAITING_R2"
    WAITING_ESCALATION = "WAITING_ESCALATION"
    WAITING_R3 = "WAITING_R3"
    DONE = "DONE"
    ABORTED = "ABORTED"


class MilestoneStatus(StrEnum):
    NOT_READY = "NOT_READY"
    READY = "READY"
    ACTIVE = "ACTIVE"
    READY_FOR_PR = "READY_FOR_PR"
    IN_R2 = "IN_R2"
    MERGED = "MERGED"
    BLOCKED = "BLOCKED"


class TaskStatus(StrEnum):
    NOT_READY = "NOT_READY"
    READY = "READY"
    IN_FLIGHT = "IN_FLIGHT"
    READY_FOR_ANCHOR = "READY_FOR_ANCHOR"
    IN_G1 = "IN_G1"
    IN_R1 = "IN_R1"
    DONE = "DONE"
    BLOCKED = "BLOCKED"
    DEFERRED = "DEFERRED"


class Trend(StrEnum):
    INITIAL = "INITIAL"
    CONVERGING = "CONVERGING"
    CONVERGING_WITH_DEBT = "CONVERGING_WITH_DEBT"
    STALLED = "STALLED"
    DIVERGING = "DIVERGING"
    OSCILLATING = "OSCILLATING"
    CONVERGED_AND_STABLE = "CONVERGED_AND_STABLE"


class DecisionAction(StrEnum):
    REQUEST_RUNTIME_FACTS = "REQUEST_RUNTIME_FACTS"
    PATCH_LOCAL = "PATCH_LOCAL"
    COMPLETE_MISSING_SCOPE = "COMPLETE_MISSING_SCOPE"
    ADD_PROOF_TESTS = "ADD_PROOF_TESTS"
    REMOVE_ENTROPY_SIGNAL = "REMOVE_ENTROPY_SIGNAL"
    REWORK_ARCHITECTURE = "REWORK_ARCHITECTURE"
    READY_FOR_ANCHOR = "READY_FOR_ANCHOR"
    ESCALATE_TO_HUMAN = "ESCALATE_TO_HUMAN"


def to_plain(obj: Any) -> Any:
    if isinstance(obj, Enum):
        return obj.value
    if is_dataclass(obj):
        return {key: to_plain(value) for key, value in asdict(obj).items()}
    if isinstance(obj, dict):
        return {key: to_plain(value) for key, value in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [to_plain(value) for value in obj]
    if isinstance(obj, Path):
        return str(obj)
    return obj


@dataclass
class RequirementSummary:
    problem: str
    goal: str


@dataclass
class MilestonePlan:
    key: str
    goal: str
    depends_on: list[str] = field(default_factory=list)
    planned_pr_model: str = "Single PR"
    acceptance: list[str] = field(default_factory=list)
    reference_assignment: str = ""


@dataclass
class WorkstreamPlan:
    key: str
    responsibility: str
    parallelizable: bool = True
    depends_on: list[str] = field(default_factory=list)
    recommended_executor: str = "Shared"


@dataclass
class TaskPlan:
    key: str
    milestone: str
    workstream: str
    summary: str
    design_refs: list[str] = field(default_factory=list)
    gap_refs: list[str] = field(default_factory=list)
    spec_refs: list[str] = field(default_factory=list)
    input: str = ""
    action: str = ""
    output: str = ""
    non_goals: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    acceptance: list[str] = field(default_factory=list)
    local_risks: list[str] = field(default_factory=list)
    recommended_executor: str = "Shared"
    execution_mode: str = "write"
    g1_commands: list[str] = field(default_factory=list)


@dataclass
class PRPlan:
    key: str
    milestone: str
    covers: list[str] = field(default_factory=list)
    goal: str = ""
    depends_on: list[str] = field(default_factory=list)
    acceptance_checklist: list[str] = field(default_factory=list)


@dataclass
class InitiativePlan:
    key: str
    title: str
    requirement_summary: RequirementSummary
    design_refs: list[str]
    gap_refs: list[str]
    sealed_decisions: list[str]
    execution_boundary: str
    initiative_reference_assignment: str
    background: str
    scope: list[str]
    non_goals: list[str]
    success_criteria: list[str]
    milestones: dict[str, MilestonePlan]
    workstreams: dict[str, WorkstreamPlan]
    tasks: dict[str, TaskPlan]
    pr_plan: list[PRPlan]
    global_residual_risks: list[str]
    follow_ups: list[str]
    g3_commands: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return to_plain(self)


@dataclass
class TaskRuntimeState:
    key: str
    milestone: str
    workstream: str
    state: TaskStatus = TaskStatus.NOT_READY
    depends_on: list[str] = field(default_factory=list)
    last_anchor_commit: Optional[str] = None
    latest_packet_ref: Optional[str] = None
    latest_observation_ref: Optional[str] = None
    latest_decision_ref: Optional[str] = None
    latest_g1_ref: Optional[str] = None
    latest_r1_ref: Optional[str] = None
    probe_count: int = 0
    stall_count: int = 0
    blocked_reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return to_plain(self)


@dataclass
class MilestoneRuntimeState:
    key: str
    state: MilestoneStatus = MilestoneStatus.NOT_READY
    task_keys: list[str] = field(default_factory=list)
    latest_pr_ref: Optional[str] = None
    latest_g2_ref: Optional[str] = None
    latest_r2_ref: Optional[str] = None
    blocked_reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return to_plain(self)


@dataclass
class InitiativeRuntimeState:
    initiative_key: str
    title: str
    state: InitiativeStatus = InitiativeStatus.READY
    current_frontier: Optional[str] = None
    task_states: dict[str, TaskRuntimeState] = field(default_factory=dict)
    milestone_states: dict[str, MilestoneRuntimeState] = field(default_factory=dict)
    latest_g3_ref: Optional[str] = None
    latest_r3_ref: Optional[str] = None
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "initiative_key": self.initiative_key,
            "title": self.title,
            "state": self.state.value,
            "current_frontier": self.current_frontier,
            "task_states": {key: value.to_dict() for key, value in self.task_states.items()},
            "milestone_states": {key: value.to_dict() for key, value in self.milestone_states.items()},
            "latest_g3_ref": self.latest_g3_ref,
            "latest_r3_ref": self.latest_r3_ref,
            "notes": list(self.notes),
        }


@dataclass
class GateCommandResult:
    command: str
    return_code: int
    stdout: str
    stderr: str

    def to_dict(self) -> dict[str, Any]:
        return to_plain(self)


@dataclass
class GateResult:
    profile: str
    object_key: str
    passed: bool
    commands: list[GateCommandResult]
    summary: str

    def to_dict(self) -> dict[str, Any]:
        return to_plain(self)


@dataclass
class ReviewReport:
    profile: str
    object_key: str
    verdict: str
    summary: str
    findings: list[str] = field(default_factory=list)
    residual_risks: list[str] = field(default_factory=list)
    escalations: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return to_plain(self)


@dataclass
class TransitionDecision:
    task_key: str
    trend: Trend
    action: DecisionAction
    why: str
    next_required_facts: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return to_plain(self)
