#!/usr/bin/env python3
"""只读校验 Forgeloop Skill 套件结构与发布契约。"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = PLUGIN_ROOT / "config" / "skill-suite.json"
METADATA_PATH = PLUGIN_ROOT / "config" / "skill-metadata.json"


@dataclass(frozen=True)
class Skill:
    directory: str
    path: Path
    name: str
    description: str
    frontmatter_keys: tuple[str, ...]


def parse_frontmatter(path: Path) -> Skill:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("缺少 YAML Frontmatter 起始分隔符")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError("缺少 YAML Frontmatter 结束分隔符") from exc
    fields: dict[str, str] = {}
    keys: list[str] = []
    for line in lines[1:end]:
        match = re.match(r"^([a-zA-Z0-9_-]+):\s*(.*)$", line)
        if not match:
            raise ValueError(f"无法解析 Frontmatter 行：{line}")
        key, value = match.groups()
        keys.append(key)
        fields[key] = value.strip().strip('"').strip("'")
    return Skill(path.parent.name, path.parent, fields.get("name", ""), fields.get("description", ""), tuple(keys))


def discover(skills_root: Path) -> tuple[list[Skill], list[str]]:
    skills: list[Skill] = []
    errors: list[str] = []
    for directory in sorted(path for path in skills_root.iterdir() if path.is_dir() and not path.name.startswith(".")):
        skill_md = directory / "SKILL.md"
        if not skill_md.exists():
            errors.append(f"{directory.name}: 缺失 SKILL.md")
            continue
        try:
            skills.append(parse_frontmatter(skill_md))
        except (OSError, UnicodeError, ValueError) as exc:
            errors.append(f"{directory.name}: {exc}")
    return skills, errors


def validate_openai_yaml(skill: Skill, explicit_only: set[str], final_names: set[str]) -> list[str]:
    errors: list[str] = []
    yaml_path = skill.path / "agents" / "openai.yaml"
    if not yaml_path.exists():
        return [f"{skill.name}: 缺失 agents/openai.yaml"]
    text = yaml_path.read_text(encoding="utf-8")
    prompt = re.search(r'(?m)^\s*default_prompt:\s*["\'](.+)["\']\s*$', text)
    if not prompt or f"${skill.name}" not in prompt.group(1):
        errors.append(f"{skill.name}: default_prompt 必须显式包含 ${skill.name}")
    policy = re.search(r"(?m)^\s*allow_implicit_invocation:\s*(true|false)\s*$", text)
    expected = "false" if skill.name in explicit_only else "true"
    if skill.name in final_names and (not policy or policy.group(1) != expected):
        errors.append(f"{skill.name}: allow_implicit_invocation 应为 {expected}")
    short = re.search(r'(?m)^\s*short_description:\s*["\'](.+)["\']\s*$', text)
    if not short or not 25 <= len(short.group(1)) <= 64:
        errors.append(f"{skill.name}: short_description 长度必须为 25–64 字符")
    return errors


def validate_tree(
    plugin_root: Path,
    mode: str,
    config: dict,
    descriptions: dict[str, str] | None = None,
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    notices: list[str] = []
    skills_root = plugin_root / "skills"
    if not skills_root.is_dir():
        return [f"缺失标准 Skills 目录：{skills_root}"], notices
    skills, discover_errors = discover(skills_root)
    errors.extend(discover_errors)
    names = [skill.name for skill in skills]
    directories = [skill.directory for skill in skills]
    duplicates = sorted({name for name in names if names.count(name) > 1})
    if duplicates:
        errors.append(f"重复 Skill 名称：{', '.join(duplicates)}")
    for skill in skills:
        if skill.name != skill.directory:
            errors.append(f"{skill.directory}: Frontmatter name 为 {skill.name or '<空>'}")
        if skill.frontmatter_keys != ("name", "description"):
            errors.append(f"{skill.directory}: Frontmatter 只允许 name、description")
        if not skill.description:
            errors.append(f"{skill.directory}: description 为空")
        elif not skill.description.startswith("Load when "):
            errors.append(f"{skill.directory}: description 必须以 Load when 开头并只描述触发条件")
        elif descriptions is not None and skill.description != descriptions.get(skill.name):
            errors.append(f"{skill.directory}: description 与 config/skill-metadata.json 不一致")
        if len((skill.path / "SKILL.md").read_text(encoding="utf-8").splitlines()) >= 500:
            errors.append(f"{skill.directory}: SKILL.md 必须少于 500 行")
        body = (skill.path / "SKILL.md").read_text(encoding="utf-8")
        if "[TODO:" in body or "disable-model-invocation" in body:
            errors.append(f"{skill.directory}: 存在 TODO 或 Claude 专用 Invocation 字段")
        for link in re.findall(r"\[[^\]]+\]\((?!https?://|#)([^)]+\.md)\)", body):
            clean = link.split("#", 1)[0]
            if not (skill.path / clean).resolve().is_file():
                errors.append(f"{skill.directory}: 失效 Markdown 引用 {link}")
        for text_path in sorted(skill.path.rglob("*")):
            if not text_path.is_file() or text_path.suffix not in {".md", ".yaml", ".yml", ".json", ".sh", ".py", ".txt"}:
                continue
            text = text_path.read_text(encoding="utf-8")
            if re.search(r"[\u3400-\u4dbf\u4e00-\u9fff]", text):
                relative = text_path.relative_to(skill.path)
                errors.append(f"{skill.directory}/{relative}: Skill 内容必须全部使用英文")

    manifest = json.loads((plugin_root / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
    if manifest.get("skills") != "./skills/":
        errors.append("Manifest 必须发现标准 ./skills/ 目录")
    expected_version = config[mode]["version"] if mode in ("baseline", "development", "release") else None
    if mode == "installed":
        release_version = re.escape(config["release"]["version"])
        installed_version = str(manifest.get("version", ""))
        if not re.fullmatch(rf"{release_version}\+codex\.[0-9A-Za-z.-]+", installed_version):
            errors.append(
                "installed 模式只接受单一 Codex Cachebuster："
                f"{config['release']['version']}+codex.<token>；实际为 {installed_version}"
            )
    elif expected_version and manifest.get("version") != expected_version:
        errors.append(f"{mode} 模式 Manifest 版本应为 {expected_version}，实际为 {manifest.get('version')}")

    final_names = set(config["release"]["skills"])
    explicit_only = set(config["release"]["explicit_only"])
    if mode == "baseline":
        expected = set(config["baseline"]["skills"])
        if set(directories) != expected:
            errors.append(f"2.5.0 Skills 不匹配：预期 {sorted(expected)}，实际 {sorted(directories)}")
    elif mode == "development":
        missing = sorted(final_names - set(directories))
        unexpected = sorted(set(directories) - final_names - set(config["removed"]))
        notices.append(f"开发中间态：已完成目标 Skill {len(final_names & set(directories))}/20")
        if missing:
            notices.append(f"尚未完成：{', '.join(missing)}")
        if unexpected:
            errors.append(f"开发目录存在未声明 Skill：{', '.join(unexpected)}")
    elif mode in ("release", "installed"):
        if set(directories) != final_names or len(directories) != len(final_names):
            errors.append(
                f"发布模式必须恰好 {len(final_names)} 个正式 Skills；"
                f"实际 {len(directories)} 个：{', '.join(directories)}"
            )
        old_present = sorted(set(config["removed"]) & set(directories))
        if old_present:
            errors.append(f"发布目录仍有旧 Skills：{', '.join(old_present)}")

    if mode != "baseline":
        for skill in skills:
            if skill.name in final_names:
                errors.extend(validate_openai_yaml(skill, explicit_only, final_names))
    return errors, notices


def export_baseline(commit: str, destination: Path) -> None:
    archive = subprocess.run(
        ["git", "archive", commit, "plugins/forgeloop"],
        check=False,
        capture_output=True,
    )
    if archive.returncode != 0:
        raise RuntimeError(archive.stderr.decode("utf-8", errors="replace"))
    extract = subprocess.run(["tar", "-x", "-C", str(destination)], input=archive.stdout, check=False, capture_output=True)
    if extract.returncode != 0:
        raise RuntimeError(extract.stderr.decode("utf-8", errors="replace"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("baseline", "development", "release", "installed"), required=True)
    parser.add_argument("--plugin-root", type=Path, default=PLUGIN_ROOT)
    args = parser.parse_args()
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    descriptions = {
        name: values.get("description", "") for name, values in metadata.items()
    }
    plugin_root = args.plugin_root.resolve()
    errors, notices = validate_tree(plugin_root, args.mode, config, descriptions)
    for notice in notices:
        print(notice)
    if errors:
        print("\n".join(f"错误：{error}" for error in errors), file=sys.stderr)
        return 1
    print(f"套件校验通过：{args.mode}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
