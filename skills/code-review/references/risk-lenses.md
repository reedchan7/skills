# Risk lenses

Each item is a triple: the **signal** worth chasing, the condition under which it
is **not a finding**, and the **check** that settles which one it is. A signal
whose suppressor you did not test is not a finding yet.

Load only the sections for lenses opened in SKILL.md §4.

| Lens (§4) | Section |
|---|---|
| 2 Correctness and state | State, concurrency, and distributed work |
| 3 Security and privacy | Trust boundaries and security |
| 4 Compatibility and integration | APIs, configuration, and integrations |
| 5 Data and migrations | Data, schema, and migrations |
| 6 Performance and capacity | Performance and capacity |
| 7 Tests | Tests |
| 8 Ownership and complexity | Ownership and complexity |
| changed UI surface | User interfaces and client state |
| removed guard, unclear invariant | History and prior guidance |
| version-specific claim | Language and framework details |

## State, concurrency, and distributed work

- Side effect moved before the record that suppresses it, or an acknowledgement
  moved before the durable write. Not a finding if the effect is idempotent at the
  receiver, or the mover added a compensating path. Check: follow the error and
  crash edge out of the new order; ask what a retry sees.
- Read-modify-write on shared state without a lock, transaction, or atomic
  operation. Not a finding if the state is per-request, per-thread, or immutable,
  or the store enforces the invariant with a constraint. Check: find a second
  writer and name it; no second writer, no race.
- Unlocked fast path added in front of a synchronized one. Not a finding if the
  value is immutable after publication and the container is never mutated in
  place. Check: find whether any writer mutates the same container rather than
  replacing it.
- Idempotency key derived per attempt rather than per request, or scoped without
  the tenant dimension. Not a finding if the receiver deduplicates on a different
  stable field. Check: read what the external call actually keys on.
- Unit of atomicity spanning a database write, a queue publish, a cache update,
  and an external call. Not a finding if a transactional outbox, or a documented
  reconciliation path, covers the gap. Check: pick the worst interleaving and
  state what is left inconsistent.
- Resource acquired without a deferred or scoped release, or released only on the
  success path. Not a finding if the framework owns the lifecycle or the scope
  exits immediately. Check: follow every early return and error branch out of the
  acquiring function.
- Lease, timeout, or retry budget changed. Not a finding if the consumer tolerates
  redelivery. Check: trace timeout-then-late-success and duplicate delivery.

## Trust boundaries and security

- Identity taken from a client-controlled field — body, header, query, path — and
  used for a permission decision. Not a finding if the framework already
  authenticated and bound it, or the value is re-checked against the session.
  Check: read the value's origin, never its name.
- Authorization checked on the operation but not on the object, or an object
  lookup that dropped its tenant/owner predicate. Not a finding if a lower layer
  enforces scoping, or the identifier is unguessable *and* the resource is public
  by design. Check: read the query that fetches the object.
- Untrusted value reaching a command, query, template, path join, redirect, or
  deserializer. Not a finding if it is a trusted constant, parameterized, or
  canonicalized and validated upstream. Check: read the sanitizer that is claimed
  to run, and confirm it runs on this path.
- Validation moved after a side effect, removed on one sibling path, or bypassable
  through an alternate encoding. Not a finding if the type system or the schema
  layer makes the invalid value unrepresentable. Check: enumerate every entry
  point that reaches the changed function.
- Secret, token, or personal data reaching a log, error body, URL, or cache key.
  Not a finding if the value is already redacted or is a public identifier. Check:
  read what the sink does with it.
- Failure path that grants instead of denying. Not a finding if the caller treats
  the error as denial. Check: read the caller's handling of the error return.

## APIs, configuration, and integrations

- Removed, renamed, or retyped field, or stricter parsing, on a surface a consumer
  reads. Not a finding if every consumer is in this repository and updated in the
  same change. Check: search for consumers, and say which discovery methods could
  not see one.
- New optional parameter with no default on the read path, so existing callers get
  behavior they did not have. Not a finding if the absent value is handled
  explicitly. Check: trace the request that omits it.
- Default value, config precedence, CLI flag, or environment variable changed. Not
  a finding if the old value is preserved for existing deployments. Check: read
  what an unset key resolves to now versus before.
- Behavior that differs between old and new code during a rolling deploy. Not a
  finding if the change is deployed atomically or the format is versioned. Check:
  evaluate old-reader/new-writer and new-reader/old-writer separately.
- Dependency version moved. Not a finding if the changelog shows no behavioral
  change on the paths used. Check: read the lockfile delta and the relevant
  release notes; runtime behavior, not just compilation.
- Feature flag added or removed. Not a finding if both flag states are correct at
  every version present during rollout. Check: enumerate the state matrix.

## Data, schema, and migrations

- Constraint, index, or type changed alongside application code. Not a finding if
  expand, migrate, and contract are separate deployable steps. Check: ask what the
  currently-deployed application does against the new schema, and vice versa.
