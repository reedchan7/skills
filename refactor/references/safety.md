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
