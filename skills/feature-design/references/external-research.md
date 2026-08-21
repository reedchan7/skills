# External research: answer decisions, not curiosity

Load during Phase 3 only. Research is conditional: every charter must answer
a named decision from recon or interrogation. Two search rounds with no
decision-changing evidence end the charter.

## Evidence discipline

- Prefer the source that owns a claim: official docs/specs/source, first-party
  product behavior, repository code/issues, or the original paper.
- A vendor page proves what the vendor documents, not user value or production
  performance. Label evidence `documented`, `observed`, or `measured`.
- Secondary sources may discover a primary source; they do not replace it.
- Every finding includes URL, access date, evidence class, limitation, and the
  question it answers. No citation → no normative SPEC claim.
- When sources conflict, preserve the conflict and make it a decision; never
  average incompatible claims into certainty.

## Charters — run only those needed

1. **Problem evidence.** Look for measured adoption, failure, support, or user
   workflow evidence relevant to this product category. Public anecdotes are
   weak evidence; say so. Output: what is known about the problem, not a
   feature list.
2. **Competitor behavior.** Inspect 2–4 leading products: observable workflow,
   defaults, limits, pricing gates, accessibility, empty/error states. Output:
   conventions users may expect, with the evidence class.
3. **OSS prior art.** Inspect 2–3 maintained projects: interfaces, data model,
   failure handling, tests, and issue/PR history that reveals pitfalls.
4. **Engineering practice.** Read current official platform guidance and,
   where architecture/algorithms warrant it, original engineering reports or
   papers. Confirm versions match the target toolchain.
5. **Buy vs build.** Compare the best library/service/internal capability on
   fit, maintenance, license, security posture, operational cost, reversibility,
   and exit strategy.

## Anti-bloat

Write the question list before findings. Every paragraph maps to a question.
Findings that cannot alter scope, an AC/NFR, an approach, or a buy/build choice
get one line or zero. Never add generic market history.

## Output

Copy `assets/research.template.md` to
`docs/features/<NNN>-<slug>/RESEARCH.md`. Findings remain evidence; the final
section may recommend decisions, each traced to finding IDs. The SPEC links to
the recommendation and records the decision — it does not duplicate the report.

## Limits and stop conditions

If authentication, paywalls, unavailable source, or time budget prevents
settling a load-bearing question:

1. Record what was tried and the exact blind spot.
2. State which decision cannot be justified.
3. At Phase 4, stop unless the user explicitly accepts that uncertainty or
   chooses a reversible validation slice.
