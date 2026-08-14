from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[3] / "plugins" / "forgeloop"
REFERENCE_ROOT = PLUGIN_ROOT / "skills" / "run-initiative" / "references"
RUN_AGENT_EVALS = os.environ.get("FORGELOOP_RUN_AGENT_EVALS") == "1"
AGENT_EVAL_MODEL = os.environ.get("FORGELOOP_AGENT_EVAL_MODEL")


def protocol(name: str) -> str:
    return (REFERENCE_ROOT / name).read_text(encoding="utf-8")


CASES = [
    {
        "id": "review-undeclared-cross-process",
        "role": "SPEC_REVIEWER",
        "evidence": """
            The approved product and deployment model has one worker. The Candidate satisfies the
            public save/read journey and all declared failure behavior. A concern asks for a
            distributed lock because a hypothetical future deployment might run multiple workers.
        """,
    },
    {
        "id": "review-approved-concurrent-retry",
        "role": "SPEC_REVIEWER",
        "evidence": """
            The approved outcome says a retried payment produces one stable charge, and the
            approved operating model allows two workers to receive the same retry. The Candidate
            performs the charge independently in both workers, producing two observable charges.
        """,
    },
    {
        "id": "review-zero-residue-hardening",
        "role": "SPEC_REVIEWER",
        "evidence": """
            The approved recovery result requires no invalid durable product fact. The Candidate
            satisfies that result, but a crash can leave an unreferenced temporary file that no
            supported reader or recovery path observes. A concern demands global reference counts
            so every crash instruction leaves zero physical residue.
        """,
    },
    {
        "id": "review-residue-corrupts-recovery",
        "role": "SPEC_REVIEWER",
        "evidence": """
            The approved result requires a failed publish to recover and retry without reporting a
            false success. After a reachable crash, the Candidate leaves a marker that the approved
            startup recovery path treats as committed, so the public command reports success for
            data that was never published.
        """,
    },
    {
        "id": "review-extra-fixture-metadata",
        "role": "SPEC_REVIEWER",
        "evidence": """
            The Candidate's public command produces the approved result and the fixture records the
            decisive product output. A concern asks the fixture to persist extra internal context
            identifiers for architectural symmetry, but names no supported failure or observable
            result that could change.
        """,
    },
    {
        "id": "review-self-authored-evidence",
        "role": "SPEC_REVIEWER",
        "evidence": """
            The approved result requires the product to reject an unauthorized operation. The test
            adapter derives the expected rejection directly from its request and returns that value
            without invoking the product authority decision. The test then accepts the adapter's
            own value as proof.
        """,
    },
    {
        "id": "review-broad-adr-preference",
        "role": "SPEC_REVIEWER",
        "evidence": """
            A broad ADR encourages convergence when parallel facts affect behavior. The Candidate
            has one fact source and satisfies every approved public outcome. A concern cites the ADR
            title to require a new owner and lifecycle solely because that architecture looks more
            uniform.
        """,
    },
    {
        "id": "review-missing-fixed-input",
        "role": "SPEC_REVIEWER",
        "evidence": """
            The supplied Ticket references an applicable ADR revision, but that exact revision is
            unreadable. The Reviewer cannot establish the effective contract for the frozen Head.
        """,
    },
    {
        "id": "coder-unapproved-durability",
        "role": "CODER_DIAGNOSIS",
        "evidence": """
            The only Blocking Finding is on the Spec axis. The approved single-process result is
            already proven through the public Seam. The Finding demands a replicated durable store
            for a hypothetical regional outage absent from the approved operating and failure
            model, and no approved outcome changes without it.
        """,
    },
    {
        "id": "coder-local-observable-error",
        "role": "CODER_DIAGNOSIS",
        "evidence": """
            A Spec Finding shows that the public formatter emits the wrong delimiter required by a
            Ticket Acceptance criterion. One existing formatter owns the value, no parallel source
            exists, and one in-Scope edit plus the same public command proves the result.
        """,
    },
    {
        "id": "coder-necessary-convergence",
        "role": "CODER_DIAGNOSIS",
        "evidence": """
            The approved public authorization result must be stable across API and retry worker.
            The Candidate has two in-Scope authority fact sources that produce conflicting public
            outcomes for a reachable approved retry. Converging them on the existing authority
            interface is necessary and publicly testable.
        """,
    },
]


