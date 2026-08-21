# RT task template (canonical)

Copy everything between the `TEMPLATE START/END` markers for each generated
task. The embedded executor protocol below is the canonical protocol text
(`rt-protocol-v1`); `references/execution.md` defers to it. On version
mismatch, the RT file's embedded version wins for that task.

<!-- TEMPLATE START -->

# RT-NNN — <title>

- Status: pending | in-progress | blocked | STALE | done
- Priority: P1 | P2 | P3 · Risk: low | medium | high · Blast radius: <modules/services affected>
- Owner: <planner/owner> · Created: <date> · Roadmap phase: <N>

## Authority

| Action | Granted |
|---|---|
| Edit files in scope | yes/no |
| Commit | yes/no (convention: `refactor(<scope>): <intent> (RT-NNN)`) |
| Create branch | yes/no (naming: <pattern>) |
| Update this task file | yes/no |
| Update roadmap | no — planner only |

## Freshness

- Base revision: <sha>
- Assessment: docs/refactor/REFACTOR-ASSESSMENT.md @ <sha or date>
- Protocol: rt-protocol-v1
- Affected symbols: <files/symbols this task's assumptions depend on>
- Assumptions: <bullets — anything that, if changed, invalidates this plan>

## Decision basis

- Findings: F-xxx, F-yyy
- Evidence summary: <observed facts + source@revision — self-contained; the
  executor must not need to open the assessment>
- Counterevidence: <or "none found">
- Confidence: high | medium | low

## Goal

<measurable, one sentence>

## Acceptance (task-local)

- [ ] <criterion observable within this task>
- [ ] Verify commands pass with no unexpected delta vs the baseline ledger
- [ ] No behavior-envelope violation observed

## Non-goals

<explicit exclusions — semantic scope, not just paths>

## Behavior envelope

- Preserved: <behavior + how observed>
- Permitted deltas: <explicit>
- Unknown exposure: <list + treatment decision>
- Consumers: <who observes this code>

## Scope

- Allowed: <files/symbols>
- Forbidden: <paths; all generated code is forbidden unless stated>

## Prerequisites

<RT-ids, environment, data, flags — or "none known">

## Coordination

<likely conflicts, owners to notify, parallel-safe with — or "none known">

## Steps

1. <intent + invariant + mechanism (named move optional metadata)>
2. <...>

## Verify

| Command | Expected |
|---|---|
| `<cmd>` | <result, read against the ledger excerpt below> |

Baseline ledger excerpt: <known-red/flaky entries relevant to these commands>

## Rollback

- Trigger: <what observation triggers rollback>
- Procedure: <exact steps>
- Last safe checkpoint: <sha/tag/description>
- Irreversible parts: <or "none — full revert possible">

## Stop conditions

Unexpected behavior change · an assumption invalidated · unrelated failure
blocking verification · scope-expansion pressure · data risk. On stop:
record state, report, do not improvise.

## Executor protocol (rt-protocol-v1)

1. Freshness first: `git rev-parse HEAD` vs base revision; diff the affected
   symbols. Drift irrelevant to Assumptions → proceed. Purely mechanical
   drift → update this file (if task-update granted), record why, proceed.
   Behavior/dependency/ownership/scope drift → set Status: STALE, report to
   the planner. Never auto-resolve out-of-scope conflicts or rebase shared
   work.
2. Baseline: run the Verify commands BEFORE any edit; expected = the ledger,
   not all-green. Unexpected pre-existing delta → stop, report.
3. Loop: smallest step → apply → verify → checkpoint (commit only per
   Authority). Every checkpoint stays releasable.
4. Red verify: caused by my step and bounded → fix within the micro-step;
   caused by my step, cause unclear → restore task-owned edits to the last
   checkpoint and split the step. Unrelated failure → record; stop only if
   it blocks verification. Never fix unrelated red tests.
5. Two hats: a real bug found here is recorded in the Handoff record and
   reported — never fixed in this task.
6. Discovered prerequisite → propose it and set Status: blocked. Never edit
   the roadmap.
7. Completion: all Acceptance boxes checked → fill the Handoff record → set
   Status: done.

## Handoff record (fill at completion)

- Changed files:
- Deviations from Steps:
- Discovered work proposed:
- Remaining risk:

<!-- TEMPLATE END -->

## Example (filled, abridged)

# RT-001 — Characterize invoice rendering before extraction

- Status: pending · Priority: P1 · Risk: low · Blast radius: billing/render
- Owner: reed · Created: 2026-07-11 · Roadmap phase: 1

**Authority**: edit yes · commit yes (`refactor(billing): <intent> (RT-001)`)
· branch `refactor/rt-001` · task-update yes · roadmap no

**Freshness**: base 3f2a91c · assessment @3f2a91c · rt-protocol-v1 ·
affected: `billing/render.py:render_invoice` · assumptions: no existing
test coverage; output format stable since 2024.

**Decision basis**: F-012 — hotspot, 23 changes/12mo, 480 lines, 0 tests
(churn log + coverage report @3f2a91c). Counterevidence: none found.
Confidence: high.

**Goal**: golden-master coverage pinning current `render_invoice` output for
the 6 invoice types in production use.

**Acceptance**: 6 approval tests passing at base revision · `pytest
tests/billing -q` shows no unexpected delta vs ledger · no production code
modified.

**Non-goals**: no refactoring of `render_invoice` itself (RT-002); no bug
fixes — pin current behavior including the known rounding quirk (F-013).

**Behavior envelope**: preserved — byte-identical rendered output per
fixture (observed via approval-test diff); permitted deltas — none
(test-only task); unknown exposure — PDF metadata timestamps, scrubbed
before comparison; consumers — invoice email pipeline, finance export.

**Scope**: allowed `tests/billing/**` + fixtures; forbidden `billing/**`
production code, generated locale files.

**Prerequisites / Coordination**: none known / none known.

**Steps**: 1. Capture current outputs for the 6 fixture invoices at base
revision (mechanism: run renderer, save scrubbed snapshots; invariant: zero
production-code edits). 2. Add approval tests comparing renderer output to
the snapshots.

**Verify**: `pytest tests/billing -q` → 6 new tests pass; ledger:
`test_tax_eu` known-flaky, retry once.

**Rollback**: trigger — any production-code diff appears; procedure —
`git checkout -- billing/`; last safe checkpoint 3f2a91c; irreversible —
none.

Stop conditions, executor protocol, and handoff record: template text above
applies verbatim.
