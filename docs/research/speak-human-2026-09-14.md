# Clear answers across agents: research and evaluation

**Current implementation and results:** [中文结果说明](./speak-human-current.md). The current release is 1.0.0, as requested by the user after the concision and adaptive-structure corrections. Development labels (including v11/1.0.0 and 1.0.1) and their hashes remain historical; they do not identify the current release. Historical attempts below retain their original outcomes.

Date: 2026-09-14. Name: **speak-human / 说人话**. The objective is a natural, complete explanation that lets a reader
understand the outcome and make a supported decision without another rewrite.


## Initial attempt — superseded by the continuation

The single-file skill is implemented and linked into 10 existing local skill
roots. A fresh Claude Code session invoked the actual installed `Skill` tool,
received the current skill body, and returned a faithful short explanation.

**The initial strict preservation gate did not pass.** Ending the task at that
point was premature: the requested outcome was a useful skill, not just a file and
a completed test run. The user rejected that delivery. The continuation below
redesigns both the skill and its evaluation. Original failures remain recorded.
No account-wide writing rule was installed.

| Observation | Coverage | Outcome |
| --- | --- | --- |
| V1 controlled comparison | 7 families × 8 cases × 3 arms = 168 case answers | Some gains, some ties/regressions; confirmed recommendation errors remain. |
| V2 controlled comparison | 152 of 168 requested case answers | GLM returned no answers in two arms. Complete blind grading covers 5 families; Gemini judge JSON failed and GLM had no complete trio. No stable advantage. |
| Final candidate regression | 48 of 56 requested case answers | Six complete batches; GLM returned planning narration. All six strict JSON-format cases passed. Source fidelity still has confirmed counterexamples. |
| Installed skill invocation | One fresh Claude Code session | Current skill body loaded and a correct single-task rewrite returned. Other agent roots were linked, not individually runtime-verified. |

These are batch-generated case answers, not 368 independent sessions. V3 is a
single-arm regression pass. It is not legitimate to combine its answers with
older baselines and describe that as a fresh controlled comparison.

Raw 0–4 judge macro-means (provisional, **not** correctness or human-comprehension
scores): V1 ordinary / short-prompt / skill = 3.793 / 3.797 / 3.890 across seven
families. V2 = 3.867 / 3.796 / 3.814 across five completely graded families. The
family sets differ, so the two series should not be interpreted as a trend.
Neither meets the predeclared +0.3 advantage over both baselines, and source
counterexamples independently veto the preservation gate.

Read [V1 answers and grading](../../evals/speak-human/results/2026-09-14-v1.json),
[V2 answers and grading](../../evals/speak-human/results/2026-09-14-v2.json),
[final answers and audits](../../evals/speak-human/results/2026-09-14-final.json), and
[author adjudications](../../evals/speak-human/results/2026-09-14-adjudication.json).
The answers are retained in full; the adjudications distinguish confirmed issues,
missed issues, and disputed judge claims without replacing the original scores.

Examples of unresolved failures are an invented migration event in a task about
worker restarts, unsupported claims that SSE meets a latency promise, and a
recommendation whose stated capacity caveat invalidates it. These are more
important than whether a paragraph is shorter. Some batch contamination is
plausible because another case discusses migration; its mechanism is unproven.

## What the existing approaches contribute

