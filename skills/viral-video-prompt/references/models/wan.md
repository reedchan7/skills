# Alibaba Wan 3.0 dialect

Facts read 2026-09-04 from Alibaba Bailian's Wan video API reference and its
prompt guide, the Wan technical report, and fal.ai's endpoint schemas. Re-read
before trusting a limit that decides a prompt.

## Which model

Wan 3.0 reached general availability on 2026-08-24. It is one all-in-one model,
not a text-to-video and image-to-video pair.

| Id | What it is |
| --- | --- |
| `wan3.0-video` | standard |
| `wan3.0-video-prime` | same capabilities, markedly faster |

On fal: `alibaba/wan-3.0/{text-to-video,image-to-video,reference-to-video}` and
the matching `alibaba/wan-3.0-prime/*`. Wan 2.6 and 2.7 live under different
namespaces and use different syntax, so a guide written for them will mislead.

Open weights stop at Wan 2.2; 3.0 is API-only.

## Write in Chinese

The documentation, every worked example, and the rewriter model itself are
Chinese-first, and the text encoder is genuinely bilingual, so English works and
is simply less evidenced. Write the body in Chinese and keep brand names and
on-screen copy in their own script inside it.

## The mode decision

| Mode | Assets | Use when |
| --- | --- | --- |
| 文生视频 | none | no product image exists |
| 图生视频 | `first_frame`, optional `last_frame` | one hero image must be reproduced pixel-exactly as frame one |
| 参考生视频 | up to 10 `reference_image`, 5 `reference_video`, 5 `reference_audio` | several product photos, a reference clip, or a voice to imitate |
| 文件 / 网页生视频 | one `file` or one `link` | a deck or a product page is the brief |

**Frame inputs and reference inputs cannot be combined.** The request errors.
For a brief with several product photos you must choose: one image reproduced
exactly as frame one and nothing else, or up to ten images informing identity
with no frame guaranteed. For e-commerce the reference route usually wins,
because the product is pinned from several angles.

`ratio` defaults to `adaptive`, which follows the source asset. Set `9:16`
explicitly, since a square product photo would otherwise produce a square video.

## Prompt structure

The model's own technical report gives the canonical order: **style, then a
one-line abstract of the content, then the detailed description**. Short keyword
prompts are the documented failure mode that the built-in rewriter exists to
repair, so write the prose yourself and keep control of the product.

The house style opens with a short comma-separated block of cinematography tags,
then moves into prose:

```text
边缘光，中近景，日光，左侧重构图。{一句话概述}。{详细描述}。
```

**Cap the tags at four.** Alibaba's published prompt-extension system prompt —
the one the built-in rewriter follows — targets 60 to 200 words and at most four
aesthetic tags, and its own worked example uses exactly four. The 提示词词典
example library stacks eight to twelve, which is a catalogue of the vocabulary
rather than a target shape; a prompt that stacks twelve is outside the
distribution the rewriter is aiming at. When the look is illustration or
otherwise non-cinematic, add no film-aesthetic tags at all.

`【…】` section headers are an official grouping device in long prompts. For
product video the reusable set is `【产品锁定】【画面】【镜头与画质】【声音】`.

**Always state the motion.** The rewriter invents motion for a static
description, and invented motion is where product identity goes.

### The formulas

| Formula | Shape |
| --- | --- |
| 基础 | 主体 + 场景 + 运动 |
| 进阶 | 主体（主体描述）+ 场景（场景描述）+ 运动（运动描述）+ 美学控制 + 风格化 |
| 图生视频 | 运动 + 运镜 — the image already fixes subject, scene, and style, so restating them invites conflict |
| 声音 | 主体 + 场景 + 运动 + 声音描述（人声 / 音效 / 背景音乐） |
| 多镜头 | 总体描述 + 镜头序号 + 时间戳 + 分镜内容 |
| 参考生视频 | 参考指代 + 动作 + 场景 + 台词（可选）+ 背景音乐（可选） |

Sound sub-formulas: 人声 = 内容 + 情绪 + 语调 + 语速 + 音色 + 口音; 音效 = 音源材质
+ 行为 + 环境音; 背景音乐 = 背景音乐 + 风格.

### Multi-shot and single-shot

Multi-shot is controlled in prose only; there is no `shot_type` or `multi_shots`
parameter in 3.0. Number the shots and timestamp them:

```text
第1个镜头[0-3秒]…
第2个镜头[3-6秒]硬切转场，固定机位，…
```

Write `生成单镜头` to force one continuous take. For a product hero shot this is
usually right, because a cut is where the product drifts.

Give every beat enough seconds. An over-packed script silently drops beats
rather than speeding up.

## Vocabulary

Draw from the official dictionary; these axes were deliberately annotated during
captioning, so naming them lands.

| Axis | Terms |
| --- | --- |
| 景别 | 特写、近景、中近景、中景、中全景、全景、极端全景、广角 |
| 基础运镜 | 镜头推进、镜头拉远、镜头向左移动、镜头向右移动、镜头上摇、镜头下摇、固定镜头 |
| 高级运镜 | 复合运镜、环绕运镜、跟随视角、快速穿越、无人机镜头、FPV |
| 机位角度 | 平拍、过肩角度、高角度、低角度、俯视角度、仰拍、航拍 |
| 镜头焦段 | 长焦、中焦距、广角、超广角-鱼眼、移轴 |
| 光线类型 | 柔光、硬光、侧光、边缘光、逆光、顶光、底光、实用光、混合光、高对比度、低对比度 |
| 光源 / 时间 | 日光、火光、阴天光、晴天光；白天、夜晚、黎明、黄昏、日出、日落 |
| 构图 | 中心构图、平衡构图、对称构图、右侧重构图、左侧重构图、短边构图 |
| 色调 | 暖色调、冷色调、混合色调、高饱和度、低饱和度 |
| 特效镜头 | 移轴摄影、延时拍摄、慢镜头、微距 |

