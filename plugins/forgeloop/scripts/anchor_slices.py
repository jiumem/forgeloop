#!/usr/bin/env python3

from __future__ import annotations

import argparse
import dataclasses
import pathlib
import re
import shutil
import sys
from collections import defaultdict


ANCHOR_RE = re.compile(r"^\s*<!--\s*forgeloop:anchor\s+([a-z0-9._/-]+)\s*-->\s*$")
SELECTOR_RE = re.compile(r"^[a-z0-9._/-]+$")
ANCHOR_MARKER_RE = re.compile(r"forgeloop:anchor")
CODE_FENCE_RE = re.compile(r"^\s*```")
FENCE_START = re.compile(r"^\s*```forgeloop\s*$")
FENCE_END = re.compile(r"^\s*```\s*$")
REQUIRED_SELECTORS_BY_SUFFIX: dict[str, frozenset[str]] = {
    "plugins/forgeloop/skills/planning-loop/references/design-doc.md": frozenset(
        {
            "document-position",
            "questions-this-doc-must-answer",
            "required-structure",
            "text-anchor-requirement",
            "section-contracts",
            "document-card",
            "requirement-baseline",
            "design-verdict-summary",
            "scope-and-non-goals",
            "target-state-design",
            "key-decisions-and-rejected-alternatives",
            "correctness-surface",
            "residual-risks-and-follow-ups",
            "writing-rules",
            "prohibited-content",
            "review-ready-standard",
            "seal-standard",
        }
    ),
    "plugins/forgeloop/skills/planning-loop/references/gap-analysis.md": frozenset(
        {
            "document-position",
            "questions-this-doc-must-answer",
            "required-structure",
            "text-anchor-requirement",
            "section-contracts",
            "document-card",
            "baseline-and-scope",
            "gap-verdict-summary",
            "current-state-snapshot",
            "gap-ledger",
            "convergence-strategy",
            "correctness-surface",
            "residual-risks-and-follow-ups",
            "writing-rules",
            "prohibited-content",
            "review-ready-standard",
            "seal-standard",
        }
    ),
    "plugins/forgeloop/skills/planning-loop/references/total-task-doc.md": frozenset(
        {
            "document-position",
            "questions-this-doc-must-answer",
            "required-structure",
            "text-anchor-requirement",
            "section-contracts",
            "input-baseline-and-sealed-decisions",
            "initiative",
            "milestone-master-table",
            "task-ledger",
            "branch-pr-integration-path",
            "acceptance-matrix",
            "global-residual-risks-and-follow-ups",
            "writing-rules",
            "prohibited-content",
            "review-ready-standard",
            "seal-standard",
        }
    ),
}
FIELD_PATTERNS = {
    "kind": re.compile(r"^kind:\s*(.+?)\s*$"),
    "round": re.compile(r"^round:\s*(.+?)\s*$"),
    "handoff_id": re.compile(r"^handoff_id:\s*(.+?)\s*$"),
    "review_target_ref": re.compile(r"^review_target_ref:\s*(.+?)\s*$"),
    "next_action": re.compile(r"^next_action:\s*(.+?)\s*$"),
    "verdict": re.compile(r"^verdict:\s*(.+?)\s*$"),
    "requirement_fit": re.compile(r"^requirement_fit:\s*(.+?)\s*$"),
    "boundary_correctness": re.compile(r"^boundary_correctness:\s*(.+?)\s*$"),
    "structural_soundness": re.compile(r"^structural_soundness:\s*(.+?)\s*$"),
    "downstream_planning_readiness": re.compile(r"^downstream_planning_readiness:\s*(.+?)\s*$"),
    "correctness_surface": re.compile(r"^correctness_surface:\s*(.+?)\s*$"),
    "current_state_evidence": re.compile(r"^current_state_evidence:\s*(.+?)\s*$"),
    "gap_ledger_integrity": re.compile(r"^gap_ledger_integrity:\s*(.+?)\s*$"),
    "convergence_strategy": re.compile(r"^convergence_strategy:\s*(.+?)\s*$"),
    "execution_boundary": re.compile(r"^execution_boundary:\s*(.+?)\s*$"),
    "object_map_integrity": re.compile(r"^object_map_integrity:\s*(.+?)\s*$"),
    "acceptance_truth_integrity": re.compile(r"^acceptance_truth_integrity:\s*(.+?)\s*$"),
    "integration_path": re.compile(r"^integration_path:\s*(.+?)\s*$"),
    "runtime_readiness": re.compile(r"^runtime_readiness:\s*(.+?)\s*$"),
    "residual_risk_boundary": re.compile(r"^residual_risk_boundary:\s*(.+?)\s*$"),
    "functional_correctness": re.compile(r"^functional_correctness:\s*(.+?)\s*$"),
    "validation_adequacy": re.compile(r"^validation_adequacy:\s*(.+?)\s*$"),
    "local_structure_convergence": re.compile(r"^local_structure_convergence:\s*(.+?)\s*$"),
    "local_regression_risk": re.compile(r"^local_regression_risk:\s*(.+?)\s*$"),
    "stage_structure_convergence": re.compile(r"^stage_structure_convergence:\s*(.+?)\s*$"),
    "mainline_merge_safety": re.compile(r"^mainline_merge_safety:\s*(.+?)\s*$"),
    "delivery_readiness": re.compile(r"^delivery_readiness:\s*(.+?)\s*$"),
    "release_safety": re.compile(r"^release_safety:\s*(.+?)\s*$"),
    "evidence_adequacy": re.compile(r"^evidence_adequacy:\s*(.+?)\s*$"),
    "residual_risks": re.compile(r"^residual_risks:\s*(.*?)\s*$"),
    "required_follow_ups": re.compile(r"^required_follow_ups:\s*(.*?)\s*$"),
    "open_issues": re.compile(r"^open_issues:\s*(.*?)\s*$"),
    "findings": re.compile(r"^findings:\s*(.*?)\s*$"),
    "seal_status": re.compile(r"^seal_status:\s*(.+?)\s*$"),
    "initiative_key": re.compile(r"^initiative_key:\s*(.+?)\s*$"),
    "milestone_key": re.compile(r"^milestone_key:\s*(.+?)\s*$"),
    "task_key": re.compile(r"^task_key:\s*(.+?)\s*$"),
    "planner_slot": re.compile(r"^planner_slot:\s*(.+?)\s*$"),
    "coder_slot": re.compile(r"^coder_slot:\s*(.+?)\s*$"),
    "stage": re.compile(r"^stage:\s*(.+?)\s*$"),
    "artifact_ref": re.compile(r"^artifact_ref:\s*(.+?)\s*$"),
    "stage_reference_ref": re.compile(r"^stage_reference_ref:\s*(.+?)\s*$"),
    "rolling_doc_contract_ref": re.compile(r"^rolling_doc_contract_ref:\s*(.+?)\s*$"),
    "author_role": re.compile(r"^author_role:\s*(.+?)\s*$"),
    "created_at": re.compile(r"^created_at:\s*(.+?)\s*$"),
}
PRESENCE_ONLY_FIELDS = frozenset({"residual_risks", "required_follow_ups", "open_issues", "findings"})


