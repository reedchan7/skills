---
name: refactor
description: Use when the user asks to refactor, restructure, or clean up code at any scale — systemic signals (recurring change friction, defect hotspots, dependency tangles, architectural erosion, modernization requests), a code-health or architecture audit, a bounded local refactor (rename, extract, simplify a function, file, or module), or when asked to execute an existing docs/refactor/tasks/RT-*.md task file.
---

# refactor

Plan and execute behavior-preserving refactors: evidence-based diagnosis,
owner-approved options, phased roadmap, and self-contained task files that
any executing agent can run safely. Specify state, authority, and divergence
handling — not doctrine.

## Mode routing — decide FIRST

| Mode | Trigger | Run |
|------|---------|-----|
| Bounded refactor | Small, clearly scoped mechanical ask (rename, extract, inline, simplify one function/file/module) | Preflight: authority, dirty-tree check, baseline verify, implicit behavior envelope. Then execute per `references/execution.md`. Skip Phases 2–6. No `docs/refactor/` artifacts unless asked. |
| Execute RT task | Given a `docs/refactor/tasks/RT-*.md` | Freshness check, then executor protocol (`references/execution.md`). |
| Assessment only | Audit / assess / "how healthy is this code", no mandate to change | Phases 0–3; stop after presenting options. Write the assessment only with write authority. |
| Full planning | Systemic refactor of a repo/subsystem | Phases 0–6. |

Bounded mode skips the planning phases, never the discipline.

## Iron laws

1. Preserve the approved behavior envelope. Behavior includes timing,
   ordering, logs, error shapes, and wire/serialization formats — not just
   return values.
2. Two hats: a commit either refactors or changes behavior, never both. A
   bug found mid-refactor is recorded and reported, never fixed in-place.
3. Small verified steps against the recorded baseline; every integration
   checkpoint stays releasable.
4. Evidence is revision-anchored (`path/symbol@revision`) and carries a
   confidence label; "unknown / not measured" is an accepted value. Never
   fabricate precision.
5. Stop at authority, safety, and freshness gates. Never self-grant
   permissions.

## Phases

### Phase 0 — Route & contract

Pick the mode. Capture: goal (ask if missing; still none → STOP — goalless
refactoring is aesthetics), scope, constraints (API compatibility, no-touch
zones, deadlines), authority grants (edit / commit / branch / task-update /
roadmap-update), base revision (`git rev-parse HEAD`), evidence budget,
artifact destination + write authority.
Stop: no meaningful goal; no write authority for requested artifacts.

### Phase 1 — Baseline

Map the system: languages, build/test commands, entry points, module
dependency direction. Inventory compatibility surfaces: public APIs, CLI
(args, output, exit codes), events/queues/schemas, config keys + defaults,
stored/serialized formats, DB schema, operational behavior (logs, metrics,
latency, resource use). Identify consumers. Record repo state — a dirty
worktree is recorded and isolated, never absorbed. Run the test suite;
record the baseline failure ledger: known-red, flaky, unrunnable (+ reason).
Verification from here on means "no unexpected delta vs the ledger", never
"all green".
Stop: no behavioral observation method can be established.

### Phase 2 — Evidence & diagnosis

Load `references/diagnose.md`. Multi-signal candidate discovery — churn ×
complexity nominates candidates only; exclude generated/vendor/lock paths;
combine temporal coupling, defect concentration, dependency cycles,
fan-in/out. Ordinal ranking with confidence and counterevidence — no decimal
ROI scores. Findings separate observed fact from inference. Deferred
candidates carry a reason and a concrete revisit trigger.
Stop: evidence budget exhausted → report partial results, gaps labeled.

### Phase 3 — Options & decision — STOP GATE

Present ≥2 viable options, always including "do nothing / retain current
architecture". A structural change appears only when cross-boundary evidence
supports it (then load `references/architecture.md`). Per option: benefit
tied to the Phase-0 goal, effort, migration risk, uncertainty.
STOP for the owner's decision unless continuation was explicitly
pre-authorized in Phase 0.

### Phase 4 — Design the approved slice

Load `references/safety.md`. Minimum target structure for the approved
option. Behavior envelope: preserved / permitted deltas / unknown exposure /
consumers / observation method. Safety mechanisms for identified gaps only.
Compatibility strategy (deprecation, versioning, expand–migrate–contract).
Rollout + rollback class. Define the first vertical slice (pilot).
Stop: the approved option needs an unavailable safety mechanism → Phase 3.

### Phase 5 — Roadmap & just-in-time tasks

Build the dependency graph. Phase the roadmap; each phase: objective, exit
gate, risk, rollback point, system releasable. Copy
`assets/rt-task.template.md` and generate RT files ONLY for the next
approved phase. Reassess after the pilot before expanding.

### Phase 6 — Handoff & outcome contract

Verify every RT file is self-contained (freshness fields, embedded protocol
+ version). Record outcome measures tied to the Phase-0 goal (lead time,
defect rate, build time, dependency violations). Executors receive exactly:
repo root, approved RT file, expected base revision, authority boundaries.
Parallel execution only for dependency-independent tasks with
non-overlapping scope.

## Deliverables (full skeletons in assets/)

`docs/refactor/REFACTOR-ASSESSMENT.md` — header (date, scope, base revision,
mode, goal, authority, evidence budget), system map, baseline failure
ledger, compatibility surfaces, findings (ID, severity, evidence,
confidence, counterevidence, candidate transformation), deferred candidates
+ revisit triggers, options + recommendation, approved design.
`docs/refactor/REFACTOR-ROADMAP.md` — goal + outcome measures, phases
(objective, tasks, exit gate, risk, rollback point), dependency notes,
mandatory pilot reassessment, reassessment log.
`docs/refactor/tasks/RT-NNN-<slug>.md` — identity, authority, freshness,
decision basis, goal + task-local acceptance, non-goals, behavior envelope,
scope, risk (class + blast radius), prerequisites, coordination,
transformation steps, verify + expected results, rollback (trigger,
procedure, checkpoint, consequences), stop conditions, divergence protocol,
embedded executor protocol, handoff record. Conditional: rollout, data
gates.

## Load references only when needed

| Condition | Load |
|---|---|
| Running Phase 2 diagnosis | `references/diagnose.md` |
| Evidence shows a cross-boundary design problem | `references/architecture.md` |
| Building envelope/safety; medium/high-risk, DB, or API change | `references/safety.md` |
| Emitting RT tasks | `assets/rt-task.template.md` |
| Executing an RT task (skill installed) | `references/execution.md` |

Executors without this skill follow the RT-embedded protocol. Never load all
references in one run.

## Never

- Big-bang rewrite
- Refactoring without an established baseline
- Mixing refactoring and behavior change in one commit
- Drive-by bug fixes
- Patterns or architecture without evidence of the problem they solve
- Fabricated evidence, or uncertainty presented as fact
- Self-granted authority (commits, pushes, roadmap edits)
- Proceeding past a failed gate
- Generating tasks for unapproved phases
- Breaking a compatibility surface without a deprecation path
