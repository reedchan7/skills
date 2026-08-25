---
name: feature-design
description: Spec-first design workflow that ends in an approved SPEC under docs/features/. Run only when the user names feature-design, or explicitly asks to design or spec a change before building it. NEVER self-select for feature requests, bug fixes, refactors, or any change the user simply wants made.
disable-model-invocation: true
---

# feature-design

Turn a raw idea into an approved, evidence-grounded SPEC whose requirements
are traceable to verification. Challenge the premise before specifying; find
facts yourself; put decisions to the user. The only terminal states are an
approved SPEC or a recorded don't-build decision.

## Activation gate — before anything else

This workflow runs only when chosen on purpose: explicit invocation (slash
command, this skill named by the user or by a standing project rule, or the
zero-active handoff from `/feature-implement`), or an explicit ask to design
or spec a change before building it. However this file came to be loaded,
verify that intent first. The test is the ask, not the task type: a bug
report, a debugging request, a refactor, or any change the user simply
wants made is not a design ask — the same task with a design-before-build
ask is. Absent that intent, say this workflow doesn't apply and handle the
request directly — no phases, no `docs/features/` artifacts, no SPEC.

## Mode routing — decide FIRST, announce with reasons

| Mode | Trigger | Run |
|---|---|---|
| Express | One reversible behavior on an existing flow, or a greenfield single-behavior spike; no new dependency, model, public contract, trust boundary, migration, authz, money, or data-lifecycle | Phases 0→1-lite→2-lite→5→6. Ask a keystone question only when a real decision remains. Skip external research and independent review. |
| Standard | A new capability in an existing product, including a bounded change on an existing security/privacy/sensitive-data surface | All phases. Phase 3 external research only for a named novelty or product-evidence question. |
| Deep | New architecture; irreversible/migration/money/multi-service work; or a new security/privacy trust boundary, authorization model, or sensitive-data lifecycle | All phases. External research and independent spec review mandatory. NFR and rollout sections mandatory. |

One-way ratchet: discoveries upgrade the mode mid-flight, never downgrade.
When in doubt between two modes, take the heavier one. Multiple independent
features in one ask → decompose first; one SPEC per feature.

## Iron laws

1. No production implementation during design. An approved throwaway
   prototype may run only in an isolated scratch workspace, is labeled
   disposable, and cannot enter the implementation branch.
2. Facts are yours to find (codebase, tools, web); decisions are the user's.
   Never ask a question you could answer by looking.
3. Evidence states its class: measured / observed / documented / inferred.
   Codebase claims cite `path:line`; external claims cite the source that
   owns them. Inference never masquerades as fact.
4. Every AC, RC, and NFR has an observable outcome and `Verify:` method.
   The mapping is auditable until a deterministic validator confirms it.
5. Ambiguity dies in design: an approved SPEC has no open questions — only
   resolved decisions and deferrals with an owner and a revisit trigger.
6. Never invent safety, privacy, compliance, retention, money, or external-
   contract defaults. Other defaults must be sourced, reversible, and
   explicitly visible at the approval gate.
7. Ceremony scales with the mode; the approval gate never does.
8. Chat is the decision medium; files are the record. Every message that
   asks the user to decide defines each open option in that same message
   with enough substance to choose — never a bare label whose meaning
   lives only in a file or an earlier message. A one-line recap is enough
   only for what the user already decided or the immediately preceding
   messages already defined in full. The user must be able to decide from
   the message alone.

## Phases

### Phase 0 — Frame, route, and create state

Capture the ask verbatim, goal, constraints, artifact destination, and write
authority. Pick the mode and allocate a collision-free `NNN`. Copy
`assets/spec.template.md` immediately to
`docs/features/<NNN>-<slug>/SPEC.md`; fill identity, `Status: Draft`,
`Assurance:` (the chosen mode), date, base revision, and raw ask. All later
write-back targets this file.
Exit: the draft exists and can be re-read. Stop: no articulable goal.

### Phase 1 — Ground the current state

Load `references/recon.md`. Read user-mentioned files first. Establish the
closest existing flow, product evidence available in-repo (analytics,
support, feedback), domain vocabulary, governing ADRs, touched seams, and
hard constraints. Express does one bounded pass; Standard/Deep map the
relevant flow end-to-end. Write findings and evidence classes into SPEC.
Exit: the keystone question can be asked without guessing about the repo.

### Phase 2 — Interrogate the premise

Load `references/interrogation.md`. Run the double-sided steelman: strongest
problem statement; strongest case FOR; strongest case AGAINST (don't build,
buy/reuse, smaller validation slice, wrong timing); name 1–3 cruxes. Ask
one keystone question only when the answer can change the design. Then ask
frontier rounds, ≤5 decisions per round, each with a recommendation. Facts
trigger lookup, never a user question. Write every answer into the existing
SPEC and append a dated decision-log entry immediately.
Exit: the decision frontier is empty or unexplored branches are owned
deferrals. Stop: user chooses don't-build → set `Status: Declined`, record
the revisit trigger, replace unneeded template placeholders with
`N/A — declined before design`, run deterministic lint
(`python3 <skill-dir>/scripts/validate_spec.py <SPEC>`), and stop successfully.

