# Viral anatomy — why a clip won, what metric it won, and how desire is built

Read this before `viral-craft.md`. That file is a library of moves; this one is
how you decide which move, for whom, aimed at which number. A pack that skips
this reads like a competent film brief and sells nothing.

Facts read 2026-09-04. Grades: **A** platform-published or peer-reviewed · **B**
a named dataset with published method · **C** practitioner convention. Sources
at the end.

## 1. Tear a winner down before you borrow from it

A reference with a view count is not evidence yet — it is a citation. Evidence
is the anatomy. For every reference that survives into the ranking, write the
teardown. Six lines, and the sixth is the one that does the work.

| Line | What to write |
| --- | --- |
| Frame one | what is in shot at 0.0, and the claim that composition makes |
| The change map | every visible change with its timestamp: cut, angle, object entering, card, scale jump, state flip. Count them |
| The proof | which single claim the clip actually settles on camera, and how |
| The metric it was built for | views, saves, comments or shares — decided from the ending and the caption, not guessed. §2 |
| The audience it addressed | who is being spoken to, from the framing, the hands, the setting and the copy register |
| **What transplants, and what does not** | the mechanism is portable; the product's own affordance is not. Name both halves |

The sixth line is where most research goes wrong. "Capacity test, 780K views"
transplants nothing, because the reason it worked was a bag that *looks* too
small — an affordance. Write instead: *portable — the two-object scale
comparison in frame one; not portable — the specific incredulity, which needs a
container whose outside understates its inside. Our product has that; a
structured box would not.*

**Do not tear down a clip you have not watched.** A thumbnail plus a title is a
guess. Run `scripts/inspect_video.py` on anything you can download, quote the
measured cut count and shot lengths, and mark the rest as unwatched.

## 2. The metric decides the script

This is the decision most packs never make, and it changes everything
downstream. Ranking signals are not interchangeable: watch time, completion,
replays and shares sit in the strongest tier, with comments, follows and saves
one tier below. [A] But **you cannot optimise all four at once**, because the
endings that earn them contradict each other. A clip that resolves cleanly is
replayable and unsaveable. A clip that ends on an open question earns comments
and loses completion.

Pick one per concept, name it in the concept, and let it choose the ending.

| Target | What the signal rewards | The script shape that earns it | The ending it needs |
| --- | --- | --- | --- |
| **Views / completion** | the clip is finished, then replayed | one claim, posed in frame one and settled by the end; no second idea | resolves, and the last frame matches the first so the loop is invisible |
| **Saves** | "I will need this later" — the clip behaves like a resource | enumerated and countable: *what fits*, *which pocket*, *three ways*. Legible when paused | a summary frame the viewer can screenshot. Everything in one shot at the end |
| **Comments** | conversation, and depth now counts more than count [A] | a genuine open choice the viewer holds an opinion about: which colourway, which size for their commute, whether it works for their job | the question, asked in the last two seconds, about their situation and not about the product |
| **Shares** | "this is for you" — a named person comes to mind | one universally recognised situation, rendered specifically enough to be somebody's | the situation, not the product. The bag is the answer to a life someone recognises |

Two consequences worth stating plainly.

**An A/B pair aimed at the same metric is a weaker test than one that splits
it.** Two hook mechanisms both chasing completion tell you which hook is
stickier. One completion arm against one save arm tells you what the product is
*for* in this audience's hands, which is the more valuable thing to learn.

**Comment-driving has a legitimate form and a brand-destroying one.** The
mechanism people reach for is the deliberate error — misspell a word, hold a
thing wrong — which works because viewers will publicly correct a stranger. [B]
Do not use it. It reads as incompetence attached to your product, and the
platform's own guidelines now penalise rage baiting. [A] The legitimate form is
a real open question the product cannot answer alone: *which of these two would
survive your commute*, *is this a work bag or not*. Ask about the viewer's
situation.

## 3. Rhythm: changes, not cuts. This is not cinema

