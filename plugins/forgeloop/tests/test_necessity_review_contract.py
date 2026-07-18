from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SYNC_SCRIPT = PLUGIN_ROOT / "scripts" / "sync_upstream.py"
SPEC = importlib.util.spec_from_file_location("sync_upstream", SYNC_SCRIPT)
assert SPEC and SPEC.loader
SYNC = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = SYNC
SPEC.loader.exec_module(SYNC)


def generated_skill(target: str) -> str:
    config = SYNC.load_config()
    mapping = next(item for item in config["mappings"] if item["target"] == target)
    return SYNC.expected_files(config, mapping)[Path("SKILL.md")].decode()


class NecessityReviewContractTests(unittest.TestCase):
    def test_to_spec_reviews_solution_necessity_before_publication(self) -> None:
        text = generated_skill("to-spec")

        review = text.index("semantic Necessity Review")
        publish = text.index("After all gates pass")
        self.assertLess(review, publish)
        for behavior in (
            "current user blockage or formal contract gap",
            "smallest authoritative production Seam",
            "existing facts, owners, interfaces, and lifecycles",
            "every new concept",
            "smaller complete alternative",
            "old-mechanism exit proof",
            "candidate Scope",
        ):
            with self.subTest(behavior=behavior):
                self.assertIn(behavior, text[review:publish])
        self.assertIn("Do not add a mandatory Necessity section", text[review:publish])
        self.assertIn("keyword, field-presence, score, or Boolean check", text[review:publish])

    def test_to_tickets_keeps_only_a_thin_minimality_gate(self) -> None:
        text = generated_skill("to-tickets")

        gate = text.index("Ticket Minimality")
        quiz = text.index("### 4. Quiz the user")
        self.assertLess(gate, quiz)
        for behavior in (
            "one to three",
            "current observable user or system result",
            "future-only infrastructure Ticket",
            "more than three Tickets",
            "every extra Ticket",
            "strong default, not a hard limit",
            "do not reopen the approved solution design",
            "return `CONTRACT_BLOCKER`",
        ):
            with self.subTest(behavior=behavior):
                self.assertIn(behavior, text[gate:quiz])

    def test_to_spec_template_does_not_reinflate_reviewed_scope(self) -> None:
        text = generated_skill("to-spec")

        self.assertNotIn("extremely extensive and cover all aspects", text)
        self.assertIn("current approved problem", text)
        self.assertIn("Do not invent future actors, variants, or capabilities", text)
        self.assertIn("Record only implementation decisions supported", text)

    def test_to_spec_restarts_all_publication_gates_after_simplification(self) -> None:
        text = generated_skill("to-spec")

        review = text.index("semantic Necessity Review")
        publish = text.index("After all gates pass")
        gate_program = text[review:publish]
        for behavior in (
            "restart the complete candidate publication gates",
            "user-approved test Seam",
            "`Delivery Acceptance`",
            "`Validation Entries`",
            "`Acceptance Prerequisites`",
            "`Cross-seam Invariants`",
            "Do not reuse an earlier gate result",
        ):
            with self.subTest(behavior=behavior):
                self.assertIn(behavior, gate_program)
        self.assertIn("return `CONTEXT_INSUFFICIENT`", gate_program)

    def test_to_tickets_keeps_prefactoring_with_its_current_consumer(self) -> None:
        text = generated_skill("to-tickets")

        self.assertNotIn("Any prefactoring should be done first", text)
        self.assertIn(
            "Keep necessary prefactoring inside the first vertical Ticket that consumes it",
            text,
        )
        self.assertIn(
            "independently provides a currently required and observable system guarantee",
            text,
        )
        self.assertEqual(
            text.count(
                "Keep necessary prefactoring inside the first vertical Ticket that consumes it"
            ),
            1,
        )
        self.assertIn(
            "Apply Ticket Minimality to necessary prefactoring; do not add a separate prefactoring step",
            text,
        )


if __name__ == "__main__":
    unittest.main()
