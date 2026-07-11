from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "sync_upstream.py"
SPEC = importlib.util.spec_from_file_location("sync_upstream", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class SyncUpstreamTests(unittest.TestCase):
    def test_wrong_commit_is_rejected(self) -> None:
        expected = "391a2701dd948f94f56a39f7533f8eea9a859c87"
        actual = "0" * 40
        with self.assertRaisesRegex(RuntimeError, "上游 Commit 不匹配"):
            MODULE.require_upstream_commit(actual, expected)

    def test_tampered_import_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            (target / "SKILL.md").write_text("tampered", encoding="utf-8")
            errors = MODULE.compare_target(target, {Path("SKILL.md"): b"expected"})
        self.assertTrue(any("上游漂移" in error for error in errors))

    def test_repeated_write_is_idempotent(self) -> None:
        expected = {Path("SKILL.md"): b"expected", Path("reference.md"): b"reference"}
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "skill"
            MODULE.write_target(target, expected)
            first = {path.relative_to(target): path.read_bytes() for path in target.rglob("*") if path.is_file()}
            MODULE.write_target(target, expected)
            second = {path.relative_to(target): path.read_bytes() for path in target.rglob("*") if path.is_file()}
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
