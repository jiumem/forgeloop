---
name: r1-task-review
description: Run the formal Task Review (R1) against an anchored Task plus G1 evidence.
---

1. Run `scripts/prepare_bundle.py --initiative-doc <doc> --profile R1 --object-key <task>`.
2. Spawn `task_reviewer` and feed it the generated bundle.
3. Save the reviewer's JSON to a temporary file.
4. Run `scripts/finalize_review.py --initiative-doc <doc> --profile R1 --object-key <task> --raw-input <json> --verdict PASS|BLOCKED`.
