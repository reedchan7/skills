# Diagnose the maintenance problem

Use for assessment or a nontrivial structural choice. Gather enough evidence
to decide the next useful slice, not an exhaustive smell inventory.

## Start from a change story

Take a recent defect, recurring edit or user-provided upcoming change. Trace
entry → decisions → effects → consumers. Locate duplicated knowledge, hidden
assumptions, state ownership and coordination points. Read relevant callers,
tests, build rules and history before proposing structure.

Record each material candidate compactly:

- observed friction and affected behavior, with `path/symbol` and revision
  plus dirty-content identity when relevant;
- proposed causal explanation, confidence and counterevidence;
- smallest transformation, preserved invariant and expected benefit;
- how the hypothesis could fail, and an observation that would decide it.

Use facts and inference separately. Missing history, coverage or production
data means unknown, not zero defects or proven stability.

## Combine signals at the relevant scale

| Signal | Useful question | Confounder to check |
|---|---|---|
| Churn + structural complexity | Where does difficult code repeatedly cost effort? | Renames, generated/vendor code, bulk formatting and release commits |
| Co-change history | Which policies or modules repeatedly need coordinated edits? | Small samples, common releases and unrelated changes bundled in commits |
| Incidents or fix concentration | Which invariants are repeatedly misunderstood? | Commit-message labels are weak evidence; trace an actual defect |
| Fan-in/out and cycles | Which dependency makes changes contagious? | A widely used stable utility can be healthy; a cycle may be only type-level |
| Nesting and decision structure | Which alternatives are hard to enumerate or test? | Essential domain branching can be clear; extraction can hide it |
| Shared mutable state | Who can change this value and when is it valid? | Aliasing, caches, globals, lifecycle and transaction boundaries |
| Coverage and test seams | Can we observe the affected contract without changing it? | High coverage may miss effects, boundary values or negative paths |
| Ownership/change boundaries | Does a change require coordination for a real reason? | Team topology is evidence, not an automatic service-extraction mandate |

Use repository-native symbol/build graphs where available; supplement with
text and runtime tracing for reflection, registration, DI, plugins, routes,
templates and config-driven entry points. A failed search is not proof of no
consumers. Exclude generated outputs from transformation candidates but inspect
their source/generator and downstream contract when affected.

For history, choose and report a window appropriate to repository age and
activity. Inspect representative commits instead of treating a message match
or raw frequency as a defect measure. Follow renames where practical. Rank
ordinally with reasons; do not multiply guessed scores into precise ROI.

## Turn symptoms into competing hypotheses

| Observed difficulty | Candidate move | Check before choosing |
|---|---|---|
| A function interleaves policy, parsing and IO | Separate a coherent calculation or effect boundary | Does the seam hide useful knowledge, or require passing the entire context? |
| Deep nesting hides the normal path | Guard clauses, named predicates, or a decision table | Evaluation order, short-circuit effects and cleanup remain equivalent |
| Repeated edits express one business rule | Give the rule one owner | Similar syntax must represent the same policy and change reason |
| A shared helper accumulates flags for divergent callers | Inline/split by policy, then extract genuine commonality | Retain caller-specific edge cases; more duplication may reduce coupling |
| Callers manipulate another module's representation | Move behavior to its owner or narrow the interface | Mutation ownership and aliasing must stay explicit |
| A class is mostly pass-through wrappers | Inline or merge shallow layers | The wrapper may own authorization, retries, instrumentation or compatibility |
| A switch repeats one varying policy across consumers | Centralize policy; consider a table/function or Strategy | A single exhaustive switch may already be the clearest design |
| Many primitives/parameters obscure relationships | Named value/parameter type or smaller responsibility | Avoid data bags and avoid introducing stricter validation as a refactor |
| Import cycle prevents isolated changes | Move one ownership boundary or invert the problematic edge | Avoid a miscellaneous shared module that merely relocates the cycle |
| Tests break for private moves | Re-anchor the same assertion to a stable behavioral seam | Do not delete assertions that protect an actual caller contract |

These are hypotheses, not prescriptions. Function length, parameter count,
SOLID violations and named smells alone are insufficient reasons to edit.
See [architecture](architecture.md) for boundary/pattern decisions and
[quality](quality.md) for measures and outcome evidence.

## Select the slice

Prefer a slice with meaningful user value, a clear observation boundary and
manageable dependency/rollback cost. A safe vertical slice can cross files;
splitting work purely by directories may break an invariant across checkpoints.
Retain the current design when the alternative has no supported net benefit.

Defer low-value candidates with a concrete revisit trigger. Low churn does
not dismiss an upcoming migration, a known security exposure or an expensive
failure. When evidence is incomplete, report the best supported result and
the consequential gap; do not fill the gap with architecture doctrine.
