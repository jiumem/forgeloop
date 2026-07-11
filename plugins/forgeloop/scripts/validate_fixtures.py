#!/usr/bin/env python3
"""校验 Fixture 证据字段与三 Tracker 领域终态等价性。"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REQUIRED = {
    "id", "group", "tracker", "initial_state", "entry_prompt", "expected_writes",
    "forbidden_writes", "terminal_state", "failure_diagnostic", "domain_state",
}
TRACKERS = {"github", "gitlab", "local"}


def validate(path: Path) -> list[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    errors: list[str] = []
    cases = data.get("cases", [])
    ids: set[str] = set()
    groups: dict[str, list[dict]] = {}
    for case in cases:
        missing = REQUIRED - set(case)
        if missing:
            errors.append(f"{case.get('id', '<unknown>')}: 缺失字段 {sorted(missing)}")
            continue
        if case["id"] in ids:
            errors.append(f"重复 Fixture ID：{case['id']}")
        ids.add(case["id"])
        groups.setdefault(case["group"], []).append(case)
        if not case["expected_writes"] or not case["forbidden_writes"]:
            errors.append(f"{case['id']}: 必须同时声明预期写入和禁止写入")
    for group, group_cases in groups.items():
        if len(group_cases) == 1:
            continue
        trackers = {case["tracker"] for case in group_cases}
        if trackers != TRACKERS:
            errors.append(f"{group}: Tracker 覆盖不完整 {sorted(trackers)}")
            continue
        states = {json.dumps(case["domain_state"], sort_keys=True, ensure_ascii=False) for case in group_cases}
        terminals = {case["terminal_state"] for case in group_cases}
        if len(states) != 1 or len(terminals) != 1:
            errors.append(f"{group}: 三 Tracker 领域终态不等价")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()
    errors: list[str] = []
    for path in args.paths:
        errors.extend(f"{path}: {error}" for error in validate(path))
    if errors:
        print("\n".join(f"错误：{error}" for error in errors), file=sys.stderr)
        return 1
    print(f"Fixture 校验通过：{len(args.paths)} 个矩阵文件")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