The failure is real and it is measurable. Videos showing a variety of scenes
converted 38% better than one continuous selling shot, and transitions lift
brand recall 53%. [A] Something on screen should change **every two to three
seconds**; even plain jump cuts every few seconds raise average watch time by 10
to 15 percentage points against a single static shot. [B] TikTok's own
shoppable-video guidance illustrates the standard with a **bag shown from eleven
angles** in one clip. [A]

Against that, a fifteen-second beat sheet of four shots is a change every 3.75
seconds, which is slower than the floor. It is a film brief.

**But do not fix it by asking for more cuts.** Ten real generations asking three
cuts each returned one clip with three, three single continuous takes and one
that churned to eight with a torn frame. These families do not cut on request.
Asking harder produces seams, not rhythm.

So budget **changes**, and spend most of the budget on changes that are not
cuts. A change is anything a viewer notices:

| Change | Renders reliably? |
| --- | --- |
| a new object entering frame | yes |
| a hand arriving or leaving | yes |
| a state flip — closed to open, flat to standing, empty to full | yes, when both states are canonical |
| a scale jump — wide to macro on the same subject | yes |
| an on-screen card appearing | yes, one position, one string |
| a camera move starting or stopping | yes |
| a lighting or setting change | no, not inside one generation |
| a hard cut | unreliably; treat as a bonus |

**Fifteen seconds wants seven to nine changes, of which one or two may be
cuts.** Write them on whole seconds. If the model delivers a single take, the
clip still has its rhythm, because the rhythm was never in the cuts. If you want
true cuts, generate the beats as separate clips and edit them together — that is
also the only way to get a lighting or location change.

**No single state holds longer than three seconds**, including the hook. The
hook's claim is made in frame one and the *first change lands by 1.5 s* — the
claim being legible does not mean the frame may sit still.

## 4. 种草: turn every attribute into something felt

A feature list with no visual proof is on the penalised list, and buyers on
these surfaces are explicitly sceptical: they want to see the thing work before
they pay. [A] Close-ups that show texture make viewers 35% more likely to trust
the product's quality. [B] So the job is mechanical: take the product's
attributes one at a time and convert each into an action a camera settles.

The lever throughout is the **comparison object** — a second thing whose size,
weight or behaviour the viewer already knows. A prop of known size is the most
effective way to communicate scale, and a hand is the strongest of all for
anything carried. [C] Choose props that are unbranded in real life, or they
arrive carrying an invented logo.

| Attribute | What makes it felt | The comparison object | Can an AI clip prove it? |
| --- | --- | --- | --- |
| **Size, capacity** | the thing that should not fit, fitting — or the container looking too small beside the load | a 13-inch laptop, an A4 notebook, a 500 ml bottle, a hand | yes, and it is the strongest available proof. One dimension, two touching objects |
| **Shape, structure** | it stands unsupported, or collapses flat | the same bag in both states, or a rival that cannot hold the shape | yes — a state flip between two canonical states |
| **Colour** | the colour against skin, against a neutral surface, and in one other light | a white surface for truth, a garment for context | yes, but colour drifts. Pin it with a reference image and defend it in the prompt |
| **Material, texture** | a macro of the weave, and the fabric's own behaviour — how it creases, how it falls | none needed; the scale jump is the proof | yes. Macro plus a slow move is the safest shot these models make |
| **Softness, give** | a thumb pressing and the surface returning | a finger, and the return | partly. Contact deforms plausibly; the *return* often does not. Keep it under a second |
| **Weight** | a one-finger lift, a wrist bearing it, the strap not digging in | the loaded bag versus the empty one, on the same grip | weakly. Weight reads through a body's effort, and these clips have no body above the wrist. Prefer a one-finger lift on a full bag |
| **Insulation, temperature** | a probe reading, a time-lapse, ice that has not melted | a thermometer, a clock, a second bag | **no. Do not attempt it.** §6 |
| **Sound** | the zip's note, the buckle's click, fabric settling | none | yes — native audio renders foley well, and it is under-used |
| **Scene fit** | the product where the buyer's day actually happens | the desk, the car seat, the locker, the gym bench | yes for a set; no for a *change* of set inside one generation |
| **Organisation** | one object per compartment, each landing visibly in its own place | the objects themselves, counted | yes, and it is the strongest save-driving proof there is |

Two rules fall out of this table.

