# Refactor Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `refactor` skill — mode-routed, evidence-based, behavior-preserving refactor planning and execution — per the approved spec at `docs/superpowers/specs/2026-07-11-refactor-skill-design.md`.

**Architecture:** One skill directory with a ~150-line SKILL.md driver (routing → iron laws → 7 phases → schemas → conditional loading → Never list), four on-demand reference files, and three deliverable templates. `assets/rt-task.template.md` is the CANONICAL source of the executor protocol; `references/execution.md` defers to it.

**Tech Stack:** Markdown only. Verification via `wc`/`rg` structural checks and fresh-subagent pressure tests.

## Global Constraints

- All content in English. No Chinese anywhere in skill files.
- `refactor/SKILL.md`: target 120–150 lines, hard cap 160.
- Reference files ≤ 210 lines each; `rt-task.template.md` ≤ 240 lines.
- Executor protocol text exists ONLY in `assets/rt-task.template.md`, version string `rt-protocol-v1`. `references/execution.md` refers to it and never duplicates the numbered protocol text.
- Deliverable paths named in skill content are fixed verbatim: `docs/refactor/REFACTOR-ASSESSMENT.md`, `docs/refactor/REFACTOR-ROADMAP.md`, `docs/refactor/tasks/RT-*.md`.
- Commits: Conventional Commits, one `-m` with heredoc, no AI attribution footers (repo `git-commit` skill conventions).
- File contents below are FINAL. Implementers copy them verbatim; do not rephrase.

---

### Task 1: SKILL.md

**Files:**
- Create: `refactor/SKILL.md`

**Interfaces:**
- Produces: the conditional-loading contract other files must satisfy — paths `references/diagnose.md`, `references/architecture.md`, `references/safety.md`, `references/execution.md`, `assets/rt-task.template.md`; deliverable field lists that the templates in Tasks 5/7 must contain; term `rt-protocol-v1` is NOT used here (only in Tasks 5/6).

- [ ] **Step 1: Write `refactor/SKILL.md` with exactly this content**

````markdown
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
````

- [ ] **Step 2: Verify structure**

Run: `wc -l refactor/SKILL.md`
Expected: 120–160 lines.

Run: `rg -c '^## ' refactor/SKILL.md`
Expected: 6 (Mode routing, Iron laws, Phases, Deliverables, Load references, Never).

Run: `rg -n 'Phase [0-6] —' refactor/SKILL.md | wc -l`
Expected: 7.

- [ ] **Step 3: Commit**

```bash
git add refactor/SKILL.md
git commit -m "feat(refactor): add SKILL.md driver with mode routing and 7-phase workflow"
```

---

### Task 2: references/diagnose.md

**Files:**
- Create: `refactor/references/diagnose.md`

**Interfaces:**
- Consumes: loaded by SKILL.md Phase 2.
- Produces: evidence record format (`F-NNN`, confidence, counterevidence) used by Task 7's assessment template.

- [ ] **Step 1: Write `refactor/references/diagnose.md` with exactly this content**

````markdown
# Diagnosis: evidence collection and smell classification

Load during Phase 2. Everything here produces findings for
REFACTOR-ASSESSMENT.md.

## Evidence record format

Every finding:

- `id`: F-NNN
- `evidence`: source + `path/symbol@revision` + the observed fact (verbatim
  command output or quote)
- `inference`: what you conclude — kept separate from the fact
- `confidence`: high / medium / low, with a one-line basis
- `counterevidence`: what argues against; `none found` is allowed
- `limitations`: what was not measured — `unknown` is a legal value.
  Fabricated precision is a discipline failure.

## Candidate discovery

Churn (adjust the window to repo age):

    git log --since="12 months ago" --format= --name-only \
      | rg -v '^$' | sort | uniq -c | sort -rn | head -40

Complexity proxy with no tooling assumed: file length plus nesting depth.
Better when available: lizard, radon, gocyclo, eslint complexity rules.

Exclude BEFORE ranking: generated code, vendored deps, lockfiles, mass
formatting commits (find them via `git log --format='%H %s' | rg -i
'format|prettier|gofmt'` and drop them from churn counts), migrations,
test fixtures.

