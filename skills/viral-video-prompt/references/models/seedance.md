# ByteDance Seedance 2.x dialect

Facts read 2026-09-04 from Volcengine Ark's Seedance prompt guides and API
reference, the 即梦 tutorials, and fal.ai's endpoint schemas. Re-read before
trusting a limit that decides a prompt.

## Which model

| Version | Released | Where |
| --- | --- | --- |
| Seedance 2.5 | 2026-07-31 | Ark `doubao-seedance-2-5-260628`; fal `bytedance/seedance-2.5/*` |
| Seedance 2.0 | 2026-02-12 | Ark `doubao-seedance-2-0-260128`; fal `bytedance/seedance-2.0/*`, plus `fast` and `mini` tiers |

There is no `seedance-2.5/fast`. The 2.0 and 2.5 endpoint ids drop the `fal-ai/`
prefix that older Seedance versions carry.

**Write for 2.5 by default**, since it is current, takes timestamps, and reaches
thirty seconds. Put the 2.0 conversion — timestamps replaced by `镜头1` / `镜头2`
shot numbers, duration capped at fifteen seconds — first in the recovery section,
because 2.0 is the cheaper tier a user falls back to.

## The one difference that changes how you write

**Seedance 2.0 ignores timestamps and responds only to shot numbers. Seedance
2.5 responds to integer-second timestamps.** Getting this wrong is the
difference between a script that runs and a script that is silently rearranged.

| | 2.0 | 2.5 |
| --- | --- | --- |
| Segment with | `镜头1` / `镜头2` / `镜头3` | timestamps, `0-3秒` / `[3s-8s]`, or shot numbers with times |
| Duration | 4–15 s | 4–30 s |
| Resolution | 480p, 720p, 1080p, 4k | 480p, 720p, 1080p |
| Reference images | up to 9 | up to 30 |
| Reference videos | up to 3, ≤15 s total | up to 10, ≤30 s total |
| Reference audio | up to 3, ≤15 s, never alone | up to 10, ≤30 s |
| Total files | 12 | 50 |
| Aspect ratio | six fixed steps | any ratio from 0.4 to 2.5 via the input assets |
| Output format | mp4 | mp4, mov |

Both output 24 fps. Advice telling you to ask for 60 fps is describing a mode
that does not exist.

## Real human faces are not accepted

Neither version accepts a reference image or video containing a real person's
face. A creator-holds-the-product video cannot be built by uploading a photo of
a real presenter. The workable routes are:

1. Generate the presenter first with the same model family and reuse that output
   within thirty days.
2. Use the platform's preset virtual-persona assets.
3. Go through the authorised-likeness flow.
4. Keep the video product-only or hands-only with voice-over.

Decide the route before writing a prompt with a person in frame, and say which
one the pack assumes.

## Prompt structure

Write as a director issuing instructions, not as a copywriter describing a
scene. Four parts, in this order:

1. **Asset binding** — every reference numbered by upload order, with the job it
   does and the job it must not do.
2. **One-line summary** — subject, place, event, genre, and any signature camera
   move.
3. **The beats** — split by shot number (2.0) or timestamp (2.5). Each beat
   carries camera, action, and audio.
4. **Closing** — what holds across the whole clip: camera policy, environment,
   sound, and the constraint list.

The formula behind it, for 2.5: 主体 + 动作/事件 + 场景与环境 + 视觉风格 +
运镜/切镜 + 声音. Omit what you do not need.

2.0 publishes a different, longer one, and it is what a 2.0 fallback should
follow: 精准主体 + 动作细节 + 场景环境 + 光影色调 + 镜头运镜 + 视觉风格 + 画质 +
约束条件.

**Label the shots.** Without labels, a long prompt produces one continuous take
rather than an edited sequence.

**Reserve the ending.** Set aside the last two to four seconds for no new
events, so the subject settles and the camera stops. A clip that runs its last
action to the final frame reads as cut off.

## Audio and text channels

Four bracket types separate the channels; ordinary prose blurs them and the
model has to guess.

| Channel | Mark | Example |
| --- | --- | --- |
| Music | （） | （轻快的原声吉他节奏） |
| Sound effect | <> | <拉链拉合的"唰"声> |
| Dialogue | {} | 她看向镜头说：{这个容量真的离谱} |
| On-screen subtitle | 【】 | 【第一次装满它】 |

