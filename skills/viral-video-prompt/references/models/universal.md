# Universal dialect

The model-agnostic prompt. It is the control arm of the pack and the file the
user pastes into a model nobody here has documented — a new release, a
competitor, an aggregator that hides the endpoint.

It is written to the **intersection** of what every modern video model accepts,
so it must survive being pasted anywhere. That means it carries no family
syntax at all: no `@Image1`, no `Image 1`, no `[Push in]`, no `--dur`, no
`图1`. Assets are described in words.

## Language

Follow the market's language, since the on-screen and spoken copy has to be in
it anyway, and every current model is at least bilingual. When the market is
unclear, write English, which is the widest-supported prompt language.

## Length

Target 400 to 900 characters, and stay under 2000. That is not a vendor limit;
it is the practical floor across the wider field, because plenty of models cap a
prompt at 1500 or 2000 characters and the ones that allow more do not reward it
for a clip of ten seconds. A prompt that needs 3000 characters is a prompt with
too many beats.

## Structure

Six blocks, which are the six every vendor guide asks for under different names.
Keep them in this order: the models that care about order all want style first
and constraints last.

```text
{Medium and look}. A {N}-second vertical {category} product film.

The product is a {given attributes, verbatim}. {Geometry: shape, proportions,
closures, hardware, finish}. {The colour, described so it cannot drift}. Its
silhouette, colour, proportions and hardware stay identical from the first frame
to the last.

0–{t1}s: {one subject action}. {One camera move}. {What is in frame that reads
the scale}.
{t1}–{t2}s: {one action that begins from the previous beat's end state}. {One
camera move}.
{t2}–{N}s: {final action}, settling into {the closing composition}.

Setting: {environment}, {light direction and quality}, {palette}.
On-screen text: "{card 1}" at {t}s. "{card 2}" at {t}s.
Audio: {room tone}. {Foley} at {t}s. {Music: instruments, tempo, where it lands}.
{Spoken line in quotes, with a direction for the delivery}.

{Exclusions, one line.}
```

## What each block must do

**Medium and look.** One declaration, no stacked aesthetics. "Live-action
commercial product film, natural daylight, neutral grade" is a look; "cinematic"
is not.

**Product lock.** Describe the product by geometry and material rather than by
name, then demand consistency explicitly. This paragraph is the only defence
against drift when no reference image exists, and it is where the given
attributes live.

**Timed beats.** Two beats for five seconds, three for ten, four for fifteen.
One subject action and one camera move each. Each beat starts from the previous
beat's end state.

**Setting.** Environment, light direction and quality, palette. The palette line
exists so the product separates from the background.

**Audio.** Room tone, foley with the second it lands, music by instrumentation
and tempo rather than mood, and any spoken line in quotes with a delivery
direction. Say so explicitly when the clip should be silent, since several
models otherwise invent dialogue and a score.

**Exclusions.** One short line at the end. Most models have no negative-prompt
field, and heavy exclusions reduce how much motion any of them produce.

## Camera vocabulary

Plain English verbs that every family understands, written as prose inside the
beat:

- shot size: wide, medium, close-up, macro
- movement: the camera pushes in, pulls out, pans left or right, tracks
  alongside, arcs around, tilts up or down, holds still
- qualifiers: slowly, quickly, slightly, a long way

Avoid a family's own token forms and avoid named film techniques an unknown
model may not have been trained on.

## Reference assets

The universal prompt cannot use a mention syntax, so name the asset by what it
is and what it governs, in words:

```text
Match the product exactly to the supplied product photograph: the same navy
shell, the same zip placement, the same handle length. Take only the lighting
from the second photograph, and nothing of its background.
```

Then say in the settings table which uploaded file is which, so the user can
wire them up in whatever interface they are using.

## Settings table

Fill it with the values the *user's* model actually offers. When the target is
unknown, write the intended value and mark it as intended:

| Setting | Value |
| --- | --- |
| Model / endpoint | any 9:16 video model |
| Mode | text-to-video, or image-to-video when a product photo exists |
| Duration | 10 s intended; use the nearest value the model offers |
| Resolution | 720p intended |
| Aspect ratio | 9:16 |
| Audio | on, if the model generates it; otherwise add it in post |
| Prompt length | *n* of 2000 |

## Do

- Write plain prose that any model can read.
- Lock the product by geometry, then demand consistency.
- Keep one action and one camera move per beat.
- Put a scale cue in frame whenever a dimension is part of the product truth.
- Say what the audio is, including silence.
- Keep the exclusion line short.

## Don't

- Any family's mention syntax, camera brackets, or command flags.
- Named film techniques an unknown model may not know.
- Quality-booster tag stacks such as "8k, masterpiece, best quality", which
  every current vendor guide advises against.
- Text baked into the video when the platform's own text layer will do; a model
  you have not tested is the most likely to garble letters.
