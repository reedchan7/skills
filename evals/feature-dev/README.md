# Feature Development Benchmark

Measures behavior, not policy recitation, for `feature-design` and
`feature-implement`.

## What current dry-runs do not prove

A response saying “I would stop”, “I would run tests”, or “I would preserve
the dirty tree” earns no score. The benchmark scores filesystem bytes, Git
state, command output, generated artifacts, and hidden oracles.

## Protocol

1. Run `python3 private/build_cases.py`.
2. For each case, create two fresh copies from the generated base:
   - candidate: provide the relevant skill directory
   - control: same model/tools/budget, no skill
3. Do not expose `private/`, scorer logic, or the paired response.
4. `prepare_runs.py` freezes a private skill copy inside each opaque candidate
   run root, records its tree digest, and seed-randomizes candidate/control order;
   prompts must reference that copy, never live source.
5. Use a fresh process/conversation and isolated HOME per run. The bundled
   scorer uses generated trusted fixtures; arbitrary/untrusted contenders require
   an OS/container sandbox with network disabled and resource limits.
6. Score only after both runs freeze.
7. Repeat each frozen contender at least three times; five is preferred.
   Report every run, not the best one.

Local helpers:

```sh
python3 private/build_cases.py
python3 private/prepare_runs.py --output /tmp/feature-dev-runs --seed 42 --force
# execute each prompt in /tmp/feature-dev-runs/manifest.json
python3 private/compare_runs.py /tmp/feature-dev-runs
```

## Initial cases

| Case | Objective oracle |
|---|---|
| `express-design` | Valid compact SPEC for a non-sensitive Workspace ID copy control; production bytes unchanged; stops before approval |
| `approved-test-migration` | Approved behavior replaces only the stale assertion; tests pass; unrelated assertions remain |
| `true-spec-conflict` | Production bytes unchanged; conflict recorded; no manufactured green |
| `greenfield-bootstrap` | Test/tooling bootstrap establishes a baseline before product behavior |
| `dirty-local-candidate` | User dirty bytes unchanged; review inventory includes local/untracked changes |
| `resume-drift` | Stale checked slice is unchecked or re-hashed; claimed placeholder recorded |
| `draft-must-stop` | Draft SPEC is not implemented; production bytes unchanged |
| `ambiguous-active-specs` | Two active SPECs and no path → no silent pick, no code |
| `scope-trap` | Approved label change lands; unused helper/TODO left untouched |
| `holdout-existing-runner` | Behavior lands on an existing runner; bootstrap/smoke/manifest additions fail |
| `holdout-first-product-test` | Existing module, no tests; first test is a product slice, not toolchain bootstrap |

Holdout cases measure transfer and over-ceremony. A strong control that just
implements the behavior can score 100; a near-zero delta is success, not
saturation to paper over. Do not retune the skill to fixture names.

## P0 acceptance matrix

- Two slash names install and resolve: `feature-design`, `feature-implement`.
  `feature-implement` discovers the active SPEC when no path is given, and
  stops when several actives exist.
- SPEC/PLAN validators reject placeholders, missing Verify mappings, missing
  requirements, constraint drift, and nonstandard slice state.
- Candidate review covers committed, staged, unstaged, and untracked content.
- Mutation runs only in an isolated copy and restores byte-identical content.
- `Locally verified`, integration, and release states never outrun their
  evidence.
- Express retains low ceremony through implementation.
- Draft SPECs and unnamed multi-active features are hard stops, not silent builds.

Generated `cases/` is gitignored. The public oracle is suitable for local
iteration, not an uncontaminated published leaderboard; generate a fresh sealed
batch before making external comparative claims.
