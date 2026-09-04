# Brief — {{slug}}

<!-- Written before any research. Frozen once research starts; later changes
     go to a new pack. A fresh session resumes by reading this file, then
     01-research.md, then 02-concepts.md. -->

- **Date**: {{date}} · **Pack**: `{{dir}}` · **Prior pack**: none | <path, and what changes>
- **Request (verbatim)**: "{{request}}"
- **Product (restated)**: <category, plus price tier and materials when known>
<!-- The gate reads the backticked terms on the next line and fails any prompt
     that drops one, so put every modifier the user gave there, verbatim. -->
- **Given attributes**: `<修饰词一>`, `<修饰词二>`, `<品类>`
- **Attribute equivalents**: <修饰词一> = <English rendering> = <another accepted spelling>; <修饰词二> = <…> — any one of these satisfies the attribute, so an English prompt need not carry the Chinese token
- **Inferred attributes** [inferred]: <what you added that the user did not say>
- **Pinned?**: a product photo was supplied, so prompts use a reference mode | **Unpinned: no reference image** — every prompt describes the product in words and colour or hardware can drift
- **Inputs**: text · images: <N> (<one line per image: what it shows, usable as first frame / subject reference / style ref>) · videos: <N> (`assets/ref-1/summary.md`) · links: <N>
- **Platform and market**: <TikTok Shop US | Douyin | 小红书 | Reels | …> — <inferred from language and request | asked>
- **Language**: on-screen text <zh | en> · voice <zh | en | none> · prompt language per model (see references/models/)
- **Target models**: {{models}}
- **Format**: 9:16 · duration per model <from its allowed set> · audio <on | off>
- **Research tier**: express | full · **tools present**: <WebSearch/WebFetch · Tavily · Brave · Apify (credit left …) · ffmpeg · none>
- **Assumptions (stated instead of asked)**: <…>
- **Must show**: `<部件一>`, `<部件二>` — features every prompt puts on screen; the gate fails a prompt that drops one, so put a feature here only if you mean it
- **Hard constraints**: brand tone <…> · must avoid <…> · category compliance <…>
- **Acceptance checklist** (tick each box in Phase 5, after checking it):
  - [ ] Concept A and B differ on at least four Viral DNA axes and share one product truth
  - [ ] Every user-given attribute (colour, size, shape, material) appears in every prompt
  - [ ] The hook lands inside the first shot, within the first second, in every prompt
  - [ ] Every prompt respects its model's limits (`check_pack.py` reports no FAIL)
  - [ ] <request-specific item>
- **Known unknowns going in**: <…>
