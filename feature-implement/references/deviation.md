# Deviation protocol: code, PLAN, or SPEC

Load whenever current reality differs from an approved artifact. Every
deviation is classified before editing and recorded in PLAN.

| Level | Predicate | Action | Approval / record |
|---|---|---|---|
| Code | Mechanism differs, but active requirements, interfaces, scope, risk, files, and verification remain unchanged | Adjust inside the current slice; rerun affected checks | PLAN deviation row |
| PLAN | Slice/file/interface/dependency/checkpoint changes, while active SPEC meaning and risk remain unchanged | Update PLAN, coverage matrix, and downstream slice interfaces; invalidate affected checkpoints | Re-run plan validator; repeat plan gate when scope/risk/files materially changed |
| SPEC | Behavior, AC/RC/NFR, global constraint, risk, rollout, or verification meaning changes; two requirements conflict; an unplanned assertion migration is needed | STOP production edits; propose options + recommendation | Update normative SPEC section, bump version, append decision log, set Draft, regain approval; then regenerate affected PLAN/tests |

When unsure, choose the higher level.

## Required report shape

```text
Expected: <artifact statement>
Found: <code/environment fact with evidence>
Impact: <requirements/slices/tests/data/rollout affected>
Options:
1. <option + consequence>
2. <option + consequence>
Recommendation: <one choice + reason>
```

## Approved test changes

SPEC is normative; tests are protected evidence.

- **Mechanical repair:** fixture/import/setup/test-code defect with unchanged
  assertion meaning. Fix narrowly, record as Code deviation, verify the same
  behavior still goes RED/GREEN as appropriate.
- **Planned migration:** PLAN names an existing test whose old assertion is
  explicitly superseded by an active approved AC/RC. Update only the superseded
  assertion, retain unrelated checks, and record requirement ID. No second
  amendment is required when the current approved SPEC already grants authority.
- **Contract change:** assertion meaning changes without current SPEC authority.
  This is a SPEC deviation; stop and amend before editing.

Deleting, skipping, weakening, broad wildcard matching, test-mode detection,
and implementation special-casing are never valid migrations.

## Amendment invariants

- Normative SPEC body describes current approved intent.
- Version increments once per amendment batch.
- Decision log states old → new, reason, approver, and affected IDs.
- Status returns to Draft for material change; implementation resumes only
  after approval and coverage/PLAN revalidation.
- Superseded behavior remains discoverable through Git and decision log; stale
  active clauses do not remain in the current contract.
