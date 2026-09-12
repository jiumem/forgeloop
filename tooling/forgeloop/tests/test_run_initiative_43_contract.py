from __future__ import annotations

import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
PLUGIN_ROOT = REPO_ROOT / "plugins" / "forgeloop"
RUN_ROOT = PLUGIN_ROOT / "skills" / "run-initiative"
RUN_SKILL = RUN_ROOT / "SKILL.md"
REVIEW_SKILL = PLUGIN_ROOT / "skills" / "spec-standards-review" / "SKILL.md"
METADATA = REPO_ROOT / "tooling" / "forgeloop" / "config" / "skill-metadata.json"


def section(text: str, start: str, end: str) -> str:
    return text[text.index(start) : text.index(end)]


class RunInitiative43ContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.run = RUN_SKILL.read_text(encoding="utf-8")

    def test_runtime_contains_no_legacy_reference_protocols(self) -> None:
        references = RUN_ROOT / "references"
        self.assertFalse(references.exists() and any(references.iterdir()))
        self.assertNotIn("legacy files under `references/`", self.run)
        self.assertNotIn("](references/", self.run)

    def test_one_primary_worker_owns_delivery_without_coder_child(self) -> None:
        intro = section(self.run, "# Run an Initiative", "## Supported delivery shapes")

        self.assertIn("one primary **Delivery Worker**", intro)
        self.assertIn("Do not create a separate Supervisor or Coder child Agent", intro)
        self.assertIn("two isolated, read-only Reviewers only once per delivery branch", intro)

    def test_large_ticket_is_one_branch_with_slice_commits_and_one_pr(self) -> None:
        large_ticket = section(self.run, "### Large Ticket", "### Spec")

        for contract in (
            "one branch for the whole Ticket",
            "plans the Slices",
            "each Slice corresponds to one complete logical Commit",
            "one dual-axis Review",
            "one final Gate phase",
            "one PR for the whole Ticket",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, large_ticket)

    def test_spec_uses_tickets_as_slices_on_one_branch(self) -> None:
        spec = section(self.run, "### Spec", "### Bounded Initiative")

        for contract in (
            "one branch for the whole Spec",
            "Tickets as implementation Slices",
            "each Ticket corresponds to one complete logical Commit",
            "Do not create a branch, Review, Gate, PR, repair cycle, or integration result per Ticket",
            "one PR for the complete Spec",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, spec)

    def test_bounded_initiative_reuses_one_reviewer_pair_across_spec_prs(self) -> None:
        initiative = section(self.run, "### Bounded Initiative", "## Entry and preflight")

        for contract in (
            "one branch and one PR per Spec",
            "Reuse those same two Reviewer threads for every later Spec",
            "Rebind both Reviewers to the current Spec, Base, Head, branch, contract, and Diff",
            "Initiative goal",
            "approved cross-Spec invariants",
            "Do not use it to combine multiple Initiatives",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, initiative)

    def test_small_ticket_is_routed_to_direct_implementation(self) -> None:
        large_ticket = section(self.run, "### Large Ticket", "### Spec")

        self.assertIn("small, direct change", large_ticket)
        self.assertIn("do not use this Skill", large_ticket)
        self.assertIn("Recommend direct implementation instead", large_ticket)

    def test_slice_phase_has_no_formal_gate_but_allows_narrow_feedback(self) -> None:
        implementation = section(self.run, "## Implement quickly", "## One-time dual-axis Review")

        self.assertIn("do not run the dual-axis Review, the complete repository Gate, CI", implementation)
        self.assertIn("narrow, fast local checks", implementation)
        self.assertIn("not delivery Gates", implementation)
        self.assertIn("`NO_CHANGE_REQUIRED`", implementation)
        self.assertIn("without creating an empty Commit", implementation)

    def test_review_is_one_comprehensive_selective_audit_not_a_verdict_loop(self) -> None:
        review = section(self.run, "## One-time dual-axis Review", "## Adjudicate Findings once")

        for contract in (
            "Collect both reports once",
            "Do not ask either Reviewer to reconsider",
            "plain comment on the selected Tracker delivery item",
            "comprehensive inspection but selective reporting",
            "A clean report is valid",
            "Reviewer output is evidence, not authority",
            "does not produce `PASS`, `REPAIR_REQUIRED`",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, review)

    def test_worker_disposes_every_finding_once_and_never_reopens_review(self) -> None:
        disposition = section(self.run, "## Adjudicate Findings once", "## Final Gate and PR")

        for contract in (
            "`FIXED`",
            "`REJECTED`",
            "`CONTRACT_BLOCKER`",
            "second plain comment",
            "Never run a second Review",
            "`REPLAN_REQUIRED`",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, disposition)

    def test_final_gate_precedes_the_single_delivery_pr(self) -> None:
        final_gate = section(self.run, "## Final Gate and PR", "## Recovery and cancellation")

        self.assertLess(final_gate.index("Run the complete repository-required Gate"), final_gate.index("Create one PR"))
        self.assertIn("Candidate-caused PR failures return directly to the Delivery Worker", final_gate)
        self.assertIn("they never reopen Review", final_gate)
        self.assertIn("Follow the repository's Integration Policy", final_gate)

    def test_recovery_uses_existing_facts_and_has_distinct_outcomes(self) -> None:
        recovery = section(self.run, "## Recovery and cancellation", "## Non-goals")

        self.assertIn("persisted Review and disposition comments", recovery)
        self.assertIn("without contacting the Reviewers", self.run)
        for outcome in (
            "`COMPLETED`",
            "`REPLAN_REQUIRED`",
            "`CONTRACT_BLOCKER`",
            "`BLOCKED`",
            "`CANCELLED`",
            "`FAILED_PRECONDITION`",
        ):
            with self.subTest(outcome=outcome):
                self.assertIn(outcome, recovery)

    def test_review_skill_inspects_comprehensively_and_reports_selectively(self) -> None:
        review = REVIEW_SKILL.read_text(encoding="utf-8")

        self.assertIn("Inspect comprehensively and report selectively", review)
        self.assertIn("Comprehensive inspection", review)
        self.assertIn("High-value findings", review)
        self.assertIn("A clean report is a valid result", review)
        self.assertNotIn("Under 400 words", review)

    def test_public_metadata_describes_the_43_delivery_model(self) -> None:
        metadata = json.loads(METADATA.read_text(encoding="utf-8"))["run-initiative"]

        self.assertIn("large spec-level Ticket", metadata["description"])
        self.assertIn("bounded Initiative", metadata["description"])
        self.assertIn("delivery branch", metadata["short_description"])
        self.assertIn("Delivery Worker", metadata["default_prompt"])


if __name__ == "__main__":
    unittest.main()
