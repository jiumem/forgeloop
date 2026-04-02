---
name: initiative-loop
description: Use when the `Global State Doc` has uniquely confirmed that current progress is at a ready or active Initiative; this skill uses single coder ownership to drive the current Initiative through formal `review/repair -> G3 -> fresh R3` closure
---

# Initiative Loop

<!-- forgeloop:anchor role -->
`initiative-loop` runs one confirmed Initiative only.

You act as the Initiative `Supervisor`: keep the minimum control plane, preserve one logical `coder_slot`, dispatch the `coder` and a fresh `initiative_reviewer`, and route only from `G3`, `R3`, and any active repair-Task callback.

`coder_slot` is the logical owner identifier, not the physical `agent_id`; the current `agent_id` may change, but `coder_slot` does not.

You are not responsible for writing code, writing `r3_result`, directly repairing Task code, rewriting any higher-level dispatch, performing governance actions outside finishing the development branch, or maintaining any parallel state.

<!-- forgeloop:anchor initiative-local-vocabulary -->
## Initiative-Local Vocabulary

- `g3_result.next_action` must be one of: `continue_initiative_repair`, `objectize_task_repair`, `enter_r3`, `wait_for_user`, `stop_on_blocker`
- `r3_result.next_action` must be one of: `continue_initiative_repair`, `objectize_task_repair`, `mark_initiative_delivered`, `wait_for_user`, `stop_on_blocker`

`mark_initiative_delivered` is reviewer output. `initiative_delivered` is the dispatcher-written stop state in the `Global State Doc`.

<!-- forgeloop:anchor canonical-runtime-contract-refs -->
## Canonical Runtime Contract Refs

- shared `Global State Doc` contract -> `../run-initiative/references/global-state.md`
- `Initiative Review Rolling Doc` contract -> `../run-initiative/references/initiative-review-rolling-doc.md`
- runtime cutover contract -> `../run-initiative/references/runtime-cutover.md`
- shared anchor-addressing contract -> `../references/anchor-addressing.md`
- shared derived-view contract -> `../references/derived-views.md`

<!-- forgeloop:anchor truth-sources-boundaries -->
## Truth Sources And Hard Boundaries

The formal input surface contains only the Initiative static truth trio `design_ref`, `gap_analysis_ref`, and `total_task_doc_ref` (`gap_analysis_ref` may be `N/A` for some Initiative types), the `Global State Doc`, the current `Initiative Review Rolling Doc`, the Milestone review docs / supporting evidence included in the current Initiative delivery candidate, and the necessary release / rollout / deployment / flag / readiness / test facts.

Hard boundaries:
- `G3` may be run only by the coder in the current delivery round, and it must be written into the `Initiative Review Rolling Doc`
- `R3` may be run only by a fresh reviewer against the current formal Initiative object
- `round` is Initiative round and owned by the `Supervisor` through the `Global State Doc`; coder and reviewer echo it in the rolling doc but do not advance it themselves
- the current Initiative round closes only when `r3_result` is written; if the coder still needs repair inside the current Initiative during `G3`, it stays in the same round
- a new round opens only on first entry into the Initiative, after `r3_result.next_action=continue_initiative_repair`, or when callback semantics from an objectized repair task explicitly say the Initiative should enter the next round
- the `Initiative Review Rolling Doc` is the only formal document for `G3 / R3`; the `Global State Doc` may contain only `current_snapshot`, `next_action`, and `last_transition`
- when reading, writing, initializing, or repairing runtime state, the `Global State Doc` and the `Initiative Review Rolling Doc` must follow the canonical contract refs above; do not improvise block shape or `next_action` spelling from memory or older design examples
- Initiative dispatch default path is controlled only by the bound runtime cutover contract: `full_doc_default` may default to authoritative full documents, while `minimal_preferred` and `minimal_required` use authoritative refs plus doc-local selectors and only the minimal slices needed for the delivery candidate
- if `next_action` changes the active object or active plane, `current_snapshot` must be updated at the same time; only when still advancing within the same Initiative may you update only `next_action` and `last_transition`
- if `G3` or `R3` finds a code problem, the default is `continue_initiative_repair` with the same `coder_slot` in the same Initiative and rerun `G3`; only when the repair needs an independent Task contract, a clearly new object boundary, or obviously exceeds the current Initiative closure radius should it be objectized into a repair Task through the `Global State Doc` and fall back to `task-loop`
- if a repair task has already been objectized, after the repair completes it must return to the same `Initiative Review Rolling Doc` to append the next round
- the current Initiative review handoff is the latest `g3_result` in the current round whose `next_action=enter_r3`
- each Initiative handoff block must carry `handoff_id` and `review_target_ref`; `r3_result` is actionable only when its `round`, `handoff_id`, and `review_target_ref` match that current handoff exactly, and if multiple `r3_result` blocks match one current handoff, only the latest matching block is actionable
- if the rolling doc does not exist, initialize only the header, including object identity and `coder_slot`, plus `initiative_contract_snapshot`, according to the canonical `Initiative Review Rolling Doc` contract; after initialization, the rolling doc becomes the only collaboration surface, and on first entry write `coder_slot=coder` into the header and `current_snapshot`, then write `round=1` into the `Global State Doc` before dispatching the first coder round

