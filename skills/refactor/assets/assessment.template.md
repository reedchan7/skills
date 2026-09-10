# Assessment template

Use for a requested durable assessment; adapt detail to the decision.

<!-- TEMPLATE START -->

# Refactor assessment — <scope>

- Goal: <user's maintenance problem>
- Scope and constraints: <affected area, no-touch zones, actual authority>
- Baseline: <revision plus relevant working content, date>
- Coverage: <inspected areas, consequential gaps>

## Recommendation

<Preferred outcome and smallest useful slice, evidence, tradeoff and the
decision needed only if material ambiguity or missing authority remains.>

## Current behavior and design

<Entry points, consumers, policy/state ownership, dependency constraints,
behavior observations and relevant baseline failures.>

## Findings and candidates

| Observed maintenance problem | Evidence and confidence | Candidate / counterevidence | Expected benefit |
|---|---|---|---|
| <concrete friction> | <path/symbol + content identity> | <causal hypothesis and limits> | <observable outcome> |

## Alternatives and selected slice

<Compare the current structure and useful alternatives. Explain why the
selected boundary hides the right knowledge, which invariant it owns, what
callers gain, and what would falsify the recommendation. No forced pattern.>

## Acceptance and delivery

- Preserved behavior and observation:
- Primary benefit evidence and non-regression constraints:
- Pilot and dependencies:
- Compatibility/rollout/recovery where needed:
- Unresolved decisions and consequential unknowns:
- Deferred work and concrete revisit triggers:

<!-- TEMPLATE END -->
