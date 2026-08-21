# Scores — 2026-08-21 (skill v2, invariant architecture)

Generator: claude-sonnet-5 --effort medium. Weighted violations
(broken 3 · illegible 2 · inconsistent 1 · bland 0.5), lower is better.
Reviewed at 1440×900 screen-by-screen + 375px, plus mechanical greps.

## driftwatch-landing

| Run | Weighted | Notes |
| --- | --- | --- |
| baseline | ~9.5 | gradient headline word, mint accent + rainbow icon chips (I4), glow shadows (I5), no focus-visible (I7, sev 2), no reduced-motion (I6), 5-star rows + MOST POPULAR badge, ▪-text logo wall |
| skilled-1 | ~0.5 | clean grid (hero split, container-anchored), varied feature weights (1 wide + 2×2), real host table as showcase, logo wall dropped entirely; miss: no tabular-nums on stats band |
| skilled-2 | ~2.0 | clean grid, stats band, diff card hero; misses: styled-text logo wall (bland), 01/02/03 numbered markers (bland), **ragged CTA datums across pricing cards (inconsistent 1, user-caught 2026-08-21)** — reviewer also missed it by judging this section from the full-page thumbnail; invariant 1 extended to horizontal datums, protocol reminder: every section gets a real-viewport pass |

| skilled-3 (row-datum verify) | ~0.5 | after extending invariant 1 to horizontal datums: prices at identical y (2837/2837/2837), CTAs 2960/2960/2964 — residual 4px from a two-line card description, vs 20px+ ragged before the change; measured via getBoundingClientRect, not eyeballed |

## driftwatch-console

| Run | Weighted | Notes |
| --- | --- | --- |
| baseline | ~5.5 | `transition: all`, no focus-visible (sev 2), no reduced-motion, strip+badge severity double-encoding, session context leaked into demo data ("reed.chan" avatar) |
| skilled-1 | ~0.5 | proper table with column headers, quiet severity pills, unified diff with line numbers, destructive action red + confirm, empty/skeleton reachable from visible UI; miss: large idle area in detail column (bland) |
| skilled-2 | ~1.5 | role-separated mono (data only), metadata row, states via visible toggle; misses: one `transition: all`, center-column dead space |

## Acceptance vs PROTOCOL

1. **skilled < baseline on every brief** — pass (0.5–1.0 vs 9.5; 0.5–1.5 vs 5.5).
2. **No regression vs prior version** — pass; the skill-v2-era severity-2
   failure (off-grid hero cluster) did not recur in any of the four skilled
   runs: every hero/section anchored to the container grid.
3. **Stability** — pass; no invariant violated at severity ≥2 in one skilled
   run but clean in its twin.
4. **Expression diversity** — **partial fail**: all four skilled runs (and
   both prior-era runs) converged on dark theme + amber accent. Attribution:
   the anti-slop dictionary bans indigo/mint/cream/acid families, leaving
   amber as the surviving "safe" hue (survivorship bias), compounded by the
   single SRE-flavored product in both briefs. Layer 2's "derive from the
   product's world" is weaker than the dictionary's negative space. Action:
   collect cross-brief data (non-infra products) before changing the skill;
   if convergence holds across worlds, the fix belongs in Layer 2
   (strengthen derivation / add rotation), not in more bans.
