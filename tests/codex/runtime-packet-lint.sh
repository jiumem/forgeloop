#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

check_pattern() {
  local file="$1"
  local pattern="$2"

  if ! rg -F -q "$pattern" "$file"; then
    echo "runtime packet lint: missing ${pattern} in ${file}"
    exit 1
  fi
}

check_pattern \
  "plugins/forgeloop/skills/references/anchor-addressing.md" \
  '`run-initiative/SKILL.md`, or `code-loop/SKILL.md`'
check_pattern \
  "plugins/forgeloop/skills/references/truth-location.md" \
  '1. authoritative bound refs plus `doc_ref + anchor_selector`'
check_pattern \
  "plugins/forgeloop/skills/references/truth-location.md" \
  '2. `rg` keyword discovery only when the needed selector or exact local section has not yet been bound clearly'
check_pattern \
  "plugins/forgeloop/skills/references/truth-location.md" \
  '3. sealed full-document reading only when the current packet or bound contract still cannot prove the needed truth through legal slices'
check_pattern \
  "plugins/forgeloop/skills/run-initiative/references/runtime-cutover.md" \
  'Ordinary coder / reviewer packets remain anchor-addressed minimal in every supported runtime mode'
check_pattern \
  "plugins/forgeloop/skills/code-loop/SKILL.md" \
  'Obey the shared packet law in `plugins/forgeloop/skills/references/anchor-addressing.md` and the runtime cutover law'
check_pattern \
  "plugins/forgeloop/skills/run-initiative/references/runtime-cutover.md" \
  'preserve `compare_base_ref` when the current handoff carries one'
check_pattern \
  "docs/initiatives/active/anchor-sliced-dispatch-optimization/total-task-doc.md" \
  'acceptance-matrix/evidence-entrypoints'
check_pattern \
  "tests/fixtures/anchor-slicing/task-review-sample.md" \
  'compare_base_ref:'
check_pattern \
  "tests/codex/token-benchmark/fixtures/milestone-review-sample.md" \
  'compare_base_ref:'
check_pattern \
  "tests/codex/token-benchmark/fixtures/initiative-review-sample.md" \
  'compare_base_ref:'
check_pattern \
  "plugins/forgeloop/agents/coder.toml" \
  'formal writeback not completed'
check_pattern \
  "plugins/forgeloop/agents/coder.toml" \
  'Obey the shared truth-location law in `plugins/forgeloop/skills/references/truth-location.md`'
check_pattern \
  "plugins/forgeloop/agents/task_reviewer.toml" \
  'formal writeback not completed'
check_pattern \
  "plugins/forgeloop/agents/task_reviewer.toml" \
  'Obey the shared truth-location law in `plugins/forgeloop/skills/references/truth-location.md`'
check_pattern \
  "plugins/forgeloop/agents/milestone_reviewer.toml" \
  'formal writeback not completed'
check_pattern \
  "plugins/forgeloop/agents/milestone_reviewer.toml" \
  'Obey the shared truth-location law in `plugins/forgeloop/skills/references/truth-location.md`'
check_pattern \
  "plugins/forgeloop/agents/initiative_reviewer.toml" \
  'formal writeback not completed'
check_pattern \
  "plugins/forgeloop/agents/initiative_reviewer.toml" \
  'Obey the shared truth-location law in `plugins/forgeloop/skills/references/truth-location.md`'
check_pattern \
  "plugins/forgeloop/skills/code-loop/SKILL.md" \
  'Treat coder natural-language completion as non-authoritative'
check_pattern \
  "plugins/forgeloop/skills/code-loop/SKILL.md" \
  'Treat reviewer natural-language completion as non-authoritative'
check_pattern \
  "plugins/forgeloop/skills/using-git-worktrees/SKILL.md" \
  'Read and obey project-level `AGENTS.md` first'
check_pattern \
  "plugins/forgeloop/skills/run-initiative/SKILL.md" \
  'project-declared environment preparation from `AGENTS.md` or repo operator docs'
check_pattern \
  "plugins/forgeloop/skills/run-initiative/SKILL.md" \
  'Obey the shared truth-location law in `../references/truth-location.md`'
check_pattern \
  "plugins/forgeloop/skills/run-initiative/SKILL.md" \
  'authoritative `doc_ref + anchor_selector` bindings for the bound object'
check_pattern \
  "plugins/forgeloop/skills/run-initiative/SKILL.md" \
  'Use the smallest fitting class:'
check_pattern \
  "plugins/forgeloop/skills/rebuild-runtime/SKILL.md" \
  'classify the cause in `last_transition.reason` using the smallest fitting class'
