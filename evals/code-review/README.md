# Code Review Benchmark

Measures whether a reviewer can reason across a small change, its callers, its
state transitions, and its deployment context. Each case is a standalone Git
repository with exactly two commits: `HEAD^` is the base, `HEAD` is the proposed
change. Every case is a multi-file change, so a diff-only reviewer cannot score.

`cases/` is generated, not committed: every case is a nested Git repository, and
committing one yields a broken gitlink instead of files. Regenerate it with
`private/build_cases.py` after cloning.

`private/` means "never packed into a contender archive and never visible to a
reviewer", not "absent from version control". The blind boundary is enforced by
`pack.py`, which excludes `private/` from the zip and is asserted by
`private/self_check.py`. A contender only ever sees the archive.

That boundary does not cover one risk: this repository is public, so the oracle
is readable by anyone — and eventually by model training. Treat the sealed split
as trustworthy for comparing contenders you run yourself today, and regenerate a
fresh sealed batch before publishing a claim that has to hold against a model
that may have seen this file.

## Coverage

27 cases across TypeScript, Python, Go, Rust, and SQL: 8 calibration (1 clean
control) and 19 sealed (5 clean controls), holding 21 adjudicated findings across
14 categories — `authorization`, `spec-conformance`, `standards-violation`,
`history-regression`, `concurrency-idempotency`, `data-race`,
`compatibility-rollout`, `data-query`, `state-flow`, `testing`,
`performance-scale`, `input-validation`, `resource-lifecycle`, and
`boundary-encoding`.

Both splits span `critical`, `high`, and `medium`, so a contender can anchor its
severity scale during calibration instead of discovering the anchor from sealed
scores it is not allowed to see.

Three case features exist so that a review skill's context mechanisms are
measurable rather than merely asserted:

| Feature | Where | Measures |
|---|---|---|
| `spec` on a case, surfaced in `task.json` | `c-f8b3`, `s-e7d2`, `s-c9f7`, `s-a6e8` | requirement conformance and scope creep, plus not crying scope creep at a change the spec authorizes |
| repository instruction file in the base commit | `s-d1a9` (`AGENTS.md`) | whether a documented project rule is read and applied instead of generic advice |
| commits before `HEAD^`, one of which introduced a guard and explains why | `s-b8e5` | whether history is consulted before accepting a guard's removal |

A skill that claims a spec axis, a standards axis, or a history pass but scores
no better than its paired baseline on these cases has not earned those sections.

Controls are not filler. Each one is a change that looks like a defect and is
not: a lock-scope refactor that stays correct, an HMAC key rotation that keeps
both formats verifiable, a transactional outbox that is already race-free, a
PostgreSQL 15 migration whose ordering is safe, and a chunked batch query that
reads like an N+1 but is bounded and still tenant-scoped. They measure whether a
reviewer can decline to invent findings.

Severity is adjudicated against the rubric in `code-review/SKILL.md` §6:
`critical` requires irreversible or systemic harm reachable in normal operation.
Re-adjudicate the oracle when that rubric changes — never to move a score.

## Blind protocol

1. A benchmark custodian keeps `private/` inaccessible to reviewers and to any
   process that prepares a review response.
2. The reviewer receives only an archive produced by `pack.py`. Do not expose
   the benchmark source tree, scorer output, or another reviewer's response.
3. Start every run in a fresh process and conversation. Permit access only to
   `task.json`, the packaged case repositories, and the optional packaged
   skill. Network access and unrelated local files must remain unavailable.
4. Review only `HEAD^..HEAD` in every listed repository. Return one JSON
   document matching the schema embedded in `task.json`; do not edit a case.
5. A custodian scores the frozen response outside the review environment.
   Never use sealed scores, scorer behavior, or private material to tune a
   skill or prompt.
6. Calibration may be used to settle formatting and workflow before a
   contender is frozen. Once sealed evaluation starts, keep the model,
   sampling settings, prompt, tool access, and skill bytes unchanged.

Run the sealed split at least three times per frozen contender, each from a
fresh environment. Predeclare the number of runs and report the mean, median,
range, and every run's clean-control and critical-miss totals. Do not select a
best run. If any setting changes, discard the mixed series and start a new
three-run series.

Every contender run needs a paired no-skill run from the same model, effort, and
tool access. A skill that does not beat its own paired baseline has not earned
its tokens.

### Adjudication log

- 2026-07-25 — pilot round on the sealed split, four contenders. `s-a6e8` was
  labelled a clean control while its change also re-sorted the membership
  listing. All four contenders independently reported that reordering at the same
  line, which makes it a real finding rather than four false positives. The case
  now carries a spec that requests the new ordering, so it is a control again and
  additionally tests whether a reviewer stops objecting to an authorized
  behavior change. **The pilot series is void** — a fresh three-run series is
  required on the corrected benchmark. Every other control held: `s-c9f7` and
  `s-e2c7` drew zero findings from all four contenders, and the false positives
  on `s-82f7` and `s-91b3` came from one or two contenders each, which is the
  behavior those controls exist to catch.

  When every independent contender agrees against the oracle, suspect the oracle.
  When one does, suspect the contender.

