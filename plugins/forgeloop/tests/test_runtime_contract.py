from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_runtime_contract.py"
PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = PLUGIN_ROOT / "skills" / "run-initiative"
SPEC = importlib.util.spec_from_file_location("validate_runtime_contract", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class RuntimeContractTests(unittest.TestCase):
    def test_current_runtime_contract_is_satisfied(self) -> None:
        self.assertEqual(MODULE.validate(), [])

    def test_missing_marker_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "SKILL.md").write_text("only one marker", encoding="utf-8")
            contract = root / "contract.json"
            contract.write_text(json.dumps({"SKILL.md": ["required marker"]}), encoding="utf-8")
            errors = MODULE.validate(root, contract)
        self.assertTrue(any("缺失封板条款" in error for error in errors))

    def test_no_change_required_has_a_reviewable_zero_diff_contract(self) -> None:
        coder = (SKILL_ROOT / "references" / "coder.md").read_text(encoding="utf-8")
        reviewers = (SKILL_ROOT / "references" / "reviewers.md").read_text(encoding="utf-8")

        self.assertIn("`Base == Head`", coder)
        self.assertIn("no Commit", coder)
        self.assertIn("`NO_CHANGE_REQUIRED` is the only valid empty Diff", reviewers)
        self.assertIn("an empty Diff for `READY_FOR_REVIEW`", reviewers)

    def test_spec_acceptance_always_uses_a_fresh_read_only_child(self) -> None:
        acceptance = (SKILL_ROOT / "references" / "acceptance.md").read_text(encoding="utf-8")
        scheduler = (SKILL_ROOT / "references" / "scheduler.md").read_text(encoding="utf-8")

        self.assertIn("Always create a fresh isolated, read-only Acceptance Reviewer", acceptance)
        self.assertIn("final target Commit", acceptance)
        self.assertIn("Do not retain or reuse a Ticket Reviewer", acceptance)
        self.assertNotIn("retain the original Spec Reviewer", scheduler)

    def test_pause_cancel_and_claim_lifecycle_are_explicit(self) -> None:
        events = (SKILL_ROOT / "references" / "events-and-recovery.md").read_text(encoding="utf-8")
        trackers = (SKILL_ROOT / "references" / "tracker-operations.md").read_text(encoding="utf-8")

        for marker in (
            "Retain the root Claim and current Ticket Claim while paused",
            "best-effort interrupt active children",
            "release only Claims owned by this `run_id`",
            "atomically remove the current Ticket lock",
            "atomically remove `scheduler.lock`",
            "Do not use a short TTL",
        ):
            self.assertIn(marker, events)
        self.assertIn("root Scheduler Claim", trackers)
        self.assertIn("Do not duplicate that Ticket Claim as an Event", trackers)

    def test_blocked_verdicts_have_non_repair_routes(self) -> None:
        scheduler = (SKILL_ROOT / "references" / "scheduler.md").read_text(encoding="utf-8")
        acceptance = (SKILL_ROOT / "references" / "acceptance.md").read_text(encoding="utf-8")

        self.assertIn("reason=`REVIEW_BLOCKED`", scheduler)
        self.assertIn("Do not send blocked input to the Coder", scheduler)
        self.assertIn("reason=`ACCEPTANCE_BLOCKED`", acceptance)
        self.assertIn("Do not derive a repair key", acceptance)

    def test_required_check_failures_are_classified(self) -> None:
        integration = (SKILL_ROOT / "references" / "repair-and-integration.md").read_text(encoding="utf-8")

        self.assertIn("candidate-caused Required Check failure", integration)
        self.assertIn("continue the original Coder", integration)
        self.assertIn("reason=`CHECKS_BLOCKED`", integration)
        self.assertIn("Do not trigger an extra full CI run", integration)

    def test_multi_spec_acceptance_uses_one_final_commit(self) -> None:
        acceptance = (SKILL_ROOT / "references" / "acceptance.md").read_text(encoding="utf-8")

        self.assertIn("defer every Spec Acceptance", acceptance)
        self.assertIn("same Commit", acceptance)
        self.assertIn("restart the sequence", acceptance)

    def test_entry_always_loads_checkpoint_contract(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")

        entry_line = next(line for line in skill.splitlines() if line.startswith("1. At entry"))
        self.assertIn("events-and-recovery.md", entry_line)

    def test_multi_spec_members_close_only_after_initiative_pass(self) -> None:
        acceptance = (SKILL_ROOT / "references" / "acceptance.md").read_text(encoding="utf-8")
        domain = (SKILL_ROOT / "references" / "domain-and-state.md").read_text(encoding="utf-8")

        self.assertIn("keeping all member Specs Open", acceptance)
        self.assertIn("Only on Initiative `PASS`", acceptance)
        self.assertIn("close the member Specs", acceptance)
        self.assertIn("keep member Specs Open through Initiative Acceptance", domain)

    def test_initiative_repairs_route_to_existing_member_specs_without_reopen(self) -> None:
        acceptance = (SKILL_ROOT / "references" / "acceptance.md").read_text(encoding="utf-8")

        self.assertIn("existing member Spec", acceptance)
        self.assertIn("Do not create a Ticket directly under the Initiative", acceptance)
        self.assertIn("do not introduce a reopen state", acceptance)
        self.assertIn("repeat the complete Spec Acceptance sequence", acceptance)

    def test_shared_review_input_changes_invalidate_both_axes(self) -> None:
        scheduler = (SKILL_ROOT / "references" / "scheduler.md").read_text(encoding="utf-8")

        self.assertIn("exact same frozen inputs", scheduler)
        self.assertIn("invalidate both collected results", scheduler)
        self.assertIn("continue both original Reviewers", scheduler)

    def test_checkpoint_time_belongs_only_to_the_native_envelope(self) -> None:
        events = (SKILL_ROOT / "references" / "events-and-recovery.md").read_text(encoding="utf-8")

        payload = events.split("The Prepared Literal Payload needs only:", 1)[1].split("```", 2)[1]
        self.assertIn("server timestamp", events)
        self.assertIn("append timestamp", events)
        self.assertNotIn("timestamp", payload)
        self.assertNotIn("native reference", payload)

    def test_ticket_fixed_point_refreshes_and_rejects_uncommitted_candidate_work(self) -> None:
        scheduler = (SKILL_ROOT / "references" / "scheduler.md").read_text(encoding="utf-8")

        self.assertIn("After every Ticket Claim, refresh", scheduler)
        self.assertIn("reported Head equals the Ticket Branch Head", scheduler)
        self.assertIn("all Ticket implementation changes are committed", scheduler)

    def test_multi_spec_parent_creation_is_idempotent(self) -> None:
        scheduler = (SKILL_ROOT / "references" / "scheduler.md").read_text(encoding="utf-8")

        self.assertIn("Query for an existing parent with that Revision", scheduler)
        self.assertIn("reuse one unique valid match", scheduler)
        self.assertIn("query again before retrying", scheduler)

    def test_multi_spec_parent_title_uses_one_canonical_initiative_prefix(self) -> None:
        scheduler = (SKILL_ROOT / "references" / "scheduler.md").read_text(encoding="utf-8")

        self.assertIn("`[Initiative] <outcome-oriented title>`", scheduler)
        self.assertIn("exactly once", scheduler)

    def test_multi_spec_revision_and_confirmation_are_recoverable(self) -> None:
        events = (SKILL_ROOT / "references" / "events-and-recovery.md").read_text(encoding="utf-8")

        self.assertIn("multi-Spec confirmation reference", events)
        self.assertIn("multi-Spec revision", events)
        self.assertIn("membership changed without confirmation", events)

    def test_spec_change_requires_explicit_to_tickets(self) -> None:
        acceptance = (SKILL_ROOT / "references" / "acceptance.md").read_text(encoding="utf-8")

        self.assertIn("user explicitly invokes `$to-tickets`", acceptance)
        self.assertIn("Do not let `run-initiative` create, delete, rewrite", acceptance)

    def test_acceptance_repair_work_is_idempotent(self) -> None:
        acceptance = (SKILL_ROOT / "references" / "acceptance.md").read_text(encoding="utf-8")

        self.assertIn("repair_key", acceptance)
        self.assertIn("Search for an existing formal Open repair Ticket", acceptance)
        self.assertIn("Route to `CONTRACT_BLOCKER`", acceptance)

    def test_skills_do_not_encode_unavailable_subagent_runtime_metadata(self) -> None:
        paths = (
            SKILL_ROOT / "SKILL.md",
            SKILL_ROOT / "references" / "scheduler.md",
            SKILL_ROOT / "references" / "reviewers.md",
            SKILL_ROOT / "references" / "repair-and-integration.md",
            SKILL_ROOT / "references" / "events-and-recovery.md",
            PLUGIN_ROOT / "skills" / "improve-codebase-architecture" / "SKILL.md",
            PLUGIN_ROOT / "skills" / "code-review" / "SKILL.md",
        )
        forbidden = (
            "subagent_type=",
            "general-purpose subagent",
            "Model Routing",
            "explicit model routing",
            "model_capability",
            "reasoning strength",
            "strongest available model",
        )

        for path in paths:
            text = path.read_text(encoding="utf-8")
            for marker in forbidden:
                self.assertNotIn(marker, text, f"{path}: unexpected runtime metadata marker {marker}")

    def test_repair_rounds_reuse_original_agent_contexts(self) -> None:
        scheduler = (SKILL_ROOT / "references" / "scheduler.md").read_text(encoding="utf-8")

        self.assertIn("does not inherit the Scheduler conversation", scheduler)
        self.assertIn("continue the same Coder and the same two Reviewer threads", scheduler)
        self.assertIn("retains its own history", scheduler)

    def test_reviewers_are_read_only_and_published_together(self) -> None:
        reviewers = (SKILL_ROOT / "references" / "reviewers.md").read_text(encoding="utf-8")
        scheduler = (SKILL_ROOT / "references" / "scheduler.md").read_text(encoding="utf-8")

        self.assertIn("read-only Reviewer", reviewers)
        self.assertIn("Inspect Commit objects", reviewers)
        self.assertIn("withhold both results", reviewers)
        self.assertIn("persist one combined review checkpoint", scheduler)

    def test_recovery_does_not_require_old_child_threads(self) -> None:
        events = (SKILL_ROOT / "references" / "events-and-recovery.md").read_text(encoding="utf-8")

        self.assertIn("Do not rely on child thread existence", events)
        self.assertIn("Create fresh isolated children", events)

    def test_coder_result_budget_matches_three_repair_rounds(self) -> None:
        tracker = (SKILL_ROOT / "references" / "tracker-operations.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("one initial Coder result plus at most three ordinary repair results", tracker)
        self.assertNotIn("at most two ordinary repair results", tracker)

    def test_target_drift_uses_evidence_bindings_without_new_runtime_state(self) -> None:
        domain = (SKILL_ROOT / "references" / "domain-and-state.md").read_text(encoding="utf-8")
        acceptance = (SKILL_ROOT / "references" / "acceptance.md").read_text(encoding="utf-8")
        integration = (SKILL_ROOT / "references" / "repair-and-integration.md").read_text(encoding="utf-8")

        self.assertIn("target reference moving alone does not invalidate", domain)
        self.assertIn("current target", integration)
        self.assertIn("not a new Event or state", acceptance)
        self.assertIn("Drift after that successful refresh counts as post-seal", acceptance)
        for invented_state in ("SEAL_PENDING", "SEAL_CONFIRMED", "TARGET_DRIFTED"):
            self.assertNotIn(invented_state, domain + acceptance + integration)

    def test_cumulative_audit_is_loaded_as_native_projection_protocol(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        cumulative = (SKILL_ROOT / "references" / "cumulative-audit.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("[cumulative-audit.md]", skill)
        self.assertIn("audit projection, not a source of truth", cumulative)
        self.assertIn("adds no Event, parser, or fact source", cumulative)
        self.assertIn("fresh Spec Acceptance", cumulative)


if __name__ == "__main__":
    unittest.main()
