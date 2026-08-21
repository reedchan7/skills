---
name: tasteful-frontend
description: Build and restyle frontend UI with modern, high-taste, Apple/Linear/Stripe-grade polish. Use when creating a new UI surface or component, refactoring or simplifying visuals, fixing UI the user calls ugly, gaudy, heavy, bland, or AI-looking, choosing typography, color, spacing, depth, or motion values, or reviewing a UI change for visual quality. Covers direction-setting, structural invariants (grid, hierarchy, rhythm, color, depth, motion, states), expression budgeting, render-verification, and anti-AI-slop review for both product UI and marketing surfaces.
---

# tasteful-frontend

Ship interfaces that look **decided, not generated**.

## Layer 0 — Axioms

1. **Design is decisions.** Every visible value — a size, a color, an edge
   position, a duration — traces to an intent you can state in one sentence.
   Unstated intent means a default, and a default is the median of training
   data: the generated look.
2. **Structure is invariant; expression is budgeted.** Lasting polish is an
   unchanging structural core wearing a thin expressive layer. Expression
   never spends itself on structure.
3. **Nothing ships unseen.** Text rules cannot catch coordinate-level errors;
   only looking at the render can. Generation without criticism is half the
   craft.
4. **Subtract first.** When something feels off, remove before you add; when
   the user calls it gaudy or heavy, the fix is less, never more effects.

The context always wins over this file: existing project tokens, components,
and conventions beat every value below. Extend the system on the surface you
are touching; never fork a parallel visual language; keep the diff surgical.

## Layer 1 — Structural invariants

These hold in every direction, every brand, every surface. Construct in this
order; each step ends with its own check.

1. **Grid.** Lay the page grid before any content: one container width
   (constrained and centered on wide viewports), its columns, one gutter.
   Declare each section's alignment axis — left-anchored or centered — and
   commit every element in the section to it. Every block's edge sits on a
   grid line. The grid has rows as well as columns: equivalent elements in
   sibling containers — card titles, prices, CTAs, the start of a feature
   list — share horizontal datums, aligned by structure (shared grid rows /
   subgrid, or anchoring to the container edge with auto margins), never
   left to content length. *Check: any two stacked blocks share an edge or
   a declared column; across any row of peer cards, equivalent elements sit
   on one line; nothing floats.*
2. **Hierarchy.** Weight and color before size: 2–3 font weights, 3 text
   tiers (primary/secondary/muted), sizes from one ratio (1.2 dense product
   · 1.25 default · 1.333 expressive). Type roles are fixed — display,
   heading, and body are proportional faces; monospace is a data role (code,
   diffs, metrics, `kbd`) and never a personality choice for headlines or
   body. *Check: squint — headline, body, and label still separate; no mono
   outside data.*
3. **Rhythm.** One spacing scale (4/8 base), one density register per
   surface; visibly more space between groups than within them — a page
   where every gap is equal has decided nothing. A repeated decorative
   device (eyebrow, badge, divider flourish) is chrome, not decoration:
   ration it to at most once per viewport or drop it. The first viewport is
   one composition — headline, support, actions, and any artifact share the
   grid with no dead bands between them. *Check: gaps encode grouping; the
   first screen composes; decoration count ≤1 per screen.*
4. **Color.** One neutral ramp with off-black/off-white ends (one hue family
   — shift lightness, never temperature), at most one accent per view. Gray
   builds structure; color communicates — status, action, identity — and
   never decorates. Semantic tokens over literal grays. *Check: count hues;
   audit both themes if the project has them.*
5. **Depth.** One strategy per surface — hairline borders, soft layered
   shadow, or background-tint shift — whisper-quiet, never mixed. Separate
   by space first, tint second, elevation last. Radii come from one scale,
   nested corners concentric (`outer = inner + padding`). *Check: shadows
   barely visible; no hard outlines; radii consistent.*
6. **Motion.** Gate by frequency first: anything high-frequency (menus,
   command palettes, keyboard-initiated) is instant. What remains: ≤300ms,
   ease-out for enter/exit, `transform`/`opacity` only, never
   `transition: all`, reduced-motion honored. An animation must state its
   purpose in one sentence or it does not exist. *Check: purpose per
   animation; nothing moves that the user triggers constantly.*
7. **Completeness.** Every interactive element has default / hover /
   focus-visible / active / disabled; every data view has loading (skeletons
   shaped like the layout) / empty (one clear action) / error. Floors:
   contrast 4.5:1 body and 3:1 large/UI, targets ≥24px (44 on touch), color
   never the only signal, `cursor-pointer` on clickables. Demo data looks
   real — locale-appropriate names, organically messy numbers, never lorem
   or Acme. *Check: tab through it; break it; read every visible string
   aloud once.*

## Layer 2 — Expression budget

A direction may vary **only**:

- the accent hue, and the temperature of the neutral ramp;
- typeface personality *within roles* — a grotesk, humanist, or serif
  display voice; body stays readable, mono stays data;
- texture and imagery treatment — grain, a gradient as a brand moment,
  illustration and photo style;
- **one signature move per surface** — a hero artifact, an interaction, a
  compositional idea. Spend the whole budget there; everything else stays
  quiet so it can work.

Everything not on this list is structure, and not available for expression.

The brief's own words always win. Where the brief is silent, do not default:
derive the direction from the product's world (what materials and light
would its physical space have?), and steer clear of the recognizable
generated looks — indigo-gradient SaaS, cream + serif + terracotta,
near-black + acid glow. Changing the typeface and palette away from these
is the single highest-leverage move.

Before writing code, declare the direction in a short visible note: one
sentence of intent in contrastive vocabulary ("warm like a notebook", not
"clean and modern"), plus the chosen system values (scale ratio, density,
ramp + accent, depth strategy, radius scale, motion budget, signature move).
A declared default is inspectable; a silent one is slop.

## Layer 3 — Verification loop

Run after building, before delivering. Nothing ships unseen.

1. **Render at real viewports**: 1440×900 screen by screen — full-page
   thumbnails hide alignment errors — then 375px. Screenshot with a browser
   tool when one is available; otherwise trace each section's box edges and
   verify the coordinates by hand.
2. **One pass per invariant**, in Layer 1 order: edges on the grid → squint
   → gaps and first-screen composition → hue count → depth quiet → motion
   purposes → states and strings.
3. Fix and re-render. The loop ends when a full pass finds nothing — not
   when you are tired of looking.

For review requests on existing UI, run the same loop and report violations
by invariant; consult [references/anti-slop.md](references/anti-slop.md) —
a diagnostic dictionary of known generated-look tells — to name what you
see. It is a review aid, not a generation input. Numeric ranges (type
scales, easing curves, shadow recipes, a11y numbers) live in
[references/values.md](references/values.md).
