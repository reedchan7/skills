# deep-research — acceptance protocol

Behavioral benchmark for the skill. Every skill change reruns this before it
lands. Claims are only as good as the paired no-skill baseline.

## Arms

| Arm | Prompt |
| --- | --- |
| baseline | brief only |
| skilled | full `SKILL.md` (references loaded by the agent as the skill directs), then the brief |

Generator: a fresh headless session per run with web search, page fetch, file
tools, and a subagent tool enabled, isolated working directory, no prior
context. The skilled arm runs twice per brief (stability sample); baseline
once. Archive under `runs/<date>/<brief>/<arm>-<n>/` the full workspace
(`plan.md`, `ledger.md`, `notes/`, `report.md`), the chat transcript, and the
`check_report.py` output.

## Briefs

Frozen in `briefs/`. New briefs may be added; existing ones are never edited,
so runs stay comparable across skill versions. Each brief gets a hidden
oracle in `private/oracles/` — the facts a correct answer must contain and the
traps it must avoid — written from primary sources and dated before the
brief's first scored run; `private/oracles/README.md` lists which exist.

| Brief | Shape | Lens | Tier expected | What it tests |
| --- | --- | --- | --- | --- |
| `pg-incremental-backup.txt` | verify + compare | technology | focused | version pinning, owner-of-fact citations, "as of" dating |
| `eu-ai-act-gpai.txt` | explain | legal + technology | standard | currency, provenance tags for non-retrieved knowledge, jurisdiction |
| `cn-agent-frameworks.txt` | compare | technology + Chinese ecosystem | standard | Chinese-language sourcing, matrix shape with "not found" cells |
| `smb-crm-choice.txt` | decide | market + product | standard | decision shape, criteria before options, labelled estimates vs filed figures |
| `claim-remote-productivity.txt` | verify | academic + policy | focused | contested evidence, contradictions with named cause, ICD-203 confidence |
| `lookup-rfc-9110-status.txt` | lookup | technology | lookup | the protocol is skipped: direct answer with citation, no workspace |

## Scoring — invariant violations, then quality

Score the report and the workspace, not the transcript.

**Hard failures** (any one fails the run):

| # | Invariant | Violation |
| --- | --- | --- |
| 1 | Open before you cite | a cited URL absent from the ledger, or present with `snippet-only`/`model-knowledge` provenance but cited as fact |
| 2 | Citation supports sentence | re-open five random citations; any one that does not support its sentence as written (subject, quantity, period, conditions) |
| 3 | No fabrication | a source that does not exist, a DOI that resolves to a different title, a quotation not in the source |
| 4 | Instruction-following | the requested format, audience, or scope ignored; a lookup brief that produced a workspace |
| 5 | Uncertainty visible | a contested oracle fact stated without the disagreement; an oracle trap stated as fact |

**Weighted defects** (severity: broken 3 · misleading 2 · inconsistent 1 ·
bland 0.5), counted per report:

- broken: placeholder text, Sources entry without locator, citation number
  with no entry, `check_report.py` FAIL not fixed
- misleading: vague attribution, precision above the source's, number without
  period or unit, stale source for a time-sensitive claim without "as of",
  confidence stated without basis, absence claimed without the prove-a-negative
  record
- inconsistent: heading with no supported claim, empty comparison cell not
  marked "not found", tier announced but budget exceeded without a logged
  reason, workers duplicating a sub-question
- bland: findings as bullet dumps, generic conclusions ("it depends"), process
  narration in the body

Score is band-dominant: the worst present severity sets the base (none 9.0 ·
bland-only 8.5 · inconsistent 7.0 · misleading 4.5 · broken 2.5), minus 0.25
per additional finding of severity ≥1 (floor base − 1.5).

**Quality lines** (RACE, 0–2 each, added to the band score for ranking only):
comprehensiveness against the oracle's required facts; insight (mechanism or
trade-off stated, not listed); instruction-following; readability (answer
first, headings carry claims).

**Cost line** (reported, not scored): searches run, sources opened, workers
spawned, wall-clock, tokens where available. A skilled run must not exceed
its tier's budget table without a logged reason.

## Stability

Two skilled runs per brief must agree on the answer's direction and on every
hard-failure invariant. Divergence on the answer is a defect in the brief or
the skill, investigated before the version lands.

## Mechanical self-check

`python3 private/test_check_report.py` exercises `scripts/check_report.py`
against fixtures in `private/fixtures/`: a compliant report passes with zero
FAIL; each planted defect (missing bibliography entry, range placeholder,
vague attribution, uncited number, evidence dump, ledger mismatch) is caught.
`python3 private/test_renumber_citations.py` covers
`scripts/renumber_citations.py`: first-appearance numbering, generated Sources
entries, and refusal on unknown or weak-provenance ids. Run both after any
change to the scripts.

Archived runs live under `runs/<date>/<brief>/<arm>-<n>/` (gitignored). The
2026-09-02 smoke runs for `pg-incremental-backup` (focused, no workers) and
`cn-agent-frameworks` (standard, three workers, resumed twice after rate
limits) are the first reference points; their delivery messages and usability
logs sit beside the workspaces.
