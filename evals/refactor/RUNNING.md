# Offline refactor behavioral fixtures

This portable bundle contains the six original, pre-frozen offline repositories,
public refactoring requests, private runtime checks, and semantic grading rubric.
It requires Python 3.9+ and Git for the harness, with no external packages or
network access. The legacy report production fixture itself targets Python 3.8.

## Build public inputs

From the repository root after copying this directory to `evals/refactor`:

```sh
python3 evals/refactor/private/build_cases.py
```

The default creates `evals/refactor/cases/`, which is ignored by the adjacent
`.gitignore`. Choose a new external output path for isolated evaluations:

```sh
python3 evals/refactor/private/build_cases.py --output /tmp/refactor-cases-new
```

An existing output path is always refused. Use a fresh path or explicitly remove
your own disposable previous output before rebuilding. The generator never
cleans an existing worktree. `legacy_report` deliberately includes a tracked
dirty document and an untracked operator scratch file.

Each generated case has `TASK.md` and a `repo/` local Git repository. Give an arm
only its task and a complete fresh repository copy, including `.git` and dirty
files. Do not expose this private directory, other arms, or follow-up requirements
during initial refactoring. Run public tests from a repository using:

```sh
python3 -m unittest -v
```

## Run private probes on disposable output copies

```sh
python3 evals/refactor/private/probe.py ledger /tmp/arm-copy/ledger/repo
python3 evals/refactor/private/probe.py dispatch /tmp/arm-copy/dispatch/repo --followup
```

The positional arguments are the explicit case ID and repository-under-test.
`--followup` runs both original behavior and the held-out acceptance checks.
Expose the relevant `private/<case>/FOLLOWUP.md` only after initial outputs freeze;
preserve the original output and give a fresh agent a maintenance copy.

Runtime checks assert public behavior and service boundaries, never helper names
or an architecture. `rubric.json` and each case's `criteria.json` separate behavior
harms from usefulness, cohesion, change locality, proportionality and clarity.
Judge actual policy locations and change interactions rather than raw file,
function, branch or diff-line counts. A data-gathering edit plus one authoritative
decision need not represent two independent policy edits. Retain justified
restraint and any ambiguous contract interpretation explicitly.

## Reproduce harness sanity checks

Build isolated original fixtures and test them:

```sh
python3 evals/refactor/private/self_check.py --output /tmp/refactor-selfcheck-new
```

Or supply an existing generated case root; it will only be read, and every test
and mutation will execute on copies in the fresh output directory:

```sh
python3 evals/refactor/private/self_check.py --cases /tmp/refactor-cases-new --output /tmp/refactor-selfcheck-replay
```

With no `--output`, self-check chooses a unique system temporary directory and
prints it. `summary.json` and `logs/` record:

- Six public baseline suites and six private baseline suites passing.
- Six seeded faults detected: monetary rounding direction, shipping threshold
  inclusivity, raw-token storage, report end-date inclusion, Unicode casefold
  substitution, and reordered historical-refund rounding.
- Two held-out original-missing failures and two positive controls accepted,
  including all original private behavior checks alongside the new requirements.
- Refusal to overwrite existing case inputs, and unchanged original file hashes.

Positive-control patches are self-check fixtures for the authored original
sources. They are not required refactoring architectures and are never compared
against an arm's source. Grading uses the runtime probes and semantic rubric.

`fixture-input-hashes.json` preserves the original public file hashes. Absolute
paths in generated manifests and Git commit metadata naturally vary by location
and run time; public source, requests, docs, tests and seeded dirty content must
remain byte-identical. Private expectations and rubrics were copied byte-for-byte
from the original frozen evaluation. Portability changes only output plumbing.

## Scope and known sensitivity

These are small single-module cases, not a representative sample of large
multi-module migrations. Near-ceiling results have limited discriminatory power.
Two repeat runs do not establish statistical significance or productivity gains.
Legacy grammar checking does not replace executing on a real Python 3.8 runtime.

The original blind review later found a credentials payload-aliasing discrepancy
under a duck-typed store adapter that consumes or normalizes its supplied mapping.
That was a separately disclosed post-freeze diagnostic, not one of these original
private probes. The original README does not explicitly discuss payload mutation;
reports should retain the distinction between the broad injected-service boundary
and a narrower nonmutating-adapter assumption. No original oracle or rubric was
retroactively modified to include that diagnostic.
