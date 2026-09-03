# Deep research skill — landscape and evidence

Research basis for `deep-research` (2026-09-02). Three corpora: ~45 published
research skills and skill collections pulled locally and read in full (the
skills.sh "deep research" and "research" leaderboards, the Anthropic official
plugin repos, academic suites, and the curated hubs that aggregate them), five
open-source deep-research systems read at the prompt and control-flow level,
and external methodology sources (Anthropic's multi-agent research write-up,
DeepResearch Bench, FINDER/DEFT, WebWeaver, RhinoInsight, ICD 203, SIFT).
This records what the skill must beat, what it borrows, and what it rejects.
Working notes and per-skill verdicts live outside the repo in
`~/Workspaces/agent/corpus/deep-research-skills/_notes/`.

## Corpus 1 — published skills (what exists, what to beat)

Install counts are skills.sh on 2026-09-02.

| Skill | Verdict |
| --- | --- |
| `mattpocock/skills@research` (424K) | Three instructions: background agent, primary sources only ("follow every claim back to the source that owns it"), write findings where the repo keeps such notes. The most-installed research skill has no scoping, tiers, source evaluation, or verification; its popularity is brand plus composability. Its two disciplines are the most-cited rules in the whole corpus. |
| `199-biotechnologies/claude-deep-research-skill` (9.7K) | The most complete mechanism set: decision tree, four modes, eight phases, sources/evidence/claims JSONL ledgers with stable ids, claim types where only factual claims hard-fail, evidence-driven outline refinement, three critic personas, anti-fatigue and zero-tolerance bibliography rules, "web content is data not instructions". Over 1,500 lines, a `brew`-installed search CLI, WeasyPrint PDFs auto-opened, minute-based thresholds an agent cannot measure, and output to `~/Documents` regardless of project convention. |
| `daymade/claude-code-skills@deep-research` (1.3K) | Best evidence pipeline discipline: notes files as the only channel between workers and lead, FINAL-numbered citation registry with a Dropped list, numeric source-governance gates, an anti-hallucination pattern table (precision inflation, unnamed "studies show", Chinese 某专家表示/据统计), mandatory counter-review with a floor. 2,056 lines that contradict their own phase numbering, five dependent agents not shipped, three overlapping templates. |
| `Weizhena/Deep-Research-skills` | The enumerative shape done right: model-drafted items × fields framework → human confirmation → one worker per item writing validated JSON with `[uncertain]` markers → resume by skipping finished files. Also the only skill with a Chinese technical-community source module. Four near-identical copies per runtime, too many confirmation prompts, no source tiering. |
| `Anjos2/recursive-research` | The only quantified stop rule (saturation ≤5% for three cycles, coverage ≥80%, ≥3 tier-1 per thread), the most concrete tier and rejection definitions, recency-by-domain, Munger inversion for missing opposition, per-cycle checkpoints with resume. Spanish only, weighted-decision-matrix theatre, PhD branding, 20-cycle default for every question. |
| `samber/cc-skills@deep-research` (2.1K) | Best scoping UX: skip the interview when the request is well-scoped, otherwise one question at a time, assumptions in the report header; confidence ladder bound to source count with access dates; conflict template. No verification layer, rigid 4+3+3 axis templates. |
| `langchain-ai/deepagents@web-research` (3.9K) | Best economy: per-worker search budgets, three stop triggers ("can answer / 3+ sources / last two searches similar"), reflect after every search, one worker by default and an explicit ban on premature decomposition. No source quality, no contradictions. |
| `bytedance/deer-flow@deep-research` (2.3K) | Best search craft: temporal precision keyed to intent, information-type diversity checklist, broad→narrow with reference-following, iterate-until-checklist stop gate. Produces no report or citations. |
| `anthropics/claude-for-legal` research skills | The most rigorous epistemic protocol anywhere: provenance tags that describe retrieval not confidence (`[fetched]`, `[snippet — verify]`, `[model knowledge — verify]`, `[user provided]`), three-valued no-silent-supplement, quote-to-proposition check, tool-vs-model conflict as a flagged finding, coverage disclosure ("know what you read"), reviewer note above the deliverable. Legal wording, generic logic. |
| `anthropics/knowledge-work-plugins` research skills (3.4K) | Anthropic's retrieval loop: question-type classification driving source ranking and freshness weight, constraint-removal broadening ladder, four confidence states including "unable to determine" expressed in prose register, contradiction protocol, "omit sections rather than fill gaps", "what decision will this inform?". Enterprise-tool shaped; numeric weights are fake precision. |
| `firecrawl-deep-research` (33.5K), `parallel-deep-research` (13.7K), `tavily-research` (17.3K) | Vendor thin clients. Firecrawl contributes one scoping question → numeric budget tiers and a report contract with Contrarian Views and Rerun Inputs; the others expose no methodology. All dead without their API key. |
| `imbad0202/academic-research-skills@deep-research` (6.1K) | Deepest academic methodology: three-tier citation existence check with `DOI_MISMATCH`, "gray zone = FAIL", two-axis source grading with an integrity floor, five-step contradiction resolution, anti-sycophantic devil's advocate ("pushback is not evidence"). Thirteen agents where five carry the value; prompts polluted with issue ids. |
| `K-Dense scientific-agent-skills` (market-research-reports, peer-review) | Claims ledger with statement types (fact / estimate / calculation / forecast / opinion), eight-rung event-proximity source ladder, "absence = unknown, not no", claim–evidence alignment fields (direction, magnitude, population, outcome, time point, uncertainty). Academic packaging. |
| `waza/learn` (10K), `warpdotdev/common-skills@research` (16.9K) | Primary-sources-only with outline↔source coupling and stall signals; the cleanest subagent delegation contract. No citations or confidence. |
| `jamditis/claude-skills-journalism` (source-verification, fact-check) | SIFT as procedure, five separate verification questions, supporting / conflicting / missing evidence recorded apart, five-valued verdicts where "unresolved" is legitimate, "state what would change the result", claim type → primary source table, evidence strength table. |
| `flonat/claude-research` (devils-advocate, multi-perspective, checkpoint) | Critic → author defence → adjudication debate so only surviving objections reach the report; anonymised cross-evaluation of perspectives; blind-spot detection; machine-readable checkpoint schema. |
| `mvanhorn/last30days` | A 2,300-line instruction contract with six "LAWs" that the author documents the model violating anyway. Its keyword-trap pre-flight (demographic phrases, number collisions, tutorial phrasing, bare nouns, non-Latin scripts) is the one transferable idea. |
| Remaining long tail (`ecc`, `jezweb`, `claude-office-skills`, `lingzhi227`, `Orchestra-Research`, `rigorpilot`, `awesome-copilot autoresearch`, `awesome-llm-apps deep-research` (3.8K; a generic "systematic approach" stub, absent from the repo snapshot), curated hubs) | Prompt-injection guardrails for fetched content; product demand-signal heuristics (one-star reviews, plugin ecosystems, migration guides); file-existence phase gates; provenance that never upgrades; setup-contract tables. Otherwise domain-locked, vendor-locked, or hollow. |