**Prefer the proofs in the top half.** Scale, structure, texture and
organisation render reliably. Weight and softness render weakly. Temperature
does not render at all. A concept whose central proof is in the bottom half is a
concept that will not deliver, however good it reads.

**One clip proves one attribute.** Three selling points at fifteen seconds is
the ceiling and one proof is the floor; a clip that gestures at five proves
none.

## 5. Audience: who, specifically, and what they need to see

"Women who commute" is not an audience, it is a category. Write the segment,
its number, and the one thing it needs to see that the others do not. The
segments below are for the Western market; a domestic-China read is a different
document and the brief says which applies.

### Bags and totes

The buyer is older and more practical than the default creative instinct
assumes. Women 25–34 are 32% of US handbag purchasers at about $250 a purchase
[B]; women **25–55** are the primary demographic for oversized totes, and 68%
buy for multi-use — errands, travel, the beach — not for commuting alone. [B]
Only 39% of American women 18–34 carry a handbag to work or school at all. [B]
Totes and shoppers grew 11% while the wider handbag market fell in the same
cohort. [B] On selection, **52% weigh sustainability attributes and 41% put
design and style first.** [B]

| Segment | What it needs to see | What loses it |
| --- | --- | --- |
| Commuter, 25–34, office or hybrid | that a laptop goes in and the bag still looks like a bag, not luggage | a bag that reads as a gym holdall; a bag that only works empty |
| Multi-use, 30–55 | the same bag in two unrelated contexts, and that it survives being over-filled | one aspirational setting; a bag treated as precious |
| Design-led, any age | the material at macro, the line of the bag empty, one restrained colour decision | feature callouts stacked over the product; loud graphics |

**時尚感 is a production decision, not an adjective.** It comes from restraint:
one light source with a visible direction, a surface with real texture, no more
than three colours in frame, the product not centred and not fully lit, and no
on-screen text over the bag itself — which the platform's own guidance asks you
to avoid anyway. [A] It does not come from writing "high fashion, cinematic" in
the prompt, which is on the over-used list.

### Lunch and insulated bags

This category has **at least three segments with contradictory priorities**, and
choosing one is the single most consequential decision in the pack. Office
workers are the largest end-use segment. [B] Healthcare and shift workers value
functionality, cleanability and durability **over aesthetics** — stated
explicitly in the market read. [B] North America is 36% of the global market and
64% of working professionals bring packed meals. [B] And the peak
bring-your-own cohort is **42–49 years old**, 85% of whom bring more often than
they buy [B] — materially older than this category's usual casting.

| Segment | What it needs to see | What loses it |
| --- | --- | --- |
| Office, 28–45 | that it does not look like a lunch box on a desk — the understatement is the product | a cartoon print; anything that reads as a kid's lunch bag |
| Healthcare and shift, 25–50 | capacity for a full shift, a wipeable interior, a strap that survives | a styled tablescape; a beautiful-life framing |
| Fitness and meal-prep, 22–40 | how many containers fit, stacked and counted | a single sandwich; a bag shown half empty |
| Parent packing for a child, 30–45 | the whole lunch going in and the bag closing flat over it | an adult-office register |

**便利 · 性价比 · 颜值 · 高级感, each rendered rather than claimed.**
Convenience is one hand doing the whole task, and never a second hand arriving
to help. Value is the load — the count of what fits, in one frame, so the
arithmetic is the viewer's. 颜值 is the interior: the outside is navy nylon in
every product in the tier, and the lining is where a cheap bag gives itself
away. 高级感 is the hardware at macro and the fabric's grain, held for a full
second, plus the absence of anything printed.

## 6. Claims you must not try to generate

Some proofs require a real shoot, and a generated substitute is either a lie or
a compliance problem.

- **Temperature and duration.** "Cold for 8 hours" is proved with a probe, a
  clock and a time-lapse. Generated, it is a fabricated test result. Several
  marketplaces also prohibit product-effect before-and-after comparisons
  outright, and a supplier's own artwork frequently contradicts itself on the
  hour count. Keep the number out of the video; if the seller wants it, they
  shoot it.
