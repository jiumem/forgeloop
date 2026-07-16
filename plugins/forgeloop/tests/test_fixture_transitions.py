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
                "repair-diagnosis-github",
                "repair-diagnosis-gitlab",
                "repair-diagnosis-local",
                "structural-repair",
                "repair-diagnosis-interrupted",
                "third-repair-pass",
                "mixed-repair-budget",
                "repair-cycle-renewed",
            }.issubset(ids)
        )

    def test_repair_diagnosis_and_three_round_budget_have_closed_loop_fixtures(self) -> None:
        data = json.loads(M2_FIXTURE.read_text(encoding="utf-8"))
        by_id = {case["id"]: case for case in data["cases"]}

        for tracker in ("github", "gitlab", "local"):
            case = by_id[f"repair-diagnosis-{tracker}"]
            self.assertEqual(case["domain_state"]["diagnosis_writes"], 0)
            self.assertEqual(case["domain_state"]["repair_rounds"], 1)
            self.assertFalse(any("REPAIR_DIAGNOSIS:" in event for event in case["event_trace"]))

        self.assertTrue(by_id["structural-repair"]["domain_state"]["codebase_design_used"])
        self.assertTrue(by_id["repair-diagnosis-interrupted"]["domain_state"]["diagnosis_rerun"])
        self.assertEqual(by_id["third-repair-pass"]["domain_state"]["repair_rounds"], 3)
        self.assertEqual(by_id["mixed-repair-budget"]["domain_state"]["repair_rounds"], 3)

        exhausted = by_id["repair-exhausted"]
        self.assertEqual(exhausted["domain_state"]["repair_rounds"], 3)
        self.assertEqual(exhausted["domain_state"]["reason"], "IMPLEMENTATION_BLOCKED")
        self.assertIn("第四轮普通修复", exhausted["forbidden_writes"])

        renewed = by_id["repair-cycle-renewed"]
        self.assertEqual(renewed["domain_state"]["repair_rounds_per_cycle"], [3, 3])
        self.assertTrue(renewed["domain_state"]["same_ticket_run_branch"])
        rendered = [
            MODULE.runtime_event_string(event) for event in renewed["event_trace"]
        ]
        self.assertIn("RUN_PAUSED:REPAIR_BUDGET", rendered)
        self.assertIn("RUN_RESUMED:AUTO_REPAIR_RENEWAL", rendered)

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

    def test_pass_substrings_do_not_satisfy_review_or_acceptance(self) -> None:
        fixture = {
            "schema_version": 1,
            "kind": "run-initiative-runtime",
            "cases": [
                {
                    "id": "false-pass",
                    "group": "false-pass",
                    "tracker": "local",
                    "initial_state": "正式 Spec。",
                    "entry_prompt": "运行。",
                    "expected_writes": ["失败 Verdict"],
                    "forbidden_writes": ["错误完成"],
                    "terminal_state": "COMPLETED",
                    "failure_diagnostic": "包含 PASS 字样不等于通过。",
                    "domain_state": {"tickets_complete": 1},
                    "event_trace": [
                        "RUN_CLAIMED",
                        "REVIEW_RESULT:NOT_PASS",
                        "INTEGRATION_RESULT:T01",
                        "ACCEPTANCE_RESULT:NOT_PASS",
                    ],
                    "final_native_state": {
                        "root_open": False,
                        "claim_active": False,
                    },
                }
            ],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.json"
            path.write_text(json.dumps(fixture), encoding="utf-8")
            errors = MODULE.validate(path)

        self.assertTrue(
            any("COMPLETED 必须包含 ACCEPTANCE_RESULT PASS" in error for error in errors)
        )
        self.assertTrue(any("每个 Integration Result 前" in error for error in errors))

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

    def test_fourth_repair_round_is_rejected(self) -> None:
        fixture = self._repair_fixture(
            "fourth-repair",
            [
                "CODER_RESULT:REPAIR_1_READY",
                "CODER_RESULT:REPAIR_2_READY",
                "CODER_RESULT:REPAIR_3_READY",
                "CODER_RESULT:REPAIR_4_READY",
                "RUN_PAUSED:REPAIR_BUDGET",
            ],
        )

        errors = self._validate_fixture(fixture)

        self.assertTrue(any("不得超过三轮普通修复" in error for error in errors))

    def test_repair_budget_pause_requires_three_rounds(self) -> None:
        fixture = self._repair_fixture(
            "early-budget-pause",
            ["CODER_RESULT:REPAIR_1_READY", "RUN_PAUSED:REPAIR_BUDGET"],
        )

        errors = self._validate_fixture(fixture)

        self.assertTrue(any("REPAIR_BUDGET 必须在当前周期第三轮修复后" in error for error in errors))

    def test_repair_rounds_cannot_reset_without_confirmed_automatic_renewal(self) -> None:
        fixture = self._repair_fixture(
            "unbound-round-reset",
            [
                "CODER_RESULT:REPAIR_1_READY",
                "CODER_RESULT:REPAIR_2_READY",
                "CODER_RESULT:REPAIR_3_READY",
                "CODER_RESULT:REPAIR_1_RETRY",
            ],
        )

        errors = self._validate_fixture(fixture)

        self.assertTrue(any("每个修复周期必须按 1、2、3 顺序" in error for error in errors))

    def test_candidate_mutation_waits_for_confirmed_automatic_renewal(self) -> None:
        fixture = self._repair_fixture(
            "mutation-before-renewal",
            [
                "CODER_RESULT:REPAIR_1_READY",
                "CODER_RESULT:REPAIR_2_READY",
                "CODER_RESULT:REPAIR_3_READY",
                "RUN_PAUSED:REPAIR_BUDGET",
                "CODER_RESULT:REPAIR_1_RETRY",
            ],
        )

        errors = self._validate_fixture(fixture)

        self.assertTrue(any("AUTO_REPAIR_RENEWAL 确认前修改 Candidate" in error for error in errors))

    def test_automatic_renewal_requires_a_confirmed_budget_pause(self) -> None:
        fixture = self._repair_fixture(
            "renewal-without-pause",
            ["RUN_RESUMED:AUTO_REPAIR_RENEWAL"],
        )

        errors = self._validate_fixture(fixture)

        self.assertTrue(any("必须绑定已确认的 REPAIR_BUDGET 暂停" in error for error in errors))

    def test_budget_pause_cannot_use_generic_recovery_resume(self) -> None:
        fixture = self._repair_fixture(
            "generic-resume-after-budget",
            [
                "CODER_RESULT:REPAIR_1_READY",
                "CODER_RESULT:REPAIR_2_READY",
                "CODER_RESULT:REPAIR_3_READY",
                "RUN_PAUSED:REPAIR_BUDGET",
                "RUN_RESUMED",
            ],
        )

        errors = self._validate_fixture(fixture)

        self.assertTrue(any("必须先经过 Exhaustion Diagnosis" in error for error in errors))

    def test_cancelled_run_cannot_renew_or_mutate_candidate(self) -> None:
        fixture = self._repair_fixture(
            "cancelled-before-renewal",
            [
                *self._exhausted_cycle_events(),
                "RUN_CANCELLED",
                self._automatic_resume("attempt-a", native_order=11),
                self._repair_event(1, "pause:cycle-1", "attempt-a"),
            ],
        )

        errors = self._validate_fixture(fixture)

        self.assertTrue(any("取消确认后不得自动续配" in error for error in errors))

    def test_duplicate_budget_pause_for_one_anchor_is_rejected(self) -> None:
        fixture = self._repair_fixture(
            "duplicate-budget-pause",
            [
                *self._exhausted_cycle_events(),
                self._budget_pause(native_ref="pause:cycle-1-duplicate", native_order=11),
            ],
        )

        errors = self._validate_fixture(fixture)

        self.assertTrue(any("同一 cycle_anchor 不得重复确认 REPAIR_BUDGET" in error for error in errors))

    def test_automatic_resume_must_bind_the_exhausted_cycle_anchor(self) -> None:
        fixture = self._repair_fixture(
            "stale-cycle-resume",
            [
                *self._exhausted_cycle_events(),
                self._automatic_resume(
                    "attempt-a",
                    native_order=11,
                    cycle_anchor="claim:old-cycle",
                ),
            ],
        )

        errors = self._validate_fixture(fixture)

        self.assertTrue(any("AUTO_REPAIR_RENEWAL 未绑定已确认的耗尽周期" in error for error in errors))

    def test_only_earliest_resume_attempt_can_authorize_candidate_mutation(self) -> None:
        fixture = self._repair_fixture(
            "non-winner-coder",
            [
                *self._exhausted_cycle_events(),
                self._automatic_resume("attempt-a", native_order=11),
                self._automatic_resume("attempt-b", native_order=12),
                self._repair_event(1, "pause:cycle-1", "attempt-b"),
            ],
        )

        errors = self._validate_fixture(fixture)

        self.assertTrue(any("Candidate mutation 必须绑定最早有效 Resume attempt" in error for error in errors))

    def test_automatic_renewal_requires_cycle_bound_coder_and_review_evidence(self) -> None:
        fixture = self._repair_fixture(
            "unbound-renewed-review",
            [
                *self._exhausted_cycle_events(),
                self._automatic_resume("attempt-a", native_order=11),
                "REVIEW_RESULT:REPAIR_REQUIRED",
            ],
        )

        errors = self._validate_fixture(fixture)

        self.assertTrue(any("Coder 与 Review 必须绑定 cycle_anchor" in error for error in errors))

    def test_cancellation_after_resume_still_prevents_candidate_mutation(self) -> None:
        fixture = self._repair_fixture(
            "cancelled-after-resume",
            [
                *self._exhausted_cycle_events(),
                self._automatic_resume("attempt-a", native_order=11),
                "RUN_CANCELLED",
                self._repair_event(1, "pause:cycle-1", "attempt-a"),
            ],
        )

        errors = self._validate_fixture(fixture)

        self.assertTrue(any("取消确认后不得修改 Candidate" in error for error in errors))

    def test_contract_blocker_fixture_cannot_claim_zero_budget_after_repair(self) -> None:
        fixture = self._repair_fixture(
            "false-zero-budget",
            ["CODER_RESULT:REPAIR_1_READY", "RUN_PAUSED:CONTRACT_BLOCKER"],
        )
        fixture["cases"][0]["terminal_state"] = "CONTRACT_BLOCKER"
        fixture["cases"][0]["domain_state"] = {"repair_budget_used": False}

        errors = self._validate_fixture(fixture)

        self.assertTrue(any("声明未消耗预算但存在修复结果" in error for error in errors))

    @staticmethod
    def _repair_fixture(case_id: str, trace: list[object]) -> dict:
        return {
            "schema_version": 1,
            "kind": "run-initiative-runtime",
            "cases": [
                {
                    "id": case_id,
                    "group": case_id,
                    "tracker": "local",
                    "initial_state": "修复中。",
                    "entry_prompt": "继续。",
                    "expected_writes": ["修复证据"],
                    "forbidden_writes": ["越界修复"],
                    "terminal_state": "PAUSED",
                    "failure_diagnostic": "预算边界。",
                    "domain_state": {},
                    "event_trace": ["RUN_CLAIMED", *trace],
                    "final_native_state": {"root_open": True, "claim_active": True},
                }
            ],
        }

    @staticmethod
    def _validate_fixture(fixture: dict) -> list[str]:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.json"
            path.write_text(json.dumps(fixture), encoding="utf-8")
            return MODULE.validate(path)

    @staticmethod
    def _repair_event(
        round_number: int,
        cycle_anchor: str,
        resume_attempt_id: str | None = None,
    ) -> dict:
        event = {
            "event": "CODER_RESULT",
            "payload": f"REPAIR_{round_number}_READY",
            "cycle_anchor": cycle_anchor,
        }
        if resume_attempt_id is not None:
            event["resume_attempt_id"] = resume_attempt_id
        return event

    @staticmethod
    def _budget_pause(
        *,
        native_ref: str = "pause:cycle-1",
        native_order: int = 10,
    ) -> dict:
        return {
            "event": "RUN_PAUSED",
            "payload": "REPAIR_BUDGET",
            "cycle_anchor": "claim:cycle-1",
            "native_ref": native_ref,
            "native_order": native_order,
            "exact_readback": True,
        }

    @classmethod
    def _exhausted_cycle_events(cls) -> list[dict]:
        return [
            cls._repair_event(1, "claim:cycle-1"),
            cls._repair_event(2, "claim:cycle-1"),
            cls._repair_event(3, "claim:cycle-1"),
            cls._budget_pause(),
        ]

    @staticmethod
    def _automatic_resume(
        attempt_id: str,
        *,
        native_order: int,
        cycle_anchor: str = "claim:cycle-1",
    ) -> dict:
        return {
            "event": "RUN_RESUMED",
            "payload": "AUTO_REPAIR_RENEWAL",
            "cycle_anchor": cycle_anchor,
            "resume_attempt_id": attempt_id,
            "native_ref": f"resume:{attempt_id}",
            "native_order": native_order,
            "exact_readback": True,
        }


if __name__ == "__main__":
    unittest.main()
