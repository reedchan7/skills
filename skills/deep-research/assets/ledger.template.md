# Ledger — <slug>

<!-- S and E ids are append-only: never renumbered or deleted (move a source to
     Dropped instead). Claims, Contradictions, Disconfirmation, and Coverage
     are rewritten during Phase 3. Every report citation must resolve to an
     S-entry whose provenance is `fetched`. Evidence lives here, not in
     conversation memory: if it is not in this file it does not exist. -->

## Sources

<!-- One line per source. The locator is always a canonical https URL (or
     doi:/arxiv:), even when the text came through an API or CLI (`gh api`
     → the github.com URL of the file or repo); the checker matches report
     citations against these URLs. type: official | data | peer-reviewed | first-party-docs |
     filing | journalism | analyst | expert-commentary | community | explainer.
     tier: A (owner of the fact / peer-reviewed / primary record) · B (reputable
     secondary with named author and citations) · C (community, single opinion,
     unattributed). provenance: fetched (full text seen) | digest (a
     summarising fetch tool's output; re-ask for verbatim before relying) |
     snippet-only | user-provided | model-knowledge. accessed: date the text
     was opened. -->

- S1 | <title> | <url or doi/arxiv/file locator> | type: … | tier: A | published: YYYY-MM | accessed: YYYY-MM-DD | fetched | stance/notes: …
- S2 | … | digest | note: verbatim passage requested for E4

## Dropped

<!-- Sources evaluated and rejected. They never reappear in the report. -->

- <url> — reason (e.g. no author; SEO aggregator restating S1; superseded by 2026 version; paywall shell, could not read)

## Evidence

<!-- Verbatim or near-verbatim extracts with a locator (section, page, timestamp,
     table). Keep quotes short; record what the passage actually supports. -->

- E1 [S1 § "Pricing", ¶3] "…" — supports: Q2 — note: figure is FY2025, seats not users
- E2 [S3 p.12 Table 4] "…" — supports: Q1

## Claims (load-bearing only)

<!-- type: factual | synthesis | recommendation | speculation. Only factual
     claims need evidence ids; synthesis names the claims it rests on.
     independent: do the cited sources share an upstream origin? status:
     supported | partial | unsupported | contested | unable-to-determine.
     confidence uses the vocabulary in references/verification.md. -->

- C1 (factual) "…" ← E1, E4 | independent: yes | status: supported | confidence: high
- C2 (factual) "…" ← E2 | independent: n/a (single source) | status: partial | confidence: low — needs a second independent source or a Low flag in the report
- C3 (synthesis) "…" ← C1, C2

## Contradictions

<!-- Both sides stay visible. Name the likely cause before choosing a weighting. -->

- X1: C1 vs C5 — S1 reports …; S4 reports … — likely cause: definition | time period | population | method | incentive — weighting: … — what would settle it: …

## Disconfirmation pass

<!-- For each central conclusion: the strongest opposing reading, what was
     searched for it, the critic's numbered objections, the author's answers,
     and the judge's rulings (stands / partly addressed / resolved). Objections
     that stand become disagreements or gaps in the report. -->

- Conclusion C1 — opposing reading: … — searched: … — objections: 1. … (stands) 2. … (resolved: E7) — surprise test: …

## Coverage

| Sub-question | Sources (ids) | Independent sources | Status | Saturation note |
| --- | --- | --- | --- | --- |
| Q1 | S1, S3, S5 | 3 | settled | round 2 added nothing new |
| Q2 | S2 | 1 | thin | needs primary data |