@dataclasses.dataclass
class Anchor:
    selector: str
    start_line: int
    end_line: int
    body: str


@dataclasses.dataclass
class ForgeloopBlock:
    raw: str
    start_line: int
    fields: dict[str, str]


@dataclasses.dataclass(frozen=True)
class RollingDocModeSpec:
    header_kind: str
    snapshot_kinds: frozenset[str]
    round_scoped_kinds: frozenset[str]
    handoff_kinds: frozenset[str]
    result_kinds: frozenset[str]

    @property
    def legal_kinds(self) -> frozenset[str]:
        return self.snapshot_kinds | self.round_scoped_kinds | {self.header_kind}


@dataclasses.dataclass(frozen=True)
class BlockSpec:
    required_fields: frozenset[str] = frozenset()
    author_role: str | None = None
    next_actions: frozenset[str] | None = None


BLOCK_SPECS = {
    "planning_rolling_header": BlockSpec(
        required_fields=frozenset({"initiative_key", "stage", "artifact_ref", "planner_slot", "created_at"})
    ),
    "planning_contract_snapshot": BlockSpec(
        required_fields=frozenset(
            {"created_at", "stage", "artifact_ref", "stage_reference_ref", "rolling_doc_contract_ref"}
        )
    ),
    "planner_update": BlockSpec(
        required_fields=frozenset({"round", "author_role", "created_at", "next_action"}),
        author_role="planner",
        next_actions=frozenset(
            {
                "continue_stage_repair",
                "request_reviewer_handoff",
                "wait_for_upstream_judgment",
                "stop_on_blocker",
            }
        ),
    ),
    "design_doc_ref": BlockSpec(
        required_fields=frozenset({"round", "author_role", "created_at", "handoff_id", "review_target_ref"}),
        author_role="planner",
    ),
    "gap_analysis_ref": BlockSpec(
        required_fields=frozenset({"round", "author_role", "created_at", "handoff_id", "review_target_ref"}),
        author_role="planner",
    ),
    "total_task_doc_ref": BlockSpec(
        required_fields=frozenset({"round", "author_role", "created_at", "handoff_id", "review_target_ref"}),
        author_role="planner",
    ),
    "design_review_result": BlockSpec(
        required_fields=frozenset(
            {
                "round",
                "author_role",
                "created_at",
                "handoff_id",
                "review_target_ref",
                "verdict",
                "seal_status",
                "requirement_fit",
                "boundary_correctness",
                "structural_soundness",
                "downstream_planning_readiness",
                "correctness_surface",
                "open_issues",
                "next_action",
                "findings",
            }
        ),
        author_role="reviewer",
    ),
    "gap_review_result": BlockSpec(
        required_fields=frozenset(
            {
                "round",
                "author_role",
                "created_at",
                "handoff_id",
                "review_target_ref",
                "verdict",
                "seal_status",
                "current_state_evidence",
                "gap_ledger_integrity",
                "convergence_strategy",
                "downstream_planning_readiness",
                "correctness_surface",
                "open_issues",
                "next_action",
                "findings",
            }
        ),
        author_role="reviewer",
    ),
    "total_task_doc_review_result": BlockSpec(
        required_fields=frozenset(
            {
                "round",
                "author_role",
                "created_at",
                "handoff_id",
                "review_target_ref",
                "verdict",
                "seal_status",
                "execution_boundary",
                "object_map_integrity",
                "acceptance_truth_integrity",
                "integration_path",
                "runtime_readiness",
                "residual_risk_boundary",
                "open_issues",
                "next_action",
                "findings",
            }
        ),
        author_role="reviewer",
    ),
    "task_review_header": BlockSpec(
        required_fields=frozenset({"initiative_key", "milestone_key", "task_key", "coder_slot", "created_at"})
    ),
    "task_contract_snapshot": BlockSpec(),
    "coder_update": BlockSpec(required_fields=frozenset({"round", "author_role", "created_at"}), author_role="coder"),
    "g1_result": BlockSpec(
        required_fields=frozenset({"round", "author_role", "created_at", "verdict", "next_action"}),
        author_role="coder",
        next_actions=frozenset(
            {
                "continue_task_coder_round",
                "request_reviewer_handoff",
                "wait_for_user",
                "stop_on_blocker",
            }
        ),
    ),
    "anchor_ref": BlockSpec(
        required_fields=frozenset({"round", "author_role", "created_at", "handoff_id", "review_target_ref"}),
        author_role="coder",
    ),
    "fixup_ref": BlockSpec(
        required_fields=frozenset({"round", "author_role", "created_at", "handoff_id", "review_target_ref"}),
        author_role="coder",
    ),
    "r1_result": BlockSpec(
        required_fields=frozenset(
            {
                "round",
                "author_role",
                "created_at",
                "handoff_id",
                "review_target_ref",
                "verdict",
                "functional_correctness",
                "validation_adequacy",
                "local_structure_convergence",
                "local_regression_risk",
                "open_issues",
                "next_action",
                "findings",
            }
        ),
        author_role="reviewer",
        next_actions=frozenset(
            {
                "continue_task_repair",
                "return_to_source_object",
                "select_next_ready_object",
                "task_done",
                "escalate_to_milestone",
                "wait_for_user",
                "stop_on_blocker",
            }
        ),
    ),
    "milestone_review_header": BlockSpec(
        required_fields=frozenset({"initiative_key", "milestone_key", "coder_slot", "created_at"})
    ),
    "milestone_contract_snapshot": BlockSpec(),
    "g2_result": BlockSpec(
        required_fields=frozenset({"round", "author_role", "created_at", "verdict", "next_action"}),
        author_role="coder",
        next_actions=frozenset(
            {
                "continue_milestone_repair",
                "objectize_task_repair",
                "enter_r2",
                "wait_for_user",
                "stop_on_blocker",
            }
        ),
    ),
    "r2_result": BlockSpec(
        required_fields=frozenset(
            {
                "round",
                "author_role",
                "created_at",
                "handoff_id",
                "review_target_ref",
                "verdict",
                "stage_structure_convergence",
                "mainline_merge_safety",
                "evidence_adequacy",
                "residual_risks",
                "open_issues",
                "next_action",
                "required_follow_ups",
                "findings",
            }
        ),
        author_role="reviewer",
        next_actions=frozenset(
            {
                "continue_milestone_repair",
                "objectize_task_repair",
                "enter_initiative_review",
                "select_next_ready_object",
                "wait_for_user",
                "stop_on_blocker",
            }
        ),
    ),
    "initiative_review_header": BlockSpec(required_fields=frozenset({"initiative_key", "coder_slot", "created_at"})),
    "initiative_contract_snapshot": BlockSpec(),
    "g3_result": BlockSpec(
        required_fields=frozenset({"round", "author_role", "created_at", "verdict", "next_action"}),
        author_role="coder",
        next_actions=frozenset(
            {
                "continue_initiative_repair",
                "objectize_task_repair",
                "enter_r3",
                "wait_for_user",
                "stop_on_blocker",
            }
        ),
    ),
    "r3_result": BlockSpec(
        required_fields=frozenset(
            {
                "round",
                "author_role",
                "created_at",
                "handoff_id",
                "review_target_ref",
                "verdict",
                "delivery_readiness",
                "release_safety",
                "evidence_adequacy",
                "residual_risks",
                "open_issues",
                "next_action",
                "required_follow_ups",
                "findings",
            }
        ),
        author_role="reviewer",
        next_actions=frozenset(
            {
                "continue_initiative_repair",
                "objectize_task_repair",
                "mark_initiative_delivered",
                "wait_for_user",
                "stop_on_blocker",
            }
        ),
    ),
}


