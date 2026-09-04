# Concepts — {{slug}}

## Difference matrix

<!-- A and B must differ on at least four rows. Product truth, platform, ratio and
     duration class are shared. check_pack.py counts the rows whose A and B cells differ. -->

| Axis | Concept A | Concept B |
| --- | --- | --- |
| **Target metric** | views/completion \| saves \| comments \| shares | a different one, and say what the split will teach |
| **Audience segment** | <segment, with its number from 01-research.md> | <a neighbouring segment, or the same one addressed differently> |
| Hook mechanism | … | … |
| Creative mechanism | … | … |
| **The proof** | <the one attribute converted into an action, and its comparison object> | <a different attribute, or a different proof of the same one> |
| Format / genre | … | … |
| Persona / POV | … | … |
| Emotional lever | … | … |
| Change density (count, gaps) | <n changes, largest gap n s, of which n cuts> | … |
| Sound design | … | … |
| Product hero moment | <a state or a result, never a mechanism> | … |
| CTA type | … | … |

Shared: <product truth line from 01-research.md §1> · <platform> · 9:16 · <duration class>.

## Concept A — <name>  ·  the convention bet

- **Hypothesis**: <A bets that … is what stops a stranger scrolling, because …>
- **Creative mechanism**: <one from references/concepts.md> · **serves**: U<n>
- **Evidence**: <reference ids V<n> and sources [n] that put this mechanism at the top of the ranking>
- **Target metric**: <views/completion | saves | comments | shares> — and the ending it therefore takes (viral-anatomy.md §2)
- **Audience segment**: <the segment, its number, and the one thing it needs to see that the neighbouring segment does not>
- **The proof**: <one attribute → the action that settles it → the comparison object>. Renders reliably? <yes | weakly — and why it is still the right proof>
- **Frame-one claim**: <the proposition frame one makes, which the clip then settles>
- **Generic-swap test**: **pass | fail** — <the concept sentence with the product name removed; who else could shoot it>
- **Competitor-frame test**: **pass | fail** — <the single frame a competitor physically cannot shoot> · in frame one: **yes | no**
- **Glance test**: **pass | fail** — <what a stranger sees in frame one with the card covered and nothing read, in one clause>
- **Hook restatement**: In the first frame I see <…>; within three seconds <…> happens; that makes me want to know <…>; it points at the product's <…>.
- **On a fail**: <what was redesigned, or the sentence escalated verbatim into the README>
- **Hook (0–1 s)**: visual <…> · text <…> · sound <…>
- **Change map** — one row per change the viewer notices. Seven to nine rows at
  15 s, five at 10 s, three at 5 s. Gaps of two seconds or under. Most rows are
  not cuts: these families do not cut on request. Whole-second boundaries, so
  the beats are identical across model families. Every row whose Change is a
  state change names the hand that causes it.

| t (s) | Change | Kind | Camera | Product on screen | On-screen text | Audio |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | … | state | … | … | … | … |
| … | … | card \| hand \| state \| camera \| object \| cut | … | … | … | … |

  **Change density**: <n> changes · largest gap <n> s · <n> cuts · hero moment is
  a <state or result, never a mechanism>

- **Persona**: <age range, look, styling, energy — matched to U<n>> | none (product-only)
- **Setting and light**: … · **palette**: <product must separate from background> · **props**: …
- **Copy**: on-screen lines (each ≤ <n> words) · spoken line(s) · caption · CTA
- **BGM**: genre · tempo · mood · where it hits
- **Loop or end frame**: …
- **Critic pass**: retention risk → <fix> · generation risk (hands, rendered text, prop branding, mechanism articulation, agentless state change, final inventory) → <fix> · fidelity risk → <fix> · compliance → <fix, and any claim from viral-anatomy.md §6 that had to be dropped>

## Concept B — <name>  ·  the transplant bet

- **Hypothesis**: <B bets instead that …>
- **Creative mechanism**: <a different one> · **serves**: U<n>
- **Evidence**: <where this mechanism is proven, and why it is rare in this category>
- **Target metric**: …
- **Audience segment**: …
- **The proof**: …
- **Frame-one claim**: …
- **Generic-swap test**: **pass | fail** — …
- **Competitor-frame test**: **pass | fail** — … · in frame one: **yes | no**
- **Glance test**: **pass | fail** — …
- **Hook restatement**: In the first frame I see …; within three seconds … happens; that makes me want to know …; it points at the product's ….
- **On a fail**: …
- **Hook (0–1 s)**: visual … · text … · sound …
- **Change map** — one row per change the viewer notices. Seven to nine rows at
  15 s, five at 10 s, three at 5 s. Gaps of two seconds or under. Most rows are
  not cuts: these families do not cut on request. Whole-second boundaries, so
  the beats are identical across model families. Every row whose Change is a
  state change names the hand that causes it.

| t (s) | Change | Kind | Camera | Product on screen | On-screen text | Audio |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | … | state | … | … | … | … |
| … | … | card \| hand \| state \| camera \| object \| cut | … | … | … | … |

  **Change density**: <n> changes · largest gap <n> s · <n> cuts · hero moment is
  a <state or result, never a mechanism>

- **Persona**: …
- **Setting and light**: … · **palette**: … · **props**: …
- **Copy**: …
- **BGM**: …
- **Loop or end frame**: …
- **Critic pass**: …

## A/B test plan

- **Metric ladder, read in order**: hook rate (3-second views / impressions) → hold rate (completions / 3-second views) → cost per action. A purchase-metric winner is not readable at these volumes; say so rather than implying one.
- **Held constant**: model, settings, seed policy, caption, posting window. One variable changes: the concept.
- **Floors**: at least 7 days per arm, and enough events that the platform's optimisation leaves its learning phase (roughly 50 conversions in a week).
- **Decision rule**: <what result picks A, what picks B, and what result means neither worked and the next pack should change X>
