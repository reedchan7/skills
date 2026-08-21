# Anti-slop catalog

A **review-mode diagnostic dictionary**: known "generated UI" tells, each
with the condition under which it becomes legitimate. Consult it when
auditing existing UI or when a verification pass smells wrong — it names
what you see. It is not a generation input: every tell here is a symptom of
some Layer 1 invariant being skipped, and following the invariants
constructively makes these unnecessary to memorize. Nothing here is a moral
rule — every entry is a *default* that must be earned before it appears.

Severity triage when reviewing: **broken > illegible > inconsistent > bland**.
Fix in that order; do not polish a bland detail on a page with a contrast
failure.

## Layout and structure

| Tell | Why it reads as slop | Override |
| --- | --- | --- |
| Centered hero + badge above H1 + two buttons | The single most common generated page shape | Fine when the brand genuinely is a centered-manifesto brand — then vary everything else |
| Exactly three equal feature cards | The median of training data | Use 3 when there are truly 3 things; vary card weight/size |
| 1·2·3 numbered step sections | Default explainer shape | Keep when order genuinely matters; the verb is the label ("Install", "Configure", "Ship"), not "Step 1" |
| Bento grid reflex | Bento with empty or filler tiles = no content plan | Bento is fine when cell count = content count and 2–3 cells carry real visual variation |
| Same layout family repeated (endless left/right zigzag) | No composition decisions | Max 2 consecutive alternating splits; a family appears once per page |
| Everything in a card ("cardocalypse") | Elevation without hierarchy meaning | Cards only when elevation = hierarchy; else `divide-y`, `border-t`, whitespace |
| 6-line wrapping hero H1 | Narrow container + oversized type, never copy length | Widen container (`max-w-4xl/5xl`), size with `clamp()`, cap at 2–3 lines |
| Trust logos / avatar rows / pricing teasers inside the hero | Hero overload | They get their own section below the fold |
| Full-bleed text on ultrawide | 200-char lines, hollow page | Constrain content columns; full-bleed only for true canvases |
| Left-aligned text cluster floating in a centered container | Two competing left edges; aligns with nothing above or below | Never — anchor to the container edge or center the cluster's axis |
| Ragged peer cards (CTAs, prices, list starts at different heights across a row) | Content length dictating position; breaks the horizontal comparison scan | Deliberate masonry/editorial layouts where cards are not peers |
| Hero text block and showcase card stacked as two full screens | Dead space between; first viewport composes nothing | Compose them together: split columns, tight stack, or overlap |
| Monospace display headlines | Terminal cosplay; mono belongs to code and data | Small doses in a deliberate brutalist/terminal brand, never the H1 |

## Color and surface

| Tell | Why | Override |
| --- | --- | --- |
| Purple→indigo gradient | The canonical AI palette | Brand is actually purple |
| Neon glow borders on dark | Awwwards-clone reflex | A deliberate cyber/terminal direction, used once |
| Pure `#000` / `#fff` fields | Kills depth, harsh contrast edges | Deliberate brutalist/print direction |
| Glassmorphism everywhere | Decoration without hierarchy | One glass layer where depth means something; solid fallback for reduced-transparency; light mode needs `bg-white/80`+ |
| Cream `#F4F1EA` + serif + terracotta | Recognizable slop look #1 | Brief names it |
| Near-black + acid green + glow | Recognizable slop look #2 | Brief names it |
| Broadsheet hairlines + zero radius everywhere | Recognizable slop look #3 | Genuinely editorial product |
| 3–4px colored left-border strip on cards/alerts | Widely called the single most reliable AI tell | An existing design system that already uses it |
| Warm and cool grays mixed on one surface | No palette ownership | Never — pick one neutral family |
| Gray text on colored background | Muddy, low-craft | Never — tint the text with the background hue instead |

## Decoration and chrome

