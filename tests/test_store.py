"""tests/test_store.py — P2 task_state 持久化测试。

覆盖：
- 保存和加载 round-trip
- 不存在的 task_id 加载应报错
- exists / delete / list_tasks 行为正确
"""

from __future__ import annotations

import pytest

from automation.state.store import FileStateStore, StateStoreError
from schemas.task_state import TaskState, TaskStatus


@pytest.fixture
def store(tmp_path: object) -> FileStateStore:
    """使用临时目录的 store。"""
    from pathlib import Path

    return FileStateStore(Path(str(tmp_path)) / "states")


class TestFileStateStore:
    """FileStateStore 测试。"""

    def test_save_and_load_roundtrip(self, store: FileStateStore) -> None:
        """保存后加载应完全一致。"""
        state = TaskState(task_id="test_roundtrip", current_status=TaskStatus.CODING, round_no=2)
        store.save(state)

        loaded = store.load("test_roundtrip")
        assert loaded.task_id == state.task_id
        assert loaded.current_status == TaskStatus.CODING
        assert loaded.round_no == 2

    def test_load_nonexistent_raises(self, store: FileStateStore) -> None:
        """加载不存在的 task_id 应报错。"""
        with pytest.raises(StateStoreError, match="不存在"):
            store.load("no_such_task")

    def test_exists(self, store: FileStateStore) -> None:
        assert not store.exists("test_exists")
        store.save(TaskState(task_id="test_exists"))
        assert store.exists("test_exists")

    def test_delete(self, store: FileStateStore) -> None:
        store.save(TaskState(task_id="test_delete"))
        assert store.exists("test_delete")
        assert store.delete("test_delete")
        assert not store.exists("test_delete")

    def test_delete_nonexistent_returns_false(self, store: FileStateStore) -> None:
        assert not store.delete("no_such_task")

    def test_list_tasks(self, store: FileStateStore) -> None:
        store.save(TaskState(task_id="task_a"))
        store.save(TaskState(task_id="task_b"))
        tasks = store.list_tasks()
        assert set(tasks) == {"task_a", "task_b"}

    def test_save_overwrites(self, store: FileStateStore) -> None:
        """重复保存应覆盖旧文件。"""
        state1 = TaskState(task_id="overwrite_test", round_no=1)
        store.save(state1)
        state2 = TaskState(task_id="overwrite_test", round_no=5)
        store.save(state2)
        loaded = store.load("overwrite_test")
        assert loaded.round_no == 5

    def test_path_traversal_protection(self, store: FileStateStore) -> None:
        """含 / 或 .. 的 task_id 不应穿越目录。"""
        state = TaskState(task_id="../escape_test")
        path = store.save(state)
        # 文件应在 base_dir 内，名称被清洗
        assert path.parent == store.base_dir
        assert ".." not in path.name
