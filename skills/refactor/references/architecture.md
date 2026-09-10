# Structure, abstractions and patterns

Use when a change crosses ownership/dependency boundaries or the right
abstraction is uncertain. Start with the current design as a viable option.

## Design around knowledge and change

Locate the decision that should vary independently: representation, business
policy, external protocol, lifecycle or storage mechanism. Give it an owner
with an interface that hides the relevant knowledge. Splitting sequential
processing stages is useful only if it produces such a boundary; otherwise
it can distribute one decision across many modules.

Inspect the interface from a caller's perspective. Count conceptual obligations:
required call order, flags, state sharing, error handling and representation
details, not just method names. A small interface hiding useful work may be
better than many tiny classes. Preserve comments that explain non-obvious
contracts or intent; do not replace clear explanation with excessive extraction.

Before extracting, try describing the responsibility without "and" joining
unrelated policies or a generic name such as "manager". This is a diagnostic,
not a naming rule. Before merging, check whether the pieces change for the
same reason. Before centralizing state, identify lifetime, owner and every
mutation route. Moving fields does not establish encapsulation.

## Use SOLID as questions

| Lens | Ask | Avoid |
|---|---|---|
| Single responsibility | Which independent policy changes force this unit to change? | One class per action or splitting an invariant across units |
| Open/closed | Is there an actual recurring variation that needs a stable extension boundary? | Registries and plugins for imagined future requirements |
| Substitution | Can existing clients use the new implementation with the same accepted inputs, guarantees, exceptions and state transitions? | Stronger preconditions, weaker outcomes or hidden mutation under an unchanged signature |
| Interface segregation | Which consumer must learn or depend on operations it does not need? | One interface per method with no reduction in consumer knowledge |
| Dependency inversion | Which policy is coupled to a volatile implementation? Can a narrow seam reverse that edge? | Interfaces for stable leaf functions or a DI framework introduced solely for this refactor |

Do not turn OO vocabulary into a requirement for functional or data-oriented
code. Functions, modules, records, algebraic data types and composition may
express the same intent more simply in the repository's language.

## Pattern selection is a tradeoff

Name the observed problem, simplest direct solution and the extra cost of a
pattern. Select it only when that cost buys a needed property. Existing
patterns can be removed when their variation or boundary has disappeared.

| Design pressure | Simple option first | Pattern when justified | Contract/cost to retain |
|---|---|---|---|
| Repeated varying policy | Function or explicit decision table | Strategy; State for meaningful state transitions | Dispatch precedence, missing cases, transition ownership; added indirection |
| Third-party representation leaks into policy | Small translation function/module | Adapter or anti-corruption boundary | Error mapping, cancellation, rate limits and data fidelity |
| Construction repeats invariants/lifecycle | Named constructor or factory function | Factory/Builder for actual variants or complex staged assembly | Defaults, initialization order, cleanup and partially built state |
| Cross-cutting behavior at one boundary | Explicit wrapper | Decorator or middleware chain | Authentication, retries and transaction ordering; wrapper order is behavior |
| Independent reactions to events | Direct calls with explicit ordering | Observer/pub-sub when decoupling is actually needed | Delivery, duplicate handling, ownership and failure visibility |
| Shared algorithm with divergent exceptions | Separate caller policies, inline if necessary | Re-extract only the common invariant | Avoid boolean mode matrices and irrelevant parameters |
| Complex workflow state | Explicit transitions and owned state | State machine when illegal transitions are the problem | Persisted state values, resumability and cancellation |

Repetition count is a clue, not a universal threshold. Two sites may already
share a dangerous invariant; many identical literals may describe unrelated
policies. Deliberate duplication can be the cheaper design.

## When architecture should change

Require evidence beyond a local smell: repeated cross-boundary change cost,
dependency cycles with concrete consequences, ownership conflicts, independent
scaling/deployment needs, or a user-mandated platform constraint. Distinguish
an internal module boundary from a process/service boundary: network, delivery,
consistency and operations costs are not solved by moving a directory.

| Context | Candidate | Evidence needed before recommending |
|---|---|---|
| Thin CRUD with local friction | Retain layers, simplify locally | Why local changes address the observed problem |
| Domain decisions tangled with IO | Cohesive policy module and narrow IO seams | Which rules need independent reasoning/testing and which effects are shared |
| Monolith with coordinated edits | Enforced internal module boundaries | Consumer clusters and knowledge that can be hidden |
| Independent deployment/scaling need | Service extraction along a proven seam | Data ownership, consistency, failure recovery, observability and team capacity |
| Mandated runtime/framework migration | Incremental compatibility boundary | Same-business baseline, consumer migration and rollback feasibility |

For the selected option, state what evidence would falsify it. Prototype only
the disputed boundary on a disposable copy when reading cannot settle it.
Use a first vertical slice to test the migration path and maintenance benefit.
Keep later phases coarse until that evidence exists.

Boundary enforcement is appropriate when preventing a measured recurrence is
part of the goal. Reuse the project's import/build/lint rules; do not add a
new architecture test framework or dependency merely to certify the design.
