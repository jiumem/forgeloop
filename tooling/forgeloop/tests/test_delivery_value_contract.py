from __future__ import annotations

import json
import unittest
from pathlib import Path


TOOLING_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]
PLUGIN_ROOT = Path(__file__).resolve().parents[3] / "plugins" / "forgeloop"
SKILL_ROOT = PLUGIN_ROOT / "skills" / "run-initiative"
REFERENCE_ROOT = SKILL_ROOT / "references"
RUNTIME_CONTRACT = TOOLING_ROOT / "config" / "runtime-contract.json"


def reference(name: str) -> str:
    return (REFERENCE_ROOT / name).read_text(encoding="utf-8")


class DeliveryValueContractTests(unittest.TestCase):
    def test_one_shared_judgment_contract_is_loaded_for_coder_and_reviewers(self) -> None:
        main = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        scheduler = reference("scheduler.md")
        judgment = reference("delivery-judgment.md")
        contract = json.loads(RUNTIME_CONTRACT.read_text(encoding="utf-8"))

        self.assertIn("delivery-judgment.md", main)
        self.assertIn("include it unchanged", main)
        self.assertIn("Delivery Judgment Contract", scheduler)
        self.assertIn("Delivery Judgment Contract", judgment)
        self.assertIn("references/delivery-judgment.md", contract)

    def test_judgment_is_lexicographic_and_minimizes_semantic_disturbance(self) -> None:
        judgment = reference("delivery-judgment.md")

        for marker in (
            "Correctness is a hard constraint",
            "Evidence credibility",
            "minimum semantic disturbance",
            "new domain concept",
            "new source of truth",
            "new state or transition",
            "new interface",
            "new lifecycle",
            "new failure mode",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, judgment)

    def test_undeclared_guarantees_are_distinguished_from_necessary_consequences(self) -> None:
        judgment = reference("delivery-judgment.md")

        for marker in (
            "Do not infer a stronger product guarantee",
            "necessary consequence",
            "approved operating and failure model",
            "explicit repository standard",
            "security boundary",
            "legal requirement",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, judgment)

    def test_spec_reviewer_searches_broadly_but_blocks_only_on_a_complete_necessity_chain(self) -> None:
        reviewers = reference("reviewers.md")

        for marker in (
            "Start from a falsifiable `PASS` hypothesis",
            "Search broadly but block narrowly",
            "necessity chain",
            "approved observable outcome",
            "necessary invariant",
            "reachable counterexample",
            "observable Candidate failure",
            "citation alone is not authority",
            "No Finding is a valid review result",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, reviewers)

    def test_coder_treats_spec_findings_as_claims_before_diagnosing_repairs(self) -> None:
        coder = reference("coder.md")

        for marker in (
            "Finding is a falsifiable claim",
            "before diagnosing a repair mechanism",
            "breaks the necessity chain",
            "prefer `NO_REPAIR`",
            "does not weaken an approved outcome",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, coder)

    def test_no_repair_reconsideration_requires_the_same_complete_chain(self) -> None:
        scheduler = reference("scheduler.md")
        repair = reference("repair-and-integration.md")

        self.assertIn("rebuild the same `finding_id` as a complete necessity chain", scheduler)
        self.assertIn("a new citation alone cannot maintain the Finding", scheduler)
        self.assertIn("authority-and-necessity-bound Findings", scheduler)
        self.assertIn("verifies authority and the complete necessity chain", repair)
        self.assertIn("smallest complete repair by semantic disturbance", repair)

    def test_judgment_adds_no_runtime_state_or_role(self) -> None:
        judgment = reference("delivery-judgment.md")

        self.assertIn("not a new role", judgment)
        self.assertIn("not a Verdict", judgment)
        self.assertIn("not an Event", judgment)
        self.assertIn("not Tracker state", judgment)
        self.assertNotIn("ADJUDICATION_RESULT", judgment)

    def test_repository_docs_explain_the_shared_value_function(self) -> None:
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        manual = (REPO_ROOT / "README.zh-CN.md").read_text(encoding="utf-8")
        release = (REPO_ROOT / "docs" / "releases" / "4.0.0-release-notes.md").read_text(
            encoding="utf-8"
        )

        for marker in (
            "统一交付价值函数",
            "正确性与证据可信度是硬约束",
            "最小语义扰动",
            "必要性链条",
            "广泛检查、克制阻塞",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, readme + manual + release)


if __name__ == "__main__":
    unittest.main()
