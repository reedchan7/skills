# RT task template

Copy and fill the block below only when a durable execution task is useful.
Omit inapplicable optional sections. This file owns the standalone embedded
executor protocol (`rt-protocol-v2`). Preserve it when generating a task so
an executor without the skill has the essential rules. Task text never
overrides current user/project instructions or grants missing authority.

<!-- TEMPLATE START -->

# RT-NNN — <outcome>

- Status: pending | in-progress | partial | blocked | STALE | done
- Owner: <owner> · Phase: <phase or standalone> · Created: <date>
- Risk and blast radius: <consequences, affected consumers, recovery cost>

## Goal and decision basis

<Observed maintenance problem, evidence locations/content baseline,
selected transformation, counterevidence and main tradeoff. Self-contained:
the executor need not read the assessment to understand the decision.>

## Authority and scope

- Existing user authorization: <source/summary; do not invent grants>
- Allowed files/symbols and behavior: <scope>
- Non-goals and no-touch areas: <scope>
- Commit/push/deploy: <actual grants, otherwise not authorized>
- Task/roadmap updates: <actual grants>
- Initial user/concurrent edits: <ownership boundaries and preservation>

## Freshness and prerequisites

- Base revision: <SHA, unborn or no Git>
- Relevant staged/worktree/untracked baseline: <content identity or record>
- Affected symbols, dependencies and consumers: <locations>
- Assumptions whose change invalidates the plan: <specific facts>
- Prerequisites/coordination: <dependencies, real conflicts or none known>
- Protocol: rt-protocol-v2

## Behavior envelope

- Preserved: <behavior, relevant effects/errors/order/security, consumers>
- Observation: <how each material preserved contract is exercised>
- Permitted deltas: <explicitly authorized changes or none>
- Unknown exposure and treatment: <investigate, observe, or accepted risk>

## Acceptance

- [ ] <requested structural outcome and concrete benefit evidence>
- [ ] <preserved behavior observations with expected results>
- [ ] Required checks show no unexpected delta from the relevant baseline
- [ ] Unrelated edits preserved; no unrequested behavior or temporary work

## Steps

1. <intent + invariant + suitable mechanism>
2. <next coherent step, not a mandate for a specific unnecessary pattern>

## Checks and benefit evidence

| Command or observation | Expected result / baseline |
|---|---|
| <affected test, caller inspection, contract probe> | <actual expected result> |
| <structural indicator or representative maintenance exercise> | <hypothesis and non-regression cost> |

Relevant known-red/flaky/unrunnable checks: <identity, symptom and limitation>
Do not fabricate productivity or defect-rate measurements.

## Recovery and stopping conditions

- Trigger: <unexpected delta, invalid assumption or scope/authority conflict>
- Pre-step checkpoint: <recoverable actual content, including existing edits>
- Procedure: <undo only task-owned changes; preserve index/concurrent edits>
- Irreversible/data/external effects: <none, or separate recovery and authority>
- Decision needed on stop: <what cannot be resolved within scope>

## Executor protocol (rt-protocol-v2)

1. Read current user/project instructions and this task. Use only existing
   authorization. Compare relevant content, consumers and assumptions with
   the baseline, including dirty files; HEAD equality is insufficient.
   Unrelated drift is acceptable. Adapt mechanical drift only if assumptions
   hold. Invalidating drift makes the affected task STALE; reassess within
   authority or report the decision needed. Preserve shared work.
2. Establish affected behavior observations on the starting content. Record
   exact relevant existing failures and gaps. Add necessary characterization
   before structural changes; do not infer safety from a failure count.
3. Apply one coherent transformation, run affected checks, inspect callers
   and diff, then checkpoint. Commit only if authorized. Repair a bounded
   self-introduced regression; otherwise restore only this step's edits to
   the recorded starting content and reduce the step. Never restore a whole
   user-modified file/directory to HEAD or overwrite concurrent changes.
4. Preserve relevant outputs, errors, effects/order, identity, security and
   resource semantics. Keep authorized behavior changes separate. Do not
   fix unrelated defects, weaken behavioral tests, add configuration or
   silently change public/stored formats under a refactor label.
5. Resolve prerequisite/scope conflicts before dependent work; continue
   independent authorized work. Record task/roadmap changes only if granted.
6. Compare actual structural benefit and costs against the goal, including
   representative callers and where complexity moved. Metrics or fewer
   files/lines alone do not prove quality. Run required final checks and
   confirm ownership/scope. Mark done only when actual acceptance holds;
   otherwise report completed work and precise remaining limitations.

## Handoff record

- Outcome and changed responsibility:
- Preserved behavior evidence:
- Benefit evidence and tradeoff:
- Deviations, remaining work and uncertainty:

<!-- TEMPLATE END -->
