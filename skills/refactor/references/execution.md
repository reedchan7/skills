# Execute a refactor

Use for both direct user requests and RT tasks. A direct bounded request
does not require an RT file, base SHA supplied by the user, or a formal plan.
Establish the necessary scope and baseline from the repository yourself.

## Starting state and ownership

Read current instructions, target definitions, callers, tests and shared
utilities. Determine supported commands from the repository. Record HEAD
(or an unborn/no-Git state), relevant staged/unstaged/untracked changes and
the affected content. HEAD alone does not identify the working baseline.
Do not stage, stash, reset, clean or overwrite other contributors' work.

For changed files, distinguish initial edits from this task's later edits.
Keep a recoverable pre-edit copy/patch in scratch when restoration may be
needed; include file absence, mode or symlink state if the change affects it.
Do not expose sensitive contents in the report. A clean file can also change
concurrently: re-read affected content before applying/restoring a patch.
If changes overlap and ownership cannot be resolved, preserve both versions
and pause only the conflicting slice. Do not restore an entire directory or
file to HEAD when it contains user or concurrent edits.

Choose the closest faithful observation boundary and run its baseline before
editing. New characterization checks must pass on the old behavior first.
If the suite is incomplete or red, record exact relevant signals and what can
still be established. Static inspection can support a low-risk mechanical
change; do not claim runtime equivalence from it. Material behavior risk with
no adequate observation method requires closing the gap before transformation.

## Small-step loop

1. State the intent, preserved invariant and expected benefit of the next
   coherent step. For a nontrivial choice consult [diagnose](diagnose.md),
   [architecture](architecture.md) or [quality](quality.md) as relevant.
2. Apply the narrowest transformation that accomplishes it, using existing
   native/compiler-aware tooling where suitable. Preserve consumer contracts
   and relevant side-effect order. Check generated/dynamic references.
3. Run affected checks, inspect the diff and representative callers, and
   compare with the baseline. A bounded regression caused by this step may
   be repaired within it. If the cause is unclear, undo only this step's
   owned edits and split it. Do not patch unrelated failures.
4. Record a safe checkpoint: current content and completed observations.
   Commit only when authorized. Preserve the initial index/refs otherwise.
   Checkpoints that will be integrated must remain usable; do not leave
   unresolved consumers or a half-migrated contract as the final result.
5. Continue until the requested result is achieved. For systemic work,
   evaluate the pilot's benefit and migration assumptions before expanding.

Do not mix an unrelated bug fix with the refactor. If both were requested,
keep their behavior contracts and verification distinct; finish both within
authorization. Tests may move or change access seams, but expected business
behavior must not be weakened to accommodate the implementation. Prove any
necessary expectation change belongs to a separately authorized behavior delta.

## Picking up an RT task

Read the full task. It needs scope/authority, baseline and assumptions,
behavior envelope, benefit/acceptance, checks and recovery appropriate to its
risk. An older task may express those facts under different headings; validate
substance rather than requiring an exact template. Resolve a missing material
contract before editing; do not invent owner decisions.

The RT template owns the versioned embedded protocol used for standalone
handoffs. The current template is `rt-protocol-v2`; existing versions do not
override current user/project instructions or authorize a dangerous recovery.
Use compatible task-specific steps. An unsafe or obsolete instruction needs
a safe equivalent within scope, or a clearly stated unresolved decision.

Compare current relevant files, dependencies and consumers with the task's
recorded baseline and assumptions, including dirty content. Unrelated drift
can proceed; mechanical drift can be adapted when the assumptions still hold.
Behavior/dependency/ownership drift that invalidates the approach makes the
affected task STALE. Reassess it within the user's planning authority or
report the concrete decision needed. Never automatically rebase shared work.

Check prerequisites and real coordination conflicts. Update task/roadmap
records only within authorization. An unresolved prerequisite blocks dependent
work; it does not prohibit independent authorized work.

## Completion and recovery

Run required project checks, [quality outcome checks](quality.md#outcome-check)
appropriate to the change, and an ownership/scope diff check. Preserve initial
unrelated content and index entries; inspect any unexpected final changes.
Confirm no temporary follow-up feature, debug output or evaluation artifact
has entered the deliverable.

Report completed behavior and benefit evidence, material failures/unknowns and
remaining work. Mark an RT task done only when its actual acceptance holds;
otherwise record partial, blocked or stale state accurately if updates are
authorized. A green suite without the requested structural result is not done.

Recovery is specific to the step: restore only owned edits to the recorded
pre-step content while preserving later edits. If data or external effects
were involved, a source-code revert is insufficient; use the separately
authorized recovery plan in [safety](safety.md). Never claim full reversibility
without accounting for those effects.
