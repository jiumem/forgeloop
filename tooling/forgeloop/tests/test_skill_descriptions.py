from __future__ import annotations

import json
import unittest
from pathlib import Path

TOOLING_ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = Path(__file__).resolve().parents[3] / "plugins" / "forgeloop"
METADATA_PATH = TOOLING_ROOT / "config" / "skill-metadata.json"
SKILLS_ROOT = PLUGIN_ROOT / "skills"
SPEC_STANDARDS_REVIEW_DESCRIPTION = (
    "Review the changes since a fixed point (commit, branch, tag, or merge-base) along two axes — "
    "Standards (does the code follow this repo's documented coding standards?) and Spec (does the "
    "code match what the originating issue/spec asked for?). Runs both reviews in parallel sub-agents "
    "and reports them side by side. Use when the user wants to review a branch, a PR, "
    "work-in-progress changes, or asks to \"review since X\"."
)


def read_description(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("description:"):
            return line.removeprefix("description:").strip()
    raise AssertionError(f"缺失 description：{path}")


class SkillDescriptionTests(unittest.TestCase):
    def test_all_descriptions_are_centralized_single_line_text(self) -> None:
        metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
        paths = sorted(SKILLS_ROOT.glob("*/SKILL.md"))

        self.assertEqual(len(paths), 20)
        self.assertEqual({path.parent.name for path in paths}, set(metadata))
        for path in paths:
            name = path.parent.name
            description = read_description(path)
            self.assertEqual(description, metadata[name]["description"], name)
            self.assertTrue(description, name)
            self.assertNotIn("\n", description, name)

    def test_descriptions_are_unique(self) -> None:
        metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
        descriptions = [values["description"] for values in metadata.values()]

        self.assertEqual(len(descriptions), len(set(descriptions)))

    def test_spec_standards_review_has_one_unambiguous_model_callable_identity(self) -> None:
        metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))

        self.assertEqual(
            metadata["spec-standards-review"]["description"],
            SPEC_STANDARDS_REVIEW_DESCRIPTION,
        )
        self.assertNotIn("code-review", metadata)
        self.assertNotIn("review-change", metadata)
        self.assertTrue((SKILLS_ROOT / "spec-standards-review" / "SKILL.md").is_file())
        self.assertFalse((SKILLS_ROOT / "code-review").exists())
        self.assertFalse((SKILLS_ROOT / "review-change").exists())

    def test_active_prompt_sources_do_not_reference_removed_review_names(self) -> None:
        paths = [
            path
            for root in (SKILLS_ROOT, TOOLING_ROOT / "config" / "overlays")
            for path in root.rglob("*")
            if path.is_file() and path.suffix in {".md", ".yaml", ".yml"}
        ]
        paths.extend(
            [
                METADATA_PATH,
                TOOLING_ROOT / "config" / "upstream-map.json",
            ]
        )

        for path in paths:
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("review-change", text, str(path))
            self.assertNotIn("$code-review", text, str(path))


if __name__ == "__main__":
    unittest.main()
