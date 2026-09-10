# Refactor evaluation

This evaluation separates behavior preservation, useful structural change,
and the cost of a subsequent maintenance task. It is not a checklist of
phrases a model should repeat, a cyclomatic-score contest, or a universal
refactoring-quality score.

The skill is installed from `skills/refactor`; this directory is never part
of a runtime skill. Once a fixture and its oracle are disclosed, it is a
known regression case, not fresh evidence of generalization.

## Comparison design

Freeze candidate/baseline skill contents, public input repositories, private
runtime probes, semantic rubric and acceptance criteria before running agents.
Use anonymous arms for no skill, the prior skill and the candidate; the grader
must not receive the mapping or read the skills. Keep model, effort, tools,
task wording, runtime and input versions aligned; record unavoidable differences.

Give each execution session only its own raw task, repository copy and skill
if applicable. Include existing dirty and untracked state. Have it actually
perform the request and retain its final code, tests and report. Do not tell
it the expected transformation or private assertions. Use fresh sessions for
repeats; do not selectively rerun only a failed arm and report the best result.

Independent case authors should use public contracts that make every private
behavior expectation legitimate. Verify original behavior and deliberately
broken variants before sealing. Quality rubrics must accept multiple coherent
designs and justified restraint, while distinguishing a no-op from completion
of a request that really needs a change.

## Outcomes

Report these separately:

- Contract status: pass, minor failure, major failure, or incomplete. Record
  ownership/authorization violations independently; good structure cannot
  compensate for lost user work or weakened security.
- Usefulness: 0–4, based on the actual user's maintenance problem.
- Cohesion, change locality, proportionality and understandability: each
  0–3, based on final code and representative consumers. File/function counts
  and reported metrics do not mechanically determine these scores.
- Held-out maintenance: after freezing the refactor output, give a fresh
  executor the same new requirement on each output. It receives no initial
  skill or designer's explanation. Compare new and original contracts, then
  independent policy changes, collateral edits and parameter/coordination
  burden. Keep these artifacts separate from the refactor deliverable.

Average repetitions per case first, then cases equally. Preserve per-case
results and repeat variation; report the no-skill comparison even if it ties
or beats the candidate. Explain any ambiguity for all arms consistently and
retain sensitivity results if an expectation cannot be justified publicly.
Do not infer significance or industrial productivity from a small fixture set.

Agent self-reports are not proof of execution: run public/private checks on
the frozen output and inspect actual changes. Structural grading remains a
semantic judgment; a deterministic results serializer is not an autonomous
quality scorer. Token counts, wall time and human effort are different measures.

## 2026-09-07 series

Six independently authored repositories, three arms, two repeats: 36 initial
refactoring artifacts. Two held-out maintenance task types are applied to all
arms/repeats: 12 subsequent artifacts. Initial and maintenance code are frozen
separately. The source author did not read private case expectations while
writing the candidate.

Predeclared acceptance: no new major contract or safety/ownership failures and
no increase in unjustified incompletion. A measured quality uplift requires
either a structural macro-mean gain of at least 0.3 on the 0–3 scale versus
the prior skill with gains on at least two independent cases, or better
maintenance locality on both held-out task types without original/new contract
regressions. The no-skill comparison and limitations remain visible regardless.

See [research and results](../../docs/research/refactor-2026-09-07.md) for the
actual outcome, reproducible material and interpretation. Raw runs are stored
under `runs/2026-09-07/`, which the repository intentionally gitignores.

The observed result did **not** meet the quality-uplift gate: candidate and
prior-skill structural means and both maintenance-locality results tied.
All 48 artifacts passed the frozen suites. One no-skill credentials result
had a separately reproduced adapter-aliasing regression under the broader
injected-service contract interpretation; the narrower nonmutating-adapter
interpretation makes all arms tie. See the research report for sensitivity.

## Reproduce the fixtures

Python 3.9+ and Git are sufficient; no external packages or network are needed:

```sh
python3 evals/refactor/private/build_cases.py
python3 evals/refactor/private/self_check.py
```

The generator refuses existing output directories. Self-check runs original
contracts, six seeded faults, and two held-out negative/positive controls in
new disposable copies. See [running instructions](RUNNING.md) for explicit
output paths, per-case probes and the blind-execution boundary.

The tracked [manifest](results/2026-09-07-manifest.json) contains arm mapping,
skill hashes, archive hashes and gate outcome. The [primary grading](results/2026-09-07.json)
and [independent crosscheck](results/2026-09-07-crosscheck.json) retain per-case
evidence. Relative log paths in the primary JSON resolve from local
`runs/2026-09-07/primary-grading/`; original source paths are recoverable from
the named initial/maintenance archives. Raw archives are local and will not
be included in a normal Git commit. Rerunning agents is a new observation,
not guaranteed reproduction of their original output or a fresh held-out test.
