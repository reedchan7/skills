---
name: git-commit
description: Use when the user asks to commit code, save changes, submit changes, or prepare a Conventional Commit message.
---

# git-commit

Write commits that are clear, traceable, and review-friendly. One theme per
commit, Conventional Commit format, compact body.

## Steps

### 1. Inspect

```bash
git status
git diff --stat           # unstaged
git diff --stat --cached  # staged
```

If the change set is unfamiliar, read the actual diff (`git diff`) — the
message must describe what really changed, not what you assume changed.

### 2. Split by theme

| Situation | Strategy |
|-----------|----------|
| All changes share one theme | Single commit |
| Independent themes (e.g. UI + API) | Split; stage by file group or `git add -p` |
| Feature and bug fix mixed | Must split; `feat` and `fix` never share a commit |

### 3. Compose the message

```
<type>(<scope>): <subject>

- <change 1>
- <change 2>
```

- **Type**: `feat` / `fix` / `refactor` / `perf` / `test` / `docs` /
  `chore` / `ci` / `style`
- **Scope**: change centered on one module → name it; cross-module → omit
- **Subject**: ≤72 chars, imperative mood ("add" not "added"), lowercase
  first letter, no trailing period, behavior over implementation

**Body** — add one only when the subject alone can't carry the change:

- One bullet per change, `- ` prefix, on consecutive lines
- ≤72 chars per line; a wrapped line continues with two-space indent
- Describe behavior and intent; don't inventory file paths, function
  names, or config keys
- Omit the body entirely when it would only restate the subject

### 4. Commit — the whole message through exactly one `-m`

```bash
git commit -m "$(cat <<'EOF'
feat(update): add post-update version confirmation

- Confirm updated agents report the expected version
- Add an opt-out flag for update-only flows
EOF
)"
```

Git turns every extra `-m` into a separate paragraph and inserts a blank
line before it — that is exactly where broken, airy bullet lists come
from. One `-m`, always; the heredoc carries the newlines.

Let pre-commit hooks (lefthook, husky, …) run. Never `--no-verify`.

### 5. Verify before reporting done

```bash
git log -1 --format=%B
git log -1 --stat
```

Check the printed message against all of:

- [ ] Subject ≤72 chars, blank line between subject and body
- [ ] Bullets on consecutive lines — no blank line between any two
- [ ] Nothing you didn't write (stray footers, duplicated paragraphs)
- [ ] Changed files match what the message claims

Any mismatch → fix with `git commit --amend` (safe while unpushed),
then re-verify.

## Examples

```
fix(chat): handle empty message content in stream

- Fall back to an empty string when a chunk arrives without content
- Cover the null-content edge case in stream tests
```

```
refactor: unify error handling across services

- Route service errors through one central handler instead of
  per-call-site try/catch
- No behavior change; media, chat, and billing call sites updated
```

Subject says it all → no body:

```
docs: document auth and chat API surface
```

## Never

- Vague subjects: `update`, `fix stuff`, `some changes`
- More than one `-m` flag on a commit command
- Blank lines between body bullets
- `--no-verify`
- Non-English messages (unless the project already commits in another
  language)
