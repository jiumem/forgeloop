from __future__ import annotations

import unittest
from pathlib import Path


TOOLING_ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = Path(__file__).resolve().parents[3] / "plugins" / "forgeloop"
SKILL_ROOT = PLUGIN_ROOT / "skills" / "run-initiative"


def reference(name: str) -> str:
    return (SKILL_ROOT / "references" / name).read_text(encoding="utf-8")


class RepairCycleContractTests(unittest.TestCase):
    def test_pause_precedes_fresh_semantic_exhaustion_diagnosis(self) -> None:
        coder = reference("coder.md")
        repair = reference("repair-and-integration.md")
        scheduler = reference("scheduler.md")

        self.assertIn("## Exhaustion Diagnosis", coder)
        self.assertIn("exactly confirmed `RUN_PAUSED` with reason=`REPAIR_BUDGET`", coder)
        self.assertIn("Only after that pause is confirmed", repair)
        self.assertIn("fresh Coder for the read-only Exhaustion Diagnosis", repair)
        self.assertIn("before creating the fresh Coder", scheduler)
        self.assertIn("Candidate mutation is forbidden during diagnosis", scheduler)

    def test_semantic_fields_serve_agents_not_a_runtime_classifier(self) -> None:
        coder = reference("coder.md")
        repair = reference("repair-and-integration.md")
        scheduler = reference("scheduler.md")

        for field in (
            "prior_mechanism:",
            "falsifying_evidence:",
            "new_causal_hypothesis:",
            "observable_prediction:",
            "falsification_condition:",
            "scope_assessment:",
            "observed_progress:",
        ):
            with self.subTest(field=field):
                self.assertIn(field, coder)
        self.assertIn("not as Boolean gates or a replacement state machine", coder)
        self.assertIn("Coder owns the semantic recommendation", repair)
        self.assertIn(
            "without using a parser, regex, keyword, score, Boolean, or field-presence check",
            scheduler,
        )

    def test_renewal_keeps_work_identity_but_refreshes_agent_contexts(self) -> None:
        repair = reference("repair-and-integration.md")
        scheduler = reference("scheduler.md")
        domain = reference("domain-and-state.md")

        self.assertIn("same Ticket, Run, and Branch across cycles", repair)
        self.assertIn("fresh Coder that performed Exhaustion Diagnosis", repair)
        self.assertIn("two fresh isolated Reviewers", repair)
        self.assertIn("Child identity remains live orchestration context, not durable state", repair)
        self.assertIn("Never persist child identity as workflow state", domain)
        self.assertIn("reuse those three live contexts only within the renewed cycle", scheduler)

    def test_cycle_anchor_binds_candidate_and_review_authority(self) -> None:
        domain = reference("domain-and-state.md")
        events = reference("events-and-recovery.md")
        reviewers = reference("reviewers.md")

        for marker in (
            "ticket_revision:",
            "adr_revisions:",
            "cycle_anchor:",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, domain)
                self.assertIn(marker, reviewers)
        self.assertIn("effective Spec/Ticket/ADR revisions, `cycle_anchor`", events)
        self.assertIn("old-cycle Verdict cannot certify", domain)
        self.assertIn("Never reuse an old-cycle Verdict", reviewers)

    def test_resume_winner_is_only_a_native_mutation_fence(self) -> None:
        events = reference("events-and-recovery.md")
        scheduler = reference("scheduler.md")

        self.assertIn("Competitive Automatic Repair Resume", events)
        self.assertIn("earliest valid native record wins", events)
        self.assertIn("proves only mutation authority", events)
        self.assertIn("does not prove that the Coder's semantic recommendation was correct", events)
        self.assertIn("recheck cancellation", scheduler)
        self.assertIn("Every loser, stale attempt, old-cycle Resume", scheduler)

    def test_active_runtime_has_no_shadow_repair_state_machine(self) -> None:
        paths = (
            SKILL_ROOT / "SKILL.md",
            *(SKILL_ROOT / "references").glob("*.md"),
            TOOLING_ROOT / "scripts" / "validate_fixtures.py",
            TOOLING_ROOT / "fixtures" / "m2-runtime-matrix.json",
        )
        forbidden = (
            "repair_cycle_runtime",
            "resume_outcome",
            "coder_context",
            "reviewer_contexts",
            "EXHAUSTION_DIAGNOSIS_FIELDS",
        )

        for path in paths:
            text = path.read_text(encoding="utf-8")
            for marker in forbidden:
                self.assertNotIn(marker, text, f"{path}: unexpected shadow state {marker}")


if __name__ == "__main__":
    unittest.main()
