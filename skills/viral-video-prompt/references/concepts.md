# Concepts — designing two bets and a beat sheet

Phase 3 in full. Ends with `02-concepts.md` written and both concepts through
the critic pass.

## A and B are two bets, not two wordings

Each concept is a stated hypothesis about **why a stranger stops scrolling**.
Write the hypothesis before the beats:

> A bets that the capacity question is what stops a commuter: showing five
> containers disappear into a bag that looks too small answers it in 3 seconds.
> B bets that the sticker shock is what stops them: three bulky rivals with
> visible prices, then the one they can afford.

An A/B test only pays when the arms differ on the *mechanism*. Two openings
that both reveal capacity, one with a hand and one with a countertop, test
nothing you can act on.

**Choose the pair this way**: from the ranked DNA, take the mechanism that wins
most often in this category — the **convention bet** — and one mechanism proven
in a neighbouring category but rare in this one — the **transplant bet**. The
test then answers a question worth answering: does the category's convention
beat the import? Two conventions, or two imports, waste the run.

Where the ranking is thin (few references, weak numbers), say so and make B the
safer of two conventions, rather than inventing a transplant with no evidence.

### Creative mechanisms

The mechanism is *how the ad constructs meaning*, and A and B must draw from
different ones. Pick from:

| Mechanism | The move |
| --- | --- |
| Product demonstration | cause and effect: the product visibly changes an outcome |
| Life insight | enter through a familiar moment the audience has never heard named |
| Visual metaphor | turn an abstract claim into one physical world that develops |
| Contrast or reversal | establish a wrong expectation, let the product flip it |
| Emotional narrative | the product changes a relationship or a feeling |
| Sensory amplification | build the whole clip around texture, sound, or speed |
| Brand worldview | behaviours and visual rules that could only be this brand |

### The frame-one claim

**The hook is a claim the camera can settle, made in frame one.** Not a mood,
not a card over a pretty shot — a proposition a stranger can see being tested.
"比电脑还窄" over a tote visibly narrower than the laptop beside it is a claim.
"13寸站着放" over a hand lowering a laptop into a bag is a caption on wallpaper.

The move that generates one, almost every time: **make the product look
inadequate for the job first, then resolve it.** The container looks too small.
The object will not fit. The rival is the obvious choice. Tension in the image
is what the card then pays off — a card carrying the tension by itself is the
commonest way a competent concept fails.

**The shape the claim has to take, or the model will not render it.** Ten real
generations across three families settled this. A claim survives into frame one
when it is **one dimension, compared between two objects that touch or share a
baseline**: the bag's top line against the laptop's top line, both standing on
the same desk. All three families rendered that comparison, from three different
prompt dialects, with the margin visible. What did not survive, in the same run,
from prompts written just as carefully:

| Claim shape | What the model returned |
| --- | --- |
| one dimension, two touching objects | the comparison, legibly, every time |
| area or volume — "this row of food is wider than that box" | the row compacted into a tidy group beside a box that looks big enough |
| count or arrangement — "both states in frame one" | a handsome flat lay with no tension in it |
| an intermediate state — "a zip already moving, salad showing in the gap" | the zip closed, the gap gone, the reversal carried only by the card |

Two rules follow. **Compare one dimension, not a quantity.** The viewer reads
height against height pre-verbally; area and volume need arithmetic and the
model needs latitude it will use against you, because it is free to arrange
loose objects compactly and it will. **Ask only for canonical object states** —
fully open, fully closed, upright, flat, on its side. A claim that depends on
half-open, ajar, mid-travel or partly visible through a gap is a claim you are
not going to get.

### Four tests, and they are allowed to fail

These are gates, not paperwork. A failure stops the concept.

**The generic-swap test.** Strip the product name from the concept sentence. If
a competitor could use it unchanged, the concept is too broad, and "a premium
looking frame" is not a hook. Judge it against the *branded competition the clip
actually scrolls past*, not against the worst product in the price tier.

**The competitor-frame test**, which is where the concept gets its edge: **name the single frame
a competitor physically cannot shoot, and put it in frame one.** If the answer is
a frame at second seven, the concept is built backwards. If there is no such
frame, there is no concept.

**The glance test**, which is the one a careful concept fails. Cover the
on-screen card. Freeze frame one. **Can a stranger take the claim in without
scanning the frame and without reading anything?** Not "is it interesting" —
is it *perceived*, in the fraction of a second before the thumb decides. A
comparison between two adjacent objects passes. An arrangement the viewer has
to inventory does not, however true its argument is.