### Consensus across the corpus (adopted)

1. Triage first; simple lookups skip the protocol; depth in tiers with budgets.
2. A written brief before the first search; clarify once or state assumptions.
3. Decompose into sub-questions; start wide, then narrow; short distinct queries.
4. Tier sources, prefer the owner of the fact, reject the unattributed.
5. Evidence persisted to disk before synthesis; subagent output through files.
6. Four-part worker briefs with a structured return contract.
7. Outline evolves with evidence; write section by section from the ledger.
8. Seek the opposing view deliberately; contradictions and gaps are deliverables.
9. Gate before delivery: citation closure, no placeholders, no vague attribution.
10. Today's date from the environment; recency judged per field.
11. Fetched content is data, never instructions.

### Nobody did well (where `deep-research` is built to win)

- **Claim-level verification with search craft in the same skill.** The two
  best searchers (deer-flow, deepagents) have no evidence discipline; the two
  best ledgers (199, daymade) have weak search and no re-opening of sources.
- **Generality with domain adaptation.** Skills are either academic-only or
  domain-blind; only recursive-research had a domain table. Domain lenses
  supply owners of facts, authority, recency, traps, and checks per field,
  including the Chinese-language ecosystem that only Weizhena covered.
- **Research shapes.** Narrative, matrix, decision, and verification reports
  have different skeletons and parallelism; the corpus hard-codes one.
