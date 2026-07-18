from __future__ import annotations

import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[3] / "plugins" / "forgeloop"
TO_TICKETS = PLUGIN_ROOT / "skills" / "to-tickets" / "SKILL.md"
RUN_ROOT = PLUGIN_ROOT / "skills" / "run-initiative"


class CumulativeAuditContractTests(unittest.TestCase):
    def test_to_tickets_keeps_topology_reason_and_policy_independent(self) -> None:
        text = TO_TICKETS.read_text(encoding="utf-8")

        for marker in (
            "Branch topology: `INDEPENDENT | SHARED`",
            "Shared-branch reason: `WIDE_REFACTOR | NON_GREEN_MIGRATION | ATOMIC_DELIVERY | CUMULATIVE_AUDIT`",
            "Integration policy: `auto-merge | human-merge`",
            "grants no merge authority",
            "at least two implementation Tickets",
            "native PR/MR runtime",
            "Local does not offer this reason",
            "Require one user approval",
        ):
            self.assertIn(marker, text)

    def test_to_tickets_uses_spec_root_without_a_ceremony_ticket(self) -> None:
        text = TO_TICKETS.read_text(encoding="utf-8")

        for marker in (
            "Final integration gate owner: SPEC_ROOT",
            "Do not draft a ceremony Ticket",
            "When the final stage has independent implementation work",
            "without gaining ownership",
        ):
            self.assertIn(marker, text)
        self.assertNotIn("integrate-and-verify", text)

    def test_runtime_separates_ticket_review_delivery_range_and_target_binding(self) -> None:
        skill = (RUN_ROOT / "SKILL.md").read_text(encoding="utf-8")
        gate = (RUN_ROOT / "references" / "final-integration-gate.md").read_text(
            encoding="utf-8"
        )
        protocol = (RUN_ROOT / "references" / "cumulative-audit.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("[final-integration-gate.md]", skill)
        self.assertIn("[cumulative-audit.md]", skill)
        self.assertIn("before the root Claim", skill)
        for marker in (
            "spec_delivery_base / delivery_head",
            "existing `RUN_CLAIMED` Payload",
            "target_before / target_after",
            "parent Validation Entries",
            "existing owner-referenced Proof",
            "CONTRACT_BLOCKER",
        ):
            self.assertIn(marker, gate + protocol)
        self.assertNotIn("integrate-and-verify", protocol)

    def test_cumulative_pr_is_a_literal_safe_native_projection(self) -> None:
        protocol = (RUN_ROOT / "references" / "cumulative-audit.md").read_text(
            encoding="utf-8"
        )
        gate = (RUN_ROOT / "references" / "final-integration-gate.md").read_text(
            encoding="utf-8"
        )

        for marker in (
            "one valid native PR/MR identity",
            "audit projection, not a source of truth",
            "file or stdin transport",
            "exact native read-back",
            "fixed `delivery_head` → create or reuse PR/MR → Required Checks → refresh projection → literal-safe write → exact read-back → merge",
            "READY_FOR_HUMAN_MERGE",
            "fresh Spec Acceptance",
            "must not aggregate multiple Specs into one PR/MR",
            "Local has no cumulative PR/MR surface",
        ):
            self.assertIn(marker, gate + protocol)
        for forbidden in ("STACK_READY", "CUMULATIVE_READY", "CUMULATIVE_RESULT"):
            self.assertNotIn(forbidden, protocol)


if __name__ == "__main__":
    unittest.main()
