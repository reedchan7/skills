# Interrogation: double-sided steelman + frontier questioning

Load during Phase 2, after recon. Goal: reach shared understanding of the
*right* problem before choosing a solution. The user's idea is a hypothesis,
not a requirement — and "don't build it" is a legitimate conclusion.

## Move 1 — Restate the problem (strongest form)

Before any question, write back the problem as if you were its best
advocate:

- What is actually being solved, for whom, and why now?
- What does the user's world look like when this succeeds?
- What is the implicit theory of value ("users will X because Y")?

State it in 3–6 sentences. If you cannot restate it convincingly, that gap
is your keystone question.

## Move 2 — Double-sided steelman

Argue both sides at full strength. Two short passages, each the best case a
smart advocate could make:

- **FOR the idea as stated**: why this, why now, what recon evidence or
  precedent supports it.
- **AGAINST**: the strongest of — don't build it (no real demand, metric
  won't move, maintenance tax exceeds value); buy/reuse instead (an existing
  library, product, or internal capability already does this); build a
  smaller slice (an Express-mode version would answer the demand question
  cheaply); wrong timing (a dependency or migration should land first).

Half-hearted objections are a discipline failure — the against-case must be
one you would genuinely defend.

## Move 3 — Name the cruxes

List the 1–3 variables that would flip the conclusion ("if existing users
already do this via export, the feature is unnecessary"; "if this must work
offline, the architecture inverts"). A crux is decision-relevant by
definition — anything that wouldn't change the outcome is not a crux and
not worth a question.

## Move 4 — The keystone question

Ask exactly ONE question first only when a genuine decision remains — the
single highest-information question, usually the largest crux. Its own
message, nothing else. If recon and the user's ask already settle every
material decision, record the sourced assumptions and move to the SPEC gate
instead of manufacturing a question. Format:

```
❓ **Keystone** — <question title>: <body; multiple choice when possible>

➡️ <your recommended answer, with one line of reasoning>
```

The question is self-contained: each choice states what it means and its
consequence, in the message itself — answerable without opening any file.

Wait for the answer. It typically reshapes everything downstream — asking
it alone protects the rest of the interview from a wrong premise.

## Frontier rounds

After the keystone, work the remaining decisions as a design tree. The
frontier is every question whose prerequisites are settled. Per round:

- ≤5 questions, numbered `❓ **Q1** …` each with `➡️` recommended answer.
- Impact order: scope > security/privacy > user experience > technical.
- Multiple choice preferred; the user should be able to answer a whole
  round with "1a, 2 yes, 3 your call".
- Self-contained rounds: every open choice is defined in the round's own
  message — what it means and its consequence. A one-line recap is enough
  only for something already decided or defined in full in the immediately
  preceding messages; never a bare reference to a file. Number questions,
  letter each question's choices (answers read like "1a, 2 yes"); once a
  choice is labeled, never relabel it.
- A question whose answer depends on another open question belongs to a
  later round.
- "Your call" / "whatever you think" → state your recommendation as the
  decision and record it as such — do not re-ask.

Facts never appear in a round. When a question needs a fact from the
environment (does the codebase already have rate limiting? does the vendor
API support webhooks?), perform the lookup and only downstream decisions
wait. Everything the user is asked must be a genuine decision or preference.

Defaults for the unasked must be sourced, reversible, low-impact, and visible
under Assumptions at the gate. Never default security, privacy, compliance,
retention, money, destructive behavior, public/external contracts, or
irreversible data decisions. If one of those remains unknown, it is a
frontier decision or owned deferral, never an assumption.

## Write-back rule

Every answer lands in the existing SPEC draft immediately, in the section it
belongs to (a scope answer → Goals/Non-goals; an edge-case answer → its AC;
a terminology ruling → used consistently everywhere). Never accumulate
answers in conversation and batch-transcribe later — that is how decisions
get dropped. Keep a dated `Q → A` line per answer in the spec's decision
log.

## Exit and stop

- Exit when the frontier is empty — every branch visited, nothing silently
  assumed — or the user explicitly says proceed with what you have (record
  the unexplored branches as Assumptions or Deferred).
- Stop (don't-build): when the against-case prevails and the user agrees,
  keep the SPEC at its canonical path, set `Status: Declined`, and record
  the steelman, decision, and revisit trigger in the decision log.

## Express-mode lite

Express mode compresses this file to: Move 1 (2 sentences), a one-line
against-check ("simpler alternative? existing capability?"), and a keystone
question only when a decision remains. If uncertainty surfaces, ratchet up
to Standard.
