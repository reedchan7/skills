---
name: feature-implement
description: Implement and verify an approved feature SPEC, or resume its existing PLAN.
disable-model-invocation: true
---

# feature-implement

Implement an approved SPEC in small verified slices. Produce bounded evidence
for requirements and regressions; never claim zero risk or a delivery state
that external Git/CI/deployment evidence does not support.

## Resolve the target — FIRST

A SPEC path is optional. Resolve one SPEC (and its PLAN if any) before Phase 0.

| User said | Use |
|---|---|
| A `SPEC.md` or `PLAN.md` path | That file. A PLAN implies its sibling SPEC. |
| A feature id/slug (`001-export-email`) | `docs/features/<that>/SPEC.md` |
| Nothing, or “continue / implement this” | Discover below |

Discovery (`docs/features/*/SPEC.md`):

1. **Active** = Status in `Approved`, `In implementation`, `Locally verified`,
   `Ready for integration`, `Integrated`. Skip Draft / Declined / Released
   unless the user named that directory.
2. One active SPEC → that target. PLAN present → resume; else create PLAN.
3. Several active → prefer the single `In implementation` with an incomplete
   PLAN. If still several, list path / status / title and ask one question.
4. Zero active → STOP and hand off to `/feature-design` (or `/new-feature`).
   Do not draft a SPEC here.

Never invent a SPEC. Never pick silently among several active features.

| Resolved input | Run |
|---|---|
| Active SPEC, no PLAN | Create PLAN in Phase 0; inherit SPEC Assurance (express / standard / deep); run all applicable phases. |
| Existing PLAN | Validate SPEC version/hash, PLAN identity, candidate snapshot, completed-slice checkpoints, and phase evidence; resume at the first invalid/incomplete gate. |
| No active SPEC | STOP and hand off to `/feature-design`. Even Express uses a compact SPEC; no inline shadow contract. |

Assurance controls depth end-to-end:

- **Express:** affected checks per slice, one review, mutation only when risk
  justifies it, exploration on a runnable touched surface; no second plan
  approval when PLAN stays inside approved scope/risk.
- **Standard:** one plan gate, final full-suite/CI evidence, one independent
  fresh-context review plus scoped re-review when needed, targeted exploration,
  risk-triggered mutation.
- **Deep:** full plan gate, independent review, risk lenses, migration/release
  gates, mutation on high-risk decision logic, full applicable exploration.

Discoveries only increase assurance.

## Pickup hard gates — before any product edit

A failed gate is a successful stop, not a reason to improvise.

1. **Authority.** Status is `Approved` or later. `Draft` / `Declined` → STOP.
   Do not edit production files. Hand off to `/feature-design`. PLAN may
   record only the stop.
2. **One target.** Several active SPECs and no named path/id → STOP. List
   path / status / title. Write no PLAN and no code until the user picks one.
3. **Resume identity.** Recompute SHA-256 of every checkpointed path before
   any product edit. Claimed digest ≠ actual bytes → uncheck that slice, write
   a Deviation row with claimed vs actual, and resume at the first invalid
   gate. A checked box is never proof of completion.
4. **Bootstrap slice.** Only greenfield: no product code and no invocable
   test command. Then the first slice establishes a runner and covers no
   AC/RC/NFR. An existing module with no tests does not get a bootstrap
   slice — its first test is the product slice.

## Authority and contract laws

1. **Authority:** user-approved SPEC is normative. Tests are protected
   executable evidence, not a higher authority. PLAN must list approved test
   migrations; any assertion change without SPEC authority is a SPEC amendment.
2. **Test-first:** for each behavior delta, one test → verified RED → minimal
   GREEN → refactor on green. A behavior already satisfied is proven green and
   changed no further; never manufacture a failure.
3. **Candidate identity:** freeze base, complete changed-path inventory, content
   hashes, and authority. Reviews and mutation checks target that exact snapshot,
   including committed, staged, unstaged, and untracked files.
4. **Evidence:** every claim uses fresh output after the last relevant edit.
   Baseline failures carry fingerprints; same test, different failure = new red.
