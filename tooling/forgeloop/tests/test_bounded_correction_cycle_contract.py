from __future__ import annotations

import unittest
from pathlib import Path


TOOLING_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]
PLUGIN_ROOT = Path(__file__).resolve().parents[3] / "plugins" / "forgeloop"
SKILL_ROOT = PLUGIN_ROOT / "skills" / "run-initiative"


def skill() -> str:
    return (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")


def reference(name: str) -> str:
    return (SKILL_ROOT / "references" / name).read_text(encoding="utf-8")


class BoundedCorrectionCycleContractTests(unittest.TestCase):
    def test_only_spec_axis_gets_contract_bounded_scope_control(self) -> None:
        reviewers = reference("reviewers.md")

        spec_axis = reviewers[reviewers.index("**Spec Reviewer**") : reviewers.index("**Standards Reviewer**")]
        standards_axis = reviewers[reviewers.index("**Standards Reviewer**") : reviewers.index("## Read-Only Boundary")]
        for contract in (
            "exact Ticket Acceptance criterion",
            "reachable inside the approved product and deployment model",
            "new deployment topology",
            "A concrete repair mechanism is non-binding",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, spec_axis)
        self.assertIn("Fowler Smell as Advisory", standards_axis)
        self.assertNotIn("new deployment topology", standards_axis)

    def test_coder_owns_no_repair_diagnosis_and_scheduler_only_routes_it(self) -> None:
        coder = reference("coder.md")
        scheduler = reference("scheduler.md")
        repair = reference("repair-and-integration.md")

        self.assertIn(
            "classification: NO_REPAIR | LOCAL_REPAIR | STRUCTURAL_REPAIR | CONTRACT_BLOCKER",
            coder,
        )
        self.assertIn("Do not accept the Reviewer's proposed mechanism", coder)
        self.assertIn("smallest complete repair", coder)
        self.assertIn("`NO_REPAIR`", repair)
        self.assertIn("same Spec Reviewer", scheduler)
        self.assertIn("one evidence-only reconsideration", scheduler)
        self.assertIn("does not involve the Standards Reviewer", scheduler)
        self.assertIn("consumes no repair round", scheduler)
        self.assertIn("must not judge the technical merits", scheduler)

    def test_no_repair_is_spec_axis_only_and_cannot_misroute_standards_findings(self) -> None:
        coder = reference("coder.md")
        scheduler = reference("scheduler.md")

        self.assertIn("`NO_REPAIR` is legal only for Spec-axis Findings", coder)
        self.assertIn("Standards-axis Finding", coder)
        self.assertIn("must never be sent to the Spec Reviewer", scheduler)
        self.assertIn(
            "all remaining Blocking Findings are Spec-axis Findings",
            coder + scheduler,
        )

    def test_one_ordinary_and_one_correction_cycle_are_the_total_budget(self) -> None:
        main = skill()
        repair = reference("repair-and-integration.md")
        scheduler = reference("scheduler.md")
        domain = reference("domain-and-state.md")

        for contract in (
            "at most two repair cycles",
            "Cycle 1 is the ordinary repair cycle",
            "Cycle 2 is the single automatic correction cycle",
            "No third cycle",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, repair + domain)
        self.assertIn("without user approval", repair)
        self.assertIn("refresh the Ticket Coder and both Ticket Reviewers only when entering Cycle 2", scheduler)
        self.assertIn("reuse them throughout Cycle 2", scheduler)
        self.assertIn("After Cycle 2 exhausts", main + repair)
        self.assertNotIn("Automatic repair has no fixed total-cycle ceiling", repair)

    def test_repository_overview_declares_the_same_two_cycle_limit(self) -> None:
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("最多两个修复周期", readme)
        self.assertIn("唯一一次自动纠偏周期", readme)
        self.assertIn("Cycle 2 耗尽后停止自动修改", readme)
        self.assertNotIn("不是 Ticket 的永久终点", readme)
        self.assertNotIn("自动续配", readme)

    def test_cycle_two_requires_a_successful_correction_diagnosis(self) -> None:
        main = skill()
        step_eight = main[main.index("8. On any repair trigger") : main.index("9. On `CONTRACT_BLOCKER`")]

        self.assertIn("fresh Correction Coder", step_eight)
        self.assertIn("Only when", step_eight)
        self.assertIn("`AUTO_REPAIR_RENEWAL`", step_eight)
        self.assertIn("enter Cycle 2", step_eight)
        self.assertIn("Otherwise", step_eight)
        self.assertIn("`IMPLEMENTATION_BLOCKED` or `CONTRACT_BLOCKER`", step_eight)
        self.assertNotIn(
            "refresh the Ticket Coder and both Ticket Reviewers once, and automatically run Cycle 2",
            step_eight,
        )

    def test_recovery_refresh_uses_one_consistent_exception_rule(self) -> None:
        scheduler = reference("scheduler.md")
        domain = reference("domain-and-state.md")
        exception_rule = (
            "unavailable, has lost its required context or read-only independence, "
            "or its contract authority materially changed"
        )

        self.assertIn(exception_rule, scheduler)
        self.assertIn(exception_rule, domain)
        self.assertNotIn(
            "After Scheduler-task recovery, do not depend on old child availability. "
            "Create a fresh child for the required role",
            scheduler,
        )

    def test_cycle_two_is_a_scale_correction_not_generic_hypothesis_rotation(self) -> None:
        coder = reference("coder.md")
        repair = reference("repair-and-integration.md")

        for contract in (
            "initial reviewed Candidate",
            "new owner, fact source, lifecycle, state model, store, coordination mechanism",
            "remove or reject every unsupported mechanism",
            "smallest credible in-Scope correction",
            "converges or reduces the design",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, coder + repair)

    def test_only_effective_tree_changes_consume_a_repair_round(self) -> None:
        repair = reference("repair-and-integration.md")

        self.assertIn("effective code or test tree changes", repair)
        for excluded in (
            "commit-message-only change",
            "evidence-only correction",
            "read-only refresh",
            "effective cumulative tree and behavior evidence remain identical",
        ):
            with self.subTest(excluded=excluded):
                self.assertIn(excluded, repair)

    def test_merge_conflict_base_change_obeys_effective_tree_round_accounting(self) -> None:
        repair = reference("repair-and-integration.md")
        conflict = repair[repair.index("## Merge Conflicts") :]

        self.assertIn("only when the effective code or test tree changes", conflict)
        self.assertIn("A Base-only change", conflict)
        self.assertIn("consumes no repair round", conflict)
        self.assertNotIn("changes code or Base, consume the shared repair round", conflict)

    def test_contract_change_approval_is_rare_and_delta_scoped(self) -> None:
        reconciliation = reference("contract-reconciliation.md")

        for contract in (
            "cannot be satisfied by any smaller in-Scope implementation",
            "Reviewer preference",
            "only the affected Spec, ADR, and Open Ticket changes",
            "stable references to unaffected items",
            "Do not copy every unaffected Open Ticket body",
            "at most one automatic package correction",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, reconciliation)

    def test_final_acceptance_uses_one_real_journey_and_focused_evidence(self) -> None:
        acceptance = reference("acceptance.md")
        final_gate = reference("final-integration-gate.md")

        for contract in (
            "one real end-to-end journey for each distinct public Seam",
            "focused tests",
            "already-bound Ticket evidence",
            "Do not mechanically repeat every lower-level scenario",
            "cannot replace observable product evidence",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, acceptance + final_gate)


if __name__ == "__main__":
    unittest.main()
