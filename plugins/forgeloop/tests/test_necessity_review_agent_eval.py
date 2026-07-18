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


def generated_skill(target: str) -> str:
    config = SYNC.load_config()
    mapping = next(item for item in config["mappings"] if item["target"] == target)
    return SYNC.expected_files(config, mapping)[Path("SKILL.md")].decode()


CASES = [
    {
        "id": "spec-simple-overbuilt",
        "stage": "SPEC",
        "evidence": """
            The user needs a settings read immediately after save to return the saved value. Code
            evidence shows the write updates the authoritative repository while the read handler
            uses a stale cache entry. The existing repository and public API seam can express and
            prove the complete fix. The candidate Spec instead adds a version token, lease service,
            cache registry, recovery lifecycle, and global migration. No observed or contracted
            permission, concurrency, recovery, or compatibility failure requires those concepts.
        """,
    },
    {
        "id": "spec-structural-evidence",
        "stage": "SPEC",
        "evidence": """
            Two workers can concurrently retry payment finalization after a timeout; a reproduction
            settles one payment twice. The approved outcome requires at-most-once external
            settlement and recovery of an old in-flight operation. The existing payment row cannot
            distinguish the two attempts or prove which external result owns finalization. The
            candidate adds one operation token, a persisted version fence, and lease expiry owned by
            the payment aggregate. Each concept is tied to the reproduced race and omitting any one
            breaks the declared concurrency or recovery invariant. A smaller local-handler change
            cannot close both workers and restart recovery through the public payment command.
        """,
    },
    {
        "id": "spec-missing-decision",
        "stage": "SPEC",
        "evidence": """
            The user wants large exports to complete reliably. Code evidence supports either a
            synchronous command that rejects oversized exports with a new public conflict outcome,
            or an asynchronous job with retry and cancellation. The resolved context does not choose
            the public failure behavior, maximum synchronous size, cancellation semantics, or actor
            allowed to retry. Selecting the smaller correct design would invent a product decision.
        """,
    },
    {
        "id": "spec-affected-path",
        "stage": "SPEC",
        "evidence": """
            Checkout pricing reads a stale legacy cache and violates the approved total. The
            candidate reuses the existing pricing owner, routes checkout through it, and proves the
            checkout production path no longer calls the legacy cache. Reporting still uses that
            cache legally for an unrelated eventual-consistency contract, and the candidate does not
            claim global retirement. No new fact source or lifecycle is introduced.
        """,
    },
    {
        "id": "tickets-simple-five",
        "stage": "TICKETS",
        "evidence": """
            The approved Spec changes one settings label and proves it through the existing settings
            page seam. The proposed graph has five Tickets: copy constant, test helper, fixture,
            component wiring, and final validation. Only the wired page produces the current result;
            the others have no independent current consumer or system guarantee.
        """,
    },
    {
        "id": "tickets-structural-five",
        "stage": "TICKETS",
        "evidence": """
            The approved Spec requires an expand-contract compatibility migration across three large
            packages. One expand Ticket makes both forms publicly accepted, three bounded migration
            Tickets independently move each package while keeping its public suite green, and one
            contract Ticket removes the old form after all legal callers reach zero. Each slice fits
            one fresh context and omitting any slice breaks the approved compatibility invariant.
        """,
    },
    {
        "id": "tickets-contract-drift",
        "stage": "TICKETS",
        "evidence": """
            The approved Spec requires an existing command to fail with its current error. The
            proposed Ticket graph adds a user-visible retry state, cancellation behavior, and a new
            public response that are absent from the Spec and cannot be expressed by its Delivery
            Acceptance or Cross-seam Invariants.
        """,
    },
]


EXPECTED_ACTIONS = {
    "spec-simple-overbuilt": "SIMPLIFY",
    "spec-structural-evidence": "KEEP",
    "spec-missing-decision": "CONTEXT_INSUFFICIENT",
    "spec-affected-path": "KEEP",
    "tickets-simple-five": "SIMPLIFY",
    "tickets-structural-five": "KEEP",
    "tickets-contract-drift": "CONTRACT_BLOCKER",
}


def output_schema() -> dict:
    item = {
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "action": {
                "type": "string",
                "enum": ["KEEP", "SIMPLIFY", "CONTEXT_INSUFFICIENT", "CONTRACT_BLOCKER"],
            },
            "reason": {"type": "string"},
            "old_mechanism_scope": {
                "type": "string",
                "enum": ["AFFECTED_PATH", "GLOBAL_RETIREMENT", "NOT_APPLICABLE"],
            },
        },
        "required": ["id", "action", "reason", "old_mechanism_scope"],
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
            "stage": case["stage"],
            "evidence": textwrap.dedent(case["evidence"]).strip(),
        }
        for case in CASES
    ]
    return f"""Apply the relevant generated Skill as an Agent reasoning program to every case.
Use to-spec for SPEC cases and to-tickets for TICKETS cases. Assume all unmentioned publication,
format, approval, and permission gates pass. Judge complete meaning rather than keywords or field
presence.

Return KEEP when the candidate is the smallest complete evidence-backed design or Ticket graph.
Return SIMPLIFY when the resolved context already supports a smaller complete result without a new
user decision. Return CONTEXT_INSUFFICIENT when choosing a correct Spec requires an unresolved user,
product, Scope, failure-semantic, ADR, or public-interface decision. Return CONTRACT_BLOCKER only for
a TICKETS case that would have to change its approved Spec or ADR. Explain the concrete evidence in
one concise reason. Report AFFECTED_PATH when old-mechanism proof is intentionally limited to the
affected path, GLOBAL_RETIREMENT only when the proposal retires it everywhere, otherwise
NOT_APPLICABLE. Do not inspect the environment, use network, or create files.

<to-spec-skill>
{generated_skill("to-spec")}
</to-spec-skill>
<to-tickets-skill>
{generated_skill("to-tickets")}
</to-tickets-skill>
<cases>
{json.dumps(cases, indent=2)}
</cases>
"""


class NecessityReviewEvalPromptTests(unittest.TestCase):
    def test_prompt_does_not_embed_expected_mapping(self) -> None:
        prompt = evaluation_prompt()

        self.assertNotIn("spec-simple-overbuilt: SIMPLIFY", prompt)
        self.assertNotIn("tickets-contract-drift: CONTRACT_BLOCKER", prompt)


@unittest.skipUnless(
    RUN_AGENT_EVALS,
    "set FORGELOOP_RUN_AGENT_EVALS=1 to run the authenticated Codex Agent eval",
)
class NecessityReviewAgentEvalTests(unittest.TestCase):
    def test_agent_preserves_minimal_and_evidence_backed_paths(self) -> None:
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

        self.assertEqual({item["id"] for item in actual}, set(EXPECTED_ACTIONS))
        by_id = {item["id"]: item for item in actual}
        for case_id, expected_action in EXPECTED_ACTIONS.items():
            with self.subTest(case=case_id):
                self.assertEqual(by_id[case_id]["action"], expected_action)
                self.assertTrue(by_id[case_id]["reason"].strip())
        self.assertEqual(by_id["spec-affected-path"]["old_mechanism_scope"], "AFFECTED_PATH")


if __name__ == "__main__":
    unittest.main()