5. **Deviation:** code / PLAN / SPEC drift follows
   `references/deviation.md`; normative amendments update SPEC body + version +
   decision log and regain approval.
6. **Scope:** edit only the current slice. Other work enters
   Noticed-not-touched; no drive-by fixes.
7. **State honesty:** local checks can reach `Locally verified`. Integration,
   CI, and release states require their own immutable external evidence.

## Phases

### Phase 0 — Pickup, isolate, and create state

Read SPEC fully. `Draft` / `Declined` is pickup gate 1 — stop, do not edit
production files. Otherwise require `Status: Approved` or later with approval
bound to current version + normative digest. Record assurance, version,
normative digest, current HEAD, `git status --porcelain -uall`, authority
(edit/commit/branch/push/PR/merge/deploy), and changed-file hashes.

Isolation:
- Inventory unrelated dirty/untracked files with content hashes first.
- Edit-only / no-commit: stay in the current worktree. Never revert, stage,
  commit, or rewrite those bytes. A scratch copy is allowed only if every
  required result is written back here before handoff.
- Commit/branch authority: prefer an isolated branch; if the user's tree is
  dirty, use a separate worktree so those bytes stay untouched.

Copy `assets/plan.template.md` immediately to the feature directory and fill
identity, `Current phase: 1`, authority, SPEC identity, and candidate baseline.
Resume: apply pickup gate 3 before judging implementability. Drift
invalidates affected gates.
**HARD GATE:** create this PLAN before judging implementability, running a
baseline, or returning a conflict/block report. A conflict still fills identity
and the Deviation row so the decision survives context loss.
Exit: PLAN exists and names an exact candidate. Stop: isolation or freshness
cannot be established.

### Phase 1 — Baseline and blast radius

Load `references/planning.md` and `references/deviation.md`. Inventory
repo-native commands and conventions with evidence. Existing repos: run the
affected baseline and full suite when feasible; otherwise record the CI/full
suite gate and blind spot. Greenfield (pickup gate 4): Phase 1 records
empty-tree identity only. Create runner/smoke files in the first PLAN
slice, covering no product AC/RC/NFR, before any product slice.

Record normalized failure fingerprints. Map credible affected consumers,
contracts, data, and operational surfaces; confirm, amend, or retire RCs
through the SPEC amendment protocol. Close the coverage ledger or label
not-assessed surfaces.
Exit: a deterministic observation method and bounded blast radius exist.

### Phase 2 — Plan tracer-bullet slices

Plan vertical slices with blocking edges, riskiest first. Greenfield starts
with the runner slice above, then product slices. Express reuses the
existing runner and writes one `none` / `N/A` row for empty ledgers.
Each slice names:
goal, AC/RC/NFR IDs, exact files, interfaces, one-at-a-time test oracles,
approved test migrations, affected checks, manual probes, checkpoint method,
and rollback. Coverage closes both ways across every active requirement.
If a destructive/cutover slice depends on a prior deployment, backfill, or
telemetry window, it is not a local downstream slice: split each releasable
expand/backfill/cutover/contract stage into a dependent SPEC/PLAN before
approval. This workflow closes Phases 3→7 for one release stage at a time.

Run `python3 <skill-dir>/scripts/validate_plan.py <SPEC> <PLAN>`.
Express proceeds without another interruption only when validation passes and
scope/risk/files do not exceed the approved SPEC; otherwise present the plan
gate. Standard/Deep present scope, non-goals, files, risks, compatibility,
and rollout for approval unless pre-authorized. On approval set SPEC
`Status: In implementation`.
Exit: validated PLAN and required approval.

### Phase 3 — Build one behavior at a time

Load `references/tdd-loop.md` and `references/deviation.md`. A fresh test
planner may propose oracle cases from SPEC without reading new implementation;
it does not write a batch of failing tests. For each behavior: materialize one
test, RED for the right reason, minimal GREEN, refactor, affected checks.
Apply only approved test migrations.