check_pattern \
  "plugins/forgeloop/skills/using-git-worktrees/SKILL.md" \
  'stop and surface the gap as `execution_ready`, not as a task/object blocker'

python3 - <<'PY'
import json
import re
from pathlib import Path

scenarios = json.loads(Path("tests/codex/token-benchmark/fixtures/scenarios.json").read_text())
run_initiative_text = Path("plugins/forgeloop/skills/run-initiative/SKILL.md").read_text()
rebuild_runtime_text = Path("plugins/forgeloop/skills/rebuild-runtime/SKILL.md").read_text()

frontier_priority_marker = "- frontier selection when `current_snapshot.active_plane=frontier` or `next_action.action=advance_frontier`"
task_priority_marker = "- task-mode code loop when a Task is clearly active"
task_next_ready_legacy = "task-mode code loop when a Task is clearly active or next-ready"
frontier_apply_marker = (
    "- if `current_snapshot.active_plane=frontier` or `next_action.action=advance_frontier`: resolve exactly one next runtime object from the admitted planning document set plus authoritative runtime rolling docs"
)
rebuild_frontier_marker = (
    "- If recovery lands on `current_snapshot.active_plane=frontier` or `next_action.action=advance_frontier`, "
    "apply the same fixed supervisor routing order used by `run-initiative`: required current Milestone closure "
    "-> required Initiative closure -> exactly one next-ready Task. Do not recover directly into Task plane merely "
    "because one next-ready Task can be guessed."
)
rebuild_formal_only_marker = (
    "- Recover only from formal runtime truth. Workspace diff, chat summaries, and interrupted worker intent may help "
    "explain what happened, but they must never promote object progression without a rereadable formal block."
)
rebuild_uncommitted_marker = (
    "- If the current round has no formal `coder_update`, `review_handoff`, or `review_result`, treat any uncommitted code or chat-only progress as unfinished in-object work "
    "and recover coder continuation from the last legal formal state instead of promoting the object"
)
run_initiative_partial_progress_marker = (
    "- if workspace diff or interrupted agent narration suggests progress that has not appeared as a rereadable "
    "`coder_update`, `review_handoff`, or `review_result`: do not advance the object from that hint alone; continue only from the last "
    "legal formal runtime state or call skill: `rebuild-runtime` when the active state is no longer provable uniquely"
)
run_initiative_disconnect_marker = (
    "If the loop ended on disconnect or partial failure and no new formal block can be reread, keep the object on its "
    "last legal formal state; uncommitted workspace progress stays merely local until a later round writes legal runtime truth."
)

if task_next_ready_legacy in run_initiative_text:
    raise SystemExit(
        "runtime packet lint: run-initiative still allows next-ready Task to bypass frontier/container forcing"
    )

frontier_priority_index = run_initiative_text.find(frontier_priority_marker)
task_priority_index = run_initiative_text.find(task_priority_marker)
if frontier_priority_index == -1 or task_priority_index == -1:
    raise SystemExit("runtime packet lint: run-initiative is missing frontier/task routing markers")
if frontier_priority_index > task_priority_index:
    raise SystemExit(
        "runtime packet lint: frontier/container forcing must be routed before task-mode direct dispatch"
    )

if frontier_apply_marker not in run_initiative_text:
    raise SystemExit(
        "runtime packet lint: run-initiative apply-case is missing the explicit frontier/container-forcing law"
    )

for marker in (
    "- use this fixed order and stop at the first match: required current Milestone closure -> required current Initiative closure -> exactly one next-ready Task",
    "- closure always beats Task entry",
    "- this step advances only the existing runtime frontier; it must not reopen planning, regenerate Task plans, or synthesize a new Milestone / Task decomposition",
):
    if marker not in run_initiative_text:
        raise SystemExit(
            "runtime packet lint: run-initiative apply-case is missing part of the explicit frontier/container-forcing law"
        )

if rebuild_frontier_marker not in rebuild_runtime_text:
    raise SystemExit(
        "runtime packet lint: rebuild-runtime is missing the closure-first frontier recovery law"
    )

if rebuild_formal_only_marker not in rebuild_runtime_text:
    raise SystemExit(
        "runtime packet lint: rebuild-runtime is missing the formal-truth-only recovery law"
    )

if rebuild_uncommitted_marker not in rebuild_runtime_text:
    raise SystemExit(
        "runtime packet lint: rebuild-runtime still allows uncommitted progress to promote object state"
    )

