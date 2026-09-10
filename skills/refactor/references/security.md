# Security properties of the affected refactor

Use only when the transformed path handles untrusted inputs, authorization,
sensitive data, privileged operations or bounded resources. Preserve the
security contract and make its ownership clearer; do not expand into a general
hardening project without an actual finding and authorization.

Trace input → normalization/validation → authorization → privileged effect
→ output/log/storage. Identify the subject, tenant/resource, authoritative
decision point and every entry route, including background/retry paths.

| Boundary change | Required question / useful negative observation |
|---|---|
| Extract shared access logic | Is authorization enforced for every operation with the correct subject, object and tenant? Exercise a denied and cross-tenant case where relevant. |
| Move validation or parsing | Does the exact value used by the sink receive the check? Preserve normalization, parameterization and output-context escaping. |
| Centralize cache/state | Can identity or permissions leak between requests? Retain tenant/user key scope, lifetime and invalidation. |
| Wrap errors/retries | Does failure still deny or abort as required? Preserve error visibility without exposing sensitive values; prevent duplicate privileged effects. |
| Move logging/serialization | Are redaction, field allowlists and output exposure unchanged? A debug wrapper must not serialize credentials or an entire request context. |
| Change async/resource management | Are limits, timeouts, cancellation and cleanup retained? An eager load or retry loop can change resource exposure. |
| Move filesystem/network calls | Are path containment, destination restrictions and privilege boundaries still applied to the final target? Retain defenses against check/use changes. |

Simplification should reduce the number of places that must implement a
security policy without leaving alternate paths unguarded. A helper named
"authorize" is no evidence unless its calls dominate the relevant effects.
An existing common mechanism, middleware or token does not by itself prove
the new path is protected.

When a pre-existing vulnerability is found, report the concrete reachability
and impact with redacted evidence. Do not silently repair behavior under a
refactor label, or propagate/expose it further. Continue separable safe work;
if the refactor depends on the unsafe behavior, resolve the behavior-change
scope before claiming completion. A separately authorized security fix needs
its own acceptance showing the undesired behavior is prevented.

Do not print secrets while looking for them. Prefer an available scanner's
redacted output; for initial text triage use filename-only search such as
`rg -l -i '(api[_-]?key|secret|token|passw)\w*\s*[:=]' <scope>`.
This pattern is incomplete and may match non-secrets. Do not dump matching
lines, repeated string literals, environment values or full configuration.
Report only location and type until safe inspection is possible.

Security principles are review questions, not a guarantee that every risk
has been eliminated. Negative tests cover the stated boundary and cases;
report unknown consequential exposure honestly.
