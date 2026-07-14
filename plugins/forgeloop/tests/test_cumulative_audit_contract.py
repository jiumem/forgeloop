from __future__ import annotations

import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
TO_TICKETS = PLUGIN_ROOT / "skills" / "to-tickets" / "SKILL.md"
RUN_ROOT = PLUGIN_ROOT / "skills" / "run-initiative"


class CumulativeAuditContractTests(unittest.TestCase):
    def test_to_tickets_keeps_topology_reason_and_policy_independent(self) -> None:
        text = TO_TICKETS.read_text(encoding="utf-8")

        for marker in (
            "Branch topology: `INDEPENDENT | SHARED`",
            "Shared-branch reason: `WIDE_REFACTOR | NON_GREEN_MIGRATION | ATOMIC_DELIVERY | CUMULATIVE_AUDIT`",
            "Integration policy: `auto-merge | human-merge`",
            "does not grant merge authority",
            "at least two implementation Tickets",
            "native PR/MR runtime",
            "Local runtime must not offer `CUMULATIVE_AUDIT`",
            "explicitly approves",
        ):
            self.assertIn(marker, text)

    def test_to_tickets_requires_one_high_risk_final_ticket(self) -> None:
        text = TO_TICKETS.read_text(encoding="utf-8")

        for marker in (
            "exactly one `integrate-and-verify` Ticket",
            "blocked by every delivery Ticket",
            "Scope, public validation Seam, failure semantics, and Acceptance criteria",
            "must be `HIGH_RISK`",
            "does not gain Cross-seam Invariant ownership",
        ):
            self.assertIn(marker, text)

    def test_runtime_separates_ticket_review_delivery_range_and_target_binding(self) -> None:
        skill = (RUN_ROOT / "SKILL.md").read_text(encoding="utf-8")
        protocol = (RUN_ROOT / "references" / "cumulative-audit.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("[cumulative-audit.md]", skill)
        self.assertIn("before the root Claim or any Integration Branch write", skill)
        for marker in (
            "review_base / candidate_head",
            "spec_delivery_base / delivery_head",
            "existing `RUN_CLAIMED` Payload",
            "target_before / target_after",
            "supplemental audit evidence, not Verdict inputs",
            "review_base == candidate_head == delivery_head",
            "After create or reuse, verify that the native PR/MR Head equals `delivery_head`",
            "rebinds the new reviewed `candidate_head` as `delivery_head`",
            "neither a second Reviewer type nor a second Verdict schema",
            "existing owner-referenced Proof",
            "CONTRACT_BLOCKER",
        ):
            self.assertIn(marker, protocol)

    def test_cumulative_pr_is_a_literal_safe_native_projection(self) -> None:
        protocol = (RUN_ROOT / "references" / "cumulative-audit.md").read_text(
            encoding="utf-8"
        )

        for marker in (
            "one valid native PR/MR identity",
            "audit projection, not a source of truth",
            "file or stdin transport",
            "exact native read-back",
            "dual Review `PASS` → create or reuse PR/MR → Required Checks → refresh projection → literal-safe write → exact read-back → merge",
            "READY_FOR_HUMAN_MERGE",
            "fresh Spec Acceptance",
            "must not aggregate multiple Specs into one PR/MR",
            "Local runtime",
        ):
            self.assertIn(marker, protocol)
        for forbidden in ("STACK_READY", "CUMULATIVE_READY", "CUMULATIVE_RESULT"):
            self.assertNotIn(forbidden, protocol)


if __name__ == "__main__":
    unittest.main()