Pair the braces with a speaker and a speech verb, which satisfies both
documented conventions at once. Name the language before a line that is not
Chinese or English. Keep dialogue in one language throughout, proper nouns
aside.

Audio follows prompt order as a timeline: whatever is written first is heard
first. For a sound that must land in the middle of a line, split the line and
put the effect between the halves.

Name music explicitly as background music, or it may be treated as a brief
effect that fades after a few seconds.

## Camera

Standard terms are followed literally: 大全景、全景、中景、近景、特写 for shot
size; 推、拉、摇、移、跟、环绕、俯冲、上摇、手持晃动 for movement; 低角度、俯视、
第一人称 for position. Popular named moves work directly: 一镜到底, 希区柯克变焦,
航拍视角, FPV, 子弹时间, 手持镜头.

**One camera move per shot.** Asking for a push and a pan and an orbit in one
shot is the documented cause of unstable frames.

An obscure term needs a gloss: write the name plus a plain description of what
the frame does.

Write a transition with its trigger and its method, for example 第5秒快速向左横移
转场（向左擦除+自然叠化）.

## Action and emotion

Specify the body part, then the amplitude, speed, and force: 缓慢抬手, 快速转头,
微微低头. Prefer slow, continuous, small movements; high-energy action is where
physics breaks.

Externalise emotion into observable detail rather than naming it. "喜悦" becomes
嘴角抑制不住地上扬、脚步变得轻快. Avoid four-character idioms in favour of
描述性语句.

## Reference assets

Cite as `@图片1` / `@视频1` / `@音频1`, numbered by upload order (fal's English
schema uses `@Image1` / `@Video1` / `@Audio1`). The wrapper is flexible; the noun
plus index is what carries.

Bind each asset in the text, and add the negative half:

```text
@图片1 提供产品外观与包装结构，@图片2 只提供材质细节，@视频1 只提供运镜路径。
不要从 @视频1 取用主体、服装或场景；不要从 @图片2 取用背景与灯光。
```

Define a subject with two or three stable static features, then reuse the label:
将 @图片1 中{特征}的{物}定义为{主体1}. State a partial reference as partial:
参考 @视频1 中的环绕运镜.

**When the reference is already precise, stop describing the picture.** Say
严格参考视频1的动作与运镜 and let the asset carry it; re-describing invites
conflict.

**More references is not better.** Four or five assets with clear roles beat a
full slate. One to eight subjects in reference images work well; beyond that,
stability drops.

| Asset | 2.5 limits | 2.0 limits |
| --- | --- | --- |
| Images | up to 30 · jpeg, png, webp, bmp, tiff, gif, heic, heif · ≤30 MB each · 300–6000 px per side · aspect ratio 0.4–2.5 | up to 9, same formats and bounds |
| Videos | up to 10 · mp4, mov, H.264 or H.265 · 1.8–30.2 s each, ≤30.2 s total · ≤200 MB · 24–60 fps | up to 3 · ≤15 s total · ≤50 MB · keep at 720p or below |
| Audio | up to 10 · mp3, wav · 1.8–30.2 s each · ≤15 MB | up to 3 · ≤15 s total · never the only reference |
| Total | ≤50 files, request body ≤64 MB | ≤12 files |

Reference product images want to be at least 1024 px square, evenly lit, on a
clean background, with the product filling half to two thirds of the frame.

## Frame modes versus reference mode

First-frame, first-and-last-frame, and full reference mode are **mutually
exclusive**.

- Setting a true first frame reproduces it exactly and **locks the aspect ratio
  to the image**, so the image itself must already be 9:16.
- Naming a reference image as the opening frame in the prompt (`图片1 为首帧`)
  keeps the ratio free and lands close to the image without matching it exactly.

For a storyboard that must hit several exact compositions, use keyframe mode:
upload the frames in order and open the prompt with 以图片1至图片N的顺序作为关键帧.

## Task keywords that hijack the request

Edit and extend tasks are triggered by words in the prompt, and they lock the
aspect ratio and sometimes the duration. Avoid 编辑, 增加, 加上, 删除, 去掉, 修改,
替换, 改成, 延长, 延续, 续写 in an ordinary generation prompt. Writing
"把背景改成白色" inside a reference prompt can silently turn it into an edit task.

## Negative control

There is no negative-prompt field; exclusions are written inline and only two
channels are formally supported.