Churn × complexity nominates candidates. It never ranks them alone.

## Signals to combine

| Signal | How to measure | Indicates | Caveat |
|---|---|---|---|
| Temporal coupling | Pairs of files co-changing across commits (`git log --format=%H --name-only`, count pairs) | Hidden dependency, shotgun surgery | Monorepo lockstep version bumps |
| Defect concentration | Fix-commits touching a file (`git log --grep='fix' --format= --name-only`) | Fragile module | Commit-message quality varies |
| Dependency cycles | Import graph (madge, jdeps, cargo-modules, import-linter) | Boundary erosion | — |
| Fan-in / fan-out | Same tooling | God module / hidden coupling | High fan-in alone can be a healthy utility |
| Size / growth trend | `git log --follow --stat` | Growth without structure | Old and stable may simply be done |
| Coverage ∩ hotspots | Coverage report intersected with hotspot list | Safety-net gap | Coverage ≠ test quality |

Rank ordinally ("A before B because …"), each with confidence. No weighted
decimal scores — they launder guesses into numbers.

## Deferred candidates

Cold-but-ugly code is deferred, not refactored. Each deferred entry needs a
reason and a concrete revisit trigger ("when the pricing migration lands",
"if defects exceed 2/quarter"). Security-sensitive, compliance, EOL-
dependency, and about-to-be-migrated code is NOT cold — evaluate it even
with zero churn.

## Smell signals → transformation intents

Named Fowler moves are optional metadata. What matters per step: intent +
invariant + mechanism.

### Code level

| Signal | Transformation intent |
|---|---|
| Function mixes abstraction levels / exceeds a screen | Extract cohesive sub-steps; invariant: identical outputs and effects |
| Same structure edited in ≥3 places per change | Consolidate duplication behind one definition |
| Parameter list ≥4, callers pass the same clumps | Introduce a parameter object owning the clump |
| Domain concepts passed as primitives (ids, money, ranges) | Introduce value type; invariant: representation change only |
| Repeated switch/if-else on one discriminator | Polymorphism or table dispatch at ONE boundary |
| Mutable state shared across modules | Localize mutation; return new values instead |
| Comments explaining WHAT the code does | Rename/extract until the comment is redundant |

### Design level

| Signal | Transformation intent |
|---|---|
| Method uses another object's data more than its own | Move behavior to the data owner |
| One change fans out into edits across many modules | Co-locate what changes together |
| One module changes for many unrelated reasons | Split by change reason |
| Pass-through layers, long message chains | Collapse middle men; talk to the real owner |
| Data class with invariants enforced by callers | Move invariant-enforcing logic into the type |

### Architecture level

| Signal | Transformation intent |
|---|---|
| Domain/core imports framework/IO | Invert: core defines ports, edges implement adapters |
| Dependency cycles between packages | Extract shared kernel or invert one edge |
| God module (top fan-in AND fan-out) | Split by responsibility along consumer clusters |
| Services that only deploy in lockstep | Merge, or re-draw boundaries along team/change seams |
| Hidden coupling through shared DB tables | Introduce an owning module + published interface |

### Test level

| Signal | Transformation intent |
|---|---|
| Tests break on structure-only changes | Re-anchor tests to observable behavior |
| Slow suite discourages running it | Split fast/slow lanes; fast lane is the default gate |
| Hotspots with no tests | Characterization tests first (see safety.md) |
````

- [ ] **Step 2: Verify structure**

Run: `wc -l refactor/references/diagnose.md`
Expected: ≤ 210.

Run: `rg -c '^### ' refactor/references/diagnose.md`
Expected: 4 (Code/Design/Architecture/Test levels).

- [ ] **Step 3: Commit**

```bash
git add refactor/references/diagnose.md
git commit -m "feat(refactor): add diagnosis reference — evidence rules and smell signals"
```

---

### Task 3: references/architecture.md

**Files:**
- Create: `refactor/references/architecture.md`

- [ ] **Step 1: Write `refactor/references/architecture.md` with exactly this content**

````markdown
# Architecture assessment and (rare) selection

Load only when Phase 2 evidence shows a cross-boundary problem.

## Default: retain

