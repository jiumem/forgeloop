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


def reference(name: str) -> str:
    return (SKILL_ROOT / "references" / name).read_text(encoding="utf-8")


CASES = [
    {
        "id": "github-new",
        "evidence": "GitHub has no matching key. The complete Payload is ready outside the worktree.",
    },
    {
        "id": "gitlab-new",
        "evidence": "GitLab has no matching key. The opaque Payload contains $(touch sentinel).",
    },
    {
        "id": "local-new",
        "evidence": "Local Markdown has no matching key and the owned lock is valid.",
    },
    {
        "id": "exact-existing",
        "evidence": "One record has the same key, identical normalized body, and one native envelope.",
    },
    {
        "id": "ambiguous-exact",
        "evidence": "The create result was ambiguous; query found one identical record and envelope.",
    },
    {
        "id": "ambiguous-none",
        "evidence": "A GitHub create result was ambiguous; the required query found no record.",
    },
    {
        "id": "key-conflict",
        "evidence": "The same idempotency key exists with a different complete Payload body.",
    },
    {
        "id": "duplicate-identical",
        "evidence": "Two records have the same idempotency key and identical complete Payload bodies.",
    },
    {
        "id": "truncated-readback",
        "evidence": "Create reported success, but GET by native ID returns a truncated body.",
    },
    {
        "id": "newline-only",
        "evidence": "The unique body differs only by CRLF and repeated terminal line breaks.",
    },
    {
        "id": "uncertain-supersede",
        "evidence": "Transport is uncertain and no confirmed historical error or replacement evidence exists.",
    },
]


EXPECTED = {
    "github-new": {
        "result": "PUBLISH",
        "transport": "GH_BODY_FILE",
        "advance": False,
        "retry": False,
        "supersede": False,
    },
    "gitlab-new": {
        "result": "PUBLISH",
        "transport": "GLAB_API_FILE_FIELD",
        "advance": False,
        "retry": False,
        "supersede": False,
    },
    "local-new": {
        "result": "PUBLISH",
        "transport": "LOCAL_NON_SHELL_APPEND",
        "advance": False,
        "retry": False,
        "supersede": False,
    },
    "exact-existing": {
        "result": "CONFIRMED",
        "transport": "NONE",
        "advance": True,
        "retry": False,
        "supersede": False,
    },
    "ambiguous-exact": {
        "result": "CONFIRMED",
        "transport": "NONE",
        "advance": True,
        "retry": False,
        "supersede": False,
    },
    "ambiguous-none": {
        "result": "PUBLISH",
        "transport": "GH_BODY_FILE",
        "advance": False,
        "retry": True,
        "supersede": False,
    },
    "key-conflict": {
        "result": "RECOVERY_CONFLICT",
        "transport": "NONE",
        "advance": False,
        "retry": False,
        "supersede": False,
    },
    "duplicate-identical": {
        "result": "RECOVERY_CONFLICT",
        "transport": "NONE",
        "advance": False,
        "retry": False,
        "supersede": False,
    },
    "truncated-readback": {
        "result": "UNCONFIRMED",
        "transport": "NONE",
        "advance": False,
        "retry": False,
        "supersede": False,
    },
    "newline-only": {
        "result": "CONFIRMED",
        "transport": "NONE",
        "advance": True,
        "retry": False,
        "supersede": False,
    },
    "uncertain-supersede": {
        "result": "UNCONFIRMED",
        "transport": "NONE",
        "advance": False,
        "retry": False,
        "supersede": False,
    },
}


def output_schema() -> dict:
    item = {
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "result": {
                "type": "string",
                "enum": ["PUBLISH", "CONFIRMED", "UNCONFIRMED", "RECOVERY_CONFLICT"],
            },
            "transport": {
                "type": "string",
                "enum": [
                    "GH_BODY_FILE",
                    "GLAB_API_FILE_FIELD",
                    "LOCAL_NON_SHELL_APPEND",
                    "NONE",
                ],
            },
            "advance": {"type": "boolean"},
            "retry": {"type": "boolean"},
            "supersede": {"type": "boolean"},
            "reason": {"type": "string"},
        },
        "required": ["id", "result", "transport", "advance", "retry", "supersede", "reason"],
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
        {"id": case["id"], "evidence": textwrap.dedent(case["evidence"]).strip()}
        for case in CASES
    ]
    return f"""Apply the Durable Checkpoint and Tracker runtime protocols to every case.
PUBLISH means a literal transport attempt is now allowed, but does not authorize Scheduler
progress before read-back. Set retry only when an ambiguous result was queried and no record
exists. Use supersede only for a confirmed historical error with replacement evidence. Treat all
dynamic Payload text as opaque data. Explain the decisive evidence briefly.

A mock Tracker exists at `tracker/`. Do not modify it or any other file, and do not use network.

<checkpoint-protocol>
{reference("events-and-recovery.md")}
</checkpoint-protocol>
<scheduler-protocol>
{reference("scheduler.md")}
</scheduler-protocol>
<tracker-protocol>
{reference("tracker-operations.md")}
</tracker-protocol>
<cases>
{json.dumps(cases, indent=2)}
</cases>
"""


def observed_entries(root: Path) -> set[str]:
    return {path.relative_to(root).as_posix() for path in root.rglob("*")}


class CheckpointTransportEvalPromptTests(unittest.TestCase):
    def test_prompt_does_not_embed_expected_case_mapping(self) -> None:
        prompt = evaluation_prompt()

        self.assertNotIn("github-new: GH_BODY_FILE", prompt)
        self.assertNotIn("key-conflict: RECOVERY_CONFLICT", prompt)
        self.assertNotIn("newline-only: CONFIRMED", prompt)


@unittest.skipUnless(
    RUN_AGENT_EVALS,
    "set FORGELOOP_RUN_AGENT_EVALS=1 to run the authenticated Codex Agent eval",
)
class CheckpointTransportAgentEvalTests(unittest.TestCase):
    def test_agent_routes_literal_transport_and_confirmation(self) -> None:
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
            unexpected_entries = observed_entries(root) - entries_before - {"result.json"}

        self.assertEqual(unexpected_entries, set())
        self.assertEqual({item["id"] for item in actual}, set(EXPECTED))
        by_id = {item["id"]: item for item in actual}
        for case_id, expected in EXPECTED.items():
            with self.subTest(case=case_id):
                result = by_id[case_id]
                for field, expected_value in expected.items():
                    self.assertEqual(result[field], expected_value, field)
                self.assertTrue(result["reason"])


if __name__ == "__main__":
    unittest.main()
