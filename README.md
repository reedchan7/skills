# skills

Personal Agent skills collected from day-to-day development and agent
workflow work.

This repository is a small source-of-truth for reusable `SKILL.md` workflows I
want to keep across local agents, experiments, and future projects.

## What's Included

| Skill | Purpose |
| --- | --- |
| [`code-review`](./code-review/SKILL.md) | Run read-only, risk-ranked, evidence-backed code reviews with strict false-positive suppression. |
| [`git-commit`](./git-commit/SKILL.md) | Write clear, scoped, review-friendly Conventional Commit messages and commits. |
| [`handoff`](./handoff/SKILL.md) | Write (and resume from) a HANDOFF.md so a zero-context future session can continue the work. |
| [`refactor`](./refactor/SKILL.md) | Evidence-based, behavior-preserving refactor planning: diagnosis, owner-approved options, phased roadmap, and self-contained executor task files. |

## Repository Layout

```text
.
|-- code-review/
|   |-- SKILL.md
|   `-- references/
|-- docs/
|   `-- research/
|-- evals/
|   `-- code-review/
|-- git-commit/
|   `-- SKILL.md
|-- handoff/
|   `-- SKILL.md
|-- refactor/
|   |-- SKILL.md
|   |-- references/
|   `-- assets/
|-- scripts/
|   `-- link-skill.sh
|-- LICENSE
`-- README.md
```

Each skill lives in its own directory and follows the standard skill shape:

```text
skill-name/
`-- SKILL.md
```

`SKILL.md` must start with YAML frontmatter:

```yaml
---
name: skill-name
description: Use when ...
---
```

Optional resources can be added only when they are actually useful:

- `references/` for larger background material loaded on demand
- `assets/` for templates or files used by the skill
- `scripts/` for repeatable commands or deterministic helpers

Runtime-specific metadata files (for example Codex's `agents/openai.yaml`) stay
out of this repository: these skills are linked into several agent CLIs, and only
one of them reads that file.

## Benchmarks

`docs/research/` records how the published code-review candidates were compared
and what the resulting skill must beat. `evals/` holds the behavioral benchmark
that decides it — a skill's claims are only as good as its paired no-skill
baseline.

`evals/` is not part of any skill: nothing under it is linked into an agent
runtime. Its generated case repositories are gitignored and rebuilt on demand:

```bash
python3 evals/code-review/private/build_cases.py
python3 evals/code-review/private/self_check.py
```

## Using These Skills

Clone the repository, then link or copy the skill directories into the skill
root used by the target Agent runtime.

For local OpenAI/Codex-style agents, a typical setup is:

```bash
mkdir -p "$HOME/.agents/skills"
ln -s "$PWD/git-commit" "$HOME/.agents/skills/git-commit"
```

After linking, start a new agent session so the runtime can load the updated
skill list.

## Writing Guidelines

- Keep each skill focused on one workflow.
- Put trigger conditions in `description`; the body loads only after the skill
  is selected.
- Prefer concise instructions and concrete examples over long explanations.
- Add scripts or references only when they reduce repeated work.
- Keep `SKILL.md` readable without requiring unrelated files.

## License

MIT. See [`LICENSE`](./LICENSE).
