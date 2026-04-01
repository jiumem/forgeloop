#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
import math
import pathlib
import shutil
import subprocess
import tempfile
from dataclasses import dataclass


ROOT = pathlib.Path(__file__).resolve().parents[3]
ANCHOR_SCRIPT = ROOT / "plugins/forgeloop/scripts/anchor_slices.py"
TOTAL_REDUCTION_FLOOR = 45.0
TASK_HOT_PATH_TARGET = 50.0


@dataclass
class TextStats:
    chars: int
    lines: int
    words: int
    approx_tokens: int


def read_text(path: pathlib.Path) -> str:
    return path.read_text()


def stats_for_text(text: str) -> TextStats:
    chars = len(text)
    lines = text.count("\n") + (0 if not text else 1)
    words = len(text.split())
    approx_tokens = math.ceil(chars / 4) if chars else 0
    return TextStats(chars=chars, lines=lines, words=words, approx_tokens=approx_tokens)


def materialize_slice(doc: str, anchor: str) -> str:
    proc = subprocess.run(
        ["python3", str(ANCHOR_SCRIPT), "slice", "--doc", doc, "--anchor", anchor],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return proc.stdout


def materialize_derived(doc: str, view: str, cache_root: pathlib.Path) -> str:
    doc_path = ROOT / doc
    cache_key = hashlib.sha1(doc.encode("utf-8")).hexdigest()[:12]
    derived_root = cache_root / f"{doc_path.stem}-{cache_key}"
    if not derived_root.exists():
        subprocess.run(
            ["python3", str(ANCHOR_SCRIPT), "derive", "--doc", doc, "--out", str(derived_root)],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    return read_text(derived_root / view)


def item_label(item: dict[str, str]) -> str:
    item_type = item["type"]
    if item_type == "full_doc":
        return item["path"]
    if item_type == "slice":
        return f'{item["doc"]}#{item["anchor"]}'
    if item_type == "derived_view":
        return f'{item["doc"]}::{item["view"]}'
    raise ValueError(f"unsupported item type: {item_type}")


def item_text(item: dict[str, str], cache_root: pathlib.Path) -> str:
    item_type = item["type"]
    if item_type == "full_doc":
        return read_text(ROOT / item["path"])
    if item_type == "slice":
        return materialize_slice(item["doc"], item["anchor"])
    if item_type == "derived_view":
        return materialize_derived(item["doc"], item["view"], cache_root)
    raise ValueError(f"unsupported item type: {item_type}")


def render_packet_envelope(items: list[dict[str, str]], labels: list[str], fallback_points: list[str] | None) -> str:
    lines = ["# Dispatch Packet", ""]
    for index, (item, label) in enumerate(zip(items, labels, strict=True), start=1):
        lines.extend(
            [
                f"## Item {index}",
                f"type: {item['type']}",
                f"ref: {label}",
            ]
        )
        if item["type"] == "slice":
            lines.append("selector_mode: anchor")
        if item["type"] == "derived_view":
            lines.append("selector_mode: derived_view")
        lines.append("")
    if fallback_points:
        lines.extend(["## Fallback Policy", ""])
        for point in fallback_points:
            lines.append(f"- {point}")
        lines.append("")
    return "\n".join(lines)


def packet_stats(
    items: list[dict[str, str]],
    cache_root: pathlib.Path,
    fallback_points: list[str] | None = None,
) -> tuple[TextStats, list[str]]:
    combined: list[str] = []
    labels = []
    for item in items:
        labels.append(item_label(item))
    combined.append(render_packet_envelope(items, labels, fallback_points).strip())
    for item in items:
        combined.append(item_text(item, cache_root).strip())
    joined = "\n\n".join(part for part in combined if part)
    return stats_for_text(joined), labels


def pct_reduction(legacy: int, minimal: int) -> float:
    if legacy == 0:
        return 0.0
    return ((legacy - minimal) / legacy) * 100


def render_stat_block(label: str, stat: TextStats) -> str:
    return (
        f"{label}: {stat.approx_tokens} tok approx | {stat.chars} chars | "
        f"{stat.lines} lines | {stat.words} words"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Approximate token benchmark for Forgeloop dispatch packets.")
    parser.add_argument("--fixtures", required=True)
    args = parser.parse_args()

    scenarios = json.loads((ROOT / args.fixtures).read_text())
    tmpdir = pathlib.Path(tempfile.mkdtemp(prefix="forgeloop-token-benchmark-"))
    hot_legacy = hot_minimal = cold_legacy = cold_minimal = 0
    task_hot_reductions: list[float] = []

    try:
        print("# Forgeloop Token Benchmark")
        print("")
        for scenario in scenarios:
            legacy_stat, legacy_labels = packet_stats(
                scenario["legacy_packet"],
                tmpdir,
                scenario.get("legacy_fallback_points"),
            )
            minimal_stat, minimal_labels = packet_stats(
                scenario["minimal_packet"],
                tmpdir,
                scenario.get("minimal_fallback_points", scenario.get("fallback_points")),
            )
            reduction = pct_reduction(legacy_stat.approx_tokens, minimal_stat.approx_tokens)
            bucket = scenario["bucket"]

            if bucket == "hot_path":
                hot_legacy += legacy_stat.approx_tokens
                hot_minimal += minimal_stat.approx_tokens
            else:
                cold_legacy += legacy_stat.approx_tokens
                cold_minimal += minimal_stat.approx_tokens
            if scenario.get("task_hot_path"):
                task_hot_reductions.append(reduction)

            print(f"## {scenario['name']}")
            print("")
            print(f"- Bucket: `{bucket}`")
            print(f"- Description: {scenario['description']}")
            print(f"- {render_stat_block('Legacy packet', legacy_stat)}")
            print(f"- {render_stat_block('Minimal packet', minimal_stat)}")
            print(f"- Reduction: {reduction:.1f}%")
            print(f"- Legacy docs read set: {', '.join(legacy_labels)}")
            print(f"- Minimal docs read set: {', '.join(minimal_labels)}")
            if scenario.get("fallback_points"):
                print(f"- Explicit fallback points: {', '.join(scenario['fallback_points'])}")
            print("")

        hot_reduction = pct_reduction(hot_legacy, hot_minimal)
        cold_reduction = pct_reduction(cold_legacy, cold_minimal)
        total_reduction = pct_reduction(hot_legacy + cold_legacy, hot_minimal + cold_minimal)
        task_hot_average = sum(task_hot_reductions) / len(task_hot_reductions) if task_hot_reductions else 0.0

        print("## Aggregate")
        print("")
        print(
            f"- Hot path reduction: {hot_reduction:.1f}% "
            f"({hot_legacy} -> {hot_minimal} tok approx)"
        )
        print(
            f"- Cold path reduction: {cold_reduction:.1f}% "
            f"({cold_legacy} -> {cold_minimal} tok approx)"
        )
        print(
            f"- Total reduction: {total_reduction:.1f}% "
            f"({hot_legacy + cold_legacy} -> {hot_minimal + cold_minimal} tok approx)"
        )
        print(f"- Task hot path average reduction: {task_hot_average:.1f}%")

        failures: list[str] = []
        if total_reduction < TOTAL_REDUCTION_FLOOR:
            failures.append(
                f"total reduction {total_reduction:.1f}% fell below the required {TOTAL_REDUCTION_FLOOR:.1f}% floor"
            )
        if task_hot_average < TASK_HOT_PATH_TARGET:
            failures.append(
                f"task hot path average reduction {task_hot_average:.1f}% fell below the {TASK_HOT_PATH_TARGET:.1f}% target"
            )
        if failures:
            print("")
            print("## Benchmark Gate Failure")
            print("")
            for failure in failures:
                print(f"- {failure}")
            return 1
    finally:
        shutil.rmtree(tmpdir)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
