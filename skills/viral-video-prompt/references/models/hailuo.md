# MiniMax Hailuo / H3 dialect

Facts read 2026-09-04 from MiniMax's model card and prompting guide, MiniMax's
video API reference, and fal.ai's endpoint schemas and pricing pages. Re-read
before trusting a limit that decides a prompt.

## Which model

| Name | What it is | Use it for |
| --- | --- | --- |
| **H3 Max** (`minimax/h3-max/*`) | fal's post-trained H3, tuned for prompt adherence | the default for this skill |
| H3 Max Turbo (`minimax/h3-max-turbo/*`) | cheapest and fastest tier | volume A/B batches |
| H3 base (`minimax/h3/*`) | MiniMax's own H3 | when 2K or 4K output is needed |
| Hailuo 2.3, 02, Video-01 | previous generations | only when the user names them; their syntax differs |

"MiniMax H3" is the official name; "Hailuo 3.0 / 03" is the consumer alias, and
"H3 Max" is a real model, jointly released with fal. Endpoint ids sit under the
bare `minimax/` namespace, not the older `fal-ai/minimax/` one.

One consequence worth knowing before you switch surfaces: **fal's `h3-max` is
fal's own post-trained variant**, which is why it exposes reference-to-video
while MiniMax's native `MiniMax-H3-Max` does not. Calling MiniMax directly, the
reference route is on base `MiniMax-H3`.

## The mode decision, and the 9:16 trap

This is the most consequential choice in the file, because it decides whether
you can have a vertical frame at all.

| Mode | Endpoint | Aspect ratio | Use when |
| --- | --- | --- | --- |
| text-to-video | `minimax/h3-max/text-to-video` | settable, default `16:9` | no product image exists |
| image-to-video | `minimax/h3-max/image-to-video` | **no `aspect_ratio` field at all — the output follows the input image** | the supplied image is already vertical and is the opening frame |
| first-to-last frame | same endpoint plus `end_image_url` | follows the input image | the clip must land on an exact packshot |
| reference-to-video | `minimax/h3-max/reference-to-video` | settable, including `9:16` | several product images, or one image plus a forced vertical frame |

**Image-to-video cannot be forced to 9:16.** When the user's product photo is
square or landscape and the output must be vertical, either crop it to 9:16
first, or use reference-to-video, which is the only mode that both anchors the
product and lets you set `aspect_ratio: "9:16"`.

Reference inputs and frame inputs are **mutually exclusive**. Sending both
completes without an error, silently discards one, and still bills. Choose one
family per request.

## Prompt structure

H3 rewrites your prompt through its own context module before generating, so
write for the user layer: natural language, organised as a timeline. Six blocks,
in this order:

1. **Style contract** — medium, finish, palette, era. It opens the prompt.
2. **Timeline** — timed beats that sum to the duration you set. Four or fewer
   for a 15-second clip; two or three for a 6-second one.
3. **Camera** — one behaviour per beat, in the vocabulary below, written as prose.
4. **Audio** — foley, room tone, and the second each cue lands.
5. **On-screen text** — every visible word spelled out in double quotes.
6. **Prohibitions** — inline, because there is no negative-prompt field.

```text
{Style contract}. A {N}-second {category} product film.

0–{t1}s: {beat}. The camera {motion} with {amplitude} at {speed} toward {target}.
{t1}–{t2}s: {beat with a different camera behaviour}.
{t2}–{N}s: {final beat} settling into a centred hero composition.

On-screen text: "{BRAND}".
Audio: {room tone and foley}; {cue} enters at {t}s.
Stable product shape, no hands, no distortion, no extra products, do not
misspell, do not add other text, do not add subtitles.
```

Write the body in English. Dialogue, lyrics, and text that appears on screen
keep their own language, so English direction with Chinese pack copy is normal
and correct.

MiniMax also documents a strict field-schema form —
`integrated_multimodal_description`, `overall_soundscape`, `non_diegetic_music`,
with `[Shot N] At MM:SS.mmm` cut lines and `<d>[Language] …</d>` speech markup —
which is what the context module produces internally. Writing it by hand is a
power-user path for people building their own context pipeline; whether a
hand-written one passes through unchanged is not documented. Emit the user layer
unless the user asks for the schema form.

## Camera vocabulary

A complete camera instruction has three parts: motion type, amplitude, speed.
Amplitude and speed are omitted when medium and normal.

