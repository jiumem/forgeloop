from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


TOOLING_ROOT = Path(__file__).resolve().parents[1]
METADATA_PATH = TOOLING_ROOT / "config" / "skill-metadata.json"
RUN_AGENT_EVALS = os.environ.get("FORGELOOP_RUN_AGENT_EVALS") == "1"

CASES = [
    {
        "id": "large-ticket",
        "request": "Use run-initiative to deliver Tracker Ticket #81. It is a spec-level migration with several coherent implementation slices.",
        "expected": "LOAD",
    },
    {
        "id": "formal-spec",
        "request": "Use run-initiative to execute formal Tracker Spec #70 and its approved Tickets.",
        "expected": "LOAD",
    },
    {
        "id": "bounded-initiative",
        "request": "Use run-initiative to execute Initiative #60, which contains three approved Specs and no other Initiative.",
        "expected": "LOAD",
    },
    {
        "id": "small-ticket",
        "request": "Should I use run-initiative for a tiny copy fix in one existing file with one focused check?",
        "expected": "DO_NOT_RECOMMEND",
    },
    {
        "id": "multiple-initiatives",
        "request": "Use one run-initiative invocation to execute Initiatives #60, #61, and #62 together.",
        "expected": "DO_NOT_RECOMMEND",
    },
    {
        "id": "ordinary-coding",
        "request": "Implement this small function and run its unit test.",
        "expected": "DO_NOT_LOAD",
    },
]


def description() -> str:
    metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    return metadata["run-initiative"]["description"]


def output_schema() -> dict:
    item = {
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "decision": {
                "type": "string",
                "enum": ["LOAD", "DO_NOT_RECOMMEND", "DO_NOT_LOAD"],
            },
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
    return f"""Decide how the Skill's trigger description applies to every request. LOAD means the
request is a supported explicit invocation. DO_NOT_RECOMMEND means the request names the Skill but
the description explicitly says not to recommend it. DO_NOT_LOAD means the request does not invoke
or warrant the Skill. Use only the description. Do not inspect files, call tools, or use the network.

<description>
{description()}
</description>

<requests>
{json.dumps(requests, indent=2)}
</requests>
"""


class RunInitiativeEvalPromptTests(unittest.TestCase):
    def test_prompt_does_not_embed_expected_decisions(self) -> None:
        prompt = evaluation_prompt()

        for case in CASES:
            self.assertNotIn(f'{case["id"]}: {case["expected"]}', prompt)


@unittest.skipUnless(
    RUN_AGENT_EVALS,
    "set FORGELOOP_RUN_AGENT_EVALS=1 to run the authenticated Codex Agent eval",
)
class RunInitiativeAgentEvalTests(unittest.TestCase):
    def test_description_routes_supported_delivery_shapes_and_boundaries(self) -> None:
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
