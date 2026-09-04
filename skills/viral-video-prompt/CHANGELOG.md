# Changelog

## 2026-09-04 — assembly, and an audio rule that was wrong

Eighteen generations, 163 s, $3.27, all H3 Max at `768P`, one draw per prompt.
Four assembled videos of 24.8 to 32.0 s, each cut from three or four separate
generations. The run's purpose was to test the rules added earlier the same day.

**They held.** Zero mechanisms attempted, zero agentless state changes, zero
wrong end states, zero doubled or wrong cards, and every one of the seven cuts
landed where the change map put it — against five of ten clips carrying at least
one of those defects in the morning run. Cost per finished second fell from $0.73
to $0.10.

**The audio rule added that morning was wrong, and is replaced.** It said: a
voice-free design comes back flat, so nominate one sound as the loudest event.
Tested: five segments whose audio line read *"No music at all"* or *"No music, no
voice"* came back at **−47 to −60 LUFS** — silence with dither, cumulative RMS at
the −63 dB noise floor, **no foley at all** — each of them having named a
transient and declared it loudest. Every segment in the same session that named a
music bed came back at −14 to −17 LUFS. The corrected rule: **always name a music
bed; name an instrument and a tempo; never qualify its level.** The five
rewritten segments proved the last clause too — *"at a very low level"* landed at
−22 to −40, still unusable, because the model obeyed the adjective.