- Subtitles: **vertical output produces unwanted subtitles noticeably more often
  than horizontal**, so every 9:16 prompt carries an exclusion, and even then it
  is not absolute. Two forms, and the choice depends on whether you wanted text:
  - no text at all → `保持无字幕，避免生成任何文字或字幕`
  - text cards you asked for through `【】` → scope the exclusion so it does not
    cancel them: `除上述字幕外，不要生成其他文字或字幕`
- Logos and watermarks: 不要生成Logo, 不要生成水印.
- Audio: 无bgm，只生成环境音和动作音, or 不要任何声音.
- Duplicate people: 视频全程禁止出现外形、着装、配饰完全一致的人物，禁止生成同款
  分身、双胞胎效果.

## Length

The documented ceiling is 500 Chinese characters or 1000 English words; beyond
it the model spreads its attention and drops elements. The bands that work:

| Job | Length |
| --- | --- |
| One product beat with a good reference image | 80–200 Chinese characters |
| Three-shot product sequence, 10–15 s | 200–400 |
| 30-second multi-shot with dialogue | 400–700 |

Every sentence should change the picture, the sound, or the next shot's state.
Repeated adjectives drown the instructions that matter.

## Parameters

On Ark, pass parameters in the request body rather than as trailing `--rs`,
`--rt`, `--dur`, `--cf`, `--wm` flags, which are weakly validated and legacy.
fal does not accept the flags at all.

| Parameter | Value |
| --- | --- |
| `resolution` | 2.5: 480p, 720p, 1080p (default 720p). 2.0 adds 4k |
| `ratio` / `aspect_ratio` | 21:9, 16:9, 4:3, 1:1, 3:4, 9:16, adaptive. Locked to the image on 2.5 image-to-video |
| `duration` | 2.5: 4–30 or auto. 2.0: 4–15 or auto |
| `generate_audio` | default true, no price difference |
| `seed`, `camera_fixed`, `watermark`, `output_format` | Ark only, not exposed on fal |

Generation is billed by output pixels and seconds, so a 30-second 720p clip is
an expensive single roll. Draft at 480p, then commit.

## Observed on real generations

Two clips, 15 s, `480p`, reference-to-video, 2026-09-04. `480p` returned
480×854.

- **The best light and the cleanest continuity of the three families.** Object
  state advanced correctly across the whole clip and the final frame was right
  without being told twice.
- **It does not cut.** Three cuts were asked of each clip; both came back as a
  single continuous take. The beats still landed on their timestamps, so the
  integer-second timing is doing real work — the cut is what it ignores. Write
  for one take.
- **No unwanted subtitles appeared** on either clip, and no invented lettering.
- **The `{}` dialogue gets captioned and the `【】` card is dropped**, when both
  sit in the same beat. Two beats, two clips, no exception: a beat carrying
  `【它比电脑矮】` and `{它比电脑还矮，你说能装吗}` rendered the spoken line as a
  bottom-band subtitle and never showed the card. What shipped was an
  eleven-character line low in frame where a five-character card at the top was
  designed. So **do not put a card and a spoken line in the same beat unless
  they say different things** — and if the beat has dialogue, design the caption
  it will generate rather than a card it will not.
- **Levels arrive 2–3 dB under target**, at -16.3 and -17.3 LUFS. Normalise up.
- **It is by far the most expensive of the three.** At 480p a 15 s clip costs
  roughly ten times the same clip from Hailuo at 768P. Budget it as the arm you
  run once, not the arm you draw twice.

## Do

- Segment with shot numbers on 2.0 and timestamps on 2.5.
- Bind every asset, with both the job it does and the job it must not do.
- Use the bracket channels for music, effects, dialogue, and subtitles.
- One camera move and one primary action per shot.
- Externalise emotion into body detail.
- Reserve the last two to four seconds for settling.
- Add the no-subtitle line to every vertical prompt.
- Put the most important reference earliest in the prompt.
- Draft at 480p.

## Don't

- Timestamps on 2.0, where they are ignored.
- Reference images or video containing a real person's face.
- Edit or extend verbs in a generation prompt.
- Frame inputs mixed with reference inputs.
- A full slate of references; four or five with clear roles beat thirty.
- Re-describing what a precise reference already carries.
- Quality-booster tag lists and static scene descriptions with no motion.
- More than three shots in a short prompt, or a beat that changes location,
  speaks, picks up the product, and moves the camera all at once.
