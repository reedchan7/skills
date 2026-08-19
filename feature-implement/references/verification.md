# Verification: exact candidate, integration, regression, sensitivity

Load for Phase 4. Evidence belongs to an immutable candidate identity. Any
subsequent code/test/config edit invalidates affected evidence and all
downstream review/readiness gates.

## Freeze the candidate

Record:

- HEAD and merge base.
- `git status --porcelain -uall`.
- Sorted task-owned file list with SHA-256, including untracked files.
- Staged/unstaged state and SPEC version/digest.
- Unrelated dirty-file hashes (must remain byte-identical).

When commit authority exists, prefer a reviewable checkpoint commit and verify
the worktree has no task-owned residue. Without commit authority, the content
manifest is the candidate identity.

## Integration sweep

1. Run every affected suite/check after the final slice.
2. Run full repo-native tests/lint/type/build locally when feasible; otherwise
   record the exact required CI gate and do not advance beyond local state until
   it passes.
3. Compare baseline failure fingerprints. Same name with changed error/stack is
   a new red.
4. Re-run early-slice checks after late slices.
5. Execute every active AC/RC/NFR `Verify:` method not already backed by fresh
   post-final-edit evidence.

An existing red cannot close a requirement. Every evidence-table row names the
command/probe, exit/result, candidate digest, and timestamp.

## Regression-contract sweep

For each RC:

- Reconfirm the credible causal path/consumer.
- Run its named test/probe against the frozen candidate.
- Record coverage or the blocking gap.

An RC failure is severity-classified by actual impact; it blocks readiness
until fixed or the SPEC is amended and re-approved. It is not automatically
Critical merely because it has an RC ID.

## Risk-selected mutation/sensitivity check

Run only when PLAN selects it:

- Deep high-risk decision logic: required.
- Standard: when new branching/state/authorization/money/data logic has weak
  sensitivity evidence.
- Express/presentation-only/config: normally N/A with reason.

Prefer repo mutation tooling. Otherwise:

1. Build a complete immutable manifest of the frozen candidate: every path,
   regular/symlink/directory type, executable mode, symlink target, and file
   SHA-256. Never mutate the primary dirty workspace.
2. For **each** mutation, create a fresh isolated copy from that manifest.
3. Pick 1–5 plausible mutations mapped to high-risk AC/RC/NFR (inverted guard,
   boundary, missing await, wrong default, dropped authz/error).
4. Apply one mutation, run focused checks, expect RED, record the catching test.
5. Discard that copy; do not “restore” it for another mutation. Re-verify the
   primary candidate's complete path/type/mode/link/content manifest before the
   next copy. Never use a destructive checkout against user-owned edits.
6. Survivor → add one spec-grounded test through the TDD loop on the primary
   candidate, refreeze, invalidate prior downstream evidence, and rerun.

The check measures test sensitivity for selected risks; it does not prove the
feature defect-free.

## Exit

- Candidate identity recorded.
- Final local/CI gates have explicit status.
- Every active requirement has fresh evidence or blocks advancement.
- Baseline fingerprints show no unexpected delta.
- Selected mutations caught and isolated copy restored byte-for-byte.
- Unrelated user files remain byte-identical.
