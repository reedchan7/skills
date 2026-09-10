# Sources, interpretation and limits

Primary sources checked on 2026-09-07. This skill is an engineering synthesis,
not a reproduction of these works or a claim that a particular author endorses
the whole workflow. Books were consulted through the linked author/publisher
material; a catalog/abstract is not evidence of reading a complete book/paper.
Normal execution does not require opening these sources.

## Foundations mapped to decisions

| Source and material consulted | Contribution to this skill | Limit / application |
|---|---|---|
| Martin Fowler, [Refactoring: definition and overview](https://refactoring.com/), and [preparatory refactoring example](https://martinfowler.com/articles/preparatory-refactoring-example.html) | Small behavior-preserving transformations, driven by making a concrete change easier | A known transformation does not prove its preconditions or local benefit |
| Michael Feathers, *Working Effectively with Legacy Code*: [publisher chapter on seams](https://www.informit.com/articles/article.aspx?p=359417), and [author's characterization-testing article](https://michaelfeathers.silvrback.com/characterization-testing) | Observe existing behavior and introduce a minimal seam when dependencies obstruct observation | Characterization preserves observed behavior; it does not establish that behavior is desirable |
| D. L. Parnas, [On the Criteria To Be Used in Decomposing Systems into Modules](https://www.cs.lafayette.edu/~gexia/cs301/resources/parnas.html), CACM 1972, university-hosted text | Hide a design decision rather than merely split processing stages | The host warns its digitization may be imperfect; apply the argument, not a universal module shape |
| John Ousterhout, *A Philosophy of Software Design*: [author's edition notes](https://www.web.stanford.edu/~ouster/cgi-bin/book.php), [modular-design lecture](https://web.stanford.edu/~ouster/cgi-bin/cs190-winter18/lecture.php?topic=modularDesign) | Evaluate what an interface hides and what callers must learn; shallow fragmentation can add complexity | Module depth is a design lens, not a numeric score or permission for oversized incoherent modules |
| Kent Beck's simple-design rules, [Martin Fowler's formulation and discussion](https://martinfowler.com/bliki/BeckDesignRules.html) | Working behavior, understandable intent, useful removal of duplication and unnecessary elements | Fowler explicitly discusses variants and judgment; these are not a mechanically complete design test |
| Gamma, Helm, Johnson and Vlissides, *Design Patterns*: [publisher overview/catalog](https://www.informit.com/store/design-patterns-elements-of-reusable-object-oriented-9780201633610) | Pattern selection must include applicability, constraints and consequences | The consulted overview supports the selection method, not claims about reading all pattern implementations; use language-native mechanisms |
| Sandi Metz, [The Wrong Abstraction](https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction) | Consider undoing a flag-laden shared abstraction when callers represent different policies | Practice-based argument; duplication and abstraction both have costs that need local evidence |
| Barbara Liskov and Jeannette Wing, [A Behavioral Notion of Subtyping](https://www.cs.cmu.edu/~wing/publications/LiskovWing94.pdf), 1994 | Replacing an implementation must retain client-visible guarantees, not only a matching signature | Formal substitution requirements do not imply that ordinary tests prove all program properties |
| Arthur H. Watson and Thomas J. McCabe, [NIST SP 500-235: Structured Testing](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication500-235.pdf), 1996 | Control-flow complexity informs test-path reasoning; path feasibility and other semantics still matter | Use the analyzer's actual graph conventions; do not equate a lower metric with total quality |
| G. Ann Campbell / SonarSource, [Cognitive Complexity white paper](https://www.sonarsource.com/docs/CognitiveComplexity.pdf), and [cyclomatic-complexity limitations](https://www.sonarsource.com/resources/library/cyclomatic-complexity/) | Complement path-oriented metrics with nesting/flow readability; detect metric gaming | Tool-authored heuristic and guidance, not a universal human-comprehension oracle |
| Adam Tornhill, [change coupling](https://codescene.com/blog/change-coupling-visualize-the-cost-of-change) | Use change history to locate coordination costs beyond static imports | Vendor/author practice evidence; sample size, bulk commits and repository workflow confound counts |
| Jerome H. Saltzer and Michael D. Schroeder, [The Protection of Information in Computer Systems: principles](https://web.mit.edu/saltzer/www/publications/protection/Basic.html), 1975 | Review enforcement ownership, failure behavior and unnecessary privilege/mechanism during boundary changes | Principles guide scrutiny; the original text itself cautions against treating them as absolute rules |
| OWASP, [Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html) | Retain least privilege, default-deny intent and checks on every relevant request | Apply to the affected path; a refactor is not blanket authorization for policy changes |

## Empirical checks on the claims

- Kim, Zimmermann and Nagappan, [An Empirical Study of Refactoring Challenges
  and Benefits at Microsoft](https://www.microsoft.com/en-us/research/publication/an-empirical-study-of-refactoring-challenges-and-benefits-at-microsoft/),
  IEEE TSE 2014, research abstract: reported benefits vary by dimension and
  include costs. This supports measuring dependencies/complexity alongside
  size; it does not establish that every refactor reduces defects.
- Kaur and Singh, [How does Object-Oriented Code Refactoring Influence Software
  Quality?](https://arxiv.org/abs/1908.05399), 2019 mapping-study abstract:
  reports variable quality effects and limited industrial validation. It
  supports explicit tradeoffs and cautious generalization, not a numeric
  uplift target for this skill.

## Resolving tensions in practice

Small steps concern change safety; they do not require tiny final functions.
Removing duplication is useful when the repeated knowledge shares a reason
to change. Information hiding may justify an abstraction before a third
occurrence; an existing abstraction may deserve removal. Preserve explanatory
contracts when naming or extraction cannot express them clearly. Complexity
metrics and design principles raise questions; behavior evidence and the
actual maintenance problem decide the transformation.

The skill's authority handling, Git ownership protocol, evidence labels and
disposable follow-up exercise are workflow choices synthesized for agent
execution. They are not attributed as verbatim rules from these sources.
