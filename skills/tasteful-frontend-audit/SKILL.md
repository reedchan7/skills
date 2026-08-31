---
name: tasteful-frontend-audit
description: Audit, score, and diagnose existing frontend UI — a whole product, a single page, or one component — against structural design invariants. Use when asked to review, evaluate, rate, or critique UI/UX visual quality, explain why a UI looks off, ugly, cheap, inconsistent, or AI-generated, check design-system conformance, or produce a prioritized improvement plan with concrete fixes. Read-only by default; reports findings and recommended fixes but does not edit code unless explicitly asked.
---

# tasteful-frontend-audit

Diagnose why an interface does or doesn't hold together, with evidence, a
score, and fixes worth making — and nothing else. Precision over vibes: a
finding you cannot back with a measurement, a coordinate, a computed value,
or a visible screenshot region is a suspicion, and is either resolved or
labeled as such.

This is the review counterpart of the `tasteful-frontend` skill: its seven
structural invariants are the rubric here (kept in sync with that skill —
it is canonical if the two ever drift). When it is installed alongside,
consult its `references/anti-slop.md` to name known generated-look tells
and `references/values.md` for target numbers to recommend. For tabs,
segmented controls, hover-tracked peer navigation, shared selection
indicators, or morphing panels, also read
[shared-state motion](../tasteful-frontend/references/shared-state-motion.md)
and apply its interaction sweep; skip it for isolated buttons and links.

## 1. Scope the audit

| Target | What to examine |
| --- | --- |
| Whole product | Representative surfaces, not everything: the highest-traffic page, one overlay (menu/dialog), one form, one data view — plus the seams between them (does one system hold across surfaces?) |
| One page | Every section, screen by screen, both key viewports |
| One component | The component in its real context — parent grid, neighbors, its states — never as an isolated fragment |

State what was and was not covered. A finding of "consistent" only extends
to what was actually examined.

## 2. Collect evidence before judging

0. **Integrity first**: confirm the artifact parses — one doctype,
   balanced tags, no truncated attributes. Browsers recover from broken
   markup silently; a review of a half-parsed file is a review of the
   recovery, not the design.
1. **Render at real viewports** when a browser is available: 1440×900
   screen by screen, then 375px. Full-page thumbnails hide alignment and
   datum errors — never judge from them alone.
2. **Measure, don't eyeball.** Alignment and datum claims come from
   `getBoundingClientRect` (left edges on the grid? peer-card CTAs on one
   y?); hierarchy claims from computed styles (font sizes, weights,
   colors); density from actual padding values.
3. **Mechanical census** of the source: hex values (how many grays, how
   many hues), font families (mono where?), transition durations and
   easings, `transition: all`, `prefers-reduced-motion`, `focus-visible`,
   `tabular-nums`, `cursor-pointer`, aria labels, gradient and shadow
   inventory.
4. **Exercise states** where possible: hover, focus (Tab through it),
   open the overlay, trigger empty/loading/error. Unreachable states are
   reported as "not verifiable", not assumed present. For shared-state
   controls, traverse adjacent and distant items, leave the control, press
   and keyboard-activate it, enable reduced motion, and probe immediately
   outside decorative wrappers for hit-test interception.
5. Without a browser, do static analysis and say so: confidence is lower,
   and datum-level findings become "suspected" unless the code structure
   proves them (e.g. content-length-driven positioning with no shared grid
   rows is provable statically). Never report coordinates or line breaks as
   measured from source alone — but two checks must still be *attempted*,
   their results labeled suspected: contrast wherever the effective
   foreground and background colors are knowable from the source, and
   headline wrap estimated from font size × average glyph width × character
   count against the container width — a projection past 3 lines is a
   suspected finding to report, never a check to skip.

## 3. The rubric — seven invariants

Check in order; every finding names its invariant.

1. **Grid.** One container system; every block's edge on a grid line or
   declared axis; equivalent elements in peer containers share horizontal
   datums (measure the y of prices, CTAs, list starts across a card row);
   no floating clusters, no two competing left edges.
2. **Hierarchy.** Weight and color carry it before size; 2–3 weights,
   ~3 text tiers, sizes from one recognizable ratio; monospace only on
   code/data/labels, never headlines or body; squint test separates
   headline / body / label.
3. **Rhythm.** One spacing scale and density register; more space between
   groups than within; no equal-gap monotone; first viewport composes as
   one unit with no dead bands; decorative devices (eyebrows, badges,
   flourishes) at most once per viewport.
