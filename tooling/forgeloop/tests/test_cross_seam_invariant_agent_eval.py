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


TOOLING_ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = Path(__file__).resolve().parents[3] / "plugins" / "forgeloop"
SYNC_SCRIPT = TOOLING_ROOT / "scripts" / "sync_upstream.py"
SPEC = importlib.util.spec_from_file_location("sync_upstream", SYNC_SCRIPT)
assert SPEC and SPEC.loader
SYNC = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = SYNC
SPEC.loader.exec_module(SYNC)

RUN_AGENT_EVALS = os.environ.get("FORGELOOP_RUN_AGENT_EVALS") == "1"


def generated_skill(target: str) -> str:
    config = SYNC.load_config()
    mapping = next(item for item in config["mappings"] if item["target"] == target)
    return SYNC.expected_files(config, mapping)[Path("SKILL.md")].decode()


CASES = [
    {
        "id": "spec-none",
        "workflow": "to-spec",
        "candidate": """
            Validation Entry: Name Public API; Covers DA-1; Behavior user reads value;
            Evidence public API returns value.
            Acceptance Prerequisites: all entries establish their runtime conditions.
            Cross-seam Invariants: None — no Cross-seam Invariants.
            Delivery Acceptance: DA-1 user reads the saved value.
        """,
        "verdict": "READY_TO_PUBLISH",
        "tracker_writes": "ALLOWED_AFTER_GATE",
    },
    {
        "id": "spec-complete",
        "workflow": "to-spec",
        "candidate": """
            Validation Entry: Name Public API; Covers DA-1; Behavior user reads canonical value;
            Evidence public API response asserts canonical value or explicit not-found failure.
            Acceptance Prerequisites: all entries establish their runtime conditions.
            Cross-seam Invariant: ID INV-1; Contract canonical stored value must pass through the
            API adapter to the public response, preserving the value or explicit not-found failure;
            Proof Public API — response asserts canonical value or explicit not-found failure.
            Delivery Acceptance: DA-1 user reads the canonical value or explicit failure.
        """,
        "verdict": "READY_TO_PUBLISH",
        "tracker_writes": "ALLOWED_AFTER_GATE",
    },
    {
        "id": "spec-missing-proof",
        "workflow": "to-spec",
        "candidate": """
            Validation Entry: Name Public API; Covers DA-1; Behavior user reads value;
            Evidence public API returns value.
            Acceptance Prerequisites: all entries establish their runtime conditions.
            Cross-seam Invariant: ID INV-1; Contract stored value reaches the public API response.
            Delivery Acceptance: DA-1 user reads the saved value.
        """,
        "verdict": "CONTEXT_INSUFFICIENT",
        "tracker_writes": "ZERO",
    },
    {
        "id": "spec-duplicate-id",
        "workflow": "to-spec",
        "candidate": """
            Validation Entry: Name Public API; Covers DA-1; Behavior user reads value;
            Evidence public API returns value.
            Acceptance Prerequisites: all entries establish their runtime conditions.
            Invariant: ID INV-1; Contract stored value reaches response; Proof Public API response value.
            Invariant: ID INV-1; Contract missing value reaches response; Proof Public API not-found response.
            Delivery Acceptance: DA-1 user reads the saved value.
        """,
        "verdict": "CONTEXT_INSUFFICIENT",
        "tracker_writes": "ZERO",
    },
    {
        "id": "spec-helper-proof",
        "workflow": "to-spec",
        "candidate": """
            Validation Entry: Name Cache helper; Covers DA-1; Behavior helper returns stored key;
            Evidence unit test reads the internal field.
            Acceptance Prerequisites: all entries establish their runtime conditions.
            Invariant: ID INV-1; Contract stored value reaches public response;
            Proof Cache helper — internal field equals stored key.
            Delivery Acceptance: DA-1 user reads the saved value.
        """,
        "verdict": "CONTEXT_INSUFFICIENT",
        "tracker_writes": "ZERO",
    },
    {
        "id": "tickets-none",
        "workflow": "to-tickets",
        "candidate": """
            Parent Cross-seam Invariants: None — no Cross-seam Invariants.
            Approved breakdown: T1 delivers DA-1; Owned Cross-seam Invariants: None.
            Approval mapping: Invariant ownership: None.
        """,
        "verdict": "READY_TO_PUBLISH",
        "tracker_writes": "ALLOWED_AFTER_GATE",
    },
    {
        "id": "tickets-unique-owner",
        "workflow": "to-tickets",
        "candidate": """
            Parent INV-1 Contract: canonical value reaches the public API; Proof: Public API response assertion.
            T1 provides storage and blocks T2; Owned Cross-seam Invariants: None.
            T2 delivers complete INV-1, cites parent Contract and Proof, and requires Public API evidence.
            Approval mapping: INV-1 → T2. User approved the breakdown and mapping.
        """,
        "verdict": "READY_TO_PUBLISH",
        "tracker_writes": "ALLOWED_AFTER_GATE",
    },
    {
        "id": "tickets-no-owner",
        "workflow": "to-tickets",
        "candidate": """
            Parent INV-1 Contract and Public API Proof are valid.
            T1 and T2 both state Owned Cross-seam Invariants: None.
            Approval mapping has no entry for INV-1.
        """,
        "verdict": "ADJUST_BREAKDOWN",
        "tracker_writes": "ZERO",
    },
    {
        "id": "tickets-multiple-owners",
        "workflow": "to-tickets",
        "candidate": """
            Parent INV-1 Contract and Public API Proof are valid.
            T1 owns INV-1 and T2 also owns INV-1.
            Approval mapping: INV-1 → T1 and T2.
        """,
        "verdict": "ADJUST_BREAKDOWN",
        "tracker_writes": "ZERO",
    },
    {
        "id": "tickets-helper-owner-proof",
        "workflow": "to-tickets",
        "candidate": """
            Parent INV-1 has a Public API Proof. T1 claims INV-1 but its Acceptance criteria only
            run an internal cache-helper test and submit no evidence from the parent Validation Entry.
            Approval mapping: INV-1 → T1.
        """,
        "verdict": "ADJUST_BREAKDOWN",
        "tracker_writes": "ZERO",
    },
    {
        "id": "tickets-undeclared-invariant",
        "workflow": "to-tickets",
        "candidate": """
            Parent states None — no Cross-seam Invariants. During decomposition, the Agent finds
            that authorization must propagate through API and worker seams for DA-1 to hold.
            The proposed tickets need this new invariant, but it is absent from the approved Spec.
        """,
        "verdict": "CONTRACT_BLOCKER",
        "tracker_writes": "ZERO",
    },
]


