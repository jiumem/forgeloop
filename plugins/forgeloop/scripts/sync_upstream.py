#!/usr/bin/env python3
"""按固定 Commit 导入或校验 Forgeloop 的上游 Skills。"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PLUGIN_ROOT.parents[1]
CONFIG_PATH = PLUGIN_ROOT / "config" / "upstream-map.json"
METADATA_PATH = PLUGIN_ROOT / "config" / "skill-metadata.json"


def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def load_metadata() -> dict:
    return json.loads(METADATA_PATH.read_text(encoding="utf-8"))


def upstream_head(root: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"无法读取上游 Commit：{result.stderr.strip()}")
    return result.stdout.strip()


def require_upstream_commit(actual: str, expected: str) -> None:
    if actual != expected:
        raise RuntimeError(f"上游 Commit 不匹配；预期 {expected}，实际 {actual}")


def transform_text(text: str, target: str, replacements: list[list[str]]) -> str:
    text = re.sub(r"(?m)^disable-model-invocation:.*\n", "", text)
    text = re.sub(r"(?m)^argument-hint:.*\n", "", text)
    for old, new in replacements:
        text = text.replace(old, new)
    text = re.sub(r"(?m)^name: [^\n]+$", f"name: {target}", text, count=1)
    if target == "primary-source-research":
        text = text.replace("# Research", "# Primary Source Research")
    return text


def apply_required_replacements(
    text: str, replacements: list[list[str]], context: str
) -> str:
    for old, new in replacements:
        if old not in text:
            raise RuntimeError(f"局部替换目标不存在：{context}：{old}")
        text = text.replace(old, new)
    return text


def replace_trigger_description(text: str, description: str, context: str) -> str:
    if not description.startswith("Load when "):
        raise RuntimeError(f"触发描述必须以 Load when 开头：{context}")
    result, count = re.subn(
        r"(?m)^description: [^\n]+$",
        f"description: {description}",
        text,
        count=1,
    )
    if count != 1:
        raise RuntimeError(f"无法替换触发描述：{context}")
    return result


def expected_files(config: dict, mapping: dict) -> dict[Path, bytes]:
    upstream = REPO_ROOT / config["upstream_root"] / mapping["source"]
    if not upstream.is_dir():
        raise RuntimeError(f"缺失上游目录：{upstream}")
    expected: dict[Path, bytes] = {}
    for source in sorted(upstream.rglob("*")):
        if not source.is_file() or ".git" in source.parts:
            continue
        relative = source.relative_to(upstream)
        data = source.read_bytes()
        try:
            transformed_text = transform_text(
                data.decode("utf-8"), mapping["target"], config["replacements"]
            )
            file_replacements = mapping.get("file_replacements", {}).get(
                relative.as_posix(), []
            )
            transformed = apply_required_replacements(
                transformed_text,
                file_replacements,
                f"{mapping['target']}/{relative.as_posix()}",
            ).encode("utf-8")
        except UnicodeDecodeError:
            transformed = data
        expected[relative] = transformed
    overlay = mapping.get("overlay")
    if overlay:
        expected[Path("SKILL.md")] = (PLUGIN_ROOT / overlay).read_bytes()
    for relative_name, append_path in mapping.get("appends", {}).items():
        relative = Path(relative_name)
        if relative not in expected:
            raise RuntimeError(f"追加目标不在上游映射中：{mapping['target']}/{relative}")
        expected[relative] = expected[relative].rstrip() + b"\n\n" + (PLUGIN_ROOT / append_path).read_bytes().lstrip()
    metadata = load_metadata()
    target_metadata = metadata.get(mapping["target"], {})
    description = target_metadata.get("description")
    if not description:
        raise RuntimeError(f"缺失集中触发描述：{mapping['target']}")
    skill_path = Path("SKILL.md")
    expected[skill_path] = replace_trigger_description(
        expected[skill_path].decode("utf-8"),
        description,
        f"{mapping['target']}/SKILL.md",
    ).encode("utf-8")
    return expected


def compare_target(target: Path, expected: dict[Path, bytes]) -> list[str]:
    errors: list[str] = []
    actual_files = {
        path.relative_to(target)
        for path in target.rglob("*")
        if path.is_file() and path.name != ".DS_Store" and path.parts[-2:] != ("agents", "openai.yaml")
    } if target.exists() else set()
    expected_files_set = set(expected)
    for missing in sorted(expected_files_set - actual_files):
        errors.append(f"缺失导入文件：{target / missing}")
    for extra in sorted(actual_files - expected_files_set):
        errors.append(f"未声明的导入文件：{target / extra}")
    for relative in sorted(actual_files & expected_files_set):
        if (target / relative).read_bytes() != expected[relative]:
            errors.append(f"上游漂移：{target / relative}")
    return errors


def write_target(target: Path, expected: dict[Path, bytes]) -> None:
    preserved_yaml = target / "agents" / "openai.yaml"
    preserved = preserved_yaml.read_bytes() if preserved_yaml.exists() else None
    if target.exists():
        shutil.rmtree(target)
    for relative, data in expected.items():
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
    if preserved is not None:
        preserved_yaml.parent.mkdir(parents=True, exist_ok=True)
        preserved_yaml.write_bytes(preserved)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="只校验，不写文件")
    parser.add_argument("--dry-run", action="store_true", help="列出固定映射与允许转换")
    args = parser.parse_args()
    config = load_config()
    upstream_root = REPO_ROOT / config["upstream_root"]
    actual_commit = upstream_head(upstream_root)
    try:
        require_upstream_commit(actual_commit, config["upstream_commit"])
    except RuntimeError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 2

    print(f"上游 Commit：{actual_commit}")
    print("允许转换：删除 Claude invocation 字段；固定品牌、Skill 名称、路径引用；集中覆盖 Load when 触发描述；Router 选集适配；封板边界与 Tracker Runtime 声明式扩展。")
    all_errors: list[str] = []
    for mapping in config["mappings"]:
        source = mapping["source"]
        target = PLUGIN_ROOT / "skills" / mapping["target"]
        changes = [f"{old}→{new}" for old, new in config["replacements"] if old in (REPO_ROOT / config["upstream_root"] / source / "SKILL.md").read_text(encoding="utf-8")]
        adaptations = []
        if mapping.get("overlay"):
            adaptations.append(f"Overlay={mapping['overlay']}")
        if mapping.get("appends"):
            adaptations.append(f"Appends={','.join(mapping['appends'])}")
        if mapping.get("file_replacements"):
            adaptations.append(
                f"FileReplacements={','.join(mapping['file_replacements'])}"
            )
        adaptations.append("TriggerDescription=config/skill-metadata.json")
        print(
            f"{source} -> skills/{mapping['target']}；"
            f"替换：{', '.join(changes) or '仅 Frontmatter 清理'}；"
            f"适配：{'; '.join(adaptations) or '无'}"
        )
        expected = expected_files(config, mapping)
        if args.dry_run:
            continue
        if args.check:
            all_errors.extend(compare_target(target, expected))
        else:
            write_target(target, expected)
    if all_errors:
        print("\n".join(f"错误：{error}" for error in all_errors), file=sys.stderr)
        return 1
    if args.check:
        print("上游漂移校验通过。")
    elif not args.dry_run:
        print("上游导入完成。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
