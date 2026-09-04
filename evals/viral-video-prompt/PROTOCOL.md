# viral-video-prompt — acceptance protocol

Behavioral benchmark for the skill. Every skill change reruns this before it
lands. Claims are only as good as the paired no-skill baseline.

## Arms

| Arm | Prompt |
| --- | --- |
| baseline | brief only |
| skilled | full `SKILL.md` (references loaded as the skill directs), then the brief |

Generator: a fresh headless session per run with web search, page fetch, file
tools, `ffmpeg`, and a subagent tool enabled, an isolated working directory, no
prior context. The skilled arm runs twice per brief (stability sample);
baseline once. Archive under `runs/<date>/<brief>/<arm>-<n>/` the whole pack
(`00-brief.md`, `01-research.md`, `02-concepts.md`, `prompts/`, `README.md`),
the chat transcript, and the `check_pack.py` output.

Briefs carrying assets name them under `assets/`; the runner copies that
directory into the working directory before starting, so both arms see the
same inputs.

## Briefs

Frozen in `briefs/`. New briefs may be added; existing ones are never edited,
so runs stay comparable across skill versions.

| Brief | Inputs | Tests |
| --- | --- | --- |
| `tote-bag-bicolor.txt` | text only | a two-tone colour surviving into every prompt; tote not handbag; a gendered audience read without stereotype filler |
| `lunch-bag-navy-10in.txt` | text only | a dimension with no visual becoming a scale cue; navy held against the model's drift to black |
| `lipstick-bullet-new.txt` | text only | launch framing from 最新; the bullet case as a hero shape; cosmetic-claim compliance; gloss and texture generation risk |
| `tumbler-en-us.txt` | text only, English | market and copy language inferred as US; TikTok Shop playbook rather than a domestic one |
| `handbag-with-images.txt` | three product images | mode selection moving to reference-to-video or image-to-video; each image given a role; no invented product details |
| `lunch-bag-with-reference.txt` | one reference video | `inspect_video.py` run before interpretation; measured cut count and shot length quoted; the reference's DNA visible in one concept and deliberately avoided in the other |
| `not-this-workflow.txt` | text only | the activation gate: a detail-page copy request produces copy, not a pack |

## Scoring — invariant violations, then quality

Score the pack and the prompts, not the transcript.

**Hard failures** (any one fails the run):

| # | Invariant | Violation |
| --- | --- | --- |
| 1 | Product truth is invariant | a given attribute missing from, or altered in, any prompt (colour renamed, size dropped, category swapped) |
| 2 | Evidence is real | a cited reference video whose URL does not resolve, or whose quoted numbers are not on the page; a platform claim attributed to a source that does not say it |
| 3 | Model contract | a prompt over its documented character limit, a duration outside the allowed set, another family's syntax pasted in, or a settings table contradicting the dialect file |
| 4 | A and B are different bets | fewer than four differing axes, or both concepts running the same hook mechanism |
| 5 | Instruction-following | supplied images or video ignored; wrong aspect ratio; an existing pack overwritten; the activation gate not honoured on `not-this-workflow` |
| 6 | The record of the work is true | a `requests/ledger.jsonl` timestamp that was written from memory rather than observed; an Apify line with no `run_id`; a claimed degradation rung the ledger does not back; a progress line dated after the file's own write |
| 7 | A failed test changed something | a concept whose generic-swap, competitor-frame or glance verdict is `fail` and which shipped unredesigned and unescalated. Recording a failure is not acting on it |
| 8 | The creative decisions were made | a concept naming no target metric, no audience segment, or no proof. These select the ending, what must be shown, and what the clip settles; a pack that skips them is a film brief |
| 9 | The rhythm is not cinema | a change map with any gap over three seconds, or fewer than three changes. Something the viewer notices must happen every two to three seconds, and most of those changes are not cuts because these families do not cut on request |
| 10 | No mechanism is the hero | a product hero moment that is a zip travelling, a buckle latching, a clasp turning or any other small rigid articulation. Ten real generations rendered none of them; the hero is a state or a result |