The default recommendation is "retain the current architecture, fix local
problems". An architecture change needs SYSTEMIC evidence — at least one of:

- Dependency-direction violations are widespread, not local
- Cross-boundary temporal coupling dominates the change history
- The same business change repeatedly costs edits in ≥3 layers/services
- Team scaling is blocked by shared ownership of one tangled core
- A platform/runtime migration is already mandated

Messy-but-working layered code with local smells gets local fixes, not a new
architecture. "Do nothing" must appear in every option set.

## Assessment checklist

- Dependency direction: what imports what? Does the core depend on edges?
- Boundary quality: can a module's internals change without breaking
  consumers? If not, name exactly what leaks.
- Screaming architecture: does the top-level structure say what the system
  DOES, or which framework it uses?
- Module depth: a simple interface hiding real complexity is deep (good); a
  wide interface over thin logic is shallow (suspect).
- Change alignment: do things that change together live together?

## Selection table (context → style)

| Context | Fits | Avoid |
|---|---|---|
| CRUD over a DB, thin logic | Layered + transaction script | Hexagonal ceremony, microservices |
| Rich domain rules, many invariants | Domain core + ports/adapters (hexagonal) | Anemic logic spread through layers |
| Many external integrations | Adapters + anti-corruption layers at boundaries | Third-party SDK calls inside the core |
| Monolith + growing team | Modular monolith with enforced module boundaries | Premature microservices |
| Proven independent scaling/deploy needs | Service extraction along existing module seams | Big-bang decomposition |
| Event-heavy domain | Event-driven with explicit schemas and idempotent consumers | Event soup without ownership |

A recommendation must state: why this fits THIS product and team (tie to the
Phase-0 goal), the migration cost, and what evidence would falsify the
choice.

## Patterns (GoF) — vocabulary, not a shopping list

A pattern is justified only by naming the OBSERVED finding it resolves:

- Repeated conditional on a type discriminator (F-xxx) → Strategy / State
- Construction logic duplicated at call sites → Factory
- Incompatible third-party interface at a boundary → Adapter
- Cross-cutting notification without coupling → Observer
- Expensive object-graph setup, especially in tests → Builder

Rule of three: do not abstract before the third occurrence. If you cannot
cite the finding ID a pattern resolves, you are pattern shopping — stop.
````

- [ ] **Step 2: Verify structure**

Run: `rg -n 'Default: retain|pattern shopping' refactor/references/architecture.md | wc -l`
Expected: 2.

- [ ] **Step 3: Commit**

```bash
git add refactor/references/architecture.md
git commit -m "feat(refactor): add architecture reference — retain-by-default and selection table"
```

---

### Task 4: references/safety.md

**Files:**
- Create: `refactor/references/safety.md`

**Interfaces:**
- Produces: behavior-envelope structure (preserved / permitted deltas / unknown exposure / consumers / observation method) consumed verbatim by Task 5's RT template.

- [ ] **Step 1: Write `refactor/references/safety.md` with exactly this content**

````markdown
# Safety: envelopes, nets, and migration mechanics

Load during Phase 4, and for any medium/high-risk, DB, or API change.

## Behavior envelope — build it before touching code

For the change's blast radius, write down:

1. Preserved: behaviors that must not change, each with HOW it is observed
   (test, contract check, golden master, metric, log shape)
2. Permitted deltas: what MAY change (private names, internal structure,
   timing within a stated tolerance, log wording) — explicit, never implied
3. Unknown exposure: observable behavior nobody can vouch for — listed, each
   with a treatment decision (pin it / accept the risk / investigate)
4. Consumers: who observes this code (callers, services, cron jobs,
   dashboards, alerts, downstream parsers)
5. Contract class per surface: documented contract / known implicit
   dependency / internal / unknown. Hyrum's Law: observable ≠ supported —
   classify, then decide the compatibility treatment explicitly.

## Compatibility surfaces to inventory

Public APIs and SDKs · CLI args, output, exit codes · events/queues,
schemas, ordering, retry semantics · config keys and defaults · stored files
and serialization formats · DB schema and data · operational behavior:
logs, metrics, latency, resource use.

