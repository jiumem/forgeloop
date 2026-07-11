#!/usr/bin/env python3
"""校验 run-initiative 封板协议的必需条款未漂移或遗漏。"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = PLUGIN_ROOT / "skills" / "run-initiative"
CONTRACT = PLUGIN_ROOT / "config" / "runtime-contract.json"


def validate(root: Path = SKILL_ROOT, contract_path: Path = CONTRACT) -> list[str]:
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    errors: list[str] = []
    for relative, markers in contract.items():
        path = root / relative
        if not path.is_file():
            errors.append(f"缺失协议文件：{relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                errors.append(f"{relative}: 缺失封板条款 {marker}")
    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("\n".join(f"错误：{error}" for error in errors), file=sys.stderr)
        return 1
    print("run-initiative 运行协议校验通过。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
