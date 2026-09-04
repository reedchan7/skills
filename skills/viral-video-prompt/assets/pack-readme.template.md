# Viral video prompt pack — <product in five words>

Generated {{date}} · pack `{{dir}}` · request: "{{request}}"

## The two concepts

- **A — <name>**: <one line>. Hook: <…>. Serves <U1>.
- **B — <name>**: <one line>. Hook: <…>. Serves <U2>.

Differ on: <axes>. Shared: <product truth · platform · 9:16 · duration class>.

## Before you generate

- **Pinned or unpinned**: <a product photo was supplied and every prompt uses a reference mode | **Unpinned: no reference image** — every prompt describes the product in words, so colour and hardware can drift. One photo would move all of these to a reference mode.>
- **Counter-read**: <what the final pass found, and what it changed — or "nothing changed".>

## Files

| File | Use it for |
| --- | --- |
| `00-brief.md` | what was asked, assumed, and accepted as done |
| `01-research.md` | product truth, audience, viral references with numbers, trends, sources |
| `02-concepts.md` | both concepts in full, the difference matrix, the A/B test plan |
| `prompts/<model>-A.md`, `prompts/<model>-B.md` | paste-ready prompt plus the settings table for each model |
| `assets/` | user inputs copied here, reference-video frames and summaries |
| `prompts/COMMON.md` | the fixes and recovery steps that apply to every prompt, so each file carries only its own deltas (omit when there are none) |

## After you generate, before you post

1. **Normalise the audio.** Native audio comes back unmastered — some families clip, some sit 8 dB under. Platform target is about -14 LUFS, true peak at or below -1 dBTP.
   ```sh
   ffmpeg -i in.mp4 -c:v copy -af "loudnorm=I=-14:TP=-1:LRA=11" -c:a aac -b:a 192k out.mp4
   ```
2. **Check the last frame.** Confirm the product's end state and that nothing that went in is sitting outside again. This is the commonest silent failure.
3. **Check frame one against the hook.** If the claim is not visible with the sound off and the card covered, redraw rather than post; the card cannot rescue it.
4. **Look for lettering that should not be there** — on the product and on every prop. A garbled invented logo on a prop is a legal problem, not a blemish.

## Run the A/B test

1. For each model, generate A and B with the settings table in its prompt file; change nothing else between arms.
2. Post them as paired variants (same caption, same window). Measure the primary metric in `02-concepts.md` §A/B test plan.
3. Apply the decision rule there; a follow-up pack is a new timestamped directory that names this one as its prior.

## Not verifiable this run

- <claim or trend — channels tried>

## What would improve the next pack

- <e.g. real product photos on white and in use; the brand's past best video; the exact platform and country>
