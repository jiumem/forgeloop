from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any


def find_repo_root(start: str | Path | None = None) -> Path:
    current = Path(start or Path.cwd()).resolve()
    for candidate in [current, *current.parents]:
        if (candidate / ".git").exists() or (candidate / "pyproject.toml").exists():
            return candidate
    return current


def read_text(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def write_text(path: str | Path, content: str) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def read_json(path: str | Path) -> Any:
    return json.loads(read_text(path))


def write_json(path: str | Path, data: Any) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def relpath(path: str | Path, root: str | Path | None = None) -> str:
    path = Path(path).resolve()
    root = Path(root or find_repo_root()).resolve()
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def path_from_ref(ref: str, repo_root: str | Path) -> Path | None:
    ref = ref.strip()
    if not ref:
        return None
    if re.match(r"^[a-zA-Z]+://", ref):
        return None
    base = ref.split("#", 1)[0].strip()
    if not base:
        return None
    return (Path(repo_root) / base).resolve()


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "item"


def run_command(command: str, cwd: str | Path) -> tuple[int, str, str]:
    completed = subprocess.run(
        command,
        shell=True,
        cwd=str(cwd),
        text=True,
        capture_output=True,
        check=False,
    )
    return completed.returncode, completed.stdout, completed.stderr


def safe_git_log(repo_root: str | Path) -> list[tuple[str, str]]:
    repo_root = Path(repo_root)
    try:
        completed = subprocess.run(
            ["git", "-C", str(repo_root), "log", "--all", "--pretty=%H%x09%s"],
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            return []
        records: list[tuple[str, str]] = []
        for line in completed.stdout.splitlines():
            if "\t" not in line:
                continue
            sha, subject = line.split("\t", 1)
            records.append((sha.strip(), subject.strip()))
        return records
    except FileNotFoundError:
        return []


def safe_git_status(repo_root: str | Path) -> list[str]:
    try:
        completed = subprocess.run(
            ["git", "-C", str(repo_root), "status", "--porcelain"],
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            return []
        return [line.strip() for line in completed.stdout.splitlines() if line.strip()]
    except FileNotFoundError:
        return []


def ensure_gitignore_entry(repo_root: str | Path, entry: str) -> None:
    gitignore = Path(repo_root) / ".gitignore"
    existing = gitignore.read_text(encoding="utf-8").splitlines() if gitignore.exists() else []
    if entry not in existing:
        existing.append(entry)
        gitignore.write_text("\n".join(existing).rstrip() + "\n", encoding="utf-8")
