# tasteful-frontend-audit — acceptance protocol

The review skill is judged against **ground truth**, not against taste:
its findings must be the ones an independent measurement pass also finds.

## Closed loop

1. **Generate** — a generator model with no skill produces a page from a
   frozen `evals/tasteful-frontend/briefs/` brief (reuse those briefs).
2. **Review** — reviewer model + this skill audits the page, producing the
   report contract: score, deduction ledger, triage-ordered fixes.
3. **Ground truth** — the harness independently measures the same page:
   raw-source integrity, datum script (`getBoundingClientRect` on peer
   elements), mechanical census (hex/font/duration/`transition: all`/
   reduced-motion/focus-visible),
   screen-by-screen screenshots at 1440×900 and 375. This yields the
   reference violation list with severities.
4. **Judge the review** against ground truth:
   - **Recall**: finds the measurable violations of severity ≥1
     (target ≥0.7; a miss of any severity-3 finding fails the run);
   - **Precision**: no fabricated finding presented as measured — every
     "measured" claim must reproduce (one fabricated measurement fails
     the run); suspected/unverifiable findings are exempt if labeled;
   - **Arithmetic**: recompute the band-dominant score from the ledger — worst
     severity sets the base (none 9.0 · bland-only 8.5 · inconsistent 7.0 ·
     illegible 4.5 · broken 2.5), subtract 0.25 per additional severity-≥1
     finding (floor: base − 1.5), then apply the documented ±0.5 expression
     adjustment — and confirm the ledger's severities follow the rubric.
5. **Fix** — the generator model applies the review's fixes (surgical).
6. **Re-review** — the score must improve, and the harness re-measures to
   confirm the claimed fixes are physically present (a score that rises
   without the measurements moving fails the run).

## Notes

- Reviewer without browser tools runs the static path; datum-level
  ground-truth items it can only reach as "suspected" count toward recall
  when correctly suspected, and are not precision failures when labeled.
- Models per round are recorded in SCORES.md; the protocol is
  model-agnostic.
- Runs archive under `runs/` (gitignored).