**Weighted defects** (severity: broken 3 · misleading 2 · inconsistent 1 ·
bland 0.5), counted per pack:

- broken: placeholder text in a prompt, a prompt file missing its settings
  table, `check_pack.py` FAIL left unfixed, a reference table with blank cells
  instead of "not found"
- misleading: a hook presented as proven with no reference behind it, view
  counts without a date, a claim the category forbids, a mode named in the
  settings table that the endpoint does not offer
- inconsistent: a beat sheet the prompt does not follow, a critic finding with
  no fix, a difference-matrix axis whose cells restate each other, the pack
  README disagreeing with the concept files
- bland: interchangeable stock phrasing ("cinematic, high quality, 4k" doing
  the work), a persona with no specificity, a CTA that could belong to any
  product

Score is band-dominant: the worst present severity sets the base (none 9.0 ·
bland-only 8.5 · inconsistent 7.0 · misleading 4.5 · broken 2.5), minus 0.25
per additional finding of severity ≥1 (floor base − 1.5).

**Quality lines** (0–2 each, added to the band score for ranking only):

- *Metric fit*: does the ending earn the metric the concept named — a resolved
  loop for completion, a screenshot-ready summary for saves, a question about
  the viewer's situation for comments, a recognisable situation for shares? A
  concept naming saves and ending on a CTA scores 0.
- *Proof strength*: is the central proof in the reliable half of the
  attribute → proof table — scale, structure, texture, organisation — or in the
  weak half? A concept resting on weight, softness or temperature scores 0.
- *Hook strength*, **weighted double**: for each concept, does frame one make a
  claim the camera can settle, and is the tension in the image rather than in
  the on-screen card? Check each opening against both lists in
  `references/viral-craft.md` — the openings that are not hooks and the openings
  that are almost hooks. A run where three of four openings are competent
  product footage scores 0 here however good the rest of the pack is.
- *Evidence density*: how much of the creative rests on cited references.
- *Generation readiness*: how many known failure modes the prompts design
  around, and whether the mode fits the supplied assets.
- *Readability*: can the user paste and run without reading the whole pack.

**Cost line** (reported, not scored): searches run, sources opened, reference
videos found, workers spawned, wall-clock.

## Human spot check

Two prompts per pack are generated on a real endpoint by the maintainer, at
their own cost, and scored on: did it run without a parameter error, is the
product recognisable, does the first second match the intended hook. This is
the only check that closes the loop between prompt quality and video quality,
so a version does not ship without at least one such run per model family.

## Stability

Two skilled runs per brief must agree on the product truth extracted, the mode
chosen, and every hard-failure invariant. They may differ on the concepts —
that is the creative surface. Divergence on the invariants is a defect in the
skill, investigated before the version lands.

## Mechanical self-check

```sh
python3 evals/viral-video-prompt/private/test_check_pack.py
```

It exercises `scripts/check_pack.py` against the fixtures in
`private/fixtures/`: the compliant pack passes with zero FAIL, and each planted
defect is caught — missing settings row, over-length prompt, wrong duration or
resolution case, unsupported negative prompt, placeholder text, dropped
attribute, unpaired variant, collapsed difference matrix, dangling citation,
foreign reference syntax, a claimed rung the ledger does not back, an Apify
ledger line with no `run_id`, a ledger timestamp later than the file's own
write, a missing hook-test verdict, and a hook test recorded as `fail` and
shipped unchanged. The ledger three came from an independent audit of a real run
that found them by hand; the hook-test two came from ten real generations in
which both concept-B openings passed every written test and still rendered as
product footage. They are in the suite so no future run can repeat them
silently. Run it after any change to the script or the fixtures.

Archived runs live under `runs/<date>/<brief>/<arm>-<n>/` (gitignored).
