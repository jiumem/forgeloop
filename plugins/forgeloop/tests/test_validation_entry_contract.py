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


def generated_to_spec() -> str:
    config = SYNC.load_config()
    mapping = next(item for item in config["mappings"] if item["target"] == "to-spec")
    return SYNC.expected_files(config, mapping)[Path("SKILL.md")].decode()


class ValidationEntryContractTests(unittest.TestCase):
    def test_testing_decisions_declares_complete_validation_entries(self) -> None:
        text = generated_to_spec()
        template = text[text.index("<spec-template>") : text.index("</spec-template>")]

        self.assertIn("### Validation Entries", template)
        for field in ("Name:", "Covers:", "Behavior:", "Evidence:"):
            self.assertIn(field, template)
        self.assertIn("at least one Validation Entry", template)

    def test_template_requires_exactly_one_prerequisite_form(self) -> None:
        text = generated_to_spec()
        template = text[text.index("<spec-template>") : text.index("</spec-template>")]

        self.assertIn("## Acceptance Prerequisites", template)
        self.assertIn("Use exactly one of these mutually exclusive forms", template)
        self.assertIn("All Validation Entries can establish their own runtime conditions", template)
        for field in ("Condition:", "Required by:", "Observation:", "Unavailable path:"):
            self.assertIn(field, template)
        self.assertLess(template.index("## Acceptance Prerequisites"), template.index("## Delivery Acceptance"))
        self.assertIn("a condition a Validation Entry cannot establish itself", text)

    def test_publication_gate_requires_exact_coverage_and_valid_references(self) -> None:
        text = generated_to_spec()
        gate = text[text.index("3. Before the first Tracker write") : text.index("After all gates pass")]

        self.assertIn("Every `Covers` reference must exactly match", gate)
        self.assertIn("Every Delivery Acceptance item must be covered", gate)
        self.assertIn("similar wording does not create a mapping", gate)
        self.assertIn("Every `Required by` name must exactly match", gate)

    def test_gate_scenarios_cover_success_failure_and_zero_writes(self) -> None:
        text = generated_to_spec()
        scenarios = {
            "self-contained": "All Validation Entries can establish their own runtime conditions",
            "declared prerequisites": "List every prerequisite with all four fields",
            "missing entry": "require at least one unique stable `Name`",
            "missing field": "Reject missing fields",
            "invalid reference": "invalid references",
            "mutually exclusive conflict": "both forms",
            "diagnostics": "listing every gap",
            "zero writes": "Every content-gate failure above leaves Tracker writes at zero",
            "single publication": "publish the validated Spec exactly once",
        }
        for scenario, contract in scenarios.items():
            with self.subTest(scenario=scenario):
                self.assertIn(contract, text)

    def test_gate_is_declarative_read_only_and_delivery_scoped(self) -> None:
        text = generated_to_spec()

        for forbidden_action in (
            "Do not establish prerequisites",
            "observe their current state",
            "execute a Validation Entry",
            "expand access",
        ):
            self.assertIn(forbidden_action, text)
        self.assertIn("Validation Entries may cover only Delivery Acceptance", text)
        self.assertIn("do not place a Post-delivery Release Action in `Covers`", text)
        self.assertIn("do not migrate or rewrite an existing Spec", text)
        self.assertIn("Agent-readable traceability, not a parser, schema, execution state", text)


if __name__ == "__main__":
    unittest.main()
