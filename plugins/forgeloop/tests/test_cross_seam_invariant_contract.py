from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
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


class CrossSeamInvariantContractTests(unittest.TestCase):
    def test_spec_template_requires_explicit_invariant_contract(self) -> None:
        text = generated_skill("to-spec")
        template = text[text.index("<spec-template>") : text.index("</spec-template>")]

        self.assertIn("## Cross-seam Invariants", template)
        self.assertIn("None — no Cross-seam Invariants", template)
        for field in ("ID:", "Contract:", "Proof:"):
            self.assertIn(field, template)
        self.assertIn("exact Validation Entry name", template)
        self.assertIn("observable assertion", template)
        self.assertLess(
            template.index("## Cross-seam Invariants"),
            template.index("## Delivery Acceptance"),
        )

    def test_to_spec_rejects_invalid_or_unprovable_invariants_before_writes(self) -> None:
        text = generated_skill("to-spec")
        gate = text[text.index("3. Before the first Tracker write") : text.index("After all gates pass")]

        for contract in (
            "Require exactly one of the two invariant forms",
            "unique stable `ID`",
            "complete `Contract` and `Proof`",
            "exactly match declared Validation Entry names",
            "real public behavior seam",
            "helper, internal field, or single intermediate projection",
            "module list or test task",
            "`CONTEXT_INSUFFICIENT`",
            "listing every gap",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, gate)
        self.assertIn("Every content-gate failure above leaves Tracker writes at zero", text)

    def test_to_tickets_presents_one_owner_and_records_only_parent_references(self) -> None:
        text = generated_skill("to-tickets")
        approval = text[text.index("### 4. Quiz the user") : text.index("### 5. Publish")]

        self.assertIn("Invariant → Owning Ticket", approval)
        self.assertIn("Invariant ownership: None", approval)
        self.assertIn("exactly one Owning Ticket", text)
        self.assertIn("deliver the complete parent `Contract`", text)
        self.assertIn("cite the invariant `ID` and parent `Proof` mapping", text)
        self.assertIn("evidence from the referenced Validation Entry", text)
        self.assertIn("do not copy or reinterpret the parent Contract", text)
        self.assertIn("Owned Cross-seam Invariants", text)
        for template_tag in ("local-ticket-template", "issue-template"):
            template = text[
                text.index(f"<{template_tag}>") : text.index(f"</{template_tag}>")
            ]
            self.assertIn("Owned Cross-seam Invariants", template)
            self.assertIn("parent Contract and Proof", template)

    def test_to_tickets_blocks_invalid_ownership_with_zero_writes(self) -> None:
        text = generated_skill("to-tickets")

        for contract in (
            "no Contributing Tickets, shared ownership, or special invariant Ticket type",
            "reshape the slices or add an ordinary vertical Ticket",
            "Never create a Ticket that only adds an integration test",
            "With no owner, multiple owners, or proof only through a helper or internal seam",
            "return `CONTRACT_BLOCKER`",
            "do not invent or write back the contract",
            "gains no ownership",
            "Every invariant gate runs before the first Tracker write",
            "create no Ticket, change no Tracker state, and add no `ready-for-agent` label",
            "Agent-readable planning traceability, not Tracker state, a parser, or a workflow",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, text)


if __name__ == "__main__":
    unittest.main()
