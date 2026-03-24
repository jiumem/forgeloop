---
name: escalation-panel
description: Merge architect/closer/pragmatist outputs into a single escalation summary.
---

1. Spawn `architect`, `closer`, and `pragmatist`.
2. Save each JSON output.
3. Run `scripts/merge_reports.py --initiative-doc <doc> --object-key <object> --inputs <json> <json> <json>`.
