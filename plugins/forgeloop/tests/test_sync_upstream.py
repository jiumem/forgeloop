from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "sync_upstream.py"
SPEC = importlib.util.spec_from_file_location("sync_upstream", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class SyncUpstreamTests(unittest.TestCase):
    def test_generated_skill_uses_central_trigger_description(self) -> None:
        config = MODULE.load_config()
        metadata = MODULE.load_metadata()
        mapping = next(
            item for item in config["mappings"] if item["target"] == "codebase-design"
        )

        text = MODULE.expected_files(config, mapping)[Path("SKILL.md")].decode()

        self.assertIn(f"description: {metadata['codebase-design']['description']}", text)
        self.assertTrue(metadata["codebase-design"]["description"].startswith("Load when "))

    def test_grill_with_docs_routes_domain_facts_and_closes_each_exit(self) -> None:
        config = MODULE.load_config()
        mapping = next(
            item for item in config["mappings"] if item["target"] == "grill-with-docs"
        )
        text = MODULE.expected_files(config, mapping)[Path("SKILL.md")].decode()

        self.assertIn("settled domain terminology only to `CONTEXT.md`", text)
        self.assertIn("satisfies all three ADR thresholds", text)
        self.assertIn("same fact to both `CONTEXT.md` and an ADR", text)
        self.assertIn("If the user cancels or stops", text)
        self.assertIn("state clearly that the design is incomplete", text)
        self.assertIn("only after the user confirms that shared understanding has been reached", text)
        self.assertIn("Do not automatically start `$to-spec`, `$to-tickets`, or `$run-initiative`", text)
        self.assertIn("Do not create a Spec, Ticket, or implementation code", text)

    def test_improve_architecture_contract_handles_side_effects_and_empty_results(self) -> None:
        config = MODULE.load_config()
        mapping = next(
            item
            for item in config["mappings"]
            if item["target"] == "improve-codebase-architecture"
        )
        text = MODULE.expected_files(config, mapping)[Path("SKILL.md")].decode()

        self.assertIn("Explore and Report phases remain read-only", text)
        self.assertIn("no genuine Deepening Opportunity caused by a shallow module", text)
        self.assertIn("Do not generate HTML, produce a Top recommendation, or enter Grilling", text)
        self.assertIn("If generation fails, report that no artifact was produced", text)
        self.assertIn("If opening fails, preserve the generated file", text)
        self.assertIn("Writing domain documentation is a separate authorization seam", text)
        self.assertIn("Without authorization, return only the proposed text", text)
        self.assertIn("Do not create a Spec, Ticket, or Initiative, and do not modify production code", text)
        self.assertIn("delegate the read-only scan to an isolated child Agent", text)
        self.assertNotIn("subagent_type=Explore", text)
        self.assertNotIn("Only write the visualization to an OS temporary directory", text)

    def test_review_change_uses_generic_child_roles(self) -> None:
        config = MODULE.load_config()
        mapping = next(
            item for item in config["mappings"] if item["target"] == "review-change"
        )
        text = MODULE.expected_files(config, mapping)[Path("SKILL.md")].decode()

        self.assertIn("two independent child Agents from self-contained prompts", text)
        self.assertNotIn("general-purpose` subagent", text)

    def test_to_spec_contract_gates_publishing(self) -> None:
        config = MODULE.load_config()
        mapping = next(
            item for item in config["mappings"] if item["target"] == "to-spec"
        )
        text = MODULE.expected_files(config, mapping)[Path("SKILL.md")].decode()

        self.assertIn("do not run `$setup-forgeloop` automatically", text)
        self.assertIn("CONTEXT_INSUFFICIENT", text)
        self.assertIn("FAILED_PRECONDITION", text)
        self.assertIn("user or role permission model", text)
        self.assertIn("Tracker publication permission", text)
        self.assertIn("add `ready-for-agent` to the parent Spec", text)
        self.assertIn("does not make the parent Spec part of the Ticket Frontier", text)
        self.assertIn("If the publication result is ambiguous, first query candidates", text)
        self.assertNotIn("No interview does not mean inventing decisions", text[text.index("</spec-template>") :])

    def test_formal_spec_and_ticket_titles_use_one_canonical_prefix(self) -> None:
        config = MODULE.load_config()
        expected_prefixes = {
            "to-spec": "`[Spec] <outcome-oriented title>`",
            "to-tickets": "`[Ticket] <outcome-oriented title>`",
        }

        for target, expected_prefix in expected_prefixes.items():
            mapping = next(
                item for item in config["mappings"] if item["target"] == target
            )
            text = MODULE.expected_files(config, mapping)[Path("SKILL.md")].decode()
            self.assertIn(expected_prefix, text, target)
            self.assertIn("exactly once", text, target)

        for target in ("triage", "wayfinder"):
            mapping = next(
                item for item in config["mappings"] if item["target"] == target
            )
            text = MODULE.expected_files(config, mapping)[Path("SKILL.md")].decode()
            for prefix in ("[Initiative]", "[Spec]", "[Ticket]"):
                self.assertNotIn(prefix, text, target)

    def test_to_tickets_accepts_idempotent_acceptance_repairs(self) -> None:
        config = MODULE.load_config()
        mapping = next(
            item for item in config["mappings"] if item["target"] == "to-tickets"
        )
        text = MODULE.expected_files(config, mapping)[Path("SKILL.md")].decode()

        self.assertIn("## Forgeloop Acceptance Repair Mode", text)
        self.assertIn("Final Gate Finding", text)
        self.assertIn("stable `repair_key`", text)
        self.assertIn("Reuse the unique matching unfinished repair Ticket", text)
        self.assertIn("do not decompose the whole Spec again", text)
        self.assertIn("Never create a repair Ticket directly under the Initiative", text)
        self.assertIn("`owning_spec_ref`", text)
        self.assertIn("does not resume `$run-initiative`", text)

    def test_explicit_workflows_do_not_invoke_setup_or_fallback_tracker(self) -> None:
        config = MODULE.load_config()
        for target in ("to-tickets", "triage", "wayfinder"):
            mapping = next(
                item for item in config["mappings"] if item["target"] == target
            )
            text = MODULE.expected_files(config, mapping)[Path("SKILL.md")].decode()
            self.assertIn("FAILED_PRECONDITION", text, target)
            self.assertIn("invoke `$setup-forgeloop` explicitly", text, target)
            self.assertNotIn("run `/setup-forgeloop`", text, target)
        self.assertIn("formal Tracker Spec", MODULE.expected_files(
            config,
            next(item for item in config["mappings"] if item["target"] == "to-tickets"),
        )[Path("SKILL.md")].decode())

    def test_to_tickets_reconciles_only_open_tickets_after_a_spec_revision(self) -> None:
        config = MODULE.load_config()
        mapping = next(
            item for item in config["mappings"] if item["target"] == "to-tickets"
        )
        text = MODULE.expected_files(config, mapping)[Path("SKILL.md")].decode()

        self.assertIn("## Forgeloop Spec Revision Reconciliation Mode", text)
        self.assertIn("Preserve every Completed or Closed Ticket", text)
        self.assertIn("Compare the revised contract only with Open Tickets", text)
        self.assertIn("`retain`, `update`, `supersede`, and `create`", text)
        self.assertIn("does not resume `$run-initiative`", text)

    def test_diagnosing_bugs_contract_covers_every_write_seam(self) -> None:
        config = MODULE.load_config()
        mapping = next(
            item
            for item in config["mappings"]
            if item["target"] == "diagnosing-bugs"
        )
        text = MODULE.expected_files(config, mapping)[Path("SKILL.md")].decode()

        self.assertLess(text.index("## Forgeloop Authorization Mode"), text.index("## Phase 1"))
        for required in (
            "default mode is diagnostic-only",
            "diagnostic-write authorization does not grant repair authorization",
            "OS temporary directory",
            "report that diagnosis is blocked",
            "workspace instrumentation require write authorization",
            "Ticket Scope",
            "Every exit path",
            "does not authorize creating or updating a Commit, PR, or MR",
            "do not start `$improve-codebase-architecture` automatically",
        ):
            self.assertIn(required, text)
        self.assertNotIn("Diagnostic-only mode may create a minimal reproduction in the workspace", text)

    def test_required_replacements_are_applied(self) -> None:
        result = MODULE.apply_required_replacements(
            "run setup automatically",
            [["run setup automatically", "ask the user to run setup"]],
            "review-change/SKILL.md",
        )
        self.assertEqual(result, "ask the user to run setup")

    def test_missing_required_replacement_is_rejected(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "局部替换目标不存在"):
            MODULE.apply_required_replacements(
                "upstream text changed",
                [["run setup automatically", "ask the user to run setup"]],
                "review-change/SKILL.md",
            )

    def test_wrong_commit_is_rejected(self) -> None:
        expected = "391a2701dd948f94f56a39f7533f8eea9a859c87"
        actual = "0" * 40
        with self.assertRaisesRegex(RuntimeError, "上游 Commit 不匹配"):
            MODULE.require_upstream_commit(actual, expected)

    def test_tampered_import_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            (target / "SKILL.md").write_text("tampered", encoding="utf-8")
            errors = MODULE.compare_target(target, {Path("SKILL.md"): b"expected"})
        self.assertTrue(any("上游漂移" in error for error in errors))

    def test_repeated_write_is_idempotent(self) -> None:
        expected = {Path("SKILL.md"): b"expected", Path("reference.md"): b"reference"}
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "skill"
            MODULE.write_target(target, expected)
            first = {path.relative_to(target): path.read_bytes() for path in target.rglob("*") if path.is_file()}
            MODULE.write_target(target, expected)
            second = {path.relative_to(target): path.read_bytes() for path in target.rglob("*") if path.is_file()}
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
