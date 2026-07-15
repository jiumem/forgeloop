from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = PLUGIN_ROOT / "fixtures" / "m5-cumulative-audit.json"
SCRIPT = PLUGIN_ROOT / "scripts" / "validate_fixtures.py"
SPEC = importlib.util.spec_from_file_location("validate_cumulative_audit_fixtures", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class CumulativeAuditFixtureTests(unittest.TestCase):
    def test_matrix_covers_planning_delivery_projection_and_runtime_boundaries(self) -> None:
        data = json.loads(FIXTURE.read_text(encoding="utf-8"))

        self.assertEqual(data["kind"], "cumulative-audit")
        self.assertEqual(MODULE.validate(FIXTURE), [])
        by_id = {case["id"]: case for case in data["cases"]}
        required = {
            "approved-github",
            "approved-gitlab",
            "user-rejects",
            "single-ticket-ineligible",
            "local-ineligible",
            "local-shared-reason",
            "wide-refactor-gate",
            "non-green-migration-gate",
            "atomic-delivery-no-ceremony",
            "serial-shared-delivery",
            "legacy-declaration-rejected",
            "real-final-implementation-ticket",
            "unattributed-commit",
            "missing-approved-commit",
            "missing-ticket-commit",
            "human-merge",
            "auto-merge",
            "gate-finding-repair",
            "matching-repair-ticket-reused",
            "multi-scope-repair",
            "target-drift",
            "projection-drift",
            "single-spec-one-pr",
            "multi-spec-per-spec-pr",
        }
        self.assertTrue(required.issubset(by_id))
        self.assertEqual(by_id["approved-github"]["domain_state"], by_id["approved-gitlab"]["domain_state"])
        self.assertFalse(by_id["user-rejects"]["domain_state"]["cumulative_selected"])
        self.assertFalse(by_id["local-ineligible"]["domain_state"]["native_pr_claimed"])
        self.assertEqual(by_id["single-spec-one-pr"]["domain_state"]["pr_identities"], 1)
        self.assertEqual(by_id["multi-spec-per-spec-pr"]["domain_state"]["cross_spec_prs"], 0)
        self.assertEqual(by_id["legacy-declaration-rejected"]["domain_state"]["tracker_writes"], 0)
        self.assertIsInstance(
            by_id["real-final-implementation-ticket"]["domain_state"]["final_implementation_ticket"],
            dict,
        )

    def test_fixture_outcomes_are_enforced_not_only_listed(self) -> None:
        data = json.loads(FIXTURE.read_text(encoding="utf-8"))
        by_id = {case["id"]: case for case in data["cases"]}
        mutations = (
            ("unattributed-commit", "unattributed_commits", [], "额外 Commit"),
            ("missing-approved-commit", "missing_ticket_commits", [], "缺失 Commit"),
            ("matching-repair-ticket-reused", "matching_unfinished_tickets", 2, "唯一未完成"),
            ("matching-repair-ticket-reused", "repair_ticket_reused", False, "必须复用"),
            ("multi-scope-repair", "repair_ticket_count", 1, "多 Scope"),
            ("target-drift", "repair_budget_used", True, "Repair Budget"),
            ("target-drift", "target_refreshed", False, "必须刷新"),
            ("projection-drift", "projection_matches_native", True, "投影漂移"),
            ("auto-merge", "spec_integration_results", [], "Spec Integration Result"),
        )
        for case_id, field, value, diagnostic in mutations:
            case = json.loads(json.dumps(by_id[case_id]))
            case["domain_state"][field] = value

            errors = self._validate(case)

            self.assertTrue(any(diagnostic in error for error in errors), case_id)

        final_ticket = json.loads(json.dumps(by_id["real-final-implementation-ticket"]))
        final_ticket["domain_state"]["final_implementation_ticket"]["risk_classification"] = "FINAL"
        errors = self._validate(final_ticket)
        self.assertTrue(any("风险分类" in error for error in errors))

        for field, diagnostic in (("implementation_scope", "真实 Scope"), ("owned_csi", "CSI ownership")):
            final_ticket = json.loads(json.dumps(by_id["real-final-implementation-ticket"]))
            final_ticket["domain_state"]["final_implementation_ticket"][field] = ""
            errors = self._validate(final_ticket)
            self.assertTrue(any(diagnostic in error for error in errors), field)

        for field, value, diagnostic in (
            ("result", "", "标量字段"),
            ("target_after", "", "标量字段"),
            ("evidence_refs", [], "最终证据"),
        ):
            integration = json.loads(json.dumps(by_id["auto-merge"]))
            integration["domain_state"]["spec_integration_results"][0][field] = value
            errors = self._validate(integration)
            self.assertTrue(any(diagnostic in error for error in errors), field)

    def test_every_shared_reason_requires_the_spec_root_without_a_ceremony_ticket(self) -> None:
        for reason in MODULE.SHARED_REASONS:
            state = {
                "topology": "SHARED",
                "reason": reason,
                "integration_policy": "auto-merge",
                "native_pr_runtime": reason == "CUMULATIVE_AUDIT",
                "implementation_tickets": 2,
                "approved": True,
                "cumulative_selected": reason == "CUMULATIVE_AUDIT",
                "gate_owner": "TICKET",
                "ceremony_ticket_count": 1,
            }

            errors = self._validate(self._case(state))

            self.assertTrue(any("SPEC_ROOT" in error for error in errors), reason)
            self.assertTrue(any("ceremony-only" in error for error in errors), reason)

    def test_final_gate_prerequisites_and_finding_payload_are_validated(self) -> None:
        state = {
            "topology": "SHARED",
            "reason": "ATOMIC_DELIVERY",
            "integration_policy": "auto-merge",
            "native_pr_runtime": True,
            "implementation_tickets": 2,
            "approved": True,
            "cumulative_selected": False,
            "gate_owner": "SPEC_ROOT",
            "ceremony_ticket_count": 0,
            "ordinary_tickets_closed": 1,
            "ticket_integration_results": 1,
            "gate_started": True,
            "blocked_reason": "FINAL_GATE_FINDING",
            "run_paused": True,
            "repair_key": "unstable",
        }

        errors = self._validate(self._case(state))

        self.assertTrue(any("普通 Ticket" in error for error in errors))
        self.assertTrue(any("Ticket Integration Result" in error for error in errors))
        self.assertTrue(any("finding_id" in error for error in errors))
        self.assertTrue(any("repair_key" in error for error in errors))

    def test_cumulative_selection_requires_native_runtime_two_tickets_and_approval(self) -> None:
        case = self._case(
            {
                "topology": "SHARED",
                "reason": "CUMULATIVE_AUDIT",
                "integration_policy": "auto-merge",
                "native_pr_runtime": False,
                "implementation_tickets": 1,
            "approved": False,
            "cumulative_selected": True,
            "gate_owner": "SPEC_ROOT",
            "ceremony_ticket_count": 0,
            }
        )

        errors = self._validate(case)

        self.assertTrue(any("原生 PR/MR runtime" in error for error in errors))
        self.assertTrue(any("至少两张实现 Ticket" in error for error in errors))
        self.assertTrue(any("用户批准" in error for error in errors))

    def test_merge_requires_complete_projection_and_exact_readback(self) -> None:
        state = {
            "topology": "SHARED",
            "reason": "CUMULATIVE_AUDIT",
            "integration_policy": "auto-merge",
            "native_pr_runtime": True,
            "implementation_tickets": 2,
            "approved": True,
            "cumulative_selected": True,
            "gate_owner": "SPEC_ROOT",
            "ceremony_ticket_count": 0,
            "pr_identities": 1,
            "merge_attempted": True,
            "projection_fields": ["Spec"],
            "projection_matches_native": False,
            "exact_readback": False,
        }

        errors = self._validate(self._case(state))

        self.assertTrue(any("累计审计字段不完整" in error for error in errors))
        self.assertTrue(any("精确回读" in error for error in errors))
        self.assertTrue(any("Final Integration Gate 验证" in error for error in errors))
        self.assertTrue(any("保护规则与权限" in error for error in errors))

    def test_completed_delivery_requires_fresh_spec_acceptance(self) -> None:
        state = {
            "topology": "SHARED",
            "reason": "CUMULATIVE_AUDIT",
            "integration_policy": "auto-merge",
            "native_pr_runtime": True,
            "implementation_tickets": 2,
            "approved": True,
            "cumulative_selected": True,
            "gate_owner": "SPEC_ROOT",
            "ceremony_ticket_count": 0,
        }
        case = self._case(state)
        case["terminal_state"] = "COMPLETED"

        errors = self._validate(case)

        self.assertTrue(any("必须先完成累计 PR/MR 合并" in error for error in errors))
        self.assertTrue(any("fresh Spec Acceptance" in error for error in errors))

    def test_human_ready_requires_one_native_identity_per_spec(self) -> None:
        state = {
            "topology": "SHARED",
            "reason": "CUMULATIVE_AUDIT",
            "integration_policy": "human-merge",
            "native_pr_runtime": True,
            "implementation_tickets": 2,
            "approved": True,
            "cumulative_selected": True,
            "gate_owner": "SPEC_ROOT",
            "ceremony_ticket_count": 0,
            "pr_identities": 0,
            "ready_for_human_merge": True,
            "lifecycle": MODULE.CUMULATIVE_HUMAN_READY_LIFECYCLE,
            "gate_validation_pass": True,
            "delivery_head_unchanged": True,
            "delivery_range_valid": True,
            "ordinary_tickets_closed": 2,
            "ticket_integration_results": 2,
            "required_checks_pass": True,
            "protection_pass": True,
            "permissions_pass": True,
            "projection_matches_native": True,
            "exact_readback": True,
        }

        errors = self._validate(self._case(state))

        self.assertTrue(any("human-merge 必须绑定" in error for error in errors))

    @staticmethod
    def _case(domain_state: dict) -> dict:
        return {
            "id": "invalid-cumulative",
            "group": "invalid-cumulative",
            "tracker": "github",
            "initial_state": "累计审计草案。",
            "entry_prompt": "继续。",
            "expected_writes": ["合法原生写入"],
            "forbidden_writes": ["越权合并"],
            "terminal_state": "BLOCKED",
            "failure_diagnostic": "累计证据无效。",
            "domain_state": domain_state,
        }

    @staticmethod
    def _validate(case: dict) -> list[str]:
        fixture = {"schema_version": 1, "kind": "cumulative-audit", "cases": [case]}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.json"
            path.write_text(json.dumps(fixture), encoding="utf-8")
            return MODULE.validate(path)


if __name__ == "__main__":
    unittest.main()
