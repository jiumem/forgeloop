import json
import tempfile
import unittest
from pathlib import Path

from codex_initiative_runtime.gate_review import run_gate_commands, finalize_review_report


REPO_ROOT = Path(__file__).resolve().parents[1]


class GateReviewTests(unittest.TestCase):
    def test_run_gate_commands(self):
        result = run_gate_commands("G1", "T001", ['python -c "print(123)"'], REPO_ROOT)
        self.assertTrue(result.passed)
        self.assertEqual(result.commands[0].return_code, 0)

    def test_finalize_review_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            raw = Path(tmp) / "raw.json"
            raw.write_text(
                json.dumps(
                    {
                        "verdict": "PASS",
                        "summary": "looks good",
                        "findings": [],
                        "residual_risks": [],
                        "escalations": [],
                        "evidence": ["demo"],
                    }
                ),
                encoding="utf-8",
            )
            json_path, md_path = finalize_review_report(
                "INIT-001",
                "R1",
                "T001",
                raw,
                repo_root=REPO_ROOT,
            )
            self.assertTrue(json_path.exists())
            self.assertTrue(md_path.exists())


if __name__ == "__main__":
    unittest.main()
