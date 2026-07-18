from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


TOOLING_ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = Path(__file__).resolve().parents[3] / "plugins" / "forgeloop"
SKILL_ROOT = PLUGIN_ROOT / "skills" / "run-initiative"
RUN_AGENT_EVALS = os.environ.get("FORGELOOP_RUN_AGENT_EVALS") == "1"


def reference(name: str) -> str:
    return (SKILL_ROOT / "references" / name).read_text(encoding="utf-8")


CASES = [
    {
        "id": "clean-target-drift",
        "evidence": "Target advanced; all Candidate Review inputs are byte-for-byte unchanged and current native checks bind the Candidate plus current target.",
    },
    {
        "id": "stale-checks",
        "evidence": "Candidate inputs are unchanged, but existing Required Checks bind only the prior target combination.",
    },
    {
        "id": "native-squash",
        "evidence": "Platform can squash the unchanged reviewed Candidate with native checks and merge evidence; no conflict repair occurred.",
    },
    {
        "id": "candidate-rebase",
        "evidence": "The Candidate Branch was rebased after PASS and now has a different Head.",
    },
    {
        "id": "force-push",
        "evidence": "Before final Acceptance, a force-push removed one Ticket target_after from final target history.",
    },
    {
        "id": "revert",
        "evidence": "All target_after commits remain ancestors, but a later revert breaks observable Delivery Acceptance behavior.",
    },
    {
        "id": "preseal-drift",
        "evidence": "Acceptance Reviewer returned PASS, then target changed before Payload rendering or publication.",
    },
    {
        "id": "postseal-recovery",
        "evidence": "Exact native read-back already confirmed the root Seal; closure and Claim release were interrupted, and target later advanced.",
    },
    {
        "id": "eligibility-refresh-drift",
        "evidence": "The target matched final_commit at the last successful eligibility refresh, advanced before confirmation, and exact native read-back then confirmed that pending PASS Payload.",
    },
]


EXPECTED = {
    "clean-target-drift": {"action": "INTEGRATE_NATIVE", "keep_review": True, "rerun_acceptance": False, "repair_diagnosis": False, "budget": "ZERO"},
    "stale-checks": {"action": "PAUSE_CHECKS", "keep_review": True, "rerun_acceptance": False, "repair_diagnosis": False, "budget": "ZERO"},
    "native-squash": {"action": "INTEGRATE_NATIVE", "keep_review": True, "rerun_acceptance": False, "repair_diagnosis": False, "budget": "ZERO"},
    "candidate-rebase": {"action": "REPAIR_CANDIDATE", "keep_review": False, "rerun_acceptance": False, "repair_diagnosis": True, "budget": "ONE"},
    "force-push": {"action": "ACCEPTANCE_REPAIR", "keep_review": True, "rerun_acceptance": False, "repair_diagnosis": False, "budget": "ZERO"},
    "revert": {"action": "ACCEPTANCE_REPAIR", "keep_review": True, "rerun_acceptance": False, "repair_diagnosis": False, "budget": "ZERO"},
    "preseal-drift": {"action": "RERUN_ACCEPTANCE", "keep_review": True, "rerun_acceptance": True, "repair_diagnosis": False, "budget": "ZERO"},
    "postseal-recovery": {"action": "RESUME_ADMIN", "keep_review": True, "rerun_acceptance": False, "repair_diagnosis": False, "budget": "ZERO"},
    "eligibility-refresh-drift": {"action": "RESUME_ADMIN", "keep_review": True, "rerun_acceptance": False, "repair_diagnosis": False, "budget": "ZERO"},
}


def schema() -> dict:
    item = {
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "action": {
                "type": "string",
                "enum": [
                    "INTEGRATE_NATIVE",
                    "PAUSE_CHECKS",
                    "REPAIR_CANDIDATE",
                    "ACCEPTANCE_REPAIR",
                    "RERUN_ACCEPTANCE",
                    "RESUME_ADMIN",
                ],
            },
            "keep_review": {"type": "boolean"},
            "rerun_acceptance": {"type": "boolean"},
            "repair_diagnosis": {"type": "boolean"},
            "budget": {"type": "string", "enum": ["ZERO", "ONE"]},
            "reason": {"type": "string"},
        },
        "required": [
            "id",
            "action",
            "keep_review",
            "rerun_acceptance",
            "repair_diagnosis",
            "budget",
            "reason",
        ],
        "additionalProperties": False,
    }
    return {"type": "object", "properties": {"results": {"type": "array", "items": item}}, "required": ["results"], "additionalProperties": False}


def prompt() -> str:
    return f"""Apply the evidence-binding, Integration, Acceptance, and repair-budget protocols to every case. Judge only immutable bindings and native evidence; do not invent file-overlap or timing gates. PUBLISH nothing and modify no files.

<domain>{reference("domain-and-state.md")}</domain>
<integration>{reference("repair-and-integration.md")}</integration>
<acceptance>{reference("acceptance.md")}</acceptance>
<cases>{json.dumps(CASES, indent=2)}</cases>
"""


class TargetDriftPromptTests(unittest.TestCase):
    def test_prompt_does_not_embed_expected_mapping(self) -> None:
        text = prompt()
        self.assertNotIn("clean-target-drift: INTEGRATE_NATIVE", text)
        self.assertNotIn("postseal-recovery: RESUME_ADMIN", text)


@unittest.skipUnless(RUN_AGENT_EVALS, "set FORGELOOP_RUN_AGENT_EVALS=1 to run Agent eval")
class TargetDriftAgentEvalTests(unittest.TestCase):
    def test_agent_routes_target_drift_by_evidence_binding(self) -> None:
        codex = shutil.which("codex")
        self.assertIsNotNone(codex)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            schema_path = root / "schema.json"
            result_path = root / "result.json"
            schema_path.write_text(json.dumps(schema()), encoding="utf-8")
            completed = subprocess.run(
                [
                    codex,
                    "exec",
                    "--ephemeral",
                    "--sandbox",
                    "read-only",
                    "--skip-git-repo-check",
                    "--color",
                    "never",
                    "--output-schema",
                    str(schema_path),
                    "--output-last-message",
                    str(result_path),
                    "-C",
                    str(root),
                    "-",
                ],
                input=prompt(),
                text=True,
                capture_output=True,
                timeout=300,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            actual = json.loads(result_path.read_text(encoding="utf-8"))["results"]

        self.assertEqual({item["id"] for item in actual}, set(EXPECTED))
        by_id = {item["id"]: item for item in actual}
        for case_id, expected in EXPECTED.items():
            with self.subTest(case=case_id):
                for field, value in expected.items():
                    self.assertEqual(by_id[case_id][field], value, field)
                self.assertTrue(by_id[case_id]["reason"])


if __name__ == "__main__":
    unittest.main()