| Motion type | Meaning |
| --- | --- |
| Zoom In / Zoom Out | focal length changes, body still |
| Push In / Pull Out | the camera moves forward or back |
| Pan Left / Pan Right | the lens pivots horizontally in place |
| Truck Left / Truck Right | the camera translates horizontally |
| Tilt Up / Tilt Down | the lens pivots vertically in place |
| Pedestal Up / Pedestal Down | the whole camera rises or drops |
| Arc Shot | the camera arcs around the subject |
| Tracking Shot | the camera follows a moving subject |
| Static Shot | nothing moves |
| Shake Slightly / Shake Strongly | camera shake |
| POV | the subject's point of view |
| Roll Clockwise / Roll Counterclockwise | the camera rolls on the lens axis |

Amplitude: `with small amplitude`, `with large amplitude`. Speed: `at slow
speed`, `at fast speed`.

Write it as an action inside the shot, never as a label stack:

```text
The camera pushes in with small amplitude at slow speed toward the zipper pull.
The camera holds a static shot as the bag settles onto the counter.
```

Bracketed tokens such as `[Push in]` belong to the older Video-01 Director
model. On H3 they are literal text. One camera behaviour per beat; stacking
orbit plus tracking plus push-in is the most-reported failure.

Wide sweeping orbital moves are reported as unstable. Prefer a push, a truck,
or an arc with small amplitude.

## Cuts and shots

H3 handles multiple shots natively. Introduce a cut only when it brings new
information about the subject, space, state, viewpoint, or time; when only the
distance or angle changes, move the camera instead. Phrase a cut as `the camera
cuts to` or `the shot cuts to`.

## Audio

H3 generates video and 32 kHz stereo audio in the same pass, so audio lives
inside the prompt and silence must be asked for explicitly.

- **Dialogue** goes in double quotes at the user layer, with a direction for the
  delivery, because the read matters as much as the words.
- **Music** is described mechanically — instruments, tempo, rhythm, dynamics,
  and when a cue enters. Abstract mood words are ignored, so "tense music that
  builds suspense" buys nothing.
- **Soundscape** covers ambience, physical action sounds, and non-verbal human
  sounds.

Roughly two and a half to three words per second of speech; a six-second clip
holds about fifteen words.

## On-screen text

Text you spell out comes back clean; text you leave unspecified comes back as
letter-shaped noise. Put every readable word in double quotes, then close with
"do not misspell, do not add other text, do not add subtitles" — otherwise the
model invents garbled copy on the packaging itself.

## Reference assets

Cite them positionally, matching the order of the URL arrays: `Image 1`,
`Image 2`, `Video 1`, `Audio 1`. The array order is part of the prompt; save it
alongside.

Give every reference exactly one job, and declare the references authoritative
before describing any motion, so a reference wins every conflict:

```text
Use the uploaded reference images exactly as provided. The reference images are
authoritative.
Image 1 is the product; its silhouette, materials and markings are authoritative.
Image 2 is the environment and lighting only.
Image 3 is the model's hands only.
Do not transfer the colour cast of Image 2 to the product.
```

| Asset | Limits |
| --- | --- |
| Reference images | up to 9 · JPG, JPEG, PNG, WEBP, HEIC, HEIF · ≤30 MB · 256–5760 px · aspect ratio 0.4–2.5 |
| Reference videos | up to 3 · MP4 or MOV, H.264 or H.265 · ≤50 MB · 2–15 s each, ≤15 s total · 23.976–60 fps |
| Reference audio | up to 3 · WAV or MP3 · ≤15 MB · 2–15 s each, ≤15 s total · never the only reference type |
| First frame, last frame | one each, and not combined with any reference asset |
| All types together | at most 12 files, request body ≤64 MB, public URLs rather than base64 |

Downscale product plates to about 1024 px on the long edge. On H3 Max the
reference allowance is token-based: roughly four 1024-pixel images are free,
while a single 2048-pixel image consumes the whole allowance.

Describe the product by geometry and material rather than by name — "wrap
curvature, mirrored surface, streamlined temples" carries more than
"sunglasses" — and demand consistency up front for the silhouette, the finish,
and any engraved or printed marking.

## Parameters

