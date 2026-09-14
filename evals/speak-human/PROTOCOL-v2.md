# Speak-human continuation: isolated evaluation protocol

Frozen candidate: 74182525194c6ee129c0ce5e8a5f48c961680754c526a5a47574e51fee529963
Registered at: 2026-09-14T08:43:51.881958+00:00

The first delivery was premature. Old eight-task batch scores are historical evidence, not acceptance evidence. This continuation changes the input unit, tasks, checks, and skill method.

## Development and held-out separation

- Three context-heavy development tasks (release judgment, mechanism explanation, constrained provider choice) test reasoning-connected communication; three negative controls test already-clear prose, exact JSON, and requested depth.
- v4, v5, and v6 were tried on the same Claude and Kimi development tasks. Select v5 for held-out testing: initial author review found v6 more speculative and verbose. Retain all outputs including failures. This selection is exploratory and does not prove uplift.
- Four new held-out cases are independently authored without seeing the skill. Two attempts using Claude did not yield complete case data (plan-only response, then timeout); use four isolated GPT author calls. Do not revise the skill after reading held-out outputs without marking those cases as development for the next iteration.
- Run each model/condition/case in a fresh CLI session. No eight-task JSON batch. The source is synthetic and the model is explicitly barred from executing mentioned actions.
- Compare against the same strong short instruction used before: concise answers preserving necessary information, context, data, conditions, conclusions, understanding and decision support. Both arms receive the identical user task and evidence.

## Measurements

1. Preserve each case's material meanings and distinguish unsupported additions. Author reviews judge allegations against quoted source evidence; log disputes and adjudication. Do not turn a reader's optional detail preference into a fact failure.
2. Blind paired readability assessment by Claude with evidence quotes; no model/arm/version labels. Counterbalance A/B labels and swap a fixed subset to detect position sensitivity. Report ties and reversals, not a manufactured 4-point mean. Semantic fact audit is separate from preference.
3. Calibrate the judge on intentionally wrong scope/status/order, invented assurance, and two equivalent good rewrites. Failed calibration invalidates automated fidelity conclusions until repaired.
4. Use a fresh proxy reader on a stratified subset: only the answer plus prewritten comprehension questions, never the source. Inspect answer recovery; this is a model proxy, not a claim about actual human reading speed.
5. Measure character length descriptively, within case/language only. Shorter is useful only alongside completeness and clarity. Full-detail and teaching controls may legitimately be longer.
6. Check strict JSON by parsing, and inspect depth/negative controls and real installed-skill invocation.

## Decision rule before held-out generation

A useful release needs more readability wins than losses against the strong baseline, no loss of required output contracts, and no material loss or invented decision claims in the delivered demonstrations. Report the aggregate fidelity error rate and per-case failures for both arms; a style win never compensates for factual harm. Any recurring skill-specific material failure requires correction and fresh confirmation, not a caveat appended to a release claim. Held-out cases must show transferable benefit, not only the tuned development tasks. No claim of statistical significance or universal accuracy from this small suite. Evidence and good demonstrations support a scoped claim of practical benefit, not a guarantee about every possible model output.
