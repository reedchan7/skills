# Oracles

One file per brief, written at freeze time with the retrieval date. Unlike a
research oracle, this one cannot fix the creative answer — there is no single
correct concept for a tote bag. It fixes what is checkable:

- **Product truth**: the exact attributes a correct run must carry into every
  prompt, and the drifts a careless run makes (白黄 → cream, 藏青 → black,
  托特包 → handbag, 10寸 → 10 litres, 子弹头 → plain tube).
- **Mode**: the generation mode the supplied assets should produce.
- **Traps**: claims the category forbids in the named market, and hooks that
  are so over-used in this category that presenting one as an edge is a defect.
- **Model contract**: the limits in force on the freeze date, so a prompt that
  violates one is a hard failure even if the dialect file has drifted.

Oracles are never shown to the generating agent.

| Brief | Oracle |
| --- | --- |
| `tote-bag-bicolor` | pending — write from marketplace listings and the category's platform policy |
| `lunch-bag-navy-10in` | pending |
| `lipstick-bullet-new` | pending — cosmetic claim rules for the named market are the core of this one |
| `tumbler-en-us` | pending |
| `handbag-with-images` | pending — the expected mode and the role of each image |
| `lunch-bag-with-reference` | pending — the reference video's measured duration, cut count, and shot length |
| `not-this-workflow` | none needed — the pass condition is that no pack is produced |

A brief without an oracle can still be run for hard-failure invariants 1, 3, 4
and 5 and for weighted defects; invariant 2 and the trap list need the oracle.

The two asset-bearing briefs need their assets committed beside them before
their first scored run: three product images and one short vertical reference
video, all cleared for redistribution. Until then those briefs run only in the
maintainer's local copy.
