# Frontend taste skill — landscape and evidence

Research basis for `tasteful-frontend` (2026-08-21). Two corpora: 12 locally
installed design skills read in full, and external authoritative sources on
high-polish UI. This records what the skill must beat, what it borrows, and
what it deliberately rejects.

## Corpus 1 — installed skills (what exists, what to beat)

| Skill | Verdict |
| --- | --- |
| `frontend-design` (Anthropic) | Best prose and restraint doctrine ("spend boldness in one place", copy-as-design, the three named slop looks). Zero concrete values — worst specificity. |
| `design-taste-frontend` (~1200 lines) | Deepest anti-slop catalog anywhere; production-tested tells (div-built fake screenshots, eyebrow rationing, banned hex families). Too big to sit in context; 60+-item checklist gets skimmed; some author-idiosyncratic bans; landing-page-scoped only. |
| `interface-design` | Best-engineered as a prompt: process spine (intent → domain exploration → declared direction → per-component checkpoint → self-tests → persistence), worked type-scale example, elevation deltas, three-layer shadow, control ladder (native → primitive → hand-roll). Product-UI-scoped. |
| `emil-design-eng` | The definitive motion skill: frequency gate, duration table, easing decision tree, transitions-vs-keyframes, spring physics. Motion-only. |
| `baseline-ui` | Highest signal-per-token; MUST/NEVER testable rules; subtraction-by-default. Prevents bad, doesn't create good. |
| `high-end-visual-design`, `minimalist-ui`, `gpt-taste`, `stitch-design-taste` | Each a single aesthetic or page formula marketed as taste; applied everywhere they become new slop. gpt-taste's bias diagnosis (6-line hero wraps from narrow containers, empty bento cells) is sharp; its fake-Python-RNG theater is a failure mode to avoid. minimalist-ui is a good worked example of a *complete* direction spec (every hex pinned). |
| `frontend-ui-engineering` | Engineering hygiene + a good "AI aesthetic table with Why column" and rationalizations table; taste content generic. |
| `ui-ux-pro-max` | CSV-database + retrieval CLI architecture; quietly excellent "overlooked" rules (light-mode glass/border failures); heavyweight machinery, shallow inline content. |
| `web-design-guidelines` (Vercel) | Fetch-and-apply shim to a canonical URL; tiny and fresh, but network-dependent and empty offline. |

### Structural lessons adopted

1. Diagnose the model's bias before prescribing (interface-design, gpt-taste).
2. Order: read → classify → declare direction → build → gate.
3. Every ban carries an override path — absolute bans breed a new monoculture.
4. Mechanically checkable rules beat vibes (countable caps, greppable tells).
5. Checklist ceiling ~10–15 items as gate; long catalog goes to references.
6. Decision procedures (frequency gate, easing tree, control ladder) compress
   judgment better than outcome lists.
7. Explicit subtraction steps; the maximalist skills' shared defect is none.
8. Self-tests: squint, swap, signature, token, twin.

### Rejected

Fake randomization theater; mandatory page formulas (AIDA); single-aesthetic
prescriptions; gimmick behaviors; unfilled scaffolding; runtime dependencies
(Python CLI, fetch-fresh) for a skill that must work degraded.

## Corpus 2 — external sources (key evidence)

- **Apple HIG**: hierarchy/harmony/consistency; Dynamic Type scale (Body 17,
  floor 11); 44×44pt targets. Canonical pages are JS-rendered; values
  corroborated via learnui.design and designsystems.one.
- **Refactoring UI** (Wathan/Schoger): hierarchy via weight+color not size;
  hand-picked non-linear scales; start with too much whitespace; shadows as
  a fixed small elevation system; reduce borders; never gray text on colored
  backgrounds; 45–75ch measure; labels last resort.
  (sglavoie.com book summary; medium.com top-20 digest)
- **Vercel Geist**: `#fafafa`/`#171717`, no accent — the ink is the brand;
  borders as box-shadow; grid as aesthetic. (vercel.com/geist,
  designsystems.one)
- **Linear**: LCH color space, 3 theme variables (base/accent/contrast),
  reduced chroma, px-level alignment as company value. (linear.app/now —
  redesign + design-reset + craft essays)
- **Stripe**: light-first, narrow columns, light-weight display type,
  gradient confined to brand moments, low-opacity layered shadows.
  (third-party teardowns: designmd.cc, stripe.design — no first-party spec)