| Tell | Why | Override |
| --- | --- | --- |
| Eyebrow label above every section | Rationing gone; mechanical rhythm | ≤1 eyebrow per ~3 sections |
| Section-number eyebrows (`001 · Capabilities`) | Fake editorial gravitas | Genuinely numbered content |
| Version badges in hero (`V2.0`, `BETA`) | Decoration masquerading as information | A real, current version that users need |
| Decorative status dots (pulsing green) | Fake liveness | A real live signal behind it |
| Middle-dot chains (`Fast · Secure · Simple`) | List evasion | Rare, once |
| Crosshair/plus hairline ornaments | Template-kit decoration | A drafting/CAD-flavored brand |
| Custom mouse cursors | Novelty over usability | Almost never |
| Scroll cues ("Scroll to explore", bouncing chevron) | Apologizing for the page | Content below the fold that genuinely looks like an ending |
| Locale/weather strips (`LIS 14:23 · 18°C`) | Copied portfolio affectation | The product is actually about time/weather/location |
| `BRAND. MOTION. SPATIAL.` word strips | Filler gravitas | Never |
| Rotated 90° side labels | Decoration that fights reading | Strong editorial grid that earns it |
| Shortcut key labels on option cards (`C`/`W` chips) | Chrome without a power-user flow | The shortcut actually exists and the surface is keyboard-driven |

## Content and data

| Tell | Why | Override |
| --- | --- | --- |
| Div-built fake screenshots | The #1 LLM design tell — uncanny, always | Build the real thing small, or use a real capture/mock image |
| John Doe / Acme / Nexus / lorem | Instantly fake | Never — realistic locale-appropriate data |
| Fake-perfect numbers (`99.99%`, `50%`, `10x`) | Reads as invented | Organic values (`47.2%`, `+38ms`) or real data |
| Fake version footers (`v1.4.2 · synced 4s ago`) | Fake liveness | Real values wired in |
| Name-only testimonials, 5-line quotes | Low-effort social proof | Quote ≤3 lines; name + role (+ company) |
| Logo "walls" as styled text spans | Fake brands in real clothes | Real SVG marks from a verified source; invented brands get an invented monogram |
| Emoji as icons | Uneven rendering, childish register | Deliberate playful brand, sparingly, never for actions |

## Copy register

Banned unless quoting: "Elevate", "Seamless", "Unleash", "Empower",
"Next-gen", "Game-changing", "Revolutionize", "Supercharge", "Delve".
Banned label poetry: "Quietly in use at", "From the field", "Field notes",
"Trusted by teams everywhere" (without real logos). Cute AI copy is worse
than boring copy — when in doubt, say the plain thing ("Testimonials",
"Latest writing", "Pricing").

Duplicate-intent CTAs ("Get in touch" here, "Let's talk" there) are one
label decided twice. One intent, one label, page-wide.

## Motion

| Tell | Why | Override |
| --- | --- | --- |
| Everything fades in on scroll | Motion without motive; slows reading | Animate the 1–2 moments that carry the story |
| Animated command palettes / menus / keyboard actions | Fights the user hundreds of times a day | Never |
| `scale(0)` entrances, bouncy overshoot everywhere | Cartoon register | Springs with bounce only in gestures/playful moments |
| Parallax + marquee + counter + typewriter on one page | Effects catalog, not design | ≤1 marquee; each effect must have a stated purpose |
| `transition: all` | Accidental animation of layout properties | Never — name the properties |
| Hover states that shift layout (scale on cards in grids) | Reflow jitter | Use color/opacity/shadow; scale only where layout is isolated |

## The self-tests

- **Squint test**: blur your eyes — do headline/body/label still separate?
- **Swap test**: set this next to the product's best existing surface —
  same family?
- **Signature test**: point to the one element that makes this *this*
  product's UI. If you can't, it's a template.
- **Token test**: read the CSS variables aloud — do the names belong to
  this product or to a framework?
- **Twin test**: would another model, given a similar prompt, produce
  roughly this output? If yes, you shipped the median.
