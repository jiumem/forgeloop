from __future__ import annotations

import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
TO_TICKETS = PLUGIN_ROOT / "skills" / "to-tickets" / "SKILL.md"
RUN_ROOT = PLUGIN_ROOT / "skills" / "run-initiative"
FINAL_GATE = RUN_ROOT / "references" / "final-integration-gate.md"
REPAIR = RUN_ROOT / "references" / "repair-and-integration.md"
EVENTS = RUN_ROOT / "references" / "events-and-recovery.md"


class FinalIntegrationGateContractTests(unittest.TestCase):
    def test_shared_delivery_is_owned_by_the_spec_root(self) -> None:
        text = TO_TICKETS.read_text(encoding="utf-8")

        self.assertIn("Final integration gate owner: SPEC_ROOT", text)
        self.assertIn(
            "Shared-branch reason: <WIDE_REFACTOR | NON_GREEN_MIGRATION | ATOMIC_DELIVERY | CUMULATIVE_AUDIT>",
            text,
        )
        self.assertIn("Final delivery surface: <configured target integration>", text)
        self.assertNotIn("Shared-branch reason: CUMULATIVE_AUDIT\n", text)
        self.assertIn("When the final stage has independent implementation work", text)
        self.assertNotIn("Final integration owner:", text)
        self.assertNotIn("integrate-and-verify", text)

    def test_every_shared_run_loads_one_final_gate_before_the_root_claim(self) -> None:
        skill = (RUN_ROOT / "SKILL.md").read_text(encoding="utf-8")
        protocol = FINAL_GATE.read_text(encoding="utf-8")

        self.assertIn("[final-integration-gate.md]", skill)
        self.assertIn("For any declared `SHARED` topology", skill)
        self.assertIn("before the root Claim", skill)
        for marker in (
            "Final integration gate owner: SPEC_ROOT",
            "every ordinary Ticket is Closed",
            "verifiable Ticket `INTEGRATION_RESULT`",
            "spec_delivery_base...delivery_head",
            "one valid native PR/MR identity",
            "Required Checks",
            "file or stdin transport",
            "exact native read-back",
            "subject_ref=<spec-ref>",
            "target_after",
            "fresh Spec Acceptance",
            "adds no Event, state, Reviewer type, Acceptance level, parser, or fact source",
        ):
            self.assertIn(marker, protocol)

        create_pr = protocol.index("creates or reuses the one valid native PR/MR identity")
        read_checks = protocol.index("read Required Checks")
        merge = protocol.index("integrate through the configured Integration Policy")
        acceptance = protocol.index("Run fresh Spec Acceptance")
        self.assertLess(create_pr, read_checks)
        self.assertLess(read_checks, merge)
        self.assertLess(merge, acceptance)

    def test_final_gate_finding_has_a_deterministic_pause_contract(self) -> None:
        protocol = FINAL_GATE.read_text(encoding="utf-8")

        self.assertIn("reason=FINAL_GATE_FINDING", protocol)
        self.assertIn(
            "repair_key=final-gate:<spec-ref>:<spec-revision>:<finding_id>",
            protocol,
        )

    def test_delivery_head_retains_ordinary_ticket_review_bindings(self) -> None:
        protocol = FINAL_GATE.read_text(encoding="utf-8")

        self.assertIn("`delivery_head` equals the latest Ticket Integration Result's `target_after`", protocol)
        self.assertIn("every mapped Candidate Head has two bound `PASS` Verdicts", protocol)
        self.assertIn("adds no final Reviewer or Spec-level `REVIEW_RESULT`", protocol)

    def test_shared_human_merge_keeps_the_spec_open_without_a_ticket(self) -> None:
        protocol = FINAL_GATE.read_text(encoding="utf-8")
        integration = REPAIR.read_text(encoding="utf-8")

        marker = "keep the Spec Open with no current Ticket"
        self.assertIn(marker, protocol)
        self.assertIn(marker, integration)

    def test_reconciliation_removes_legacy_ceremony_relationships(self) -> None:
        text = TO_TICKETS.read_text(encoding="utf-8")

        self.assertIn("unfinished ceremony-only Ticket", text)
        self.assertIn("remove its native parent relation and blocking edges", text)
        self.assertIn("only after explicit user approval", text)

    def test_final_gate_findings_use_the_existing_repair_entry(self) -> None:
        text = TO_TICKETS.read_text(encoding="utf-8")

        for marker in (
            "Final Gate Finding",
            "formal `RUN_PAUSED`",
            "stable `repair_key`",
            "user explicitly invokes `$to-tickets`",
            "source_ticket_ref",
            "completed Tickets, and their Checkpoints unchanged",
        ):
            self.assertIn(marker, text)
        self.assertNotIn("reopen the completed Ticket", text)

    def test_shared_ticket_completion_hands_delivery_to_the_spec_gate(self) -> None:
        skill = (RUN_ROOT / "SKILL.md").read_text(encoding="utf-8")
        repair = REPAIR.read_text(encoding="utf-8")
        events = EVENTS.read_text(encoding="utf-8")

        self.assertIn("For a SHARED Spec, close an ordinary Ticket after it enters the Integration Branch", skill)
        self.assertIn("let the Spec Root Final Integration Gate deliver", skill)
        self.assertIn("Final integration gate owner: SPEC_ROOT", repair)
        self.assertIn("[final-integration-gate.md]", repair)
        self.assertIn("an ordinary Ticket completes after its reviewed Candidate enters the declared Integration Branch", repair)
        self.assertNotIn("integrate-and-verify", repair)
        self.assertIn("Spec Final Integration Gate", events)
        self.assertIn("spec_delivery_base, delivery_head", events)


if __name__ == "__main__":
    unittest.main()
