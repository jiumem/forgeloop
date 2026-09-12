from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


TOOLING_ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = Path(__file__).resolve().parents[3] / "plugins" / "forgeloop"
SKILL_ROOT = PLUGIN_ROOT / "skills"
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

    def test_to_tickets_declares_parent_references_before_both_templates(self) -> None:
        text = generated_skill("to-tickets")
        local_template = text[text.index("<local-ticket-template>") : text.index("</local-ticket-template>")]
        issue_template = text[text.index("<issue-template>") : text.index("</issue-template>")]

        self.assertLess(text.index("Map every Ticket to"), text.index("### 5. Publish"))
        self.assertIn("Parent Delivery Acceptance references", local_template)
        self.assertIn("Parent Delivery Acceptance references", issue_template)

    def test_run_completes_delivery_without_claiming_release_authority(self) -> None:
        skill = (SKILL_ROOT / "run-initiative" / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("`Release Boundary`", skill)
        self.assertIn("Post-delivery action", skill)
        self.assertIn("Tracking reference", skill)
        self.assertIn("Do not execute that action", skill)
        self.assertIn("create, claim, update, or close the referenced external item", skill)
        self.assertIn("release and deployment remain outside this Skill's authority", skill)

    def test_release_boundary_adds_no_runtime_schema(self) -> None:
        text = (SKILL_ROOT / "run-initiative" / "SKILL.md").read_text(encoding="utf-8")

        self.assertNotIn("Release Reviewer", text)
        self.assertNotIn("level=RELEASE", text)
        self.assertNotIn("RELEASE_RESULT", text)
        self.assertNotIn("RELEASE_PENDING", text)


if __name__ == "__main__":
    unittest.main()
