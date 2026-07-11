# Refactor Skill — Design Spec (2026-07-11)

Design converged over two adversarial review rounds between Claude (Fable 5,
max effort) and Codex (gpt-5.6-sol, max reasoning effort). All disputed points
resolved; Codex round-2 verdict: 6/6 deviations accepted, final P1 refinements
incorporated.

## Goal

A `refactor` skill that drives an AI agent to: systematically analyze a
codebase, produce an evidence-based diagnosis, recommend the best-fit target
structure (defaulting to "retain current architecture"), and emit a safe,
phased refactoring roadmap plus self-contained task files that other executing
agents — possibly without this skill installed — can pick up and execute
without breaking existing behavior.

Core stance (from cross-review): specify **state, authority, and divergence
handling** over doctrine. Real repositories have red tests, dirty worktrees,
concurrent feature work, and stale plans; the skill must survive all of them.

## Constraints

- Skill name is `refactor` (fixed). One skill, not a planning/execution split.
- All content in English. Repo conventions: SKILL.md with YAML frontmatter
  (name + description-as-trigger), optional `references/` and `assets/`.
- SKILL.md target: 120–150 lines. Terse, imperative, tables over prose.
- Deliverable paths in target repos (fixed):
  `docs/refactor/REFACTOR-ASSESSMENT.md`, `docs/refactor/REFACTOR-ROADMAP.md`,
  `docs/refactor/tasks/RT-*.md`.

## File structure

```text
refactor/
|-- SKILL.md                 # routing + iron laws + 7-phase table + inline output
|                            #   schemas + conditional reference loading + Never list
|-- references/
|   |-- diagnose.md          # multi-signal evidence collection + smell signals ->
|   |                        #   transformation intents (named moves optional metadata)
|   |-- architecture.md      # loaded only on cross-boundary evidence; default = retain;
|   |                        #   selection table; GoF-as-vocabulary + anti-pattern-shopping
|   |-- safety.md            # behavior envelope construction; compat surfaces; charac-
|   |                        #   terization tests + seams; migration patterns; rollout;
|   |                        #   codemod tooling ladder; performance gates
|   `-- execution.md         # how to apply the executor protocol (canonical protocol
|                            #   text lives in rt-task.template.md; no duplication)
`-- assets/
    |-- assessment.template.md
    |-- roadmap.template.md
    `-- rt-task.template.md  # CANONICAL: full field contract + embedded, versioned
                             #   executor protocol block + one compact filled example