This test exists because the other three do not catch the failure. They all
measure how *distinctive* a concept is, and a concept can be perfectly
distinctive and still be invisible at scroll speed. In the run that produced
this rule, one concept passed generic-swap and competitor-frame with real
reasoning behind both verdicts — its frame one genuinely was a frame no
competitor could shoot — and rendered as a top-down flat lay whose tension no
viewer would ever find, because the argument was "the flat closed bag and all
of its contents are in shot at the same time" and nobody infers that at speed.
Write the verdict as `pass` or `fail` like the others, and name what a stranger
sees in the first fraction of a second, in one clause with no product knowledge
in it.

**The hook restatement test.** Complete this: *"In the first frame I see ____;
within three seconds ____ happens; that makes me want to know ____, and it
points at the product's ____."*

**What a failure obliges you to do.** Redesign the concept and record that you
did. A failure you cannot design out is escalated verbatim into the opening lines
of the pack README, where the seller reads it before generating — never recorded
in `02-concepts.md` and shipped as if noting it were the same as fixing it. Write
the verdict as the literal word `pass` or `fail` next to each test so the record
cannot be read two ways.

## The difference matrix

Fill it before writing any beats. A and B must differ on at least four rows,
and `check_pack.py` counts them.

| Axis | What varies |
| --- | --- |
| Hook mechanism | the reason the first second holds: curiosity, shock, satisfaction, identity, conflict |
| Format / genre | ASMR, demo, review, POV, before-after, comparison, story, unboxing |
| Persona / POV | no person, hands only, first-person, on-camera creator, and who that creator is |
| Emotional lever | satisfaction, aspiration, thrift, belonging, relief, humour |
| Tempo | shot count and cut cadence over the same duration |
| Sound design | ASMR-forward, music-forward, voice-forward, silence-then-hit |
| Product hero moment | which single second sells it, and how the product is framed then |
| CTA type | none, implied, on-screen text, spoken, end card |

Shared across both, always: the product truth, the platform, 9:16, and the
duration class. Changing those turns the test into two unrelated videos.

## The beat sheet

Every concept is a table before it is a prompt, one row per beat, seconds
explicit. A prompt written without one drifts into atmosphere and loses the
hook.

| t (s) | Shot | Action (one verb) | Camera | Product on screen | On-screen text | Audio |
| --- | --- | --- | --- | --- | --- | --- |

Rules that hold in every category:

- **The product is in the first shot.** Not the second. A hook that withholds
  the product works for a 30-second ad and dies in a 6-second clip.
- **One action per shot**, and one commercial job per shot. Two verbs in one
  shot is the most common cause of a smeared, physically wrong generation.
- **One camera move per shot**, and the move serves the action rather than
  decorating it.
- **Write the physics, not the word "realistic".** The beat sheet's Action column
  holds the one verb that names the beat; the prompt then spells that verb out as
  approach, contact or weight shift, resulting motion, and settle. Cause before
  reaction, contact before motion. One verb in the table, four phases in the
  prompt, is the intended shape.
- **Each beat inherits the previous beat's state**: which hand holds what,
  whether the lid is open, how many objects there are, which way things travel.
  When something is hidden behind an obstruction, say what returns unchanged, or
  the hidden interval becomes a reset.
- **Let a completion state be seen.** Hold the end of an action for a beat, or
  let the next shot open on it, rather than cutting on the movement.
- **The last frame is a decision**: an end card, a beauty shot, or a loop back
  into frame one. Say which.
