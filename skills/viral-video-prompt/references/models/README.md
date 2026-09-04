# Dialects — one concept, many prompts

Phase 4 in full. The concept is settled before this step and does not change
here. What changes is how it is said.

## Files

| File | Family | Use for |
| --- | --- | --- |
| `universal.md` | none | the model-agnostic prompt, and any model with no dialect file |
| `hailuo.md` | MiniMax Hailuo | `hailuo-*` on MiniMax and on fal.ai |
| `wan.md` | Alibaba Wan | `wan*` on Bailian, wan.video, and fal.ai |
| `seedance.md` | ByteDance Seedance | Seedance on Ark, 即梦, and fal.ai |
| `limits.json` | all | machine-readable limits, read by `scripts/check_pack.py` |

Always produce `universal` alongside the named models. It is what the user
pastes into a model nobody has documented yet, and it is the control arm when
a model-specific prompt underperforms.

## The translation order

Work down the beat sheet, not down the dialect file. For each concept:

1. **Pick the mode** from the inputs the user supplied, not from habit.

   | The user gave | Mode | Why |
   | --- | --- | --- |
   | text only | text-to-video | nothing pins the product, so the prompt describes it fully |
   | one image that could open the clip | image-to-video | the opening frame is settled and product identity is safest |
   | several product images | reference-to-video where the family supports it, otherwise image-to-video from the best one | several angles hold the shape across motion |
   | an end card or beauty shot | first-last-frame where supported | the landing is guaranteed |
   | a reference video | the family's video-reference mode where it exists; otherwise the video informs the beat sheet only | most families cannot take a video as a style source |

2. **Set duration first.** Pick from the family's allowed set, then fit the
   beats to it. A beat sheet that needs 9 seconds against a model that offers 6
   and 10 is re-cut, not rounded.

3. **Write the prompt in the family's structure** and its preferred language.
   Every family wants subject, action, setting, camera, light, and style; they
   differ in order, in syntax, and in how much prose they reward.

4. **Address the assets in the family's own syntax.** An `@`-mention that one
   family understands is literal noise in another. When a family has no syntax
   for it, describe the referenced subject in words instead.

5. **Count the characters** and put the count in the settings table against the
   limit. A prompt over the limit is silently truncated, usually losing the
   ending, which is where the payoff lives.

6. **Fill the settings table completely.** It is the other half of the
   deliverable: the same prompt at the wrong duration or resolution produces a
   different video.

## Rules that hold for every dialect

- **Generation settings stay out of the prompt text.** The model's name, the
  duration, the aspect ratio, and the resolution belong in the settings table.
  Writing them into the prompt wastes characters and sometimes contradicts the
  parameter. Two exceptions: a family whose prompt format encodes timing carries
  its timestamps, and a family whose own skeleton opens with a duration or an
  orientation phrase keeps it. Where a dialect file and this rule disagree, the
  dialect file wins.
- **Compile, do not translate.** A prompt written for one family and reworded
  for another is one right prompt and one wrong one. Each dialect gets its own
  expression of the same beat sheet.
- **Never invent a claim, a statistic, or a testimonial** to make copy land. A
  spoken line that states a fact must trace to something in `01-research.md`.
- **Say the exclusions once, as a short fixed list.** None of these families has
  a negative-prompt field, and heavy exclusions reduce how much motion the model
  produces.

## What never changes between models

- The hypothesis, the hook mechanism, the beats, and the product truth.
- The market's language for spoken and on-screen copy.
- The aspect ratio.

When a model cannot express a beat — no audio, no second shot, no on-screen
text — the beat is *adapted and the adaptation is named* in the file's "If the
result is off" section. It is not silently dropped.

## Keep the pack readable

Eight prompt files repeating the same paragraph is padding, not thoroughness.
When a fix or a recovery step applies to every family — the colour that drifts,
the hardware that deforms, the fallback to a reference mode — write it once in
`prompts/COMMON.md` and let each prompt file carry only what is true of that
family. Each file still needs its own settings table, its own paste-ready block,
and at least one line of its own under *Why this works* and *If the result is
off*.

## Adding a model

1. Read the vendor's own prompt guide and API reference. Record the structure,
   the camera vocabulary, length limits, durations, resolutions, negative-prompt
   support, optimizer flags, audio support, and reference-asset syntax.
2. Write `<family>.md` following the shape of the existing dialect files:
   what the family is, the prompt skeleton, the syntax table, the limits, the
   do/don't list, and two worked skeletons.
3. Add an entry to `limits.json` with `aliases`, `max_prompt_chars`,
   `durations`, `negative_prompt`, `audio`, `max_reference_images`, and
   `forbidden_in_prompt` — the other families' syntax that this one would read
   as literal text.
4. Never write a number you did not read. An unknown limit is omitted from
   `limits.json` (the gate then skips that check) and marked unverified in the
   dialect file.

## Version drift

Model families rename and re-version quickly. Every dialect file carries the
date its facts were read. When a fact is older than a few months, or the user
names a version the file does not cover, re-read the vendor page before
trusting the limit, and update the file and `limits.json` in the same edit.
