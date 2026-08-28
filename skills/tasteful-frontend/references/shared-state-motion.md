# Shared-state motion

Read this reference for tabs, segmented controls, hover-tracked peer
navigation, shared selection indicators, morphing chips or panels, and other
interfaces where one material appears to move between related states. Skip it
for isolated buttons, ordinary links, dense keyboard-driven menus, and places
where instant state changes are clearer.

The goal is **material continuity**: the interface should feel as if one
surface changes position or shape, while the real content remains crisp,
semantic, and fully interactive. The goal is not a gooey visual effect.

## Model the states before the animation

Keep durable and transient state separate:

- **Active / selected** is durable truth: the current route, section, mode, or
  value. It changes only when the product state changes.
- **Preview** is transient intent: pointer hover or, when appropriate, focus.
  It clears on leave or blur and must never overwrite durable state.
- **Pressed** is local feedback while the pointer or key is down. It should not
  become another persistent state.

The shared surface targets `preview ?? active`. A separate durable marker stays
anchored to `active` while another item is previewed. On leave, clear preview;
the surface returns to the current truth without reconstructing it.

This separation prevents the common failure where hover looks selected, or the
selected location disappears as soon as the pointer explores another item.

## Build four layers

Order the component from back to front:

1. **Shell** — geometry, clipping, one depth strategy, and the component's real
   visual boundary.
2. **Shared surface** — a single decorative silhouette that moves between
   items. It is `aria-hidden` and `pointer-events: none`.
3. **Durable marker** — a short underline, dot, weight change, or equivalent
   signal attached to the active item. It also ignores pointer events.
4. **Content and hit targets** — real DOM text, icons, buttons, focus rings,
   ARIA, and event handlers. Never filter or rasterize this layer.

The decorative layers may not extend the component's visual or interactive
boundary without an explicit reason. A transparent full-width wrapper can
still intercept neighboring controls; a solid masking layer can hide content
outside a compact control. Put `pointer-events: none` on the wrapper and enable
pointer events only on the true control when needed.

This split preserves sharp text and accessibility while allowing the surface
to feel soft, liquid, elastic, or elevated.

## Choose restrained material character

A shared surface is often enough. Add a trail, bridge, bend, or morph only when
it strengthens spatial continuity and remains the surface's single signature
move.

Useful starting ranges:

- Main surface travel: 180–260ms, strong ease-out, interruptible and able to
  retarget mid-flight.
- Optional trailing silhouette: settle 40–100ms after the main surface, or use
  a 280–340ms travel with lower opacity. It must visually merge at rest.
- Hover content response: 120–160ms, usually color plus at most 1px isolated
  translation.
- Pressed response: 120–150ms, return the hover lift and optionally compress
  isolated content to roughly 0.98–0.99.
- Leave: return to active without a special exit animation.

Prefer CSS transitions that retarget naturally. Animate the silhouette with
`transform` and `opacity`; a small component may also transition a quiet color
or shadow when paint cost is measured and negligible. Do not use
`transition: all`, layout-changing hover, repeated bounce, or scale entrances.

The optional trailing layer should communicate velocity, not emit a glow for
its own sake. If the trail is visible while idle, competes with labels, or
makes every hover feel theatrical, remove it.

## Let color communicate the state

Do not default to a generic gray block as the only selected or hover signal.
Derive the material from the product's existing accent or surface system:

- Tinted fill can start around 5–10% accent opacity.
- A hairline can start around 10–20% accent opacity.
- Keep a durable marker, weight, shape, or position signal so color is not the
  only carrier.
- In a deliberately neutral product, use luminance and depth instead of adding
  an unearned hue.

These are calibration ranges, not tokens to copy. Existing product variables,
contrast, themes, and user direction decide the final values.

## Preserve interaction quality

- Keep text, icons, focus rings, hit targets, ARIA, and handlers in the crisp
  content layer.
- Honor `prefers-reduced-motion`: shared travel and trailing motion collapse to
  an instant state change; focus and selection remain fully visible.
- Avoid per-frame JavaScript for ordinary tabs. Event-driven state plus
  compositor-friendly CSS has zero idle work.
- If a specialized liquid renderer is justified, its measurement loop must
  sleep at rest and its filtered silhouette must remain separate from content.
- Treat focus as its own state. It may preview the shared surface for a small
  control, while rapid keyboard traversal should remain instant.
- Touch has no hover. The active surface and marker must still make the control
  understandable without the preview layer.

## Interaction sweep

Static inspection cannot validate timing or hit testing. Use the real rendered
surface and run this sweep:

1. Confirm the idle state identifies the active item without hover.
2. Move across adjacent items, then jump from the first to the last. The main
   surface should lead, any trail should settle behind it, and labels should
   stay sharp.
3. Move the pointer outside. The shared surface must return to active and any
   trail must become invisible.
4. Press an item. Feedback should be visible before navigation or state change,
   without moving layout.
5. Tab through the control and activate an item from the keyboard. Focus and
   active state must remain distinguishable.
6. Enable reduced motion and repeat selection. State changes must remain clear
   without travel or trailing effects.
7. Test 1440×900, 375px width, and a short viewport. Check labels, counts,
   touch targets, clipping, and overflow.
8. Probe points immediately outside a compact overlay (for example with
   `document.elementFromPoint`). They must resolve to the underlying content,
   not a transparent decorative wrapper.
9. Inspect console warnings and animation-related layout shift.

If the component feels slow, remove the trail before shortening every duration.
If it feels rigid, first replace per-item hover fills with one shared surface;
more bounce is rarely the answer.

## Source ideas

- [liquid-gooey](https://github.com/Jakubantalik/Libraries/tree/main/packages/liquid-gooey)
  separates a filtered silhouette from crisp interactive DOM, keeps real focus
  and hit targets, sleeps its measurement loop at rest, and collapses motion
  under reduced-motion preferences.
- [Motion Tab Select](https://motion.dev/examples/react-tab-select) demonstrates
  one shared selection element moving between peer tabs and combines it with
  press and focus feedback.
- [Material Design 3 interaction states](https://m3.material.io/foundations/interaction/states/overview)
  treats hover, focus, pressed, and selected states as combinable signals rather
  than mutually exclusive paint swaps.