**A described set does not survive assembly.** Concept A's three segments carry a
byte-identical setting clause and returned three different rooms; concept B
returned three different wood surfaces. The assumption in the pack — identical
wording so the cuts read as angle changes — is disproven. Two things in the same
run did work and are now the rule: **design the change into the story** (concept
C's surface change reads as a week change) or **shoot on a seamless ground**
(concept D, four segments, zero drift, because there is nothing in it to drift).
A third option, supplying a photograph of the set as a plate, is untested.

**A real trademark defeated a frame-wide exclusion.** Three of four videos put a
sharp Apple logo on the device against a line forbidding brand marks anywhere in
frame. The morning's rule said to choose prop classes that are unbranded in life
— and was not enough to stop the prompt naming "a closed silver 13-inch laptop".
So the rule now **names the substitutions**: a plain unmarked slate-grey panel of
laptop size, a plain glass bottle over a soft-drink can, a plain white gel pack
over a commercial ice pack. A garbled fake logo is a blemish; a real trademark is
a takedown.

**One prompt in thirteen came back letterboxed** — 768×1214 of picture inside the
768×1344 frame — and repeated it on a second generation, so it is a property of
the prompt. Recorded in `hailuo.md` with what it correlated with, and the pack
README now carries a `cropdetect` step.

**The gate learned the shapes a real request takes.** It was built for an A/B
pair and the user asked for four concepts, so it reported no difference matrix
found and demanded a B that was not missing. Now: the matrix accepts one axis
column plus any number of concept columns; concept letters must form a
contiguous run from A but may run past B; prompt files may be named
`<LETTER>-<slug>.md` for a concept-per-file pack, which is what an assembled
multi-segment video needs; the glance test may be answered `n/a` **with a stated
reason**, because forcing a product film to claim a pass is worse than letting it
say why the test does not apply; and every per-concept check now reads wrapped
markdown bullets rather than physical lines, which is what made the justified
`n/a` invisible in the first place.

## 2026-09-04 — the creative core, and why zips do not zip

Two criticisms from the user, both correct, both structural.

**"这套 Skills 根本没弄懂什么叫爆款."** The skill had a hook library, beat sheets
and a DNA card, and none of it made the decisions that actually shape a script.
Added `references/viral-anatomy.md`, now the first thing Phase 2 reads:

- **Tear a winner down before borrowing from it.** Six lines per reference, and
  the sixth is what transplants against what is the product's own affordance. A
  DNA card without that line is a citation pretending to be evidence.
- **The metric decides the script.** Views, saves, comments and shares reward
  endings that contradict each other — a clip that resolves is replayable and
  unsaveable; one that ends on a question earns comments and loses completion.
  Each concept now names its target metric and the metric selects the ending.
  Splitting the A/B pair across two metrics teaches more than pointing both at
  completion.
- **Rhythm: changes, not cuts. This is not cinema.** Something must change every
  two to three seconds, and the platform's own bag example uses eleven angles.
  The old sheets were four shots in fifteen seconds — a change every 3.75 s,
  below the floor. But asking for more cuts does not work: ten real generations
  asking three cuts each returned one clip with three, three single takes and one
  torn frame. So the budget is now **changes** — an object entering, a hand
  arriving, a state flip, a scale jump, a card, a camera move — of which one or
  two may be cuts. Fifteen seconds wants seven to nine, no state holding past
  three seconds.
- **种草, made mechanical.** An attribute → proof table: what makes size,
  structure, colour, texture, softness, weight, insulation, sound, scene fit and
  organisation *felt*, which comparison object makes each legible, and whether an
  AI clip can prove it at all. Scale, structure, texture and organisation render;
  weight and softness render weakly; temperature does not render.
- **Audience as a segment, not a category**, with the Western-market numbers.
  Totes: women 25–55 are the primary oversized-tote buyers and 68% buy for
  multi-use, only 39% of women 18–34 carry a bag to work at all, and 41% put
  design first. Lunch bags have **at least three segments with contradictory
  priorities** — office, healthcare/shift who rate function over aesthetics, and
  meal-prep — and the peak bring-your-own cohort is 42–49, materially older than
  this category's usual casting. Choosing the segment is now the pack's most
  consequential decision, and it is stated.
- **Claims that must not be generated.** Temperature and duration, any measured
  result, a named rival, a person testifying. A generated insulation test is a
  fabricated test result.

**"连拉个拉链都拉不好."** Confirmed by frame-stepping the run, and the diagnosis is
sharper than bad physics: **these models are good at large soft deformation and
bad at small rigid articulation.** A bag mouth widening, fabric creasing, a wall
bulging — reliable. A zip slider travelling a track, a buckle latching, a clasp
turning — not. In one clip a hand pinched the two zip pulls and the next frame
was closed with no travel and no hand; in another the lid rotated shut with
nothing touching it; in a third the fingers interpenetrated the bag's edge. No
clip in the run animated a zip.

Four moves, in `concepts.md`: cut the mechanism out and show two canonical states
with an agent between them; **put the mechanism in the audio and keep it off
camera**, because foley renders convincingly while the picture is elsewhere;
occlude the moving part with the hand; move the soft thing instead of the rigid
thing. And the rule that makes all four unnecessary — **never nominate a
mechanism as the hero moment.** The lunch pack's hero was "the two metal zip
pulls travelling together", which aimed the most important two seconds at the one
thing that would not render.

Also added: **every state change names its agent**, because a beat saying *the
lid folds flat* gets a lid that folds itself; and two more risk rows for hardware
vanishing across a morph and hands interpenetrating fabric.

**Enforced, not just documented.** `check_pack.py` now fails a concept with no
target metric, no audience segment or no proof, and fails a change map with a gap
over three seconds or fewer than three changes. Three new hard-failure invariants
in the protocol (8, 9, 10) and two new quality lines. Suite at 17 tests.

**Not evidenced this pass.** Engagement figures broken out by metric for these
two categories. The Apify budget stood at $4.56 of a $5 monthly cap, so no
leaderboard pull was run. The signal hierarchy is platform-published; the mapping
from signal to script shape is practitioner reasoning and is labelled as a
hypothesis the A/B test exists to settle.

## 2026-09-04 — what ten real generations changed

Ten clips at 15 s from three families (MiniMax Hailuo H3 Max, Wan 3.0, Seedance
2.5), reference-to-video, off two real products with 64 supplied photographs.
Every change below is a thing the renders showed, not a thing a reading of the
prompts suggested.

**The hook, which is where the leverage was.**

- Added the **glance test** as a fourth gate. The three existing tests all
  measure how *distinctive* a concept is. A concept can be perfectly
  distinctive and still be invisible at scroll speed, and in this run both
  concept-B openings passed generic-swap and competitor-frame with real
  reasoning and rendered as handsome product footage with no tension in them.
- Recorded **the shape a frame-one claim has to take to survive generation**:
  one dimension, compared between two objects that touch or share a baseline,
  both in canonical states. All three families rendered "the bag's top line is
  below the laptop's top line" from three different dialects. None of them
  rendered an area comparison, a count, "both states at once", or anything
  needing a half-open zip.
- Corrected the before/after cure in the almost-hooks table. "Put both states
  in frame one" is what produced the weak B arm; the arrangement it invites is a
  flat lay, and a flat lay has to be scanned. Added the row.
- `check_pack.py` now **fails** a pack missing any of the four verdicts, and
  fails a concept whose verdict is `fail` and whose `On a fail` line records no
  redesign. The audit before this run found tests being run as documentation;
  prose asking for better was not enough, so it is mechanical now.

**Generation defects the packs did not design around.**

- **Final-state drift.** Four prompts specified a closed product in the last
  frame; three came back open. One clip put the packed food back on the counter.
  Beat sheets now require the last beat to name the full visible inventory
  including what is absent, in positive prose, because none of these families
  takes a negative prompt.
- **Invented branding on props.** Every exclusion in every prompt was scoped to
  the product, so a soda can and an ice pack arrived carrying fabricated logos in
  garbled type. Exclusions are now frame-wide, and prop classes that are
  unbranded in life are preferred over an exclusion asking a can not to have a
  label.
- **A card with a space in it can render twice.** `"这些 全在里面"` came back as
  two cards at once, in two positions, one of them re-wrapped. Another spaced
  card in the same run rendered correctly, so it is a risk, not a rule: carry a
  wanted break on punctuation instead.
- **A spoken line beats the card it duplicates.** Seedance 2.5 captioned the
  `{}` dialogue and dropped the `【】` card in both beats of both its clips, so a
  five-character card designed for the top of frame shipped as an
  eleven-character subtitle at the bottom. A card and a spoken line must not say
  the same thing in one beat.
- **Cut counts are advisory.** Three cuts were asked of each of ten clips. One
  clip hit three, three came back as single continuous takes, one churned to
  eight with a frame seam. The beats landed regardless, so beat sheets are now
  written to work as a single take and cutting is a post decision.

**Audio, which nothing in the skill had covered.**

- Native audio arrives unmastered: one family clipped above full scale on three
  of four clips, another sat 3 dB under, one clip came back at -22.0 LUFS. The
  pack README now carries a normalisation step to -14 LUFS / -1 dBTP.
- A sound design with no voice comes back flat — loudness range 0.7 and 2.1 LU
  against 11.5 to 20.0 elsewhere. A voice-free concept must nominate one sound
  as the loudest event and give it a visible physical cause.

**Two things the pack-writing agents reported that the renders could not show.**

- The lunch pack shipped engagement figures inherited from an earlier pack that
  had saved no raw responses, so their only support was a transcript. A number
  carried over now needs its own saved response in this pack or an explicit
  `[inherited, unverified]` label, and no concept may rest its case on one.
- Six of the ten clips ran a resolution tier below what their prompt file
  specified — `480p` where both packs asked for `720p` on Wan and Seedance —
  because of a budget decision taken outside the packs. Any judgement of fine
  detail in this run is reading a lower tier than the prompts asked for.

**What held up and was left alone.** Reference-to-video pinned both products
faithfully enough that colour, lining colour, handle construction, zip-pull
count and a mesh side pocket all survived. The two packs' language reads
diverged — English for the lunch bag, Chinese for the tote — and both were
right, each evidenced from the listing itself. Every clip had continuous audio
from frame one, which the hook lines had asked for in those words.

## 2026-09-04 — the audit before the run

The failure modes an independent adversarial audit found by hand, and the
mechanical checks that now reproduce them: a ledger timestamp written from
memory, an Apify line with no `run_id`, a paid call whose response was never
saved, a claimed degradation rung the ledger does not back, a `Must show`
attribute certified but never checked, and a prompt-length check that measured
the negative-prompt block. See `evals/viral-video-prompt/PROTOCOL.md`.
