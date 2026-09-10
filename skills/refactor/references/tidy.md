# Tidy without changing policy

Use for wide but shallow cleanup. Follow the common [execution](execution.md)
loop, grouping transformations by shared intent and reviewable scope. No RT
file or planning-document bundle is required.

## Decide whether a cleanup earns its cost

| Candidate | Useful action | Preserve / reject |
|---|---|---|
| Literal with unclear meaning/unit | Name it at the narrowest useful scope | Keep type, value, evaluation timing and representation |
| Repeated literal or block | Share only the same policy/change reason | Same value or syntax alone is insufficient |
| Fixed URL/host/port/path | Named constant if clarity improves | New env/config override is new behavior; use it only when separately requested |
| Misleading local/helper name | Rename with caller/reference awareness | Public, reflected or serialized names need compatibility analysis |
| Nested conditionals | Guard clause or clear predicate | Preserve short-circuit effects, error precedence and cleanup |
| Suspected dead code | Remove with consumer and side-effect evidence | No static references does not rule out dynamic registration |
| Comment | Remove a redundant restatement or update an authorized explanation | Retain intent, contracts, constraints, tooling directives and legal notices |
| User-facing copy | Normally leave | Moving to i18n can change interpolation, escaping and fallback |
| Test literal | Usually retain local explicit examples | Excessive fixture reuse can obscure expected behavior |

Leave obvious arithmetic and self-evident values inline. Do not add constants,
enums, configuration or helpers just to satisfy a generic clean-code label.
Duplicated constants can be preferable to coupling unrelated concepts.

## Inventory and batches

Read the scope, callers and existing linter/static-analysis output. Searches
generate candidates, not proof. Avoid broad string dumps that may expose
credentials; use redacted or filename-only triage from [security](security.md)
if secret handling is relevant. Inspect definitions with semantic context.

Summarize larger batches by intention and affected areas. Continue within
existing authorization; neither a file count nor module count requires a
fresh approval. If a real public/dependency/behavior tradeoff emerges, route
that item through design or migration assessment and continue independent
bounded cleanup.

Use one transformation intent per coherent step. Run the relevant affected
checks after each step and the required integration/project checks at the
appropriate boundary. Do not repeat an expensive full suite without a new
reason. Attribute unexpected failures: repair a bounded self-introduced
regression or restore only the step-owned edits; record unrelated failures.

Generated/vendor code and migrations are not ordinary tidy targets. Change
their authoring source only when in scope and regenerate using the repository
workflow when required. Do not hand-edit generated artifacts to hide drift.

## Finish

Inspect actual callers and the final diff. Confirm unchanged behavior and
that the new names/grouping clarify intent without added navigation or policy
coupling. Report useful changes and material unresolved items; do not turn
every deferred literal into a finding or claim quality from site counts.
