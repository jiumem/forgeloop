from __future__ import annotations

import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = PLUGIN_ROOT / "skills" / "run-initiative"


def reference(name: str) -> str:
    return (SKILL_ROOT / "references" / name).read_text(encoding="utf-8")


class TargetDriftContractTests(unittest.TestCase):
    def test_candidate_review_binds_immutable_inputs_not_the_moving_target(self) -> None:
        domain = reference("domain-and-state.md")

        for marker in (
            "## Evidence Bindings",
            "### Candidate Review",
            "review_base: <frozen reviewed Base commit>",
            "candidate_head: <reviewed Head commit>",
            "spec_revision: <formal Spec revision>",
            "coder_evidence: <bound shared evidence references>",
            "target reference moving alone does not invalidate",
            "review_base is an immutable Commit, not a moving alias",
            "Invalidate both Verdicts only when candidate code, review_base, candidate_head, Spec Revision, or bound shared Coder evidence changes",
        ):
            self.assertIn(marker, domain)
        self.assertNotIn("or final target changes", domain)

    def test_integration_rebinds_unchanged_candidate_to_the_current_target(self) -> None:
        domain = reference("domain-and-state.md")
        integration = reference("repair-and-integration.md")
        events = reference("events-and-recovery.md")

        for marker in (
            "### Integration Result",
            "candidate_head: <reviewed Candidate commit>",
            "target_before: <target commit immediately before integration>",
            "target_after: <target commit produced or confirmed by integration>",
            "integration_method: <merge | squash | already_present | configured native method>",
            "native_ref: <PR/MR, checks, and merge evidence>",
        ):
            self.assertIn(marker, domain)
        for marker in (
            "refresh the current target, native mergeability, Integration Policy, Required Checks, and native merge evidence",
            "unchanged Candidate plus current target",
            "do not infer safety from file overlap or a single `MERGEABLE` or `CLEAN` value",
            "do not trigger an extra full CI run",
            "native merge or squash preserves the dual `PASS`",
            "rebase, target merge into the Candidate Branch, manual conflict resolution, or any other Head rewrite",
            "target_before == target_after",
        ):
            self.assertIn(marker, integration)
        self.assertIn("candidate_head, target_before, target_after, integration_method, and native_ref", events)

    def test_final_acceptance_forms_a_read_back_confirmed_seal(self) -> None:
        domain = reference("domain-and-state.md")
        acceptance = reference("acceptance.md")
        scheduler = reference("scheduler.md")
        events = reference("events-and-recovery.md")

        for marker in (
            "### Final Acceptance",
            "acceptance_level: <SPEC | INITIATIVE>",
            "subject_revision: <subject reference and revision>",
            "membership: <confirmed members when applicable>",
            "final_target_commit: <accepted immutable target commit>",
            "idempotency_key: <stable acceptance checkpoint key>",
            "native_checkpoint_ref: <confirmed native reference>",
        ):
            self.assertIn(marker, domain)
        for marker in (
            "each Ticket's complete Integration binding",
            "Integration `target_after` is an ancestor of or equal to the final target Commit",
            "Ancestry alone is not behavior proof",
            "force-push or history rewrite removes an integrated target_after",
            "## Acceptance Seal",
            "After an Acceptance Reviewer returns `PASS`, refresh the target before rendering its Payload",
            "last successful target refresh is the Seal eligibility linearization point",
            "literal-safe transport and exact native read-back",
            "Drift after that successful refresh counts as post-seal",
            "counts as post-seal",
            "must not invalidate the Seal, rerun Acceptance, rewrite history, or reopen the Run",
            "member Spec results remain provisional",
        ):
            self.assertIn(marker, acceptance)
        self.assertIn("refresh the target again before rendering an Acceptance `PASS` Payload", scheduler)
        self.assertIn("resume unfinished closure and Claim release from that Seal", events)

    def test_target_refresh_and_acceptance_rerun_do_not_spend_repair_budget(self) -> None:
        integration = reference("repair-and-integration.md")

        for marker in (
            "Target refresh, mergeability and Check refresh, read-only Acceptance, and pre- or post-seal drift consume no repair round",
            "A Candidate code change or Head rewrite enters Repair Diagnosis",
            "consumes one round",
            "shared three-round budget",
        ):
            self.assertIn(marker, integration)


if __name__ == "__main__":
    unittest.main()
