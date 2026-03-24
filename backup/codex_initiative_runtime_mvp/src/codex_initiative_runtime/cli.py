from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from .escalation import merge_panel_reports
from .models import InitiativeStatus, MilestoneStatus, TaskStatus
from .gate_review import (
    commands_for_initiative,
    commands_for_milestone,
    commands_for_task,
    finalize_review_report,
    persist_gate_result,
    prepare_review_bundle_for_initiative,
    prepare_review_bundle_for_milestone,
    prepare_review_bundle_for_task,
    run_gate_commands,
)
from .initiative_runtime import planning_preflight, rebuild_state, run_initiative
from .planning_parser import parse_initiative_doc
from .review_packet import build_task_packet
from .scheduler import select_frontier, select_ready_tasks
from .state_store import (
    decision_path,
    fact_path,
    initiative_dir,
    load_state,
    observation_path,
    packet_path,
    report_path,
    save_state,
)
from .task_controller import load_observation, step_transition
from .utils import find_repo_root, run_command, safe_git_status, write_json, write_text


def _print_json(data: dict) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def cmd_planning_preflight(args: argparse.Namespace) -> int:
    result = planning_preflight(args.initiative_doc, args.repo_root)
    _print_json(result)
    return 0 if result["passed"] else 2


def cmd_rebuild_state(args: argparse.Namespace) -> int:
    state = rebuild_state(args.initiative_doc, args.repo_root)
    _print_json(state.to_dict())
    return 0


def cmd_select_frontier(args: argparse.Namespace) -> int:
    plan = parse_initiative_doc(args.initiative_doc)
    state = load_state(plan.key, args.repo_root) or rebuild_state(args.initiative_doc, args.repo_root)
    frontier = select_frontier(plan, state)
    _print_json({"initiative": plan.key, "frontier": frontier})
    return 0


def cmd_select_ready_tasks(args: argparse.Namespace) -> int:
    plan = parse_initiative_doc(args.initiative_doc)
    state = load_state(plan.key, args.repo_root) or rebuild_state(args.initiative_doc, args.repo_root)
    frontier = select_frontier(plan, state)
    selection = select_ready_tasks(plan, state, frontier, max_write_tasks=args.max_write_tasks)
    _print_json(
        {
            "initiative": plan.key,
            "frontier": frontier,
            "write_tasks": selection.write_tasks,
            "readonly_tasks": selection.readonly_tasks,
        }
    )
    return 0


def cmd_run_initiative(args: argparse.Namespace) -> int:
    summary = run_initiative(args.initiative_doc, args.repo_root, max_write_tasks=args.max_write_tasks)
    _print_json(summary)
    return 0 if summary.get("status") != "PLANNING_BLOCKED" else 2


def cmd_build_task_packet(args: argparse.Namespace) -> int:
    plan = parse_initiative_doc(args.initiative_doc)
    state = load_state(plan.key, args.repo_root) or rebuild_state(args.initiative_doc, args.repo_root)
    packet = build_task_packet(plan, state, args.task_key, args.repo_root)
    path = packet_path(plan.key, f"{args.task_key}.json", args.repo_root)
    write_json(path, packet)
    state.task_states[args.task_key].latest_packet_ref = str(path)
    save_state(state, args.repo_root)
    _print_json({"packet": str(path), "task": args.task_key})
    return 0


def cmd_collect_runtime_facts(args: argparse.Namespace) -> int:
    plan = parse_initiative_doc(args.initiative_doc)
    repo_root = find_repo_root(args.repo_root)
    payload = {
        "initiative": plan.key,
        "task_key": args.task_key,
        "probe_id": args.probe_id,
        "command": args.command,
        "git_status": safe_git_status(repo_root),
    }
    if args.command:
        rc, stdout, stderr = run_command(args.command, repo_root)
        payload["return_code"] = rc
        payload["stdout"] = stdout
        payload["stderr"] = stderr
    path = fact_path(plan.key, f"{args.task_key}-{args.probe_id}.json", repo_root)
    write_json(path, payload)
    state = load_state(plan.key, repo_root) or rebuild_state(args.initiative_doc, repo_root)
    state.task_states[args.task_key].probe_count += 1
    save_state(state, repo_root)
    _print_json({"fact": str(path), **payload})
    return 0


