import unittest
from pathlib import Path

from codex_initiative_runtime.initiative_runtime import rebuild_state
from codex_initiative_runtime.scheduler import select_frontier, select_ready_tasks
from codex_initiative_runtime.planning_parser import parse_initiative_doc


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "initiatives" / "INIT-001.md"


class StateTests(unittest.TestCase):
    def test_rebuild_state_marks_first_task_ready(self):
        state = rebuild_state(DOC, REPO_ROOT)
        self.assertEqual(state.task_states["T001"].state.value, "READY")
        self.assertEqual(state.task_states["T002"].state.value, "NOT_READY")

    def test_scheduler_selects_frontier_and_ready_tasks(self):
        plan = parse_initiative_doc(DOC)
        state = rebuild_state(DOC, REPO_ROOT)
        frontier = select_frontier(plan, state)
        selection = select_ready_tasks(plan, state, frontier)
        self.assertEqual(frontier, "M1")
        self.assertEqual(selection.write_tasks, ["T001"])


if __name__ == "__main__":
    unittest.main()
