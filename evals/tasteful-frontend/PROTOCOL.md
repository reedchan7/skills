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

**Score = violations weighted by severity** (broken 3 · illegible 2 ·
inconsistent 1 · bland 0.5), lower is better. Record per arm per brief.

## Acceptance criteria for a skill change

1. skilled beats baseline on every brief (fewer weighted violations);
2. skilled does not regress vs the previous skill version's archived runs;
3. the two skilled runs stay close (stability): no invariant violated in one
   run but clean in the other at severity ≥2;
4. the two skilled runs differ in expression (direction, palette, signature
   move) — identical directions across runs means the skill is imposing a
   house style, which is its own failure.

## Archive

`runs/` (gitignored, like other eval case dirs) keeps
`<date>-<brief>-<arm>-<n>.html` plus a `SCORES.md` per session. Known
historical reference points from 2026-08-21 (rule-pile skill era):
baseline 6/10, skill-v1 8.5/10, skill-v2 9→7.5/10 after real-viewport
review caught an off-grid hero — the miss that motivated screen-by-screen
rendering in this protocol.
