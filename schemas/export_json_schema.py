"""导出四个核心模型的 JSON Schema 文件到 schemas/ 目录。"""

from __future__ import annotations

import json
from pathlib import Path

from schemas.coder_result import CoderResult
from schemas.review_result import ReviewResult
from schemas.task_packet import TaskPacket
from schemas.task_state import TaskState

SCHEMA_DIR = Path(__file__).resolve().parent.parent / "schemas"

MODELS = {
    "task_packet": TaskPacket,
    "coder_result": CoderResult,
    "review_result": ReviewResult,
    "task_state": TaskState,
}


def export_schemas() -> None:
    for name, model in MODELS.items():
        path = SCHEMA_DIR / f"{name}.schema.json"
        schema = model.model_json_schema()
        path.write_text(json.dumps(schema, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"exported: {path}")


if __name__ == "__main__":
    export_schemas()
