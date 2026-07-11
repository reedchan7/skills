# REFACTOR-ASSESSMENT template

Copy everything below the marker to `docs/refactor/REFACTOR-ASSESSMENT.md`.

<!-- TEMPLATE START -->

# Refactor Assessment — <repo/subsystem>

- Date: <date> · Base revision: <sha> · Mode: assessment-only | full-planning
- Goal (owner's words): <why this refactor exists>
- Scope: <in> · No-touch zones: <out>
- Authority: edit <y/n> · commit <y/n> · branch <y/n> · task-update <y/n> ·
  roadmap-update <y/n>
- Evidence budget: <cap> · Spent: <actual>

## System map

- Languages/frameworks: · Build: `<cmd>` · Test: `<cmd>` (runtime: <dur>)
- Entry points:
- Module dependency direction (observed, not assumed):

## Baseline failure ledger

| Test/check | Status | Note |
|---|---|---|
| <name> | known-red / flaky / unrunnable | <reason> |

## Compatibility surfaces

| Surface | Details | Contract class |
|---|---|---|
| <API/CLI/event/config/format/DB/operational> | <what> | documented / implicit / internal / unknown |

## Findings

| ID | Severity | Signal | Evidence (source@revision, observed fact) | Inference | Confidence | Counterevidence | Candidate transformation |
|---|---|---|---|---|---|---|---|
| F-001 | | | | | | | |

## Deferred candidates

| Area | Reason deferred | Revisit trigger |
|---|---|---|

## Options

### Option 1 — Do nothing / retain current architecture

Benefit vs goal: · Cost: · Risk: · Uncertainty:

### Option 2 — <bounded local refactor>

Benefit vs goal: · Cost: · Risk: · Uncertainty:

### Option N — <structural change; only with cross-boundary evidence>

Benefit vs goal: · Cost: · Risk: · Uncertainty:

**Recommendation** (+ what evidence would falsify it):

## Approved design (fill after the decision gate)

- Approved option: · Approved by: <owner> on <date>
- Behavior envelope summary:
- Safety mechanisms (gap-driven):
- Compatibility strategy:
- Rollout / rollback:
- Pilot slice:

<!-- TEMPLATE END -->
