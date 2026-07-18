from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[3] / "plugins" / "forgeloop"
RUN_ROOT = PLUGIN_ROOT / "skills" / "run-initiative"
RUN_AGENT_EVALS = os.environ.get("FORGELOOP_RUN_AGENT_EVALS") == "1"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


CASES = [
    {"id": "eligible", "evidence": "GitHub Spec has two implementation Tickets; the full SHARED/CUMULATIVE_AUDIT declaration binds Final integration gate owner to SPEC_ROOT and awaits user approval."},
    {"id": "rejected", "evidence": "The user rejected CUMULATIVE_AUDIT but approved the ordinary independent Ticket set."},
    {"id": "single-ticket", "evidence": "GitLab Spec has exactly one implementation Ticket."},
    {"id": "local", "evidence": "Configured runtime is Local Markdown and the Spec has three Tickets."},
    {"id": "extra-commit", "evidence": "Final audit range contains one Commit that cannot be attributed to an approved Ticket."},
    {"id": "projection-drift", "evidence": "The unique native MR body omits the latest Required Check, while Tracker and Git facts are readable and unchanged."},
    {"id": "human-ready", "evidence": "Under human-merge, the fixed delivery Head, Gate evidence, native Checks, and exact body read-back are ready; the Spec remains Open."},
    {"id": "gate-finding", "evidence": "The Final Integration Gate found an implementation defect after every ordinary Ticket closed; no Open repair Ticket carries its stable repair_key."},
    {"id": "target-drift", "evidence": "Target advanced after Gate validation; delivery Head is unchanged, but current-combination Checks and projection need refresh."},
    {"id": "multi-spec", "evidence": "Two Initiative member Specs each independently approved CUMULATIVE_AUDIT."},
    {"id": "legacy", "evidence": "The approved graph still declares Final integration owner as a Ticket and contains a ceremony-only final Ticket."},
]


EXPECTED = {
    "eligible": ("PROPOSE_CUMULATIVE_GATE", 0),
    "rejected": ("KEEP_INDEPENDENT", 0),
    "single-ticket": ("REJECT_CUMULATIVE", 0),
    "local": ("REJECT_CUMULATIVE", 0),
    "extra-commit": ("BLOCK_FINAL_PR", 0),
    "projection-drift": ("REFRESH_PROJECTION", 0),
    "human-ready": ("PAUSE_HUMAN", 0),
    "gate-finding": ("PAUSE_REPAIR", 0),
    "target-drift": ("REFRESH_NATIVE", 0),
    "multi-spec": ("PER_SPEC_PRS", 0),
    "legacy": ("FAILED_PRECONDITION", 0),
}


def schema() -> dict:
    return {
        "type": "object",
        "properties": {
            "results": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "action": {"type": "string", "enum": sorted({value[0] for value in EXPECTED.values()})},
                        "ordinary_repair_rounds_consumed_now": {"type": "integer", "enum": [0, 1]},
                        "policy_preserved": {"type": "boolean"},
                        "native_facts_authoritative": {"type": "boolean"},
                        "invented_state_or_event": {"type": "boolean"},
                        "reason": {"type": "string"},
                    },
                    "required": ["id", "action", "ordinary_repair_rounds_consumed_now", "policy_preserved", "native_facts_authoritative", "invented_state_or_event", "reason"],
                    "additionalProperties": False,
                },
            }
        },
        "required": ["results"],
        "additionalProperties": False,
    }


def prompt() -> str:
    return f"""Apply the planning and runtime protocols to every case. Judge from native Tracker/Git/PR facts. Use KEEP_INDEPENDENT only after explicit user rejection; use REJECT_CUMULATIVE when the Spec or runtime is ineligible. Report only ordinary repair rounds consumed by the immediate action, not the available or remaining budget. Do not invent an Integration Policy, state, Event, parser, Draft phase, or file-overlap gate. Modify nothing.

<to-tickets>{read(PLUGIN_ROOT / "skills" / "to-tickets" / "SKILL.md")}</to-tickets>
<final-gate>{read(RUN_ROOT / "references" / "final-integration-gate.md")}</final-gate>
<cumulative>{read(RUN_ROOT / "references" / "cumulative-audit.md")}</cumulative>
<integration>{read(RUN_ROOT / "references" / "repair-and-integration.md")}</integration>
<cases>{json.dumps(CASES, indent=2)}</cases>
"""


class CumulativeAuditPromptTests(unittest.TestCase):
    def test_prompt_does_not_embed_expected_mapping(self) -> None:
        text = prompt()
        self.assertNotIn("eligible: PROPOSE_CUMULATIVE_GATE", text)
        self.assertNotIn("gate-finding: PAUSE_REPAIR", text)


@unittest.skipUnless(RUN_AGENT_EVALS, "set FORGELOOP_RUN_AGENT_EVALS=1 to run Agent eval")
class CumulativeAuditAgentEvalTests(unittest.TestCase):
    def test_agent_routes_cumulative_planning_and_delivery(self) -> None:
        codex = shutil.which("codex")
        self.assertIsNotNone(codex)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            schema_path = root / "schema.json"
            result_path = root / "result.json"
            schema_path.write_text(json.dumps(schema()), encoding="utf-8")
            completed = subprocess.run(
                [codex, "exec", "--ephemeral", "--sandbox", "read-only", "--skip-git-repo-check", "--color", "never", "--output-schema", str(schema_path), "--output-last-message", str(result_path), "-C", str(root), "-"],
                input=prompt(), text=True, capture_output=True, timeout=300, check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            actual = json.loads(result_path.read_text(encoding="utf-8"))["results"]

        self.assertEqual({item["id"] for item in actual}, set(EXPECTED))
        by_id = {item["id"]: item for item in actual}
        for case_id, (action, rounds) in EXPECTED.items():
            with self.subTest(case=case_id):
                self.assertEqual(by_id[case_id]["action"], action)
                self.assertEqual(by_id[case_id]["ordinary_repair_rounds_consumed_now"], rounds)
                self.assertTrue(by_id[case_id]["policy_preserved"])
                self.assertTrue(by_id[case_id]["native_facts_authoritative"])
                self.assertFalse(by_id[case_id]["invented_state_or_event"])
                self.assertTrue(by_id[case_id]["reason"])


if __name__ == "__main__":
    unittest.main()
