from __future__ import annotations

import unittest
from pathlib import Path


TOOLING_ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = Path(__file__).resolve().parents[3] / "plugins" / "forgeloop"
REPO_ROOT = PLUGIN_ROOT.parents[1]
SKILL_ROOT = PLUGIN_ROOT / "skills" / "run-initiative"


def reference(name: str) -> str:
    return (SKILL_ROOT / "references" / name).read_text(encoding="utf-8")


class CheckpointTransportContractTests(unittest.TestCase):
    def test_checkpoint_separates_native_envelope_from_literal_payload(self) -> None:
        events = reference("events-and-recovery.md")

        self.assertIn("Native envelope", events)
        self.assertIn("Prepared Literal Payload", events)
        self.assertIn("native reference", events)
        self.assertIn("record position", events)
        self.assertIn("server timestamp", events)
        self.assertIn("append timestamp", events)
        self.assertIn("must not contain a native timestamp or reference", events)

    def test_payload_generation_never_interprets_dynamic_shell_text(self) -> None:
        events = reference("events-and-recovery.md")

        for marker in (
            "opaque literal data",
            "Markdown fences",
            "Unicode",
            "multiline text",
            "outside the repository worktree",
            "clean it up after confirmed read-back or explicit failure",
        ):
            self.assertIn(marker, events)
        for forbidden in (
            "inline `--body` or `--message`",
            "`echo` or `printf`",
            "unquoted heredoc",
            "`eval`",
            "command substitution",
            "manual shell escaping",
        ):
            self.assertIn(forbidden, events)

    def test_each_runtime_uses_literal_transport_and_native_read_back(self) -> None:
        trackers = reference("tracker-operations.md")

        for marker in (
            "`gh issue comment --body-file <payload-file>`",
            "`--body-file -`",
            "Comment URL as a native reference",
            "`glab api`",
            "`--field body=@<payload-file>`",
            "not `glab issue note --message`",
            "native Note reference",
            "non-shell file operation",
            "same Prepared Literal Payload",
            "record position",
            "read back",
        ):
            self.assertIn(marker, trackers)
        for marker in (
            "Comment URL",
            "complete the Native envelope through an API GET",
            "`--input` accepts a safely generated complete JSON request body, not bare Markdown",
            "Do not submit `created_at`",
        ):
            self.assertIn(marker, trackers)

    def test_read_back_confirms_full_payload_before_progress(self) -> None:
        events = reference("events-and-recovery.md")
        scheduler = reference("scheduler.md")

        for marker in (
            "normalize CRLF to LF",
            "at most one trailing LF",
            "every other byte of text must match",
            "one record with an identical Payload",
            "reuse it without another write",
            "one different record",
            "more than one record",
            "`RECOVERY_CONFLICT`",
            "ambiguous write result",
            "query before retrying",
            "unique identical record",
            "missing, truncated, or different",
            "keep the Item Open and its Claims recoverable",
            "native reference and the body difference",
            "must not use `EVENT_SUPERSEDED`",
        ):
            self.assertIn(marker, events)
        self.assertIn("Do not advance the Frontier, Integration, Acceptance, or Closure", scheduler)

    def test_native_time_never_decides_claims_and_envelopes_must_be_unique(self) -> None:
        events = reference("events-and-recovery.md")

        self.assertIn("Never use a Native envelope timestamp to decide a Claim winner", events)
        self.assertIn("whether their Payload bodies are identical or different", events)

    def test_proposal_matches_the_checkpoint_envelope_boundary(self) -> None:
        proposal = (REPO_ROOT / "docs" / "proposals" / "forgeloop-skill-suite-rebuild.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("Native envelope", proposal)
        self.assertIn("Prepared Literal Payload", proposal)
        self.assertNotIn("主体引用、Tracker 服务端时间，以及该事件恢复所必需的字段", proposal)


if __name__ == "__main__":
    unittest.main()
