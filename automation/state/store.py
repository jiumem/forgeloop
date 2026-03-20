"""store — task_state 文件级持久化。

v1 持久化策略：文件落盘优先。
每个 task_state 以 JSON 文件形式存储，路径为 {base_dir}/{task_id}.json。

设计依据：任务规划 §5.2 M1-3
"""

from __future__ import annotations

from pathlib import Path

from schemas.task_state import TaskState


class StateStoreError(Exception):
    """持久化层错误。"""


class FileStateStore:
    """基于文件系统的 task_state 存储。

    职责单一：读写 task_state JSON 文件。
    不做状态推进逻辑，那是 transitions 模块的事。
    """

    def __init__(self, base_dir: str | Path) -> None:
        self._base_dir = Path(base_dir)
        self._base_dir.mkdir(parents=True, exist_ok=True)

    @property
    def base_dir(self) -> Path:
        """存储根目录。"""
        return self._base_dir

    def _path_for(self, task_id: str) -> Path:
        """返回 task_id 对应的存储路径。"""
        # 防止路径穿越
        safe_name = task_id.replace("/", "_").replace("..", "_")
        return self._base_dir / f"{safe_name}.json"

    def save(self, state: TaskState) -> Path:
        """保存 task_state 到文件，返回文件路径。"""
        path = self._path_for(state.task_id)
        data = state.model_dump_json(indent=2)
        path.write_text(data, encoding="utf-8")
        return path

    def load(self, task_id: str) -> TaskState:
        """从文件加载 task_state。"""
        path = self._path_for(task_id)
        if not path.exists():
            raise StateStoreError(f"task_state 不存在: {task_id} (路径: {path})")
        try:
            raw = path.read_text(encoding="utf-8")
            return TaskState.model_validate_json(raw)
        except Exception as e:
            raise StateStoreError(f"task_state 解析失败: {task_id} - {e}") from e

    def exists(self, task_id: str) -> bool:
        """检查 task_state 是否存在。"""
        return self._path_for(task_id).exists()

    def delete(self, task_id: str) -> bool:
        """删除 task_state 文件，返回是否成功。"""
        path = self._path_for(task_id)
        if path.exists():
            path.unlink()
            return True
        return False

    def list_tasks(self) -> list[str]:
        """列出所有已存储的 task_id。"""
        return [p.stem for p in self._base_dir.glob("*.json")]