if run_initiative_partial_progress_marker not in run_initiative_text:
    raise SystemExit(
        "runtime packet lint: run-initiative is missing the partial-progress no-promotion law"
    )

if run_initiative_disconnect_marker not in run_initiative_text:
    raise SystemExit(
        "runtime packet lint: run-initiative is missing the disconnect recovery law"
    )

targets = {
    "Same-Task Same-Round Coder Continue",
    "Same-Task Reviewer Entry",
    "Milestone Review",
    "Initiative Review",
    "same-task warm-path delta legal",
    "same-task warm-path delta illegal -> full packet fallback",
    "selector legality failure -> full-doc fallback",
}
forbidden = {
    "plugins/forgeloop/skills/run-initiative/SKILL.md",
    "plugins/forgeloop/skills/code-loop/SKILL.md",
    "plugins/forgeloop/skills/task-loop/SKILL.md",
    "plugins/forgeloop/skills/milestone-loop/SKILL.md",
    "plugins/forgeloop/skills/initiative-loop/SKILL.md",
}
supervisor_scenarios = {
    "Runtime Cold Start": {
        "plugins/forgeloop/skills/run-initiative/SKILL.md",
    },
    "Runtime Resume Into Active Task": {
        "plugins/forgeloop/skills/run-initiative/SKILL.md",
        "plugins/forgeloop/skills/code-loop/SKILL.md",
    },
    "Rebuild Runtime": {
        "plugins/forgeloop/skills/rebuild-runtime/SKILL.md",
    },
    "Waiting Or Blocked Resume": {
        "plugins/forgeloop/skills/run-initiative/SKILL.md",
    },
}
for scenario in scenarios:
    active_skill_docs = supervisor_scenarios.get(scenario["name"])
    if active_skill_docs:
        for item in scenario["minimal_packet"]:
            path = item.get("path") or item.get("doc")
            if path in active_skill_docs:
                raise SystemExit(
                    f"runtime packet lint: supervisor minimal packet re-feeds active skill law in scenario {scenario['name']}: {path}"
                )

    if scenario["name"] not in targets:
        continue

    promoted_non_agent_full_doc = False
    for item in scenario["minimal_packet"]:
        path = item.get("path") or item.get("doc")
        if path in forbidden:
            raise SystemExit(
                f"runtime packet lint: worker minimal packet still references supervisor skill doc in scenario {scenario['name']}: {path}"
            )
        if item.get("type") == "full_doc":
            if path == "docs/initiatives/active/anchor-sliced-dispatch-optimization/total-task-doc.md":
                raise SystemExit(
                    f"runtime packet lint: worker minimal packet still includes full Total Task Doc in scenario {scenario['name']}"
                )
            if path and not path.startswith("plugins/forgeloop/agents/"):
                promoted_non_agent_full_doc = True

    if promoted_non_agent_full_doc:
        if not scenario.get("minimal_fallback_mode"):
            raise SystemExit(
                f"runtime packet lint: missing minimal_fallback_mode for promoted worker packet in scenario {scenario['name']}"
            )
        if not scenario.get("minimal_fallback_reason"):
            raise SystemExit(
                f"runtime packet lint: missing minimal_fallback_reason for promoted worker packet in scenario {scenario['name']}"
            )

