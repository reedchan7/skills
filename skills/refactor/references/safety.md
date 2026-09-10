# Preserve behavior across structural change

Load for gaps in observation, stateful/async logic, public contracts, data
migration or affected critical paths. Apply only the relevant mechanisms.

## Behavior envelope

For each affected surface, identify consumers, preserved behavior, permitted
deltas, observation method and consequential unknowns. Classify it as a
documented contract, known implicit dependency, internal detail or unknown.
Do not silently promote every incidental detail to a public API, or dismiss
a real consumer merely because its dependency is undocumented.

Inspect return values and also effects, errors, order, state/identity, wire
and storage representations, configuration semantics and resource behavior.
Changing a private name is usually harmless; changing reflection/serialization
keys, exported names or template routes may not be.

## Establish observations before transformation

Run the affected existing checks on the actual starting content. Record
known failures with identity, symptom and relevance, rather than a failure
count. Missing dependencies and flaky checks remain visible. Use an isolated
baseline comparison when attribution is uncertain; avoid destructive checkout.

Add characterization tests only for a material gap. Exercise current behavior
through the nearest faithful seam, including relevant failures and effects.
An observation records what the program does, not whether that behavior is
desirable. Handle an authorized correction as a distinct behavior change.

Use differential tests for complex behavior where practical: identical inputs
and controlled dependencies through old/new implementations, then compare
outcomes, errors and effect traces. Snapshot normalization is an allowlist of
proven incidental nondeterminism, not a blanket scrub of IDs, timestamps or
paths. Retain relationships, ordering and domain fields; control clocks/random
sources when they affect semantics. Snapshots do not replace independent
expected invariants where both implementations could share a defect.

For difficult dependency seams, first make the smallest separately checked
change that allows observation (parameterization, wrapper or extraction).
Do not bootstrap a large rewrite under cover of making it testable.

## Transformation hazards

| Change | Observe before and after |
|---|---|
| Extract/inline/reorder expressions | Short-circuit/evaluation order, repeated reads, exception timing and side effects |
| Guard clauses or exception cleanup | All exits, finally/defer/destructor behavior and resource release |
| Move state or cache | Aliasing/identity, object lifetime, invalidation, key scope and mutability |
| Separate calculation from IO | Same effect count/order and transaction ownership; no duplicate work |
| Async or concurrency restructuring | Await/scheduling order, cancellation propagation, lock scope and races |
| Collection/stream transformation | Ordering, laziness, mutation during iteration, equality and memory usage |
| Type/value-object/enum change | Coercion, precision, overflow, null/missing distinctions and serialized values |
| Move/rename/remove symbols | Dynamic registration, exports, plugins, import-time hooks and generated consumers |

For a relevant concurrent invariant, enumerate a failing interleaving and
use controlled barriers/schedules where available; sleeps and a passing happy
path do not establish race freedom. Cancellation and retries must not create
an extra external effect. A pure helper does not make its orchestration atomic.

Use [security](security.md) for affected trust or sensitive-data boundaries.
Do not weaken checks or invent fallbacks to preserve a green test run.

## Mechanical tooling

Prefer repository-native/compiler-aware transforms, then existing codemods,
then suitable structural tools. Use text replacement only with a demonstrated
scope and residue check. For codemods inspect dry-run diff, affected paths,
second-run stability, missed references and a task-owned rollback path.
Tool success does not establish behavior preservation.

## API and data evolution

A pure internal refactor should not require new compatibility surfaces. If a
schema/API change is actually needed and authorized, treat it as a migration
with explicit permitted deltas and separate acceptance.

Inventory all consumers and overlapping deployed versions. Use an appropriate
expand → migrate → contract sequence, versioned adapter or branch-by-abstraction
when coexistence is required. Internal coordinated changes may not need a
public deprecation mechanism; external compatibility needs real evidence.

For database movement, specify authoritative reads/writes, transaction and
failure semantics, concurrent updates during backfill, resumable progress,
reconciliation and cutover criteria. Dual-write is not automatically safe:
define atomicity or recovery for either write failing. Bound locks and batch
load using the actual database/deployment constraints. Destructive contraction
requires explicit authorization, retention/backup treatment and evidence that
old readers/writers are retired, including scheduled and rollback versions.

## Performance and rollout

For an affected critical path compare the same workload, environment,
data scale and warm/cold state. Record repetitions/noise and the relevant
latency, allocations, queries, IO, bundle or CPU cost. Define a meaningful
regression boundary before optimization claims. Desktop measurements do not
establish mobile-device performance.

Shadow runs must suppress or isolate real external effects. Flags/canaries
need ownership, observation and removal criteria only when the deployment
actually needs them. Name rollout ordering, safe stopping points, recovery
and any irreversible step. A code revert cannot undo committed data or an
external side effect. Keep these actions within current authorization.
