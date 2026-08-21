# RESEARCH template (canonical)

Copy everything between the TEMPLATE markers to
`docs/features/<NNN>-<slug>/RESEARCH.md`. Delete charters that did not run.
Every claim carries a citation; a finding without a source does not enter
the spec.

<!-- TEMPLATE START -->

# Research — Feature NNN <title>

- Date: <date> · Mode: <mode> · Spec: ./SPEC.md

## Questions

<The named open questions this research answers — carried from
interrogation and recon. Every finding below maps to one.>

1. <question>

## Problem evidence *(conditional)*

| Finding | Class | Source | Limitation |
|---|---|---|---|
| <adoption/failure/workflow evidence> | measured / observed / documented / inferred | <URL, accessed date> | <cannot establish> |

## Competitor / product scan *(conditional)*

| Product | Behavior | Defaults/limits | Class | Source |
|---|---|---|---|---|
| <name> | <observed behavior> | <limits> | observed / documented | <URL, accessed date> |

<2–4 lines: what users of this category will expect.>

## OSS prior art *(conditional)*

- <project> — <pattern, data model, edge cases> — <repo/PR/issue URL>;
  class: <observed/documented>; limitation: <what this cannot prove>

## Engineering practice *(conditional)*

- <practice/constraint> — <original source URL, accessed date>; applies to:
  <version/context>; limitation: <what this cannot prove>

## Buy vs build

- Candidates: <library/service/internal capability>
- Verdict: <build | adopt <candidate> | hybrid> — <maturity, license,
  security, maintenance signal, integration/exit cost in one line each>

## What this recommends

<The only opinionated section. Each recommendation traces to findings
above by reference.>

1. <recommendation> (per <finding refs>)

## Answered / unanswered

- Answered: <question ids>
- Unanswered after 2 rounds: <question ids> → carried to SPEC as a
  Limit/Deferral, never silently defaulted

<!-- TEMPLATE END -->
