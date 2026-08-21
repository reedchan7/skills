# Scores — 2026-08-21 (review skill v1, closed loop)

Generator and reviewer: **grok-4.6, reasoning-effort high** (static path —
no browser). Ground truth: harness measurement in Chrome (datum scripts,
WCAG contrast math, censuses, screen-by-screen screenshots).

## Loop

| Step | Result |
| --- | --- |
| Generate (no skill) | Driftwatch landing, 46KB; coherent "instrument" direction (Syne + radar + ticker) sitting on anti-slop look #2 (near-black + acid green) |
| Review 1 | score **3.5**, 6-item ledger, fixes with line numbers and target values |
| Fix (apply review) | 83-line surgical diff; eyebrows 5→1, tabular-nums added, v2.4 removed |
| Re-review | score **6.0**, 3-item ledger (all new/residual, none stale) |

## Judgment vs ground truth

- **Precision: 100%** on every checked "measured" claim, both rounds —
  contrast 3.52/3.26/6.71 reproduced to the exact hundredth in-browser;
  bento 3-col/6-card, radius 18 vs 14, console mega-shadow, featured-plan
  `0 24px 60px`, `.logos` 13px/700 `#5c6b62` all confirmed. Zero
  fabrication.
- **Recall ≈ 0.83** on harness ground truth; the review also found six
  real issues the harness pass missed (small-text contrast — the heaviest
  real defect — bento orphan row, quote datums, radius split, fake
  interactivity, nav hit-height), and correctly overturned one harness
  item (mono "headings" were data labels inside the console mock —
  legitimate mono role).
- **Miss**: the 5-line hero H1 wrap (render-level; static path neither
  caught nor suspected it in round 1; round 2 flagged H1 line count as
  suspected). Severity 2 — within protocol tolerance, logged.
- **Arithmetic**: both ledgers sum exactly to their scores.
- **Closed loop**: score rose 3.5 → 6.0 and every claimed fix was
  physically re-measured as present (contrast 6.71:1, quote datums
  3692×3, bento 2 rows, radius 14, shadow gone). The fix round also
  introduced a real file-level regression (truncated meta + a second
  doctype at L7, masked by browser error recovery) — **the re-review
  caught it**, honestly labeled as unverified in Not covered.

## Round 2 — browser path (claude + chrome-devtools, same baseline page)

The skill's full evidence path, exercised by an agent with a real browser:
rendered both viewports, measured everything, verified source integrity
first. Found **two severity-heavy defects every static pass (grok's and
the harness's) had missed, both spot-checked exact**: mobile nav clipping
at 375px (nav-cta right 395.5 vs wrap 359 — 36.5px overflow, sev 3) and a
CSS-specificity bug rendering prices at 14px with their "/month" suffix at
16px (sev 2). Also measured the H1 5-line wrap that static round 1 missed
(classified as a flagged rubric conflict rather than a deduction — a
defensible judgment, surfaced with a fix either way), reproduced the
contrast/bento/quote-datum findings, and recorded an 11-point passed-check
list matching harness ground truth (130px edge datum 11/11, CTA bottoms,
reduced-motion behavior). Score 0.0 by formula on a 12-point ledger, with
the report itself noting the top-3 fixes recover to ~7 — reinforcing that
score-band calibration (pending human anchor ratings) is the remaining
open item, not the evidence quality.

## Round 3 — human calibration consequences

Blind anchor ratings (2026-08-21) inverted two of this skill's judgment
calls: the fix-round file corruption the re-review left in "not covered"
corresponds to the human's lowest score on the whole set (1/10, "伤害眼
睛"), and the 5-line Syne hero the round-2 report exempted as a
"deliberate poster gesture" drove the baseline to 3.5. Codified into §4:
integrity failures ledger as broken; magnitude defects are never
exemptible as direction; invisible a11y scores as inconsistent; scoring is
band-dominant. Under the calibrated mapping: grok-baseline 2.0 (human
3.5), grok-fixed 1.0 (human 1.0).

## Verdict

Passes the protocol. Notable behaviors beyond the bar: correct
project-wins-over-rubric calls (semantic status colors not deducted),
expression note names tells without scoring them, "not covered" lists are
genuinely load-bearing. Improvement candidates for v2: ask the static
path to *suspect* headline wrap from font-size × container math
(round 1's only meaningful miss), and consider a broken-file check
(doctype/tag balance) as step 0 of evidence collection.
