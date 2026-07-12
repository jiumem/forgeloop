from __future__ import annotations

import json
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
METADATA_PATH = PLUGIN_ROOT / "config" / "skill-metadata.json"
SKILLS_ROOT = PLUGIN_ROOT / "skills"


def read_description(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("description:"):
            return line.removeprefix("description:").strip()
    raise AssertionError(f"缺失 description：{path}")


class SkillDescriptionTests(unittest.TestCase):
    def test_all_descriptions_are_centralized_trigger_sentences(self) -> None:
        metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
        paths = sorted(SKILLS_ROOT.glob("*/SKILL.md"))

        self.assertEqual(len(paths), 20)
        self.assertEqual({path.parent.name for path in paths}, set(metadata))
        for path in paths:
            name = path.parent.name
            description = read_description(path)
            self.assertEqual(description, metadata[name]["description"], name)
            self.assertTrue(description.startswith("Load when "), name)
            self.assertLessEqual(len(description), 240, name)
            self.assertNotIn("\n", description, name)

    def test_descriptions_are_unique(self) -> None:
        metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
        descriptions = [values["description"] for values in metadata.values()]

        self.assertEqual(len(descriptions), len(set(descriptions)))


if __name__ == "__main__":
    unittest.main()