- Backfill that maps values without a total mapping — a `CASE` without `ELSE`, a
  lookup without a default. Not a finding if the source domain is closed and every
  member is mapped. Check: ask which writers can produce a value outside the
  mapping while the migration runs.
- `NULL` compared with `=` or `!=`, or a partial index predicate using `= NULL`.
  Not a finding when the column is non-nullable. Check: read the column
  definition, not the surrounding intent.
- Destructive step — drop column, drop index, delete rows. Not a finding if every
  reader is provably gone and the spec authorizes it. Check: name the release that
  removed the last reader and confirm it is fully deployed.
- Long-running or locking DDL on a live table. Not a finding if the table is small
  or writes are paused for the window. Check: read the stated table size and
  maintenance window before recommending a concurrent variant.
- Partial backfill with no restart path, or failed rows swallowed. Not a finding if
  the operation is idempotent and re-runnable. Check: ask what happens when it dies
  at 50%.
- Query-plan or cardinality claim. Not a finding without an execution plan or
  stated data volume. Check: get the plan, or drop the claim.

## Performance and capacity

- Query, network call, or expensive parse moved inside a loop, or a batch call
  replaced by a per-item one. Not a finding if the collection is bounded small or
  the layer caches. Check: name the realistic item count from the code or the
  stated context.
- Unbounded growth — input size, pagination, queue depth, recursion, retained
  listeners, file descriptors, response size. Not a finding if an upstream limit
  caps it. Check: find the cap and quote it.
- Blocking or CPU-heavy work on an event loop, or a lock held across I/O. Not a
  finding if the path is off the request path. Check: identify the caller and
  whether it is latency-sensitive.
- Any micro-optimization without a hot path. Not a finding, period. Check: if you
  cannot name the hot path and the scale, say nothing.

## Tests

- Changed behavior with no assertion that would fail if it regressed. Not a
  finding if an existing test already covers the decisive value. Check: mentally
  revert the change and name the test that goes red.
- Assertion weakened — an exact value replaced by a called-check, a decisive
  assertion deleted. Not a finding if the value is asserted elsewhere. Check: read
  the whole test file, not the diff hunk.
- Test that only proves mocks were called, duplicates the implementation, depends
  on ordering, or swallows errors. Not a finding if it guards a contract the real
  boundary cannot be exercised for. Check: ask what production bug this test would
  have caught.
- Missing negative case for permissions, boundaries, partial failure, retry,
  concurrency, or migration — when that risk changed in this diff. Not a finding
  when the risk is unchanged. Check: confirm the diff introduced the risk.

## Ownership and complexity

- Feature logic placed in a shared module, or a near-duplicate helper added beside
  a canonical one. Not a finding unless it creates a concrete inconsistency or a
  second source of truth. Check: find the canonical owner and show the two now
  disagree.
- Hand-rolled implementation of something the standard library, platform, or an
  installed dependency already provides. Not a finding if the existing option
  lacks a required property. Check: name the existing API and why it was rejected.
- Speculative parameter, one-implementation abstraction, pass-through layer, or a
  branch the task does not require. Not a finding if a caller in this change needs
  it. Check: count the real call sites.
- Removal that shortens code while dropping a boundary check, type safety, or
  error isolation. Always a finding; brevity is not a justification. Check: the
  behavior envelope, not the line count.

## User interfaces and client state

- Reachable state with no rendering — loading, empty, partial, error, offline,
  permission-denied. Not a finding if the state cannot occur on this path. Check:
  find the code path that produces it.
- Rapid repeated action, navigation during async work, or a stale response
  applied. Not a finding if the request is keyed or cancelled. Check: read the
  effect's cleanup and the response's identity check.
- Client-side permission or validation with no server enforcement. Always a
  finding. Check: read the server handler.
- Keyboard access, focus, labels, semantic role, or contrast changed. Not a
  finding if the control's semantics are unchanged. Check: read the rendered
  element, not the styling.

## History and prior guidance

- Guard, retry, lock, transaction, validation, or error branch removed. Not a
  finding if the reason it existed is provably gone. Check:
  `git log -S '<removed token>'` and `git log -L` on the region; read the
  introducing commit message before accepting the removal.
- The same defect appearing again after an earlier fix. Not a finding if the
  earlier fix addressed a different path and this one is genuinely new. Check:
  search closed issues, fix commits, and regression tests naming the changed
  symbol, then compare the triggering path.
- Change contradicting a comment, docstring, or accepted review note on a prior
  PR touching these files. Not a finding if the guidance is stale — then the stale
  guidance is the finding. Check: `gh pr list --state merged --search <path>`.
- "This was always broken" versus "this change broke it". Only the second is
  reportable. Check: run the trace against the base revision.

## Language and framework details

Prefer the repository's pinned versions, compiler/runtime behavior, official
documentation, and existing idioms. Do not apply a memorized version-specific rule
until the toolchain and configuration confirm it. When a claim depends on a
version, quote where the version is pinned.
