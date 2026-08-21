# Review loop: exact candidate, independent verdicts, bounded repair

Load for Phase 5. The loop is bounded; the quality bar is not.

## Build the review target

Use the Phase-4 frozen candidate:

- **Committed candidate:** frozen merge-base → head SHA; verify no task-owned
  staged/unstaged/untracked residue.
- **Local candidate:** frozen HEAD → working tree, explicitly including:
  commit list, status inventory, `git diff --cached`, `git diff`, every relevant
  untracked file's content, and content hashes.

Write the package in OS temp/scratch outside the repository. Re-check status and
hashes before accepting the review; drift makes the review stale.

Never use `BASE..HEAD` alone when local changes exist.

## Independent review

Invoke `code-review-pro` when installed, supplying:

1. Approved SPEC (binding behavior and global constraints).
2. PLAN (scope, test migrations, deviations, checkpoints, evidence).
3. Exact review target and candidate identity.

Require two independent verdict axes:

- **Spec:** missing / extra / misunderstood, per active AC/RC/NFR where
  determinable.
- **Engineering:** introduced correctness, state/concurrency, security,
  compatibility/data, performance, test-sensitivity, and maintainability
  defects.

The reviewer receives artifacts, never author-session history or instructions
to suppress a suspected finding. Reports and test claims are untrusted until
checked against the candidate/evidence.

## Fallback when code-review-pro is unavailable

Use another fresh read-only context with the embedded contract. Express may
fall back to self-review when no independent context exists, labeled
non-independent. Standard/Deep stop below `Locally verified` until an
independent review is supplied; a waiver records acceptance of an unfinished
gate, not readiness.
For each finding require:

```text
location       changed path + tight range
axis           spec | correctness | security | compatibility | data |
               performance | tests | complexity
claim          falsifiable defect
introduced_by  candidate change
trigger        concrete input/state/timing/caller
impact         wrong behavior or violated contract
suppressor     guard/type/caller/framework guarantee checked and ruled out
fix            minimum root-cause direction
```

Severity: Critical / Important / Minor, independent of confidence. Drop
pre-existing, unlocated, tool-enforced, and conjectural items.

## Repair rounds — maximum three

Round 1 is the full review. Each later round is:

1. One fix batch for all open Critical/Important findings.
2. Covering tests and affected checks.
3. Refreeze candidate identity.
4. Scoped re-review of the fix diff: ADDRESSED / NOT ADDRESSED plus new
   breakage in the fix only.

Round 3 ends additional autonomous repair attempts.

- Disproved/contestable finding: rule out with concrete counterevidence.
- Real Minor: fix if in-scope or record follow-up/risk.
- Real unresolved Critical/Important: STOP. User may change scope/SPEC or end
  the attempt; it cannot reach Locally verified/production-ready while open.

The user can accept an experimental/non-ready handoff, but a waiver does not
turn an unmet requirement, RC, security gate, or real Critical/Important into
green.

## Record

PLAN review log stores candidate digest, independence, rounds, every finding,
fixed/disproved/open status, and final verdict per axis. Any code edit after
the final verdict invalidates it.
