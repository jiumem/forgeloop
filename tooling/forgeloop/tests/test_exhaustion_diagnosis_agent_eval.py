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
SKILL_ROOT = PLUGIN_ROOT / "skills" / "run-initiative"
RUN_AGENT_EVALS = os.environ.get("FORGELOOP_RUN_AGENT_EVALS") == "1"


def protocol(name: str) -> str:
    return (SKILL_ROOT / "references" / name).read_text(encoding="utf-8")


CASES = [
    {
        "id": "credible-scale-correction",
        "cycle_position": "CYCLE_1_EXHAUSTED",
        "evidence": """
            The initial reviewed Candidate satisfied five of seven public outcomes through the
            existing backend resolver. Three repairs added a second store, a reconciliation layer,
            and internal read-count tests, none required by an approved criterion; the two original
            failures remain. The correction removes those unsupported mechanisms and repairs the
            remaining resolver path through the existing owner. The same public conformance test
            makes both the prediction and failure condition observable.
        """,
    },
    {
        "id": "wording-only-retry",
        "cycle_position": "CYCLE_1_EXHAUSTED",
        "evidence": """
            The proposed next direction renames the previous mechanism and repeats the same edits.
            The public failure, Blocking Findings, shared mechanism, and authoritative uncertainty
            are unchanged from cycle start to cycle end.
        """,
    },
    {
        "id": "logging-without-new-fact",
        "cycle_position": "CYCLE_1_EXHAUSTED",
        "evidence": """
            The cycle added logs but they did not answer the declared uncertainty. The next proposal
            is to add more logs without naming a new causal intervention, prediction, or fact that
            would falsify the old mechanism. Public behavior and Findings are unchanged.
        """,
    },
    {
        "id": "different-mechanism-zero-progress",
        "cycle_position": "CYCLE_1_EXHAUSTED",
        "evidence": """
            A materially different in-Scope intervention is conceivable, but the exhausted cycle
            cannot map it to an exact approved criterion, does not name unsupported mechanisms to
            remove, and offers no public prediction that distinguishes it from the failed approach.
        """,
    },
    {
        "id": "progress-regressed",
        "cycle_position": "CYCLE_1_EXHAUSTED",
        "evidence": """
            A public test passed temporarily during the cycle, then failed again at the final Head.
            The cycle-end Candidate has the same Blocking Findings and shared mechanism as the cycle
            start. The proposal relies on that temporary pass as its only progress evidence.
        """,
    },
    {
        "id": "contract-change-required",
        "cycle_position": "CYCLE_1_EXHAUSTED",
        "evidence": """
            The only correct implementation needs a new user-visible outcome that is absent from the
            effective Spec, Ticket Acceptance criteria, and approved interface. No implementation
            inside the current contract can honestly express the required result.
        """,
    },
    {
        "id": "cycle-two-exhausted",
        "cycle_position": "CYCLE_2_EXHAUSTED",
        "evidence": """
            The correction cycle used all three effective repair rounds. One approved public
            outcome still fails, and satisfying it needs no contract change. A further local idea
            exists, but the protocol permits no third cycle or second automatic renewal.
        """,
    },
]


EXPECTED = {
    "credible-scale-correction": "AUTO_REPAIR_RENEWAL",
    "wording-only-retry": "IMPLEMENTATION_BLOCKED",
    "logging-without-new-fact": "IMPLEMENTATION_BLOCKED",
    "different-mechanism-zero-progress": "IMPLEMENTATION_BLOCKED",
    "progress-regressed": "IMPLEMENTATION_BLOCKED",
    "contract-change-required": "CONTRACT_BLOCKER",
    "cycle-two-exhausted": "IMPLEMENTATION_BLOCKED",
}


def output_schema() -> dict:
    item = {
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "recommendation": {
                "type": "string",
                "enum": [
                    "AUTO_REPAIR_RENEWAL",
                    "IMPLEMENTATION_BLOCKED",
                    "CONTRACT_BLOCKER",
                ],
            },
            "cycle_position": {
                "type": "string",
                "enum": ["CYCLE_1_EXHAUSTED", "CYCLE_2_EXHAUSTED"],
            },
            "prior_mechanism": {"type": "string"},
            "falsifying_evidence": {"type": "string"},
            "new_causal_hypothesis": {"type": "string"},
            "observable_prediction": {"type": "string"},
            "falsification_condition": {"type": "string"},
            "scope_assessment": {"type": "string"},
            "observed_progress": {"type": "string"},
            "initial_candidate_comparison": {"type": "string"},
            "unsupported_mechanisms": {"type": "string"},
            "correction_plan": {"type": "string"},
        },
        "required": [
            "id",
            "recommendation",
            "cycle_position",
            "prior_mechanism",
            "falsifying_evidence",
            "new_causal_hypothesis",
            "observable_prediction",
            "falsification_condition",
            "scope_assessment",
            "observed_progress",
            "initial_candidate_comparison",
            "unsupported_mechanisms",
            "correction_plan",
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
    cases = [
        {
            "id": case["id"],
            "cycle_position": case["cycle_position"],
            "evidence": textwrap.dedent(case["evidence"]).strip(),
        }
        for case in CASES
    ]
    return f"""Apply the Exhaustion Diagnosis and repair-cycle protocols to every case.
Read each case as semantic evidence, not as keywords or Boolean flags. Recommend the one automatic
correction cycle only after Cycle 1, when an authority-bound violation remains and a materially
different, in-Scope, falsifiable correction converges or reduces the design. Never recommend renewal
after Cycle 2. Explain every field even when the recommendation is blocked. Modify nothing and do not
use network.

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
{json.dumps(cases, indent=2)}
</cases>
"""


class ExhaustionDiagnosisEvalPromptTests(unittest.TestCase):
    def test_prompt_does_not_embed_expected_recommendations(self) -> None:
        prompt = evaluation_prompt()

        for case_id, recommendation in EXPECTED.items():
            self.assertNotIn(f"{case_id}: {recommendation}", prompt)


@unittest.skipUnless(
    RUN_AGENT_EVALS,
    "set FORGELOOP_RUN_AGENT_EVALS=1 to run the authenticated Codex Agent eval",
)
class ExhaustionDiagnosisAgentEvalTests(unittest.TestCase):
    def test_agent_routes_semantic_exhaustion_evidence(self) -> None:
        codex = shutil.which("codex")
        self.assertIsNotNone(codex, "Codex CLI is required for Agent evals")

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            schema_path = root / "schema.json"
            result_path = root / "result.json"
            schema_path.write_text(json.dumps(output_schema()), encoding="utf-8")
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

        self.assertEqual({item["id"] for item in actual}, set(EXPECTED))
        for item in actual:
            with self.subTest(case=item["id"]):
                self.assertEqual(item["recommendation"], EXPECTED[item["id"]])
                for field, value in item.items():
                    if field not in {"id", "recommendation"}:
                        self.assertTrue(value.strip(), field)


if __name__ == "__main__":
    unittest.main()