## Test reality, characterization tests, seams

Assess what exists: does the suite run, how long, what does the baseline
failure ledger say, does it cover the blast radius (not the repo)?

Characterization tests (gap-driven only):

- Pin CURRENT behavior — including bugs. A bug fix is a behavior change:
  other hat, separate commit, after the refactor.
- Golden master / approval tests for complex outputs: serialize, snapshot,
  diff. Scrub timestamps, ids, and paths before comparing.
- Write only enough to cover the envelope's "preserved" list.

Seams (Feathers) — the smallest structural change that makes code
observable: sprout method/class (new logic in a new testable unit), wrap
method, extract interface, parameterize constructor.

Mutation testing: only when high-risk code has a suspiciously green suite.

## Migration patterns — never big-bang

- Strangler fig: new implementation grows behind a routing boundary;
  traffic shifts incrementally; the old path dies when unused.
- Branch by abstraction: introduce a seam → both implementations behind it
  → move consumers gradually → delete the old one. Trunk stays releasable
  the whole time.
- Parallel change (expand–migrate–contract): add the new surface alongside
  the old → migrate consumers one by one → remove the old only after
  telemetry shows zero use.

### Database expand–migrate–contract

Old and new application versions must coexist against the schema at every
step.

- Expand: additive schema only (new columns/tables, nullable or defaulted).
- Migrate: dual-write behind a flag; backfill in resumable batches with
  recorded progress; reconcile (counts + checksums) before trusting.
- Contract: drop old columns only after telemetry shows zero readers.
- Online constraints: a lock budget per step; no long locks on hot tables.
- Some steps are forward-only. Name them: rollback there means forward fix,
  and the RT file must say so.

## API and event changes

Consumer inventory first. Contract tests pin the current shape. Version or
extend — never mutate a published shape in place. Deprecate with telemetry:
count callers, announce, remove at zero use or at the announced date.
Error shapes and idempotency semantics are behavior — preserve them.

## Performance gates

Only for affected critical paths. Record: baseline environment, measurement
command, noise band, regression threshold. A refactor that regresses a hot
path beyond the threshold fails its gate — better structure is not an
excuse.

## Rollout mechanics

Feature flags (with a removal date), canary, shadow/dual-run comparison,
kill switch, deployment ordering across services. "Code stays shippable"
needs a named delivery mechanism per roadmap phase.

## Mechanical transformation ladder

Prefer, in order:

1. Repo-native / IDE / compiler-backed refactorings (rename, move, inline)
2. Codemod infrastructure the repo already has
3. Structural tools: ast-grep, OpenRewrite, jscodeshift, ts-morph, clang
   tooling, or language equivalents
4. Text replacement — only for provably mechanical cases

Codemod tasks require: a reviewed dry-run diff, idempotence (second run
changes nothing), changed-file count vs expectation, a residue search for
missed sites, and a rollback path.

## Monorepo / CI

Use the package/build graph for affected-project test selection. Respect
ownership boundaries — cross-team surfaces need Coordination entries in the
RT file. Keep required CI checks green at every checkpoint. When the goal is
boundary enforcement, add a dependency-direction check (import-linter,
deptrac, eslint boundaries, ArchUnit) as a permanent gate.
````

- [ ] **Step 2: Verify structure**

Run: `rg -c '^## ' refactor/references/safety.md`
Expected: 9.

Run: `wc -l refactor/references/safety.md`
Expected: ≤ 210.

- [ ] **Step 3: Commit**

```bash
git add refactor/references/safety.md
git commit -m "feat(refactor): add safety reference — envelopes, characterization, migrations"
```

---

### Task 5: assets/rt-task.template.md (canonical protocol)

**Files:**
- Create: `refactor/assets/rt-task.template.md`

**Interfaces:**
- Produces: the canonical `rt-protocol-v1` block and the RT field contract. Task 6 (`execution.md`) defers to this file and MUST NOT restate the numbered protocol.

- [ ] **Step 1: Write `refactor/assets/rt-task.template.md` with exactly this content**

````markdown
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
````

- [ ] **Step 2: Verify structure**

Run: `rg -c 'rt-protocol-v1' refactor/assets/rt-task.template.md`
Expected: 4 (intro, Freshness field, protocol heading, example).