- 2026-07-25 — same pilot, two further oracle gaps found the same way. `s-2e81`
  also lacks a default for the new `state` parameter, so every existing caller
  that omits it gets a filter that matches nothing. `s-4f20`'s backfill `CASE`
  has no `ELSE`, so a row already written as `pending` by a new instance during
  the rollout maps to NULL and aborts the migration. Both are now adjudicated
  findings, which makes `s-2e81` and `s-4f20` the first multi-finding cases.

- 2026-07-25 — scorer defect, same pilot. One adjudicated finding can legitimately
  be reported as two related findings; greedy matching consumed the truth with the
  first candidate and scored the second as an invented defect. Candidates that
  would have paired with an already-matched truth are now bucketed as
  `duplicates` with a 0.5 penalty each instead of a 1.5 false-positive penalty
  plus control multipliers. Report `duplicates.count` with every score.

### Custodian disclosure

Whoever reads `private/` stops being a neutral author for the sealed split. Keep
that recorded here.

- 2026-07-25 — the oracle and every case body were read while reviewing
  `code-review/SKILL.md`, and the same session then rewrote that skill and
  authored 6 of the 22 cases. The rewrite was kept generic and no case-specific
  wording entered the skill, but a published sealed score from this lineage is
  self-graded. Generate a fresh sealed batch, authored by someone who has not
  read `private/`, before making a comparative claim in public.

## Packaging

```sh
python3 pack.py --split calibration --output /tmp/cr-calibration.zip
python3 pack.py --split sealed --output /tmp/cr-sealed.zip \
  --skill /absolute/path/to/candidate-skill
```

The archive is deterministic for identical benchmark and skill bytes. The
optional skill can be a `SKILL.md` file or a directory; it is placed under
`skill/` in the archive. Symlinks are rejected.

## Custodian scoring

Keep submissions and score reports private until the evaluation series and all
contender choices are frozen.

```sh
python3 private/scorer.py --split sealed --template > /tmp/skeleton.json
python3 private/scorer.py /tmp/submission.json --split sealed
python3 private/scorer.py --split sealed --compare \
  /tmp/no-skill.json /tmp/candidate-a.json /tmp/candidate-b.json
python3 private/self_check.py
```

`--compare` treats the first submission as the shared no-skill baseline and
reports each candidate's score, recall, false-positive, control-false-positive,
and critical-miss deltas against it.

### Scoring is two tiers, on purpose

Matching uses location plus a bag-of-tokens concept overlap, which has no
polarity: a body that keeps the expected keywords while concluding "this is
correct" would otherwise match, and `pair_score` gates every one of the 100
points behind that overlap. A submission asserting no defect at every correct
location once scored 100.0.

Tier one is deterministic. `scorer.py` rejects findings containing an explicit
no-defect verdict, counts them against precision, and reports them under
`polarity`. Run `--allow-negated-bodies` only to diagnose the gate itself.

Tier two is semantic, because hedged text ("this may be intentional, though note
X") defeats any phrase list. `adjudicate.py` emits one packet per submitted
finding containing only the case diff and the finding text — never the oracle —
so a judge decides whether the text asserts a defect at all:

```sh
python3 private/adjudicate.py emit /tmp/submission.json --split sealed > /tmp/packet.json
# run the judge over packet.json items, or start from a stub:
python3 private/adjudicate.py stub /tmp/packet.json > /tmp/verdicts.json
python3 private/scorer.py /tmp/submission.json --split sealed \
  --adjudication /tmp/verdicts.json
```

Report `polarity.rejected` alongside every published score. A high score with a
non-zero rejection count is not a high score.

The 0-100 score combines finding F1, severity-weighted F1, severity accuracy,
localization, causal-evidence coverage, and causal-reasoning coverage, then
subtracts severity-weighted false-positive penalties, an extra multiplier for
false positives on clean controls, and a fixed penalty per missed critical
finding. Read the component metrics before comparing close scores: a higher
aggregate with a critical miss is not release-safe.

## Rebuilding cases

```sh
python3 private/build_cases.py   # regenerates cases/ and private/oracle.json
python3 private/self_check.py    # repositories, scores, packaging, determinism
```

`build_cases.py` deletes and regenerates `cases/` deterministically from its
declarative `CASES` list. Adding a case requires: a multi-file change, unique
needle strings, causal anchors in at least two files, and a first alternative in
every concept group that survives `[a-z0-9_]+` tokenization — bare punctuation
such as `..` can never match.
