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


def generated_to_tickets() -> str:
    config = SYNC.load_config()
    mapping = next(item for item in config["mappings"] if item["target"] == "to-tickets")
    return SYNC.expected_files(config, mapping)[Path("SKILL.md")].decode()


class AdversarialDesignContractTests(unittest.TestCase):
    def test_risk_screening_uses_material_properties_after_complete_drafting(self) -> None:
        text = generated_to_tickets()

        self.assertIn("### 2. Explore the relevant codebase", text)
        self.assertNotIn("### 2. Explore the codebase (optional)", text)
        self.assertIn("Complete this exploration before drafting or risk screening", text)
        self.assertIn("Ticket → STANDARD | HIGH_RISK → evidence", text)
        for risk_property in (
            "dynamic, untrusted, or extensible input",
            "concurrency, ordering, cancellation, retry, timeout, re-entry, or resource lifecycle",
            "atomicity, rollback, recovery, or finalization",
            "authority, permission, ownership, or another trust relationship",
            "versioning, compatibility, migration, or recovery of old state",
            "cross-stage identity, provenance, or evidence",
        ):
            with self.subTest(risk_property=risk_property):
                self.assertIn(risk_property, text)
        self.assertIn("correctness, failure semantics, or evidence credibility materially depends", text)
        self.assertIn("syntax, fields, dependencies, paths, project names, or technology labels", text)
        self.assertLess(text.index("every ordinary implementation Ticket"), text.index("Ticket → STANDARD"))
        self.assertLess(text.index("Ticket → STANDARD"), text.index("### 4. Quiz the user"))

    def test_high_risk_ticket_has_complete_adversarial_design_contract(self) -> None:
        text = generated_to_tickets()

        section = text[text.index("## Adversarial Design") : text.index("### 4. Quiz the user")]
        for field in (
            "Risk surface:",
            "Bounded model:",
            "Invariants:",
            "Adversarial cases:",
            "Proof:",
        ):
            with self.subTest(field=field):
                self.assertIn(field, section)
        self.assertIn("finite and falsifiable", section)
        self.assertIn("no `TBD`, placeholders, or unresolved branches", text)
        self.assertIn("directly related to the identified risk", section)

    def test_ticket_design_evidence_does_not_replace_parent_contracts(self) -> None:
        text = generated_to_tickets()

        for contract in (
            "Ticket-level adversarial design evidence, not another `Delivery Acceptance` source",
            "cite its existing Validation Entry/Proof mapping",
            "do not copy or reinterpret the parent contract",
            "change the Spec, `Delivery Acceptance`, product behavior, Scope, an ADR, or an approved public interface",
            "return `CONTRACT_BLOCKER`",
            "Approved implementation design cannot replace a missing product contract",
            "unapproved high-risk product behavior, invariant, or failure semantics",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, text)

    def test_approval_precedes_fresh_read_only_reviewers(self) -> None:
        text = generated_to_tickets()

        approval = text[text.index("### 4. Quiz the user") : text.index("### 5. Publish")]
        for contract in (
            "Show the complete Ticket bodies",
            "risk classification",
            "blocking edges",
            "Adversarial Design",
            "one fresh, isolated, read-only Design Reviewer for each approved `HIGH_RISK` Ticket",
            "parent Spec revision",
            "relevant ADRs",
            "complete Ticket draft",
            "blocking edges",
            "code evidence",
            "referenced invariants",
            "must not modify files, the Spec, ADRs, draft Tickets, or Tracker state",
            "PASS | DESIGN_GAPS | REVIEW_BLOCKED",
            "PASS only with no Findings",
            "If any Finding has `SPEC` or `ADR` impact",
            "evidence",
            "counterexample",
            "missing_decision",
            "required_proof",
            "contract_impact: NONE | SPEC | ADR",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, approval)

    def test_review_verdicts_gate_one_atomic_publication(self) -> None:
        text = generated_to_tickets()

        for contract in (
            "skip Design Reviewers for `STANDARD` Tickets",
            "discard the affected PASS and run a new Reviewer",
            "Do not create an automatic design repair loop",
            "design clarification entry point",
            "unreadable or invalid fixed input",
            "do not treat missing evidence as PASS",
            "publish the complete Ticket set in one batch",
            "Tracker writes at zero",
            "Do not publish `STANDARD` Tickets early",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, text)

    def test_change_stays_agent_native_and_outside_runtime(self) -> None:
        text = generated_to_tickets()

        self.assertIn(
            "Agent-readable design judgment and evidence, not Tracker fields, a parser, a state machine, or a workflow DSL",
            text,
        )
        runtime_text = "\n".join(
            path.read_text()
            for path in (PLUGIN_ROOT / "skills" / "run-initiative").rglob("*.md")
        )
        self.assertNotIn("Design Reviewer", runtime_text)
        self.assertNotIn("Adversarial Design", runtime_text)


if __name__ == "__main__":
    unittest.main()