MODE_SPECS = {
    "planning": RollingDocModeSpec(
        header_kind="planning_rolling_header",
        snapshot_kinds=frozenset({"planning_contract_snapshot"}),
        round_scoped_kinds=frozenset(
            {
                "planner_update",
                "design_doc_ref",
                "gap_analysis_ref",
                "total_task_doc_ref",
                "design_review_result",
                "gap_review_result",
                "total_task_doc_review_result",
            }
        ),
        handoff_kinds=frozenset({"design_doc_ref", "gap_analysis_ref", "total_task_doc_ref"}),
        result_kinds=frozenset({"design_review_result", "gap_review_result", "total_task_doc_review_result"}),
    ),
    "task": RollingDocModeSpec(
        header_kind="task_review_header",
        snapshot_kinds=frozenset({"task_contract_snapshot"}),
        round_scoped_kinds=frozenset({"coder_update", "g1_result", "anchor_ref", "fixup_ref", "r1_result"}),
        handoff_kinds=frozenset({"anchor_ref", "fixup_ref"}),
        result_kinds=frozenset({"r1_result"}),
    ),
    "milestone": RollingDocModeSpec(
        header_kind="milestone_review_header",
        snapshot_kinds=frozenset({"milestone_contract_snapshot"}),
        round_scoped_kinds=frozenset({"coder_update", "g2_result", "r2_result"}),
        handoff_kinds=frozenset({"g2_result"}),
        result_kinds=frozenset({"r2_result"}),
    ),
    "initiative": RollingDocModeSpec(
        header_kind="initiative_review_header",
        snapshot_kinds=frozenset({"initiative_contract_snapshot"}),
        round_scoped_kinds=frozenset({"coder_update", "g3_result", "r3_result"}),
        handoff_kinds=frozenset({"g3_result"}),
        result_kinds=frozenset({"r3_result"}),
    ),
}