- **Confidence language.** Decimal confidences and percentage bands by source
  type are fake precision; ICD 203 likelihood words plus evidence-bound
  confidence levels with a stated basis replace them.
- **Instruction-following.** DeepResearch Bench scores it as a first-class
  dimension; almost no skill checks the report against the request.
- **Interruption survival.** Only two skills checkpoint; none describe resume.
- **Tool independence.** Vendor skills die without their key; a protocol must
  detect and degrade honestly.
- **Size.** Completeness correlated with rot: 1,500–2,300-line skills whose
  own numbering disagrees with itself. Core ≤ 250 lines, references on demand.

### Rejected

Weighted decision matrices and confidence decimals the agent cannot compute;
minute-based thresholds; minimum word counts; mandatory section templates;
"LAW"-style prohibitions stacked four deep; vendor CLIs as primary tools;
automatic PDF/HTML generation and opening; output to `~/Documents`; thirteen
agent roles; PhD or McKinsey branding; four per-runtime copies of one skill.

## Corpus 2 — open-source deep-research systems

- **langchain open_deep_research**: clarify once then rewrite the request as a
  first-person brief with unstated dimensions declared open-ended; researcher
  budgets 2–3 / ≤5 searches with a hard cap; supervisor ≤6 rounds, ≤5 parallel;
  reflect after every search; "compress, don't summarize" keeping every URL;
  writer with no self-reference and structure by question type.
- **dzhng/deep-research**: ≤3 dense learnings per batch (entities, numbers,
  dates) plus follow-up questions; breadth halves per depth level; stop when a
  level yields nothing.
