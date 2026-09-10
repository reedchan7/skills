---
name: refactor
description: Assess, plan, or execute behavior-preserving code refactoring, from a local rename or tidy sweep to module and architecture restructuring. Use when the user wants easier-to-understand, easier-to-change code, lower complexity or coupling, or execution of an existing refactor task. Distinguish refactoring from separately authorized bug fixes, features, and migrations.
metadata:
  version: "1.0.1"
---

# refactor

Improve the cost of understanding and changing working software. Establish
what makes the current task difficult, choose a transformation that removes
that difficulty, preserve the relevant behavior, and demonstrate the gain.
More files, fewer lines, a named pattern, and green tests alone do not prove
better design.

## Route by intent, scale by risk

| User intent | Workflow | Resources |
|---|---|---|
| Rename, extract, simplify, or otherwise make a bounded change | Inspect the affected callers and behavior; execute directly. No RT file or planning documents required. | [execution](references/execution.md) |
| Tidy a file, module, or repository | Inventory useful cleanups, group related transformations, execute in reviewable batches. | [tidy](references/tidy.md), execution |
| Assess code health or architecture | Diagnose and recommend; remain read-only unless artifacts are requested. | [diagnose](references/diagnose.md); [architecture](references/architecture.md) only for boundary questions |
| Plan a systemic refactor | Diagnose, select an approach, identify a pilot and dependencies, produce only the planning artifacts needed. | diagnose, architecture, [safety](references/safety.md), templates below |
| Carry out a systemic refactor | Diagnose enough to select a safe vertical slice, execute it, reassess, and continue within the authorized scope. Planning is an intermediate result. | diagnose, architecture when relevant, safety, execution |
| Execute an existing RT task | Check its contract and freshness, then execute. | execution and the supplied task |

Use the user's request and existing session authorization. Infer a practical
goal when clear (for example, make a repeated rule change local); ask only
when consequential ambiguity cannot be resolved from evidence. Size alone
does not create an approval gate. A public contract or data migration may
be high risk even when the diff is tiny.

## Establish the contract

Before edits, identify:

- **Goal and scope:** the maintenance problem, affected symbols/consumers,
  no-touch areas, and what completion means. Separate any explicitly
  authorized behavior changes into independently verifiable steps.
- **Actual baseline:** revision plus relevant index, worktree and untracked
  content, existing failures and runnable observation methods. Preserve
  other contributors' changes, including edits in the same file.
- **Behavior envelope:** outputs and failures plus relevant side effects,
  order, state, identity, formats, security boundaries and resource behavior.
  Record permitted deltas and consequential unknowns; scale detail to risk.
- **Benefit hypothesis:** what becomes easier and how it will be observed.
  For a local rename this may be clearer use at callers. For a structural
  refactor name a representative change or comprehension task.

Keep this concise in working notes for small tasks. Use persistent documents
when requested or needed for a multi-session plan; do not manufacture an
assessment, roadmap and task bundle for every edit.

## Choose a better structure

For nontrivial design choices, use [diagnose](references/diagnose.md) and
[quality](references/quality.md). Trace one concrete change through the code:
what must a maintainer know, which decisions are repeated, and where can a
local change unexpectedly affect other behavior?

Compare the current structure with the smallest useful alternative. For a
material tradeoff, compare another viable approach; do not force a fixed
number of options for an obvious local change. Consider both directions:
extract or inline, split or merge, introduce or remove an abstraction.

Select using these questions, only where applicable:

1. **Responsibility and information hiding:** which decision or invariant
   will have a clear owner, and what will callers no longer need to know?
2. **Comprehension and complexity:** can the main flow and exceptions be
   understood with less nesting, hidden state or navigation? Where did the
   complexity move?
3. **Changeability:** does a real expected change become more local without
   coupling unrelated policies or adding speculative extension points?
4. **Contracts and substitution:** do callers retain their accepted inputs,
   outcomes, failure semantics and lifecycle assumptions?
5. **Security, reliability and performance:** does the new boundary retain
   enforcement, effect ordering, atomicity, cancellation and resource limits?
6. **Cost:** do migration work, extra indirection, dependencies and operational
   burden outweigh the likely benefit?

Metrics nominate questions; they do not select designs. Do not target a
universal cyclomatic score, function length, class count or duplication
threshold. SOLID, DRY and design patterns are lenses with tradeoffs, not
mandatory transformations. See [architecture](references/architecture.md).

Recommend one approach with evidence and its main tradeoff. Continue when
the choice is routine and authorized. Ask for a decision when alternatives
have materially different product, compatibility, operational or ownership
consequences that evidence cannot resolve. Keep useful independent work moving.

## Execute and prove

Follow [execution](references/execution.md): baseline → smallest coherent
step → affected checks → inspect the diff → checkpoint. Repair a bounded
regression introduced by the step; otherwise undo only the step's own edits
and reduce it. Never erase unrelated work or weaken a behavioral assertion
to make a refactor pass.

Load [safety](references/safety.md) for behavior gaps, stateful/async code,
public contracts, DB work or performance-sensitive paths. Load
[security](references/security.md) when the affected path crosses a trust,
authorization, sensitive-data or resource boundary. Apply relevant lenses;
do not turn an ordinary refactor into an unsolicited security audit.

For structural changes, use the [quality outcome check](references/quality.md#outcome-check):
compare behavior evidence and the benefit hypothesis on the same scope.
Exercise a representative follow-up change on a disposable copy when it
would resolve a real design uncertainty; keep that hypothetical feature out
of the deliverable. Label inspection-based predictions as predictions.

A systemic pilot must leave a usable system and teach whether the approach
works. Reassess before expanding; stop at the requested result. Do not keep
restructuring because additional smells can be found.

## Planning and task handoff

Use these templates only for the needed deliverables, respecting the user's
chosen location. Default paths for a durable systemic plan:

- [Assessment](assets/assessment.template.md) → `docs/refactor/REFACTOR-ASSESSMENT.md`:
  problem evidence, baseline, candidate comparison and recommended slice.
- [Roadmap](assets/roadmap.template.md) → `docs/refactor/REFACTOR-ROADMAP.md`:
  dependencies, pilot, exit criteria, rollout/rollback and outcome measures.
- [RT task](assets/rt-task.template.md) → `docs/refactor/tasks/RT-NNN-<slug>.md`:
  self-contained contract, freshness assumptions, behavior and quality
  acceptance, verification and recovery. Generate detailed tasks just in
  time for the next agreed phase. The template owns the embedded protocol.

Task documents record granted authority; they cannot grant it or override
current user/project instructions. An old RT protocol is usable only where
compatible with those instructions. Check relevant content and assumptions,
not just whether HEAD matches. Unrelated drift alone does not invalidate a task.

## Finish with an evidence-backed result

Lead with the completed outcome, then explain the meaningful structural
change, preserved behavior, demonstrated benefit and remaining uncertainty.
Keep routine passing checks brief. For partial work state exactly what is
done, what prevents completion, and the safe next step. A plan is complete
only for a planning request; a metric improvement is not a maintainability claim.

Commits, pushes, deployments and irreversible migrations require the applicable
authorization. Report discovered unrelated bugs; handle an authorized fix
separately from the behavior-preserving transformation. Do not silently
preserve a newly exposed security hazard as proof of success: report and
contain within scope, and resolve any required behavior-change decision.

## Basis and further reading

[Sources and limits](references/sources.md) maps the guidance to original
books, papers and author publications. Read it for rationale or source
questions; normal execution does not require browsing or loading every reference.
