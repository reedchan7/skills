# Speak human evaluation

The current release is 1.0.0, as requested by the user after development: select necessary content first, then use paragraphs,
labelled points, or sections according to its complexity. The 1.0.1 concision
comparisons remain evidence for those development snapshots, not new tests of the current release.
The v11/1.0.0 judgments below are historical, not current user acceptance. Historical version labels and hashes are unchanged; use the hashes to distinguish snapshots from the release.
See `cases-concision.json`, `results/concision-1.0.1.json` for the first focused comparison,
`results/concision-1.0.1-final.json` for the intermediate attempt, and
`results/concision-1.0.1-release.json` for the 1.0.1 shortened guide. All retain actual answers and hashes;
the question-specific meanings replace the earlier tendency to require every source detail.
Start with [current results](../../docs/research/speak-human-current.md) and
[final confirmation protocol](./PROTOCOL-final.md).

The current release's [installation record](./results/install-current.json) contains
the exact source hash, 21 agent directory checks plus the shared hub, nine native
runtime discovery results, and Claude's successful load of the exact release body.
Installation checks establish availability, separately from writing-quality tests.

Fresh sessions alone do **not** isolate global instructions or installed skills.
Use `isolated.py --clean` for Claude, Gemini, GLM, and DeepSeek. OpenCode uses an
empty child XDG configuration, disables external/project/Claude discovery, and
uses a minimal text-only agent; Claude uses safe-mode with skills/tools disabled.
Authentication is preserved. Grok's system override still showed about 32k input
tokens on a tiny probe and is not a verified clean route. GPT/Kimi and prior
seven-family results are existing-profile observations. No global settings change.

The continuation uses one task per fresh session. Its historical design is in
[PROTOCOL-v2.md](./PROTOCOL-v2.md), [development cases](./cases-v2-dev.json), and
[independently authored held-out cases](./cases-v2-heldout.json). The earlier batch
evaluation below is archived evidence, not the current acceptance method.

```sh
python3 evals/speak-human/isolated.py --clean --cases evals/speak-human/case-final-transfer.json --models claude gemini-api deepseek-api --arms brief skill --output evals/speak-human/runs/new-run
python3 evals/speak-human/assess.py --cases evals/speak-human/case-final-transfer.json --baseline evals/speak-human/runs/new-run --candidate evals/speak-human/runs/new-run --output evals/speak-human/runs/new-assessment --swap
python3 evals/speak-human/reader.py --run evals/speak-human/runs/new-run --output evals/speak-human/runs/new-reader
```

Each output directory must be new. Model calls use existing local credentials;
no secrets are exported. Generation prompts exclude answer keys and reader questions.
Raw runs are gitignored; tracked result exports retain actual answers and judgments.
Run `python3 evals/speak-human/export_evidence.py` to refresh continuation exports.
Frozen cases are now public regression fixtures, not future unseen tests.

## Archived initial method

Eight synthetic cases compare the same model and raw task under three conditions:
no writing skill, a one-sentence brevity prompt, and the frozen candidate skill.
The generator receives `id`, `request`, and `source` only. `required` is a private
semantic checklist during execution; it is disclosed here for reproducibility.
These authored fixtures are regression evidence, not independent held-out cases.

Predeclared gates, before generation:

- No material omission, unsupported addition, changed certainty, or format error
  in any candidate answer. A strong average cannot cancel an individual failure.
- Score clarity, causal coherence, decision usefulness (where relevant), natural
  language, and economy on 0–4 anchored scales. A material error vetoes preference.
- A useful measured advantage requires at least +0.3 macro-mean quality versus
  each baseline and more pairwise wins than losses, with no new material failure.
  Ties and near-ceiling baselines must be reported; shorter alone is not a win.
- Report characters descriptively, never as semantic preservation or token cost.
- Separate blocked calls from bad answers. Freeze every attempt and model identity;
  do not replace models or cherry-pick reruns. Timeouts stop the entire process
  group. API-backed Claude calls have a per-call USD 1.50 budget cap.

Each model receives the eight independent tasks as one batch, in a fresh session
per arm. The shared JSON transport is outside the simulated answer: its values
contain the actual user-facing output. This reduces call overhead but permits
cross-case influence; it is not a multi-turn or tool-execution benchmark.
Native agent system prompts and account settings differ across providers. Compare
arms *within* each runtime; this is not a ranking of model families.

Claude Code performs a read-only, anonymous evaluation of each pair against the
raw requests, sources, and semantic checklist. It receives neither the skill nor
arm/model labels. Machine checks cover JSON transport and exact-format constraints
only. The author audits material findings and records any disagreement explicitly.
A single model judge has bias; human comprehension has not been experimentally
measured. No claim of universal information-loss prevention is warranted.

Run `python3 evals/speak-human/run.py --help`. Runs are gitignored; tracked results
retain answers, anonymous grading, hashes, and failure metadata so the conclusions
remain reviewable without local raw logs. Model calls use existing local login
profiles and synthetic data. The runtime skill has no evaluator dependency.

## Run and inspect

```sh
python3 evals/speak-human/run.py --output evals/speak-human/runs/my-comparison
python3 evals/speak-human/grade.py evals/speak-human/runs/my-comparison --output evals/speak-human/runs/my-grading
python3 evals/speak-human/summarize.py --runs evals/speak-human/runs/my-comparison --judges evals/speak-human/runs/my-grading --output evals/speak-human/results/my-comparison.json
python3 evals/speak-human/audit_final.py --runs evals/speak-human/runs/my-comparison --output evals/speak-human/runs/my-source-audit
```

Every output directory must be new. `--models` and `--arms` bound a run; default
models use the seven working routes discovered on this machine. Availability is
time-specific. The CLI profiles remain user-owned. The scripts never install a
model, change a global provider, purchase credits, or retry a failed model call.
The runner snapshots source and protocol, saves all raw responses and exit status,
and marks unusable transport as blocked. Manual wrapper recoveries in this study
are explicit in collected manifests; they do not alter individual answer strings.

V1/V2 were development comparisons; V3 was the initial single-arm regression
pass. See [research and results](../../docs/research/speak-human-2026-09-14.md).
That initial preservation gate failed and stable quality uplift was not demonstrated.
The final source audit uses a structured-output schema and the actual user/source,
without the private checklist: this reduces unjustified field-placement expectations
found in earlier judging. All raw judgments remain model opinions until checked
against the source, even when they satisfy JSON Schema.
