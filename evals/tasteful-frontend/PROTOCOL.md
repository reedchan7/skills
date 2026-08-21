# tasteful-frontend — acceptance protocol

Behavioral benchmark for the skill. Every skill change reruns this before it
lands. Claims are only as good as the paired no-skill baseline.

## Arms

| Arm | Prompt |
| --- | --- |
| baseline | brief only |
| skilled | full SKILL.md + references/anti-slop.md + references/values.md, then the brief |

Generator: `claude -p --model claude-sonnet-5 --effort medium`, no tools,
single self-contained HTML to stdout. The skilled arm runs **twice** per
brief (stability sample); baseline once.

## Briefs

- `briefs/driftwatch-landing.txt` — marketing surface (nav, hero, showcase,
  features, pricing, social proof, footer).
- `briefs/driftwatch-console.txt` — product surface (sidebar, event list,
  diff detail, states).
- `briefs/component-align.txt` + `component-align-fixture.html` — sub-page
  scope: align one deliberately off-system card ("Connect Slack") with an
  existing page's design system. Assemble the prompt as brief text + fixture
  appended. Scored differently: **conformance and diff discipline**, not
  direction — (a) untouched regions survive byte-for-byte (any drive-by
  restyle = inconsistent 1 each), (b) the fixed card uses only existing
  tokens/classes (each new hex or novel visual vocabulary = inconsistent 1),
  (c) the card lands on the page's grid, radius, type tiers, and states
  (each miss = 1), (d) emoji/gradient/glow removed (each survivor = 1).
  The fixture's planted bad design trips design linters by construction —
  expected, do not "fix" the fixture.

Briefs are frozen. New briefs may be added; existing ones never edited, so
runs stay comparable across skill versions.

## Scoring — invariant violations, not impressions

Render each output at **1440×900 screen by screen** (full-page thumbnails
hide alignment errors), then 375px full page. Count violations per Layer 1
invariant:

| # | Invariant | Example violations |
| --- | --- | --- |
| 1 | Grid | block edge off-grid; floating cluster; two competing left edges; ragged horizontal datums across peer cards (CTAs/prices at different heights) |
| 2 | Hierarchy | squint fails; >3 text tiers; mono headline/body |
| 3 | Rhythm | equal-gap monotone; dead band in first viewport; decorative device >1 per screen |
| 4 | Color | >1 accent; mixed gray temperatures; decorative color; pure #000/#fff fields |
| 5 | Depth | mixed strategies; loud shadows; non-concentric nested radii |
| 6 | Motion | >300ms UI; ease-in; animated high-frequency path; no reduced-motion; `transition: all` |
| 7 | Completeness | missing hover/focus/disabled or loading/empty/error; contrast/target floor; fake data |

Plus a code grep for the mechanical signals:
`prefers-reduced-motion`, `focus-visible`, `tabular-nums`, `transition: all`,
transition durations, gradient count.

**Severity weights** (broken 3 · illegible 2 · inconsistent 1 · bland 0.5)
build the ledger; the **score is band-dominant** (provisionally calibrated 2026-08-21, single rater,
see `calibration/FIT.md`, Spearman 0.95 vs blind human anchors): worst
present severity sets the base (none 9.0 · bland-only 8.5 · inconsistent
7.0 · illegible 4.5 · broken 2.5), minus 0.25 per additional sev-≥1
finding (floor base − 1.5), ±0.5 for expression. The old linear
`10 − Σ` correlated only 0.76 with human judgment — many small tells do
not zero a page for a human; one broken thing does. Both viewports are
mandatory before scoring: two of eight anchor notes cited mobile defects
the desktop-only pass had missed.

## Visual regression, not just code greps

Every scored run archives four artifacts under `runs/`: the HTML, a
1440×900 first-screen screenshot, full-page screenshots at 1440 and 375,
and the JSON from `private/measure.js` executed in the rendered page at
1440×900 (it measures H1 wrap, mono-heading roles, peer-row CTA datum
spread, WCAG contrast failures, a hue census, and the mechanical flags).
A skill change is compared against the previous version's archived
artifacts: the measure.js JSONs diff mechanically; the paired screenshots
answer what numbers can't (composition, expression, coherence).
Before full-page screenshots, neutralize scroll-reveal animation — inject
`*{transition:none!important;animation:none!important}` and force reveal
classes visible — otherwise below-fold sections screenshot as empty and
read as false missing-content findings.
`private/run.sh <brief> <arm> [claude|grok] [model] [effort]` assembles and
runs one arm; briefs with a `<brief>-fixture.html` get it appended
automatically.

## Direction diversity battery

Because the skill must not impose a house style, the battery spans three
product worlds: `driftwatch-landing` (infra/dev tool), `verdant-landing`
(consumer plant-care app), `ondes-landing` (music festival). Acceptance:
across the three, skilled runs must differ in theme (not all dark),
hue family (measure.js hue census), and type personality. Convergence on
one palette across worlds is a Layer 2 failure even when every page is
individually clean.

## Acceptance criteria for a skill change

1. skilled beats baseline on every brief (fewer weighted violations);
2. skilled does not regress vs the previous skill version's archived runs;
3. the two skilled runs stay close (stability): no invariant violated in one
   run but clean in the other at severity ≥2;
4. the two skilled runs differ in expression (direction, palette, signature
   move) — identical directions across runs means the skill is imposing a
   house style, which is its own failure.

## Score calibration (human anchors)

The deduction formula's *ledger* is ground truth; its *mapping to a
0–10 score* is calibrated against human gut ratings:

1. Pick 6–10 archived runs spanning the quality range and both surface
   types; assign blind labels (mapping saved to `calibration/anchors.json`
   — the rater must not peek) and present them shuffled, chrome-neutral
   (see the anchor-gallery artifact pattern: samples in sandboxed
   iframes, 1440/375 toggle, 0–10 slider at 0.5 steps, optional note).
2. The rater scores on first impression, 1–2 minutes per sample, using
   the band anchors (9–10 ship-grade · 7–8 shippable with nits · 5–6 one
   more work cycle · 3–4 clearly bad/AI · 0–2 broken) — no analysis, no
   reference to SCORES.md.
3. Fit: compare human scores to each run's severity-weighted ledger sum.
   Adjust the mapping, not the ledger — candidate shapes: linear
   `10 − Σ` (current), diminishing `10·exp(−Σ/k)`, or band-dominant
   (highest severity present sets the band, lesser findings move within
   it). Choose whichever maximizes rank agreement with the human scores;
   validate on the anchors (Spearman ≥ 0.8 to accept), record the chosen
   mapping here, and re-state all archived scores under it.
4. Re-calibrate only when the rater disagrees with a fresh score by ≥2
   bands, adding that sample as a new anchor.

## Archive

`runs/` (gitignored, like other eval case dirs) keeps
`<date>-<brief>-<arm>-<n>.html` plus a `SCORES.md` per session. Known
historical reference points from 2026-08-21 (rule-pile skill era):
baseline 6/10, skill-v1 8.5/10, skill-v2 9→7.5/10 after real-viewport
review caught an off-grid hero — the miss that motivated screen-by-screen
rendering in this protocol.
