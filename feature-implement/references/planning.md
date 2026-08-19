# Planning: baseline, bounded blast radius, slices, resume identity

Load for Phases 1–2. PLAN is a revision-pinned execution state, not a second
SPEC. Standard checkboxes plus immutable checkpoints survive context loss.

## Conventions inventory

Record evidence for:

- Repo-native affected/full test, lint, typecheck, build, run, and CI commands.
- Feature/test placement and naming (2–3 observed examples).
- Error/logging/config/dependency/fixture idioms.
- Ownership/instruction files governing every planned path.

New code follows observed conventions unless SPEC/PLAN records why not.

## Baseline protocol

### Existing repository

Before feature edits:

1. Freeze HEAD, complete status inventory, and unrelated dirty-file hashes.
2. Run affected tests/checks for the blast radius.
3. Run the full suite when locally feasible. Otherwise record the exact
   remote-CI/final gate, runtime reason, and coverage blind spot — never call
   the baseline “clean”.
4. For each failure record command, exit code, failing test, and normalized
   fingerprint (exception/error type + stable message/stack anchor).

Later “no unexpected delta” compares fingerprints, not test names. A known-red
test that fails differently is a new red. No known-red result can prove an
AC/RC/NFR.

### Greenfield bootstrap

Use this slice only when pickup has no product code and no invocable test
command. An existing module with zero tests is not greenfield: its first
test is the product slice.

Phase 1 records the empty-tree hash and toolchain decision. The first PLAN
slice then establishes a runner — titled Bootstrap — and covers no product
AC/RC/NFR:

- one smoke proving the chosen runner can go red and green
- a dependency manifest only when the repo will declare dependencies
- lint/type/build entry points when applicable

Create those files in that slice. No product behavior enters it. Plan
production slices after it.

## Bounded blast-radius and coverage ledger

Trace credible causal paths from touched interfaces/state/data/config to
consumer classes and operational surfaces. Map each material path to RC/NFR,
an existing central suite, or `not-assessed` with reason.

Do not enumerate everything behind a shared database/auth layer/event bus.
Sample only after establishing equivalence across a consumer class. RC may be
retired when recon disproves impact — through SPEC amendment, never by silent
deletion.

Coverage states:

- `covered` — named check/probe and owner.
- `no material risk` — causal-path reason.
- `not assessed` — blind spot, impact, and what would settle it.

## Slice rules

- **Tracer bullet:** narrow complete behavior through every required layer;
  independently demonstrable; affected checks green at its end.
- **Reliability-sized:** one requirement cluster and one checkpoint; split at
  independent review decisions, not arbitrary file counts.
- **Risk/dependency ordered:** risky unknowns first; blockers explicit.
- **Interface-complete:** exact names/signatures produced and consumed.
- **Wide mechanical change:** expand → migrate batches → contract; contract
  waits for consumer/telemetry evidence.
- **Release boundary:** a slice whose prerequisite is a deployment, completed
  backfill, telemetry window, or external consumer cutover belongs to a
  separate dependent SPEC/PLAN. Never place multiple release stages behind one
  local “all slices complete” gate.

Each slice names:

Goal · active AC/RC/NFR IDs · blockers · exact create/modify/test paths ·
interfaces · ordered oracle cases · approved test migrations · affected
commands + expected results · manual probes · rollback · checkpoint method.

## Checkpoints and resume

Every completed slice stores:

- Commit/tree SHA when commit authority exists; otherwise sorted file list +
  SHA-256 per file and full status inventory.
- SPEC version/digest.
- Commands, exit codes, and evidence timestamps.
- Deviation/amendment IDs.

Resume recomputes SHA-256 (or commit/tree SHA) for every checkpointed path
before any product edit. Write claimed vs actual in PLAN. A checked box
whose bytes do not match is incomplete: uncheck it, invalidate downstream
gates, and record a Deviation row. Never treat a placeholder or all-zero
digest as a real checkpoint. Rerun only what the dependency graph marks
affected.

## Coverage matrix

Two-way closure:

- Every active AC, RC, and NFR maps to ≥1 slice and final evidence method.
- Every non-bootstrap slice maps to ≥1 active requirement.
- Every planned test migration maps to an active approved requirement that
  explicitly supersedes the old assertion; only absent authority requires an
  amendment.

## Plan self-review and gate

Run the deterministic validator, then inspect:

1. No placeholders or invented commands/paths.
2. Interfaces agree across slices.
3. Global constraints copied verbatim from SPEC.
4. Compatibility/release ordering is safe.
5. Coverage ledger and matrix close.
6. Checkpoints are possible under recorded authority.

Express inherits the SPEC approval when plan scope/risk/files stay within it;
record `gate: inherited`. Empty Express ledger rows are one `none` / `N/A`.
Any expansion triggers a user gate. Standard/Deep present: scope, non-goals,
files, risks, compatibility, rollout, and rollback.
