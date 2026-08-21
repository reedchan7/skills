# Craft values — extended tables

Concrete numbers for when SKILL.md's inline values need more range. All of
these are starting points calibrated to industry practice (Apple HIG,
Refactoring UI, Geist/Linear/Stripe teardowns, NN/g motion research) — a
project's own tokens always win.

## Type scales

| Context | Ratio | Body | Resulting steps (rounded px) |
| --- | --- | --- | --- |
| Dense product UI | 1.2 | 13–14 | 11 · 13 · 16 · 19 · 23 · 28 |
| Standard product UI | 1.25 | 14 | 11 · 14 · 16 · 18 · 22 · 28 · 44+ display |
| Marketing / editorial | 1.333 | 16–18 | 12 · 16 · 21 · 28 · 38 · 50 · 67 |

- Fluid display sizing: `font-size: clamp(2.5rem, 1rem + 4vw, 4.5rem)` —
  tune the middle term so the H1 holds 2–3 lines at every breakpoint.
- Line-height: ~1.1 display, 1.2–1.3 headings, 1.5–1.6 body, 1.7–1.9 CJK
  body. Tracking: −0.01 to −0.03em above ~28px; never on body.
- iOS Dynamic Type reference (default size): Large Title 34 · Title1 28 ·
  Title2 22 · Title3 20 · Headline 17 semibold · Body 17 · Subhead 15 ·
  Footnote 13 · Caption 12/11. 11pt is the absolute floor.
- Metric/KPI composition: label 11px/500/muted/tracked-wide · value
  28px/600/`tabular-nums` · delta 12px/500/semantic color.

## Spacing

- Scale (non-linear, off a 16px base): 4 · 8 · 12 · 16 · 24 · 32 · 48 ·
  64 · 96 · 128. Pick from it; never invent 13px.
- Density registers: 12–16px component padding = workbench; 20–24px =
  comfortable product; 24–32px = brochure. One register per surface.
- Section rhythm: product pages `py-16`–`py-24`; airy marketing
  `py-24`–`py-32` (up to `py-48` only with content that fills it); mobile
  section gaps `clamp(3rem, 8vw, 6rem)`.
- Containers: content `max-w-[65ch]` reading / `max-w-5xl`–`7xl` page shell
  / `max-w-[1400px]` outer bound. Nav height 56–72px, single row on desktop.

## Color construction

- Neutrals: 8–10 steps of ONE hue family, tinted toward the brand hue
  (a pure-gray ramp reads dead). Build ramps in OKLCH so lightness steps
  are perceptually even: hold hue, step `L` evenly, taper chroma at the
  extremes.
- Working set per accent: 5–10 shades. Saturation of the main accent <80%.
- Text tiers on light: `#111`–`#18181B` primary · ~`#52525B` secondary ·
  ~`#A1A1AA` muted-but-still-3:1 for large only. On dark, lighten text and
  desaturate accents ~10–15%.
- On colored backgrounds, derive secondary text from the background hue
  (lower saturation, higher lightness) — never a flat gray.
- Muted accent pill pairs (bg/text) that pass contrast: `#FDEBEC/#9F2F2D` ·
  `#E1F3FE/#1F6C9F` · `#EDF3EC/#346538` · `#FBF3DB/#956400`.
- Reference points: Geist ink `#171717` on `#fafafa` with *no* accent —
  monochrome restraint is a valid whole direction. Linear: LCH, reduced
  chroma, 3 theme variables (base/accent/contrast).

## Depth recipes

- Light-mode lift (three layers):
  `0 0 0 1px rgba(0,0,0,.06), 0 1px 2px -1px rgba(0,0,0,.06), 0 2px 4px rgba(0,0,0,.04)`
- Hover lift: `0 2px 8px rgba(0,0,0,.04)` over ~200ms.
- Dark-mode "shadow": `0 0 0 1px rgba(255,255,255,.08)` ring; elevation via
  background lightness steps of roughly +7% / +9% / +12% per level.
- Hairlines: dark `rgba(255,255,255,.06–.12)`, light `rgba(0,0,0,.06–.10)`.
  Border-as-box-shadow (`box-shadow: 0 0 0 1px …`) avoids box-model shift
  and follows radius smoothly.
- Image edges: 1px inset outline `rgba(0,0,0,.1)` light /
  `rgba(255,255,255,.1)` dark.
- Concentric radius: `outer = inner + padding`. Tailwind form:
  `rounded-[2rem]` outer, `p-1.5`, `rounded-[calc(2rem-0.375rem)]` inner.
- Glass, when earned: `backdrop-blur` + 1px `border-white/10` + inset
  highlight `inset 0 1px 0 rgba(255,255,255,.1)`; light mode needs
  `bg-white/80`+; provide a solid fallback under
  `prefers-reduced-transparency`.

## Motion library

Frequently repeated and keyboard-initiated paths are instant. The ranges below
apply to occasional interactions; modal/drawer and page/route rows are the only
low-frequency exceptions to the ordinary ≤300ms ceiling.

| Interaction | Duration | Easing |
| --- | --- | --- |
| Button/press feedback | 100–160ms | ease-out |
| Hover color/opacity | 150–200ms | ease-out |
| Tooltip / popover | 125–200ms | ease-out |
| Dropdown / menu (occasional, pointer-opened) | 150–250ms | ease-out |
| Modal / drawer in | 200–400ms | strong ease-out |
| Modal / drawer out | ~2/3 of in | ease-out |
| Toast | 200–300ms | ease-out |
| Deliberate page/route transition | 300–500ms max | ease-in-out |

Named curves:

- Strong ease-out (default enter/exit): `cubic-bezier(0.23, 1, 0.32, 1)`
- Reveal/expand: `cubic-bezier(0.16, 1, 0.3, 1)`
- On-screen movement (in-out): `cubic-bezier(0.77, 0, 0.175, 1)`
- iOS-style drawer: `cubic-bezier(0.32, 0.72, 0, 1)`
- Springs: `{ type: "spring", duration: 0.5, bounce: 0.1–0.3 }` — bounce
  >0 only for gestures/playful; springs preserve velocity, so use them for
  anything interruptible or draggable.

Rules of thumb: entrances slightly longer than exits; stagger 30–80ms;
tooltips animate the first, then `data-instant` for adjacent; hold-to-delete
style asymmetry — slow (~2s linear) where the user is deciding, fast
(200ms ease-out) where the system responds. Transitions over keyframes for
anything re-triggerable (transitions retarget mid-flight; keyframes restart).
`@starting-style` gives CSS-only entry animation. Framer Motion `x/y/scale`
shorthands are not hardware-accelerated under main-thread load — pass full
`transform` strings for performance-critical paths.

## Accessibility numbers

- Contrast (WCAG 2.2 AA): 4.5:1 body · 3:1 large text (≥24px, or ≥18.66px
  bold) · 3:1 non-text UI components and graphics. APCA targets if the
  project uses it: Lc ≥75 body, ≥45 large, ≥30 non-text.
- Targets: 44×44 (Apple pt / AAA) · 48dp Android · 24×24 CSS px WCAG 2.2 AA
  absolute floor (or 24px clearance to neighbors).
- Performance gates that read as taste: LCP <2.5s (preload the hero image),
  INP <200ms, CLS <0.1 (reserve space for images, fonts, embeds).
