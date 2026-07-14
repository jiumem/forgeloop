from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SYNC_SCRIPT = PLUGIN_ROOT / "scripts" / "sync_upstream.py"
SPEC = importlib.util.spec_from_file_location("sync_upstream", SYNC_SCRIPT)
assert SPEC and SPEC.loader
SYNC = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = SYNC
SPEC.loader.exec_module(SYNC)

RUN_AGENT_EVALS = os.environ.get("FORGELOOP_RUN_AGENT_EVALS") == "1"


def generated_to_spec() -> str:
    config = SYNC.load_config()
    mapping = next(item for item in config["mappings"] if item["target"] == "to-spec")
    return SYNC.expected_files(config, mapping)[Path("SKILL.md")].decode()


CASES = [
    {
        "id": "self-contained",
        "candidate": """
            ## Testing Decisions
            ### Validation Entries
            - Name: Public API check
              Covers: DA-1
              Behavior: An authenticated user reads the saved value.
              Evidence: The public API test observes the saved value.

            ## Acceptance Prerequisites
            All Validation Entries can establish their own runtime conditions without separately supplied acceptance prerequisites.

            ## Delivery Acceptance
            - DA-1: An authenticated user can read the saved value.
        """,
        "verdict": "READY_TO_PUBLISH",
        "tracker_writes": "ALLOWED_AFTER_GATE",
    },
    {
        "id": "complete-prerequisite-list",
        "candidate": """
            ## Testing Decisions
            ### Validation Entries
            - Name: Staging API check
              Covers: DA-1
              Behavior: An authenticated user reads the staging value.
              Evidence: The public API response contains the staging value.

            ## Acceptance Prerequisites
            - Condition: A staging fixture exists.
              Required by: Staging API check
              Observation: Confirm through the fixture dashboard; permissions: Viewer; allowed side effects: None.
              Unavailable path: Recover the fixture; responsible role: Test operator.

            ## Delivery Acceptance
            - DA-1: An authenticated user can read the staging value.
        """,
        "verdict": "READY_TO_PUBLISH",
        "tracker_writes": "ALLOWED_AFTER_GATE",
    },
    {
        "id": "missing-entry",
        "candidate": """
            ## Testing Decisions
            Test the public API.

            ## Acceptance Prerequisites
            All Validation Entries can establish their own runtime conditions without separately supplied acceptance prerequisites.

            ## Delivery Acceptance
            - DA-1: An authenticated user can read the saved value.
        """,
        "verdict": "CONTEXT_INSUFFICIENT",
        "tracker_writes": "ZERO",
    },
    {
        "id": "missing-field",
        "candidate": """
            ## Testing Decisions
            ### Validation Entries
            - Name: Public API check
              Covers: DA-1
              Behavior: An authenticated user reads the saved value.

            ## Acceptance Prerequisites
            All Validation Entries can establish their own runtime conditions without separately supplied acceptance prerequisites.

            ## Delivery Acceptance
            - DA-1: An authenticated user can read the saved value.
        """,
        "verdict": "CONTEXT_INSUFFICIENT",
        "tracker_writes": "ZERO",
    },
    {
        "id": "invalid-reference",
        "candidate": """
            ## Testing Decisions
            ### Validation Entries
            - Name: Public API check
              Covers: DA-2
              Behavior: An authenticated user reads the saved value.
              Evidence: The public API test observes the saved value.

            ## Acceptance Prerequisites
            All Validation Entries can establish their own runtime conditions without separately supplied acceptance prerequisites.

            ## Delivery Acceptance
            - DA-1: An authenticated user can read the saved value.
        """,
        "verdict": "CONTEXT_INSUFFICIENT",
        "tracker_writes": "ZERO",
    },
    {
        "id": "both-prerequisite-forms",
        "candidate": """
            ## Testing Decisions
            ### Validation Entries
            - Name: Public API check
              Covers: DA-1
              Behavior: An authenticated user reads the saved value.
              Evidence: The public API test observes the saved value.

            ## Acceptance Prerequisites
            All Validation Entries can establish their own runtime conditions without separately supplied acceptance prerequisites.
            - Condition: A staging fixture exists.
              Required by: Public API check
              Observation: Confirm through the fixture dashboard; permissions: Viewer; allowed side effects: None.
              Unavailable path: Request fixture recovery; responsible role: Test operator.

            ## Delivery Acceptance
            - DA-1: An authenticated user can read the saved value.
        """,
        "verdict": "CONTEXT_INSUFFICIENT",
        "tracker_writes": "ZERO",
    },
    {
        "id": "contradictory-self-contained-form",
        "candidate": """
            ## Testing Decisions
            The validation requires a separately supplied staging credential.
            ### Validation Entries
            - Name: Public API check
              Covers: DA-1
              Behavior: An authenticated user reads the saved value.
              Evidence: The public API test observes the saved value.

            ## Acceptance Prerequisites
            All Validation Entries can establish their own runtime conditions without separately supplied acceptance prerequisites.

            ## Delivery Acceptance
            - DA-1: An authenticated user can read the saved value.
        """,
        "verdict": "CONTEXT_INSUFFICIENT",
        "tracker_writes": "ZERO",
    },
]


