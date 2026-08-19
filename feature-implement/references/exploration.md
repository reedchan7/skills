# Exploratory verification: risk-selected charters with real oracles

Load for Phase 6. Exploration hunts behavior not anticipated by scripted
checks. It is conditional on surface and risk; N/A is legal with a reason.

## Safety boundary

- Use local, isolated, disposable data/services by default.
- Never probe production or shared environments, send external messages,
  alter real user data, exhaust shared resources, or kill dependencies without
  explicit authority and a cleanup plan.
- Cap generated load and clean it up. “10× realistic” is not a license for an
  unbounded stress test.

## Method

1. Select applicable surface and cross-cutting charters from the blast-radius
   ledger.
2. State the oracle before the probe: expected behavior, reference/contract,
   and failure signal.
3. Exercise the highest real seam in a sandbox.
4. Log action → observation → verdict → evidence.
5. Finding: add a regression test and fix, or follow SPEC deviation.

Cannot boot is Critical only when the approved feature promises a runnable
surface and the expected run command fails. Libraries/config/migrations use
their own seams.

## Surface charters

| Surface | Representative probes |
|---|---|
| HTTP/API | missing/wrong/oversized input; duplicate request; authn/authz/tenant boundary; pagination limits; concurrent mutation; stable error shape/no leakage |
| UI/mobile | double action; back/refresh/deep link; empty/overflow; slow/offline; stale session; keyboard/focus/semantics/contrast; localization/time; responsive states |
| CLI | no/unknown/conflicting args; stdin/encoding/large input; exit codes; interruption/cleanup; idempotent rerun |
| Job/worker/event | empty/poison/duplicate/out-of-order event; crash/restart; retry/backoff; partial failure; clock skew |
| Library/SDK | public API contract; type/runtime errors; cancellation; resource cleanup; version compatibility; examples compile/run |
| Migration/data | forward on representative disposable data; resumable rerun; reconciliation counts/checksums; mixed-version compatibility; rollback/forward-fix drill |
| Config/flag | absent/invalid/deprecated values; default; live/restart semantics; flag off/on; secret redaction |

## Cross-cutting charters

Boundaries · error recovery · state transitions · concurrency/idempotency ·
permissions/tenant isolation · Unicode/RTL/time zones/DST · bounded resources ·
mixed versions · observability.

Open only those with a credible path from the feature.

## UI visual and accessibility oracle

When visual behavior matters, record:

- Approved reference (design/prototype/existing canonical component).
- Viewport/browser/theme matrix relevant to SPEC.
- Screenshot or visual-diff result with threshold; otherwise explicit user
  visual approval.
- Keyboard order, visible focus, semantic roles/names, contrast, zoom/reflow,
  and reduced-motion checks as applicable.
- Console errors and failed network requests.

A screenshot without a reference/verdict proves only that a page opened.

## Time budget

Express: 5–10 minutes on the changed surface. Standard: 15–30 minutes on
selected charters. Deep: risk-based, with each charter bounded by PLAN.
Stop when the charter's uncertainty is settled, not when a generic timer ends.

## Log

```markdown
| Charter / oracle | Probe | Observation / evidence | Verdict |
|---|---|---|---|
| <expected + source> | <action> | <result> | ok / finding / N/A + reason |
```

Record selected, skipped, and not-assessed charters. An empty log is not a
completed phase.
