import unittest

from codex_initiative_runtime.task_controller import step_transition


class ControllerTests(unittest.TestCase):
    def test_ready_for_anchor(self):
        observation = {
            "gate_status": "PROCEED",
            "gate_reason": "clean",
            "closure_state": {
                "functional_completeness": "COMPLETE",
                "reverse_path_completeness": "COMPLETE",
                "test_proof_strength": "ADEQUATE",
            },
            "entropy_signals": [],
            "baseline_adherence": {"contracts": []},
            "mandatory_fixes": [],
            "suggested_action": {"type": "PROCEED_TO_NEXT_TASK", "why": "done"},
        }
        decision = step_transition("T001", {"probe_count": 0, "stall_count": 0}, None, observation)
        self.assertEqual(decision.action.value, "READY_FOR_ANCHOR")

    def test_add_proof_tests_for_test_p0(self):
        observation = {
            "gate_status": "HALT_AND_FIX",
            "gate_reason": "proof missing",
            "closure_state": {
                "functional_completeness": "COMPLETE",
                "reverse_path_completeness": "PARTIAL",
                "test_proof_strength": "WEAK",
            },
            "entropy_signals": [],
            "baseline_adherence": {"contracts": []},
            "mandatory_fixes": [
                {
                    "id": "MISSING_REVERSE_PATH_TEST",
                    "title": "need test",
                    "plane": "TEST_PROOF",
                    "severity": "P0",
                    "evidence_type": "CONFIRMED_BY_CODE",
                    "description": "need more tests",
                }
            ],
            "suggested_action": {"type": "ADD_PROOF_TESTS", "why": "tests missing"},
        }
        decision = step_transition("T001", {"probe_count": 0, "stall_count": 0}, None, observation)
        self.assertEqual(decision.action.value, "ADD_PROOF_TESTS")


if __name__ == "__main__":
    unittest.main()
