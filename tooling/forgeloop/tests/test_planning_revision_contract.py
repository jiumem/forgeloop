from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


TOOLING_ROOT = Path(__file__).resolve().parents[1]
SYNC_SCRIPT = TOOLING_ROOT / "scripts" / "sync_upstream.py"
SPEC = importlib.util.spec_from_file_location("sync_upstream", SYNC_SCRIPT)
assert SPEC and SPEC.loader
SYNC = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = SYNC
SPEC.loader.exec_module(SYNC)


def generated_skill(target: str) -> str:
    config = SYNC.load_config()
    mapping = next(item for item in config["mappings"] if item["target"] == target)
    return SYNC.expected_files(config, mapping)[Path("SKILL.md")].decode()


class PlanningRevisionContractTests(unittest.TestCase):
    def test_to_tickets_hands_contract_gaps_back_to_the_existing_spec(self) -> None:
        text = generated_skill("to-tickets")

        self.assertIn("existing Spec", text)
        self.assertIn("invoke `$to-spec` explicitly", text)
        self.assertIn("must not create a replacement Spec", text)

    def test_to_spec_revises_the_same_issue_before_ticket_publication(self) -> None:
        text = generated_skill("to-spec")

        section = text[
            text.index("Planning Revision Mode") : text.index("Forgeloop Approved Revision Mode")
        ]
        for contract in (
            "same existing Spec",
            "`CONTRACT_BLOCKER`",
            "bound to the current Revision",
            "predecessor Revision",
            "exact read-back",
            "must not create a replacement Spec",
            "refresh and verify",
            "no child Ticket has been published",
            "FAILED_PRECONDITION",
            "Tracker writes at zero",
            "must not fall through to normal new-Spec publication",
            "temporary file",
            "non-interpreting",
            "RECOVERY_CONFLICT",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, section)


if __name__ == "__main__":
    unittest.main()
