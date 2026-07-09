---
name: handoff
description: Use when a session is about to end, context is running low, or the user asks to hand off / save progress for a future session — e.g. "write a handoff", "session is ending", "save state before we stop", "交接", "写交接文档", "会话要结束了". Also use when resuming work in a repo that contains a HANDOFF.md.
---

# handoff

Write a HANDOFF.md that lets a brand-new, zero-context session continue the
work without asking a single question. Verified facts only; every guess must
be labeled.

## Writing a handoff

### 1. Capture real state — don't trust memory

```bash
git branch --show-current
git status --short
git log --oneline -5
```

If the last build/test command is cheap, re-run it so the reported state is
current, not remembered.

### 2. Write `HANDOFF.md` at the repo root (overwrite any existing one)

This file is explicitly requested by the user — create it even if other
rules discourage adding documentation files.

Fixed skeleton:

```markdown
# Handoff — <task name> (<date>)

## Goal
One sentence: what we're building, why, and the acceptance criteria
that mean "done".

## Current state
- Branch: `<name>` — uncommitted changes: yes/no (one-line summary)
- Done so far: each item with file refs (`path:line`), marked
  **verified** or **written-but-unverified**
- Build/test: exact commands run (verbatim, copy-paste runnable)
  and their results

## Stuck on
The exact error/symptom (paste the original text), causes already
ruled out, and the current best hypothesis marked `[assumption]`.

## Next steps
Priority-ordered list. Step 1 must name the file to open, the change
to make, and the command that verifies it.

## Pitfalls — do not repeat
Only pitfalls actually hit in this session, each written as:
symptom → root cause → correct approach.
```

### 3. Constraints

- ≤150 lines total — cut detail rather than grow the file
- Every file reference is a relative path; every command is copy-paste
  runnable
- Anything unverified carries an `[assumption]` label — a guess inherited
  as fact is the #1 handoff failure
- Write only this one file; make no other changes

### 4. Hand the user the opening line

After writing the file, end your reply — in the chat, NOT inside
HANDOFF.md — with one line the user can paste into the next session:

> Read HANDOFF.md first, then continue <task name>, starting from
> Next steps #1.

## Resuming from a handoff

When asked to resume, or when HANDOFF.md exists at session start: read it,
then verify "Current state" against reality (`git status`, re-run the listed
test command) before acting — the file may be stale. Execute Next steps in
order. Update or delete HANDOFF.md once the work has moved past it.

## Never

- A narrative essay or chronological log of the session
- Unverified claims presented as facts
- Vague next steps ("continue the fix", "keep debugging")
- Pitfalls without a root cause
