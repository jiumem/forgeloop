from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_suite.py"
SPEC = importlib.util.spec_from_file_location("validate_suite", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class SuiteValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "skills").mkdir()
        (self.root / ".codex-plugin").mkdir()
        (self.root / ".codex-plugin" / "plugin.json").write_text(
            json.dumps({"version": "3.0.0", "skills": "./skills/"}), encoding="utf-8"
        )
        self.config = {
            "baseline": {"version": "2.5.0", "skills": []},
            "development": {"version": "3.0.0-dev.0"},
            "release": {"version": "3.0.0", "skills": ["alpha"], "explicit_only": ["alpha"]},
            "removed": [],
        }

    def tearDown(self) -> None:
        self.temp.cleanup()

    def add_skill(self, directory: str = "alpha", name: str = "alpha", yaml: bool = True) -> Path:
        root = self.root / "skills" / directory
        root.mkdir(parents=True)
        (root / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: 完整能力说明与明确触发条件。\n---\n\n# Test\n", encoding="utf-8"
        )
        if yaml:
            (root / "agents").mkdir()
            (root / "agents" / "openai.yaml").write_text(
                f'interface:\n  display_name: "Alpha"\n  short_description: "Validate a complete skill suite fixture"\n  default_prompt: "Use ${name} for this task."\npolicy:\n  allow_implicit_invocation: false\n',
                encoding="utf-8",
            )
        return root

    def test_release_positive_fixture(self) -> None:
        self.add_skill()
        errors, _ = MODULE.validate_tree(self.root, "release", self.config)
        self.assertEqual(errors, [])

    def test_missing_skill_md_is_reported(self) -> None:
        (self.root / "skills" / "alpha").mkdir()
        errors, _ = MODULE.validate_tree(self.root, "release", self.config)
        self.assertTrue(any("缺失 SKILL.md" in error for error in errors))

    def test_directory_name_mismatch_is_reported(self) -> None:
        self.add_skill(name="beta")
        errors, _ = MODULE.validate_tree(self.root, "release", self.config)
        self.assertTrue(any("Frontmatter name" in error for error in errors))

    def test_invocation_policy_is_reported(self) -> None:
        root = self.add_skill()
        yaml_path = root / "agents" / "openai.yaml"
        yaml_path.write_text(yaml_path.read_text(encoding="utf-8").replace("false", "true"), encoding="utf-8")
        errors, _ = MODULE.validate_tree(self.root, "release", self.config)
        self.assertTrue(any("allow_implicit_invocation" in error for error in errors))

    def test_duplicate_name_is_reported(self) -> None:
        self.add_skill()
        self.add_skill(directory="beta", name="alpha")
        errors, _ = MODULE.validate_tree(self.root, "release", self.config)
        self.assertTrue(any("重复 Skill 名称" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
