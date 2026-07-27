# Review task

This archive contains independent Git repositories under `cases/`, one per case,
plus `task.json`.

1. Read `task.json`. It lists every case, its repository path, its base and head
   refs, and the JSON schema your response must match.
2. For each repository, review only `HEAD^..HEAD`. Read whatever unchanged code
   in that repository you need in order to reason about the change.
3. Report only findings introduced or newly exposed by that change. A case may
   contain no finding at all. Do not assume any distribution of findings,
   severities, or defect categories across cases.
4. Do not modify any repository, and do not write outside a temporary directory.
5. If `skill/` is present, follow it. Where it conflicts with `task.json`, the
   schema and instructions in `task.json` win.
6. Return exactly one JSON object matching `output_schema`, and nothing else.

No network access is available or needed.
