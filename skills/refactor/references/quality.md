# Judge refactoring quality

Use for a structural choice, complexity goal or outcome claim. Select the
dimensions relevant to the user's problem; do not compute a universal score.

## What should become easier?

| Dimension | Useful evidence | A misleading improvement |
|---|---|---|
| Comprehension | Main flow, names, nesting, concepts held in mind, navigation needed to explain one outcome | Shorter functions that require tracing many shallow helpers |
| Cohesion/information hiding | One policy or invariant has a clear owner; callers need less representation knowledge | Files renamed by domain while shared state still leaks everywhere |
| Changeability | A representative rule change affects fewer independent decisions/consumers | Fewer changed files achieved by a giant module or generic flag-driven helper |
| Control-flow complexity | Same-tool per-function distribution, worst affected paths, module decision burden | Lower maximum obtained solely by splitting or moving branches |
| Testability | A stable seam exercises decisions and effects with less setup and fewer brittle mocks | Tests bypass integration semantics or only assert private calls |
| Reliability/security | Contract and negative-path observations at the affected boundary | Happy-path tests pass while ordering, authority or failure handling changes |
| Performance/resources | Equivalent workloads, latency distribution, allocations/IO or bundle cost where relevant | A cleaner interface hides an extra query, eager load or retained buffer |
| Delivery cost | Consumer migration, dependencies, rollout and cleanup burden | Local elegance requires synchronizing every service deployment |

Choose one primary benefit and relevant non-regression constraints before
editing. Do not claim all dimensions improve. A tradeoff may be acceptable
when explicit, within scope and justified by the goal.

## Complexity measurement without gaming

Cyclomatic complexity describes control-flow independence. For a connected
single-routine control-flow graph, the conventional `E - N + 2` measure
depends on the graph's modeling conventions. Use an existing analyzer and
record tool/version, language rules, scope and exclusions; do not substitute
an ad-hoc regex count and call it McCabe complexity.

Cognitive Complexity is a separate heuristic emphasizing flow interruptions
and nesting. It is neither a universal measure of human comprehension nor
interchangeable with cyclomatic complexity. If no analyzer is available,
describe observed nesting/branching qualitatively or label a proxy explicitly.

Compare the same logical responsibility before and after, including extracted
helpers. Report relevant maxima/distribution and where decisions moved;
per-function base values make raw summed cyclomatic scores sensitive to
function count. Check navigation, state and coupling alongside any score.
Do not remove necessary decision cases or contract tests to meet a threshold.
Branch/path metrics do not establish path feasibility, value correctness,
concurrency behavior or security completeness.

Use thresholds already justified by the project as screening gates; explain
exceptions from evidence. Do not introduce a global complexity limit as part
of an unrelated refactor. Size, coverage, churn and coupling metrics also need
their denominator, scope and collection method.

## Outcome check

For a substantial structural refactor:

1. Re-run the affected behavior observations and required project checks
   against the recorded baseline. Confirm test discovery and expectations
   still cover the contract; no unexpected red, skipped coverage or weakened
   assertions. Remaining known failures need their actual relevant evidence.
2. Revisit the original change story. Explain which decision now has an
   owner, what knowledge was hidden, and what a maintainer no longer has to
   coordinate. Inspect representative callers, not only the new helper.
3. Compare the chosen benefit evidence and its costs on identical scope.
   Classify the result as demonstrated, inspection-supported, unchanged,
   regressed or unknown. Distinguish structural indicators from productivity.
4. When uncertainty about changeability matters, attempt one realistic
   follow-up change on disposable before/after copies with the same public
   requirement and acceptance checks. Compare correctness first, then the
   independent policies touched, navigation, code/test changes and new
   exceptions. Do not ship this hypothetical feature. If only one side was
   exercised, disclose it; it is not a controlled before/after comparison.
5. If the primary benefit did not appear, reconsider the slice instead of
   relabeling fewer lines as success. Do not undo other contributors' work
   during that reconsideration.

An independent maintainer can strengthen comprehension evidence for a
substantial change when delegation is available and authorized. Give the
actual task and code without the designer's preferred conclusion. A toy
benchmark, self-report or one successful follow-up does not establish a
general productivity gain. Future lead time and incident rate require later
observation; do not fabricate them at completion.

## Report to the reader

Lead with the practical outcome. Usually a short explanation of the problem,
changed responsibility and key evidence suffices. Use a compact before/after
table only when several comparable measurements matter. Include failed or
unrun acceptance items and material tradeoffs; omit empty sections, repeated
labels and a chronology of routine commands.
