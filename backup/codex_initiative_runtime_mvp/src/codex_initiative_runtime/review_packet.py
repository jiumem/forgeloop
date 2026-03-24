from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .models import InitiativePlan, InitiativeRuntimeState
from .utils import find_repo_root, relpath, safe_git_status, write_json


def build_task_packet(
    plan: InitiativePlan,
    state: InitiativeRuntimeState,
    task_key: str,
    repo_root: str | Path | None = None,
) -> dict[str, Any]:
    repo_root = find_repo_root(repo_root)
    task = plan.tasks[task_key]
    task_state = state.task_states[task_key]
    packet = {
        "initiative": {"key": plan.key, "title": plan.title},
        "task": {
            "key": task.key,
            "milestone": task.milestone,
            "workstream": task.workstream,
            "summary": task.summary,
            "design_refs": task.design_refs,
            "gap_refs": task.gap_refs,
            "spec_refs": task.spec_refs,
            "input": task.input,
            "action": task.action,
            "output": task.output,
            "non_goals": task.non_goals,
            "dependencies": task.dependencies,
            "acceptance": task.acceptance,
            "local_risks": task.local_risks,
            "recommended_executor": task.recommended_executor,
            "execution_mode": task.execution_mode,
        },
        "task_runtime": task_state.to_dict(),
        "repo": {
            "root": relpath(repo_root, repo_root),
            "git_status": safe_git_status(repo_root),
        },
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    return packet


def build_review_bundle(
    profile: str,
    object_key: str,
    references: list[str],
    evidence: list[str],
    repo_root: str | Path | None = None,
) -> dict[str, Any]:
    repo_root = find_repo_root(repo_root)
    return {
        "profile": profile,
        "object_key": object_key,
        "references": references,
        "evidence": evidence,
        "repo_root": str(repo_root),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
