from __future__ import annotations

import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[3] / "plugins" / "forgeloop"
SKILL_ROOT = PLUGIN_ROOT / "skills" / "run-initiative"


def skill() -> str:
    return (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")


def reference(name: str) -> str:
    return (SKILL_ROOT / "references" / name).read_text(encoding="utf-8")


class AcceptanceSealGateContractTests(unittest.TestCase):
    def test_final_acceptance_is_a_scheduler_owned_seal_not_a_reviewer(self) -> None:
        acceptance = reference("acceptance.md")
        scheduler = reference("scheduler.md")
        repair = reference("repair-and-integration.md")

        self.assertIn("Scheduler owns Seal Eligibility", acceptance)
        self.assertIn("does not judge product correctness", acceptance + scheduler)
        self.assertIn("existing semantic evidence", acceptance)
        self.assertNotIn("Acceptance Reviewer", acceptance + scheduler + repair)
        self.assertNotIn("Final Acceptance creates", acceptance + scheduler + repair)
        self.assertNotIn("verdict: PASS | REPAIR_REQUIRED | ACCEPTANCE_BLOCKED", acceptance)

    def test_acceptance_cannot_create_findings_or_repair_work(self) -> None:
        acceptance = reference("acceptance.md")
        events = reference("events-and-recovery.md")
        main = skill()

        for forbidden in (
            "## Acceptance Repair Boundary",
            "reason=`ACCEPTANCE_REPAIR`",
            "PAUSED_FOR_ACCEPTANCE_REPAIR",
            "repair_key",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, acceptance + main)
        self.assertIn("cannot create a new implementation Finding", acceptance)

        acceptance_payload = next(
            line for line in events.splitlines() if line.startswith("- Acceptance:")
        )
        self.assertNotIn("Findings", acceptance_payload)
        self.assertNotIn("repair key", acceptance_payload)
        for binding in (
            "level",
            "parent revision",
            "applicable confirmed membership",
            "final target Commit",
            "integration references",
            "evidence references",
            "limitations",
            "idempotency key",
        ):
            with self.subTest(binding=binding):
                self.assertIn(binding, acceptance_payload)

    def test_every_acceptance_blocker_has_an_existing_owner_action(self) -> None:
        acceptance = reference("acceptance.md")

        for contract in (
            "checkpoint publication or read-back",
            "retry the same literal-safe write",
            "target drift",
            "return to the applicable Integration or Final Integration Gate",
            "Spec Revision or confirmed membership drift",
            "Spec Change or Contract Reconciliation",
            "Delivery Acceptance or Cross-seam Proof lacks an Owning Ticket",
            "upstream planning contract is incomplete",
            "Integration Result is missing",
            "return to that Ticket's integration path",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, acceptance)

    def test_seal_preserves_completion_and_recovery_bindings(self) -> None:
        acceptance = reference("acceptance.md")
        events = reference("events-and-recovery.md")

        for contract in (
            "ACCEPTANCE_RESULT",
            "Acceptance Seal",
            "exact native read-back",
            "final target Commit",
            "same final Commit",
            "close the member Specs",
            "close the Initiative parent last",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, acceptance + events)

    def test_final_gate_is_the_last_implementation_finding_owner(self) -> None:
        final_gate = reference("final-integration-gate.md")
        acceptance = reference("acceptance.md")

        self.assertIn(
            "last workflow stage permitted to produce an implementation Finding",
            final_gate,
        )
        self.assertIn("FINAL_GATE_FINDING", final_gate)
        self.assertIn("hand Seal Eligibility to the Scheduler", final_gate)
        self.assertNotIn("Run fresh Spec Acceptance", final_gate)
        self.assertNotIn("finding_id:", acceptance)

    def test_main_and_cumulative_flow_enter_seal_without_fresh_acceptance(self) -> None:
        main = skill()
        cumulative = reference("cumulative-audit.md")
        domain = reference("domain-and-state.md")

        self.assertIn("evaluate Spec Seal Eligibility", main)
        self.assertIn("evaluate Initiative Seal Eligibility", main)
        self.assertIn("evaluate Spec Seal Eligibility", cumulative)
        self.assertIn("Seal Eligibility", domain)
        self.assertNotIn("fresh Spec Acceptance", main + cumulative + domain)
        self.assertNotIn("fresh Initiative Acceptance", main)

    def test_to_tickets_repair_mode_accepts_only_final_gate_findings(self) -> None:
        tickets = (PLUGIN_ROOT / "skills" / "to-tickets" / "SKILL.md").read_text(
            encoding="utf-8"
        )

        repair_mode = tickets.split("## Forgeloop Final Gate Repair Mode", 1)[1]
        self.assertIn("Final Gate Finding", repair_mode)
        self.assertNotIn("Acceptance Finding", repair_mode)
        self.assertNotIn("`ACCEPTANCE_RESULT` with `REPAIR_REQUIRED`", repair_mode)
        self.assertNotIn("Spec Acceptance", repair_mode)
        self.assertNotIn("Initiative Acceptance", repair_mode)


if __name__ == "__main__":
    unittest.main()
