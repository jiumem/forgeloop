#!/usr/bin/env python3

from __future__ import annotations

import argparse
import dataclasses
import pathlib
import re
import sys
from collections import defaultdict


ANCHOR_RE = re.compile(r"^\s*<!--\s*forgeloop:anchor\s+([a-z0-9._/-]+)\s*-->\s*$")
FENCE_START = re.compile(r"^\s*```forgeloop\s*$")
FENCE_END = re.compile(r"^\s*```\s*$")
FIELD_PATTERNS = {
    "kind": re.compile(r"^kind:\s*(.+?)\s*$"),
    "round": re.compile(r"^round:\s*(.+?)\s*$"),
    "handoff_id": re.compile(r"^handoff_id:\s*(.+?)\s*$"),
    "review_target_ref": re.compile(r"^review_target_ref:\s*(.+?)\s*$"),
    "next_action": re.compile(r"^next_action:\s*(.+?)\s*$"),
    "verdict": re.compile(r"^verdict:\s*(.+?)\s*$"),
    "author_role": re.compile(r"^author_role:\s*(.+?)\s*$"),
    "created_at": re.compile(r"^created_at:\s*(.+?)\s*$"),
}


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


def read_lines(path: pathlib.Path) -> list[str]:
    return path.read_text().splitlines()


def collect_anchor_occurrences(lines: list[str]) -> dict[str, list[int]]:
    occurrences: dict[str, list[int]] = defaultdict(list)
    for line_no, line in enumerate(lines, start=1):
        match = ANCHOR_RE.match(line)
        if match:
            occurrences[match.group(1)].append(line_no)
    return occurrences


def parse_anchors(path: pathlib.Path) -> list[Anchor]:
    lines = read_lines(path)
    occurrences = collect_anchor_occurrences(lines)
    duplicates = {selector: locs for selector, locs in occurrences.items() if len(locs) > 1}
    if duplicates:
        rendered = ", ".join(
            f"{selector}@{','.join(str(loc) for loc in locs)}" for selector, locs in sorted(duplicates.items())
        )
        raise ValueError(f"{path}: duplicate anchors found: {rendered}")

    anchors: list[tuple[str, int]] = []
    for line_no, line in enumerate(lines, start=1):
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
    return parsed


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
                        fields[key] = match.group(1)
            blocks.append(ForgeloopBlock(raw=raw, start_line=start_line, fields=fields))
            in_block = False
            body = []
            continue
        if in_block:
            body.append(line)
    return blocks


def check(paths: list[pathlib.Path]) -> int:
    failures: list[str] = []
    for path in paths:
        if path.suffix != ".md":
            continue
        try:
            parse_anchors(path)
        except ValueError as exc:
            failures.append(str(exc))
    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1
    return 0


def print_slice(doc: pathlib.Path, selector: str) -> int:
    anchors = {anchor.selector: anchor for anchor in parse_anchors(doc)}
    if selector not in anchors:
        print(f"{doc}: missing anchor {selector}", file=sys.stderr)
        return 2
    anchor = anchors[selector]
    print(anchor.body)
    return 0


def detect_mode(blocks: list[ForgeloopBlock]) -> str:
    header_kind = next((block.fields.get("kind") for block in blocks if block.fields.get("kind", "").endswith("_header")), "")
    if header_kind == "planning_rolling_header":
        return "planning"
    if header_kind == "task_review_header":
        return "task"
    if header_kind == "milestone_review_header":
        return "milestone"
    if header_kind == "initiative_review_header":
        return "initiative"
    raise ValueError("unsupported rolling doc kind")


def is_handoff_block(mode: str, fields: dict[str, str]) -> bool:
    kind = fields.get("kind")
    next_action = fields.get("next_action")
    if mode == "planning":
        return kind in {"design_doc_ref", "gap_analysis_ref", "total_task_doc_ref"}
    if mode == "task":
        return kind in {"anchor_ref", "fixup_ref"}
    if mode == "milestone":
        return kind == "g2_result" and next_action == "enter_r2"
    if mode == "initiative":
        return kind == "g3_result" and next_action == "enter_r3"
    return False


def is_result_block(mode: str, fields: dict[str, str]) -> bool:
    kind = fields.get("kind")
    if mode == "planning":
        return kind in {"design_review_result", "gap_review_result", "plan_review_result"}
    if mode == "task":
        return kind == "r1_result"
    if mode == "milestone":
        return kind == "r2_result"
    if mode == "initiative":
        return kind == "r3_result"
    return False


def latest_by_round(blocks: list[ForgeloopBlock]) -> dict[str, list[ForgeloopBlock]]:
    grouped: dict[str, list[ForgeloopBlock]] = defaultdict(list)
    for block in blocks:
        if "round" in block.fields:
            grouped[block.fields["round"]].append(block)
    return dict(sorted(grouped.items(), key=lambda item: int(item[0])))


def write_text(path: pathlib.Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def derive(doc: pathlib.Path, out: pathlib.Path) -> int:
    blocks = parse_forgeloop_blocks(doc)
    mode = detect_mode(blocks)
    grouped = latest_by_round(blocks)
    handoff_index: dict[str, ForgeloopBlock] = {}
    current_effective_lines = [
        f"# Derived View: {doc.name}",
        "",
        "> Non-authoritative. Rebuild from the formal rolling doc at any time.",
        "",
    ]
    for round_id, round_blocks in grouped.items():
        current_handoff = next((block for block in reversed(round_blocks) if is_handoff_block(mode, block.fields)), None)
        current_result = None
        if current_handoff:
            handoff_id = current_handoff.fields.get("handoff_id")
            review_target_ref = current_handoff.fields.get("review_target_ref")
            if handoff_id:
                handoff_index[handoff_id] = current_handoff
            for block in reversed(round_blocks):
                if not is_result_block(mode, block.fields):
                    continue
                if (
                    block.fields.get("handoff_id") == handoff_id
                    and block.fields.get("review_target_ref") == review_target_ref
                ):
                    current_result = block
                    break
        current_effective_lines.append(f"## Round {round_id}")
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
            if block.fields.get("handoff_id") == handoff_id:
                handoff_lines.extend(["```forgeloop", block.raw, "```", ""])
        write_text(out / "handoff-scoped" / f"{handoff_id}.md", "\n".join(handoff_lines).rstrip() + "\n")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate and materialize Forgeloop anchor-addressed slices.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    check_parser = subparsers.add_parser("check", help="Validate anchor syntax and duplicates.")
    check_parser.add_argument("paths", nargs="+")

    slice_parser = subparsers.add_parser("slice", help="Print one addressed slice.")
    slice_parser.add_argument("--doc", required=True)
    slice_parser.add_argument("--anchor", required=True)

    derive_parser = subparsers.add_parser("derive", help="Build disposable rolling-doc projections.")
    derive_parser.add_argument("--doc", required=True)
    derive_parser.add_argument("--out", required=True)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "check":
        return check([pathlib.Path(path) for path in args.paths])
    if args.command == "slice":
        return print_slice(pathlib.Path(args.doc), args.anchor)
    if args.command == "derive":
        return derive(pathlib.Path(args.doc), pathlib.Path(args.out))
    parser.error("unknown command")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
