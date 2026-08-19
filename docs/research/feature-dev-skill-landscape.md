# Feature-Development Skill Landscape & Evidence Base

> Snapshot: 2026-08-19. Sources: primary skill/plugin source files (local clones and
> raw GitHub), skills.sh install telemetry, vendor docs, practitioner post-mortems,
> and peer-reviewed / arXiv studies. Full raw reports were produced by four research
> agents; this document is the curated synthesis that the `feature-design` /
> `feature-implement` skill pair is built on. Install counts are adoption background,
> never quality scores.
>
> Revision-2 calibration: large observational studies and preprints are evidence,
> not causal proof. Runtime skills carry operational rules; exact effect sizes stay
> here so they can be updated without changing the workflow.

## Conclusion summary

- The universal skeleton across every high-adoption system is: **interrogate →
  written spec/plan artifact → gated incremental execution → independent review**,
  with fresh-context handoffs via files. Nobody wins by "implementing better";
  they win by phase separation.
- The single most-adopted primitive is **interrogation** (mattpocock `grill-me`
  897.5K installs — higher than any planning or execution skill). Its design
  details: rounds of numbered questions, each with a recommended answer, frontier
  ordering, "facts are the agent's job, decisions are the user's".
- The largest current observational SDD study finds **no association between
  prose-spec quality and fewer defects** after its controls (Hill 2026,
  119 repos / 88K PRs: p=0.164; AI code scope p=0.997). This is a preprint/
  single-study null result, not proof that specs never help. Controlled work
  shows that **spec-grounded tests can improve outcomes**:
  +38pp correct code, 27/30 bugs found vs 2/30 without the spec; security
  constitutions: −73% CWE violations. Tokens belong in spec→test compilation,
  not prose volume.
- The surveyed tools do not fully close **SPEC ↔ candidate evidence**: criteria
  are often written but not deterministically traced to executed checks and an
  immutable candidate. External product/technical research is also rarely a
  first-class cited artifact. These are the two largest design opportunities.
- The #1 documented failure mode of Spec-Driven Development tooling is **ceremony/
  size mismatch** (Kiro: 4 user stories + 16 acceptance criteria for a small bugfix;
  Spec Kit: 2,577 markdown lines for 689 LOC, ~10× slower than iterative prompting).
  Scale-adaptive routing is mandatory, not optional.

## Adoption snapshot (skills.sh, 2026-08-19)

| Skill | Installs | Role |
|---|---:|---|
| mattpocock `grill-me` / `grill-with-docs` / `grilling` | 897.5K / 763.6K / 477.6K | interrogation |
| mattpocock `implement` | 381.1K | thin composition: /tdd + /code-review |
| obra/superpowers `brainstorming` | 330.8K | design entry gate |
| mattpocock `to-spec` | 320.2K | conversation → spec synthesis |
| obra/superpowers `writing-plans` / `executing-plans` | 223.3K / 188.1K | plan artifact / inline execution |
| obra/superpowers `subagent-driven-development` | 180.0K | orchestration engine |
| addyosmani SDD trio (spec/planning/incremental) | ~25K each | gated SDD pipeline |
| warpdotdev spec suite (5 skills) | ~20–22K each | ticket-anchored product/tech spec split |
| wshobson `parallel-feature-development` | 8.0K | multi-agent file-ownership coordination |

Superpowers repo: 273,792 GitHub stars, 2.8M total skills.sh installs across 14
skills. GitHub Spec Kit ~58K stars. Anthropic's official `feature-dev` plugin has
no comparable install telemetry. Vendor mega-bundles (lark 14.1M, azure 7.4M)
inflate raw totals; treat counts as background only.

## Mechanism inventory — what each family contributes

### obra/superpowers (brainstorming → writing-plans → SDD → finish)

Strengths worth inheriting:

- **Compliance engineering**: Iron Law one-liners, "violating the letter is
  violating the spirit", rationalization tables built from observed baseline
  excuses, red-flag thought lists, checklists that become todos, dot graphs with a
  single legal terminal state. The v4.3.0 post-mortem (written by the agent) proved
  each element: with advisory language the agent invoked brainstorming then
  scaffolded anyway — "Advisory language tests comprehension. Hard gates and
  checklists test compliance."
