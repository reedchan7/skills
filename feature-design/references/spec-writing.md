# SPEC writing: current truth, verifiable requirements, safe amendments

Load for Phases 5–6. The SPEC is the normative product/behavior contract.
Implementation detail belongs in PLAN; evidence depth belongs in RESEARCH.

## Product outcome hypothesis

Behavioral acceptance is not product success. Standard/Deep SPECs state:

- Target actor and problem evidence.
- Baseline (measured value, or `not measured`).
- Expected outcome and target.
- Measurement method/window.
- Decision rule: expand / revise / retire.

Express may use one sentence or `not measured — behavior-only change`.

## Global constraints

One canonical section lists exact rules every implementation slice inherits:
version/platform floors, allowed/forbidden dependencies, compatibility,
security/privacy/compliance constraints, naming/copy rules, no-touch zones,
and rollout restrictions. Values are sourced or explicitly user-approved.

## Acceptance criteria — constrained grammar

Every active requirement has one stable ID, one behavior, and `Verify:`:

| ID | Shape | Template |
|---|---|---|
| AC | Event | WHEN `<trigger>` THE SYSTEM SHALL `<observable response>` |
| AC | State | WHILE `<state>` THE SYSTEM SHALL `<behavior>` |
| AC | Unwanted | IF `<error/abuse condition>` THEN THE SYSTEM SHALL `<safe response>` |
| AC | Ubiquitous | THE SYSTEM SHALL `<always-on invariant>` |
| AC | Optional | WHERE `<flag/tier exists>` THE SYSTEM SHALL `<behavior>` |
| RC | Preserved behavior | THE SYSTEM SHALL CONTINUE TO `<material existing behavior>` WHEN `<interaction>` |
| NFR | Quality constraint | Under `<measurement condition>`, THE SYSTEM SHALL `<quantified result>` |

`Verify:` is one of:

- `test` — automated behavior check at a named seam.
- `command` — exact command + expected result and environment.
- `probe` — scripted/manual steps + expected observation; only when
  automation genuinely cannot settle the criterion.

The mapping is mechanically lintable, not proof by itself. Phase 6 runs this
skill's `scripts/validate_spec.py`; feature-implement later supplies execution
evidence.

### Quantify or expose uncertainty

Replace vague quality words with a target and measurement condition. Never
invent a number. If no safe value can be sourced or approved, use
`not yet measured`, make the criterion a decision or owned deferral, and do
not approve it as satisfied.

## Regression contract — bounded by credible impact

Include existing behavior only when recon shows a credible causal path from
the feature's touched seam/state/data to that behavior and the impact clears
the feature's risk threshold. Prefer a stable central regression suite over
enumerating every behavior behind a shared database, auth layer, or event bus.

Each RC has `Verify:` and an affected consumer class. `No material RC known`
is legal when recon states where it looked and its blind spots. RCs may be
added, changed, or retired only through the amendment protocol.

## NFR menu — conditional, not boilerplate

Open only relevant lenses; Deep sweeps all:

Performance · security/authz/abuse · privacy/compliance/retention ·
accessibility · i18n/time · reliability/idempotency · observability ·
compatibility/mixed versions · capacity/resource bounds.

Every included NFR is quantified or explicitly unresolved; every active NFR
has `Verify:`.

## Design, release, and testing decisions

- Chosen approach, rejected alternatives, and falsifying evidence.
- Interfaces/data/state at decision level — no implementation file paths.
- Testing seams: highest behavior seam that exercises each requirement.
- Rollout/rollback for medium/high risk: flag/default, deployment order,
  migration phases, observability, kill switch, rollback or forward-fix
  boundary.
- Outcome measurement after release.

Prototype-derived state/schema snippets are allowed only when they encode a
decision more precisely than prose; mark the source and keep them minimal.

## Amendment protocol — current body + append-only history

Post-approval change:

1. Update the normative section so the SPEC describes the intended current
   behavior.
2. Increment `Spec version`.
3. Append a decision-log row: old meaning, new meaning, why, approver, and
   affected AC/RC/NFR/slices/tests.
4. Mark retired IDs `Superseded by <ID/version>` in the log; never silently
   reuse an ID for unrelated behavior.
5. Return `Status: Draft` when behavior, scope, risk, or verification changed;
   rerun lint/review and regain approval before implementation continues.

Git preserves old bytes; the normative body never stays knowingly stale.
Lifecycle-only status changes do not alter the normative digest.

## Checkable size budgets

Exclude citations and decision log:

- Express: ≤800 words, normally 3–7 active requirements.
- Standard: ≤2,000 words.
- Deep: ≤4,000 words.

Over budget → cut narrative first. Requirement overflow → decompose into
separate SPECs with explicit dependencies.

## Self-review and lint

1. Placeholder scan: TBD/TODO/unfilled template slots.
2. Internal consistency and glossary terminology.
3. Scope fits one implementation plan.
4. Every AC/RC/NFR has trigger/condition, observable outcome, and `Verify:`.
5. Every probe has exact steps and expected result.
6. Global constraints are sourced/approved and contain no unsafe default.
7. Against-case risks are addressed, accepted, or owned deferrals.
8. Outcome hypothesis distinguishes behavior from product value.
9. Rollout matches migration/compatibility risk.
10. Run `python3 <skill-dir>/scripts/validate_spec.py <SPEC> --json` while
    Draft; read `normative_digest`, bind the approval log to that exact version
    and digest, set Approved, then rerun. Any normative edit changes the digest
    and invalidates the approval.

Fix every deterministic lint failure before review.

## Adversarial review (Standard/Deep)

Provide SPEC + RESEARCH (if any) to a context that did not author them:

```text
Review this SPEC as the engineer and operator accountable for it.
Report only:
1. two-way ambiguities, quoting both readings
2. AC/RC/NFR whose Verify can pass while intent fails
3. missing error, limit, concurrency, permission, migration, or rollback cases
4. regression items without a credible causal path, and credible paths omitted
5. contradictions, unsafe defaults, and scope too large for one plan
6. strongest evidence-backed case not to build this version
Rank Blocking / Important / Minor and cite SPEC sections.
```

Fix Blocking/Important findings in the normative body and decision log.
Rejected findings need a falsifiable disproof. One scoped re-check follows.
When no independent context exists, follow the capability ladder in SKILL.md
and disclose that limitation; never describe self-review as independent.
