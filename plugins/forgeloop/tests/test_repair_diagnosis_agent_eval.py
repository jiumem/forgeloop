from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = PLUGIN_ROOT / "skills" / "run-initiative"
RUN_AGENT_EVALS = os.environ.get("FORGELOOP_RUN_AGENT_EVALS") == "1"


def protocol(name: str) -> str:
    return (SKILL_ROOT / "references" / name).read_text(encoding="utf-8")


CASES = [
    {
        "id": "local-repair",
        "evidence": """
            A public formatter emits one wrong delimiter. The existing formatter interface can
            express the correct value, it is the only fact source, and its public CLI test proves
            the behavior. The fix stays inside Ticket Scope.
        """,
    },
    {
        "id": "structural-repair",
        "evidence": """
            API and worker each derive authorization independently and disagree on retry. The
            Ticket Scope contains both paths and the shared authorization interface. Correctness
            requires converging both paths on that interface and proving the public API result.
        """,
    },
    {
        "id": "contract-blocker",
        "evidence": """
            The only correct failure result is a new user-visible outcome absent from the Spec and
            Ticket Acceptance criteria. Adding it would change the approved public contract.
        """,
    },
    {
        "id": "missing-field",
        "evidence": """
            A proposed diagnosis declares LOCAL_REPAIR and supplies mechanism, evidence,
            repair_seam, convergence, and scope_check, but omits proof. The Scheduler is deciding
            whether code repair may start.
        """,
    },
    {
        "id": "candidate-check",
        "evidence": """
            A candidate-caused public conformance check exposes an off-by-one error. One existing
            interface owns the value, no parallel path exists, the repair is in Scope, and rerunning
            that public check proves it.
        """,
    },
    {
        "id": "unsupported-downgrade",
        "evidence": """
            The prior diagnosis was STRUCTURAL_REPAIR because two in-Scope parsers were parallel
            fact sources. The repair changed neither source and the same Findings remain. No new
            evidence exists, but the new proposal calls the work LOCAL_REPAIR.
        """,
    },
    {
        "id": "shared-mechanism",
        "evidence": """
            On the third diagnosis, three different finding_id values all trace to two competing
            lifecycle owners. Both implementations and their shared ownership Seam are in Ticket
            Scope. The public cancellation behavior can prove convergence.
        """,
    },
]


EXPECTED = {
    "local-repair": ("LOCAL_REPAIR", "AUTHORIZE_LOCAL", True, False, "ONE_IF_CODE_CHANGES"),
    "structural-repair": (
        "STRUCTURAL_REPAIR",
        "AUTHORIZE_STRUCTURAL",
        True,
        True,
        "ONE_IF_CODE_CHANGES",
    ),
    "contract-blocker": ("CONTRACT_BLOCKER", "PAUSE_CONTRACT", False, False, "ZERO"),
    "missing-field": ("LOCAL_REPAIR", "REJECT_DIAGNOSIS", False, False, "ZERO"),
    "candidate-check": ("LOCAL_REPAIR", "AUTHORIZE_LOCAL", True, False, "ONE_IF_CODE_CHANGES"),
    "unsupported-downgrade": ("LOCAL_REPAIR", "REJECT_DIAGNOSIS", False, False, "ZERO"),
    "shared-mechanism": (
        "STRUCTURAL_REPAIR",
        "AUTHORIZE_STRUCTURAL",
        True,
        True,
        "ONE_IF_CODE_CHANGES",
    ),
}


def output_schema() -> dict:
    item = {
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "classification": {
                "type": "string",
                "enum": [
                    "LOCAL_REPAIR",
                    "STRUCTURAL_REPAIR",
                    "CONTRACT_BLOCKER",
                ],
            },
            "route": {
                "type": "string",
                "enum": [
                    "AUTHORIZE_LOCAL",
                    "AUTHORIZE_STRUCTURAL",
                    "PAUSE_CONTRACT",
                    "REJECT_DIAGNOSIS",
                ],
            },
            "authorize_code": {"type": "boolean"},
            "invoke_codebase_design": {"type": "boolean"},
            "budget_effect": {
                "type": "string",
                "enum": ["ZERO", "ONE_IF_CODE_CHANGES"],
            },
            "reason": {"type": "string"},
        },
        "required": [
            "id",
            "classification",
            "route",
            "authorize_code",
            "invoke_codebase_design",
            "budget_effect",
            "reason",
        ],
        "additionalProperties": False,
    }
    return {
        "type": "object",
        "properties": {"results": {"type": "array", "items": item}},
        "required": ["results"],
        "additionalProperties": False,
    }


