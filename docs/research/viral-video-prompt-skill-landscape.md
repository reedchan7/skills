# Viral video prompt skill — landscape and evidence

Research basis for `viral-video-prompt` (2026-09-04). Six parallel workers, each
writing to a notes file outside the repo
(`~/Workspaces/agent/corpus/viral-video-prompt-skill/_notes/`): the three target
model families read from their vendors' own documentation, fal.ai's machine
schemas, the published landscape of video-prompt skills, the short-video craft
literature, and a live verification of the research tooling this skill can use.
This records what the skill must beat, what it borrows, and what it rejects.

## Corpus 1 — published skills (what exists, what to beat)

Stars and installs as of 2026-09-04.

| Skill | Verdict |
| --- | --- |
| `Square-Zero-Labs/video-prompting` (164★ / 431⬇) | The structural benchmark: a router `SKILL.md` plus ten per-model reference files, and global rules banning model name, duration, and aspect ratio from the prompt text. Deep, disciplined, model-faithful, and completely without market or creative strategy. |
| `MiniMax-AI` official `h3-prompt-writing` (7,952★ / 6,499⬇) | The most-installed skill that is genuinely about writing a video prompt. Forty lines that delegate to the verbatim official guides. Authoritative on fidelity, beatable on everything else. |
| `dexhunter/seedance2-skill` (3,510★ / 2,682⬇) | The best single-model documentation of Seedance's `@`-reference system: limits table, role table, eight-part formula, camera glossary. Static; no strategy layer. |
| `nutllwhy/seedance-tvc-director` (217★) | **The craft benchmark.** Seven creative mechanisms with a no-repeat rule, eight hook types plus a banned pseudo-hook list, the generic-swap and hook-restatement tests, one-action-one-commercial-task per shot, and an evidence-driven retake loop that extracts frames from the generated video. Chinese only, one model, no research, no per-model compilation. |
| `EVZheng-Lab/h3-seedance-prompt` (20★) | **The closest architecture to this skill**: one idea compiled into two official formats with the explicit rule that the versions must not be translations of each other, plus a parameter-divergence table. Tiny audience, two models, manual snapshot refresh, no strategy or research layer. |
| `coreyhaines31/marketingskills@ad-creative` (46,794★ / 106,384⬇) | The discipline benchmark, and not a video skill. Three to five distinct angles before a single headline; every concept cites a grounded source; "no invented claims, stats, or testimonials — ever"; refuses to generate when the inputs corpus is empty. |
| `xigua0626/tiktok-ugc-seedance` (4★) | The best reference-video ingestion pipeline anywhere: download, transcribe, contact sheet, conversion-node breakdown. Unusable autonomously because four human confirmation gates block it. |
| `Creatify-AI/video-ad-generator` (55★) | The only explicit A/B methodology in a skill, with a hook-rate to hold-rate to cost metric ladder. Its variants are hook swaps on one concept, and it never emits a video-model prompt. |
| `rediumvex/ai-video-generator-claude` (354★) | The best raw hook-pattern library, in four families with camera and lighting presets. Uses an `@material[name]` syntax no target platform accepts. |
| `beshuaxian/higgsfield-seedance2-jineng` (801★) | Fifteen genre skills of 900 to 1,900 lines each. Volume over adaptivity, and an enormous token cost per skill. |
| `smixs/visual-skills` (272★) | Second-strongest per-model claim, with the best film-theory grounding in the field. |
| `heloraai/Seedance2.0-Prompt-Optimizer` (91★), `op7418/Seedance-Product-Video` (149★) | Both ship "two versions" that are style labels — Apple versus Bauhaus, cinematic versus natural. Exactly what the craft benchmark bans. |
| `Alisa0808/vibe-creating-skill` (137★) | Deliberately model-agnostic. Correct for a polisher, wrong for a compiler, since H3 rejects prose that is not its schema and Wan's reference syntax changes with the prompt language. Its restraint rules are worth stealing. |
| `LichAmnesia/awesome-ad-video-prompts` (158★) | The best curated ad-prompt corpus, and the companion of the closest commercial competitor to the product idea. |
| Execution wrappers (`skills-101/superpowers/ai-video-generation` 560,937⬇, `runcomfy/video-edit` 413,974⬇, and peers) | Where the install volume actually is. They pick a model, pass the prompt as an opaque string, and poll. That opacity is the gap this skill fills, and it should not compete with them on execution. |
| Hugging Face Spaces, ComfyUI nodes | Empty ground. The best-liked video-prompt Space has two likes; ComfyUI prompt extenders are node-level LLM wrappers with no creative strategy. |

### Recurring failures across the field

1. **One model per skill.** Most hard-code a single family, usually Seedance.
2. **No research.** Exactly one prompt-craft skill in the corpus references web
   search at all, and only to check that a named landmark is real.
3. **Variants are cosmetic** — style labels, not different mechanisms.
4. **Blocking interactivity** that stalls an autonomous run.
5. **Frozen snapshots** of vendor guidance that go stale silently.
6. **Syntax drift**: `@Image1`, `@图片1`, `Image 1`, `<Picture 1>`,
   `@material[name]`. Several skills emit a syntax their target rejects.