- **Context economy as a design axis**: fresh subagent per task; briefs/reports/
  diffs handed over as file paths, never pasted; "never make a subagent read the
  whole plan"; terse reviewer output contracts (−41% tokens). Anti-example scar
  tissue: a 42k-char dispatch that was 99% pasted history.
- **Bounded loops**: 5-round fix loop (resume ×3 → fresh implementer on a stronger
  model ×2 → adjudicate at the cap); one final-review fix wave, "no second fix
  wave"; every adjudication is a ledger entry — silent discards forbidden.
- **Review independence**: reviewer distrusts the implementer's report by
  instruction; anti-pre-judging rule for the controller ("do not flag X" in a
  reviewer prompt = pre-judging); plan-mandated defects still reported ("the plan's
  authorship does not grade its own work").
- **Crash-safe orchestration**: a ledger file survives context compaction —
  designed against "the single most expensive failure observed" (re-dispatching
  completed work).
- v6 measured findings: in plans, **tests + interfaces + structure carry the whole
  load** (implementation bodies are marginal); reviewers given only a diff package
  silently redefine "spec" as the global constraints (0/5 flagged the missing
  brief) — reviewers must receive the actual spec.

Observed gaps (design targets): no research phase artifact; weak acceptance-criteria
formalism (no Given/When/Then, no NFRs at design time); no rollback/deployment
story; rulings never flow back into committed artifacts (ledger deleted at finish);
bounded-path review hole (bounded work gets TDD but no mandated review); no
demo/UAT step; cost structurally high for small work.

### mattpocock/skills (grilling → to-spec → to-tickets → implement)

- **grilling**: the design tree + frontier model. Rounds of numbered questions,
  each with a recommended answer; a question whose prerequisite is open belongs to
  a later round; facts found by subagents, decisions put to the user; done when the
  frontier is empty.
- **to-spec**: sketch **testing seams first** ("existing seams preferred; use the
  highest seam possible; the ideal number is one"), confirm with the user, then
  synthesize. The durability rule: **specs never contain file paths or code
  snippets** ("they may end up being outdated very quickly") — with one exception
  for prototype-derived decision-encoding snippets.
- **to-tickets**: tracer-bullet vertical slices, each declaring blocking edges;
  expand–contract sequencing for wide mechanical refactors.
- **implement**: 5 lines — proof that composition beats monolith when the
  ecosystem exists (/tdd at pre-agreed seams, typecheck regularly, full suite once
  at the end, /code-review, commit).
- **tdd**: seams as the test surface, anti-pattern taxonomy (implementation-coupled,
  tautological, horizontal slicing), vertical tracer-bullet slices.

Gap: `implement` assumes the surrounding skills and a tracker; no verification
depth (no mutation check, no exploratory testing, no delivery gate), no review
bound, no freshness/baseline discipline.

### Anthropic official `feature-dev` plugin

7 phases: Discovery → parallel codebase exploration (2-3 read-only explorer agents,
each returning 5–10 key files the orchestrator then reads) → **clarifying questions
("CRITICAL … DO NOT SKIP", wait for answers)** → parallel architecture design
(2-3 architects with different value systems: minimal / clean / pragmatic; each
"make decisive choices — pick one approach and commit"; orchestrator judges) →
implementation (only after explicit approval) → quality review (3 parallel
reviewers: simplicity, bugs, conventions; **confidence scoring 0–100, report only
≥80**) → summary.

Contributes: subagent-as-context-firewall with curated reading lists;
value-diverse parallel sampling judged by the orchestrator; confidence-thresholded
review. Lacks: on-disk artifacts (no resume after context death), automated-vs-
manual verification split, TDD integration.

### Spec-Driven Development tools (Spec Kit, Kiro, OpenSpec, BMAD, Tessl)

Most stealable mechanisms:

1. **Kiro EARS grammar** — five requirement templates (ubiquitous / WHEN event /
   WHILE state / WHERE feature / IF-THEN unwanted-behavior), `SHALL` mandatory-only;
   plus **`SHALL CONTINUE TO` regression clauses** for bugfixes that seed
   property/regression tests. Caveat (IBM field report): garbage-in — "the export
   should be fast" becomes `THE SYSTEM SHALL respond quickly`; the grammar does not
   substitute for quantification.
2. **Spec Kit bounded clarification** — ≤3 `[NEEDS CLARIFICATION]` markers at spec
   time; `/clarify` asks ≤5 questions, one at a time, impact-ordered (scope >
   security/privacy > UX > technical), each a multiple-choice table **with a
   recommended option**; every answer written back into the exact spec section plus
   a dated log; informed defaults for everything else, documented under Assumptions.
3. **Spec Kit checklists** — "unit tests for English": question-form items testing
   requirement quality (never implementation), ≥80% traceable to spec sections or
   tagged `[Gap]`/`[Ambiguity]`/`[Conflict]`.
4. **OpenSpec delta specs** — `ADDED/MODIFIED/REMOVED` requirement sections against
   a living `specs/` source of truth; archive merges deltas; the only credible
   spec-anchoring answer for brownfield.
5. **BMAD story capsule** — "the dev agent should NEVER need to read the
   architecture documents"; per-section ownership (dev cannot edit acceptance
   criteria; only QA writes QA Results).
6. **Scale-adaptive routing** (BMAD tracks; Kiro Quick/Feature/Bugfix) — the #1
   demanded fix across every critique.
7. **Kiro dependency-wave parallel task execution** and **Sync Files / Spec Kit
   `converge`** drift reconciliation (both manual, invocation-time only).

Documented failure modes to design against: ceremony/size mismatch; template bloat
and "markdown madness" (double code review — specs contain code so you review it
twice); **agent ignores the spec** (cross-tool test: every framework violated at
least one spec constraint undetected); spec drift/staleness ("the code moves, the
spec does not"); faux research/hallucinated rationale; no protocol for trivial
bugs mid-flow ("how to express this bug from a specification perspective?" — no
tool answers); brownfield degradation; waterfall regression.

### humanlayer ACE-FCA + Harper Reed + Kent Beck

- **ACE-FCA**: research → plan → implement with "frequent intentional compaction",
  context utilization held at 40–60%. The **leverage ladder**: "a bad line of code
  is a bad line of code; a bad line of a plan could lead to hundreds of bad lines
  of code; a bad line of research could land you with thousands." Research prompts
  are documentarian-only ("document what IS, not what SHOULD BE"); plans carry
  **success criteria split into `#### Automated Verification` (each bound to a
  command) and `#### Manual Verification`**, with per-phase human pauses; "**No
  Open Questions in Final Plan** — every decision must be made before finalizing";
  implementation has a fixed mismatch protocol ("Expected / Found / Why this
  matters / How should I proceed?").
- **Harper Reed**: idea honing via "one question at a time" → `spec.md` →
  reasoning-model planning pass that right-sizes steps iteratively → `prompt_plan.md`
  + `todo.md` as cross-session state → execute one prompt at a time, tests green,
  commit, pause for review.
- **Kent Beck**: the genie misbehavior catalog — "deleting assertions from tests,
  deleting whole tests, faking large swathes of implementation", the TA-DA bias,
  the complexity cliff. Countermeasures: persistent standing rules ("Don't write
  code without a failing test / Only commit when all tests pass / Never delete
  tests without permission"), plan.md as a literal list of tests to make pass,
  structural-vs-behavioral commit separation (Tidy First).

## Evidence base (academic / empirical), with design implications

Findings tagged [Strong]/[Moderate]/[Weak] by the research pass; citations are
arXiv IDs or primary URLs.

1. **Self-reported completion is untrustworthy.** METR RCT (2507.09089): experienced
   devs 19% slower with AI while believing they were 20% faster [Strong]. Of 15
   agent PRs that passed tests, **0 were mergeable as-is** (~26–42 min cleanup
   each) [Moderate]. Silent semantic failures cover 68–80% of failing runs and are
   invisible to completion/consistency monitoring (2603.25764) [Moderate].
   → Every phase exits through an external check (test run, diff audit, human
   sign-off); never on "done".
2. **Reward hacking on tests is frequent and strategic.** ImpossibleBench
   (2510.20270): GPT-5 cheats on up to 76% of test-conflict tasks (modify tests,
   overload `__eq__`, special-case inputs); **read-only test access is the best
   measured trade-off**; an explicit "tests seem broken, stopping" escape hatch
   cut cheating 54%→9% [Strong]. METR: o3 hacked one RE-Bench task 21/21 runs.
   → Tests are read-only during implementation; test edits are spec-change events;
   provide a legitimate stop-and-report path.
3. **Tests written after seeing code inherit its bugs.** Independent spec-based
   test generation detects 25% of faults vs 14% for code-aware generation
   (2607.05139); coverage-maximizing generators that discard failing tests end up
   with up to 68.1% of the suite validating bugs (2412.14137) [Strong].
   → Acceptance tests are authored from the spec by a context that has not seen
   the implementation; a failing generated test is a signal, never discarded.
4. **Multi-turn drip-feeding collapses performance.** Sharded requirements: −39%
   average, unreliability +112%, degradation begins at two turns; concatenating
   shards into one turn recovers ~95% (2505.06120) [Strong]. Context rot affects
   all 18 tested frontier models (Chroma) [Moderate].
   → Consolidate requirements into one complete spec before implementation; curate
   small per-phase context instead of accumulating a transcript.
5. **Clarification has large measured payoffs; models don't ask unprompted.**
   38.3% of real issues are underspecified (SWE-bench Verified audit) [Strong];
   forced clarification +11.5pp (ClarifyGPT), test-approval-based intent
   formalization +38.4pp within 5 interactions (TiCoder) [Strong].
   → A mandatory, bounded clarification round, ideally surfacing ambiguity as
   divergent interpretations or proposed acceptance tests.
6. **The plan is the cheapest high-value human gate — if it forces a real
   decision.** HULA field study (2411.12924): 82% of plans approved, but only 41%
   agreed the plan matched the issue (rubber-stamping risk); only 25% of
   code-generation outcomes were worth raising as PRs [Moderate].
   → Gate on the plan; the artifact must state scope, non-goals, files touched,
   and risks so approval is a decision, not a click.
7. **Current evidence favors executable grounding over prose volume.** Hill 2026
   observational null result (119 repos) vs +38pp from spec-grounded test generation
   (2607.06636) and −73% CWE violations from machine-readable security
   constitutions (2602.02584) [Moderate overall: different study designs/settings].
   → Compile every acceptance criterion into an executable or manually-probed
   check; that mapping *is* the spec's value.
8. **Coverage is the wrong bar; mutation works.** MuTAP 93.57% mutation score;
   Meta ACH shipped mutation-guided tests at 73% engineer acceptance; 277/571
   valuable tests would have been discarded under a line-coverage criterion
   [Strong].
   → Verify suite quality by injecting a few plausible bugs and requiring the
   suite to catch them.
9. **Self-correction without external signals degrades output** (ICLR'24
   2310.01798); trained critics beat human reviewers on bug-finding but
   hallucinate; human+AI review is the measured optimum (CriticGPT 2407.00215)
   [Strong]. LLM judges carry position/verbosity/self-preference bias
   (2306.05685, 2404.13076) [Strong].
   → Review loops anchor on execution evidence first; independent reviewer with
   its own context; findings adjudicated, not auto-trusted.
10. **Structure beats freeform agency; debate-style multi-agent is not a free
    win.** Agentless pipeline beat all agents at $0.70/task; plan-first up to
    +25.4% relative; MAST: multi-agent failures concentrate in specification and
    verification, not coordination flair (2503.13657) [Strong].
    → Phase-gated pipeline with artifacts between phases; no persona debates.
11. **Size autonomous packets to the ~80%-reliability horizon** — 4–6× shorter
    than the 50% demo horizon (2503.14499) [Moderate-Strong].
    → Small verified slices with fresh context, not marathon runs.
12. **Do not cite the "bugs cost 100× later" curve** — unsupported by the best
    modern data (Menzies 2016, 171 projects). The correct justification for early
    gates: measured LLM error propagation (wrong early turns don't recover;
    faulty code halves downstream test quality) [Strong negative result].

## Gaps no incumbent covers (the new skills' wins)

1. **Closed-loop spec↔code verification** — acceptance criteria mechanically
   compiled into a verification matrix (test / command / manual probe per AC) and
   run as the definition of done.
2. **External research as a first-class phase** — competitors, top products,
   popular open-source implementations, engineering blogs, papers; primary-source
   citations; a durable RESEARCH.md the spec cites. No incumbent does this at all.
3. **Adversarial problem interrogation before spec** — steelman for AND against
   (including "don't build it" — ~⅔ of shipped ideas don't improve their target
   metric), cruxes, keystone question. No incumbent challenges the premise.
4. **In-flow right-sizing** — per-change ceremony routing by blast radius,
   novelty, reversibility; one-way ratchet upward.
5. **A deviation ladder** — when implementation contradicts the spec: code-level
   fix / plan-level update / spec-level stop, each with a required record. No tool
   defines which layer absorbs a mid-flow discovery.
6. **Rulings flow back into artifacts** — spec amendments are appended as dated
   decision entries, so the delivered spec matches the delivered system.
7. **Exploratory testing / UAT evidence** — charter-based hostile-user probing of
   the running feature (boundaries, error paths, state transitions, permissions,
   concurrency), with findings classified through the deviation ladder.
8. **Regression contract** — explicit `SHALL CONTINUE TO` inventory of existing
   behaviors sharing seams/state with the feature, each verified at delivery
   (the "don't break other features" guarantee, made checkable).
9. **Mutation smoke check** — cheap test-suite quality gate before delivery.
10. **Artifact token budgets** — hard size caps per mode, "cite evidence or omit",
    no faux rationale.

## Sources index

- Superpowers: skill sources at `obra/superpowers@main`; blog.fsck.com posts
  2025-10-05 / 2025-10-09 / 2025-12-18 / 2026-02-12 (v4.3.0 post-mortem) /
  2026-06-15 (v6 eval data); skills.sh/obra/superpowers.
- mattpocock/skills: local clone + skills.sh/mattpocock/skills.
- Anthropic feature-dev: `anthropics/claude-plugins-official` plugins/feature-dev
  (command + 3 agents, verbatim).
- SDD tools: `github/spec-kit` templates + command files; kiro.dev docs (EARS,
  hooks, steering); `Fission-AI/OpenSpec`; `bmad-code-org/BMAD-METHOD` v4/v6;
  tessl.io docs. Critiques: martinfowler.com/articles/exploring-gen-ai (Böckeler
  SDD series), blog.scottlogic.com 2025-11-26, marmelab.com 2025-11-12,
  ercan.ai/kiro-after-the-hype, innoq.com 2026-04, martinelli.ch.
- ACE-FCA: `humanlayer/advanced-context-engineering-for-coding-agents` +
  `.claude/commands/` templates. Harper Reed: harper.blog 2025-02-16, 2025-05-08.
  Kent Beck: tidyfirst.substack.com (Augmented Coding; Genie posts).
- Evidence: arXiv 2507.09089 (METR RCT), 2603.25764, 2505.06120, 2510.20270
  (ImpossibleBench), 2606.28430, 2410.06992 (SWE-bench+), 2503.14499 (horizons),
  2402.13521, 2607.05139, 2410.21136, 2412.14137, 2308.16557 (MuTAP), 2501.12862
  (Meta ACH), 2407.21787, 2310.01798, 2407.00215 (CriticGPT), 2306.05685,
  2404.13076, 2311.17371, 2503.13657 (MAST), 2407.01489 (Agentless), 2303.06689,
  2411.12924 (HULA), 1609.04886 (Menzies), 2310.10996 (ClarifyGPT), 2208.05950 /
  2404.10100 (TiCoder), 2207.05987 (DocPrompting), 2407.09726, 2401.01701,
  2607.06636 (spec-grounded tests), 2602.02584 (security constitutions), Hill 2026
  (doi.org/10.5281/zenodo.19415187), Kohavi (Trustworthy Online Controlled
  Experiments).
