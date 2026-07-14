from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = PLUGIN_ROOT / "skills"
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


class DeliveryAcceptanceContractTests(unittest.TestCase):
    def test_to_spec_gates_the_candidate_before_publication(self) -> None:
        text = generated_skill("to-spec")

        template_end = text.index("</spec-template>")
        publish = text.index("After all gates pass")
        self.assertLess(text.index("## Delivery Acceptance"), template_end)
        self.assertLess(text.index("Validate the in-memory candidate"), publish)
        self.assertIn("An ordinary Spec must omit `Release Boundary`", text[:template_end])

    def test_to_spec_publishes_one_observable_delivery_acceptance_source(self) -> None:
        text = generated_skill("to-spec")

        self.assertIn("## Delivery Acceptance", text)
        self.assertIn("stable local reference in the current Revision", text)
        self.assertIn("observable delivery outcome", text)
        self.assertIn("single source of truth", text)
        self.assertIn("`CONTEXT_INSUFFICIENT`", text)
        for invalid in ("missing", "empty", "duplicate", "`TBD`", "placeholder", "unresolved branch"):
            self.assertIn(invalid, text)

    def test_to_spec_semantically_separates_delivery_from_release_before_writes(self) -> None:
        text = generated_skill("to-spec")

        self.assertIn("Post-delivery Release Action", text)
        self.assertIn("semantic consistency", text)
        self.assertIn("all normative content", text)
        self.assertIn("Before the first Tracker write", text)
        self.assertIn("must not use keyword lists", text)
        self.assertIn("claims an external action already happened", text)
        self.assertIn("evidence only proves release readiness", text)
        self.assertIn("conflicting goal and evidence", text)

    def test_to_spec_adds_release_boundary_only_when_relevant(self) -> None:
        text = generated_skill("to-spec")

        self.assertIn("## Release Boundary", text)
        self.assertIn("Delivery completion proves:", text)
        self.assertIn("Post-delivery action:", text)
        self.assertIn("Tracking reference:", text)
        self.assertIn("ordinary Spec must omit `Release Boundary`", text)
        self.assertIn("Do not create a Release Item", text)

    def test_agent_scenarios_cover_delivery_and_release_decisions(self) -> None:
        to_spec = generated_skill("to-spec")
        run_skill = (SKILL_ROOT / "run-initiative" / "SKILL.md").read_text()
        acceptance = (SKILL_ROOT / "run-initiative" / "references" / "acceptance.md").read_text()

        expected_to_spec_scenarios = (
            "An ordinary Spec must omit `Release Boundary`",
            "Delivering release capability, a release pipeline, or release readiness is valid",
            "If a title or body claims an external action already happened",
            "evidence only proves release readiness",
            "existing external item or `None`",
            "`None` does not mean the action is covered",
        )
        for scenario in expected_to_spec_scenarios:
            self.assertIn(scenario, to_spec)
        self.assertIn("must not mutate the referenced item's Open/Closed state", acceptance)
        self.assertIn("Delivery is complete; Release was not executed by this Run", run_skill)

    def test_delivery_acceptance_is_shared_without_replacing_ticket_criteria(self) -> None:
        to_tickets = generated_skill("to-tickets")
        domain = (SKILL_ROOT / "run-initiative" / "references" / "domain-and-state.md").read_text()
        coder = (SKILL_ROOT / "run-initiative" / "references" / "coder.md").read_text()
        reviewers = (SKILL_ROOT / "run-initiative" / "references" / "reviewers.md").read_text()
        acceptance = (SKILL_ROOT / "run-initiative" / "references" / "acceptance.md").read_text()

        for text in (to_tickets, domain, coder, reviewers, acceptance):
            self.assertIn("Delivery Acceptance", text)
        self.assertIn("Ticket Acceptance criteria", to_tickets)
        self.assertIn("stable Delivery Acceptance references", to_tickets)
        self.assertNotIn("Spec Acceptance Criteria", to_tickets)

    def test_to_tickets_declares_parent_references_before_both_templates(self) -> None:
        text = generated_skill("to-tickets")
        local_template = text[text.index("<local-ticket-template>") : text.index("</local-ticket-template>")]
        issue_template = text[text.index("<issue-template>") : text.index("</issue-template>")]

        self.assertLess(text.index("Map every Ticket to"), text.index("### 5. Publish"))
        self.assertIn("Parent Delivery Acceptance references", local_template)
        self.assertIn("Parent Delivery Acceptance references", issue_template)

    def test_run_accepts_delivery_without_performing_or_claiming_release(self) -> None:
        skill = (SKILL_ROOT / "run-initiative" / "SKILL.md").read_text()
        acceptance = (SKILL_ROOT / "run-initiative" / "references" / "acceptance.md").read_text()

        self.assertIn("Delivery Acceptance", acceptance)
        self.assertIn("does not execute or validate any Post-delivery Release Action", acceptance)
        self.assertIn("must not return `REPAIR_REQUIRED`", acceptance)
        self.assertIn("Delivery is complete", skill)
        self.assertIn("Release was not executed by this Run", skill)
        self.assertIn("Tracking reference", skill)
        self.assertIn("must not create, claim, update, or close", skill)

    def test_release_tracking_reference_stays_outside_delivery_scope(self) -> None:
        domain = (SKILL_ROOT / "run-initiative" / "references" / "domain-and-state.md").read_text()
        acceptance = (SKILL_ROOT / "run-initiative" / "references" / "acceptance.md").read_text()

        for term in ("Ticket Frontier", "Spec Scope", "Initiative membership"):
            self.assertIn(term, domain)
        self.assertIn("Open/Closed state, assignee, labels, or comments", acceptance)
        self.assertIn("remain unchanged", acceptance)

    def test_initiative_invariants_are_evidence_not_a_second_acceptance_source(self) -> None:
        acceptance = (SKILL_ROOT / "run-initiative" / "references" / "acceptance.md").read_text()

        self.assertIn(
            "cross-Spec invariants only as evidence for the Delivery Acceptance items that reference them",
            acceptance,
        )
        self.assertNotIn("`Delivery Acceptance` and cross-Spec invariants", acceptance)

    def test_parent_and_ticket_acceptance_terms_are_unambiguous(self) -> None:
        to_tickets = generated_skill("to-tickets")
        coder = (SKILL_ROOT / "run-initiative" / "references" / "coder.md").read_text()

        self.assertNotIn("changing Scope, Acceptance Criteria", to_tickets)
        self.assertNotIn("Acceptance Criteria", coder)
        self.assertNotIn("every Acceptance Criterion", coder)

    def test_release_boundary_does_not_add_runtime_schema(self) -> None:
        text = "\n".join(
            path.read_text()
            for path in (SKILL_ROOT / "run-initiative").rglob("*.md")
        )

        self.assertNotIn("Release Reviewer", text)
        self.assertNotIn("level=RELEASE", text)
        self.assertNotIn("RELEASE_RESULT", text)
        self.assertNotIn("RELEASE_PENDING", text)


if __name__ == "__main__":
    unittest.main()