- **Any measured result** — a scale reading, a thermometer, a stopwatch, a
  durability test. The model will happily render digits, and they will be
  invented.
- **A named rival.** A side-by-side against an identifiable competitor is a
  legal exposure and the model will invent its branding anyway.
- **A person testifying.** An AI presenter implied to be a real customer is an
  endorsement problem independent of detection, and it is on the hard-avoid
  list.

What replaces them is the geometric and the countable: what fits, what stands,
what closes, how many. Those are provable in a frame, and they are the claims
this product category can actually win on.

## Sources

- TikTok Shop, *Suggestions for Creating High-Quality Shoppable Videos* — multi-angle
  standard including the eleven-angle bag example, the prohibition on overlaying
  text or stickers on the product, the ban on still-frame content, and the
  requirement that the video's product match the listing. [A]
  https://seller-us.tiktok.com/university/essay?knowledge_id=2816204956665642
- TikTok algorithm signal hierarchy — watch time, completion, replays and shares
  strongest; comments, follows and saves one tier below; comment depth now
  weighted over count. [A] https://blog.hootsuite.com/tiktok-algorithm/ ·
  https://sproutsocial.com/insights/tiktok-algorithm/
- Change cadence and jump-cut effect — a visible change every two to three
  seconds; jump cuts worth 10–15 percentage points of average watch time against
  a static shot. [B] https://www.opus.pro/blog/tiktok-length-format-retention-data
- Retention benchmarks under fifteen seconds — 60–70% average, above 75% strong,
  above 85% exceptional, 2026. [B]
  https://retensis.com/blog/tiktok-retention-rate-benchmarks-2026
- Proof-shot practice and the texture close-up effect — visual demonstration of
  function, texture, size, scale and fit; close-ups and a 35% trust lift; three
  to five angles in performing product videos. [B]
  https://viryze.com/blog/tiktok-product-videos-guide ·
  https://www.3318-creative.com/post/tiktok-shop-creative-production-how-to-make-product-videos-that-convert
- Deliberate-error comment mechanism, and why it is rejected here. [B]
  https://slate.com/technology/2023/02/tiktok-algorithm-engagement-hack-intentional-errors.html
- Rage-baiting penalties under the 2026 community guidelines. [A]
  https://www.auditsocials.com/platforms/tiktok-community-guidelines
- Tote and handbag demographics — Circana June 2023 omnibus (39% of women 18–34
  carry a handbag to work or school), NPD 2024 (women 25–55 primary for
  oversized totes, 68% multi-use), 25–34 at 32% of purchasers and about $250 a
  purchase, totes and shoppers up 11%, 52% sustainability and 41% design. [B]
  https://sgbonline.com/report-younger-consumers-trading-handbags-for-totes-waist-packs-and-backpacks/
  · https://www.fortunebusinessinsights.com/tote-bags-market-111935
- Lunch-bag segments — office workers the largest end use; healthcare and shift
  workers prioritising function over aesthetics; North America 36% of the global
  market; 64% of working professionals bringing packed meals; the 42–49 cohort at
  85% bring-over-buy. [B]
  https://www.indexbox.io/blog/insulated-lunch-bag-market-forecast-points-higher-toward-2035-driven-by-workplace-reopening-and-premiumization-trends/
  · https://www.databridgemarketresearch.com/reports/global-lunch-bags-market
- Scale-prop and hand-as-reference technique. [C]
  https://www.replicasurfaces.com/blogs/q-as/how-can-i-create-a-sense-of-scale-in-product-photos
  · https://beverlyboy.com/filmmaking/how-to-use-scale-contrast/
- Insulation testing method, recorded here as the proof format a generated clip
  must not fake. [C]
  https://www.qualitylogoproducts.com/blog/lunch-bag-cooler-test/

**Not evidenced this pass.** Engagement figures broken out by metric for these
two categories. The Apify budget was at $4.56 of a $5 monthly cap, so no
leaderboard or play-count pull was run, and nothing in §2's table rests on
category-specific engagement data — the signal hierarchy is platform-published,
the mapping from signal to script shape is practitioner reasoning. Treat the
mapping as a hypothesis the A/B test is there to settle.