7. **No output validation.** Nobody checks the emitted prompt against the
   model's schema before handing it over.

## Corpus 2 — vendor documentation and research

Read from the owners: MiniMax's H3 model card, prompting guide, and video API;
Alibaba's Model Studio prompt guide and Wan video API plus the Wan technical
report; Volcengine Ark's Seedance guides and API reference; fal.ai's queue
OpenAPI schemas for every endpoint in the three families; and the prompt-rewrite
literature (Wan's prompt-alignment section, Prompt-A-Video, and the caption
upsampling work behind it).

**What every modern video model agrees on**: decompose into subject, action,
environment, camera, light, and sound; concrete and observable beats abstract;
motion must be specified and singular, one camera move and one subject action
per shot; camera needs type plus amplitude plus speed plus a start and a stop;
lighting is named by quality, direction, and colour; image-to-video means
animate rather than re-describe; style is declared first and stays consistent;
generation parameters stay out of the prompt text; audio shares the same
timeline with in-world sound separated from score; and exact spoken words are
never rewritten.

**Where the three targets diverge**, which is why compiling beats translating:

| | MiniMax H3 | Wan 3.0 | Seedance 2.x |
| --- | --- | --- | --- |
| Reference syntax | `Image 1`, spaced | `图1` or `Image 1`, spaced | `@图片1` or `@Image1`, no space |
| Camera | prose, from a closed vocabulary with amplitude and speed | dictionary tags front-loaded, then prose | standard terms taken literally, one per shot |
| Multi-shot | native, timestamped cut lines | prose only; `生成单镜头` forces one take | 2.0 shot numbers only; 2.5 integer-second timestamps |
| Language | body in English, dialogue keeps its own | Chinese-first, bilingual by design | Chinese-first, eleven spoken languages |
| Audio | always on, no toggle, two dedicated fields | toggle, three sub-formulas | toggle, four bracket channels |
| Hard constraint | frame and reference inputs are exclusive | frame and reference inputs are exclusive; no alpha channel | frame and reference inputs are exclusive; **no real human faces in references** |

**Two research findings shape the skill directly.** Dense caption-style prose is
the target distribution because the model's rewriter exists to move short
keyword prompts toward its training captions; and a fixed negative list matches
per-prompt adaptive negatives while measurably reducing the amount of motion,
which is the wrong trade for a clip whose job is to stop a scroll.

## Corpus 3 — short-video craft

Platform-published data (TikTok Creative Center, Creative Codes, TikTok Shop
Academy), named creative datasets, peer-reviewed work on social proof and
scarcity in short-video commerce, and Chinese practitioner teardowns.

The finding that shapes the whole design: on the largest paid-creative dataset
here, the hit rate for a winning creative is about five percent, and the report's
own reading is that low hit rates are a statistical feature rather than a quality
signal. **Viral DNA is a compression of what to try, not a formula that raises
the odds of any single clip.** Structural diversity across a batch is the lever,
which is exactly what two rival concepts are for.

## Corpus 4 — tooling, verified live

Every recipe in `references/research.md` was executed against the real APIs on
2026-09-04. The decisive negative: **no general search API can see short-video
engagement.** Brave's video index returns no TikTok at all, including with a
`site:` operator, and Tavily's extraction fails on every TikTok and Instagram
video URL. Engagement numbers come from a scraper or from the user. That finding
is why the skill ships a four-rung degradation ladder and states which rung it
reached.

## Where this skill is built to win

- **One brief, several models, compiled not translated.** Only a 20-star
  Chinese-only repo attempts it, for two models.
- **Research at all.** No prompt-craft skill in the corpus does a market,
  category, or trend lookup.
- **Strategic divergence joined to per-model compilation.** The best mechanism
  diversity rule in existence produces prose treatments for one model; the best
  angle discipline never emits a video prompt.
- **Reference video as a first-class input**, measured before it is interpreted,
  without blocking gates.
- **Validation before delivery.** A zero-dependency checker reads a machine
  limits file and fails a pack whose prompt is over length, whose duration or
  resolution is not offered, whose variants collapse into one, or whose product
  attributes went missing.
- **Honest measurement.** Every skill that mentions A/B implies a readable
  winner; none reconciles that with the sample sizes. This one reads hook rate,
  then hold rate, and says so.

## Rejected

Blocking confirmation gates; per-shot bespoke negative prompts; genre-template
sprawl; a single universal prompt relabelled per model; non-standard reference
syntax; style presets sold as variants; frozen manual snapshots; padding a
prompt past the training-caption band; implying two variants yield a
statistically valid winner; and wrapping a vendor API, which the execution
skills already own.

## Open items

Runway, Luma, and Pika guidance was not retrieved. ByteDance's Seedance 2.5
manual is currently reached through fal, 即梦, and a third-party snapshot rather
than as a first-party document. Several safe-zone pixel margins come from
secondary sources that disagree with each other. The measured effect of the
prompt rewriter on a long, fully specified product prompt is untested, as is
whether a hand-written H3 field-schema prompt passes through its context module
unchanged.
