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


def generated_to_tickets() -> str:
    config = SYNC.load_config()
    mapping = next(item for item in config["mappings"] if item["target"] == "to-tickets")
    return SYNC.expected_files(config, mapping)[Path("SKILL.md")].decode()


CASES = [
    {
        "id": "all-standard",
        "candidate": """
            T1 adds static help text and T2 renames a user-visible label. Neither interprets input,
            coordinates lifecycle, changes trust, migrates state, or carries cross-stage evidence.
            The user approved both complete drafts and their blocking edges.
        """,
    },
    {
        "id": "high-risk-pass",
        "candidate": """
            T1 interprets an extensible expression supplied by an untrusted caller. Its approved
            Adversarial Design bounds the grammar and rejection rules, references the parent
            authorization invariant, lists malformed and privilege-escalation counterexamples,
            and proves results through the public command seam. A fresh bound Reviewer returned
            PASS with no Findings.
        """,
    },
    {
        "id": "surface-only",
        "candidate": """
            T1 only changes copy that mentions "retry" and displays an existing lock status. It
            neither controls retry behavior nor affects ordering, failure semantics, or evidence.
            The user approved the complete draft.
        """,
    },
    {
        "id": "missing-field",
        "candidate": """
            T1 owns a cancellation-sensitive resource lifecycle. Its Adversarial Design omits
            Adversarial cases. The remaining fields are complete and do not change an upstream
            contract. The user approved the draft.
        """,
    },
    {
        "id": "unfalsifiable-model",
        "candidate": """
            T1 coordinates concurrent finalization. Bounded model says only "correctly handle all
            concurrency". Other design fields are complete; fixing this wording needs no Spec or
            ADR change. The user approved the draft.
        """,
    },
    {
        "id": "internal-proof",
        "candidate": """
            T1 makes an authority decision but its Proof checks only a private helper field. A
            public command seam exists. Moving proof to it needs no Spec or ADR change. The user
            approved the draft.
        """,
    },
    {
        "id": "design-gaps-none",
        "candidate": """
            T1 recovers a partially committed operation. A fresh bound Reviewer returns
            DESIGN_GAPS because retry can double-finalize; contract_impact is NONE and all Finding
            fields are present.
        """,
    },
    {
        "id": "design-gaps-spec",
        "candidate": """
            T1 discovers that safe recovery requires a new user-visible conflict outcome absent
            from the approved Spec. The Reviewer returns DESIGN_GAPS with contract_impact SPEC and
            complete Findings.
        """,
    },
    {
        "id": "mixed-contract-impact",
        "candidate": """
            T1 handles a migration. Its fresh Reviewer returns DESIGN_GAPS with one local Finding
            carrying contract_impact NONE and another Finding requiring an ADR decision. Every
            Finding contains the required fields.
        """,
    },
    {
        "id": "review-blocked",
        "candidate": """
            T1 validates cross-stage provenance. Its bound ADR revision cannot be read. The fresh
            Reviewer returns REVIEW_BLOCKED and identifies that invalid fixed input.
        """,
    },
    {
        "id": "draft-changed",
        "candidate": """
            T1 received PASS, then the user changed its blocking edge and Adversarial Design. No
            Reviewer has examined the changed draft.
        """,
    },
]


EXPECTED = {
    "all-standard": ("STANDARD", "PUBLISH"),
    "high-risk-pass": ("HIGH_RISK", "PUBLISH"),
    "surface-only": ("STANDARD", "PUBLISH"),
    "missing-field": ("HIGH_RISK", "RETURN_FINDINGS"),
    "unfalsifiable-model": ("HIGH_RISK", "RETURN_FINDINGS"),
    "internal-proof": ("HIGH_RISK", "RETURN_FINDINGS"),
    "design-gaps-none": ("HIGH_RISK", "RETURN_FINDINGS"),
    "design-gaps-spec": ("HIGH_RISK", "CONTRACT_BLOCKER"),
    "mixed-contract-impact": ("HIGH_RISK", "CONTRACT_BLOCKER"),
    "review-blocked": ("HIGH_RISK", "REPORT_REVIEW_BLOCKED"),
    "draft-changed": ("HIGH_RISK", "RERUN_REVIEW"),
}


def output_schema() -> dict:
    item = {
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "classification": {"type": "string", "enum": ["STANDARD", "HIGH_RISK"]},
            "next_action": {
                "type": "string",
                "enum": [
                    "PUBLISH",
                    "RETURN_FINDINGS",
                    "CONTRACT_BLOCKER",
                    "REPORT_REVIEW_BLOCKED",
                    "RERUN_REVIEW",
                ],
            },
            "gaps": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["id", "classification", "next_action", "gaps"],
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
        {"id": case["id"], "candidate": textwrap.dedent(case["candidate"]).strip()}
        for case in CASES
    ]
    return f"""Evaluate each complete to-tickets draft using only the Skill below. Assume every
unmentioned gate and permission passes. Return the Skill-required risk classification and choose
the next action that faithfully represents its required disposition. Use PUBLISH only when the
complete Ticket set may now be published, RETURN_FINDINGS for locally clarifiable design gaps,
CONTRACT_BLOCKER for upstream contract impact, REPORT_REVIEW_BLOCKED for invalid fixed inputs,
and RERUN_REVIEW when an earlier verdict no longer binds the current draft.

A mock Tracker exists at `tracker/`. Create one empty `tracker/<id>.published` only for PUBLISH.
For every other action, write nothing. List concrete gaps when not publishing and return an empty
gaps list when publishing. Do not create any other file, inspect the environment, or use network.

<to-tickets-skill>
{generated_to_tickets()}
</to-tickets-skill>
<candidates>
{json.dumps(candidates, indent=2)}
</candidates>
"""


def observed_tracker_entries(tracker: Path) -> set[str]:
    return {path.relative_to(tracker).as_posix() for path in tracker.rglob("*")}


class AdversarialDesignEvalPromptTests(unittest.TestCase):
    def test_prompt_does_not_embed_expected_case_mapping(self) -> None:
        prompt = evaluation_prompt()

        self.assertNotIn("all-standard: STANDARD", prompt)
        self.assertNotIn("design-gaps-spec: CONTRACT_BLOCKER", prompt)
        self.assertNotIn("draft-changed: RERUN_REVIEW", prompt)

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
class AdversarialDesignAgentEvalTests(unittest.TestCase):
    def test_risk_and_review_gates_keep_failed_publication_at_zero_writes(self) -> None:
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

        self.assertEqual({item["id"] for item in actual}, set(EXPECTED))
        self.assertEqual(
            tracker_entries,
            {
                f"{case_id}.published"
                for case_id, (_, action) in EXPECTED.items()
                if action == "PUBLISH"
            },
        )
        by_id = {item["id"]: item for item in actual}
        for case_id, (classification, action) in EXPECTED.items():
            with self.subTest(case=case_id):
                result = by_id[case_id]
                self.assertEqual(result["classification"], classification)
                self.assertEqual(result["next_action"], action)
                if action == "PUBLISH":
                    self.assertEqual(result["gaps"], [])
                else:
                    self.assertTrue(result["gaps"])


if __name__ == "__main__":
    unittest.main()
