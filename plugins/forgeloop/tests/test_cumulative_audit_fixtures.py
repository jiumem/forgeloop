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
            "serial-shared-delivery",
            "final-ticket-missing",
            "unattributed-commit",
            "missing-ticket-commit",
            "human-merge",
            "auto-merge",
            "final-conflict-repair",
            "final-check-repair",
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
            "final_ticket_count": 1,
            "final_ticket_high_risk_pass": True,
            "pr_identities": 1,
            "merge_attempted": True,
            "projection_fields": ["Spec"],
            "projection_matches_native": False,
            "exact_readback": False,
        }

        errors = self._validate(self._case(state))

        self.assertTrue(any("累计审计字段不完整" in error for error in errors))
        self.assertTrue(any("精确回读" in error for error in errors))
        self.assertTrue(any("最终 Ticket 必须双 PASS" in error for error in errors))
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
            "final_ticket_count": 1,
            "final_ticket_high_risk_pass": True,
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
            "final_ticket_count": 1,
            "final_ticket_high_risk_pass": True,
            "pr_identities": 0,
            "ready_for_human_merge": True,
            "lifecycle": MODULE.CUMULATIVE_HUMAN_READY_LIFECYCLE,
            "final_dual_pass": True,
            "head_revision_unchanged": True,
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
