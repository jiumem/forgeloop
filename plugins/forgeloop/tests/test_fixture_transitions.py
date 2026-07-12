from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PLUGIN_ROOT / "scripts" / "validate_fixtures.py"
M2_FIXTURE = PLUGIN_ROOT / "fixtures" / "m2-runtime-matrix.json"
SPEC = importlib.util.spec_from_file_location("validate_fixtures", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class FixtureTransitionTests(unittest.TestCase):
    def test_m2_cases_declare_transition_traces(self) -> None:
        data = json.loads(M2_FIXTURE.read_text(encoding="utf-8"))

        self.assertEqual(data["kind"], "run-initiative-runtime")
        self.assertEqual(MODULE.validate(M2_FIXTURE), [])
        for case in data["cases"]:
            if case["terminal_state"] == "FAILED_PRECONDITION":
                self.assertEqual(case["event_trace"], [], case["id"])
            else:
                self.assertTrue(case["event_trace"], case["id"])
            self.assertIn("final_native_state", case)

        ids = {case["id"] for case in data["cases"]}
        self.assertTrue(
            {
                "review-input-blocked",
                "acceptance-input-blocked",
                "candidate-check-repair",
                "external-check-blocked",
                "initiative-parent-idempotent",
                "review-shared-input-corrected",
                "spec-revision-reconciled",
                "initiative-repair-owned",
            }.issubset(ids)
        )

    def test_completed_without_acceptance_is_rejected(self) -> None:
        fixture = {
            "schema_version": 1,
            "kind": "run-initiative-runtime",
            "cases": [
                {
                    "id": "bad-complete",
                    "group": "bad-complete",
                    "tracker": "local",
                    "initial_state": "正式 Spec。",
                    "entry_prompt": "运行。",
                    "expected_writes": ["RUN_CLAIMED"],
                    "forbidden_writes": ["PLAN.md"],
                    "terminal_state": "COMPLETED",
                    "failure_diagnostic": "无。",
                    "domain_state": {},
                    "event_trace": ["RUN_CLAIMED"],
                    "final_native_state": {"root_open": False},
                }
            ],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.json"
            path.write_text(json.dumps(fixture), encoding="utf-8")
            errors = MODULE.validate(path)

        self.assertTrue(any("COMPLETED 必须包含 ACCEPTANCE_RESULT PASS" in error for error in errors))

    def test_cancelled_with_live_claim_is_rejected(self) -> None:
        fixture = {
            "schema_version": 1,
            "kind": "run-initiative-runtime",
            "cases": [
                {
                    "id": "bad-cancel",
                    "group": "bad-cancel",
                    "tracker": "local",
                    "initial_state": "活动 Run。",
                    "entry_prompt": "取消。",
                    "expected_writes": ["RUN_CANCELLED"],
                    "forbidden_writes": ["关闭为成功"],
                    "terminal_state": "CANCELLED",
                    "failure_diagnostic": "无。",
                    "domain_state": {},
                    "event_trace": ["RUN_CLAIMED", "RUN_CANCELLED"],
                    "final_native_state": {"claim_active": True, "root_open": True},
                }
            ],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.json"
            path.write_text(json.dumps(fixture), encoding="utf-8")
            errors = MODULE.validate(path)

        self.assertTrue(any("CANCELLED 后 Claim 必须失效" in error for error in errors))

    def test_legacy_runtime_event_is_rejected(self) -> None:
        fixture = {
            "schema_version": 1,
            "kind": "run-initiative-runtime",
            "cases": [
                {
                    "id": "legacy-event",
                    "group": "legacy-event",
                    "tracker": "local",
                    "initial_state": "正式 Spec。",
                    "entry_prompt": "运行。",
                    "expected_writes": ["ACCEPTANCE_RESULT"],
                    "forbidden_writes": ["SPEC_ACCEPTANCE"],
                    "terminal_state": "PAUSED",
                    "failure_diagnostic": "拒绝旧事件。",
                    "domain_state": {},
                    "event_trace": ["SPEC_ACCEPTANCE:PASS"],
                    "final_native_state": {"root_open": True, "claim_active": True},
                }
            ],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.json"
            path.write_text(json.dumps(fixture), encoding="utf-8")
            errors = MODULE.validate(path)

        self.assertTrue(any("包含未声明的运行事件" in error for error in errors))

    def test_serial_ticket_count_requires_one_integration_per_ticket(self) -> None:
        fixture = {
            "schema_version": 1,
            "kind": "run-initiative-runtime",
            "cases": [
                {
                    "id": "short-trace",
                    "group": "short-trace",
                    "tracker": "local",
                    "initial_state": "三张 Ticket。",
                    "entry_prompt": "运行。",
                    "expected_writes": ["三次集成"],
                    "forbidden_writes": ["并行 Ticket"],
                    "terminal_state": "COMPLETED",
                    "failure_diagnostic": "轨迹必须完整。",
                    "domain_state": {"tickets_complete": 3},
                    "event_trace": [
                        "RUN_CLAIMED",
                        "REVIEW_RESULT:DUAL_PASS",
                        "INTEGRATION_RESULT:T01",
                        "ACCEPTANCE_RESULT:SPEC_PASS",
                    ],
                    "final_native_state": {"root_open": False, "claim_active": False},
                }
            ],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.json"
            path.write_text(json.dumps(fixture), encoding="utf-8")
            errors = MODULE.validate(path)

        self.assertTrue(any("声明完成 3 张 Ticket" in error for error in errors))

    def test_multi_spec_acceptance_before_last_integration_is_rejected(self) -> None:
        fixture = {
            "schema_version": 1,
            "kind": "run-initiative-runtime",
            "cases": [
                {
                    "id": "early-acceptance",
                    "group": "early-acceptance",
                    "tracker": "local",
                    "initial_state": "两个 Specs。",
                    "entry_prompt": "运行。",
                    "expected_writes": ["最终验收"],
                    "forbidden_writes": ["提前验收"],
                    "terminal_state": "COMPLETED",
                    "failure_diagnostic": "验收必须后置。",
                    "domain_state": {"shared_final_commit": True},
                    "event_trace": [
                        "RUN_CLAIMED",
                        "REVIEW_RESULT:S1_DUAL_PASS",
                        "INTEGRATION_RESULT:S1",
                        "ACCEPTANCE_RESULT:SPEC_PASS_S1_FINAL",
                        "REVIEW_RESULT:S2_DUAL_PASS",
                        "INTEGRATION_RESULT:S2",
                        "ACCEPTANCE_RESULT:INITIATIVE_PASS",
                    ],
                    "final_native_state": {"root_open": False, "claim_active": False},
                }
            ],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.json"
            path.write_text(json.dumps(fixture), encoding="utf-8")
            errors = MODULE.validate(path)

        self.assertTrue(any("所有 Ticket 集成后开始" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