def read_lines(path: pathlib.Path) -> list[str]:
    return path.read_text().splitlines()


def iter_non_fenced_lines(lines: list[str]):
    in_fenced_block = False
    for line_no, line in enumerate(lines, start=1):
        if CODE_FENCE_RE.match(line):
            in_fenced_block = not in_fenced_block
            continue
        if not in_fenced_block:
            yield line_no, line


def collect_anchor_occurrences(lines: list[str]) -> dict[str, list[int]]:
    occurrences: dict[str, list[int]] = defaultdict(list)
    for line_no, line in iter_non_fenced_lines(lines):
        match = ANCHOR_RE.match(line)
        if match:
            occurrences[match.group(1)].append(line_no)
    return occurrences


def find_illegal_anchor_lines(lines: list[str]) -> list[int]:
    illegal_lines: list[int] = []
    for line_no, line in iter_non_fenced_lines(lines):
        if ANCHOR_MARKER_RE.search(line) and not ANCHOR_RE.match(line):
            illegal_lines.append(line_no)
    return illegal_lines


def parse_anchors(path: pathlib.Path) -> list[Anchor]:
    lines = read_lines(path)
    illegal_lines = find_illegal_anchor_lines(lines)
    if illegal_lines:
        rendered = ",".join(str(line_no) for line_no in illegal_lines)
        raise ValueError(f"{path}: illegal anchor syntax on line(s): {rendered}")
    occurrences = collect_anchor_occurrences(lines)
    duplicates = {selector: locs for selector, locs in occurrences.items() if len(locs) > 1}
    if duplicates:
        rendered = ", ".join(
            f"{selector}@{','.join(str(loc) for loc in locs)}" for selector, locs in sorted(duplicates.items())
        )
        raise ValueError(f"{path}: duplicate anchors found: {rendered}")

    anchors: list[tuple[str, int]] = []
    for line_no, line in iter_non_fenced_lines(lines):
        match = ANCHOR_RE.match(line)
        if match:
            anchors.append((match.group(1), line_no))

    parsed: list[Anchor] = []
    for index, (selector, start_line) in enumerate(anchors):
        end_line = anchors[index + 1][1] - 1 if index + 1 < len(anchors) else len(lines)
        body_lines = lines[start_line:end_line]
        parsed.append(
            Anchor(
                selector=selector,
                start_line=start_line + 1,
                end_line=end_line,
                body="\n".join(body_lines).strip(),
            )
        )
    empty_selectors = [anchor.selector for anchor in parsed if not anchor.body]
    if empty_selectors:
        rendered = ", ".join(empty_selectors)
        raise ValueError(f"{path}: empty slice for selector(s): {rendered}")
    return parsed