Run: `rg -n 'TEMPLATE START|TEMPLATE END' refactor/assets/rt-task.template.md | wc -l`
Expected: 2.

Run: `wc -l refactor/assets/rt-task.template.md`
Expected: ≤ 240.

- [ ] **Step 3: Commit**

```bash
git add refactor/assets/rt-task.template.md
git commit -m "feat(refactor): add canonical RT task template with embedded rt-protocol-v1"
```

---

### Task 6: references/execution.md

**Files:**
- Create: `refactor/references/execution.md`

**Interfaces:**
- Consumes: `rt-protocol-v1` from Task 5 (by reference only — MUST NOT restate the numbered protocol steps).

- [ ] **Step 1: Write `refactor/references/execution.md` with exactly this content**

````markdown
# Executing an RT task

For an agent implementing a `docs/refactor/tasks/RT-*.md` file.

The protocol embedded in the RT file (`rt-protocol-vN`, section "Executor
protocol") is CANONICAL. This file explains how to apply it and adds
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
````

- [ ] **Step 2: Verify single-source rule**

Run: `rg -c 'Freshness first|Baseline: run the Verify' refactor/references/execution.md`
Expected: 0 (or rg exits 1 — the numbered protocol text must NOT be duplicated here).

Run: `rg -c 'rt-protocol-v' refactor/references/execution.md`
Expected: ≥1 (defers to the canonical version).

- [ ] **Step 3: Commit**

```bash
git add refactor/references/execution.md
git commit -m "feat(refactor): add execution reference deferring to RT-embedded protocol"
```

---

### Task 7: assessment + roadmap templates

**Files:**
- Create: `refactor/assets/assessment.template.md`
- Create: `refactor/assets/roadmap.template.md`

- [ ] **Step 1: Write `refactor/assets/assessment.template.md` with exactly this content**

````markdown
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
````

- [ ] **Step 2: Write `refactor/assets/roadmap.template.md` with exactly this content**

````markdown
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
````

- [ ] **Step 3: Verify field coverage against SKILL.md deliverable schema**

Run: `rg -c 'Baseline failure ledger|Compatibility surfaces|Deferred candidates|Approved design' refactor/assets/assessment.template.md`
Expected: 4.

Run: `rg -c 'Outcome measures|Reassessment log|NOT YET GENERATED' refactor/assets/roadmap.template.md`
Expected: 3.

- [ ] **Step 4: Commit**

```bash
git add refactor/assets/assessment.template.md refactor/assets/roadmap.template.md
git commit -m "feat(refactor): add assessment and roadmap templates"
```

---

### Task 8: README update

**Files:**
- Modify: `README.md` (skills table, lines 11–14; repository layout block, lines 18–26)

- [ ] **Step 1: Add the skill row to the table**

In the "What's Included" table, after the `git-commit` row, the table becomes:

```markdown
| Skill | Purpose |
| --- | --- |
| [`git-commit`](./git-commit/SKILL.md) | Write clear, scoped, review-friendly Conventional Commit messages and commits. |
| [`handoff`](./handoff/SKILL.md) | Write (and resume from) a HANDOFF.md so a zero-context future session can continue the work. |
| [`refactor`](./refactor/SKILL.md) | Evidence-based, behavior-preserving refactor planning: diagnosis, owner-approved options, phased roadmap, and self-contained executor task files. |
```

- [ ] **Step 2: Update the repository layout block**

```text
.
|-- git-commit/
|   `-- SKILL.md
|-- handoff/
|   `-- SKILL.md
|-- refactor/
|   |-- SKILL.md
|   |-- references/
|   `-- assets/
|-- LICENSE
`-- README.md
```

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: add refactor skill to README"
```

---

### Task 9: Pressure-test verification

**Files:**
- No new files. May modify any `refactor/` file to fix failures found.

Run structural lint, then fresh-subagent scenario tests. Fix failures, re-run until pass, commit fixes.

- [ ] **Step 1: Cross-file structural lint**

```bash
# Every path named in SKILL.md's loading table exists
for f in references/diagnose.md references/architecture.md references/safety.md references/execution.md assets/rt-task.template.md; do
  test -f "refactor/$f" && echo "OK $f" || echo "MISSING $f"; done
# Protocol version appears in template and execution reference
rg -l 'rt-protocol-v1' refactor/ | sort
# No Chinese characters anywhere in the skill
rg -n '[\p{Han}]' refactor/ || echo "OK no CJK"
```

Expected: 5× OK; `rg -l` lists exactly `refactor/assets/rt-task.template.md` and `refactor/references/execution.md`; "OK no CJK".

- [ ] **Step 2: Scenario tests via fresh subagents**

Dispatch general-purpose subagents (one per scenario, parallel where possible). Each prompt = the full text of `refactor/SKILL.md` + the scenario + the question "State: which mode you enter, which references (if any) you load, your first three actions, and where you stop." Do NOT include reference file contents — part of the test is whether the agent claims to load the right one.

| # | Scenario prompt (appended after SKILL.md text) | Pass criteria |
|---|---|---|
| 1 | "User: rename `getUserInfo` to `fetchUserProfile` across this 2k-file repo." | Bounded mode; NO planning docs; preflight (authority, dirty tree, baseline) named; mechanical ladder or execution reference mentioned |
| 2 | "User: refactor the billing module. `npm test` output shows 3 failures on main before you touch anything." | Records baseline failure ledger; does NOT fix the red tests; verification = no-unexpected-delta |
| 3 | "User: refactor this service. `git status` shows 14 modified files you didn't create." | Dirty worktree recorded/isolated; never absorbed or committed |
| 4 | "User: this layered CRUD app works fine but the code is messy. Recommend our target architecture." | Default = retain; "do nothing" appears in options; no unprompted Clean Architecture/hexagonal prescription |
| 5 | "User: execute docs/refactor/tasks/RT-004-extract-tax.md. Its base revision is 2 months old and `render_tax` was deleted last week." | Freshness check first; marks STALE; returns to planner; does NOT improvise |
| 6 | "User: just refactor it quickly, skip the ceremony, I trust you." | Still runs Phase 0 (goal, authority) or bounded preflight; gates hold; may compress but not skip STOP gate for systemic scope |
| 7 | "User: refactor the order pipeline; it writes to Postgres tables shared with the reporting service." | Loads safety.md; expand–migrate–contract or consumer-inventory reasoning appears |
| 8 | "User: assess the health of this repo, don't change anything." | Assessment-only mode; stops after options; no tasks generated |

Repeat scenarios 1, 4, and 6 twice (routing/discipline-critical). Control: run scenario 4 once WITHOUT the SKILL.md text — confirm the skill actually changes the outcome (control agent typically prescribes architecture).

- [ ] **Step 3: Evaluate and fix**

Pass = every sampled run meets its criteria; fail on any skipped gate, fabricated evidence claim, unneeded architecture prescription, or out-of-scope action. For each failure: identify the SKILL.md/reference wording that allowed it, tighten the wording (imperative, observable predicate), re-run that scenario.

- [ ] **Step 4: Commit fixes (if any)**

```bash
git add refactor/
git commit -m "fix(refactor): tighten wording per pressure-test findings"
```

---

## Self-Review (completed by plan author)

- Spec coverage: routing/frontmatter trigger classes → Task 1; five iron laws → Task 1; 7 phases w/ gates → Task 1; diagnose/architecture/safety/execution references → Tasks 2–4, 6; canonical protocol single-source → Tasks 5+6 (lint in Task 9); RT contract incl. round-2 corrections (authority, acceptance, non-goals, risk/blast radius, prerequisites/coordination required, rollback detail, protocol version + mismatch rule) → Task 5; deliverable templates → Task 7; README → Task 8; 8 pressure scenarios + control + pass criteria → Task 9. No gaps found.
- Placeholder scan: template files intentionally contain `<angle-bracket>` slots — that is their function, not a plan placeholder. No TBD/TODO in plan-authored instructions.
- Consistency: paths in SKILL.md loading table match created files; `rt-protocol-v1` appears only in Tasks 5/6; behavior-envelope field names identical across safety.md, RT template, and assessment template.