## Audio

Wan 3.0 generates dialogue, sound effects, and music in the same pass, and the
`audio` switch costs nothing either way.

- **Dialogue** goes inline in full-width quotes after a speech verb, and quoted
  text is preserved as written: `用轻快的语气说道："这个颜色我能背一整年。"`
  Accent and language are named directly (`美式英文`, `地道的京腔`).
- **Sound effects** are written as onomatopoeia in quotes plus their source:
  `拉链拉合发出"唰"的一声`.
- **Ambience** is a clause; **music** is a style label.
- **Silence must be requested.** Write `无台词` and `无背景音乐`, or the model
  invents both.

## Reference assets

Cite them as `图1` / `图片1` / `视频1` / `音频1`, matching upload order. Images,
videos, and audio are **counted separately**, so `图1` and `视频1` coexist. With
a single reference the number can be dropped: `参考图片`. The English form is
`Image 1`, capitalised with a space.

Give each reference an explicit job, and say what must not transfer:

```text
【产品锁定】主角是图1的托特包：{形态、材质、颜色、比例、关键部件逐条列举}。
图2 仅提供环境与光线。外形、比例、配色与标签位置全程不变，不新增文字或 logo。
```

| Asset | Limits |
| --- | --- |
| `reference_image` | up to 10 · JPEG, JPG, PNG, BMP, WEBP · **no alpha channel** · 240–8000 px per side · aspect ratio ≤8:1 · ≤20 MB |
| `reference_video` | up to 5 · mp4, mov · 1–15 s each, ≤15 s total · ≥16 fps · 240–4096 px · ≤100 MB |
| `reference_audio` | up to 5 · wav, mp3 · 1–15 s each, ≤15 s total · ≤15 MB |
| `first_frame`, `last_frame` | one each, and never with a reference asset |
| `file` or `link` | one of either; on fal both require `enable_thinking` |

**Flatten transparent PNGs before upload.** Cut-out product images on
transparent backgrounds are the e-commerce norm and are not supported.

## Parameters

| Parameter | Value |
| --- | --- |
| `prompt` | 20,000 characters first-party, 5,000 on fal — write to 5,000 so the prompt is portable. Practical band: 150–600 characters for one shot, 600–1,200 for a storyboarded 15–30 s piece |
| `negative_prompt` | **does not exist in 3.0**, unlike 2.5 through 2.7 |
| `prompt_extend` (fal: `enable_prompt_expansion`) | default on. Leave it on; disabling saves 20–60 seconds and usually costs quality. Turn it off only when a long, fully specified product prompt is drifting |
| `duration` | 2–30 seconds; `-1` (fal: `null`) lets the model choose |
| `resolution` | 480, 720, 1080. **fal spells them `480p`/`720p`/`1080p`; Alibaba's own API spells them `480P`/`720P`/`1080P`.** Write the spelling your endpoint documents. No 4K |
| `ratio` | `adaptive`, `16:9`, `4:3`, `1:1`, `3:4`, `9:16` |
| `audio` | boolean, default true, no price difference |
| `seed` | accepted, but reproducibility is explicitly not guaranteed |
| `watermark` | default off |

Output frame rate is 30 fps. On fal the response carries `actual_prompt`, the
text after rewriting — read it to see what the rewriter added, then promote the
good parts into the next draft.

Draft at 480P and finish at 1080P: price is per second and scales with the tier.

## Observed on real generations

Four clips, 15 s, `480p`, reference-to-video, 2026-09-04. `480p` returned
480×832.

- **Chinese cards rendered cleanly**, including four-character and
  six-character lines, at 480p.
- **It masters hot enough to clip.** Three of four clips peaked above full
  scale, at +0.57 to +0.95 dBFS, and two sat at -8.0 LUFS. Always normalise;
  never post the file as it arrives.
- **Props grow invented branding.** A soda can and an ice pack both arrived
  carrying fabricated logos in garbled type, on a prompt whose exclusion line
  covered the product only. Scope the exclusion to the whole frame and choose
  prop classes that are unbranded in life.
- **The end state resets if you do not spell it out.** One clip packed five
  objects into the bag and then showed them back on the counter in its final
  seconds. The last beat has to name the full inventory, including what is no
  longer on the surface.
- **Cut counts are advisory.** Three cuts asked, four times; results were 2, 2,
  4 and 0.

## Do

- Write in Chinese, ordered style, abstract, detail.
- Open with at most four dictionary tags, then prose, and target 60 to 200 words.
- Enumerate the product physically, then add an invariance clause. This replaces
  the missing negative prompt and is more precise than one would be.
- Give each reference one job, cited as `图n`, and say what must not transfer.
- State the motion, always.
- Write `生成单镜头` for a hero shot, or numbered timestamped shots for a story.
- Write `无台词` and `无背景音乐` when you want silence.
- Set `ratio` explicitly for social formats.
- Read `actual_prompt` back and iterate on it.

## Don't

- Reach for `negative_prompt`, or paste the old `低分辨率、错误、最差质量` boilerplate.
- Mix a first or last frame with any reference asset.
- Use `character1` / `character2`, which is Wan 2.6 syntax.
- Restate subject, scene, and style when a first frame already fixes them.
- Carry over the Wan 2.1-era advice that one or two sentences is best; it
  contradicts every 3.0 example and the technical report.
- Put contact-heavy action or a destructive reveal in the hero beat. Physics
  bugs, prop substitution, colour drift, and inconsistent cross-sections are the
  observed weak spots.
- Rely on `seed` for a repeatable render.