EXPECTED = {
    "review-undeclared-cross-process": "PASS",
    "review-approved-concurrent-retry": "REPAIR_REQUIRED",
    "review-zero-residue-hardening": "PASS",
    "review-residue-corrupts-recovery": "REPAIR_REQUIRED",
    "review-extra-fixture-metadata": "PASS",
    "review-self-authored-evidence": "REPAIR_REQUIRED",
    "review-broad-adr-preference": "PASS",
    "review-missing-fixed-input": "REVIEW_BLOCKED",
    "coder-unapproved-durability": "NO_REPAIR",
    "coder-local-observable-error": "LOCAL_REPAIR",
    "coder-necessary-convergence": "STRUCTURAL_REPAIR",
}


def output_schema() -> dict:
    item = {
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "decision": {
                "type": "string",
                "enum": [
                    "PASS",
                    "REPAIR_REQUIRED",
                    "REVIEW_BLOCKED",
                    "NO_REPAIR",
                    "LOCAL_REPAIR",
                    "STRUCTURAL_REPAIR",
                    "CONTRACT_BLOCKER",
                ],
            },
            "reason": {"type": "string"},
        },
        "required": ["id", "decision", "reason"],
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
        {
            "id": case["id"],
            "role": case["role"],
            "evidence": textwrap.dedent(case["evidence"]).strip(),
        }
        for case in CASES
    ]
    return f"""Apply the shared Delivery Judgment Contract and the matching role protocol to
every case. A SPEC_REVIEWER returns PASS when no Blocking Finding is justified,
REPAIR_REQUIRED for an authority-bound observable violation, and REVIEW_BLOCKED only for invalid
fixed input. A CODER_DIAGNOSIS independently validates the Finding and returns NO_REPAIR,
LOCAL_REPAIR, STRUCTURAL_REPAIR, or CONTRACT_BLOCKER. Assume every unmentioned contract input and
permission is valid. Do not inspect files, call tools, or use network. Explain the decisive
necessity-chain evidence briefly.

<delivery-judgment>
{protocol("delivery-judgment.md")}
</delivery-judgment>
<reviewer-protocol>
{protocol("reviewers.md")}
</reviewer-protocol>
<coder-protocol>
{protocol("coder.md")}
</coder-protocol>
<cases>
{json.dumps(candidates, indent=2)}
</cases>
"""


class DeliveryValueEvalPromptTests(unittest.TestCase):
    def test_prompt_does_not_embed_expected_decisions(self) -> None:
        prompt = evaluation_prompt()

        for case_id, decision in EXPECTED.items():
            self.assertNotIn(f"{case_id}: {decision}", prompt)


@unittest.skipUnless(
    RUN_AGENT_EVALS,
    "set FORGELOOP_RUN_AGENT_EVALS=1 to run the authenticated Codex Agent eval",
)
class DeliveryValueAgentEvalTests(unittest.TestCase):
    def test_agent_preserves_true_findings_and_rejects_unnecessary_complexity(self) -> None:
        codex = shutil.which("codex")
        self.assertIsNotNone(codex, "Codex CLI is required for Agent evals")

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            schema_path = root / "schema.json"
            result_path = root / "result.json"
            schema_path.write_text(json.dumps(output_schema()), encoding="utf-8")
            command = [
                codex,
                "exec",
                "--ephemeral",
                "--sandbox",
                "read-only",
                "--skip-git-repo-check",
                "--output-schema",
                str(schema_path),
                "--output-last-message",
                str(result_path),
                "-",
            ]
            if AGENT_EVAL_MODEL:
                command[2:2] = ["--model", AGENT_EVAL_MODEL]
            completed = subprocess.run(
                command,
                cwd=root,
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
            payload = json.loads(result_path.read_text(encoding="utf-8"))

        observed = {item["id"]: item["decision"] for item in payload["results"]}
        self.assertEqual(observed, EXPECTED)


if __name__ == "__main__":
    unittest.main()