### Phase 3 — Targeted research (conditional)

Load `references/external-research.md`. Run only charters tied to unresolved
questions: problem evidence, competitor behavior, OSS prior art, engineering
practice, buy-vs-build. Separate documented claims from observed/measured
behavior. Write `RESEARCH.md`; link each recommendation to findings. If
network/access limits block a load-bearing question, label the limitation
and stop at Phase 4 unless the user accepts it.
Exit: each named research question is answered or explicitly unresolved.

### Phase 4 — Design options — STOP GATE

Produce 2–3 approaches with genuinely different value systems (minimal /
clean / pragmatic), each with trade-offs, effort, risk, rollout impact, and
falsifying evidence. Lead with one recommendation. Sketch test seams first:
existing seams preferred, highest seam possible. For material visual/state
uncertainty, offer an isolated prototype before choosing — it carries what
must be experienced; the message still defines each option. Cover data model,
public contracts, compatibility, and rollout at decision level.
Present the options in the chat message itself (iron law 8): per approach a
name, a 2–4 sentence mechanism, its main trade-off/effort/risk, and when it
wins; define every label before referencing it, then give the recommendation
with one reason, then ask. Never ask a bare "choose 1/2/3" where the
substance lives only in a file. While this gate is open, record options and
recommendation in the decision log only — do not pre-fill normative
sections with the recommended approach.
STOP for the user's choice unless continuation was pre-authorized.
Exit: one approach and its test seams are approved.

### Phase 5 — Complete the SPEC

Load `references/spec-writing.md`; fill the existing SPEC. Include product
outcome hypothesis, goals/non-goals, global constraints, AC/RC/NFR with
`Verify:`, design and testing decisions, assumptions, rollout/rollback,
deferred items, and amendment policy. Regression items cover material,
credible affected paths — not every behavior sharing a broad dependency.
Durable SPEC: no implementation file paths or code, except a
prototype-derived decision snippet. Express empty sections are one
`none` / `N/A` / `not measured` line — do not open unused NFR lenses
or invent research. Word budgets (excluding citations/log):
Express ≤800, Standard ≤2,000, Deep ≤4,000; overflow → decompose.
Exit: no placeholder or open decision remains.

### Phase 6 — Spec gate

Self-review per `references/spec-writing.md`. Standard/Deep review ladder:
fresh-context reviewer → independent user-started review → explicitly
labeled non-independent self-review. A missing independent path requires a
user waiver and remains in SPEC limitations. Fix Critical/Important
findings, updating normative sections and decision log together. Present an
inline approval digest in the chat message — goal, chosen approach, every
active AC/RC/NFR at one line each (group when the list would drown the
message; IDs stay visible), key risks and rollout, assumptions and
deferrals — then ask:

> "SPEC `<path>` version `<n>` — digest above. Approve for implementation?"

The path is for deeper reading, not a required detour: the user can approve
or reject from the message alone — unless the digest names a section that
must be read in full before approving, and says why.
On approval set `Status: Approved`, record approver/date, and hand off:
bind the approval entry to the current version + validator-produced normative
digest, rerun validation, then hand off `/feature-implement` (it discovers
this SPEC; name the path only if several actives exist).
Never begin implementation in this skill.
Exit: approved SPEC or Declined decision; no other completion claim.

## Deliverables

`SPEC.md` is the current normative truth; Git + its append-only decision log
preserve history. `RESEARCH.md` is conditional evidence, not a second spec.
Post-approval amendments update the normative section, increment
`Spec version`, append what changed/superseded and why, and require renewed
approval when behavior, scope, risk, or verification changes.

## Load references only when needed

| Condition | Load |
|---|---|
| Running Phase 1 | `references/recon.md` |
| Running Phase 2 | `references/interrogation.md` |
| Running Phase 3 | `references/external-research.md` + `assets/research.template.md` |
| Running Phase 5 or 6 | `references/spec-writing.md` + `assets/spec.template.md` |

Never load all references up front.

## Never

- Run this workflow for any ask — bug fix, debug, refactor, direct
  change — that never requested design
- Ask the user to choose among options whose substance lives only in a file
- Implement production code or let a prototype leak into the target branch
- Ask the user for a fact a lookup can answer
- Default a safety/privacy/compliance/retention/external-contract decision
- Fabricate, launder, or overstate evidence
- Approve a SPEC containing placeholders, open decisions, or unverified claims
- Skip the user approval gate or downgrade the mode mid-flight