<!-- forgeloop:anchor initiative.packet-shape -->
## Initiative Packet Shape

Initiative coder packets should carry only:

- current Initiative identity and continuity metadata
- authoritative refs
- current `round` and `coder_slot`
- the current `g3_result` handoff tuple when one already exists
- only the Milestone evidence selectors, release/readiness selectors, and residual-risk selectors needed for the current delivery candidate
- only the minimum inline slices already rebuilt from those refs

Initiative reviewer packets should carry only:

- the same authoritative refs
- current `round`, `handoff_id`, and `review_target_ref`
- only the Initiative delivery selectors and supporting Milestone evidence selectors needed for this review
- an optional `handoff-scoped` or `current-effective` derived view when it is still legal and rebuildable

Do not default to whole Milestone docs, unrelated Task histories, or obsolete delivery attempts.

<!-- forgeloop:anchor initiative.current-selection -->
## Initiative Current Selection

- the current Initiative handoff is always the latest `g3_result` in the current round whose `next_action=enter_r3`
- the current actionable Initiative review result is always the latest matching `r3_result` for that handoff
- stale or mismatched `r3_result` blocks remain history and must not drive routing

<!-- forgeloop:anchor initiative.warm-path-delta -->
## Initiative Warm-Path Delta

Same-thread warm-path delta is legal only for the same Initiative, same workspace, same logical `coder_slot`, and same Initiative `round`.

Return to a full packet immediately on Initiative change, round change, slot succession, handoff change, derived-view invalidation that requires promotion, selector legality failure, anchor conflict, or first reviewer entry into a handoff.

<!-- forgeloop:anchor initiative.cutover-mode-law -->
## Initiative Cutover Mode Law

Bind `../run-initiative/references/runtime-cutover.md` before deciding the Initiative default read path.

- `full_doc_default`
  - authoritative full-document Initiative packets remain the default runtime route
  - minimal packets may still be assembled for validation, benchmark, or explicit sidecar use
- `minimal_preferred`
  - minimal Initiative packets are the default
  - selector legality failure, stale derived views, rolling-doc initialization, or unresolved formal conflict may promote one read to full-document fallback
- `minimal_required`
  - minimal Initiative packets are required
  - ordinary legality failure should stop unless the cutover contract names a disaster-recovery exception

<!-- forgeloop:anchor workflow -->
## Workflow

1. Bind the current Initiative
- First bind `current_runtime_cutover_mode`.
- Follow the mode-selected read order defined by `../run-initiative/references/runtime-cutover.md`; use `../references/derived-views.md` only for legal hot-path helpers.
- This loop specifies only the Initiative-specific proofs that must still be established after that shared read path.
- Read the Initiative definition, relevant Milestone review docs / supporting evidence, and the minimum engineering facts only after that runtime read order still leaves delivery readiness, acceptance, or routing legality incomplete
- Confirm that the active initiative is unique, the workspace is executable, the rolling doc matches the active initiative, `coder_slot` is unique, and the Initiative `round` is unique when it already exists
- Confirm that the Initiative has entered the delivery-review window: required Milestones are already clean, and there is no higher-priority blocker
- If the `Global State Doc` conflicts with the rolling doc, hand control back to `rebuild-runtime`
- If the current Initiative cannot be confirmed uniquely, the contract is missing, the delivery-review window has not opened, or the facts show the system should wait for the user, stop
- If the rolling doc does not exist, initialize only the header, including object identity and `coder_slot`, plus `initiative_contract_snapshot`, according to the canonical `Initiative Review Rolling Doc` contract

2. Update the minimum control plane
- `current_snapshot` points to the active initiative, `coder_slot`, and the Initiative `round`
- `next_action.action = continue_initiative_repair`
- Record entering the current round, resuming the current round, or coder succession in `last_transition` when needed
- Do not write implementation details, review body text, or full test output into the `Global State Doc`

3. Dispatch the coder
- Continue reusing the same logical `coder_slot` for the current Initiative
- Reuse the current `agent_id` while the physical thread is alive; if it is lost, you may assign a successor `agent_id`, but you must reuse the original `coder_slot` and record the succession
- Default to `fork_context=false`
- The coder input only needs to locate the current formal input surface: current Initiative identity, authoritative refs, the current handoff identifiers, the selectors for the Initiative success criteria and included Milestone evidence, and any already materialized minimal slices
- The coder returns its result to the `Initiative Review Rolling Doc` according to the contract