reviewer_requirements = {
    "Same-Task Reviewer Entry": {
        "required_slices": {
            ("docs/initiatives/active/anchor-sliced-dispatch-optimization/total-task-doc.md", "task-ledger/task-definitions/asdo-t5"),
            ("docs/initiatives/active/anchor-sliced-dispatch-optimization/total-task-doc.md", "acceptance-matrix/task-acceptance-index/asdo-t5"),
            ("docs/initiatives/active/anchor-sliced-dispatch-optimization/total-task-doc.md", "acceptance-matrix/evidence-entrypoints"),
        },
        "optional_view": ("tests/fixtures/anchor-slicing/task-review-sample.md", "current-effective.md"),
        "required_header_fields": {
            "initiative_key": "anchor-sliced-dispatch-optimization",
            "milestone_key": "ASDO-M2",
            "task_key": "ASDO-T5",
        },
        "required_handoff_fields": {
            "kind": "review_handoff",
            "round": "2",
            "review_target_ref": "commits/sample-a2",
            "compare_base_ref": "commits/sample-a1",
        },
    },
    "Milestone Review": {
        "required_slices": {
            ("docs/initiatives/active/anchor-sliced-dispatch-optimization/total-task-doc.md", "milestone-master-table/milestone-acceptance/asdo-m2"),
            ("docs/initiatives/active/anchor-sliced-dispatch-optimization/total-task-doc.md", "milestone-master-table/milestone-reference-assignment/asdo-m2"),
            ("docs/initiatives/active/anchor-sliced-dispatch-optimization/total-task-doc.md", "acceptance-matrix/milestone-acceptance-index/asdo-m2"),
            ("docs/initiatives/active/anchor-sliced-dispatch-optimization/total-task-doc.md", "acceptance-matrix/evidence-entrypoints"),
        },
        "optional_view": ("tests/codex/token-benchmark/fixtures/milestone-review-sample.md", "current-effective.md"),
        "required_header_fields": {
            "initiative_key": "anchor-sliced-dispatch-optimization",
            "milestone_key": "ASDO-M2",
        },
        "required_handoff_fields": {
            "kind": "review_handoff",
            "round": "1",
            "review_target_ref": "milestone-rounds/asdo-m2/r1",
            "compare_base_ref": "milestone-rounds/asdo-m2/r0",
        },
    },
    "Initiative Review": {
        "required_slices": {
            ("docs/initiatives/active/anchor-sliced-dispatch-optimization/total-task-doc.md", "initiative/success-criteria/ic-5"),
            ("docs/initiatives/active/anchor-sliced-dispatch-optimization/total-task-doc.md", "acceptance-matrix/initiative-acceptance-index/ic-5"),
            ("docs/initiatives/active/anchor-sliced-dispatch-optimization/total-task-doc.md", "acceptance-matrix/evidence-entrypoints"),
        },
        "optional_view": ("tests/codex/token-benchmark/fixtures/initiative-review-sample.md", "current-effective.md"),
        "required_header_fields": {
            "initiative_key": "anchor-sliced-dispatch-optimization",
        },
        "required_handoff_fields": {
            "kind": "review_handoff",
            "round": "1",
            "review_target_ref": "initiative-rounds/asdo/r1",
            "compare_base_ref": "initiative-rounds/asdo/r0",
        },
    },
}

HEADER_FIELD_RE = re.compile(r"^(initiative_key|milestone_key|task_key):\s*(.+?)\s*$", re.MULTILINE)
BLOCK_RE = re.compile(r"```forgeloop\n(.*?)\n```", re.DOTALL)
FIELD_RE = re.compile(r"^([a-z_]+):\s*(.+?)\s*$")


def parse_forgeloop_blocks(text):
    blocks = []
    for match in BLOCK_RE.finditer(text):
        fields = {}
        for line in match.group(1).splitlines():
            field_match = FIELD_RE.match(line.strip())
            if field_match:
                fields[field_match.group(1)] = field_match.group(2)
        if fields:
            blocks.append(fields)
    return blocks

for scenario in scenarios:
    requirements = reviewer_requirements.get(scenario["name"])
    if not requirements:
        continue
    packet = scenario["minimal_packet"]
    slices = {
        (item.get("doc"), item.get("anchor"))
        for item in packet
        if item.get("type") == "slice"
    }
    missing = sorted(requirements["required_slices"] - slices)
    if missing:
        raise SystemExit(
            f"runtime packet lint: reviewer minimal packet missing object-local slice(s) in scenario {scenario['name']}: {missing}"
        )
    views = {
        (item.get("doc"), item.get("view"))
        for item in packet
        if item.get("type") == "derived_view"
    }
    optional_view = requirements.get("optional_view")
    if optional_view and optional_view in views:
        fixture_path = Path(optional_view[0])
        fixture_text = fixture_path.read_text()
        header_fields = dict(HEADER_FIELD_RE.findall(fixture_text))
        blocks = parse_forgeloop_blocks(fixture_text)
        for field, expected in requirements.get("required_header_fields", {}).items():
            actual = header_fields.get(field)
            if actual != expected:
                raise SystemExit(
                    f"runtime packet lint: reviewer fixture/header mismatch in scenario {scenario['name']}: "
                    f"{field} expected {expected!r} got {actual!r}"
                )
        required_handoff_fields = requirements.get("required_handoff_fields", {})
        if required_handoff_fields:
            matched_block = None
            for block in blocks:
                if all(block.get(field) == expected for field, expected in required_handoff_fields.items()):
                    matched_block = block
                    break
            if matched_block is None:
                raise SystemExit(
                    f"runtime packet lint: reviewer fixture/handoff mismatch in scenario {scenario['name']}: "
                    f"missing compare-pair block {required_handoff_fields}"
                )
PY

echo "runtime packet lint passed"
