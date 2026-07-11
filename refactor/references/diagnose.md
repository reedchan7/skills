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
