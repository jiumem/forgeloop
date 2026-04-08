#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

check_pattern() {
  local file="$1"
  local pattern="$2"

  if ! rg -q "$pattern" "$file"; then
    echo "runtime packet lint: missing ${pattern} in ${file}"
    exit 1
  fi
}

check_pattern \
  "plugins/forgeloop/skills/references/anchor-addressing.md" \
  '`run-initiative/SKILL.md`, or `code-loop/SKILL.md`'
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

python3 - <<'PY'
import json
import re
from pathlib import Path

scenarios = json.loads(Path("tests/codex/token-benchmark/fixtures/scenarios.json").read_text())
run_initiative_text = Path("plugins/forgeloop/skills/run-initiative/SKILL.md").read_text()

frontier_priority_marker = "- frontier selection when `current_snapshot.active_plane=frontier` or `next_action.action=select_next_ready_object`"
task_priority_marker = "- task-mode code loop when a Task is clearly active"
task_next_ready_legacy = "task-mode code loop when a Task is clearly active or next-ready"
frontier_apply_marker = (
    "- if `current_snapshot.active_plane=frontier` or `next_action.action=select_next_ready_object`: "
    "resolve the next ready object from the admitted planning document set plus authoritative runtime rolling docs; "
    "container forcing applies here first. Do not short-circuit directly into Task mode merely because one next-ready Task exists."
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

targets = {
    "Same-Task Same-Round Coder Continue",
    "Same-Task Handoff To Fresh Reviewer",
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
for scenario in scenarios:
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
    "Same-Task Handoff To Fresh Reviewer": {
        "required_slices": {
            ("docs/initiatives/active/anchor-sliced-dispatch-optimization/total-task-doc.md", "task-ledger/task-definitions/asdo-t5"),
            ("docs/initiatives/active/anchor-sliced-dispatch-optimization/total-task-doc.md", "acceptance-matrix/task-acceptance-index/asdo-t5"),
            ("docs/initiatives/active/anchor-sliced-dispatch-optimization/total-task-doc.md", "acceptance-matrix/evidence-entrypoints"),
        },
        "required_view": ("tests/fixtures/anchor-slicing/task-review-sample.md", "current-effective.md"),
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
        "required_view": ("tests/codex/token-benchmark/fixtures/milestone-review-sample.md", "current-effective.md"),
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
        "required_view": ("tests/codex/token-benchmark/fixtures/initiative-review-sample.md", "current-effective.md"),
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
    if requirements["required_view"] not in views:
        raise SystemExit(
            f"runtime packet lint: reviewer minimal packet missing required review-cycle view in scenario {scenario['name']}: {requirements['required_view']}"
        )
    fixture_path = Path(requirements["required_view"][0])
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
