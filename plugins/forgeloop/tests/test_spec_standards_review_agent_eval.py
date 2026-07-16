from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
METADATA_PATH = PLUGIN_ROOT / "config" / "skill-metadata.json"
RUN_AGENT_EVALS = os.environ.get("FORGELOOP_RUN_AGENT_EVALS") == "1"

CASES = [
    {
        "id": "review-pr",
        "request": "Review pull request #42 against its accepted Spec and repository standards.",
        "expected": "LOAD",
    },
    {
        "id": "review-module",
        "request": "Review the implemented authentication module against docs/auth-spec.md and repository standards.",
        "expected": "LOAD",
    },
    {
        "id": "agent-review",
        "request": "Implementation is complete. Review the frozen candidate files against the supplied Spec and standards.",
        "expected": "LOAD",
    },
    {
        "id": "standards-only",
        "request": "Review src/cache.py for repository standards. No originating Spec exists.",
        "expected": "LOAD",
    },
    {
        "id": "investigate-trigger",
        "request": "Investigate which code paths can trigger automatic retry.",
        "expected": "DO_NOT_LOAD",
    },
    {
        "id": "impact-analysis",
        "request": "Analyze which modules could be affected by commit abc123.",
        "expected": "DO_NOT_LOAD",
    },
    {
        "id": "debug-failure",
        "request": "Find why checkout fails after the latest deployment.",
        "expected": "DO_NOT_LOAD",
    },
    {
        "id": "architecture-exploration",
        "request": "Explore the codebase for misplaced module boundaries.",
        "expected": "DO_NOT_LOAD",
    },
]


def spec_standards_review_description() -> str:
    metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    return metadata["spec-standards-review"]["description"]


def output_schema() -> dict:
    item = {
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "decision": {"type": "string", "enum": ["LOAD", "DO_NOT_LOAD"]},
        },
        "required": ["id", "decision"],
        "additionalProperties": False,
    }
    return {
        "type": "object",
        "properties": {"results": {"type": "array", "items": item}},
        "required": ["results"],
        "additionalProperties": False,
    }


def evaluation_prompt() -> str:
    requests = [{"id": case["id"], "request": case["request"]} for case in CASES]
    return f"""Decide whether the Skill should load for each request using only its trigger
description. Return one decision for every request. Do not inspect files, call tools, or use the
network.

<description>
{spec_standards_review_description()}
</description>

<requests>
{json.dumps(requests, indent=2)}
</requests>
"""


class SpecStandardsReviewEvalPromptTests(unittest.TestCase):
    def test_prompt_does_not_embed_expected_decisions(self) -> None:
        prompt = evaluation_prompt()

        for case in CASES:
            self.assertNotIn(f'{case["id"]}: {case["expected"]}', prompt)
        for expected in {case["expected"] for case in CASES}:
            self.assertNotIn(expected, prompt)


@unittest.skipUnless(
    RUN_AGENT_EVALS,
    "set FORGELOOP_RUN_AGENT_EVALS=1 to run the authenticated Codex Agent eval",
)
class SpecStandardsReviewAgentEvalTests(unittest.TestCase):
    def test_description_routes_review_without_absorbing_investigation(self) -> None:
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
                timeout=180,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            result = json.loads(result_path.read_text(encoding="utf-8"))

        observed = {item["id"]: item["decision"] for item in result["results"]}
        expected = {case["id"]: case["expected"] for case in CASES}
        self.assertEqual(observed, expected)


if __name__ == "__main__":
    unittest.main()
