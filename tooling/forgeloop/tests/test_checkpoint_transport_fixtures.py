from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


TOOLING_ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = Path(__file__).resolve().parents[3] / "plugins" / "forgeloop"
FIXTURE = TOOLING_ROOT / "fixtures" / "m3-checkpoint-transport.json"
SCRIPT = TOOLING_ROOT / "scripts" / "validate_fixtures.py"
SPEC = importlib.util.spec_from_file_location("validate_checkpoint_fixtures", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class CheckpointTransportFixtureTests(unittest.TestCase):
    def test_transport_matrix_covers_literal_safety_and_confirmation_paths(self) -> None:
        data = json.loads(FIXTURE.read_text(encoding="utf-8"))

        self.assertEqual(data["kind"], "checkpoint-transport")
        self.assertEqual(MODULE.validate(FIXTURE), [])
        by_id = {case["id"]: case for case in data["cases"]}

        for scenario in ("normal", "reuse", "ambiguous"):
            states = []
            for tracker in ("github", "gitlab", "local"):
                case = by_id[f"checkpoint-{scenario}-{tracker}"]
                states.append(case["domain_state"])
            self.assertEqual(states[0], states[1])
            self.assertEqual(states[1], states[2])

        self.assertEqual(by_id["checkpoint-body-conflict"]["terminal_state"], "RECOVERY_CONFLICT")
        self.assertEqual(
            by_id["checkpoint-duplicate-identical"]["terminal_state"],
            "RECOVERY_CONFLICT",
        )
        self.assertEqual(by_id["checkpoint-truncated-readback"]["terminal_state"], "UNCONFIRMED")
        self.assertTrue(by_id["checkpoint-newline-normalized"]["domain_state"]["payload_equal"])

        attack = by_id["checkpoint-adversarial-literal"]
        payload = attack["prepared_payload"]
        for marker in ("`command`", "$(touch", "${HOME}", "```yaml", "--body"):
            self.assertIn(marker, payload)
        self.assertEqual(attack["domain_state"]["sentinel_effects"], 0)
        self.assertTrue(attack["domain_state"]["worktree_unchanged"])

    def test_confirmed_transport_rejects_a_mismatched_payload(self) -> None:
        fixture = self._single_case_fixture(
            terminal_state="CONFIRMED",
            domain_state={"writes": 1, "payload_equal": False, "advance": True},
        )

        errors = self._validate(fixture)

        self.assertTrue(any("CONFIRMED 必须完整匹配 Payload" in error for error in errors))

    def test_adversarial_fixture_rejects_sentinel_side_effects(self) -> None:
        fixture = self._single_case_fixture(
            terminal_state="CONFIRMED",
            domain_state={
                "writes": 1,
                "payload_equal": True,
                "advance": True,
                "sentinel_effects": 1,
                "worktree_unchanged": False,
            },
        )

        errors = self._validate(fixture)

        self.assertTrue(any("攻击性 Payload 不得产生副作用" in error for error in errors))

    @staticmethod
    def _single_case_fixture(*, terminal_state: str, domain_state: dict) -> dict:
        return {
            "schema_version": 1,
            "kind": "checkpoint-transport",
            "cases": [
                {
                    "id": "invalid-transport",
                    "group": "invalid-transport",
                    "tracker": "local",
                    "initial_state": "准备写入。",
                    "entry_prompt": "发布。",
                    "expected_writes": ["Checkpoint"],
                    "forbidden_writes": ["错误推进"],
                    "terminal_state": terminal_state,
                    "failure_diagnostic": "验证失败。",
                    "domain_state": domain_state,
                }
            ],
        }

    @staticmethod
    def _validate(fixture: dict) -> list[str]:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.json"
            path.write_text(json.dumps(fixture), encoding="utf-8")
            return MODULE.validate(path)


if __name__ == "__main__":
    unittest.main()
