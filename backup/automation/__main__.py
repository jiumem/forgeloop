"""python -m automation — forgeloop 最小运行入口。

当前仅提供 status / smoke 两个子命令，作为 P0 的"入口占坑"。
后续 P4（adapter 实现）和 P5（loop 集成）会扩展真实子命令。

用法::

    # 查看系统基本信息
    uv run python -m automation status

    # 用 mock 样例跑一次 smoke 检查（schema + 状态机创建）
    uv run python -m automation smoke
"""

from __future__ import annotations

import argparse
import sys
from datetime import UTC, datetime


def _cmd_status() -> None:
    """打印系统基本信息。"""
    from automation.controller.transitions import TRANSITION_RULES
    from schemas.task_state import TaskStatus

    cause_rules = [r for r in TRANSITION_RULES if r.cause is not None]
    helper_rules = [r for r in TRANSITION_RULES if r.cause is None]

    print("forgeloop status")
    print(f"  状态数: {len(TaskStatus)}")
    n_cause, n_helper = len(cause_rules), len(helper_rules)
    print(f"  跃迁规则: {len(TRANSITION_RULES)} 条（cause 驱动 {n_cause}, helper-only {n_helper}）")
    print(f"  时间: {datetime.now(UTC).isoformat()}")


def _cmd_smoke() -> None:
    """用 mock 样例执行最小 smoke 检查。"""
    from automation.controller.transitions import start_task
    from mock.sample_task_packets import FULL_PACKET, MINIMAL_PACKET
    from schemas.task_state import TaskState

    errors: list[str] = []

    for label, packet in [("minimal", MINIMAL_PACKET), ("full", FULL_PACKET)]:
        try:
            state = TaskState(task_id=packet.task_id)
            state = start_task(state)
            print(f"  [{label}] {packet.task_id}: NEW → {state.current_status.value} ✓")
        except Exception as e:
            errors.append(f"[{label}] {packet.task_id}: {e}")

    if errors:
        print("\nsmoke 失败:")
        for err in errors:
            print(f"  {err}")
        sys.exit(1)
    else:
        print("\nsmoke 通过")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="python -m automation",
        description="forgeloop — Codex 自动任务编码循环",
    )
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("status", help="打印系统基本信息")
    sub.add_parser("smoke", help="用 mock 样例跑 smoke 检查")

    args = parser.parse_args()
    if args.command == "status":
        _cmd_status()
    elif args.command == "smoke":
        _cmd_smoke()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
