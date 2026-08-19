# Tidy sweep: clean-code pass without structural change

Load in Tidy mode. A tidy sweep applies small, behavior-preserving,
category-based cleanups across a scope (one file up to a repo). Wide but
shallow: many sites, one transformation class per batch. All iron laws
apply — especially two hats and the behavior envelope.

## Scope contract

In scope for this mode:

- Extract hard-coded values into named constants or config
- Deduplicate repeated literals that share meaning
- Delete provably dead code
- Rename locals / private helpers to reveal intent
- Replace magic flags and indices with named enums where language-native
- Flatten trivially nested conditionals into guard clauses
- Delete comments that restate the code

Out of scope — escalate instead of doing:

| Found | Route to |
|---|---|
| Public signature, module boundary, or dependency change needed | Bounded / Full mode, owner decides |
| Bug, wrong logic, contradicting comment vs code | Report only. Never fix in a tidy batch (two hats) |
| God module, cycles, mixed abstraction levels | Record as candidate for Assessment / Full mode |
| Generated code, vendored deps, lockfiles, migrations | Leave untouched |
| Wholesale reformatting | A formatter's job; separate dedicated commit only if asked |

## Golden rule: same value ≠ same meaning

Two literals merge into one constant only when they change for the same
reason. A timeout of 30 and a page size of 30 are two constants — or one
stays inline. When unsure, do not merge; duplicate constants are cheaper
than a coupled bug. List uncertain pairs in the report.

## Hard-code taxonomy → destination

| Finding | Destination | Notes |
|---|---|---|
| Magic number with intent | Named constant at the narrowest shared scope | Name states meaning and unit: `RETRY_LIMIT`, `TIMEOUT_SECONDS` |
| Repeated string key (status, event, header name) | Constant / enum / language idiom | Only when meaning matches at every site |
| URL, endpoint, host, port | Config (env var or settings module) with a default | Default MUST equal the old inline value — envelope |
| File path, directory | Constant, or derived from one root constant | |
| Timeout, limit, threshold, interval | Named constant or config | Unit belongs in the name |
| Credential, API key, token | STOP the batch. Flag to owner; never relocate-and-commit, never print the value | A leak is a security incident, not a tidy finding |
| User-facing copy | i18n catalog if the project has one; else leave and note | |
| Test-only literals | Usually leave; extract only when repeated within one test module | Test readability beats DRY |
| Self-evident values (0, 1, -1, obvious arithmetic) | Leave inline | Naming these is noise, not clarity |

## Other in-scope findings

- Dead code: delete only when provably unreachable — no references AND no
  dynamic use (reflection, string dispatch, DI containers, templates,
  re-exports, config-driven entry points). Delete; never comment out.
- Naming: rename misleading or meaningless locals and private helpers.
  Public names are Bounded-mode work.
- Comment rot: a comment restating the code → delete the comment. A
  comment contradicting the code → flag it; do not "fix" the code to
  match the comment.
- Duplicated block: near-identical blocks within one module may collapse
  into a private helper if all call sites keep identical behavior.
  Cross-module dedup changes dependency shape — escalate.

## Protocol

1. Preflight (same as Bounded): authority, dirty tree recorded, baseline
   verify → failure ledger.
2. Inventory: scan the scope; group findings by category × module.
   Starter scans (tune per language; linters with magic-number rules are
   better when present):
   - numbers: `rg -n '\b\d{2,}\b' <scope>`
   - repeated strings: `rg -oIN '"[^"]{3,}"' <scope> | sort | uniq -c | sort -rn | head -20`
   - secret bait: `rg -in '(api[_-]?key|secret|token|passw)\w*\s*[:=]' <scope>`
   - dead-code candidates: symbol defined, `rg` finds no second reference
3. Plan: per category — sites, proposed name, destination, and the
   meaning question answered for every merge group. If the sweep spans
   more than one module or ~20 sites, present the grouped plan and get
   owner approval before editing.
4. Execute in batches: one category (or one module) per batch; one batch
   = one commit-sized step. Verify against the ledger after every batch;
   an unexpected delta reverts the batch, never patches forward.
5. Report, not narrate: batches applied, sites changed, flagged items
   (secrets, contradicting comments, uncertain merges), escalation
   candidates recorded for other modes.

## Verification

The tidy envelope is bit-identical behavior: same outputs, same errors,
same logs, same serialized values. Known traps:

- Constant extraction changing type or precision (int → float, string
  interning, sign/width in typed languages)
- Config extraction moving a read from call time to import/startup time,
  or introducing a new failure path when the variable is unset
- Enum replacement changing serialized wire values
- Dead-code deletion removing a registration side effect (import-time
  hooks, decorators)

Baseline run before the first batch, full run after each batch, final
run at the end. "Pass" means no unexpected delta vs the ledger, never
"all green".
