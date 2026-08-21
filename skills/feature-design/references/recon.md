# Recon: repository reality and problem evidence

Load during Phase 1. The goal is not broad exploration; it is enough verified
context to ask the highest-value question without making the user supply facts
the repository already contains.

## Read first

1. Every file, issue, SPEC, screenshot, or URL the user named.
2. Governing instructions (`AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`),
   `CONTEXT.md`, and ADRs in the affected area.
3. The closest existing flow and its tests, end-to-end at the highest useful
   seam.

## Evidence packet

Record each finding in the SPEC draft:

```text
claim          one factual statement
class          measured | observed | documented | inferred
source         path:line, command output, or source URL
relevance      which design decision or regression risk it informs
limitation     what this evidence cannot establish
```

### System evidence

- Existing behavior and entry points for the closest comparable feature.
- Directory, naming, error, state, persistence, and test conventions.
- Public contracts, stored data, config, events, consumers, and operational
  signals the feature can affect.
- Current behavior at those seams — candidates for the regression contract.
- Toolchain and platform constraints from manifests/config, never memory.

### Problem evidence

Look for evidence that the problem exists before researching solutions:

- Product analytics or feature usage (measured).
- Support tickets, incidents, user interviews, or sales/customer requests
  (observed/documented).
- Existing workarounds in code, docs, or user workflows (observed).
- A stakeholder assertion without corroboration (inferred until verified).

Absence is data: write “not measured” instead of inventing demand. Never treat
competitor behavior as evidence that this product's users need the feature.

## Scope by mode

- **Express:** one existing flow, its test seam, touched consumers, and hard
  constraints. Stop when no decision depends on more context.
- **Standard:** trace 1–2 comparable flows and all directly affected consumer
  classes.
- **Deep:** map the subsystem, data ownership, external contracts, deployment
  topology, and decision-relevant product evidence.

With parallel explorers, use distinct read-only charters and require
`path:line` evidence plus 5–10 key files. Their summaries are leads; re-read
the load-bearing files yourself.

## Exit

Recon is complete when:

- The current behavior and touched seams are stated with evidence.
- Facts needed for the steelman and keystone question are known or explicitly
  unavailable.
- The first regression-contract candidates and coverage limits are named.
- No user question asks for something the codebase can answer.
