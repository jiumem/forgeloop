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


class FormalDesignDocumentContractTests(unittest.TestCase):
    def test_grill_with_docs_owns_a_semantically_necessary_design_document(self) -> None:
        text = generated_skill("grill-with-docs")

        for behavior in (
            "repeat or independently invent shared engineering decisions",
            "Do not require a Formal Design Document merely because the feature is large",
            "Recommend one repository-native path",
            "create or update that same document in place",
            "cannot override them",
            "directly owns creation and in-place revision",
            "preserve confirmed domain-documentation updates and any confirmed Formal Design Document revision",
        ):
            with self.subTest(behavior=behavior):
                self.assertIn(behavior, text)
        self.assertIn("Do not create a Spec, Ticket, or implementation code", text)

    def test_to_spec_references_but_does_not_author_detailed_design(self) -> None:
        text = generated_skill("to-spec")

        for behavior in (
            "optional `## Design Document` section",
            "Do not copy its detailed design into the Spec",
            "return `CONTEXT_INSUFFICIENT`",
            "keep Tracker writes at zero",
            "explicitly invoke `$grill-with-docs`",
            "Do not create or revise the document inside `$to-spec`",
            "A simple feature whose design can remain local proceeds",
        ):
            with self.subTest(behavior=behavior):
                self.assertIn(behavior, text)

    def test_to_tickets_consumes_design_and_routes_real_design_gaps(self) -> None:
        text = generated_skill("to-tickets")

        for behavior in (
            "before drafting",
            "return `DESIGN_DOCUMENT_REQUIRED`",
            "keep Tracker writes at zero",
            "create or revise the same document in place",
            "Do not distribute the missing design across Ticket bodies",
            "optional `## Design Document` section",
            "Do not copy the shared design into Ticket bodies",
            "cannot create a stronger acceptance standard",
            "Use the existing `CONTRACT_BLOCKER` path instead only when",
        ):
            with self.subTest(behavior=behavior):
                self.assertIn(behavior, text)


if __name__ == "__main__":
    unittest.main()