| Source | Useful idea | Boundary for this skill |
| --- | --- | --- |
| [Matt Pocock's wait-what](https://raw.githubusercontent.com/mattpocock/skills/main/skills/productivity/wait-what/SKILL.md) | Re-explain a message with enough context and consistent terminology. | Its current short instruction explicitly uses ASD-STE100 English and project CONTEXT.md / CONTEXT-MAP.md. Our skill has no project-file dependency and follows the reader's language. |
| [Humanizer 3.0.0](https://github.com/blader/humanizer/releases/tag/v3.0.0) | Edit structural habits, preserve claims, reread the result; treat weaker stylistic tells contextually. | Removing AI-writing patterns alone does not specify what a task result or recommendation must retain. No AI detector or invented personal voice. |
| [no-ai-slop](https://github.com/petergyang/no-ai-slop/blob/main/SKILL.md) | Minimum effective edits, concrete verbs and details, preserving personal voice, structure that serves the piece. | Its draft-edit workflow normally adds editing commentary; the new skill returns the requested answer and works with existing conversation context. |
| [Caveman](https://raw.githubusercontent.com/JuliusBrussee/caveman/main/skills/caveman/SKILL.md) | Preserve exact technical terms, quantities and negations; abandon compression when it creates ambiguity. | Current full/ultra modes also permit fragments and cut hedging. We preserve real uncertainty and complete grammatical connections, with no compression quota or forced persistent mode. |
| [Google developer style: jargon](https://developers.google.com/style/jargon) | Keep audience-appropriate specialist terms and explain unfamiliar concepts in context. | This supports a judgment about the reader, not a Chinese/English percentage. The proposed Chinese sentence-frame rule is our design inference, not a rule claimed from Google. |
| [CDC Clear Communication Index](https://www.cdc.gov/ccindex/tool/how-to-use.html) and [scope](https://www.cdc.gov/ccindex/tool/faq.html) | Identify audience, objective and main message; state known/unknown information; independently review comprehension. | The Index is a public-health communication tool. We borrow questions, not its 100-point score or any claim of validated software-agent assessment. |

The release page identifies Humanizer v3.0.0 as the latest release when checked.
The installed SKILL.md also declares 3.0.0. no-ai-slop was read in full from the
installed local file; the search index returned the upstream content, but direct
GitHub/raw opens returned 404. Its current upstream availability is unconfirmed.
All instructions in the new skill are independently written; these sources are
influences, not runtime dependencies or copied mandatory rule lists.

## Design decisions

Preserve meaning first, organize the explanation second, remove reading friction
last. The core invariant is whether removing a fact, scope restriction, numerical
basis, uncertainty, or connection could change what the user understands or does.
A faithful rewrite separately preserves every substantive source claim. A summary
can exclude genuinely irrelevant detail, but must not hide decisive caveats in a
link or appendix. A short answer may need to become longer to restore a missing
explanation.

The skill operates on communication during or after a task. It does not reduce
investigation, implement code, grant new permissions, enforce a report template,
create a context document, or globally overwrite agent rules. Exact user output
formats and requested depth take priority. A single SKILL.md is portable; there
is no runtime script, model-specific adapter, or dependent skill to load.

Natural technical Chinese uses Chinese sentence structure with useful terms such
as HTTP and API intact. Ordinary actions become natural verbs; exact symbols stay
when the reader needs them. Neither English-fragment chains nor compulsory Chinese
translations improve comprehension. The relevant question is what the reader must
mentally reconstruct, not how many characters belong to each language.

## Evidence protocol

See [evaluation protocol](../../evals/speak-human/README.md). The complete candidate,
input cases and protocol were frozen before generation. Eight authored synthetic
cases, three arms, seven attempted local model runtimes. Baselines are ordinary
answers and a one-sentence instruction to be concise while retaining needed facts.
The expected invariants are excluded from generation prompts. This is an authored
regression suite, not independent held-out data.

The proposed advantage must clear both semantic preservation and comparative
quality gates. No statistical significance, universal cross-model reliability,
actual human reading-time improvement, or information-theoretic losslessness is
claimed. The same Claude judge used across models may favor its own writing;
anonymous labels mitigate knowledge of condition, not taste bias.

## Iteration record

Three candidate snapshots are retained under the local runs. V1 established the
information-preservation and natural-language guidance. V2 made the deletion check
symmetric, clarified when every claim must be retained, and required derived
quantities and recommendations to satisfy all constraints. V3 additionally asks
whether a recommendation survives its own caveats; an infeasible recommendation
must be withdrawn or narrowed. All three snapshots use the same package version
while developing the first release; their SHA-256 hashes distinguish the bytes.

V1 and V2 reran all three arms. V3 is a final single-arm regression pass, not a new
controlled estimate of improvement. The source author saw previous failures before
revising the skill. The same fixtures were reused; they are not held-out tests.
The detailed judge wording was completed after the first generator calls started;
the gates and cases were frozen first. This is a development evaluation, not a
fully preregistered study.

The author found errors the anonymous judge missed: V1 Claude recommended switching
to C beyond 1500 tasks despite C's hard 1500-task limit, and Kimi implied A was
unusable above 1500 although A remains within budget up to 1600. V2 Claude still
recommended an option contradicted by its own caveat. Merely repeating every
constraint is not semantic preservation. These failures veto a strong reliability
claim even where a raw judge score is near 4/4.

The judge also overreached: it marked GPT's JSON answer as losing the smoke-test
result even though the result appears in `status`; the user did not dictate which
field must contain it. Another flag treated omission of the inferable 60/client/min
intermediate calculation as material even though 30,000 requests at 500 clients
was preserved. These are retained as judge disagreements, not silently rewritten
into positive scores.

## Runtime boundaries

| Family | Tested runtime and model identity |
| --- | --- |
| Claude | Claude Code 2.1.270; output usage identifies `claude-opus-5`; auxiliary title generation also reports Haiku. |
| GPT | Codex CLI 0.154.0; explicit requested model `gpt-6-astra`, accepted; the captured completion does not independently echo a served model ID. |
| Grok | Grok CLI; requested `grok-4.6`, usage identifies `grok-4.6-build`. |
| Kimi | Kimi Code 0.42.0; live configuration selects `kimi-code/k3`; the captured answer stream does not independently echo the served model ID. |
| GLM | Claude Code through the existing CCS profile; usage identifies `glm-5.2[1m]`. |
| Gemini | OpenCode with the existing API credential and requested `google/gemini-3.1-pro-preview`. |
| DeepSeek | OpenCode with the existing API credential and requested `deepseek/deepseek-v4-pro`. |

Gemini CLI 0.47.0 returned `IneligibleTierError` / `UNSUPPORTED_CLIENT`. CCS's
DeepSeek profile returned HTTP 401. The alternatives kept the requested model
families and model names; no login or global credential settings were changed.
OpenCode's Google adapter needed the existing Gemini credential passed under its
expected variable name for that child process. Credentials are absent from tracked
results. OpenCode logs include provider token/cost estimates; they are not invoices.

Kimi rejects `--prompt` with `--plan`; all three arms were rerun without that
incompatible flag and without enabling automatic approvals. All generation tasks
instructed the agent to use only synthetic source material and make no tool calls.
Grok's successful JSON uses `text`, which was reparsed without another model call.
Some responses had malformed *batch transport*: GLM prefaced JSON with planning
text; DeepSeek emitted a trailing comma and surplus closing brace. Where the eight
answer strings were unambiguous, only the wrapper was repaired and the original
retained. These repairs never fix a user-facing answer's own JSON or prose.
GLM later returned planning narration without the requested answers; those are
incomplete executions, not scored writing samples.

Some judge responses likewise had malformed structure or an impossible pairwise
winner. Unambiguous structural repairs are documented and retain original text;
a winner outside its stated pair is left unscored. Scores alone are insufficient
acceptance evidence.

## Using the skill

Start a new agent session after installation. In Codex, invoke `$speak-human`;
in agents exposing installed skills as slash commands, use `/speak-human`. For
example: `用 speak-human 讲清楚刚才的结论、依据和建议。` For an ongoing task, state
that scope: `这项任务后续的说明都使用 speak-human。`

A bare invocation repairs the current explanation. It does not make a permanent
account-wide style setting. The installation links only this skill into existing
agent skill roots; it does not alter AGENTS.md, credentials, or other skills.
The skill is a single portable Markdown file. The evaluator and research report
are outside its runtime folder.



## Continuation after user feedback

The initial evaluation was poorly matched to the task. It bundled unrelated cases
into one response, imposed JSON wrapping on prose, used near-ceiling absolute scores,
and mixed core reasoning mistakes with communication quality. It did not adequately
represent long, confusing agent replies. Passing structural checks was not delivery.

A read-only Claude Code review identified the need for a concrete repair procedure,
especially recommendations invalidated by their own caveats, factual status
distinctions, and turning noun chains into causal sentences. Its proposed fixed
length/first-sentence rules were not adopted literally: complete handovers and
teaching can need more explanation. A four-case independent author request failed
(plan narration, then timeout); four isolated GPT calls produced the new held-out
material, without access to the candidate. These are synthetic, not harvested user
conversations or a representative sample of all agent work.

Additional primary-source guidance:

- [NIH plain-language guide](https://www.nih.gov/sites/default/files/2025-02/nih-plain-language-getting-started-brushing-up.pdf): organize around the audience's questions, explain necessary technical terms in context, and test whether readers understood the main ideas. Readability formulas can penalize useful definitions. We therefore assess complete understanding rather than a compression ratio.
- [FActScore](https://arxiv.org/abs/2305.14251): assess supported atomic claims instead of treating one fluent paragraph as uniformly factual. Our source-coverage checks additionally look for omitted material meanings; they are not an implementation of the published FActScore metric.
- [The Comparative Trap](https://arxiv.org/abs/2406.12319): pairwise model judgments can favor superficial attributes. We retain source audits separately, calibrate on controlled faults, blind labels, and swap order. This reduces some evaluation mistakes without making a model judge equivalent to a human reader.

The candidate now rebuilds from the reader's question, supporting facts, and
meaning-changing conditions; it includes a complete-answer example and a two-way
source check. v4, v5, and v6 development outputs are retained. v6's longer Chinese
instruction did not help and was withdrawn. v5 reduced incidental material more
effectively in author inspection; its blind development preference was mixed
(2 wins, 4 losses), so selection alone is not evidence of a successful release.

See [pre-registered continuation protocol](../../evals/speak-human/PROTOCOL-v2.md)
and the independent case files. Final continuation results are recorded separately
from the old batch evaluations.

## Final continuation and user preference

The user selected the visible structure of B and explicitly requested more natural complete sentences and theoretical support. This superseded the earlier preference for connected paragraphs as the default. v8 added the evidence–mechanism–implication chain and a structured cache example. v9 distinguished full handovers from decision summaries. v10 attempted to freeze critical clauses and prevent repeated sections; v11 places verbatim operative clauses before explanatory prose. Repeated Gemini handover omissions and the unchanged-notification failure are not resolved by merely having these rules in the file.

Fresh-session global contamination was verified: Grok tried to load the installed skill in a baseline, and OpenCode pure mode retained global instructions. Empty child XDG configuration, disabled project/external/Claude discovery, a text-only custom agent, and Claude safe-mode established the revised comparison conditions. Configuration capabilities were checked in the local executable and [official OpenCode config documentation](https://opencode.ai/docs/config/) and [agent documentation](https://opencode.ai/docs/agents/). Grok remained unverified as a clean route.

Final fresh transfer: three model pairs, all six counterbalanced style judgments preferred the skill. This supports the scoped structural/causal writing improvement, not universal superiority or perfect fidelity. Full source fidelity still has concrete counterexamples documented in the current Chinese report. Final four-provider bare JSON passed; final Claude Skill invocation returned the exact installed body. Current reports and complete exported evidence supersede the initial final-delivery language above.
