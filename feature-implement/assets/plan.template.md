# PLAN template (canonical)

Copy between markers in Phase 0. Replace every placeholder. PLAN is pinned
execution state; exact paths/commands/checkpoints belong here, not in SPEC.

<!-- TEMPLATE START -->

# Plan — Feature NNN <title>

- SPEC: ./SPEC.md · version: <n> · normative digest: <sha256>
- Assurance: express | standard | deep
- Base revision: <sha> · Branch/worktree: <name/path>
- Candidate mode: commits | local-content-manifest
- Authority: edit <yes/no> · commit <yes/no> · branch <yes/no> ·
  push <yes/no> · PR <yes/no> · merge <yes/no> · deploy <yes/no>
- Created: <date> · Current phase: 1

## Workflow gates

- [ ] P1 Baseline and blast radius established
- [ ] P2 PLAN validated and required gate approved/inherited
- [ ] P3 All slices checkpointed
- [ ] P4 Integration/requirement/sensitivity evidence closed
- [ ] P5 Review closed with no real Critical/Important open
- [ ] P6 Applicable exploratory charters closed
- [ ] P7 Readiness report validated

## Candidate and unrelated-work inventory

| Path/state | SHA-256 / identity | Owner | Must remain unchanged? |
|---|---|---|---|
| <path or HEAD/index/worktree> | <digest> | task / user | yes/no |

## Global constraints (verbatim from SPEC)

- <exact rule>

## Conventions inventory

- Affected tests: `<cmd>` · Full tests/CI: `<cmd or remote gate>`
- Lint: `<cmd>` · Typecheck: `<cmd>` · Build: `<cmd>` · Run: `<cmd>`
- Structure/naming/idioms: <finding — path:line>
- Governing instructions/owners: <path:line>

## Baseline failure ledger

| Command | Exit | Test/check | Normalized fingerprint | Status/note |
|---|---:|---|---|---|
| `<cmd>` | <n> | <name> | <error type + stable message/stack> | known-red / flaky / clean / unavailable |

## Blast-radius coverage ledger

| Surface / consumer class | Causal path | Requirement/check | State | Limitation |
|---|---|---|---|---|
| <surface> | <entry → state/data → effect> | RC/NFR/suite | covered / no material risk / not assessed | <reason> |

## Approved test migrations

| Existing test | Active requirement superseding old assertion | Narrow change |
|---|---|---|
| <path::name> | AC/RC-### | <assertion only; unrelated checks retained> |

## Slices

- [ ] **S0 — Bootstrap** *(keep only when pickup had no test runner; otherwise delete this slice)*
  - Covers: none — toolchain only
  - Blocked by: none · Risk: low — runner proof only
  - Files: create `<smoke test>`; create `<manifest>` only if deps will be declared
  - Interfaces: produces `<test command>`; consumes none
  - Oracle order: smoke RED then GREEN; no product AC
  - Approved test migrations: none
  - Affected verify: `<test command>` → runner works
  - Manual/scripted probe: N/A — runner proof only
  - Rollback: delete bootstrap files
  - Checkpoint: <sorted path:digest manifest>
  - Evidence: <commands, exits/results, candidate digest, timestamp>

- [ ] **S1 — <end-to-end behavior>**
  - Covers: AC-001, RC-001, NFR-001
  - Blocked by: S0 when present · Risk: <low/medium/high + mechanism>
  - Files: create `<path>`; modify `<path>`; test `<path>`
  - Interfaces: produces `<exact signature>`; consumes `<exact signature>`
  - Oracle order: <one behavior case at a time>
  - Approved test migrations: <ids or none>
  - Affected verify: `<cmd>` → <expected>
  - Manual/scripted probe: <exact steps or N/A + reason>
  - Rollback: <trigger + procedure>
  - Checkpoint: <commit/tree SHA OR sorted path:digest manifest>
  - Evidence: <commands, exits/results, candidate digest, timestamp>

- [ ] **S2 — <behavior>**
  - Covers: <ids>
  - Blocked by: S1
  - <same fields as S1>

## Coverage matrix

| Active AC/RC/NFR | Slice(s) | Final Verify method |
|---|---|---|
| AC-001 | S1 | test — `<cmd>` |

Every active requirement appears; every non-bootstrap slice maps to one.

## Deviations and amendments

| ID/date | Level | Expected / found / impact | Resolution and approval |
|---|---|---|---|
| D-001 <date> | code / PLAN / SPEC | <evidence> | <action; SPEC version if amended> |

## Noticed, not touched

- <thing — location — why out of scope>

## Review log

| Round | Candidate digest | Independent? | Findings C/I/M | Fixed / disproved / open | Verdict |
|---|---|---|---|---|---|
| 1 | <digest> | yes/no | 0/0/0 | 0/0/0 | <spec + engineering> |

## Delivery report

### Requirement evidence

| AC/RC/NFR | Verify method | Command/probe + result | Candidate | Time |
|---|---|---|---|---|
| AC-001 | test | `<cmd>` → pass | <digest> | <date/time> |

### CI / full-suite / coverage limits

- <gate → status/evidence>

### Mutation/sensitivity *(selected by risk)*

| Requirement/risk | Mutation | Caught by | Isolated restore digest |
|---|---|---|---|
| <id> | <mutation or N/A + reason> | <test> | <digest> |

### Exploration

| Charter/oracle | Probe | Observation/evidence | Verdict |
|---|---|---|---|
| <surface> | <action> | <result> | ok / finding / N/A + reason |

### Waivers, open work, and remaining risk

- <owner · exact gate · consequence · status impact>

### Clean-checkout demo

1. `<command>` → <expected observation>

### State evidence

- Locally verified: <candidate + local gates>
- Ready for integration: <commit + CI/PR>
- Integrated: <merge + post-merge checks>
- Released: <deployment + post-deploy checks>

<!-- TEMPLATE END -->
