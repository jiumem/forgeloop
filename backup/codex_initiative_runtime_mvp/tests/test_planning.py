import unittest
from pathlib import Path

from codex_initiative_runtime.initiative_runtime import planning_preflight
from codex_initiative_runtime.planning_parser import parse_initiative_doc


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "initiatives" / "INIT-001.md"


class PlanningTests(unittest.TestCase):
    def test_preflight_passes_for_sample_doc(self):
        result = planning_preflight(DOC, REPO_ROOT)
        self.assertTrue(result["passed"], result)

    def test_parse_initiative_doc(self):
        plan = parse_initiative_doc(DOC)
        self.assertEqual(plan.key, "INIT-001")
        self.assertIn("M1", plan.milestones)
        self.assertIn("T001", plan.tasks)
        self.assertEqual(plan.tasks["T001"].milestone, "M1")


if __name__ == "__main__":
    unittest.main()
