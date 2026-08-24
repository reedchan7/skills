# skills

Personal Agent skills collected from day-to-day development and agent
workflow work.

This repository is a small source-of-truth for reusable `SKILL.md` workflows I
want to keep across local agents, experiments, and future projects.

## What's Included

| Skill | Eval | Purpose |
| --- | --- | --- |
| [`code-review`](./skills/code-review/SKILL.md) | [`evals/code-review`](./evals/code-review) | Run read-only, risk-ranked, evidence-backed code reviews with strict false-positive suppression. |
| [`feature-design`](./skills/feature-design/SKILL.md) | [`evals/feature-dev`](./evals/feature-dev) | Produce one approved normative SPEC: repository/problem evidence, double-sided steelman, targeted external research, verifiable AC/RC/NFR, and rollout decisions. User-invoked as `/feature-design`. |
| [`feature-implement`](./skills/feature-implement/SKILL.md) | [`evals/feature-dev`](./evals/feature-dev) | Implement an approved SPEC in tracer-bullet TDD slices; freeze the exact candidate, verify bounded regressions, independently review it, explore applicable surfaces, and report only evidence-supported readiness state. |
| [`git-commit`](./skills/git-commit/SKILL.md) | — | Write clear, scoped, review-friendly Conventional Commit messages and commits. |
| [`handoff`](./skills/handoff/SKILL.md) | — | Write (and resume from) a HANDOFF.md so a zero-context future session can continue the work. |
| [`refactor`](./skills/refactor/SKILL.md) | — | Evidence-based, behavior-preserving refactor planning: diagnosis, owner-approved options, phased roadmap, and self-contained executor task files. Includes a lightweight Tidy mode for clean-code sweeps (hard-coded values, duplicated literals, dead code, naming). |
| [`tasteful-frontend`](./skills/tasteful-frontend/SKILL.md) | [`evals/tasteful-frontend`](./evals/tasteful-frontend) | Build and restyle UI with modern, high-taste polish: direction-setting, typography, layout, color, depth, motion, states, copy, accessibility floors, and anti-AI-slop discipline with concrete values and a 10-item ship gate. |
| [`tasteful-frontend-audit`](./skills/tasteful-frontend-audit/SKILL.md) | [`evals/tasteful-frontend-audit`](./evals/tasteful-frontend-audit) | Audit, score, and diagnose existing UI (product / page / component) against the tasteful-frontend invariants: measured evidence, a severity-weighted deduction ledger, and triage-ordered concrete fixes. |

`feature-design` and `feature-implement` share one eval because they are a
paired workflow, not two independent products.

## Repository Layout

```text
.
|-- skills/                      # linked into agent runtimes
|   |-- code-review/
|   |-- feature-design/
|   |-- feature-implement/
|   |-- git-commit/
|   |-- handoff/
|   |-- refactor/
|   |-- tasteful-frontend/
|   `-- tasteful-frontend-audit/
|-- evals/                       # not linked; paired with skills/ by name
|   |-- code-review/
|   |-- feature-dev/             # covers feature-design + feature-implement
|   |-- tasteful-frontend/
|   `-- tasteful-frontend-audit/
|-- docs/
|   `-- research/
|-- scripts/
|   `-- link-skills.sh           # one smart linker for personal + Matt + all agents
|-- LICENSE
`-- README.md
```

Each skill lives in its own directory and follows the standard skill shape:

```text
skills/skill-name/
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

`docs/research/` records what published candidates and evidence a skill must
beat. `evals/` holds deterministic and behavioral benchmarks — a skill's claims
are only as good as its paired no-skill baseline.

`evals/` is not part of any skill: nothing under it is linked into an agent
runtime. Its generated case repositories are gitignored and rebuilt on demand:

```bash
python3 evals/code-review/private/build_cases.py
python3 evals/code-review/private/self_check.py
python3 -m unittest -v evals.feature-dev.test_contracts
python3 evals/feature-dev/private/self_check.py
```

## Using These Skills

One script. No args = full smart sync:

```bash
./scripts/link-skills.sh
```

It will:

1. Link every personal skill in `skills/` (`code-review` publishes as
   `code-review-pro`)
2. Auto-detect a Matt Pocock clone and link those too (`code-review` → `matt-code-review`)
3. Keep personal names when they already own a hub entry (e.g. `handoff`)
4. Retire known renames and sweep broken hub symlinks
5. Fan out hub entries to Claude / Codex / Grok / zcode / kimi / pi /
   reasonix / Gemini / Antigravity (CLI + IDE) / dsh / Cursor / agy /
   openclaw / iflow / qwen / trae / continue

Optional one-offs:

```bash
./scripts/link-skills.sh git-commit              # single personal skill
./scripts/link-skills.sh code-review             # still installs as code-review-pro
./scripts/link-skills.sh /path/to/skill [as]     # any external skill dir
./scripts/link-skills.sh --unlink some-name      # remove from hub + agents
```

After `git pull` on Matt (or editing a personal skill), just re-run
`./scripts/link-skills.sh`. Then start a new agent session so runtimes reload.

Hub root: `~/.agents/skills`.

## Writing Guidelines

- Keep each skill focused on one workflow.
- For model-invoked skills, put trigger branches (not workflow summaries) in
  `description`; for user-invoked skills, set `disable-model-invocation: true`
  and keep the description human-facing.
- Prefer concise instructions and concrete examples over long explanations.
- Add scripts or references only when they reduce repeated work.
- Keep `SKILL.md` readable without requiring unrelated files.

## License

MIT. See [`LICENSE`](./LICENSE).