```

Single-source rule (Codex round-2 P1): `assets/rt-task.template.md` is the
canonical source of the executor protocol block. `references/execution.md`
explains how to apply it and defers to the RT file's embedded protocol version
on mismatch. Never maintain two copies of the protocol text.

## SKILL.md specification

Section order: purpose (1–2 lines) → mode routing → iron laws → phase table →
output schemas → reference loading table → Never list.

### Frontmatter

Description must cover ALL THREE trigger classes (routing in the body cannot
affect skill discovery):

1. Systemic refactor signals: recurring change friction, defect hotspots,
   dependency tangles, architectural erosion, modernization requests, "refactor
   this repo/system", code-health or architecture audit requests.
2. Bounded local refactors: rename / extract / simplify a function, file, or
   module.
3. Executing an existing `docs/refactor/tasks/RT-*.md` task file.

### Mode routing (first body section)

| Mode | Trigger | Runs |
|---|---|---|
| Bounded refactor | Small, clearly-scoped mechanical ask | Minimal preflight (authority, dirty-tree check, baseline verify, implicit behavior envelope) then execute directly per executor protocol. Skips Phases 2–6. No `docs/refactor/` artifacts unless asked. |
| Execute RT task | User points at an `RT-*.md` | Freshness check, then executor protocol. |
| Assessment only | Audit/assess request, no mandate to change | Phases 0–3, stop after presenting options. Writes assessment only with write authority. |
| Full planning | Systemic refactor request | Phases 0–6. |

Bounded mode skips the planning phases, never the discipline: authority,
dirty-worktree handling, baseline, and behavior envelope still apply
(Codex round-2 P1).

### Iron laws (5)

1. Preserve the approved behavior envelope. Behavior includes timing,
   ordering, logs, error shapes, and wire/serialization formats — not just
   return values.
2. Two hats: a commit either refactors or changes behavior, never both. Bugs
   found mid-refactor are recorded and reported, never fixed in-place.
3. Small verified steps against a recorded baseline; every integration
   checkpoint stays releasable.
4. Evidence is revision-anchored (`path/symbol@revision`) with a confidence
   label; "unknown / not measured" is an accepted value. Never fabricate
   precision.
5. Stop at authority, safety, and freshness gates. Never self-grant
   permissions.

### Phases — uniform five-slot contract

Every phase is specified as: **Inputs / Required actions / Output / Exit
condition / Stop condition.**

**Phase 0 — Route & contract.** Pick mode. Capture: goal (no goal after asking
→ stop; goalless refactoring is aesthetics), scope, constraints (API compat,
no-touch zones, deadlines), authority grants (edit / commit / branch /
task-update / roadmap-update), base revision, evidence budget, artifact
destination + write authority. Stop: no meaningful goal; no write authority
for requested artifacts.

**Phase 1 — Baseline.** System map (languages, build/test commands, entry
points, module dependency direction). Compatibility surface inventory (public
APIs, CLI args/output/exit codes, events/queues/schemas, config keys +
defaults, stored/serialized formats, DB schema, operational: logs, metrics,
latency, resource use). Consumers. Repo state (dirty worktree recorded and
isolated, never absorbed). Run the test suite; record the **baseline failure
ledger** (known-red, flaky, unrunnable + reason). Later verification means "no
unexpected delta vs ledger", never "all green". Stop: no behavioral
observation method can be established at all.

**Phase 2 — Evidence & diagnosis.** Multi-signal candidate discovery: churn ×
complexity is candidate discovery ONLY (exclude generated/vendor/lock paths);
combine temporal coupling, defect/incident concentration, dependency cycles,
fan-in/fan-out, size/age trends. Ordinal ranking with confidence and
counterevidence — no fake decimal ROI scores. Smell classification via
diagnose.md (signals → transformation intents). Safety-net gap assessment.
Deferred candidates carry a reason and a concrete revisit trigger (replaces
"do-not-refactor list"). Findings separate observed fact from inference. Stop:
evidence budget exhausted → report partial results with gaps labeled.

**Phase 3 — Options & decision (STOP gate).** ≥2 viable options, always
including "do nothing / retain current architecture". Structural change
appears only when cross-boundary evidence supports it. Per option: benefit
tied to the Phase-0 goal, effort, migration risk, uncertainty. **Always stop
for owner decision unless continuation was explicitly pre-authorized in
Phase 0.**

**Phase 4 — Design the approved slice.** Minimum target structure for the
approved option. Behavior envelope: preserved behavior / permitted deltas /
unknown exposure / consumers / observation method. Safety mechanisms only for
identified gaps (characterization tests are gap-driven, not unconditional).
Compatibility strategy (deprecation, versioning, expand–migrate–contract).
Rollout + rollback class. First vertical slice (pilot). Stop: approved option
requires an unavailable safety mechanism → back to options.

**Phase 5 — Roadmap & JIT tasks.** Dependency graph. Phased roadmap; each
phase: objective, exit gate, risk level, rollback point, system releasable.
Generate detailed RT files ONLY for the next approved phase. Mandatory
reassessment after the pilot before expanding later phases.

**Phase 6 — Handoff & outcome contract.** Verify each RT file is
self-contained (freshness fields, embedded protocol + version). Outcome
measures tied to the Phase-0 goal (e.g., lead time, defect rate, build time,
dependency-violation count). Tell the user how to launch executors: executors
receive exactly repository root, approved RT file, expected base revision,
authority boundaries. Parallel execution only for dependency-independent
tasks with non-overlapping scope.

### Inline output schemas

SKILL.md lists required fields for all three deliverables as positive schemas
(full skeletons live in assets). Output-shape requirements buried in
references get omitted — they must be in SKILL.md.

### Conditional reference loading

| Condition | Load |
|---|---|
| Running Phase 2 diagnosis | `references/diagnose.md` |
| Evidence shows a cross-boundary design problem | `references/architecture.md` |
| Building envelope/safety mechanisms; medium/high-risk boundary, DB, or API change | `references/safety.md` |
| Emitting RT tasks | `assets/rt-task.template.md` |
| Executing an RT task | `references/execution.md` (executors without the skill use the RT-embedded protocol) |

Never load all references in one run — that defeats progressive disclosure.

### Never list

Big-bang rewrite; refactoring without an established baseline; mixing
refactoring and behavior change in one commit; drive-by bug fixes; patterns or
architecture without evidence of the problem they solve; fabricated or
unlabeled-uncertainty evidence; self-granted authority (commits, pushes,
roadmap edits); proceeding past a failed gate; generating tasks for unapproved
phases; breaking a compatibility surface without a deprecation path.

## References specification

### diagnose.md (~150–200 lines)

Evidence collection: git churn commands, hotspot construction, exclusion rules
(generated/vendor/lock/formatting-only), multi-signal table (signal → how to
measure → what it indicates → caveats), ordinal ranking + confidence +
counterevidence, evidence record format (source, revision, observed fact vs
inference, confidence, limitations, "not measured" allowed). Smell table:
detectable signal → transformation intent (+ optional Fowler move name as
metadata), grouped code/design/architecture/test levels. Slim: signals and
mechanisms only, no textbook prose.

### architecture.md

Default = retain current architecture. Systemic-evidence bar for proposing
architectural change. Assessment checklist: dependency direction, boundary
quality ("can you change internals without breaking consumers?"), screaming
architecture, deep vs shallow modules. Selection table: context → suitable
style (CRUD app → layered; rich domain → hexagonal/ports-and-adapters; many
integrations → adapters at boundaries; monolith + team growth → modular
monolith with enforced boundaries before microservices; event-heavy →
event-driven with explicit caveats). Migration mechanics live in safety.md.
GoF subsection: patterns are vocabulary for observed problems; a pattern must
name the finding it resolves; rule of three; anti-pattern-shopping rule.

### safety.md

Behavior envelope construction procedure. Compatibility surface checklist
(mirrors Phase 1 inventory). Test-reality assessment. Characterization tests:
pin current behavior including bugs; golden master / approval testing for
complex outputs; gap-driven only. Seams (Feathers): sprout method/class, wrap
method, extract interface, parameterize constructor. Migration patterns:
strangler fig, branch by abstraction, parallel change (expand–migrate–
contract), DB specifics (old/new coexistence, online migration constraints,
resumable backfills, dual read/write policy, lock budgets, reconciliation,
forward-only recovery where rollback is unsafe). API/event changes: consumer
inventory, contract tests, compatibility matrix, versioning, deprecation
telemetry, idempotency, error-shape preservation. Performance gates: only for
affected critical paths; record baseline environment, tolerance, noise,
regression threshold. Rollout: feature flags, canary, shadow traffic, dual
run, kill switches, deployment sequencing. Codemod tooling ladder:
(1) repo-native / IDE / compiler refactorings, (2) existing AST codemod
tooling, (3) structural tools (ast-grep, OpenRewrite, jscodeshift, ts-morph,
clang tooling, language equivalents), (4) text replacement only for
mechanically safe cases. Codemod tasks require dry-run output, idempotence,
changed-file counts, residue search, rollback path. Monorepo/CI notes:
package/build graphs, affected-project selection, ownership boundaries,
required checks.

### execution.md

How an executing agent applies the protocol: task pickup (inputs: repo root,
RT file, expected base revision, authority boundaries), freshness check
detail, the small-step loop, failure classification, escalation, handoff
record. States explicitly: the protocol text embedded in the RT file is
canonical for executors; on version mismatch the RT-embedded version wins.

Executor protocol content (canonical text in rt-task.template.md):

1. Freshness first: compare current revision + scoped symbols against the
   recorded base. Irrelevant drift → proceed. Purely mechanical drift → update
   task, record reason. Behavior/dependency/ownership/scope drift → mark
   `STALE`, return to planning. Never auto-resolve out-of-scope conflicts or
   rebase shared work without authority.
2. Baseline-delta verification, per the task's ledger excerpt — never
   "all green".
3. Loop: smallest step → apply transformation intent → verify → checkpoint
   (commit only per granted authority and repo-native conventions).
4. Red verify → classify: caused by my step and bounded → fix within the
   micro-step; otherwise restore task-owned edits only to the last checkpoint
   and split the step; unrelated failure → record, stop only if it blocks
   verification.
5. Two hats: real bug found → record + report, never fix in-place.
6. Discovered prerequisite → propose it and mark the task blocked. Never
   self-modify the roadmap.
7. Handoff record on completion: changed files, deviations, discovered work,
   remaining risk.

## RT task file contract (rt-task.template.md)

Required fields:

- **Identity**: ID (`RT-NNN`), title, status, priority, owner, created,
  roadmap phase.
- **Authority**: edit / commit / branch / task-update / roadmap-update grants.
- **Freshness**: base revision, assessment version, embedded protocol version
  (+ mismatch rule), affected symbols, assumptions.
- **Decision basis**: finding IDs + evidence summary (source, revision,
  observed facts) + counterevidence + confidence. Self-contained — IDs alone
  are not.
- **Goal**: measurable. **Acceptance**: task-local completion criteria (the
  program-level goal may not be observable within one task).
- **Non-goals**: explicit, prevents semantic scope creep beyond forbidden
  paths.
- **Behavior envelope**: preserved / permitted deltas / unknown exposure /
  consumers / observation method.
- **Scope**: allowed files/symbols, forbidden paths, generated-code policy.
- **Risk**: class + blast radius — determines which conditional gates
  activate.
- **Prerequisites**: required; `none known` allowed.
- **Coordination**: required; `none known` allowed (likely conflicts, owners,
  parallel-safe tasks).
- **Transformation steps**: ordered, intent-level (intent + invariant +
  mechanism); named Fowler moves optional metadata.
- **Verify**: commands + expected results + relevant baseline-ledger excerpt.
- **Rollback**: trigger, procedure, last safe checkpoint, irreversible /
  forward-fix consequences — never class alone.
- **Stop conditions**: unexpected behavior, changed assumptions, unrelated
  failures, scope expansion, data risk.
- **Divergence protocol**: proceed / mechanical-update + record / `STALE` →
  return to planning.
- **Handoff record**: filled at completion.

Conditional fields (include only when applicable): rollout (deployment order,
monitoring, canary/shadow requirements), data gates.

Sizing rule: one conceptual transformation + one behavior envelope + bounded
scope + a clear rollback point. "One agent session" is not a sizing rule.

The template ends with ONE compact filled example (replaces prose field
explanations).

## Deliverable templates

- **assessment.template.md**: header (date, scope, base revision, mode, goal,
  authority), system map, baseline failure ledger, compatibility surfaces,
  findings table (ID / severity / smell / evidence / confidence / impact /
  candidate transformation), deferred candidates (+ revisit triggers),
  options + recommendation, approved design (filled post-decision).
- **roadmap.template.md**: goal + outcome measures, phases (objective / tasks
  / exit gate / risk / rollback point), dependency notes, reassessment points
  (pilot gate mandatory).

## Verification plan (pre-ship)

Pressure-test with fresh agents, WITH a no-skill control group, explicit pass
criteria, and repeated samples for routing/discipline scenarios:

1. Simple rename request (must route to bounded mode, no planning docs)
2. Known-red test suite (must build ledger, not stall or "fix" unrelated red)
3. Dirty worktree (must isolate, never absorb or commit user work)
4. Large monorepo (must respect evidence budget, no context burnout)
5. DB-adjacent refactor (must load safety.md, propose expand–migrate–contract)
6. Architecture bait — messy but working layered app (must default to retain;
   no drive-by Clean Architecture prescription)
7. Stale RT task (must detect drift, mark STALE, not improvise)
8. Time pressure ("just do it quickly") (must still hold gates)

Pass criteria: no skipped gates, no unsupported claims, no unneeded
architecture recommendations, no out-of-scope edits.

Also: add the skill to the repo README table.

## Cross-review decision log

| Decision | Outcome |
|---|---|
| Rename to `planning-refactors` | Rejected — name fixed by owner; mitigated by frontmatter covering all three trigger classes + routing as first body section |
| Split into planning + execution skills | Rejected — one skill with routed modes; RT files embed the protocol so executors without the skill are covered |
| Cut two-hats from iron laws | Rejected — drive-by fixes are the top observed agent failure; keeps its own law |
| Cut smell catalog | Reduced — signals → transformation intents only |
| Cut GoF entirely | Reduced — conditional subsection, vocabulary-for-observed-problems framing |
| Mandatory architecture recommendation | Replaced — default retain, evidence bar for change |
| "All green or stop" | Replaced — baseline failure ledger + no-unexpected-delta |
| "Red means revert, always" | Replaced — failure classification, task-owned-edits-only restore |
| Upfront full task generation | Replaced — JIT per approved phase + pilot reassessment |
| Unconditional characterization tests / mutation testing | Replaced — gap-driven; mutation testing only for high-risk weak-test code |
| 7 iron laws | Compressed to 5 enforceable invariants |
| Executor self-updates roadmap | Replaced — propose + blocked; planner/owner owns scope |