def required_selectors_for_path(path: pathlib.Path) -> frozenset[str]:
    normalized = path.as_posix()
    for suffix, selectors in REQUIRED_SELECTORS_BY_SUFFIX.items():
        if normalized.endswith(suffix):
            return selectors
    return frozenset()


def validate_required_selectors(path: pathlib.Path, anchors: list[Anchor]) -> None:
    required = required_selectors_for_path(path)
    if not required:
        return
    existing = {anchor.selector for anchor in anchors}
    missing = sorted(required - existing)
    if missing:
        raise ValueError(f"{path}: missing required selectors: {', '.join(missing)}")


def parse_forgeloop_blocks(path: pathlib.Path) -> list[ForgeloopBlock]:
    lines = read_lines(path)
    blocks: list[ForgeloopBlock] = []
    in_block = False
    start_line = 0
    body: list[str] = []
    for line_no, line in enumerate(lines, start=1):
        if not in_block and FENCE_START.match(line):
            in_block = True
            start_line = line_no + 1
            body = []
            continue
        if in_block and FENCE_END.match(line):
            raw = "\n".join(body).strip()
            fields: dict[str, str] = {}
            for body_line in body:
                stripped = body_line.strip()
                for key, pattern in FIELD_PATTERNS.items():
                    match = pattern.match(stripped)
                    if match and key not in fields:
                        captured = match.group(1)
                        if key in PRESENCE_ONLY_FIELDS and not captured.strip():
                            fields[key] = "__present__"
                        else:
                            fields[key] = captured
            blocks.append(ForgeloopBlock(raw=raw, start_line=start_line, fields=fields))
            in_block = False
            body = []
            continue
        if in_block:
            body.append(line)
    if in_block:
        raise ValueError(f"{path}: unclosed forgeloop fence starting at line {start_line - 1}")
    return blocks


def check(paths: list[pathlib.Path]) -> int:
    failures: list[str] = []
    for path in paths:
        if path.suffix != ".md":
            continue
        try:
            anchors = parse_anchors(path)
            validate_required_selectors(path, anchors)
        except ValueError as exc:
            failures.append(str(exc))
    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1
    return 0


