from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_runtime_contract.py"
SPEC = importlib.util.spec_from_file_location("validate_runtime_contract", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class RuntimeContractTests(unittest.TestCase):
    def test_missing_marker_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "SKILL.md").write_text("only one marker", encoding="utf-8")
            contract = root / "contract.json"
            contract.write_text(json.dumps({"SKILL.md": ["required marker"]}), encoding="utf-8")
            errors = MODULE.validate(root, contract)
        self.assertTrue(any("缺失封板条款" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
