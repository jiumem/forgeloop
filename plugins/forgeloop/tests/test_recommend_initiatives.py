from __future__ import annotations

import json
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = PLUGIN_ROOT / "skills" / "recommend-initiatives" / "SKILL.md"
FIXTURE_PATH = PLUGIN_ROOT / "fixtures" / "recommend-initiatives.json"


class RecommendInitiativesTests(unittest.TestCase):
    def test_contract_supports_one_to_three_candidates(self) -> None:
        text = SKILL_PATH.read_text(encoding="utf-8")

        self.assertIn("Keep only 1–3 candidates", text)
        self.assertIn("`COMPLETE`: Return 1–3 well-supported candidates", text)
        self.assertIn("Cross-category means considering every category, not forcing category quotas", text)

    def test_partial_contract_exposes_dedup_and_recovery(self) -> None:
        text = SKILL_PATH.read_text(encoding="utf-8")

        for required in (
            "Deduplication: VERIFIED | UNVERIFIED",
            "deduplication as `UNVERIFIED`",
            "missing configuration, failed authentication, insufficient permission, or a network error",
            "completed scope",
            "recovery action",
            "safe retry point",
            "before entering a later Workflow",
        ):
            self.assertIn(required, text)

    def test_fixture_covers_primary_acceptance_paths(self) -> None:
        cases = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))["cases"]
        by_id = {case["id"]: case for case in cases}

        self.assertEqual(
            set(by_id),
            {
                "one-candidate-complete",
                "three-candidates-complete",
                "missing-product-goal",
                "tracker-unavailable",
            },
        )
        self.assertEqual(by_id["one-candidate-complete"]["expected_terminal"], "COMPLETE")
        self.assertEqual(by_id["three-candidates-complete"]["candidate_count"], 3)
        self.assertEqual(
            by_id["missing-product-goal"]["expected_product_value_confidence"],
            "LOW",
        )
        self.assertEqual(by_id["tracker-unavailable"]["expected_dedup"], "UNVERIFIED")
        self.assertTrue(
            by_id["tracker-unavailable"]["requires_recheck_before_next_workflow"]
        )


if __name__ == "__main__":
    unittest.main()