def print_slice(doc: pathlib.Path, selector: str) -> int:
    if not SELECTOR_RE.fullmatch(selector):
        print(f"{doc}: illegal_selector {selector}", file=sys.stderr)
        return 2
    anchors = {anchor.selector: anchor for anchor in parse_anchors(doc)}
    if selector not in anchors:
        print(f"{doc}: missing anchor {selector}", file=sys.stderr)
        return 2
    anchor = anchors[selector]
    print(anchor.body)
    return 0


def detect_mode(blocks: list[ForgeloopBlock]) -> str:
    header_kind = next((block.fields.get("kind") for block in blocks if block.fields.get("kind", "").endswith("_header")), "")
    for mode, spec in MODE_SPECS.items():
        if header_kind == spec.header_kind:
            return mode
    raise ValueError("unsupported rolling doc kind")


def is_handoff_block(mode: str, fields: dict[str, str]) -> bool:
    spec = MODE_SPECS[mode]
    kind = fields.get("kind")
    next_action = fields.get("next_action")
    if kind not in spec.handoff_kinds:
        return False
    if mode in {"planning", "task"}:
        return True
    if mode == "milestone":
        return next_action == "enter_r2"
    if mode == "initiative":
        return next_action == "enter_r3"
    return False


def is_result_block(mode: str, fields: dict[str, str]) -> bool:
    return fields.get("kind") in MODE_SPECS[mode].result_kinds


def is_round_scoped_block(mode: str, fields: dict[str, str]) -> bool:
    return fields.get("kind") in MODE_SPECS[mode].round_scoped_kinds


def latest_by_round(blocks: list[ForgeloopBlock], mode: str) -> dict[str, list[ForgeloopBlock]]:
    grouped: dict[str, list[ForgeloopBlock]] = defaultdict(list)
    for block in blocks:
        if is_round_scoped_block(mode, block.fields):
            grouped[block.fields["round"].strip()].append(block)
    return dict(sorted(grouped.items(), key=lambda item: int(item[0])))


def latest_round(blocks_by_round: dict[str, list[ForgeloopBlock]]) -> tuple[str, list[ForgeloopBlock]] | None:
    if not blocks_by_round:
        return None
    round_id = max(blocks_by_round, key=lambda value: int(value))
    return round_id, blocks_by_round[round_id]


def has_real_tuple_value(value: str | None) -> bool:
    if value is None:
        return False
    normalized = value.strip()
    if not normalized:
        return False
    return normalized.lower() not in {"null", "none", "n/a", "na"}


def has_valid_round_value(value: str | None) -> bool:
    if not has_real_tuple_value(value):
        return False
    normalized = value.strip()
    return normalized.isdigit() and int(normalized) > 0


def validate_block_schema(doc: pathlib.Path, blocks: list[ForgeloopBlock], mode: str) -> None:
    spec = MODE_SPECS[mode]
    illegal_kinds: list[str] = []
    singleton_violations: list[str] = []
    round_violations: list[str] = []
    field_violations: list[str] = []
    role_violations: list[str] = []
    next_action_violations: list[str] = []
    kind_counts: dict[str, int] = defaultdict(int)
    for block in blocks:
        kind = block.fields.get("kind")
        if not kind or kind not in spec.legal_kinds:
            illegal_kinds.append(f"{kind or 'unknown_kind'}@{block.start_line}")
            continue
        kind_counts[kind] += 1
        block_spec = BLOCK_SPECS.get(kind, BlockSpec())
        missing = [field for field in sorted(block_spec.required_fields) if not has_real_tuple_value(block.fields.get(field))]
        if missing:
            field_violations.append(f"{kind}@{block.start_line} missing {','.join(missing)}")
        if is_round_scoped_block(mode, block.fields):
            round_value = block.fields.get("round")
            if not has_real_tuple_value(round_value):
                round_violations.append(f"{kind}@{block.start_line} missing round")
            elif not has_valid_round_value(round_value):
                round_violations.append(f"{kind}@{block.start_line} invalid round={round_value.strip()}")
        if block_spec.author_role is not None and has_real_tuple_value(block.fields.get("author_role")):
            actual_role = block.fields["author_role"].strip()
            if actual_role != block_spec.author_role:
                role_violations.append(f"{kind}@{block.start_line} author_role={actual_role} expected {block_spec.author_role}")
        if block_spec.next_actions is not None and has_real_tuple_value(block.fields.get("next_action")):
            next_action = block.fields["next_action"].strip()
            if next_action not in block_spec.next_actions:
                next_action_violations.append(f"{kind}@{block.start_line} next_action={next_action}")
    for singleton_kind in (spec.header_kind, *sorted(spec.snapshot_kinds)):
        count = kind_counts.get(singleton_kind, 0)
        if count != 1:
            singleton_violations.append(f"{singleton_kind} count={count}")
    if illegal_kinds:
        raise ValueError(f"{doc}: illegal formal block kinds: {', '.join(illegal_kinds)}")
    if singleton_violations:
        raise ValueError(f"{doc}: singleton block violations: {', '.join(singleton_violations)}")
    if round_violations:
        raise ValueError(f"{doc}: malformed round-scoped blocks: {'; '.join(round_violations)}")
    if field_violations:
        raise ValueError(f"{doc}: malformed block fields: {'; '.join(field_violations)}")
    if role_violations:
        raise ValueError(f"{doc}: malformed author_role values: {'; '.join(role_violations)}")
    if next_action_violations:
        raise ValueError(f"{doc}: malformed next_action values: {'; '.join(next_action_violations)}")


