# skills

Personal Agent skills collected from day-to-day development and agent
workflow work.

This repository is a small source-of-truth for reusable `SKILL.md` workflows I
want to keep across local agents, experiments, and future projects.

## What's Included

| Skill | Purpose |
| --- | --- |
| [`git-commit`](./git-commit/SKILL.md) | Write clear, scoped, review-friendly Conventional Commit messages and commits. |

## Repository Layout

```text
.
|-- git-commit/
|   `-- SKILL.md
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

- `agents/openai.yaml` for UI-facing metadata
- `scripts/` for repeatable commands or deterministic helpers
- `references/` for larger background material loaded on demand
- `assets/` for templates or files used by the skill

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