- **Rauno Freiberg** (rauno.me/craft/interaction-design): interruptible
  gestures; frequency kills animation; spatially consistent origins.
- **Emil Kowalski** (emilkowal.ski, skills/review-animations STANDARDS):
  ease-out enter/exit, never ease-in; curves `0.23,1,0.32,1` /
  `0.77,0,0.175,1` / `0.32,0.72,0,1`; durations 100–500ms by component;
  ≤300ms general UI; transform/opacity only; reduced-motion = gentler not
  zero.
- **NN/g** (nngroup.com/articles/animation-duration): 100–500ms envelope;
  ~100ms feedback; 200–300ms modal; entrances > exits.
- **AI-slop discourse 2024–26** (vibecodekit.dev, mania.design,
  925studios.co, prg.sh): tells converge on indigo gradients, cardocalypse,
  colored left-border strips, three cards, emoji icons, uniform radius;
  cures: typeface change first, ≤3 hues 60/30/10, borderless-first,
  8pt grid, ×1.25–1.333 scales, design non-happy-path states.
- **WCAG 2.2**: 4.5:1 / 3:1 / 3:1 non-text (SC 1.4.3, 1.4.11); targets
  24px AA (SC 2.5.8), 44px AAA/Apple, 48dp Android. (w3.org/TR/WCAG22)

Unverified, excluded from the skill: the "Wathan indigo apology" anecdote
(secondary sources only).

## Gaps in the whole landscape (future work, not in v1)

Data-viz/table taste (covered by a separate `dataviz` skill in some
runtimes); mobile-first composition beyond column collapse; OKLCH ramp
generation in depth (v1 has one paragraph); i18n/CJK (v1 has a starter
block — none of the 12 corpus skills had any); imagery art direction;
view-transitions/perceived-performance design; IA and multi-step flows;
taste-under-legacy-constraints.

## What `tasteful-frontend` is

v1 (2026-08-21, morning): a distilled rule pile — interface-design's process
spine + emil's motion framework + design-taste-frontend's tells with
override paths + baseline-ui's terseness + frontend-design's copy doctrine,
~250 lines core + 2 references + a 10-item gate.

## Why v1's architecture was replaced the same day

Live A/B testing (sonnet-5 medium, fixed brief, paired baseline) exposed the
rule-pile failure mode within three rounds: each observed defect (eyebrow on
every section, off-grid hero cluster, monospace display headlines) triggered
a new rule, growing the core while missing the shared cause. This is the
`design-taste-frontend` trajectory — 1200 lines of scar tissue — restarted.
Root causes identified:

1. **Bans are a blacklist over an infinite error space.** Composition errors
   cannot be enumerated; the finite object is the set of structural
   invariants whose observance makes whole error classes unconstructible
   (a declared grid kills every floating-cluster variant at once).
2. **The failure is the missing feedback loop, not missing knowledge.**
   Coordinate-level bugs are invisible in code text; only rendering shows
   them. A generation-only skill is an open-loop system. (Confirmed twice:
   the model produced the off-grid hero, and the *reviewer* — full-page
   thumbnail screenshots — missed it. Both sides need the loop.)
3. **Structure and expression were not layered.** Apple/Linear-grade
   stability = invariant structural core + thin budgeted expression layer.
   Unlayered rules let the model spend expression on structure (mono
   headlines) while the skill could only chase symptoms.
4. **Rule count has negative marginal utility** at medium effort: 580 lines
   in-context dilute per-rule attention; every patch taxes every other rule.

v2 architecture (current): **Layer 0 axioms → Layer 1 seven constructive
invariants (each with its own check) → Layer 2 expression budget (what a
direction may vary; everything else is structure) → Layer 3 render-verify
loop (screen-by-screen at real viewports)**. References demoted to
review-mode diagnostics (anti-slop dictionary) and a numeric handbook.
Core ~150 lines and frozen: a new failure must first be attributed to an
existing invariant (fix its construction/check step, zero net growth);
only an unattributable failure may propose a new invariant.

Acceptance is codified in `evals/tasteful-frontend/PROTOCOL.md`: frozen
briefs (marketing + product surface), paired baseline, double skilled runs
for stability, scoring by severity-weighted invariant violations at real
viewports, plus expression-diversity check (identical directions across
runs = imposed house style = failure).
