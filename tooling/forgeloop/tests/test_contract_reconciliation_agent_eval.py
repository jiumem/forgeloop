from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


TOOLING_ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = Path(__file__).resolve().parents[3] / "plugins" / "forgeloop"
RUN_SKILL = PLUGIN_ROOT / "skills" / "run-initiative"
RUN_AGENT_EVALS = os.environ.get("FORGELOOP_RUN_AGENT_EVALS") == "1"


def reference(name: str) -> str:
    return (RUN_SKILL / "references" / name).read_text(encoding="utf-8")


CASES = [
    {
        "id": "same-spec-material-ticket-revision",
        "evidence": """
            The approved package keeps the same core Problem, primary Actor, and observable delivery
            outcome. It materially changes this Ticket's effective Acceptance and interface. The old
            Branch and Commits contain useful implementation evidence, but both old Verdicts bind the
            predecessor Spec and Ticket Revisions. Every approved native fact has been read back.
        """,
    },
    {
        "id": "unrelated-non-material-revision",
        "evidence": """
            A spelling-only Revision affects an unrelated Spec section and no applicable ADR, Ticket
            body, relationship, Scope, Acceptance, or effective Candidate binding for this Ticket.
            The current repair cycle and both fixed Candidate Review inputs remain unchanged.
        """,
    },
    {
        "id": "changed-spec-identity",
        "evidence": """
            The proposed package replaces the primary Actor and observable delivery outcome. The old
            Run still owns Claims and has useful Branches, Commits, Findings, and evidence. No
            reconciliation write has started.
        """,
    },
    {
        "id": "partial-confirmed-reconciliation",
        "evidence": """
            One approved material Spec Revision affecting this Ticket and one Ticket body update are
            already confirmed natively. Required ADR integration, Ticket relationships, canonical
            Ticket Revision, full graph read-back, and CONTRACT_RECONCILED are still missing. The
            approved package is unchanged.
        """,
    },
]


EXPECTED = {
    "same-spec-material-ticket-revision": {
        "action": "REVISE_AND_RESUME",
        "preserve_old_evidence": True,
        "old_verdict_can_certify": False,
        "new_initial_cycle": True,
        "rollback_confirmed_writes": False,
        "ask_same_decision_again": False,
        "resume_before_complete_readback": False,
    },
    "unrelated-non-material-revision": {
        "action": "KEEP_EXISTING_CYCLE",
        "preserve_old_evidence": True,
        "old_verdict_can_certify": True,
        "new_initial_cycle": False,
        "rollback_confirmed_writes": False,
        "ask_same_decision_again": False,
        "resume_before_complete_readback": False,
    },
    "changed-spec-identity": {
        "action": "CANCEL_AND_NEW_SPEC",
        "preserve_old_evidence": True,
        "old_verdict_can_certify": False,
        "new_initial_cycle": False,
        "rollback_confirmed_writes": False,
        "ask_same_decision_again": False,
        "resume_before_complete_readback": False,
    },
    "partial-confirmed-reconciliation": {
        "action": "RECOVER_FORWARD",
        "preserve_old_evidence": True,
        "old_verdict_can_certify": False,
        "new_initial_cycle": True,
        "rollback_confirmed_writes": False,
        "ask_same_decision_again": False,
        "resume_before_complete_readback": False,
    },
}


def output_schema() -> dict:
    item = {
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "action": {
                "type": "string",
                "enum": [
                    "REVISE_AND_RESUME",
                    "KEEP_EXISTING_CYCLE",
                    "CANCEL_AND_NEW_SPEC",
                    "RECOVER_FORWARD",
                ],
            },
            "preserve_old_evidence": {"type": "boolean"},
            "old_verdict_can_certify": {"type": "boolean"},
            "new_initial_cycle": {"type": "boolean"},
            "rollback_confirmed_writes": {"type": "boolean"},
            "ask_same_decision_again": {"type": "boolean"},
            "resume_before_complete_readback": {"type": "boolean"},
            "reason": {"type": "string"},
        },
        "required": [
            "id",
            "action",
            "preserve_old_evidence",
            "old_verdict_can_certify",
            "new_initial_cycle",
            "rollback_confirmed_writes",
            "ask_same_decision_again",
            "resume_before_complete_readback",
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
    return f"""Apply the contract-reconciliation protocols to every case. Judge the complete
semantic evidence rather than matching keywords. Preserve fact ownership: prompts may organize the
answer, but they are not a parser-driven workflow. `REVISE_AND_RESUME` means reconcile the same Spec
and original Run, while still forbidding Resume before complete native read-back. Modify nothing and
do not use network.

<contract-reconciliation>
{reference("contract-reconciliation.md")}
</contract-reconciliation>
<domain-and-state>
{reference("domain-and-state.md")}
</domain-and-state>
<ticket-reconciliation>
{(PLUGIN_ROOT / "skills" / "to-tickets" / "SKILL.md").read_text(encoding="utf-8")}
</ticket-reconciliation>
<cases>
{json.dumps(CASES, indent=2)}
</cases>
"""


class ContractReconciliationEvalPromptTests(unittest.TestCase):
    def test_prompt_does_not_embed_expected_case_mapping(self) -> None:
        prompt = evaluation_prompt()

        for case_id, expected in EXPECTED.items():
            self.assertNotIn(f"{case_id}: {expected['action']}", prompt)


@unittest.skipUnless(
    RUN_AGENT_EVALS,
    "set FORGELOOP_RUN_AGENT_EVALS=1 to run the authenticated Codex Agent eval",
)
class ContractReconciliationAgentEvalTests(unittest.TestCase):
    def test_agent_preserves_reconciliation_semantics(self) -> None:
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
        by_id = {item["id"]: item for item in actual}
        for case_id, expected in EXPECTED.items():
            with self.subTest(case=case_id):
                for field, value in expected.items():
                    self.assertEqual(by_id[case_id][field], value, field)
                self.assertTrue(by_id[case_id]["reason"].strip())


if __name__ == "__main__":
    unittest.main()