def cmd_step_transition(args: argparse.Namespace) -> int:
    repo_root = find_repo_root(args.repo_root)
    plan = parse_initiative_doc(args.initiative_doc)
    state = load_state(plan.key, repo_root) or rebuild_state(args.initiative_doc, repo_root)
    task_state = state.task_states[args.task_key]
    current = load_observation(args.observation)
    previous = None
    if task_state.latest_observation_ref and Path(task_state.latest_observation_ref).exists():
        previous = load_observation(task_state.latest_observation_ref)
    decision = step_transition(args.task_key, task_state.to_dict(), previous, current)
    obs_path = observation_path(plan.key, Path(args.observation).name, repo_root)
    if Path(args.observation).resolve() != obs_path.resolve():
        write_json(obs_path, current)
    task_state.latest_observation_ref = str(obs_path)
    if decision.trend == decision.trend.STALLED:
        task_state.stall_count += 1
    else:
        task_state.stall_count = 0
    if decision.action == decision.action.REQUEST_RUNTIME_FACTS:
        task_state.probe_count += 1
    dec_path = decision_path(plan.key, f"{args.task_key}.json", repo_root)
    write_json(dec_path, decision.to_dict())
    task_state.latest_decision_ref = str(dec_path)
    if decision.action == decision.action.READY_FOR_ANCHOR:
        task_state.state = TaskStatus.READY_FOR_ANCHOR
    elif decision.action == decision.action.ESCALATE_TO_HUMAN:
        task_state.state = TaskStatus.BLOCKED
        task_state.blocked_reason = decision.why
    else:
        task_state.state = TaskStatus.IN_FLIGHT
    save_state(state, repo_root)
    _print_json({"decision": str(dec_path), **decision.to_dict()})
    return 0


def cmd_cut_anchor(args: argparse.Namespace) -> int:
    repo_root = find_repo_root(args.repo_root)
    plan = parse_initiative_doc(args.initiative_doc)
    state = load_state(plan.key, repo_root) or rebuild_state(args.initiative_doc, repo_root)
    task = plan.tasks[args.task_key]
    task_state = state.task_states[args.task_key]
    summary = args.summary or task.summary
    kind = args.kind
    title = f"{kind}({task.milestone.lower()}/{task.key.lower()}): {summary}"
    checks = ", ".join(task.g1_commands or ["python -m unittest -q"])
    body = "\n".join(
        [
            f"Intent: {task.summary}",
            f"Scope: {task.action}",
            f"Non-Goals: {'; '.join(task.non_goals) if task.non_goals else 'None'}",
            f"Checks: {checks}",
        ]
    )
    draft_path = initiative_dir(plan.key, repo_root) / "drafts" / f"{kind}-{args.task_key}.txt"
    write_text(draft_path, title + "\n\n" + body + "\n")
    executed = False
    commit_sha = None
    if args.execute:
        subprocess.run(["git", "-C", str(repo_root), "add", "-A"], check=False)
        completed = subprocess.run(["git", "-C", str(repo_root), "commit", "-F", str(draft_path)], text=True, capture_output=True, check=False)
        if completed.returncode == 0:
            executed = True
            head = subprocess.run(["git", "-C", str(repo_root), "rev-parse", "HEAD"], text=True, capture_output=True, check=False)
            if head.returncode == 0:
                commit_sha = head.stdout.strip()
                task_state.last_anchor_commit = commit_sha
                task_state.state = TaskStatus.IN_G1
                save_state(state, repo_root)
        else:
            _print_json({"draft": str(draft_path), "executed": False, "error": completed.stderr})
            return 4
    _print_json({"draft": str(draft_path), "executed": executed, "commit_sha": commit_sha})
    return 0


