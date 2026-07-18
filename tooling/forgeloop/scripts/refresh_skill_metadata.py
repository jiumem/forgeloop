#!/usr/bin/env python3
"""使用 Skill Creator 生成并校验全部 agents/openai.yaml。"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TOOLING_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = TOOLING_ROOT.parents[1]
PLUGIN_ROOT = REPO_ROOT / "plugins" / "forgeloop"
METADATA_PATH = TOOLING_ROOT / "config" / "skill-metadata.json"
SUITE_PATH = TOOLING_ROOT / "config" / "skill-suite.json"
CODEX_HOME = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
GENERATOR = CODEX_HOME / "skills" / ".system" / "skill-creator" / "scripts" / "generate_openai_yaml.py"


def generate(skill_dir: Path, values: dict[str, str], explicit_only: bool) -> str:
    command = [sys.executable, str(GENERATOR), str(skill_dir)]
    for key in ("display_name", "short_description", "default_prompt"):
        command.extend(["--interface", f"{key}={values[key]}"])
    result = subprocess.run(command, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stdout + result.stderr)
    yaml_path = skill_dir / "agents" / "openai.yaml"
    text = yaml_path.read_text(encoding="utf-8")
    text += "policy:\n"
    text += f"  allow_implicit_invocation: {'false' if explicit_only else 'true'}\n"
    yaml_path.write_text(text, encoding="utf-8")
    return text


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="在临时目录生成并比较，不写活动目录")
    args = parser.parse_args()
    if not GENERATOR.is_file():
        print(f"错误：找不到 Skill Creator 生成器：{GENERATOR}", file=sys.stderr)
        return 2
    metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    suite = json.loads(SUITE_PATH.read_text(encoding="utf-8"))
    expected_names = set(suite["release"]["skills"])
    if set(metadata) != expected_names:
        missing = sorted(expected_names - set(metadata))
        extra = sorted(set(metadata) - expected_names)
        print(f"错误：元数据清单不一致；缺失={missing}；多余={extra}", file=sys.stderr)
        return 1
    explicit = set(suite["release"]["explicit_only"])
    errors: list[str] = []
    for name in suite["release"]["skills"]:
        skill_dir = PLUGIN_ROOT / "skills" / name
        if not skill_dir.is_dir():
            if args.check:
                errors.append(f"{name}: Skill 尚未创建")
                continue
            print(f"跳过尚未创建的 Skill：{name}")
            continue
        if args.check:
            with tempfile.TemporaryDirectory() as directory:
                temp_skill = Path(directory) / name
                temp_skill.mkdir()
                shutil.copy2(skill_dir / "SKILL.md", temp_skill / "SKILL.md")
                expected = generate(temp_skill, metadata[name], name in explicit)
            actual_path = skill_dir / "agents" / "openai.yaml"
            if not actual_path.is_file() or actual_path.read_text(encoding="utf-8") != expected:
                errors.append(f"{name}: agents/openai.yaml 已漂移")
        else:
            generate(skill_dir, metadata[name], name in explicit)
            print(f"已刷新：{name}")
    if errors:
        print("\n".join(f"错误：{error}" for error in errors), file=sys.stderr)
        return 1
    print("Skill UI 元数据校验通过。" if args.check else "Skill UI 元数据刷新完成。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