| Parameter | Value |
| --- | --- |
| `prompt` | ≤7000 characters; target 350–500 English words in reference mode, shorter when references carry the description |
| `prompt_expansion_mode` | `balanced` or `quality`; **required on every H3 Max endpoint**; base H3 adds `fast`. Use `balanced` — `quality` adds up to 30 seconds per clip |
| `negative_prompt` | does not exist on any H3 endpoint |
| `prompt_optimizer` | belongs to Hailuo 02 and 2.3, not H3 |
| `duration` | integer, 5–15 seconds on fal |
| `resolution` | H3 Max: `480P`, `768P`. Base H3 adds `2K` and `4K`, which upscale a 768P render |
| `aspect_ratio` | `21:9`, `16:9`, `4:3`, `1:1`, `3:4`, `9:16`, `adaptive` — not settable on image-to-video |
| `seed`, `enable_safety_checker` | as documented |

The submit endpoint validates almost nothing: a wrong MIME type, a dead URL, or
mutually exclusive fields all return success and fail later. Check the request
before sending it.

## Observed on real generations

### Second session, 2026-09-04, eighteen generations at `768P`, assembled

- **Audio is off unless a music bed is named.** Five segments saying "No music at
  all" returned −47 to −60 LUFS with no foley at all, despite each naming a
  transient and declaring it the loudest event. Every segment naming a bed
  returned −14 to −17 LUFS. And do not qualify the bed's level: *"at a very low
  level"* landed at −22 to −40, while *"a warm plucked acoustic guitar figure at
  about 105 BPM"* landed on target.
- **A described set does not repeat across generations.** Three segments with a
  byte-identical setting clause returned three different rooms; another three
  returned three different wood surfaces. A seamless studio ground repeated
  perfectly across four segments, because there is nothing in it to drift.
- **A real trademark defeats a frame-wide exclusion.** "A closed silver 13-inch
  laptop" produced a sharp Apple logo in three of four videos against an
  exclusion forbidding brand marks anywhere in frame. Substitute the prop class.
- **One prompt in thirteen came back letterboxed** — 768×1214 of picture inside
  the 768×1344 frame, 130 px of black split top and bottom — and reproduced it on
  a second generation, so it is a property of the prompt, not luck. That prompt
  was an overhead flat-lay that also referred to *"the same height and framing as
  a previous overhead shot"*. Correlation, not a proven cause; check `cropdetect`
  on every delivered segment.
- **Eleven on-screen cards, all correct**, including an em dash, a deliberate
  two-line card and a seven-word question. Cards are reliable at `768P` when each
  has one named position.
- **Cost per finished second was $0.10** including the regenerations, against
  $0.73 for the previous run's single-generation clips at the same tier.

### First session, 2026-09-04, four generations at `768P`

Four clips, 15 s, `768P`, reference-to-video, 2026-09-04. `768P` returned
768×1344.

- **Product fidelity was the best of the three families.** Colour, lining
  colour, handle construction, zip-pull count and a mesh side pocket all came
  through off a single reference plate.
- **Cut counts are advisory.** Three cuts were asked of each clip; the results
  were 3, 1, 1 and 8. Time the beats, do not hang one on a cut.
- **A card containing a space renders twice.** `"这些 全在里面"` came back as
  「这些在里面」 at the top of the frame and a wrapped 「这些 / 全在里面」 at the
  bottom, simultaneously. One position per card, no internal space.
- **A frame seam is the failure mode at the high end of the cut request.** The
  clip that churned to eight had a strip of a different scene composited along
  its top edge for seconds at a time.
- **Loudness lands closest to platform target of the three** — -12.9 LUFS on
  two clips — but one voice-free design came back at -22.0 LUFS with a 2.1 LU
  range. Normalise before posting.
- English cards spelled correctly; casing drifted once (`Ten inches` versus
  `Ten Inches` across two clips from the same copy).

## Do

- Write a timeline whose beats sum to the duration you set.
- One camera behaviour, one product behaviour, per beat.
- Give each reference one job and cite it positionally.
- Spell every readable word and forbid the rest.
- Write the audio, including the silence.
- Rank the elements when instructions could collide: the product outranks the
  typography.
- Reach for `reference-to-video` when you need both a pinned product and a
  vertical frame.
- Use `end_image_url` when the clip must land on a specific packshot.

## Don't

- Bracket tokens like `[Push in]`, or `prompt_optimizer` — both belong to older
  models.
- Frame inputs and reference inputs in the same request.
- Mood words standing in for camera instructions, or for music.
- More story than the duration carries: one scene, one action, one camera move
  per beat.
- Changing product, wardrobe, location, and camera between two runs, which makes
  the comparison unreadable.
- A long prompt substituting for a good reference image.
