# Collecting a stable review scope

Run the helper from the installed skill directory with Python 3.10+; keep its JSON
in session scratch outside the reviewed repository. It reads Git state without
staging, committing, fetching, or changing refs. It disables external diff helpers,
text conversion, and optional Git locks. The output is an inventory, not a review.

```sh
# Explicit endpoints: compare exactly these two commits.
python3 scripts/review_scope.py --repo /path/to/repo --base BASE --head HEAD
# Branch or PR: compare the merge base to the specified head.
python3 scripts/review_scope.py --repo /path/to/repo --base TARGET --head HEAD --merge-base
# All local states; include supporting files whose working contents you read.
python3 scripts/review_scope.py --repo /path/to/repo --local --context-path src/caller.ts
# Save the chosen invocation's stdout to a scratch file, then recheck it.
python3 scripts/review_scope.py --recheck /scratch/scope.json
```

Exit codes: 0 success/unchanged, 2 detected drift, 1 capture or argument failure.
Never interpret failure as an empty diff. `limits` identifies content the helper
cannot fingerprint fully, such as submodules. It does not copy files or prove that
all contextual dependencies were read. Add `--context-path` for each relevant local
caller/configuration/instruction file to the next capture, then use that expanded
manifest for the final recheck. Read committed context at the captured OIDs.

## Interpret the local states

- **Staged:** proposed index content relative to HEAD. Read with `git show :path`.
- **Unstaged:** worktree relative to index. Read both versions when they differ.
- **Combined:** final tracked worktree relative to HEAD. A reverted staged change
  can disappear here while remaining staged; attribute findings to their actual
  state. On an unborn branch, combined is a conservative staged/unstaged union.
- **Untracked:** inventory from `git ls-files --others --exclude-standard -z`.
  Decide relevance explicitly. Ignored artifacts require an explicit context path
  if they materially determine behavior; do not dump secrets into a report.

The manifest fingerprints the index entries, inventory, HEAD, changed working
files, symlink targets, file modes, and explicitly added context. It does not follow
symlinks outside the repository. A later recheck can detect changed content even
when `git status` still shows the same letters. It is a drift detector, not an
atomic filesystem snapshot: if files keep changing, pause the affected judgement
or create an authorized isolated copy and verify its contents against the manifest.

For local diagnostics, select the state relevant to the claim. Populate a disposable
copy with that state and necessary untracked files, then compare its hashes. Do not
run only committed HEAD and claim that it tests the dirty worktree. A detached
worktree alone also shares repository metadata and has ordinary network access.

## Manual fallback

When Python is unavailable, record resolved OIDs using `git rev-parse --verify` and
use `git diff BASE HEAD` for endpoints or resolve `git merge-base BASE HEAD` first
for branches. For local scope, combine the NUL-delimited inventories from:

```sh
git diff --cached --name-status -z
git diff --name-status -z
git ls-files --others --exclude-standard -z
git status --porcelain=v1 -z --untracked-files=all
```

Fingerprint the corresponding index content, file bytes/modes, and reviewed
context with available read-only tools; check them again before output. If tooling,
unmerged entries, inaccessible content, or dynamic dependencies prevent a reliable
comparison, expose the precise limit instead of claiming a frozen target.