def cmd_run_gate(args: argparse.Namespace) -> int:
    plan = parse_initiative_doc(args.initiative_doc)
    if args.profile == "G1":
        commands = commands_for_task(plan, args.object_key)
    elif args.profile == "G2":
        commands = commands_for_milestone(plan, args.object_key)
    elif args.profile == "G3":
        commands = commands_for_initiative(plan)
    else:
        raise SystemExit(f"unsupported profile: {args.profile}")

    result = run_gate_commands(args.profile, args.object_key, commands, args.repo_root)
    path = persist_gate_result(plan.key, result, repo_root=args.repo_root)
    state = load_state(plan.key, args.repo_root) or rebuild_state(args.initiative_doc, args.repo_root)

    if args.profile == "G1":
        state.task_states[args.object_key].latest_g1_ref = str(path)
        state.task_states[args.object_key].state = TaskStatus.IN_R1 if result.passed else TaskStatus.BLOCKED
    elif args.profile == "G2":
        state.milestone_states[args.object_key].latest_g2_ref = str(path)
        state.milestone_states[args.object_key].state = MilestoneStatus.IN_R2 if result.passed else MilestoneStatus.BLOCKED
    elif args.profile == "G3":
        state.latest_g3_ref = str(path)
    save_state(state, args.repo_root)

    _print_json({"report": str(path), **result.to_dict()})
    return 0 if result.passed else 3


def cmd_prepare_review_bundle(args: argparse.Namespace) -> int:
    plan = parse_initiative_doc(args.initiative_doc)
    if args.profile == "R1":
        path = prepare_review_bundle_for_task(plan, args.object_key, plan.key, args.repo_root)
    elif args.profile == "R2":
        path = prepare_review_bundle_for_milestone(plan, args.object_key, plan.key, args.repo_root)
    elif args.profile == "R3":
        path = prepare_review_bundle_for_initiative(plan, plan.key, args.repo_root)
    else:
        raise SystemExit(f"unsupported profile: {args.profile}")
    _print_json({"bundle": str(path), "profile": args.profile, "object_key": args.object_key})
    return 0


def cmd_finalize_review(args: argparse.Namespace) -> int:
    plan = parse_initiative_doc(args.initiative_doc)
    json_path, md_path = finalize_review_report(
        plan.key,
        args.profile,
        args.object_key,
        args.raw_input,
        repo_root=args.repo_root,
    )
    state = load_state(plan.key, args.repo_root) or rebuild_state(args.initiative_doc, args.repo_root)
    if args.profile == "R1":
        task_state = state.task_states[args.object_key]
        task_state.latest_r1_ref = str(json_path)
        task_state.state = TaskStatus.DONE if args.verdict == "PASS" else TaskStatus.BLOCKED
    elif args.profile == "R2":
        milestone_state = state.milestone_states[args.object_key]
        milestone_state.latest_r2_ref = str(json_path)
        milestone_state.state = MilestoneStatus.MERGED if args.verdict == "PASS" else MilestoneStatus.BLOCKED
    elif args.profile == "R3":
        state.latest_r3_ref = str(json_path)
        state.state = InitiativeStatus.DONE if args.verdict == "PASS" else InitiativeStatus.WAITING_R3
    save_state(state, args.repo_root)
    _print_json({"json_report": str(json_path), "markdown_report": str(md_path)})
    return 0


