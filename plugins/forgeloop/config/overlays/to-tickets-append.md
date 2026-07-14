## Forgeloop Cumulative Audit Declaration

Keep three approved facts independent:

- Branch topology: `INDEPENDENT | SHARED`.
- Shared-branch reason: `WIDE_REFACTOR | NON_GREEN_MIGRATION | ATOMIC_DELIVERY | CUMULATIVE_AUDIT`.
- Integration policy: `auto-merge | human-merge`.

`CUMULATIVE_AUDIT` extends only the legal reasons for `SHARED`; it does not grant merge authority or change the existing reasons. Offer it only for a Spec with a native PR/MR runtime and at least two implementation Tickets. A single-Ticket Spec remains `INDEPENDENT`. Local runtime must not offer `CUMULATIVE_AUDIT`, while its other approved shared-branch reasons remain available.

When eligible, propose this declaration with the complete Ticket and dependency drafts:

```text
Branch topology: SHARED
Shared-branch reason: CUMULATIVE_AUDIT
Integration branch: <derived Spec branch>
Target: <declared target>
Final integration owner: <integrate-and-verify Ticket>
Final delivery surface: one cumulative PR/MR to <target>
```

Publish nothing until the user explicitly approves this declaration, every Ticket body, and all blocking edges together. Rejection keeps `INDEPENDENT`; `$run-initiative` must never switch modes later.

A cumulative draft has exactly one `integrate-and-verify` Ticket, blocked by every delivery Ticket. Ordinary Tickets remain independently verifiable vertical slices and keep only real dependencies; do not turn them into Stacked PRs. The final Ticket must declare its final integration Scope, public validation Seam, failure semantics, and Acceptance criteria before publication. It re-executes or verifies each existing owner-referenced Proof on the final Head but does not gain Cross-seam Invariant ownership.

Because cumulative delivery depends on cross-stage identity, provenance, and evidence, the final `integrate-and-verify` Ticket must be `HIGH_RISK` and receive the normal bound Adversarial Design Review with the complete draft set. Do not publish it or any ordinary Ticket until that Review returns `PASS`.

## Forgeloop Acceptance Repair Mode

Enter this mode only when the user explicitly invokes `$to-tickets` for a formal `ACCEPTANCE_RESULT` with `REPAIR_REQUIRED` and one stable `repair_key` per Finding. Read the parent Spec or Initiative, the Acceptance Findings, the final Commit, existing Open Tickets, and every Ticket already carrying any of those keys.

- Keep the approved parent contract and completed Ticket history unchanged. If the Findings require changing Scope, `Delivery Acceptance`, Ticket Acceptance criteria, the Spec, an ADR, or confirmed Initiative membership, stop with `CONTRACT_BLOCKER` instead of drafting repair Tickets.
- For Spec Acceptance, use that Spec as `owning_spec_ref`. For Initiative Acceptance, route each repair slice to an existing member Spec whose approved Scope covers it; use coordinated Tickets under multiple member Specs when necessary. Never create a repair Ticket directly under the Initiative. If no existing member Spec can own a Finding without contract change, return `CONTRACT_BLOCKER`.
- Query every key before drafting. Reuse the unique valid Open repair Ticket carrying each key; stop when one key has ambiguous or conflicting matches. Multiple keys may point to the same Ticket only when its body lists every key and the Findings form one atomic vertical slice. Do not recreate represented work.
- For unmatched keys, draft only the smallest vertical Ticket or Tickets needed to satisfy their named Acceptance Findings. Do not decompose the whole Spec again. Preserve the normal user quiz and approval before publication.
- Put `owning_spec_ref`, the Initiative reference when applicable, Acceptance level, assigned `repair_key` values, final Commit, stable `finding_id` values, observable repair checks, and any genuine blockers in every repair Ticket. Keep each Ticket inside the existing approved Scope and sized for one fresh context.
- Publish idempotently. If a write result is ambiguous, query by every assigned `repair_key` and verify the body and parent relationship before retrying. Never create a second Ticket merely because the first response was uncertain.

This mode creates or reuses formal repair Tickets only after the user's explicit invocation. It does not resume `$run-initiative`; the user resumes the original Run separately after the Tracker work is valid.

## Forgeloop Spec Revision Reconciliation Mode

Enter this mode only when the user explicitly invokes `$to-tickets` for a formal Spec with a material new Revision and a paused Run. Read the previous and current Spec Revisions plus every existing child Ticket, including body, comments, status, parent, and blockers.

- Preserve every Completed or Closed Ticket and its history unchanged.
- Compare the revised contract only with Open Tickets. Present the smallest proposed set of `retain`, `update`, `supersede`, and `create` actions, including dependency changes, and obtain normal user approval before writing.
- Reuse an Open Ticket when its delivery goal remains valid. Update only the approved contract fields and blockers. Create only missing vertical slices. Do not delete obsolete Open Tickets; mark them superseded and close them only after explicit approval.
- Before every write, refresh the current Ticket and search for an already-applied equivalent action. If a write result is ambiguous, query and verify before retrying.
- Stop with `CONTRACT_BLOCKER` when reconciliation requires a different core Problem, Actor, delivery target, expanded Scope, Spec rewrite, ADR change, or Initiative membership change.

Do not modify the Spec, parent Initiative, Completed Tickets, Run Claim, or Run checkpoints. This mode reconciles Tracker Tickets only; it does not resume `$run-initiative`.
