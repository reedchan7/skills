# Executing an RT task

For an agent implementing a `docs/refactor/tasks/RT-*.md` file.

The protocol embedded in the RT file (`rt-protocol-vN`, section "Executor
protocol"; current version `rt-protocol-v1`) is CANONICAL. This file explains how to apply it and adds
context; it deliberately does not restate the numbered steps. On any
mismatch, the RT file's embedded version wins for that task.

## Inputs — refuse to start without them

Repository root · the approved RT file · expected base revision · authority
boundaries. Nothing else is required; nothing less is acceptable. If the RT
file is missing any of Authority, Freshness, Behavior envelope, Verify, or
Rollback, stop and report — never improvise a missing contract.

## Pickup sequence

1. Read the RT file fully before touching anything.
2. Run its freshness/divergence check (protocol step 1).
3. Confirm Prerequisites are done and Coordination entries acknowledged.
4. Establish the baseline (protocol step 2) — Verify commands BEFORE any
   edit, read against the task's ledger excerpt.
5. Only then edit, following the loop (protocol step 3).

## Choosing mechanisms

Steps in RT files are intent-level. Pick the mechanism per the ladder in
`references/safety.md` (IDE/compiler-native → existing codemods →
structural tools → text replacement last). Codemod steps carry their own
gates: dry-run diff, idempotence, changed-file count, residue search,
rollback path.

## Judgment calls the protocol leaves to you

- "Bounded" in protocol step 4 means: the failure is in code you just
  touched, the cause is visible in the diff, and the fix does not widen the
  step's scope. Anything else is not bounded — restore and split.
- "Purely mechanical drift" in step 1 means formatting, renames your tools
  can re-map, or moved files with unchanged behavior. When in doubt, it is
  not mechanical — mark STALE.

## Escalation — stop and report when

Any Stop condition in the task fires · an Assumption is invalidated · a
behavior-envelope violation is observed · a prerequisite is discovered
(propose it, set Status: blocked) · granted authority is insufficient for a
needed action. Roadmap changes belong to the planner: propose, never edit.

## Completion

All Acceptance boxes checked → fill the Handoff record → Status: done.
Report back: changed files, deviations, discovered work proposed, remaining
risk.
