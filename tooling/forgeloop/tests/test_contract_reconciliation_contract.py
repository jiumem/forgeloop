from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


TOOLING_ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = Path(__file__).resolve().parents[3] / "plugins" / "forgeloop"
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


class ContractReconciliationContractTests(unittest.TestCase):
    def test_one_approval_is_consumed_by_existing_fact_owners(self) -> None:
        run = (PLUGIN_ROOT / "skills/run-initiative/references/contract-reconciliation.md").read_text(
            encoding="utf-8"
        )
        to_spec = generated_skill("to-spec")
        domain = generated_skill("domain-modeling")
        tickets = generated_skill("to-tickets")

        self.assertIn("asked exactly once", run)
        self.assertIn("The user does not invoke or approve them separately", run)
        self.assertIn("Do not interview the user", to_spec)
        self.assertIn("do not ask the user again", domain)
        self.assertIn("do not quiz the user or request another approval", tickets)

    def test_decision_and_resume_boundaries_are_explicit(self) -> None:
        run = (PLUGIN_ROOT / "skills/run-initiative/references/contract-reconciliation.md").read_text(
            encoding="utf-8"
        )
        events = (PLUGIN_ROOT / "skills/run-initiative/references/events-and-recovery.md").read_text(
            encoding="utf-8"
        )

        for choice in ("`REJECT`", "`APPROVE_PAUSE`", "`APPROVE_CONTINUE`"):
            self.assertIn(choice, run)
        self.assertIn("reason=`CONTRACT_RECONCILED`", run)
        self.assertIn("reason=`CONTRACT_RECONCILED`", events)
        self.assertIn("earliest valid immutable native record is the only winner", run)

    def test_internal_review_must_pass_before_user_adjudication(self) -> None:
        run = (PLUGIN_ROOT / "skills/run-initiative/references/contract-reconciliation.md").read_text(
            encoding="utf-8"
        )

        for result in ("`PASS`", "`DESIGN_GAPS`", "`REVIEW_BLOCKED`"):
            self.assertIn(result, run)
        self.assertIn("Ask the user only after a `PASS`", run)
        self.assertIn("keeps contract writes at zero", run)

    def test_changed_spec_identity_cancels_and_never_resumes_old_run(self) -> None:
        run = (PLUGIN_ROOT / "skills/run-initiative/references/contract-reconciliation.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("Exactly publish and read back `RUN_CANCELLED`", run)
        self.assertIn("release only its Claims", run)
        self.assertIn("require a new formal Spec", run)
        self.assertIn("must never publish `CONTRACT_RECONCILED`", run)
        self.assertIn("compete to Resume", run)

    def test_old_candidate_evidence_survives_revision_but_qualification_does_not(self) -> None:
        run = (PLUGIN_ROOT / "skills/run-initiative/references/contract-reconciliation.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("Candidate Branch, Commit, Finding, and evidence", run)
        self.assertIn("reusable read-only input", run)
        self.assertIn("new Candidate bound to the effective Revisions", run)
        self.assertIn("fresh dual review", run)

    def test_only_an_affecting_material_revision_opens_a_new_cycle(self) -> None:
        tickets = generated_skill("to-tickets")

        self.assertIn("material Revision affecting this Ticket", tickets)
        self.assertIn("opens a new initial repair cycle", tickets)
        self.assertIn("unrelated or non-material changes do not reset", tickets)
        self.assertIn("preserves Repair Lineage", tickets)

    def test_revisions_use_literal_safe_file_backed_publication(self) -> None:
        run = (PLUGIN_ROOT / "skills/run-initiative/references/contract-reconciliation.md").read_text(
            encoding="utf-8"
        )
        to_spec = generated_skill("to-spec")
        tickets = generated_skill("to-tickets")

        for text in (run, to_spec, tickets):
            self.assertIn("file-backed Tracker operation", text)
            self.assertIn("inline body/message argument", text)
            self.assertIn("command substitution", text)

    def test_adr_revision_is_effective_only_on_target_branch(self) -> None:
        domain = generated_skill("domain-modeling")

        self.assertIn("effective only when", domain)
        self.assertIn("package's target branch", domain)
        self.assertIn("PR/MR Head", domain)
        self.assertIn("not an effective ADR Revision", domain)
        self.assertIn("do not request another contract approval", domain)

    def test_prompt_contract_rejects_a_shadow_workflow_engine(self) -> None:
        paths = (
            PLUGIN_ROOT / "skills/run-initiative/references/contract-reconciliation.md",
            TOOLING_ROOT / "config/overlays/to-spec-append.md",
            TOOLING_ROOT / "config/overlays/domain-modeling-append.md",
            TOOLING_ROOT / "config/overlays/to-tickets-append.md",
        )
        combined = "\n".join(path.read_text(encoding="utf-8") for path in paths)

        self.assertIn("does not replace Agent judgment", combined)
        self.assertIn("does not resume `$run-initiative`", combined)
        for forbidden in ("reconciliation_state", "transition_table", "scope_unchanged"):
            self.assertNotIn(forbidden, combined)

    def test_only_key_runtime_fixture_is_added(self) -> None:
        fixture = json.loads(
            (TOOLING_ROOT / "fixtures/m2-runtime-matrix.json").read_text(encoding="utf-8")
        )
        cases = [
            case for case in fixture["cases"]
            if case.get("group") == "contract-reconciliation"
        ]

        self.assertEqual(len(cases), 1)
        case = cases[0]
        self.assertTrue(case["domain_state"]["single_approval"])
        self.assertEqual(case["domain_state"]["resume_winners"], 1)
        self.assertIn("RUN_PAUSED:CONTRACT_RECONCILED", case["event_trace"])
        self.assertIn("RUN_RESUMED:CONTRACT_RECONCILED", case["event_trace"])


if __name__ == "__main__":
    unittest.main()
