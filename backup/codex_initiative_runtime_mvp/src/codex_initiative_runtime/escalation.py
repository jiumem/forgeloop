from __future__ import annotations

from pathlib import Path
from typing import Any

from .utils import read_json, write_json


def merge_panel_reports(output_path: str | Path, *inputs: str | Path) -> Path:
    merged = {
        "panel": [],
        "recommended_resolution": "",
        "blocking_reasons": [],
        "follow_ups": [],
    }
    for path in inputs:
        if not path:
            continue
        data = read_json(path)
        merged["panel"].append(data)
        merged["blocking_reasons"].extend(data.get("blocking_reasons", []) or [])
        merged["follow_ups"].extend(data.get("follow_ups", []) or [])
    if merged["blocking_reasons"]:
        merged["recommended_resolution"] = "ESCALATE_TO_HUMAN"
    else:
        merged["recommended_resolution"] = "PATCH_LOCAL"
    return write_json(output_path, merged)
