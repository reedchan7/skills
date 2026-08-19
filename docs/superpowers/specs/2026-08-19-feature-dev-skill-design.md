# Feature Development Skill Pair — Design Specification

- Date: 2026-08-19
- Revision: 4 (anti-overfit: greenfield-only bootstrap + holdout oracles)
- Research basis: `docs/research/feature-dev-skill-landscape.md`
- Runtime skills: `feature-design`, `feature-implement`
- User aliases: `new-feature`

## Goal

Create a portable, scale-adaptive feature workflow for frontend, backend,
full-stack, and greenfield work:

1. `/feature-design <idea>` challenges and grounds the premise, then produces
   one approved normative SPEC.
2. `/feature-implement` implements that contract in small verified
   slices, proves a bounded regression surface, independently reviews the exact
   candidate, and advances only to the delivery state supported by Git/CI/deploy
   evidence.

The workflow must reduce failure probability; it must never promise zero hidden
bugs or use confidence language as evidence.

## Invocation contract

Both skills are user-invoked (`disable-model-invocation: true`). This removes
the ambiguous auto-routing between “design an add/build request” and “implement a
small feature”. Full sync installs:

- `/feature-design`
- `/new-feature` → rewritten alias of `feature-design`
- `/feature-implement` (SPEC path optional; discovers the active feature)

No hidden router decides whether the user wants design or implementation.

## Artifact and authority model

### One normative contract

Every feature, including Express, owns:

```text
docs/features/<NNN>-<slug>/
|-- SPEC.md                 # current approved normative intent
|-- RESEARCH.md             # conditional evidence; not normative
`-- PLAN.md                 # revision-pinned execution state
```

There is no inline mini-spec or second shadow contract.

Authority:

```text
user-approved SPEC
  > approved executable tests
  > PLAN
  > implementation
```

Tests are protected evidence, not an authority above the SPEC. Test edits are
mechanical repairs, approved migrations, or unapproved contract changes; only
the third requires SPEC amendment.

### Amendments

A behavior/risk/verification change:

1. updates the normative SPEC section;
2. increments Spec version;
3. appends old → new, reason, approver, affected IDs/slices/tests;
4. returns status to Draft;
5. regains approval and revalidates affected PLAN/tests.

Git and the decision log preserve history; stale clauses do not remain active.
Approval binds the current version and a validator-computed **normative digest**
(Assurance + normative sections, excluding lifecycle status and decision log).
Changing lifecycle state does not invalidate approval; changing normative text
or version does.

### Evidence-bound state

```text
Draft
  → Approved
  → In implementation
  → Locally verified
  → Ready for integration
  → Integrated
  → Released
