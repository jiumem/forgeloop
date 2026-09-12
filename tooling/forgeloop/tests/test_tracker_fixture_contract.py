from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


TOOLING_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = TOOLING_ROOT / "scripts" / "validate_fixtures.py"
FIXTURE = TOOLING_ROOT / "fixtures" / "m1-tracker-paths.json"
SPEC = importlib.util.spec_from_file_location("validate_fixtures", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class TrackerFixtureContractTests(unittest.TestCase):
    def test_current_planning_matrix_is_valid_and_platform_equivalent(self) -> None:
        self.assertEqual(MODULE.validate(FIXTURE), [])

    def test_missing_tracker_variant_is_rejected(self) -> None:
        data = json.loads(FIXTURE.read_text(encoding="utf-8"))
        data["cases"] = [
            case
            for case in data["cases"]
            if not (case["group"] == "setup" and case["tracker"] == "local")
        ]

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            errors = MODULE.validate(path)

        self.assertTrue(any("setup: Tracker 覆盖不完整" in error for error in errors))

    def test_platform_domain_drift_is_rejected(self) -> None:
        data = json.loads(FIXTURE.read_text(encoding="utf-8"))
        case = next(
            case
            for case in data["cases"]
            if case["group"] == "publish" and case["tracker"] == "gitlab"
        )
        case["terminal_state"] = "DIFFERENT"

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            errors = MODULE.validate(path)

        self.assertIn("publish: 三 Tracker 领域终态不等价", errors)


if __name__ == "__main__":
    unittest.main()
