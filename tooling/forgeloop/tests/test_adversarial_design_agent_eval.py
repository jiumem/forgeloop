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
            and proves results through the public command seam. Its initial fresh bound Reviewer
            returned PASS with no admitted BLOCKING_GAP concerns.
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
        "id": "contract-bound-gap",
        "candidate": """
            T1 recovers a partially committed operation. Its Reviewer returns BLOCKING_GAP because
            retry can double-finalize. The Finding binds authority_ref to parent DA-3, names the
            observable duplicate result, gives a reachable retry counterexample inside the approved
            failure model, explains why the current smaller design fails, and names public proof.
        """,
    },
    {
        "id": "contract-question",
        "candidate": """
            Parent DA-3 requires concurrent retry to preserve one stable terminal result through
            the public command, but the Spec does not decide whether a reachable ownership conflict
            is rejected or retried. The Reviewer returns CONTRACT_QUESTION with authority_ref DA-3,
            the observable ambiguity, a reachable concurrent-retry counterexample, why no smaller
            Ticket-local choice can satisfy DA-3 without inventing product behavior, the missing
            product decision, and the required public proof.
        """,
    },
    {
        "id": "unbound-contract-question",
        "candidate": """
            T1 already satisfies every approved recovery outcome. The Reviewer asks whether the
            product should expose a new conflict status but supplies no authority_ref, approved
            failure behavior, reachable counterexample, observable violation, necessity, or public
            proof. The owning Agent rejects the unbound question as Scope expansion; there are no
            other admitted concerns and the same Reviewer inputs remain fixed.
        """,
    },
    {
        "id": "hardening-does-not-block",
        "candidate": """
            T1 atomically publishes an immutable result and startup recovery deletes unreferenced
            temporary directories. The parent contract requires no invalid durable product fact but
            does not require zero physical residue at every crash instruction. The Reviewer suggests
            global blob refcounts as HARDENING_RECOMMENDATION. The owning Agent adjudicates DEFER,
            and the same Reviewer returns PASS with no admitted BLOCKING_GAP.
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
    {
        "id": "third-round-scale-review",
        "candidate": """
            T1 has completed three consecutive non-PASS review rounds. Each repair added another
            storage owner or cleanup lifecycle, and no scale review has compared those mechanisms
            with the initially approved draft and parent authority.
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
    "contract-bound-gap": ("HIGH_RISK", "RETURN_FINDINGS"),
    "contract-question": ("HIGH_RISK", "CONTRACT_BLOCKER"),
    "unbound-contract-question": ("HIGH_RISK", "PUBLISH"),
    "hardening-does-not-block": ("HIGH_RISK", "PUBLISH"),
    "review-blocked": ("HIGH_RISK", "REPORT_REVIEW_BLOCKED"),
    "draft-changed": ("HIGH_RISK", "CONTINUE_SAME_REVIEWER"),
    "third-round-scale-review": ("HIGH_RISK", "SCALE_REVIEW"),
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
                    "CONTINUE_SAME_REVIEWER",
                    "SCALE_REVIEW",
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
complete Ticket set may now be published, RETURN_FINDINGS for an admitted contract-bound local gap,
CONTRACT_BLOCKER for a missing upstream decision, REPORT_REVIEW_BLOCKED for invalid fixed inputs,
CONTINUE_SAME_REVIEWER when an earlier Verdict no longer binds a changed draft, and SCALE_REVIEW
after the third consecutive non-PASS round.

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
        self.assertNotIn("contract-question: CONTRACT_BLOCKER", prompt)
        self.assertNotIn("draft-changed: CONTINUE_SAME_REVIEWER", prompt)

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