def cmd_draft_milestone_pr(args: argparse.Namespace) -> int:
    plan = parse_initiative_doc(args.initiative_doc)
    state = load_state(plan.key, args.repo_root) or rebuild_state(args.initiative_doc, args.repo_root)
    milestone = plan.milestones[args.milestone_key]
    related_pr = next((pr for pr in plan.pr_plan if pr.milestone == args.milestone_key), None)
    title = f"[{args.milestone_key}] {milestone.goal}"
    lines = [
        f"# {title}",
        "",
        "## Goal",
        milestone.goal,
        "",
        "## Acceptance",
    ]
    lines.extend([f"- {item}" for item in milestone.acceptance] or ["- None"])
    lines.extend(["", "## Task Status"])
    for task_key in [key for key, task in plan.tasks.items() if task.milestone == args.milestone_key]:
        lines.append(f"- {task_key}: {state.task_states[task_key].state.value}")
    if related_pr:
        lines.extend(["", "## Checklist"])
        lines.extend([f"- [ ] {item}" for item in related_pr.acceptance_checklist] or ["- [ ] No checklist"])
    path = initiative_dir(plan.key, args.repo_root) / "drafts" / f"pr-{args.milestone_key}.md"
    write_text(path, "\n".join(lines) + "\n")
    state.milestone_states[args.milestone_key].latest_pr_ref = str(path)
    save_state(state, args.repo_root)
    _print_json({"pr_draft": str(path), "title": title})
    return 0


def cmd_shadow_check(args: argparse.Namespace) -> int:
    plan = parse_initiative_doc(args.initiative_doc)
    state = load_state(plan.key, args.repo_root) or rebuild_state(args.initiative_doc, args.repo_root)
    color = "green"
    reasons: list[str] = []
    if any(task.state.name == "BLOCKED" for task in state.task_states.values()):
        color = "red"
        reasons.append("存在 BLOCKED Task。")
    elif any(task.state.name in {"IN_FLIGHT", "IN_G1", "IN_R1", "READY_FOR_ANCHOR"} for task in state.task_states.values()):
        color = "yellow"
        reasons.append("存在尚未正式收口的 Task。")
    elif any(ms.state.name in {"READY_FOR_PR", "IN_R2"} for ms in state.milestone_states.values()):
        color = "yellow"
        reasons.append("存在等待 R2 收口的里程碑。")
    payload = {
        "initiative": plan.key,
        "color": color,
        "reasons": reasons or ["当前未观察到显著早期漂移。"],
    }
    path = report_path(plan.key, f"shadow-check-{plan.key}.json", args.repo_root)
    write_json(path, payload)
    _print_json({"report": str(path), **payload})
    return 0


def cmd_shadow_review(args: argparse.Namespace) -> int:
    plan = parse_initiative_doc(args.initiative_doc)
    report = report_path(plan.key, f"shadow-check-{plan.key}.json", args.repo_root)
    if not report.exists():
        raise SystemExit("shadow-check report not found; run shadow-check first")
    payload = json.loads(report.read_text(encoding="utf-8"))
    action = "continue"
    if payload["color"] == "yellow":
        action = "checkpoint before next task"
    elif payload["color"] == "red":
        action = "open milestone review early"
    out = {
        "initiative": plan.key,
        "color": payload["color"],
        "action": action,
        "reasons": payload["reasons"],
    }
    path = report_path(plan.key, f"shadow-review-{plan.key}.json", args.repo_root)
    write_json(path, out)
    _print_json({"report": str(path), **out})
    return 0


def cmd_merge_escalation(args: argparse.Namespace) -> int:
    plan = parse_initiative_doc(args.initiative_doc)
    output = report_path(plan.key, f"escalation-{args.object_key}.json", args.repo_root)
    merge_panel_reports(output, *args.inputs)
    _print_json({"report": str(output)})
    return 0