def output_schema() -> dict:
    item = {
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "verdict": {
                "type": "string",
                "enum": [
                    "READY_TO_PUBLISH",
                    "CONTEXT_INSUFFICIENT",
                    "ADJUST_BREAKDOWN",
                    "CONTRACT_BLOCKER",
                ],
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
        "properties": {"results": {"type": "array", "items": item}},
        "required": ["results"],
        "additionalProperties": False,
    }


def evaluation_prompt() -> str:
    candidates = [
        {
            "id": case["id"],
            "workflow": case["workflow"],
            "candidate": textwrap.dedent(case["candidate"]).strip(),
        }
        for case in CASES
    ]
    return f"""Evaluate the Cross-seam Invariant gate of the two Skills below. Assume all unrelated
gates, permissions, conflicts, and required user approvals pass. A temporary mock Tracker is in
`tracker/`. For each candidate:

- Use the disposition required by the applicable Skill: READY_TO_PUBLISH when its gate passes,
  CONTEXT_INSUFFICIENT when `to-spec` requires that result, ADJUST_BREAKDOWN when `to-tickets`
  requires further slice adjustment, or CONTRACT_BLOCKER when `to-tickets` requires that result.
- Create one empty `tracker/<id>.published` only for READY_TO_PUBLISH; write nothing for every
  other disposition.
- use ALLOWED_AFTER_GATE only with READY_TO_PUBLISH; otherwise use ZERO;
- list every gap on failure and use an empty gaps list on success.

Do not create any other file, inspect the environment, or use the network.

<to-spec-skill>
{generated_skill("to-spec")}
</to-spec-skill>
<to-tickets-skill>
{generated_skill("to-tickets")}
</to-tickets-skill>
<candidates>
{json.dumps(candidates, indent=2)}
</candidates>
"""


def observed_tracker_entries(tracker: Path) -> set[str]:
    return {
        path.relative_to(tracker).as_posix()
        for path in tracker.rglob("*")
    }


class CrossSeamInvariantEvalPromptTests(unittest.TestCase):
    def test_eval_prompt_does_not_supply_domain_answers(self) -> None:
        prompt = evaluation_prompt()

        for leaked_answer in (
            "for no owner, multiple owners",
            "internal-only owner proof",
            "for a required but undeclared invariant",
        ):
            with self.subTest(leaked_answer=leaked_answer):
                self.assertNotIn(leaked_answer, prompt)
        self.assertIn("Use the disposition required by the applicable Skill", prompt)

    def test_tracker_observation_includes_every_entry(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            tracker = Path(directory)
            (tracker / "success.published").touch()
            (tracker / "failed.comment").touch()
            (tracker / "nested").mkdir()
            (tracker / "nested" / "status").touch()

            self.assertEqual(
                observed_tracker_entries(tracker),
                {"failed.comment", "nested", "nested/status", "success.published"},
            )


@unittest.skipUnless(
    RUN_AGENT_EVALS,
    "set FORGELOOP_RUN_AGENT_EVALS=1 to run the authenticated Codex Agent eval",
)
class CrossSeamInvariantAgentEvalTests(unittest.TestCase):
    def test_invariant_and_owner_gates_with_zero_writes(self) -> None:
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
            tracker_entries = observed_tracker_entries(tracker)

        self.assertEqual({item["id"] for item in actual}, {case["id"] for case in CASES})
        self.assertEqual(
            tracker_entries,
            {
                f"{case['id']}.published"
                for case in CASES
                if case["tracker_writes"] == "ALLOWED_AFTER_GATE"
            },
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