4. Handle the coder result
- Decide only from the rolling doc and release / rollout / test facts, not from chat summaries
- Read the latest `g3_result.next_action` first
- If the latest `g3_result.next_action=continue_initiative_repair`: do not enter reviewer; let the same `coder_slot` continue Initiative repair inside the same round
- If the latest `g3_result.next_action=objectize_task_repair`: create a repair Task bound to the same `coder_slot` in the `Global State Doc`; `last_transition` must record that the repair Task came from the current Initiative, which `Initiative Review Rolling Doc` it must return to on completion, and whether the callback should continue the current round or enter the next round; then switch `current_snapshot` to that Task, set `next_action.action = continue_task_repair`, and hand control back upstream
- If the latest `g3_result.next_action=enter_r3`, and the current handoff is valid: set `next_action.action = enter_r3`
- If the latest `g3_result.next_action=wait_for_user`: write waiting into the `Global State Doc`, then stop
- If the latest `g3_result.next_action=stop_on_blocker`: write blocked into the `Global State Doc`, then stop
- Only if `next_action` is missing or still not explicit enough should you fall back to compatibility judgment from `verdict` plus surrounding formal facts

5. Dispatch a fresh `initiative_reviewer`
- Every `R3` round uses a freshly spawned reviewer, with `fork_context=false` by default
- The reviewer reads the same authoritative refs, the current handoff identifiers, the selectors for the Initiative success criteria and included Milestone evidence, and only the minimal slices needed for delivery-radius review unless fallback is triggered explicitly
- The reviewer returns its result to the `Initiative Review Rolling Doc` according to the contract

6. Handle `r3_result`
- The current actionable `r3_result` is the latest matching review result for the current handoff
- If the current actionable `r3_result` has `verdict=clean` and `next_action=mark_initiative_delivered`: update `last_transition`, move `current_snapshot` forward into the delivered Initiative stop snapshot, set `next_action.action = initiative_delivered`, and hand control back upstream
- If the current actionable `r3_result` has `verdict=changes_requested` and `next_action=continue_initiative_repair`: increment the Initiative `round` in the `Global State Doc`, set `next_action.action = continue_initiative_repair`, and let the same `coder_slot` enter the next round
- If the current actionable `r3_result` has `verdict=changes_requested` and `next_action=objectize_task_repair`: create a repair Task bound to the same `coder_slot` only through the `Global State Doc`; `last_transition` must record that the repair Task came from the current Initiative, which `Initiative Review Rolling Doc` it must return to on completion, and that the callback should enter the next round; then switch `current_snapshot` to that Task, set `next_action.action = continue_task_repair`, and hand control back upstream
- If the current actionable `r3_result` has `verdict=changes_requested` and `next_action=wait_for_user`: the reviewer writes only the recommendation, the `Supervisor` writes waiting into the `Global State Doc`, then hands control back upstream
- If the current actionable `r3_result` has `verdict=changes_requested` and `next_action=stop_on_blocker`: the reviewer writes only the recommendation, the `Supervisor` writes blocked into the `Global State Doc`, then hands control back upstream
- If the rolling doc does not expose one unique actionable `r3_result`, or if `verdict` and `next_action` do not form one legal combination above, stop and surface the illegal Initiative review output explicitly

<!-- forgeloop:anchor stop-conditions -->
## Stop Conditions

Stop immediately and hand control back upstream or to the user when:
- the active initiative cannot be confirmed uniquely
- the Initiative contract is missing, the Milestone candidate set is missing, or the `Global State Doc` conflicts with the rolling doc
- the Initiative has not entered the delivery-review window yet
- the workspace is not an executable implementation environment, or current facts show the system should wait for the user
- the coder or reviewer exposes a real blocker

<!-- forgeloop:anchor red-lines -->
## Red Lines

Never:
- enter `R3` without a valid `g3_result`
- silently replace the logical `coder_slot`
- keep a temporary bootstrap note, temporary commentary, or chat summary as a second collaboration truth source
- write coder / reviewer body content into the `Global State Doc`
- dispatch multiple coders concurrently for the same Initiative
- let the reviewer repair code
- skip `G3 -> R3`
- forcibly split repair into a repair task when it can still close within the current Initiative
- force repair to stay in the Initiative layer when it should be objectized into a repair task
- claim delivery completion while the Initiative still has an active repair task
- claim the Initiative is clean without `r3_result: clean`

<!-- forgeloop:anchor completion-criteria -->
## Completion Criteria

On correct completion, all of the following should be true:
- the current Initiative state can be recovered uniquely from the `Global State Doc` and the `Initiative Review Rolling Doc`
- `coder_slot` continuity is unambiguous
- if the Initiative is clean, the rolling doc already contains a valid `g3_result` and `r3_result`
- if the Initiative is not yet clean, the system is either clearly stopped in current Initiative repair, or has objectized a clear repair task and fallen back to the Task layer when needed
- no second runtime truth source has been created outside the four formal runtime surfaces