def cmd_summary(args: argparse.Namespace) -> int:
    plan = parse_initiative_doc(args.initiative_doc)
    state = load_state(plan.key, args.repo_root) or rebuild_state(args.initiative_doc, args.repo_root)
    _print_json(state.to_dict())
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cir", description="Codex Initiative Runtime")
    sub = parser.add_subparsers(dest="command", required=True)

    def add_common(command: argparse.ArgumentParser) -> None:
        command.add_argument("--repo-root", default=".")

    p = sub.add_parser("planning-preflight")
    p.add_argument("--initiative-doc", required=True)
    add_common(p)
    p.set_defaults(func=cmd_planning_preflight)

    p = sub.add_parser("rebuild-state")
    p.add_argument("--initiative-doc", required=True)
    add_common(p)
    p.set_defaults(func=cmd_rebuild_state)

    p = sub.add_parser("select-frontier")
    p.add_argument("--initiative-doc", required=True)
    add_common(p)
    p.set_defaults(func=cmd_select_frontier)

    p = sub.add_parser("select-ready-tasks")
    p.add_argument("--initiative-doc", required=True)
    p.add_argument("--max-write-tasks", type=int, default=1)
    add_common(p)
    p.set_defaults(func=cmd_select_ready_tasks)

    p = sub.add_parser("run-initiative")
    p.add_argument("--initiative-doc", required=True)
    p.add_argument("--max-write-tasks", type=int, default=1)
    add_common(p)
    p.set_defaults(func=cmd_run_initiative)

    p = sub.add_parser("build-task-packet")
    p.add_argument("--initiative-doc", required=True)
    p.add_argument("--task-key", required=True)
    add_common(p)
    p.set_defaults(func=cmd_build_task_packet)

    p = sub.add_parser("collect-runtime-facts")
    p.add_argument("--initiative-doc", required=True)
    p.add_argument("--task-key", required=True)
    p.add_argument("--probe-id", required=True)
    p.add_argument("--command", default="")
    add_common(p)
    p.set_defaults(func=cmd_collect_runtime_facts)

    p = sub.add_parser("step-transition")
    p.add_argument("--initiative-doc", required=True)
    p.add_argument("--task-key", required=True)
    p.add_argument("--observation", required=True)
    add_common(p)
    p.set_defaults(func=cmd_step_transition)

    p = sub.add_parser("cut-anchor")
    p.add_argument("--initiative-doc", required=True)
    p.add_argument("--task-key", required=True)
    p.add_argument("--summary", default="")
    p.add_argument("--kind", choices=["anchor", "fixup", "revert"], default="anchor")
    p.add_argument("--execute", action="store_true")
    add_common(p)
    p.set_defaults(func=cmd_cut_anchor)

    p = sub.add_parser("run-gate")
    p.add_argument("--initiative-doc", required=True)
    p.add_argument("--profile", choices=["G1", "G2", "G3"], required=True)
    p.add_argument("--object-key", required=True)
    add_common(p)
    p.set_defaults(func=cmd_run_gate)

    p = sub.add_parser("prepare-review-bundle")
    p.add_argument("--initiative-doc", required=True)
    p.add_argument("--profile", choices=["R1", "R2", "R3"], required=True)
    p.add_argument("--object-key", required=True)
    add_common(p)
    p.set_defaults(func=cmd_prepare_review_bundle)

    p = sub.add_parser("finalize-review")
    p.add_argument("--initiative-doc", required=True)
    p.add_argument("--profile", choices=["R1", "R2", "R3"], required=True)
    p.add_argument("--object-key", required=True)
    p.add_argument("--raw-input", required=True)
    p.add_argument("--verdict", choices=["PASS", "BLOCKED"], required=True)
    add_common(p)
    p.set_defaults(func=cmd_finalize_review)

    p = sub.add_parser("draft-milestone-pr")
    p.add_argument("--initiative-doc", required=True)
    p.add_argument("--milestone-key", required=True)
    add_common(p)
    p.set_defaults(func=cmd_draft_milestone_pr)

    p = sub.add_parser("shadow-check")
    p.add_argument("--initiative-doc", required=True)
    add_common(p)
    p.set_defaults(func=cmd_shadow_check)

    p = sub.add_parser("shadow-review")
    p.add_argument("--initiative-doc", required=True)
    add_common(p)
    p.set_defaults(func=cmd_shadow_review)

    p = sub.add_parser("merge-escalation")
    p.add_argument("--initiative-doc", required=True)
    p.add_argument("--object-key", required=True)
    p.add_argument("--inputs", nargs="+", required=True)
    add_common(p)
    p.set_defaults(func=cmd_merge_escalation)

    p = sub.add_parser("summary")
    p.add_argument("--initiative-doc", required=True)
    add_common(p)
    p.set_defaults(func=cmd_summary)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