def validate_tuple_fields(doc: pathlib.Path, blocks: list[ForgeloopBlock], mode: str) -> None:
    violations: list[str] = []
    for block in blocks:
        if not (is_handoff_block(mode, block.fields) or is_result_block(mode, block.fields)):
            continue
        missing = []
        if not has_real_tuple_value(block.fields.get("handoff_id")):
            missing.append("handoff_id")
        if not has_real_tuple_value(block.fields.get("review_target_ref")):
            missing.append("review_target_ref")
        if missing:
            violations.append(
                f"{block.fields.get('kind', 'unknown_kind')}@{block.start_line} missing {','.join(missing)}"
            )
    if violations:
        raise ValueError(f"{doc}: malformed block fields: {'; '.join(violations)}")


def block_tuple(block: ForgeloopBlock) -> tuple[str, str, str]:
    return (
        block.fields["round"].strip(),
        block.fields["handoff_id"].strip(),
        block.fields["review_target_ref"].strip(),
    )


def validate_result_handoff_consistency(doc: pathlib.Path, blocks: list[ForgeloopBlock], mode: str) -> None:
    handoff_tuples = {block_tuple(block) for block in blocks if is_handoff_block(mode, block.fields)}
    violations: list[str] = []
    for block in blocks:
        if not is_result_block(mode, block.fields):
            continue
        result_tuple = block_tuple(block)
        if result_tuple not in handoff_tuples:
            rendered = "/".join(result_tuple)
            violations.append(f"{block.fields.get('kind', 'unknown_kind')}@{block.start_line} has no matching handoff tuple {rendered}")
    if violations:
        raise ValueError(f"{doc}: result/handoff tuple mismatches: {'; '.join(violations)}")


def collect_handoff_blocks(
    doc: pathlib.Path,
    blocks: list[ForgeloopBlock],
    mode: str,
) -> dict[str, ForgeloopBlock]:
    handoff_index: dict[str, ForgeloopBlock] = {}
    duplicates: dict[str, list[int]] = defaultdict(list)
    for block in blocks:
        if not is_handoff_block(mode, block.fields):
            continue
        handoff_id = block.fields.get("handoff_id")
        if not handoff_id:
            continue
        if handoff_id in handoff_index:
            duplicates[handoff_id].append(block.start_line)
            if len(duplicates[handoff_id]) == 1:
                duplicates[handoff_id].insert(0, handoff_index[handoff_id].start_line)
            continue
        handoff_index[handoff_id] = block
    if duplicates:
        rendered = ", ".join(
            f"{handoff_id}@{','.join(str(line) for line in lines)}"
            for handoff_id, lines in sorted(duplicates.items())
        )
        raise ValueError(f"{doc}: duplicate handoff_id found among handoff blocks: {rendered}")
    return handoff_index


