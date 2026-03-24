"""一次性脚本：从 Python 样例实例重新生成 JSON fixture 文件。"""

from pathlib import Path

from pydantic import BaseModel

from mock.sample_coder_results import CLEAN_CODER, FAILED_CHECKS_CODER, PARTIAL_CODER
from mock.sample_review_results import (
    BLOCKING_FINDING_REVIEW,
    CLEAN_REVIEW,
    FAILED_CHECKS_REVIEW,
    LOOP_LIMIT_REVIEW,
    NEEDS_HUMAN_RULING_REVIEW,
)
from mock.sample_task_packets import FULL_PACKET, MINIMAL_PACKET, SCENARIO_PACKET

fixtures = Path(__file__).resolve().parent / "fixtures"

_ITEMS: list[tuple[str, BaseModel]] = [
    # task packets
    ("minimal_task_packet", MINIMAL_PACKET),
    ("scenario_task_packet", SCENARIO_PACKET),
    ("full_task_packet", FULL_PACKET),
    # coder results
    ("clean_coder_result", CLEAN_CODER),
    ("partial_coder_result", PARTIAL_CODER),
    ("failed_checks_coder_result", FAILED_CHECKS_CODER),
    # review results
    ("clean_review_result", CLEAN_REVIEW),
    ("blocking_finding_review_result", BLOCKING_FINDING_REVIEW),
    ("failed_checks_review_result", FAILED_CHECKS_REVIEW),
    ("needs_human_ruling_review_result", NEEDS_HUMAN_RULING_REVIEW),
    ("loop_limit_review_result", LOOP_LIMIT_REVIEW),
]

for name, obj in _ITEMS:
    json_text = obj.model_dump_json(indent=2)
    (fixtures / f"{name}.json").write_text(json_text, encoding="utf-8")

print(f"Done: {len(_ITEMS)} fixtures written to {fixtures}")
