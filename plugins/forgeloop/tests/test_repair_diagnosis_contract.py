from __future__ import annotations

import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = PLUGIN_ROOT / "skills" / "run-initiative"


def reference(name: str) -> str:
    return (SKILL_ROOT / "references" / name).read_text(encoding="utf-8")


class RepairDiagnosisContractTests(unittest.TestCase):
    def test_diagnosis_is_a_complete_read_only_coder_turn_before_repair(self) -> None:
        coder = reference("coder.md")
        repair = reference("repair-and-integration.md")

        self.assertIn("## Repair Diagnosis", coder)
        self.assertIn("separate read-only Coder turn", repair)
        self.assertIn("before authorizing any candidate code change", repair)
        for required_input in (
            "trigger evidence",
            "complete cumulative Diff",
            "Ticket Scope",
            "Spec and ADRs",
            "applicable Reviewer Findings",
            "prior diagnosis and repair history",
        ):
            with self.subTest(required_input=required_input):
                self.assertIn(required_input, coder)
        for field in (
            "classification:",
            "mechanism:",
            "evidence:",
            "repair_seam:",
            "convergence:",
            "proof:",
            "scope_check:",
        ):
            with self.subTest(field=field):
                self.assertIn(field, coder)
        self.assertIn("must not modify files, create a Commit, or change the candidate Head", coder)
        self.assertIn("diagnosis turn returns only this schema", coder)
        self.assertIn("implementation Results below do not apply", coder)

    def test_classification_routes_without_scheduler_reinterpretation(self) -> None:
        repair = reference("repair-and-integration.md")
        scheduler = reference("scheduler.md")

        for contract in (
            "`LOCAL_REPAIR`",
            "existing interface can honestly express the correct behavior",
            "one authoritative fact source",
            "`STRUCTURAL_REPAIR`",
            "converge a fact source, interface, shared Seam, or parallel implementation",
            "invoke `$codebase-design` before modifying code",
            "`CONTRACT_BLOCKER`",
            "expand Ticket Scope",
            "change the Spec, Ticket Acceptance criteria, product behavior, an ADR, or an approved public interface",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, repair)
        self.assertIn("validate that every diagnosis field is present", scheduler)
        self.assertIn("route the declared classification", scheduler)
        self.assertIn("must not classify the mechanism itself", scheduler)
        self.assertIn("must not merge, reorder, or rewrite Reviewer Findings", scheduler)

    def test_three_round_budget_is_per_cycle_and_exhaustion_stays_semantic(self) -> None:
        repair = reference("repair-and-integration.md")
        tracker = reference("tracker-operations.md")

        for contract in (
            "at most three ordinary repair rounds per `cycle_anchor`",
            "Reviewer Findings, a candidate-caused Required Check failure, or compatibility or merge-conflict resolution",
            "Diagnosis turns do not consume this budget",
            "After the third repair",
            "two fresh `PASS` Verdicts",
            "do not start a fourth repair",
            "reason=`REPAIR_BUDGET`",
            "fresh Coder for the read-only Exhaustion Diagnosis",
            "Coder owns the semantic recommendation",
            "does not parse, score, keyword-match",
            "Automatic repair has no fixed total-cycle ceiling",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, repair)
        self.assertIn(
            "one initial Coder result plus at most three ordinary repair results per repair cycle",
            tracker,
        )
        self.assertNotIn("at most two ordinary repair", tracker)

    def test_later_diagnoses_compare_history_without_unsupported_downgrade(self) -> None:
        repair = reference("repair-and-integration.md")

        for contract in (
            "second and third diagnoses",
            "whether the prior mechanism hypothesis was falsified",
            "different `finding_id` values share one mechanism",
            "`LOCAL_REPAIR` to `STRUCTURAL_REPAIR`",
            "`STRUCTURAL_REPAIR` to `CONTRACT_BLOCKER`",
            "must not downgrade `STRUCTURAL_REPAIR` to `LOCAL_REPAIR` without new evidence",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, repair)

    def test_diagnosis_is_temporary_and_persists_only_with_coder_result(self) -> None:
        coder = reference("coder.md")
        repair = reference("repair-and-integration.md")
        events = reference("events-and-recovery.md")
        checkpoint_set = events[: events.index("## Minimal Durable Record")]

        for contract in (
            "zero-write, zero-budget preflight",
            "does not create durable Tracker state",
            "interrupted before the repair result",
            "rerun the diagnosis",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, repair + events)
        self.assertNotIn("`REPAIR_DIAGNOSIS`", checkpoint_set)
        self.assertIn("diagnosis summary", coder)
        self.assertIn("every `finding_id` disposition", coder)
        self.assertIn("final Head", coder)
        self.assertIn("validation evidence", coder)
        self.assertIn("diagnosis summary", events)
        self.assertIn("finding dispositions", events)

    def test_main_loop_and_runtime_contract_share_the_diagnosis_gate(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        contract = (PLUGIN_ROOT / "config" / "runtime-contract.json").read_text(
            encoding="utf-8"
        )

        self.assertIn("independent read-only Repair Diagnosis turn", skill)
        self.assertIn("Only an authorized `LOCAL_REPAIR` or `STRUCTURAL_REPAIR`", skill)
        for marker in (
            "at most three ordinary repair rounds",
            "Repair Diagnosis",
            "zero-write, zero-budget preflight",
            "Exhaustion Diagnosis",
            "AUTO_REPAIR_RENEWAL",
            "per repair cycle",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, contract)

    def test_check_and_conflict_triggers_do_not_bypass_coder_diagnosis(self) -> None:
        repair = reference("repair-and-integration.md")

        self.assertIn(
            "send its complete evidence into Repair Diagnosis before deciding whether it is in Scope",
            repair,
        )
        self.assertIn(
            "Diagnose compatibility and conflict evidence before invoking `$resolving-merge-conflicts`",
            repair,
        )
        self.assertIn("Blocking Finding, candidate-caused failure, or unresolved compatibility or merge conflict", repair)
        self.assertNotIn("decide whether repair is allowed", repair)

    def test_repair_loop_is_the_authoritative_budget_contract(self) -> None:
        tracker = reference("tracker-operations.md")

        self.assertIn("Repair Loop is the authoritative repair-budget contract", tracker)


if __name__ == "__main__":
    unittest.main()