def write_text(path: pathlib.Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def reset_derived_dir(out: pathlib.Path) -> None:
    current_effective = out / "current-effective.md"
    if current_effective.exists():
        current_effective.unlink()
    for child in ("attempt-aware", "handoff-scoped"):
        shutil.rmtree(out / child, ignore_errors=True)


def derive(doc: pathlib.Path, out: pathlib.Path) -> int:
    reset_derived_dir(out)
    blocks = parse_forgeloop_blocks(doc)
    mode = detect_mode(blocks)
    validate_block_schema(doc, blocks, mode)
    validate_tuple_fields(doc, blocks, mode)
    validate_result_handoff_consistency(doc, blocks, mode)
    grouped = latest_by_round(blocks, mode)
    handoff_index = collect_handoff_blocks(doc, blocks, mode)
    latest_round_data = latest_round(grouped)
    current_effective_lines = [
        f"# Derived View: {doc.name}",
        "",
        "> Non-authoritative. Rebuild from the formal rolling doc at any time.",
        "",
    ]
    if latest_round_data is None:
        current_effective_lines.extend(
            [
                "## Current Frontier",
                "",
                "_No round-scoped formal blocks._",
                "",
            ]
        )
    else:
        current_round_id, current_round_blocks = latest_round_data
        current_handoff = next(
            (block for block in reversed(current_round_blocks) if is_handoff_block(mode, block.fields)),
            None,
        )
        current_result = None
        if current_handoff:
            handoff_id = current_handoff.fields.get("handoff_id")
            review_target_ref = current_handoff.fields.get("review_target_ref")
            for block in reversed(current_round_blocks):
                if not is_result_block(mode, block.fields):
                    continue
                if (
                    block.fields.get("handoff_id") == handoff_id
                    and block.fields.get("review_target_ref") == review_target_ref
                ):
                    current_result = block
                    break

        current_effective_lines.append(f"## Current Frontier: round {current_round_id}")
        if current_handoff:
            current_effective_lines.extend(
                [
                    "",
                    "### Current Handoff",
                    "",
                    "```forgeloop",
                    current_handoff.raw,
                    "```",
                ]
            )
        else:
            current_effective_lines.extend(["", "_No current handoff._"])
        if current_result:
            current_effective_lines.extend(
                [
                    "",
                    "### Latest Matching Result",
                    "",
                    "```forgeloop",
                    current_result.raw,
                    "```",
                ]
            )
        current_effective_lines.append("")

        for round_id, round_blocks in grouped.items():
            round_lines = [
                f"# Attempt-Aware View: round {round_id}",
                "",
                "> Non-authoritative. Rebuild from the formal rolling doc at any time.",
                "",
            ]
            for block in round_blocks:
                round_lines.extend(["```forgeloop", block.raw, "```", ""])
            write_text(out / "attempt-aware" / f"round-{round_id}.md", "\n".join(round_lines).rstrip() + "\n")

    write_text(out / "current-effective.md", "\n".join(current_effective_lines).rstrip() + "\n")

    for handoff_id, handoff_block in handoff_index.items():
        handoff_tuple = block_tuple(handoff_block)
        handoff_lines = [
            f"# Handoff-Scoped View: {handoff_id}",
            "",
            "> Non-authoritative. Rebuild from the formal rolling doc at any time.",
            "",
            "## Handoff",
            "",
            "```forgeloop",
            handoff_block.raw,
            "```",
            "",
        ]
        for block in blocks:
            if block is handoff_block:
                continue
            if not is_result_block(mode, block.fields):
                continue
            if block_tuple(block) != handoff_tuple:
                continue
            handoff_lines.extend(["```forgeloop", block.raw, "```", ""])
        write_text(out / "handoff-scoped" / f"{handoff_id}.md", "\n".join(handoff_lines).rstrip() + "\n")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate and materialize Forgeloop anchor-addressed slices.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    check_parser = subparsers.add_parser(
        "check", help="Validate anchor syntax, duplicates, empty slices, and required-selector coverage."
    )
    check_parser.add_argument("paths", nargs="+")

    slice_parser = subparsers.add_parser("slice", help="Print one addressed slice.")
    slice_parser.add_argument("--doc", required=True)
    slice_parser.add_argument("--anchor", required=True)

    derive_parser = subparsers.add_parser("derive", help="Build disposable rolling-doc projections.")
    derive_parser.add_argument("--doc", required=True)
    derive_parser.add_argument("--out", required=True)
    return parser


def render_cli_error(exc: Exception) -> str:
    if isinstance(exc, OSError):
        return str(exc)
    return str(exc)


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        if args.command == "check":
            return check([pathlib.Path(path) for path in args.paths])
        if args.command == "slice":
            return print_slice(pathlib.Path(args.doc), args.anchor)
        if args.command == "derive":
            return derive(pathlib.Path(args.doc), pathlib.Path(args.out))
        parser.error("unknown command")
        return 1
    except (ValueError, OSError) as exc:
        print(render_cli_error(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
