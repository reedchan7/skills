# {{model_display}} — Concept {{variant}}: <concept name>

| Setting | Value |
| --- | --- |
| Model / endpoint | <exact model or endpoint id from references/models/{{model}}.md> |
| Mode | text-to-video \| image-to-video \| reference-to-video \| first-last-frame |
| Inputs | none \| image 1 = <which user file, role> · image 2 = … · video 1 = … |
| Duration | <value from the model's allowed set> |
| Resolution | <value, copied with its exact capitalisation> |
| Aspect ratio | 9:16 \| n/a — follows the input image |
| Audio | on \| off · dialogue: yes \| no |
| Prompt optimizer / extend | on \| off — <why> |
| Negative prompt | supported \| not supported |
| Prompt length | <n> chars of <limit> |

## Prompt (paste as-is)

```text
<the prompt, in the language and structure references/models/{{model}}.md prescribes>
```

<!-- Add a "## Negative prompt" section with its own fenced block ONLY for a
     model whose limits entry has "negative_prompt": true. None of the four
     families here does, so exclusions go inline at the end of the prompt and
     this section stays absent. -->

<!-- Before this file is written, check the prompt text itself for three things
     that a real run got wrong on five clips out of ten:

     1. The last beat names the whole visible inventory, including what is NOT
        on the surface any more, and says whether the product is open or closed.
        A last beat that describes only the camera returns whatever end state
        the model finds photogenic.
     2. The exclusion covers the whole frame, not just the product. "No
        lettering on the bag" leaves the props free to grow invented logos.
     3. Every on-screen card has one named position and no internal space. A
        space inside a CJK string comes back as two cards.
-->

## Why this works

- <hook mechanism and the evidence behind it, V<n> / [n]>
- <what the model does well that this prompt leans on>
- <how product truth is protected>

## If the result is off

- <symptom → the one line to change>
- <symptom → the one setting to change>
- <symptom → fall back to image-to-video with image <n>>
- The end state is wrong, or something that was packed is outside again → restate the whole final inventory in the last beat, absences included
- A logo or garbled type appears on a prop → widen the exclusion from the product to the frame, and swap the prop for a class that carries no label in life
- One card rendered as two → remove the space inside the string, or move that line to the platform's text layer
- The audio clips, or is too quiet to hear → `ffmpeg -i in.mp4 -c:v copy -af "loudnorm=I=-14:TP=-1:LRA=11" -c:a aac -b:a 192k out.mp4`