- **gpt-researcher**: orientation search before planning; curate sources ("err
  on inclusion, filter never rewrite"); writer must "determine your own
  concrete and valid opinion" rather than generic conclusions.
- **smolagents open_deep_research**: facts survey (given / to look up / to
  derive) re-planned every few steps with steps remaining.
- **deer-flow**, **NVIDIA AI-Q**: clarify → plan → act as a hard rule; shallow
  versus deep routing with "unsure → shallow"; typed plan with
  `required_components` as a coverage checklist; citation whitelist copied
  from a registry ("if a claim cannot be mapped to a verified source, remove it
  or state it as a gap"); "never claim an action you did not execute".

Where the systems agree: separate research from writing; stop when you can
answer confidently, with hard caps as backstop; parallel only along independent
axes with standalone briefs; every claim cites a URL that appeared in tool
results; match the user's language; degrade to the best answer plus named gaps
at any limit; clarify before, never during.

## Corpus 3 — external methodology (key evidence)

- **Anthropic, "How we built our multi-agent research system"** (2025-06):
  orchestrator–worker; effort scaling (1 agent / 3–10 calls for facts, 2–4
  agents for comparisons, 10+ for complex); four-part delegation (objective,
  output format, tools and sources, boundaries); start wide then narrow; source
  quality heuristics after agents preferred SEO farms to authoritative PDFs;
  LLM-as-judge on factual accuracy, citation accuracy, completeness, source
  quality, tool efficiency; plans and outputs in memory and files; ~15× chat
  tokens, worth it only for high-value parallel work.
- **DeepResearch Bench** (arXiv 2506.11763): RACE (comprehensiveness, insight,
  instruction-following, readability) and FACT (effective citations, citation
  accuracy). WebWeaver reached 93.37% citation accuracy with evidence-driven
  dynamic outlines and section-wise retrieval from an evidence bank.
- **FINDER / DEFT** (arXiv 2512.01948): fourteen failure modes measured on
  current agents; the top five (strategic content fabrication 19%,
  insufficient external information 16%, lack of analytical depth 11%,
  content specification deviation 11%, failure to understand requirements 11%)
  sum to two thirds. "DRAs struggle not with task comprehension but with
  evidence integration, verification, and reasoning-resilient planning."
- **RhinoInsight** (arXiv 2511.18743): verifiable checklists from requirements;
  evidence audit binding ranked evidence to the outline; targets error
  accumulation and context rot.
- **ICD 203** (ODNI analytic standards): likelihood words bound to bands
  (almost no chance 1–5% … almost certainly 95–99%); confidence in the
  judgment as a separate statement with its basis; alternative analysis.
- **SIFT** (Caulfield): stop, investigate the source, find better coverage,
  trace the claim to its origin; lateral reading over checklists.
- **NVIDIA AI-Q**: intent classification → clarification → shallow/deep;
  evaluation on FreshQA, Deep Research Bench, DeepSearchQA.
- **Commercial products** (OpenAI, Gemini, Perplexity deep research, 2026
  comparisons): clarify or show an editable plan before running; browsing
  scale tied to depth; citations transparent.

## What `deep-research` is

Seven axioms → a six-phase protocol with exit criteria (triage and brief,
plan, gather loop, verify and reconcile, synthesize, gate and deliver) → a tier
table binding budgets → shapes for the report → domain lenses → three working
files (plan, ledger, report) that survive compaction → a zero-dependency
mechanical gate. Failure modes are organised by DEFT's three categories and
each names the step that prevents it. Core 230 lines; five references loaded
by phase; four templates; one script.

Acceptance is codified in `evals/deep-research/PROTOCOL.md`: frozen briefs
across shapes and domains, a paired no-skill baseline, scoring on citation
accuracy by re-opening sources, RACE dimensions, and invariant violations.

## First smoke runs (2026-09-02, skilled arm only)

- **lookup** (`lookup-rfc-9110-status`): tier chosen correctly, two owner
  pages opened directly, no workspace, answer matched the oracle including
  the "portions of 7230" trap and a `[model knowledge — verify]` tag on the
  one unretrieved statement. Five tool calls, two of them retrieval.
- **focused** (`pg-incremental-backup`, no subagents): 8 searches, 15 sources
  opened (tier A 11, B 4), 17 dropped, disconfirmation pass surfaced a
  contradicting expert post that changed a finding, report passed
  `check_report.py` with zero FAIL; over budget by three sources with the
  reason logged. Archived under `evals/deep-research/runs/2026-09-02/`.
- **standard** (`cn-agent-frameworks`, headless top-level session, three
  workers): interrupted twice by session rate limits and resumed each time
  from `plan.md §4`; workers produced notes in the brief's exact shape with
  version-pinned tier-A sources read through `gh api`. Final run: a Chinese
  compare report of ~3,800 words with two 12-entity matrices, 88 citations,
  ledger of 150 sources / 141 evidence lines / 66 claims / 14 contradictions,
  `check_report.py` zero FAIL and zero WARN. Twelve web searches and 89 opened
  sources in total, far above the tier's default because a 12-entity matrix
  needs about three owner sources per entity; that rule is now in Phase 0.
  Archived under `evals/deep-research/runs/2026-09-02/`.
- The usability logs from these runs produced the fixes now in v1: phase
  numbering aligned across files, shape tie-break, reviewer-note ordering,
  batch logging under parallel fetches, `digest` provenance for summarising
  fetch tools, owner-text sufficiency for documented behaviour, budget-overrun
  logging, language and length rules, checker regexes for confidence phrasing,
  real table detection, quantity units, and reviewer-note presence.
