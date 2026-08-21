# Architecture assessment and (rare) selection

Load only when Phase 2 evidence shows a cross-boundary problem.

## Default: retain

The default recommendation is "retain the current architecture, fix local
problems". An architecture change needs SYSTEMIC evidence — at least one of:

- Dependency-direction violations are widespread, not local
- Cross-boundary temporal coupling dominates the change history
- The same business change repeatedly costs edits in ≥3 layers/services
- Team scaling is blocked by shared ownership of one tangled core
- A platform/runtime migration is already mandated

Messy-but-working layered code with local smells gets local fixes, not a new
architecture. "Do nothing" must appear in every option set.

## Assessment checklist

- Dependency direction: what imports what? Does the core depend on edges?
- Boundary quality: can a module's internals change without breaking
  consumers? If not, name exactly what leaks.
- Screaming architecture: does the top-level structure say what the system
  DOES, or which framework it uses?
- Module depth: a simple interface hiding real complexity is deep (good); a
  wide interface over thin logic is shallow (suspect).
- Change alignment: do things that change together live together?

## Selection table (context → style)

| Context | Fits | Avoid |
|---|---|---|
| CRUD over a DB, thin logic | Layered + transaction script | Hexagonal ceremony, microservices |
| Rich domain rules, many invariants | Domain core + ports/adapters (hexagonal) | Anemic logic spread through layers |
| Many external integrations | Adapters + anti-corruption layers at boundaries | Third-party SDK calls inside the core |
| Monolith + growing team | Modular monolith with enforced module boundaries | Premature microservices |
| Proven independent scaling/deploy needs | Service extraction along existing module seams | Big-bang decomposition |
| Event-heavy domain | Event-driven with explicit schemas and idempotent consumers | Event soup without ownership |

A recommendation must state: why this fits THIS product and team (tie to the
Phase-0 goal), the migration cost, and what evidence would falsify the
choice.

## Patterns (GoF) — vocabulary, not a shopping list

A pattern is justified only by naming the OBSERVED finding it resolves:

- Repeated conditional on a type discriminator (F-xxx) → Strategy / State
- Construction logic duplicated at call sites → Factory
- Incompatible third-party interface at a boundary → Adapter
- Cross-cutting notification without coupling → Observer
- Expensive object-graph setup, especially in tests → Builder

Rule of three: do not abstract before the third occurrence. If you cannot
cite the finding ID a pattern resolves, you are pattern shopping — stop.
