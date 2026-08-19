# Readiness and delivery: evidence-bound states

Load for Phase 7. “Production-ready” is a set of passed gates on an immutable
candidate, not a tone of confidence.

## Deterministic artifact gate

This skill is self-contained. Do not look for `feature-design` scripts.

`--stage delivery` requires SPEC status to already be a delivery state
(`Locally verified` or higher). Running it while `In implementation` is an
expected fail and does not mean local gates are incomplete.

Order:

1. When local gates (requirements, review, exploration, housekeeping) are
   green, set SPEC `Status: Locally verified` and write positive State
   evidence that names the candidate digest.
2. Then run:

```sh
python3 <feature-implement-skill-dir>/scripts/validate_plan.py \
  <SPEC> <PLAN> --stage delivery
```

3. Validator failure reverts SPEC to `In implementation` and keeps P7 open.
4. Validator pass plus unchanged candidate hashes closes P7.

## Readiness lenses — open by risk

| Lens | Required when | Gate |
|---|---|---|
| Failure/recovery | all | unwanted/error ACs verified; failures visible and recoverable |
| Docs/demo | consumer-facing | usage/API/run path updated where users look; clean-checkout demo executed |
| Config/flags | config or staged rollout | defaults/invalid values/secret handling verified; flag owner and removal trigger |
| Observability | operational behavior or medium/high risk | named logs/metrics/traces show success and failure; thresholds/owner stated |
| Security/privacy | identity, untrusted input, secrets, money, PII | authz/tenant/input/abuse/data lifecycle reviewed and tested |
| Performance/capacity | critical or multiplicative path | measured environment, load, noise, threshold, bounded resources |
| Accessibility/visual | UI/mobile | reference/viewport/browser/a11y oracle closed |
| Compatibility/migration | persisted data or external/public contract | multi-version matrix and staged release gates below |
| Housekeeping | all | no debug/test hacks/stray task TODOs; generated artifacts intentional |

N/A includes a reason. A failed active requirement, RC, security/privacy gate,
or real Critical/Important review finding cannot be waived into readiness.

## Multi-release migration gate

Schema/data/API/event compatibility uses separate releasable stages:

1. **Expand:** additive surface; old and new application versions both work.
2. **Backfill:** resumable/idempotent batches with progress, lock budget, and
   reconciliation (counts + checksums or domain equivalent).
3. **Cutover:** consumer compatibility matrix closed; dual-read/write policy,
   ordering, retries, and observability verified.
4. **Contract:** destructive removal only after deployed telemetry proves zero
   old consumers and rollback/forward-fix policy is approved.

Each stage owns a dependent SPEC/PLAN and closes its own Phases 3→7. The next
stage cannot become Approved until the previous stage's external prerequisite
is evidenced. One PLAN never marks expand and contract locally complete
together.

## Delivery report

Assemble from recorded evidence, never memory:

1. Candidate identity: SPEC version/digest, commit/tree or content manifest.
2. AC/RC/NFR evidence table: method, command/probe, result, candidate, time.
3. Baseline/CI/full-suite status and coverage limits.
4. Review: rounds, independence, fixed/disproved/open counts and severity.
5. Exploration: selected/N/A/not-assessed charters and findings.
6. Mutations: selected risks, caught/survived, isolated restoration digest.
7. Deviations/amendments/test migrations.
8. Waivers: owner, exact gate, consequence; waivers never imply green.
9. Remaining risk and Noticed-not-touched.
10. Clean-checkout demo/reproduction steps.

## State transitions

- `Locally verified`: all required local checks, requirements, review, and
  exploration closed on frozen candidate.
- `Ready for integration`: immutable commit exists and required remote CI/PR
  checks are green.
- `Integrated`: merge/integration evidence exists; post-merge required checks
  are green.
- `Released`: deployment evidence and post-deploy smoke/observability checks
  exist.

Do not advance beyond available authority/evidence. A user may accept an
experimental handoff with open risk; keep status `In implementation` and say
exactly what remains.

## Git/external actions

Commit only when Phase-0 commit authority is `yes`, following `git-commit`.
Push/PR/merge/deploy each require their own grant. Re-run the relevant gate
after merge/deploy before advancing state.

## Final message

Report facts, not a fixed success sentence:

```text
State: <In implementation | Locally verified | Ready for integration |
        Integrated | Released>
Requirements: <verified>/<active>; unresolved: <ids>
Review: fixed <n>, disproved <n>, open <n>
Exploration: selected <n>, N/A <n>, not assessed <n>, findings <n>
Waivers / remaining risk: <explicit>
Evidence: <PLAN path> @ <candidate identity>
Next authorized action: <action or none>
```
