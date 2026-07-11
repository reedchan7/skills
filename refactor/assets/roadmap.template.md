# REFACTOR-ROADMAP template

Copy everything below the marker to `docs/refactor/REFACTOR-ROADMAP.md`.

<!-- TEMPLATE START -->

# Refactor Roadmap — <repo/subsystem>

- Base assessment: REFACTOR-ASSESSMENT.md @ <revision/date>
- Approved by: <owner> on <date>
- Goal: <from Phase 0, verbatim>
- Outcome measures: <post-refactor success metrics tied to the goal — e.g.
  lead time, defect rate, build time, dependency-violation count>

## Phases

### Phase 1 — <objective> (pilot)

- Tasks: RT-001 <slug>, RT-002 <slug> (generated)
- Exit gate: <observable criteria>
- Risk: low/med/high · Rollback point: <sha/flag/mechanism>
- Releasable at end because: <flag off / adapter in place / ...>
- MANDATORY: reassess this roadmap after the pilot, before generating
  Phase 2 tasks.

### Phase 2 — <objective>

- Tasks: NOT YET GENERATED — just-in-time after the Phase 1 reassessment
- Exit gate: · Risk: · Rollback point:

## Dependency notes

<ordering constraints between phases/tasks; parallel-safe groups (must be
dependency-independent with non-overlapping scope)>

## Reassessment log

| Date | After phase | Changes made | Why |
|---|---|---|---|

<!-- TEMPLATE END -->