At each slice end, run affected lint/type/build/tests, record fresh evidence,
then freeze a checkpoint: commit/tree SHA when authorized, otherwise complete
file inventory + content digests. Mark the standard slice checkbox only then.
Exit: every slice requirement is green at its seam and checkpointed.

### Phase 4 — Integration and sensitivity verification

Load `references/verification.md` and `references/deviation.md`. Freeze the
candidate snapshot. Run final integration checks, every RC method, and every
AC/NFR not already closed by fresh evidence. Run mutation only when Assurance
and risk select it, inside an isolated copy/tool, with byte-for-byte restoration
proof. Any changed evidence invalidates downstream gates.
Exit: evidence table closes or uncovered items block readiness.

### Phase 5 — Independent review, 1–3 bounded rounds

Load `references/review-loop.md` and `references/deviation.md`. Invoke
`code-review-pro` when installed; otherwise use the embedded fallback. Review
the exact candidate against SPEC and PLAN. Round 1 is mandatory. Standard/Deep
require a fresh independent context; if unavailable, stop below
`Locally verified` and ask the user to run/authorize one. Express may use a
clearly labeled self-review fallback. Fix
Critical/Important findings and scoped re-review; round 3 ends the loop, not
the quality bar. False findings may be ruled out with disproof. Real unresolved
Critical/Important findings require user action and keep the feature below
production-ready status.
Exit: no unresolved Critical/Important, or STOP with an explicit non-ready state.

### Phase 6 — Risk-driven exploratory verification

Load `references/exploration.md` and `references/deviation.md`. Select
applicable surface charters (UI/API/CLI/job/library/SDK/event/migration/config);
N/A requires a reason. Use local/scratch systems only unless explicit external
authority exists. UI has a visual/a11y oracle when relevant. Findings re-enter
test-first or SPEC amendment flow.
Exit: applicable charters logged with findings resolved or blocking.

### Phase 7 — Readiness and truthful handoff

Load `references/delivery.md`. Fill PLAN evidence, review, exploration,
deviation, waiver, remaining-risk, and demo sections. Apply risk-scaled
readiness lenses.

When every required local gate is green on the frozen candidate:
1. Set SPEC `Status: Locally verified` and write matching positive State
   evidence that names the candidate digest.
2. Run `python3 <skill-dir>/scripts/validate_plan.py <SPEC> <PLAN>
   --stage delivery`. This skill is self-contained; do not require
   `feature-design` scripts.
3. If validation fails, revert SPEC to `In implementation`, keep P7 open,
   and repair. Do not remain `Locally verified` with a red delivery
   validator.
4. If validation passes and candidate hashes still match, close P7.

`--stage delivery` requires a delivery status (`Locally verified` or
higher). Running it while `In implementation` is an expected fail and is
not a reason to withhold the status change.

Higher states:
- Immutable commit + required CI/PR checks green → `Ready for integration`.
- Merge evidence → `Integrated`.
- Deployment + post-deploy verification → `Released`.

Commit/push/PR/merge/deploy only with recorded authority. Never advance a
state on a waiver that leaves an active requirement, RC, security gate, or
Critical/Important finding unresolved.

## Progressive loading

| Phase | Load |
|---|---|
| 1–2 | `references/planning.md`, `references/deviation.md`, `assets/plan.template.md` |
| 3 | `references/tdd-loop.md`, `references/deviation.md` |
| 4 | `references/verification.md`, `references/deviation.md` |
| 5 | `references/review-loop.md`, `references/deviation.md` |
| 6 | `references/exploration.md`, `references/deviation.md` |
| 7 | `references/delivery.md` |

## Never

- Weaken/delete/skip/special-case a test to manufacture green
- Review an unfrozen or partial candidate
- Mutate production files in the primary dirty workspace
- Treat the same test name as the same baseline failure without fingerprinting
- Park a real Critical/Important finding without explicit user action
- Advance integration/release status without immutable external evidence
- Touch unrelated code, or perform an unapproved commit/push/merge/deploy