- **Write the last beat as a full inventory, including what is absent.** State
  inheritance is an instruction to you, not to the model — the model gets one
  sentence per beat and no memory of the earlier ones, so a final beat that only
  says what the camera does will get whatever end state the model finds most
  photogenic. Spell out, in the prompt text: the product open or closed, what is
  inside it, where the hands are, and **what is no longer on the surface**. The
  absent half has to be positive prose (*"the counter behind the bag is bare, and
  nothing that went in is outside it"*), because none of these families supports
  a negative prompt. Ten real generations, four of which specified a closed
  product in the last frame: three came back open, one came back with the packed
  food sitting outside the bag again, and one reset the whole load back onto the
  counter. Every one of those five last beats described the camera and the card
  and left the inventory implied.
- **Beats fit the duration.** Work back from the model's allowed durations
  (`references/models/limits.json`), never from a story you then have to trim.
- **Generation settings stay out of the prompt text.** Duration, aspect ratio,
  resolution, and the model's own name belong in the settings table. Two
  exceptions, both of which the dialect files take: a model whose prompt format
  encodes timing carries its timestamps, and a family whose own skeleton opens
  with a duration or an orientation phrase keeps it. Where a dialect file and
  this rule disagree, the dialect file wins.

## Critic pass

Run all four before writing prompts. Each finding gets a fix in the beat sheet,
and the finding plus fix goes into `02-concepts.md` so the reasoning survives.

**Retention.** Where would you scroll? Name the weakest second and fix it. The
usual weak second is the one after the hook resolves and before the payoff
starts.

**Generation.** What will the model break? Take the fix from the table below
into the beats, rather than hoping the prompt is lucky.

**Fidelity.** Would a buyer still recognise the product they will receive? A
concept whose beauty shot needs a colour, a proportion, or a finish the product
does not have is a returns problem, not a creative choice.

**Compliance.** Category claims (medical, cosmetic, food safety), platform
policy for the market, and AI-content labelling where the platform requires it.
When a claim is central to the hook and cannot be made, replace the hook.

## Generation-risk table

What current text-to-video models break, and the prompt-side move that avoids
it. Confirm the model-specific entries against the dialect file before relying
on one.

| Risk | Symptom | Move |
| --- | --- | --- |
| Rendered text and logos | garbled letters, invented brand marks | keep words out of the video; put copy in the platform's caption or sticker layer; when text is essential, use image-to-video from a frame that already contains it |
| Invented branding on the props | a garbled logo on a can, a wrapper, a box — anything the exclusion did not name | exclusions scoped to the product do not protect the set. Choose prop classes that are unbranded in real life, then write the exclusion over the whole frame, not the product |
| **A real trademark on a prop** | naming a laptop produced a correct, sharp **Apple logo** in three of four videos, straight through a frame-wide exclusion that forbade brand marks anywhere | an exclusion is a request; the prop class is a constraint, and a class whose every training photograph carries a logo will carry one. **Substitute the class, and write the substitution out**: a plain unmarked slate-grey panel of laptop size, not "a 13-inch laptop"; a plain glass bottle, not a soft-drink can; a plain white gel pack, not a commercial ice pack; loose fruit over anything packaged. A garbled fake logo is a blemish — a real trademark is a takedown |
| A card with a space in it | one card rendered as two, in two positions, one of them re-wrapped — one of two spaced cards in a real run | give every on-screen string exactly one position, and carry a wanted break on punctuation rather than a space, or move the line to the platform's text layer |
| A card competing with a spoken line | the model captions the speech and drops the card, so the hook ships as a long bottom-band subtitle instead of a short top card | never put a card and a spoken line saying the same thing in one beat. If the beat has dialogue, design the caption it will generate |
| A seam instead of a cut | a strip of a different scene composited along one frame edge, churning for seconds | happens when several cuts are asked of a family that does not cut. Ask for one continuous move; see the row below |
| Hands on small objects | extra fingers, objects passing through skin | fewer fingers in frame, one contact point, slow motion, hands entering from the edge rather than fully visible |
| **A mechanism as the hero action** | the zip, buckle, clasp or catch never operates. The state teleports: a hand touches the pull, and the next frame is closed, with no slider travelling and often no hand left in shot | **never nominate a mechanism as the hero moment.** These models render *states* and morph between them; they do not animate a small rigid part translating along a track. Make the state change the hero and hide the mechanism — see the four moves below |
| A state change with no agent | a lid closes itself, an object moves with nothing touching it, the load repacks | every change of state names the hand that causes it, in the same clause as the change. A beat that says what the object does without saying who does it will be rendered without anyone doing it |
| Hand-to-fabric contact | fingers interpenetrate the edge instead of occluding it; the hand becomes a blob over the thing it grips | the hand approaches from the frame edge and stops at contact; the *product* moves in response rather than the hand moving through it. Keep the grip point at the silhouette edge, not against a busy interior |
| Small hardware between states | a front-pocket zip, a mesh pocket or a strap present in one second and gone the next | name the hardware once, in the product clause, and keep the camera off it during any state change. Hardware survives a static frame and a slow move; it does not survive a morph |
| Product identity drift | shape or colour changes mid-clip | image-to-video or subject reference; avoid rotations past 90°; never let the product leave frame and return |
| Fine straps, chains, handles | melting, merging with the background | hold them still while the camera moves, and keep them against a contrasting background |
| Gloss, liquid, powder | physics artefacts, unnatural flow | macro framing, slow move, short beat |
| Speech without native audio | mouth flaps that match nothing | keep the mouth out of frame, or choose a model with native audio, or hold the line for post |
| Multiple people | identity drift between shots | one person, or people whose faces stay out of frame |
| Cuts in a single-shot model | ignored, or a smeared morph | one continuous move per generation; edit separate generations together |
| A described set across separate generations | three segments naming a byte-identical setting returned three different rooms, and another three returned three different wood surfaces | **a described set does not survive assembly.** Three things that do work, all observed in the same run: design the change into the story so a new surface reads as a new scene; shoot on a seamless studio ground, which has nothing in it to drift; or supply a photograph of the set as a reference plate. Never rely on identical prose |
| Cuts anywhere | the count you asked for is not the count you get | across ten real generations asking three cuts each, one clip hit three, three came back as single takes, and one churned to eight. The beats landed anyway. So **time the beats and let the cut be optional**: write the sheet so a single continuous take still shows every beat, and treat cutting as a post decision. Never hang a beat on a cut happening |
| Mirrors and glass | ghosting, doubled products | avoid reflective set dressing near the product |

**Exclusions are a fixed list, not an essay.** A controlled study found a
comprehensive fixed negative set matches per-prompt adaptive negatives, and that
adding negatives measurably *lowers* the dynamic degree — the amount of motion.
For a clip whose job is to stop a scroll that trade matters. Keep one short
standing exclusion list per family, and add a line only for a risk this concept
actually carries. None of the three target families has a negative-prompt field,
so the list is written inline at the end of the prompt.

### Large soft deformation, never small rigid articulation

This is the one sentence that predicts most of what these models get wrong with
a product in a hand: **they are good at large soft deformation and bad at small
rigid articulation.** A bag mouth widening, fabric creasing, a wall bulging
under a load, a strap falling — all reliable, because they are big continuous
changes to a soft body. A zip slider travelling a track, a buckle latching, a
clasp turning, a snap engaging, a hinge closing — none reliable, because each is
a small rigid part with an articulated relationship to another part.

Ten real generations put this beyond doubt for zips. In one clip a hand pinched
the two zip pulls, and the very next frame was the bag closed, hand gone, with no
travel in between. In another the lid rotated shut with nothing touching it. In a
third the fingers interpenetrated the bag's edge and became a blur over the
slider. No clip in the run animated a zip.

Four moves, in order of preference:

1. **Cut the mechanism out of the clip.** Show closed, then a hand arriving, then
   open. Two canonical states with an agent between them is a change the model
   renders every time, and the viewer supplies the zip themselves.
2. **Put the mechanism in the audio and keep it off camera.** Native audio
   renders foley convincingly — a zip's travel, a buckle's click, fabric
   settling — while the picture is on the hand or the interior. The sound sells
   the action the picture is not attempting. This is the cheapest fix available
   and it is under-used.
3. **Occlude the moving part.** Let the hand cover the pull for the whole travel.
   What is hidden cannot be rendered wrong, and this is how real product video
   shoots it anyway.
4. **Move the soft thing instead of the rigid thing.** Rather than a slider
   travelling along a still bag, hold the hand steady and let the mouth widen
   around it. The large deformation carries the same information and it is the
   thing the model is good at.

And the rule that makes all four unnecessary when you can follow it: **do not
nominate a mechanism as the product's hero moment.** If the hero is "the two
metal zip pulls travelling together", the most important two seconds of the clip
are aimed at the one thing that will not render. Aim them at the load standing
in the bay, the lid lying flat over a full load, the counter left bare — results,
which are states.

**Every state change names its agent.** A beat that says *the lid folds flat*
will be rendered with the lid folding itself. Write *the hand folds the lid
flat*, in the same clause, every time. This is the same discipline as the final
inventory rule: the model has one sentence and no memory, so anything the
sentence leaves implied gets invented.

**Scope the exclusion to the frame, not to the product.** "No lettering on the
bag" leaves every prop free to grow a logo, and in a real run the props took
the invitation: a soda can and an ice pack both arrived carrying invented
branding in garbled type. Write it as *no lettering, numbers or brand marks
anywhere in frame, on the product or on anything else* — and pick props that do
not want a label in the first place, because an exclusion is a request and the
prop class is a constraint.

## Copy inside the concept

- **On-screen text** is short enough to read at scroll speed: about three to
  five words per card, and never more cards than there are beats.
- **A spoken line** runs about two and a half to three words per second; a
  6-second clip holds roughly fifteen words including a breath.
- **The caption is not the video.** Long copy, the offer, and the disclaimer
  live in the platform caption where they cost no screen time.
- Write copy in the market's language, chosen in the brief, not the language of
  the conversation.

## A/B test plan

Close `02-concepts.md` with the plan, because a pack without one produces two
videos and no learning.

**Be honest about what two variants can settle.** At realistic budgets, two
creatives will not reach statistical significance on a purchase metric:
detecting a 20% lift on a 1% baseline needs tens of thousands of impressions per
arm. The readable signal sits upstream, where volume is cheap.

- **Read the ladder in order**: hook rate (three-second views over impressions),
  then hold rate (completions over three-second views), then cost per action.
  A concept that loses on hook rate is settled; one that wins on hook rate and
  loses on cost is a different lesson.
- **Respect the platform floors**: change one variable, run at least seven days,
  and give each arm enough events that the platform's own optimisation leaves
  its learning phase, which is roughly fifty conversions in a week.
- **Held constant**: model, settings, seed policy, caption, posting window.
- **Decision rule** written before the run, including the result that means
  *neither* concept worked and what the next pack should change.
