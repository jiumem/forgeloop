from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = PLUGIN_ROOT / "fixtures" / "m4-target-drift.json"
SCRIPT = PLUGIN_ROOT / "scripts" / "validate_fixtures.py"
SPEC = importlib.util.spec_from_file_location("validate_target_drift_fixtures", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class TargetDriftFixtureTests(unittest.TestCase):
    def test_target_drift_matrix_covers_review_integration_and_seal_paths(self) -> None:
        data = json.loads(FIXTURE.read_text(encoding="utf-8"))

        self.assertEqual(data["kind"], "run-initiative-runtime")
        self.assertEqual(MODULE.validate(FIXTURE), [])
        by_id = {case["id"]: case for case in data["cases"]}
        required = {
            "clean-target-drift-github",
            "clean-target-drift-gitlab",
            "clean-target-drift-local",
            "stale-checks-current-target",
            "native-merge",
            "native-squash",
            "candidate-rebase",
            "conflict-repair",
            "already-present-current-target",
            "integration-fast-forward",
            "force-push-removes-integration",
            "revert-preserves-ancestry",
            "single-spec-preseal-drift",
            "eligibility-refresh-before-readback-drift",
            "multi-spec-acceptance-drift",
            "post-seal-drift",
            "post-seal-partial-close-recovery",
        }
        self.assertTrue(required.issubset(by_id))

        clean_states = [
            by_id[f"clean-target-drift-{tracker}"]["domain_state"]
            for tracker in ("github", "gitlab", "local")
        ]
        self.assertEqual(clean_states[0], clean_states[1])
        self.assertEqual(clean_states[1], clean_states[2])
        self.assertFalse(clean_states[0]["review_rerun"])

        for case_id in ("candidate-rebase", "conflict-repair"):
            self.assertTrue(by_id[case_id]["domain_state"]["both_reissued"])
            self.assertEqual(by_id[case_id]["domain_state"]["repair_rounds"], 1)

        self.assertFalse(by_id["stale-checks-current-target"]["domain_state"]["advance"])
        self.assertTrue(by_id["single-spec-preseal-drift"]["domain_state"]["acceptance_rerun"])
        self.assertFalse(
            by_id["eligibility-refresh-before-readback-drift"]["domain_state"]["acceptance_rerun"]
        )
        self.assertTrue(by_id["multi-spec-acceptance-drift"]["domain_state"]["sequence_restarted"])
        self.assertFalse(by_id["post-seal-drift"]["domain_state"]["acceptance_rerun"])
        self.assertTrue(
            by_id["post-seal-partial-close-recovery"]["domain_state"]["resumed_from_seal"]
        )

        evidence = {item["id"]: item for item in data["evidence_cases"]}
        for tracker in ("github", "gitlab", "local"):
            item = evidence[f"clean-target-drift-{tracker}"]
            self.assertEqual(
                set(item["integrations"][0]),
                {"candidate_head", "target_before", "target_after", "integration_method", "native_ref"},
            )
            self.assertTrue(item["seal"]["native_readback"]["exact_match"])
        self.assertEqual(
            evidence["already-present-current-target"]["integrations"][0]["target_before"],
            evidence["already-present-current-target"]["integrations"][0]["target_after"],
        )
        self.assertTrue(evidence["multi-spec-acceptance-drift"]["seal"]["membership"])

    def test_unchanged_review_inputs_cannot_force_review_rerun_on_target_drift(self) -> None:
        case = self._case(
            {"target_drift": True, "review_inputs_unchanged": True, "review_rerun": True}
        )

        errors = self._validate(case)

        self.assertTrue(any("目标漂移不得使未变 Candidate Review 失效" in error for error in errors))

    def test_post_seal_drift_cannot_rerun_acceptance(self) -> None:
        case = self._case(
            {"seal_confirmed": True, "post_seal_drift": True, "acceptance_rerun": True}
        )

        errors = self._validate(case)

        self.assertTrue(any("Seal 后漂移不得重跑 Acceptance" in error for error in errors))

    def test_seal_requires_exact_readback_and_complete_bindings(self) -> None:
        evidence = {
            "id": "invalid-drift",
            "integrations": [{"candidate_head": "c1"}],
            "seal": {
                "acceptance_level": "SPEC",
                "subject_revision": "spec@r1",
                "membership": [],
                "final_target_commit": "t2",
                "idempotency_key": "a1",
                "native_checkpoint_ref": "local:1",
                "integration_target_afters": [],
                "all_in_final_history": True,
                "eligibility_refresh": {"final_target_commit": "t2", "observed_target": "t2"},
                "native_readback": {"exact_match": False, "native_ref": "local:1"},
            },
        }
        case = self._case({"seal_confirmed": True, "acceptance_rerun": False})

        errors = MODULE.validate_evidence_cases([evidence], {"invalid-drift"}, [case])

        self.assertTrue(any("Integration binding" in error for error in errors))
        self.assertTrue(any("confirmed membership" in error for error in errors))
        self.assertTrue(any("精确原生回读" in error for error in errors))

    @staticmethod
    def _case(domain_state: dict) -> dict:
        return {
            "id": "invalid-drift",
            "group": "invalid-drift",
            "tracker": "local",
            "initial_state": "已有证据。",
            "entry_prompt": "继续。",
            "expected_writes": ["合法推进"],
            "forbidden_writes": ["错误失效"],
            "terminal_state": "PAUSED",
            "failure_diagnostic": "证据绑定错误。",
            "domain_state": domain_state,
            "event_trace": ["RUN_CLAIMED"],
            "final_native_state": {"root_open": True, "claim_active": True},
        }

    @staticmethod
    def _validate(case: dict) -> list[str]:
        fixture = {"schema_version": 1, "kind": "run-initiative-runtime", "cases": [case]}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.json"
            path.write_text(json.dumps(fixture), encoding="utf-8")
            return MODULE.validate(path)


if __name__ == "__main__":
    unittest.main()
