#!/usr/bin/env python3

from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys


REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT_PATH = REPO_ROOT / ".forgeloop/exports/planning-runtime-formal-bundle.txt"

PLANNING_FILES = [
    "plugins/forgeloop/skills/run-planning/SKILL.md",
    "plugins/forgeloop/skills/run-planning/references/planning-state.md",
    "plugins/forgeloop/skills/planning-loop/SKILL.md",
    "plugins/forgeloop/agents/planner.toml",
    "plugins/forgeloop/agents/design_reviewer.toml",
    "plugins/forgeloop/agents/gap_reviewer.toml",
    "plugins/forgeloop/agents/plan_reviewer.toml",
    "plugins/forgeloop/skills/planning-loop/references/planning-rolling-doc.md",
    "plugins/forgeloop/skills/planning-loop/references/design-doc.md",
    "plugins/forgeloop/skills/planning-loop/references/gap-analysis.md",
    "plugins/forgeloop/skills/planning-loop/references/total-task-doc.md",
]

RUNTIME_FILES = [
    "plugins/forgeloop/skills/run-initiative/SKILL.md",
    "plugins/forgeloop/skills/rebuild-runtime/SKILL.md",
    "plugins/forgeloop/skills/task-loop/SKILL.md",
    "plugins/forgeloop/skills/milestone-loop/SKILL.md",
    "plugins/forgeloop/skills/initiative-loop/SKILL.md",
    "plugins/forgeloop/agents/coder.toml",
    "plugins/forgeloop/agents/task_reviewer.toml",
    "plugins/forgeloop/agents/milestone_reviewer.toml",
    "plugins/forgeloop/agents/initiative_reviewer.toml",
    "plugins/forgeloop/skills/run-initiative/references/global-state.md",
    "plugins/forgeloop/skills/run-initiative/references/task-review-rolling-doc.md",
    "plugins/forgeloop/skills/run-initiative/references/milestone-review-rolling-doc.md",
    "plugins/forgeloop/skills/run-initiative/references/initiative-review-rolling-doc.md",
    "plugins/forgeloop/skills/run-initiative/references/runtime-cutover.md",
    "plugins/forgeloop/skills/using-git-worktrees/SKILL.md",
]

SHARED_CONTRACT_FILES = [
    "plugins/forgeloop/skills/references/anchor-addressing.md",
    "plugins/forgeloop/skills/references/derived-views.md",
    "plugins/forgeloop/skills/references/validation-matrix.md",
    "plugins/forgeloop/scripts/anchor_slices.py",
]

SEPARATOR = "=" * 100


def ordered_relative_paths() -> list[str]:
    return PLANNING_FILES + RUNTIME_FILES + SHARED_CONTRACT_FILES


def repo_path(rel_path: str) -> pathlib.Path:
    return REPO_ROOT / rel_path


def blob_exists(rel_path: str, rev: str | None) -> bool:
    if rev is None:
        return repo_path(rel_path).exists()
    result = subprocess.run(
        ["git", "cat-file", "-e", f"{rev}:{rel_path}"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def read_blob(rel_path: str, rev: str | None) -> str:
    if rev is None:
        return repo_path(rel_path).read_text()
    result = subprocess.run(
        ["git", "show", f"{rev}:{rel_path}"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise FileNotFoundError(f"missing required file at {rev}: {rel_path}")
    return result.stdout


def render_header(paths: list[str], missing: list[str], rev: str | None) -> str:
    lines = [
        SEPARATOR,
        "FORGELOOP FORMAL LOOPS BUNDLE",
        f"REPO ROOT: {REPO_ROOT}",
        f"REVISION: {rev or 'WORKTREE'}",
        f"TOTAL FILES: {len(paths)}",
        SEPARATOR,
        "",
        "[planning]",
    ]
    lines.extend(f"- {path}" for path in paths[: len([p for p in PLANNING_FILES if p in paths])])
    lines.extend(["", "[runtime]"])
    planning_count = len([p for p in PLANNING_FILES if p in paths])
    runtime_count = len([p for p in RUNTIME_FILES if p in paths])
    runtime_start = planning_count
    runtime_end = runtime_start + runtime_count
    lines.extend(f"- {path}" for path in paths[runtime_start:runtime_end])
    lines.extend(["", "[shared-contracts-and-tooling]"])
    lines.extend(f"- {path}" for path in paths[runtime_end:])
    if missing:
        lines.extend(["", "[omitted-missing-at-revision]"])
        lines.extend(f"- {path}" for path in missing)
    lines.extend(["", SEPARATOR, ""])
    return "\n".join(lines)


def render_file_block(rel_path: str, index: int, total: int, rev: str | None) -> str:
    content = read_blob(rel_path, rev)
    body = content.rstrip("\n")
    lines = [
        SEPARATOR,
        f"BEGIN FILE {index}/{total}",
        f"PATH: {rel_path}",
        f"REVISION: {rev or 'WORKTREE'}",
        SEPARATOR,
        body,
        SEPARATOR,
        f"END FILE {index}/{total}",
        f"PATH: {rel_path}",
        f"REVISION: {rev or 'WORKTREE'}",
        SEPARATOR,
        "",
    ]
    return "\n".join(lines)


def build_bundle(rev: str | None) -> str:
    all_paths = ordered_relative_paths()
    existing = [rel_path for rel_path in all_paths if blob_exists(rel_path, rev)]
    missing = [rel_path for rel_path in all_paths if rel_path not in existing]
    if rev is None and missing:
        rendered = ", ".join(missing)
        raise FileNotFoundError(f"missing required file(s): {rendered}")
    if not existing:
        raise FileNotFoundError("no bundle inputs were found")

    sections = [render_header(existing, missing, rev)]
    total = len(existing)
    for index, rel_path in enumerate(existing, start=1):
        sections.append(render_file_block(rel_path, index=index, total=total, rev=rev))
    return "\n".join(sections)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Concatenate Forgeloop planning/runtime formal loop sources into one text bundle."
    )
    parser.add_argument(
        "--out",
        type=pathlib.Path,
        help=(
            "Write the bundle to this path. "
            f"If omitted, default to {DEFAULT_OUTPUT_PATH}."
        ),
    )
    parser.add_argument(
        "--rev",
        help="Read bundle inputs from this git revision instead of the current worktree.",
    )
    args = parser.parse_args()

    bundle = build_bundle(rev=args.rev)
    output_path = args.out or DEFAULT_OUTPUT_PATH
    if not output_path.is_absolute():
        output_path = REPO_ROOT / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(bundle)
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