def output_schema() -> dict:
    result = {
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "verdict": {
                "type": "string",
                "enum": ["READY_TO_PUBLISH", "CONTEXT_INSUFFICIENT"],
            },
            "tracker_writes": {
                "type": "string",
                "enum": ["ALLOWED_AFTER_GATE", "ZERO"],
            },
            "gaps": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["id", "verdict", "tracker_writes", "gaps"],
        "additionalProperties": False,
    }
    return {
        "type": "object",
        "properties": {"results": {"type": "array", "items": result}},
        "required": ["results"],
        "additionalProperties": False,
    }


def evaluation_prompt() -> str:
    candidates = [
        {"id": case["id"], "candidate": textwrap.dedent(case["candidate"]).strip()}
        for case in CASES
    ]
    return f"""You are evaluating the Agent behavior of the `to-spec` Skill below.

Apply only its Validation Entries and Acceptance Prerequisites publication gate. Assume every
other gate, user approval, Tracker permission, and conflict check passes. A temporary mock Tracker
is available in `tracker/`. For each candidate:

- when the gate passes, create exactly one empty `tracker/<id>.published` file, then return
  READY_TO_PUBLISH and ALLOWED_AFTER_GATE;
- when it fails, do not create a file, then return CONTEXT_INSUFFICIENT and ZERO;
- list every detected gap for a failure, and use an empty gaps list for a success.

Do not create any other file, inspect the environment, or use the network.

<to-spec-skill>
{generated_to_spec()}
</to-spec-skill>

<candidates>
{json.dumps(candidates, indent=2)}
</candidates>
"""


@unittest.skipUnless(
    RUN_AGENT_EVALS,
    "set FORGELOOP_RUN_AGENT_EVALS=1 to run the authenticated Codex Agent eval",
)
class ToSpecAgentEvalTests(unittest.TestCase):
    def test_validation_gate_scenarios_and_zero_writes(self) -> None:
        codex = shutil.which("codex")
        self.assertIsNotNone(codex, "Codex CLI is required for Agent evals")

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tracker = root / "tracker"
            tracker.mkdir()
            schema_path = root / "schema.json"
            result_path = root / "result.json"
            schema_path.write_text(json.dumps(output_schema()), encoding="utf-8")
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
            published = {path.stem for path in tracker.glob("*.published")}

        self.assertEqual({item["id"] for item in actual}, {case["id"] for case in CASES})
        self.assertEqual(
            published,
            {case["id"] for case in CASES if case["tracker_writes"] == "ALLOWED_AFTER_GATE"},
        )
        by_id = {item["id"]: item for item in actual}
        for case in CASES:
            with self.subTest(case=case["id"]):
                result = by_id[case["id"]]
                self.assertEqual(result["verdict"], case["verdict"])
                self.assertEqual(result["tracker_writes"], case["tracker_writes"])
                if case["verdict"] == "READY_TO_PUBLISH":
                    self.assertEqual(result["gaps"], [])
                else:
                    self.assertTrue(result["gaps"])


if __name__ == "__main__":
    unittest.main()
