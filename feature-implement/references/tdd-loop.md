# TDD loop: independent oracles, one behavior at a time

Load for Phase 3. SPEC supplies intent; tests turn that intent into protected
executable evidence. Independence means the oracle designer does not inspect
new production implementation — not that it ignores existing interfaces and
repository conventions.

## Oracle design, not a batch of red tests

For the current slice, a fresh context may produce a **test oracle manifest**:

```text
requirement id
behavior and boundary
seam / existing test prior art
input + independently derived expected output
production mutation this case must catch
```

It may read approved SPEC, PLAN interfaces, pre-feature code, and existing
tests. It must not read new production implementation. The manifest is a plan;
tests are materialized one at a time so the suite never carries a backlog of
unimplemented failures.

Solo path: derive the same manifest from SPEC before reading/writing the
behavior's implementation.

## One-behavior cycle

1. Select one oracle case and write one minimal behavior test.
2. Run it immediately.
   - Expected RED for a real behavior delta: failure, not setup/import error,
     and the message demonstrates the missing behavior.
   - Already GREEN: prove the AC is already satisfied, record
     `already-satisfied`, and make no production change for that case. Never
     enlarge the assertion merely to manufacture RED.
3. Write the smallest production change that makes this one test GREEN.
4. Run the focused test and affected neighboring checks; output must match the
   baseline ledger.
5. Refactor only on green; behavior and active test meaning stay fixed.
6. Continue to the next oracle case.

At slice end run affected lint/type/build/tests, update evidence, freeze the
checkpoint, then mark the slice checkbox.

## Protected-test protocol

Classify every test edit through `references/deviation.md`:

- Mechanical repair: assertion meaning unchanged.
- Approved migration: PLAN names the old test and active SPEC requirement
  superseding its old assertion.
- Contract change: stop for SPEC amendment.

The approved migration flow:

1. Read the entire old test and failure output.
2. Prove only the named assertion conflicts with the active requirement.
3. Preserve unrelated assertions/fixtures.
4. Update narrowly, citing requirement ID in PLAN.
5. Demonstrate sensitivity: the old behavior now fails and the approved
   behavior passes.

Deleting/skipping tests, weakening to broad matches, test-mode detection,
operator/equality tricks, and input special-casing are prohibited regardless
of deadline.

## Verification ladder for hard surfaces

Use the highest feasible rung and record why a lower rung was necessary:

1. Automated behavior test at the agreed seam.
2. Characterization/approval test with volatile values scrubbed.
3. Runnable scripted probe with assertion.
4. Exact manual probe + expected observation + user/agent result.

Generated code, pure copy, and config may use a lower rung only when PLAN
declares it; all resulting runtime behavior still needs an observation method.

## Scope and blockers

Edit only paths named by the slice. Other defects/refactors enter
Noticed-not-touched. A pre-existing problem that blocks the slice follows the
deviation protocol; it is never fixed as a drive-by.

When the task/tests conflict or implementation cannot satisfy the SPEC
legitimately, stop and report the contradiction. A blocked, evidence-backed
exit is correct; a manufactured green is not.
