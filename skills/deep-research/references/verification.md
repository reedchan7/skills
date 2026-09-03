# Verification: claims, corroboration, contradictions, confidence

Loaded for Phase 3 (Verify and reconcile). Works on the ledger; the report is
written only from claims that have passed through here.

## Which claims get verified

Every claim the answer depends on (load-bearing): the conclusion itself, every
number in the Answer or a table, every attribution to a named person or
organisation, every "first / only / largest / deprecated / illegal" style
superlative, and every claim a sceptical reader would challenge first. Colour
and background claims are cited but not independently corroborated; the report
does not present them as findings. In a comparison matrix, one `C` line may
cover one entity's row for one attribute group (licence and release facts;
capability facts) as long as every cell still carries its own citation and the
line lists the evidence ids behind each cell.

Rank by consequence: high = central to the answer and costly if wrong; medium
= supporting; low = peripheral. High claims are verified first and fully.

## The claim ledger

Each load-bearing claim gets a `C` line: text, type, evidence ids,
independence, status, confidence.

- **Type**: factual (checkable against a source) · estimate or forecast (a
  source's projection, cited as theirs) · calculation (cites its inputs and
  shows the arithmetic) · synthesis (follows from named claims) ·
  recommendation · speculation. Only factual claims can be `unsupported`; a
  synthesis is only as strong as its weakest input. Compound sentences are
  split so each claim carries its own evidence; one citation at the end of a
  paragraph covers only the sentence it follows.
- **Alignment fields**: a passage supports a claim when it matches on subject,
  direction, magnitude, population or scope, outcome, time point, and stated
  uncertainty. A mismatch on any one downgrades the claim to `partial`.
- **Status**: supported · partial (the source supports a narrower or weaker
  statement than written) · unsupported · contested (credible sources disagree)
  · unable to determine (every channel failed).

## Corroboration

- A high-consequence factual claim about the world (a figure, an event, a
  measurement, an attribution) needs **two independent sources**, at least one
  of tier A, before it is stated without a flag. Independence means no shared
  upstream: the same press release relayed by five outlets is one source.
  When only one source exists, the report says so beside the claim.
- A **documented behaviour** whose owner is a single authoritative text (a
  software option in the pinned version's docs or code, a clause of a
  standard, the operative text of a rule) is high confidence on the owner's
  text alone once the quote-to-proposition check passes; a second page or the
  source code corroborates but is not required. Two pages from the same owner
  are one source for every other kind of claim.
- A claim whose only support carries `digest` provenance is `partial` until
  the verbatim passage has been retrieved or a second record agrees.
- **Quote-to-proposition check**: re-read the evidence line against the
  sentence that will cite it. The passage must support the proposition *as
  written*: same subject, same quantity, same period, same conditions. A
  passage that supports a weaker statement downgrades the claim to `partial`
  and the sentence is rewritten to what the source actually says.
- **Numbers**: two sources for the same metric within ~10% corroborate; 10–20%
  apart is reported as a range with the cause named; beyond 20% is a
  contradiction (below). Precision in the report never exceeds the source's.
- **Currency**: a time-sensitive claim (price, version behaviour, market
  figure, legal status, "current" anything) rests on a source dated within the
  domain's turnover window (see `sourcing.md`); an older source supports only
  "as of <date>".
- **Provenance**: a claim whose only support is model knowledge stays tagged
  `[model knowledge — verify]` in the report, whatever the confidence feels
  like. If it was not retrieved, it is model knowledge.

## Contradictions

Disagreement between credible sources is a finding, never noise to average
away. For each one, an `X` line records both positions with citations, then:

1. **Name the likely cause**: definition (active users vs provisioned seats),
   period (FY vs calendar), population or scope (TAM vs SAM; global vs US),
   method (survey vs telemetry), incentive (vendor vs independent), version
   (behaviour changed), or error (one source misquotes another — trace both to
   origin).
2. **Weigh, and say why**: tier, independence, recency, and closeness to the
   fact decide; incentive-aligned sources lose ties. When the cause is a
   definition, the report states both figures with their definitions rather
   than picking one.
3. **Say what would settle it**: the document or measurement that would
   resolve the disagreement, so the reader can pursue it.

A conflict between a fetched source and model knowledge is itself flagged in
the report; the fetched source is preferred but not silently.

## Disconfirmation pass

Before synthesis, for each of the two or three central conclusions:

1. **Write the strongest opposing reading** and the competing hypotheses that
   would also explain the evidence (there are usually three to five).
2. **Search for it deliberately**: critics, failure reports, retractions,
   dissenting experts, the losing side of the argument, sources from outside
   the dominant region or school. A conclusion nobody has attacked has not
   been tested; the report says whether a search for opposition found any.
3. **Run a short debate on paper**: a hostile competent critic lists five to
   eight numbered objections; the author answers each with evidence from the
   ledger; a neutral adjudicator rules each objection *stands*, *partly
   addressed*, or *resolved*. Objections that stand become disagreements or
   gaps in the report. Resolved objections are listed briefly so the reader
   sees what was considered.
4. **Stress-test the structure**: remove the single strongest source; does the
   conclusion still stand? Name the premise the whole line of reasoning has
   taken for granted and check it once. Pushback from the requester is a
   prompt to re-examine the evidence, never evidence in itself.
5. **Ask the surprise test**: would this finding surprise the requester? A
   report that only confirms what the requester already believes has probably
   verified in a circle; look for the evidence that would change their mind.

The report never states that "all contradictions were resolved"; it lists the
ones that were, the ones that were not, and what each rests on.

## Confidence vocabulary

Judgments carry two separate things: how likely something is, and how good the
evidence behind the judgment is. Use the words, not decimals.

**Likelihood** (ICD 203 bands):

| Words | Band |
| --- | --- |
| almost no chance / remote | 1–5% |
| very unlikely | 5–20% |
| unlikely | 20–45% |
| roughly even chance | 45–55% |
| likely | 55–80% |
| very likely | 80–95% |
| almost certainly | 95–99% |

**Confidence in the judgment**, bound to the evidence:

| Level | Basis |
| --- | --- |
| high | two or more independent tier-A/B sources agree; current; the passage supports the claim as written |
| moderate | one strong source, or several consistent tier-B/C sources; or a definitional gap the report explains |
| low | single weak source, inferred, dated, or contested without resolution |
| unable to determine | every channel tried failed; the report names the channels |

Write the basis with the level: "*Confidence: moderate — one primary source
(the filing) and one consistent analyst estimate.*" A critical number (size,
growth, share, deadline, safety) is either high confidence or visibly flagged
low; nothing critical hides at moderate.

## Exit criteria for this phase

Every load-bearing claim has a status and a confidence with its basis; every
contradiction has a named cause and a weighting; the disconfirmation pass has
been run for the central conclusions and its surviving objections are recorded;
unable-to-determine claims list the channels that failed. Then, and only then,
synthesis begins.
