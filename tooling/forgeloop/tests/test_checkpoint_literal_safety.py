from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ATTACK_PAYLOAD = """finding: `command`
probe: $(touch {sentinel})
env: ${{FORGELOOP_LITERAL_SENTINEL}}
quotes: 'single' "double" \\\\ slash
flag: --body --message
```yaml
key: :[]{{}}#
```
多行 Unicode：保持原样
"""

FAKE_CLI = """#!/usr/bin/env python3
import os
import pathlib
import sys

tool = pathlib.Path(sys.argv[0]).name
arguments = sys.argv[1:]
if tool == "gh":
    source = arguments[arguments.index("--body-file") + 1]
elif tool == "glab":
    field = arguments[arguments.index("--field") + 1]
    if not field.startswith("body=@"):
        raise SystemExit("missing file-backed body field")
    source = field.removeprefix("body=@")
else:
    raise SystemExit(f"unexpected tool: {tool}")

pathlib.Path(os.environ["MOCK_CAPTURE"]).write_bytes(pathlib.Path(source).read_bytes())
with pathlib.Path(os.environ["MOCK_COMMAND_LOG"]).open("a", encoding="utf-8") as log:
    log.write(tool + "\\n")
"""


class CheckpointLiteralSafetyTests(unittest.TestCase):
    def test_runtime_channels_preserve_attack_payload_without_extra_commands(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            worktree = root / "worktree"
            worktree.mkdir()
            sentinel = root / "sentinel"
            payload = ATTACK_PAYLOAD.format(sentinel=sentinel)
            prepared = root / "prepared.md"
            prepared.write_text(payload, encoding="utf-8")
            adapter = root / "adapter.py"
            adapter.write_text(FAKE_CLI, encoding="utf-8")
            adapter.chmod(0o755)
            gh = root / "gh"
            glab = root / "glab"
            gh.symlink_to(adapter)
            glab.symlink_to(adapter)
            command_log = root / "commands.log"
            worktree_before = set(worktree.rglob("*"))
            environment_before = os.environ.get("FORGELOOP_LITERAL_SENTINEL")

            commands = (
                (
                    [str(gh), "issue", "comment", "42", "--body-file", str(prepared)],
                    root / "github-readback.md",
                ),
                (
                    [
                        str(glab),
                        "api",
                        "projects/1/issues/42/notes",
                        "--field",
                        f"body=@{prepared}",
                    ],
                    root / "gitlab-readback.md",
                ),
            )
            for command, captured in commands:
                environment = os.environ.copy()
                environment["MOCK_CAPTURE"] = str(captured)
                environment["MOCK_COMMAND_LOG"] = str(command_log)
                environment["FORGELOOP_LITERAL_SENTINEL"] = "unchanged"
                completed = subprocess.run(
                    command,
                    capture_output=True,
                    env=environment,
                    check=False,
                )
                self.assertEqual(completed.returncode, 0, completed.stderr.decode())
                self.assertEqual(captured.read_text(encoding="utf-8"), payload)
                self.assertTrue(all(payload not in argument for argument in command))

            local_readback = root / "local-readback.md"
            local_readback.write_bytes(prepared.read_bytes())
            self.assertEqual(local_readback.read_text(encoding="utf-8"), payload)
            self.assertEqual(command_log.read_text(encoding="utf-8").splitlines(), ["gh", "glab"])
            self.assertFalse(sentinel.exists())
            self.assertEqual(os.environ.get("FORGELOOP_LITERAL_SENTINEL"), environment_before)
            self.assertEqual(set(worktree.rglob("*")), worktree_before)
            self.assertFalse(prepared.is_relative_to(worktree))


if __name__ == "__main__":
    unittest.main()
