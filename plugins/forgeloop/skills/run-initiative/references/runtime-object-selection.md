# Runtime Object Selection Contract Reference

<!-- forgeloop:anchor document-role -->
## Document Role

- Plane: runtime dispatcher selection contract
- Applies to: `run-initiative` and `rebuild-runtime`
- Primary readers: runtime `Supervisor`
- Primary purpose: define the only legal runtime object selection and runtime-only rebinding law inside one sealed execution map

<!-- forgeloop:anchor control-law -->
## Control Law

- Selection operates only inside the sealed execution map defined by the current sealed planning artifacts, especially the sealed `Total Task Doc`.
- Selection never creates a new Initiative, Milestone, or Task.
- Selection never rewrites planning truth.
- Legal runtime object kinds are only `task`, `milestone`, and `initiative`.
- `frontier` is an ephemeral dispatcher computation only. It is never a legal persisted runtime object, plane, or `current_snapshot` value.
- Runtime may rebind from one current object to another object inside the same sealed execution map without returning to planning.
- Returning to planning is legal only when the sealed execution map itself is missing, contradictory, or no longer sufficient to decide the next executable object.

<!-- forgeloop:anchor required-output -->
## Required Output

Every legal selection result must bind exactly one next runtime object with:

- `object_kind`
- `object_key`
- `rolling_doc_ref`
- `reason`

Durable refs must remain repo-root-relative.

<!-- forgeloop:anchor selection-order -->
## Selection Order

Apply this order strictly:

1. **Same-object continuation**
   - If the current bound object still has an open same-object repair or review cycle, keep the same object.

2. **Explicit runtime rebind target**
   - If `last_transition` already records a legal runtime-only rebind target inside the same sealed execution map, and it is still valid, bind that target.

3. **Nearest sufficient parent object**
   - If the current object is no longer the correct execution focus, but the sealed execution map proves that a parent object now owns the next acceptance or integration frontier, bind the nearest sufficient parent object.
   - Nearest sufficient parent means: prefer `milestone` over `initiative` when `milestone` is enough.

4. **Next ready child object**
   - If no same-object continuation or parent rebind is needed, bind the next ready `task` according to the sealed dependency truth.

5. **Initiative delivery**
   - If no runnable object remains and Initiative acceptance is satisfied, the runtime may stop at `initiative_delivered`.

<!-- forgeloop:anchor red-lines -->
## Red Lines

Never:

- persist `frontier` into `Global State Doc`
- invent a new object outside the sealed execution map
- return to planning only because the current object is no longer the best execution focus
- encode closure-first wrapper hierarchy anywhere else once this contract exists
- let PR order replace object selection truth
