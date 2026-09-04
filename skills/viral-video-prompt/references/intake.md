# Intake — turning a request into a brief

Phase 0 in full. Ends with `00-brief.md` written and the tier announced.

## Read the request literally

Take the product noun phrase apart and keep every modifier **verbatim**. These
become the product truth that every prompt must carry, and `check_pack.py`
enforces them, so write each one in backticks under `Given attributes` in the
brief.

A prompt written in another language should not have to carry the original
token, so write the accepted spellings on the `Attribute equivalents` line and
the gate takes any one of them:

```text
- **Given attributes**: `藏青`, `10寸`, `午餐包`
- **Attribute equivalents**: 藏青 = navy = deep navy blue; 10寸 = 10-inch = 25 cm; 午餐包 = lunch bag = insulated lunch bag
```

An equivalent must be the same attribute in another language or notation. A
looser word is a different product: "dark blue" is not 藏青, and "cooler" is not
午餐包.

| Request | Given attributes | Do not silently change |
| --- | --- | --- |
| 一个女士白黄色的托特包 | `女士`, `白黄` (white and yellow, two-tone), `托特包` (tote) | into "cream", "beige", "handbag" |
| 一个10寸藏青色的午餐包 | `10寸`, `藏青` (navy), `午餐包` (insulated lunch bag) | into "10-litre", "dark blue", "cooler" |
| 一支子弹头的最新口红 | `子弹头` (bullet-shaped case), `最新` (a launch, not a staple) | into "lipstick tube" without the shape |

A modifier you cannot render (a size in inches has no visual) still stays in
the brief and becomes a **scale cue** in the prompt: something in frame that
reads the size, such as the bag beside a laptop or a hand.

`最新` / "newest" / "just launched" is a *positioning* attribute: it makes
launch-shaped hooks (first look, drop, restock) legitimate and rules out
"everyone already has this" framing.

Anything you infer rather than read is marked `[inferred]` in the brief and
may be corrected by the user; anything you read is never overwritten.

## Inventory the inputs

Write one row per input in the brief. The inputs decide which generation mode
each prompt targets, which is a bigger lever than any wording.

**Images.** Look at every one. For each, record: what it shows, the angle,
background (cut-out on white / in-scene / lifestyle), lighting, whether a
person or hands appear, whether the logo or printed text is legible, and the
role it can play:

| Role | What the image must be | Feeds |
| --- | --- | --- |
| first frame | the exact opening composition you want, already 9:16 | image-to-video |
| subject reference | the product clean and unambiguous, ideally several angles | reference-to-video |
| style reference | the light, palette, and set dressing to imitate | style words in the prompt |
| last frame | the end card or beauty shot | first-last-frame mode |

Several images of one product are a subject reference set. Several images of
*different* things (product, model, location) are a multi-reference set, and
each reference's job is named in the prompt in whatever syntax the model's
dialect file gives.

When the runtime cannot show you an image, run the `inspect-media` skill or
ask the user for a one-line description of each; never guess what a product
looks like from its name.

**Reference video.** Facts first, opinion second:

```sh
python3 <skill-dir>/scripts/inspect_video.py <video> --out <pack>/assets/ref-1
```

It writes `meta.json`, `summary.md`, one frame per second, and `sheet.jpg`.
Read `sheet.jpg` for the arc, `frame_01.jpg` for the hook frame, then fill a
Viral DNA card (`references/viral-craft.md` §DNA card) from what is visible.
Duration, cut count, and average shot length come from `meta.json` and are
quoted as measurements, not impressions. Audio you have not transcribed is
recorded as unverified.

Ask what the reference video is **for**, because the answer changes everything
downstream, and infer it when the user already said:

- *"make something like this"* → copy its DNA into both concepts, vary the rest.
- *"this is my product in use"* → it is footage evidence of the product, not a creative model.
- *"this is the competitor"* → it is a reference to beat; concepts must differ from it deliberately.

Without ffmpeg, ask the user for three screenshots (first frame, middle, end)
and work from those, saying in the brief that timing facts are unverified.

**Links.** A product page yields materials, dimensions, price, and the claims
the brand already makes. Fetch it. A social link yields a reference video: fetch
its stats when the platform exposes them.

## Choose the platform, market, and language

These decide the hook library, the compliance rules, and the language of the
on-screen text. Infer, then say what you inferred:

- The request's language is a weak signal about the *market*: Chinese sellers
  commonly target TikTok Shop US. Treat it as a real fork, not a default.
- A price in ¥ or a Taobao/Douyin link means the domestic market; a price in $
  or an Amazon/TikTok-Shop link means overseas.
- On-screen text language follows the market, never the conversation.

## Ask at most four questions, once

Ask only when two readings lead to materially different work. Put every
question in one message, offer a default for each, and proceed on the defaults
if the user does not answer. The ones that usually qualify:

1. Market and platform, when nothing in the request or links settles it.
2. Whether a real person may appear on camera, when the category has both
   product-only and creator-led formats that win.
3. A brand constraint that would invalidate a concept (a tone, a claim that is
   forbidden, a required logo lockup).

A fourth question earns its place whenever the product is physical and no image
came with the request: **ask for one product photograph.** Text-to-video
describes a product the model has never seen, so colour, proportions and
hardware are all free to drift. One photo moves every prompt from text-to-video
to a reference mode and is the single largest quality lever in the run. Ask it
in the same message; if nothing arrives, record `Unpinned: no reference image`
at the top of the brief and proceed.

Everything else is an assumption written into the brief. Model choice, hook
choice, and format choice are yours to make; they are what the user is asking
for.

When research later hits a wall that only the user can open (no reference
videos found for a niche category, a needed stat behind a login), say what you
tried, what you assumed instead, and what would sharpen the next pack. Ask
after trying, never instead of trying.

## Pick the target models

Default: `universal` plus every model the user named. When the user names none,
produce `universal`, `hailuo`, `wan`, and `seedance`, because the request
usually goes to whichever is available that day.

Each model needs a dialect file in `references/models/`. A model with no
dialect file gets the universal prompt plus a line saying its dialect is
unverified: never invent a syntax.

## Triage the research

| Tier | When | Sources opened | Reference videos | Time |
| --- | --- | --- | --- | --- |
| express | the user says quick, or the category is one you already researched in a prior pack in this session | 3–6 | 3–5 | one round |
| full | default | 10–20 | 8–15 | two rounds |

Announce the tier in one line. Move up when the category turns out to be
unfamiliar or the references disagree; log the move in the brief.

## Create the pack

```sh
mkdir -p <root>/<YYYY-MM-DD-HHMM>-<slug>/{prompts,assets}
```

`<root>` is, in order: the path the user named; an existing `docs/viral-video/`
or `viral-video/` directory in the working tree; otherwise a new
`viral-video/` under the working directory. Look for the existing directory
rather than inferring a convention. `<slug>` is three or four words from the product. The timestamp makes
every run a new directory, so no pack ever overwrites another. Copy the user's
images and videos into `assets/` so the pack stays readable on its own.

A pack that supersedes an earlier one names it in `00-brief.md` under
`Prior pack` and says what changed.
