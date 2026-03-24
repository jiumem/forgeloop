---
name: cut-anchor
description: Draft or execute a formal anchor/fixup/revert commit for a single Task.
---

1. Ensure the Task state is READY_FOR_ANCHOR.
2. Run `scripts/cut_anchor.py --initiative-doc <doc> --task-key <task>`.
3. By default, create a structured commit message draft.
4. Execute the commit only when approvals and user policy permit.
