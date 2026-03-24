---
name: r2-milestone-review
description: Run the formal Milestone Review (R2) against a Milestone PR boundary.
---

1. Run `scripts/prepare_bundle.py --initiative-doc <doc> --profile R2 --object-key <milestone>`.
2. If needed, spawn `architect`, `closer`, and `pragmatist`.
3. Finalize the review with `scripts/finalize_review.py`.
