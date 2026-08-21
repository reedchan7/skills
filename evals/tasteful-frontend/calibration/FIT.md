# Score calibration fit — 2026-08-21

8 blind anchors (see anchors.json for the mapping, ratings-2026-08-21.json
for the raw ratings). Candidates compared by Spearman rank correlation
against the human scores:

| Mapping | Spearman |
| --- | --- |
| linear `10 − Σ weights` | 0.756 — rejected |
| **band-dominant** (worst severity sets base 9.0/8.5/7.0/4.5/2.5; −0.25 per extra sev-≥1, floor base−1.5; ±0.5 expression) | **0.952 — adopted** |

Residuals within ±1.5 everywhere; largest: B (grok baseline, predicted 2.0
vs rated 3.5 — its desktop art direction partially redeemed it, and its
severity-3 nav clip is mobile-only, which a gut pass under-observes).

## What the anchors taught (beyond the mapping)

1. **Tells barely move humans; breakage dominates.** The "AI slop"
   sonnet baseline (D) rated 7 despite ~9 weighted points of tells; the
   corrupted "fixed" page (G) rated 1. Linear summation punished exactly
   backwards.
2. **Integrity failures and typographic violence are broken/illegible,
   never footnotes or "deliberate poster gestures"** — codified into the
   audit skill's severity notes.
3. **Invisible a11y absences don't register in gut scores** — still
   ledgered as floors, scored as inconsistent.
4. **Mobile is heavily weighted by the rater** (2/8 notes) — both-viewport
   passes are now mandatory before scoring.

## Recalibration trigger

A fresh score the rater disagrees with by ≥2 bands becomes a new anchor;
refit and record here.

## Status: provisional

Single rater, n=8, and the rater's own caveat on record: "我的打分不一定
是权威，仅供参考，别照搬，我又不是专业的设计." Treated accordingly:

- The ratings tuned only the **ledger→score mapping**, never the ledger
  itself — design findings remain measurement-backed and rater-independent.
- The band-dominant *shape* stands on its own argument (linear summation
  lets many 0.5-point tells zero out a usable page — wrong regardless of
  who rates); the *parameters* (band bases, ±0.5 expression) are
  provisional and refine as anchors accrue.
- A non-expert gut is the correct instrument for this specific question —
  the score predicts how a normal human perceives the page — but future
  rounds should add raters (and optionally one expert pass to catch
  dimensions gut ratings under-observe, e.g. mobile-only breakage, as B's
  residual showed).