4. **Color.** One neutral ramp, one hue family (lightness shifts only),
   ≤1 accent per view; color communicates, never decorates; no pure
   #000/#fff fields; no gray text on colored backgrounds; both themes
   audited if present.
5. **Depth.** One strategy (hairline / soft shadow / tint), quiet shadows,
   no glows or hard outlines; radii from one scale, nested radii
   concentric; borders the last resort after space and tint.
6. **Motion.** Frequently repeated and keyboard-initiated paths are instant;
   ordinary feedback and enter/exit stay ≤300ms, with only low-frequency
   spatial exceptions (modal/drawer ≤400ms, deliberate page/route ≤500ms).
   Enter/exit uses ease-out; on-screen movement may use ease-in-out. Motion is
   limited to transform/opacity; no `transition: all`, unmotivated scroll
   theatre, or missing `prefers-reduced-motion` handling. In shared-state
   controls, durable selection remains legible during preview, decorative
   silhouettes never filter or intercept real content, optional trails vanish
   at rest, and touch remains understandable without hover.
7. **Completeness.** All interactive states (default/hover/focus-visible/
   active/disabled) and data states (loading/empty/error); contrast
   4.5:1 body, 3:1 large/UI; targets ≥24px (44 touch); `cursor-pointer`;
   realistic synthetic product-state data; no invented customers,
   testimonials, certifications, security/compliance claims, usage metrics,
   or business outcomes presented as factual marketing proof; copy in one
   register with no filler clichés.

Beyond the invariants, assess **expression** (not scored, reported):
is there a coherent direction and one signature move, or is it the
generated median? Name specific tells via the anti-slop dictionary.

## 4. Severity and score

Weight each finding: **broken 3** (unusable, overlapping, illegible-in-fact,
keyboard-dead) · **illegible 2** (contrast/hierarchy failures that impede
reading) · **inconsistent 1** (violates the surface's own system) ·
**bland 0.5** (generic default where a decision was available).

**Score is band-dominant** (provisionally calibrated against a single-rater blind anchor round,
2026-08-21, Spearman 0.95): the worst severity present sets the base —
no findings **9.0** · bland-only **8.5** · worst is inconsistent **7.0** ·
worst is illegible **4.5** · any broken **2.5** — then subtract 0.25 per
additional severity-≥1 finding (floor: base − 1.5), and adjust ±0.5 for
expression (a genuine signature that passes the twin test earns +0.5; the
generated median earns −0.5). One decimal. Report the score with its
deduction ledger — a score without the ledger is a vibe.

Severity notes from calibration: a failed integrity check (broken markup,
duplicated doctype, truncated attributes) is itself a **broken** ledger
finding, never a footnote — rendering damage dominates human perception.
Absent-but-invisible a11y mechanics (`focus-visible`, reduced-motion
handling) stay in the ledger as the floors they are but score as
**inconsistent**, not illegible. And the project-wins exemption applies to
*systems* (a token choice, a consistent convention), never to *magnitude
defects*: a hero wrapping past 3 lines, text sizes inverted by a
specificity bug, or clipped controls ledger at full severity no matter how
deliberate the direction claims to be.

Do not pad the ledger: pre-existing issues outside the audited scope,
style preferences the surface's own system contradicts, and speculative
redesigns are out. When the project's system and this rubric disagree, the
project wins — flag the rubric conflict once, don't deduct.

## 5. Report contract

Lead with the verdict: one sentence + the score. Then:

1. **Deduction ledger** — each finding: invariant, severity, the evidence
   (measured values, coordinates, `file:line` when source is available),
   one line.
2. **Fixes, in triage order** (broken > illegible > inconsistent > bland):
   each with the concrete target value or mechanism ("anchor CTAs with
   `margin-top:auto`; row datum currently 2960/2960/2984", not "improve
   alignment"). Fixes must be expressible in the surface's existing
   tokens; flag when a real fix genuinely needs a new token.
3. **Expression note** — direction coherence, signature move, named tells.
4. **Not covered** — states or surfaces that couldn't be exercised.

Stay read-only: recommend, don't edit, unless the user explicitly asks for
the fix. When they do, hand off to the `tasteful-frontend` skill's scope
rules (inherit direction, zero expression budget, surgical diff) and
re-run this review afterward — the score must move for the fix to count.