```

`Locally verified` requires all applicable local requirements, regression,
review, and exploration gates on one frozen candidate. Later states require
immutable commit, CI/PR, merge, and deployment/post-deploy evidence
respectively. A waiver cannot convert an unmet active requirement, RC,
security/privacy gate, or real Critical/Important finding into ready.

## Assurance routing

Assurance is stored in SPEC and inherited by PLAN.

| Assurance | Predicate | Design depth | Implementation depth |
|---|---|---|---|
| Express | one reversible existing-flow change or a greenfield single-behavior spike; no new dependency/model/public contract/trust boundary/migration/authz/money/data-lifecycle behavior | bounded recon; steelman-lite; no external research unless upgraded; one approval gate | affected checks; one review; mutation only if risk appears; runnable-surface exploration; inherited plan gate when scope/risk stays fixed |
| Standard | new capability in an existing product, including bounded work on an existing security/privacy/sensitive-data surface | full recon/interrogation; targeted external research; options + independent review | plan gate; affected checks + final full/CI; independent review; targeted exploration; risk-selected mutation |
| Deep | new architecture; irreversible/migration/money/multi-service work; or a new trust boundary/authz/sensitive-data lifecycle. An empty repo is not Deep by itself. | external research, NFRs, rollout, independent review mandatory | full compatibility/release gates, high-risk sensitivity, broad applicable exploration |

Discoveries only raise assurance.

## feature-design phases

### 0 — Frame and create state

Capture raw ask, goal, constraints, destination, and authority. Allocate an ID
and create SPEC Draft immediately from the template. The draft is the target for
all subsequent write-back.

### 1 — Ground current state

Read named files and governing instructions. Trace the closest flow and product
evidence (analytics/support/workarounds), classify evidence as measured /
observed / documented / inferred, map touched seams and hard constraints.

### 2 — Interrogate

Run strongest problem statement, FOR/AGAINST steelman, cruxes, and a keystone
question only when a real decision remains. Facts trigger lookup; decisions go
to the user. Answers update SPEC + decision log immediately.

### 3 — Targeted external research

Conditional charters: problem evidence, competitor behavior, OSS prior art,
engineering practice, buy-vs-build. Every claim carries source, access date,
evidence class, limitation, and question mapping. Blocked load-bearing research
stops the approach gate unless uncertainty is explicitly accepted.

### 4 — Approach gate

Present 2–3 genuinely different approaches, recommendation, falsifying evidence,
test seams, compatibility, rollout, and risks. Use approved isolated prototypes
only for material visual/state unknowns.

### 5 — Complete SPEC

Required normative content:

- problem evidence and product outcome hypothesis;
- goals, non-goals, and Global constraints;
- active AC/RC/NFR, each with `Verify:`;
- bounded regression contract based on credible causal paths;
- design, test seam, rollout/rollback, assumptions, deferrals, limitations;
- amendment policy and decision log.

Deterministic lint checks structure, IDs, Verify mappings, deep-mode NFR/rollout,
approval entry, and word budgets.

### 6 — Approval gate

Self-review plus assurance-selected independent review. Update normative body and
log together. User approval sets status Approved; the only next workflow is
`/feature-implement`.

## feature-implement phases

### 0 — Freeze input and create PLAN

Require Approved SPEC. Draft/Declined is a hard stop. Several unnamed actives
is a hard stop: list and ask, write no PLAN. Record assurance/version/digest,
HEAD, complete Git status, task/unrelated file hashes, and authority. Isolate
unrelated dirty state. Create PLAN immediately. Resume recomputes every
checked slice's bytes before any product edit.

### 1 — Baseline and bounded blast radius

Existing repo: affected baseline, full suite when feasible, otherwise explicit
CI gate/blind spot. Record failure fingerprints, not names only. Greenfield
only when pickup has no product code and no invocable test command: first
slice establishes a runner before product behavior. An existing module with
zero tests is not greenfield — its first test is the product slice.
Coverage ledger tracks covered / no material risk / not assessed.

### 2 — Tracer-bullet PLAN

Every slice maps active AC/RC/NFR, files/interfaces, ordered oracle cases,
approved test migrations, affected checks, rollback, and immutable checkpoint.
Coverage closes both ways. Deterministic validator catches constraint drift,
missing IDs, placeholders, and nonstandard state.
Any stage requiring an earlier deployment, backfill, telemetry window, or
consumer cutover becomes a separate dependent SPEC/PLAN, so each release stage
closes its own Phase 3→7 loop.

### 3 — One-behavior TDD

Fresh context may design an oracle manifest but never a batch of failing tests.
Materialize one test → expected RED → minimal GREEN → affected checks. Already
satisfied behavior remains GREEN with no invented failure. Every slice freezes
a commit/tree or content manifest.

### 4 — Exact-candidate verification

Freeze committed/staged/unstaged/untracked bytes. Run final integration and every
active requirement method. Mutation is risk-selected and runs only in an isolated
copy/tool with byte-for-byte restore proof.

### 5 — Independent review

Use `code-review-pro` when available. Review exact candidate against SPEC + PLAN
on spec and engineering axes. Maximum three autonomous repair rounds; the cap
ends looping, not quality. Real unresolved Critical/Important keeps the feature
non-ready.

### 6 — Risk-driven exploration

Select applicable UI/API/CLI/job/library/SDK/event/migration/config charters.
Sandbox-only by default. UI needs a visual/a11y oracle; N/A carries a reason.

### 7 — Readiness and handoff

Run artifact validators, fill evidence/review/exploration/waiver/risk/demo
report, and advance only to the state supported by local/external evidence.
Commit/push/PR/merge/deploy each require separate authority.

## Deterministic helpers

```text
feature-design/scripts/validate_spec.py
feature-implement/scripts/validate_plan.py
```

The scripts lint traceability and state; they do not claim semantic correctness.

## Behavioral evaluation

`evals/feature-dev/` contains generated Git fixture repositories, deterministic
artifact tests, candidate/control preparation, and hidden local scorers.

Initial objective cases:

1. Express design: SPEC only; production unchanged; approval stop.
2. Approved old-test migration: narrow assertion migration, unrelated assertion
   preserved, test green, PLAN trace.
3. True SPEC conflict: production unchanged; conflict recorded.
4. Greenfield bootstrap: test infrastructure before product behavior, only
   on a true empty tree.
5. Dirty local candidate: unrelated bytes preserved and inventoried.
6. Resume drift: stale checked slice invalidated.
7. Holdout existing runner: implement the behavior; adding a bootstrap
   slice or invented smoke/manifest is a fail (over-ceremony).
8. Holdout first product test: existing module, no tests; first test is a
   product slice, not toolchain bootstrap.

Comparative claims require same model/tools/budget, paired no-skill control,
fresh process, randomized order, at least three runs (five preferred), and
filesystem/Git/test/oracle scoring. Policy-restatement dry-runs are calibration,
not acceptance evidence.

## Decision log

| Decision | Revision-2 outcome | Reason |
|---|---|---|
| Invocation | user-invoked + two aliases | removes overlapping model triggers; matches requested slash UX |
| Small feature contract | compact SPEC, never inline mini-spec | one authority across design/review/delivery |
| Express gate | one SPEC approval; PLAN gate inherited when unchanged | preserves assurance without repeated ceremony |
| Test authority | SPEC normative; tests protected evidence | permits approved old-behavior migration without reward hacking |
| TDD granularity | oracle manifest + one test at a time | avoids horizontal red-test backlog |
| SPEC history | current body + append-only change log | anti-drift and auditable history both hold |
| Contract identity | version + normative digest + bound approval | status changes remain legal; unapproved normative changes cannot execute |
| Candidate identity | committed + index + worktree + untracked + hashes | prevents empty/partial review |
| Mutation | risk-selected, isolated, byte-verified restore | converts destructive manual protocol into bounded evidence |
| Delivery state | local/integration/release split | prevents premature Delivered claims |
| Greenfield | bootstrap only if no product and no runner | avoids forcing S0 onto existing modules |
| Holdout eval | over-ceremony fails; delta vs control is not the goal | detects overfitting to prior trap cases |
| Multi-release migration | one dependent SPEC/PLAN per release stage | prevents local all-slices gate from deadlocking on deployed telemetry |
| Regression scope | credible causal paths + coverage ledger | avoids unbounded shared-seam contracts |
| Review cap | real Important/Critical cannot be parked into ready | loop bound does not lower quality |
| Evaluation | persistent paired behavioral harness | replaces “8/8 policy dry-run” overclaim |