def evaluation_prompt() -> str:
    candidates = [
        {"id": case["id"], "evidence": textwrap.dedent(case["evidence"]).strip()}
        for case in CASES
    ]
    return f"""Apply the Repair Diagnosis, Scheduler routing, and repair budget protocols below
to every case. Judge the complete mechanism and Scope. Classification uses only the protocol's
three values. When a supplied diagnosis is incomplete or violates the history rule, preserve its
declared classification, choose REJECT_DIAGNOSIS, and do not authorize repair. `authorize_code`
means the Scheduler may start a later code-changing turn; diagnosis itself remains read-only. Use
ONE_IF_CODE_CHANGES only when a later authorized modification would consume one shared repair
round; otherwise use ZERO. Explain the decisive evidence briefly.

A mock Tracker exists at `tracker/`. Do not modify it or any other file, and do not use network.

<coder-protocol>
{protocol("coder.md")}
</coder-protocol>
<scheduler-protocol>
{protocol("scheduler.md")}
</scheduler-protocol>
<repair-protocol>
{protocol("repair-and-integration.md")}
</repair-protocol>
<cases>
{json.dumps(candidates, indent=2)}
</cases>
"""


def observed_entries(root: Path) -> set[str]:
    return {path.relative_to(root).as_posix() for path in root.rglob("*")}


class RepairDiagnosisEvalPromptTests(unittest.TestCase):
    def test_prompt_does_not_embed_expected_case_mapping(self) -> None:
        prompt = evaluation_prompt()

        self.assertNotIn("local-repair: LOCAL_REPAIR", prompt)
        self.assertNotIn("structural-repair: STRUCTURAL_REPAIR", prompt)
        self.assertNotIn("contract-blocker: CONTRACT_BLOCKER", prompt)


@unittest.skipUnless(
    RUN_AGENT_EVALS,
    "set FORGELOOP_RUN_AGENT_EVALS=1 to run the authenticated Codex Agent eval",
)
class RepairDiagnosisAgentEvalTests(unittest.TestCase):
    def test_agent_classifies_repairs_and_keeps_diagnosis_read_only(self) -> None:
        codex = shutil.which("codex")
        self.assertIsNotNone(codex, "Codex CLI is required for Agent evals")

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tracker = root / "tracker"
            tracker.mkdir()
            schema_path = root / "schema.json"
            result_path = root / "result.json"
            schema_path.write_text(json.dumps(output_schema()), encoding="utf-8")
            entries_before = observed_entries(root)
            completed = subprocess.run(
                [
                    codex,
                    "exec",
                    "--ephemeral",
                    "--sandbox",
                    "workspace-write",
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
                input=evaluation_prompt(),
                text=True,
                capture_output=True,
                timeout=300,
                check=False,
            )
            self.assertEqual(
                completed.returncode,
                0,
                f"Codex Agent eval failed:\n{completed.stdout}\n{completed.stderr}",
            )
            actual = json.loads(result_path.read_text(encoding="utf-8"))["results"]
            tracker_entries = observed_entries(tracker)
            unexpected_entries = observed_entries(root) - entries_before - {"result.json"}

        self.assertEqual(tracker_entries, set())
        self.assertEqual(unexpected_entries, set())
        self.assertEqual({item["id"] for item in actual}, set(EXPECTED))
        by_id = {item["id"]: item for item in actual}
        for case_id, expected in EXPECTED.items():
            with self.subTest(case=case_id):
                result = by_id[case_id]
                self.assertEqual(
                    (
                        result["classification"],
                        result["route"],
                        result["authorize_code"],
                        result["invoke_codebase_design"],
                        result["budget_effect"],
                    ),
                    expected,
                )
                self.assertTrue(result["reason"])


if __name__ == "__main__":
    unittest.main()
