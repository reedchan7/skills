# Code-review Agent Skills 市场与机制调研

> 快照时间：2026-07-24 15:12–15:26 CST
>
> 范围：公开 `SKILL.md`、Claude Code 官方插件源码、GitHub 官方目录/API、skills.sh 官方目录，以及一篇一手评测论文。
>
> 初筛 27 个，保留 15 个代表候选深读。此文只评估现有候选与可复用机制，不评价本仓库后续产出的 skill。

## 结论摘要

- 公开采用量最高的 code-review 相关 skill 是 Superpowers `requesting-code-review`（177.6K 次目录安装）、Matt Pocock `code-review`（166.6K）与 Superpowers `receiving-code-review`（147.4K）。前两项 Superpowers skill 分别负责发起审查与处理反馈，缺陷发现能力依赖被调度的 reviewer。
- 通用审查中，Matt 的“标准 / 需求双轴隔离”、Addy Osmani 的“五轴质量门禁”、Anthropic 的“多路发现 + 逐条置信度复核”、Dyad 的“多角度发现 + 对抗式反驳”、Sentry 的“可利用性与攻击者输入确认”最值得提炼。
- 专项审查的程序化程度更高。Trail of Bits 的 C review 使用确定性任务规划、并行 worker、产物完整性复核、去重裁判、误报裁判以及 Markdown/SARIF 双输出；这类机制明显强于只堆语言清单的通用 prompt。
- 安装量、仓库星数和质量没有稳定的等价关系。Trail of Bits `c-review` 只有 2.0K 次安装，却有完整的 worker/judge/重试/产物协议；安装排行只能作为采用背景。
- 没有公开、可比的“好评率”、星级评分、活跃用户数或 code-review 缺陷召回率。下文不会把 GitHub stars、forks 或 skills.sh installs 写成质量分。

## 证据口径

### 真实采用数据

skills.sh 官方文档说明，其排行榜来自 `skills` CLI 的匿名安装遥测；详细 API 文档将 `installs` 定义为累计去重安装数。本文通过 `npx -y skills find ...` 和公开 skill 页面采样。它能说明该 CLI 生态内的安装采用，不能说明活跃使用、执行成功、用户满意度或审查质量。

来源：[skills.sh 文档](https://www.skills.sh/docs)、[skills.sh API 字段定义](https://www.skills.sh/docs/api#response-fields)。表中的 `K` 为官方页面的四舍五入显示值。

### 流行度代理

GitHub stars/forks 来自官方 REST `GET /repos/{owner}/{repo}`，采样时间为 2026-07-24 15:12 CST。它们是整个仓库的热度代理；对于 Gemini CLI、Dyad、Bitwarden Android、OpenEnv 等产品主仓，不能归因到某一个内置 skill。

来源：[GitHub Repositories REST API](https://docs.github.com/en/rest/repos/repos#get-a-repository)。最近更新日期取官方 commits API 中“最后一次触及入口文件”的 commit 时间，统一显示 UTC 日期。

### 缺失数据

- skills.sh 没有用户评分、评论数、点赞数或活跃用户数。
- Claude 官方插件目录没有公开安装量；Anthropic 两个插件只能报告源码机制与仓库热度。
- skills.sh 页面存在但没有展示 installs 时，表中写“未公开”，不按 0 处理。
- GitHub release downloads 对这些纯 Markdown skills 通常没有意义，未拿它充当下载量。

## 实证背景：skill 本身不保证提升

[SWE-Skills-Bench](https://arxiv.org/abs/2603.15401) 将 49 个公开 SWE skills 与固定 commit 的真实仓库、显式验收条件和执行型测试配对，约 565 个任务实例。论文报告：39/49 个 skill 没有提升通过率，平均增益只有 +1.2%；7 个专项 skill 有显著收益，3 个因版本错配最多下降 10%，token 开销最高增加 451% 且通过率不变。官方实现与数据在 [GeniusHTX/SWE-Skills-Bench](https://github.com/GeniusHTX/SWE-Skills-Bench)。

这组结果支持后续采用“固定仓库版本 + 隐藏缺陷 + 干净补丁 + 有无 skill 成对运行 + 召回/误报/token/时延”评测。静态清单完整度只能作为设计评审证据，不能代替行为数据。

## 候选全景

### A. 通用审查与 review-loop 工作流

| 候选（固定源码） | 真实安装量 | 仓库热度（stars / forks） | 许可；入口最近更新 | 核心机制与边界 |
|---|---:|---:|---|---|
| [obra/superpowers — requesting-code-review](https://github.com/obra/superpowers/blob/cfb6281371ef/skills/requesting-code-review/SKILL.md) | [177.6K](https://www.skills.sh/obra/superpowers/requesting-code-review) | [260,225 / 23,209](https://api.github.com/repos/obra/superpowers) | MIT；2026-07-24 | 在每个任务、重大功能和合并前调度独立 reviewer；传入精确 commit 范围、需求和实现摘要，隔离主会话上下文。它是审查发起协议，实际发现质量取决于 reviewer 模板与模型。 |
| [mattpocock/skills — code-review](https://github.com/mattpocock/skills/blob/14c13c5bf9ec/skills/engineering/code-review/SKILL.md) | [166.6K](https://www.skills.sh/mattpocock/skills/code-review) | [185,349 / 15,897](https://api.github.com/repos/mattpocock/skills) | MIT；2026-07-01 | 固定 merge-base 后并行运行 Standards 与 Spec 两个隔离 subagent；明确抓“违反仓库规范、缺需求、错实现、范围膨胀”。双轴结果保持分离，减少重排损失；没有显式的独立安全/性能/历史发现通道。 |
| [wshobson/agents — code-review-excellence](https://github.com/wshobson/agents/blob/47a5dbc3f9c2/plugins/developer-essentials/skills/code-review-excellence/SKILL.md) | [25.3K](https://www.skills.sh/wshobson/agents/code-review-excellence) | [38,190 / 4,093](https://api.github.com/repos/wshobson/agents) | MIT；2026-03-07 | 从上下文、高层设计、逐行审查到总结决策的完整流程，含 severity、Python/TS/JS 模式、安全/测试/架构清单和反馈话术。覆盖广且可教学；没有逐条独立复核或显式误报门槛。 |
| [addyosmani/agent-skills — code-review-and-quality](https://github.com/addyosmani/agent-skills/blob/e27041522689/skills/code-review-and-quality/SKILL.md) | [18.1K](https://www.skills.sh/addyosmani/agent-skills/code-review-and-quality) | [80,099 / 8,631](https://api.github.com/repos/addyosmani/agent-skills) | MIT；2026-07-05 | Correctness、Readability、Architecture、Security、Performance 五轴；先看测试，再看实现；有 severity、结构性修复、依赖升级纪律、多模型视角和结构化 verdict。公开采用高，暂无公开的跨语言缺陷召回/误报数据。 |
| [google-gemini/gemini-cli — code-reviewer](https://github.com/google-gemini/gemini-cli/blob/b703c87a643a/.gemini/skills/code-reviewer/SKILL.md) | [8.5K](https://www.skills.sh/google-gemini/gemini-cli/code-reviewer) | [106,147 / 14,310](https://api.github.com/repos/google-gemini/gemini-cli) | Apache-2.0；2026-01-21 | 自动区分远程 PR 与本地 staged/unstaged 变更，读取 PR 描述和评论，覆盖正确性、安全、性能、可维护性和测试，按 Critical/Warning/Suggestion 输出。简洁易移植；没有并行发现和独立置信度复核。 |
| [awesome-skills/code-review-skill](https://github.com/awesome-skills/code-review-skill/blob/ee0353632400/SKILL.md) | [586](https://www.skills.sh/awesome-skills/code-review-skill/code-review-skill) | [1,502 / 163](https://api.github.com/repos/awesome-skills/code-review-skill) | MIT；2026-07-14 | 核心约 190 行，按需加载 17+ 语言/框架、架构、安全和性能参考，四阶段流程与六级反馈标签。progressive disclosure 做得清楚；14,000+ 行指南带来版本漂移、规则冲突和维护成本。 |
| [garrytan/gstack — review](https://github.com/garrytan/gstack/blob/11de390be1be/review/SKILL.md) | [269](https://www.skills.sh/garrytan/gstack/review) | [124,000 / 18,573](https://api.github.com/repos/garrytan/gstack) | MIT；2026-06-25 | 预落地审查：探测 base、scope drift、plan items 的 DONE/NOT DONE/CHANGED/UNVERIFIABLE、远端最新 merge-base、外部状态边界、历史 learnings 等。运营闭环丰富；入口超过千行且强耦合 gstack，token 和迁移成本高。 |

### B. 多 Agent、误报控制与安全审查

| 候选（固定源码） | 真实安装量 | 仓库热度（stars / forks） | 许可；入口最近更新 | 核心机制与边界 |
|---|---:|---:|---|---|
| [Anthropic 官方 code-review plugin](https://github.com/anthropics/claude-plugins-official/blob/4ca561fb8532/plugins/code-review/commands/code-review.md) | 未公开 | [32,578 / 3,656](https://api.github.com/repos/anthropics/claude-plugins-official) | Apache-2.0；2025-11-20 | 先做 PR eligibility、收集相关 `CLAUDE.md` 和摘要；5 个 Sonnet finder 分别看规范、浅层 bug、git history、历史 PR 评论和代码注释；每条候选再交给独立 Haiku 打 0–100，低于 80 丢弃，最后复查 eligibility 并评论。强项是历史上下文与误报门槛；明确跳过 build/typecheck、一般测试覆盖和泛安全问题。README 仍写 4 个 reviewer，与命令源码的 5 个有文档漂移。 |
| [dyad-sh/dyad — deep-review](https://github.com/dyad-sh/dyad/blob/92646d765ded/.claude/skills/deep-review/SKILL.md) | 未公开 | [21,035 / 2,545](https://api.github.com/repos/dyad-sh/dyad) | Apache-2.0（该路径位于非 Pro 区域）；2026-07-03 | 6 个 finder 并行覆盖 shallow diff、深层逻辑、history、跨文件一致性、边界测试和项目规则；去重后，每条交给“尝试反驳”的 verifier，只有置信度 ≥75 才报告。高信号设计突出；agent 成本与延迟高，暂无公开安装/行为基准。 |
| [dyad-sh/dyad — multi-pr-review](https://github.com/dyad-sh/dyad/blob/7d8379b21b73/.claude/skills/multi-pr-review/SKILL.md) | 未公开 | [21,035 / 2,545](https://api.github.com/repos/dyad-sh/dyad) | Apache-2.0（该路径位于非 Pro 区域）；2026-02-14 | Correctness、Code Health、UX 三个 reviewer 接收不同随机文件顺序，降低首因顺序偏差；汇总后由主 agent 做 reasoned validation，不采用简单票数共识，再去重已有评论并发布。对偏差控制有明确设计；内联完整 diff 容易碰上下文上限。 |
| [getsentry/skills — security-review](https://github.com/getsentry/skills/blob/24361e7958f9/skills/security-review/SKILL.md) | [11.5K](https://www.skills.sh/getsentry/skills/security-review) | [884 / 45](https://api.github.com/repos/getsentry/skills) | Apache-2.0；2026-04-19 | 研究范围允许扩到全仓，但报告限制在用户指定 scope；每条需确认攻击者输入、source→sink、缓解措施和实际影响，只报告 High confidence，另列 Needs Verification。误报纪律很强。当前入口引用的 `languages/go.md`、`languages/rust.md`、`infrastructure/terraform.md`、`ci-cd.md`、`cloud.md` 在仓库中缺失，属于可复现的包完整性缺陷。 |
| [trailofbits/skills — differential-review](https://github.com/trailofbits/skills/blob/540111a52a2b/plugins/differential-review/skills/differential-review/SKILL.md) | [5.1K](https://www.skills.sh/trailofbits/skills/differential-review) | [6,242 / 541](https://api.github.com/repos/trailofbits/skills) | CC-BY-SA-4.0；2026-04-29 | 面向安全 diff：按仓库规模自适应深度，强制 git history/blame、blast radius、测试覆盖、攻击场景、覆盖限制和 Markdown 报告；高风险可调 adversarial modeler。证据意识强；适合作为安全专项层，无法取代通用产品/需求审查。 |

### C. 语言、数据库与项目规则专项

| 候选（固定源码） | 真实安装量 | 仓库热度（stars / forks） | 许可；入口最近更新 | 核心机制与边界 |
|---|---:|---:|---|---|
| [github/awesome-copilot — sql-code-review](https://github.com/github/awesome-copilot/blob/caab1f623bb6/skills/sql-code-review/SKILL.md) | [12.1K](https://www.skills.sh/github/awesome-copilot/sql-code-review) | [36,979 / 4,631](https://api.github.com/repos/github/awesome-copilot) | MIT；2026-02-24 | 通用 SQL 的 injection、权限、数据保护、查询/index/join/聚合性能、schema、MySQL/PostgreSQL/SQL Server/Oracle 差异、测试与输出模板。知识面广；1–10 主观分与大量 checklist 缺少 exploitability/执行计划证据门槛。 |
| [trailofbits/skills — c-review](https://github.com/trailofbits/skills/blob/cfe5d7b1619e/plugins/c-review/skills/c-review/SKILL.md) | [2.0K](https://www.skills.sh/trailofbits/skills/c-review) | [6,242 / 541](https://api.github.com/repos/trailofbits/skills) | CC-BY-SA-4.0；2026-06-30 | C/C++ 安全审查的确定性 planner 将 memory corruption、integer、race、platform 风险分配给并行 workers；带 cache primer、失败重试、coverage/artifact validator、去重 judge、FP+severity judge、`REPORT.md` 与 SARIF，并显式暴露 partial run。机制最完整之一；重、慢、强依赖插件脚本与 Claude/Codex tool 语义。 |
| [thoughtbot/rails-audit-thoughtbot](https://github.com/thoughtbot/rails-audit-thoughtbot/blob/c50f924e2fb4/SKILL.md) | [43](https://www.skills.sh/thoughtbot/rails-audit-thoughtbot/rails-audit-thoughtbot) | [222 / 11](https://api.github.com/repos/thoughtbot/rails-audit-thoughtbot) | MIT；2026-03-27 | Rails 全仓审计，按 Testing/Security/Models/Controllers/Design/Views 分类；可并行运行 SimpleCov 与 RubyCritic，用真实 coverage/complexity 反哺人工分析，最后分 severity 输出 Markdown。证据融合好；任务更像全仓 audit，成本高于 PR diff review。 |

## 横向比较

### 采用量领先者

1. `requesting-code-review` — 177.6K，属于调度工作流。
2. Matt `code-review` — 166.6K，属于实际双轴 review。
3. `receiving-code-review` — 147.4K，属于反馈处置工作流。
4. `code-review-excellence` — 25.3K，属于通用流程/清单型 review。
5. Addy `code-review-and-quality` — 18.1K，属于五轴通用质量门禁。

把前三名合并看成“review loop 生态”更准确；只按 skill 名称排序会把调度、发现、反馈处置混在一起。

### 机制成熟度领先者

- **误报控制**：Anthropic code-review（每条独立评分、阈值 80）、Dyad deep-review（对抗式反驳、阈值 75）、Sentry security-review（攻击者输入与可利用性确认）、Trail of Bits C review（独立 FP judge）。
- **需求对齐**：Matt 将 Standards 与 Spec 隔离并行；gstack 进一步把计划项分成 DONE/NOT DONE/CHANGED/UNVERIFIABLE，并区分 repo diff 与外部状态。
- **跨文件与历史**：Anthropic、Dyad、Trail of Bits differential-review 都显式使用 history/blame；Dyad 还单列跨文件一致性，Alireza 单列 blast radius。
- **可复现产物**：Trail of Bits C review 的产物协议最完整，能暴露漏跑、worker 失败、产物缺失和空结果；多数通用 skill 只规定最终 Markdown 样式。
- **专项知识**：SQL、C/C++ 与 Rails 候选的价值来自强领域约束。SWE-Skills-Bench 的结论也支持优先选择上下文匹配的专项 skill。

### 高频缺陷

- **把清单当证据**：列出 OWASP、性能、测试、架构等词不等于能找到真实、可达、位于变更行的缺陷。
- **缺 scope 防线**：部分 skill 没有 merge-base、changed-line、pre-existing 问题或读写边界，容易审成全仓重构建议。
- **没有误报裁判**：单模型边看边报，缺少“尝试反驳、追调用链、确认输入可控、复现失败场景”的第二阶段。
- **固定主观评分**：1–10 的“安全分/质量分”没有校准集，跨语言和跨模型不可比。
- **文档或包漂移**：Anthropic README 的 reviewer 数量落后于命令源码；Sentry security-review 当前引用若干不存在的参考文件；14,000+ 行多语言 reference 也更容易过时。
- **主仓热度错配**：Gemini CLI、gstack 与 Dyad 的 stars 主要来自产品本身，不能据此断言内置 review skill 流行。

## 可提炼的通用精华

1. **先固定审查对象**：解析 base/fixed point，使用 merge-base，纳入 staged/unstaged 的规则需明确；空 diff、draft、closed、generated/trivial PR 早停。
2. **先恢复意图**：读取 PR/issue/spec/plan 与仓库规则；将“需求符合度”和“工程质量”分轴，避免其中一类发现淹没另一类。
3. **发现与复核分离**：finder 追求召回，verifier 负责反驳；每条发现都重新读取真实代码、调用方和变更边界。
4. **只报可行动缺陷**：要求精确 file:line、触发输入/状态、实际错误行为、影响、证据和最小修复方向；排除 pre-existing、未改行、lint/typecheck 可自动处理项和泛泛建议。
5. **按风险配置视角**：通用 correctness、spec、cross-file、history 为基础；只有相关时加载 auth/crypto/database/concurrency/performance/UI/a11y 专项，减少 token 噪音。
6. **历史和 blast radius 是一级输入**：git blame、过去修复、调用方、schema/config/API 消费端、序列化边界能识别 diff 表面看不到的回归。
7. **测试审查分两层**：先看需求是否被测试，再看测试能否真的在回归时失败；测试缺失本身要结合风险和可达路径，避免机械要求覆盖率。
8. **置信度需有证据量表**：把“已复现/调用链确认/框架缓解排除”映射到阈值，未知时降分；severity 与 confidence 分开。
9. **输出暴露覆盖边界**：列出已读 diff、调用链/历史范围、未完成 agent、超大 diff 截断、外部状态和人工后续，避免“零发现”被误读成“零风险”。
10. **只读默认**：报告、PR 评论、自动修复、提交分别需要独立授权；初次审查不隐式改代码。
11. **领域参考按需加载**：progressive disclosure 有价值，但 reference 必须存在、带适用版本，并在运行前做完整性自检。
12. **行为评测优先**：用隐藏缺陷与干净补丁成对测试 recall、precision/误报、severity calibration、changed-line discipline、token 和时延；stars、installs、prompt 行数仅作背景特征。

## 对后续评测的直接要求

- 至少覆盖：隐蔽逻辑错误、跨文件契约、权限/AuthZ、SQL/命令注入、并发竞态、事务/重试、迁移兼容、性能退化、测试假阳性、范围外干净补丁。
- 每个 case 同时记录真阳性、假阳性、漏报、变更行命中、证据完整度、severity 是否合理、token、时延和 agent 数。
- 同一模型、同一固定仓库 commit、同一工具权限下做有/无 skill 配对，至少多次运行；随机化文件顺序，用于观测顺序偏差和稳定性。
- 将 general review 与 security/domain specialist 分开排名；workflow-only skills 不参与缺陷发现榜，只评调度正确性与上下文隔离。
- 报告每轮未覆盖范围和失败 worker。不能把部分运行或工具失败写成 clean review。

## 一手来源索引

- Agent Skill 与 Copilot code review 的官方适配规则：[GitHub Docs — Adding agent skills for GitHub Copilot](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills)
- GitHub 仓库指标：[Repositories REST API](https://docs.github.com/en/rest/repos/repos#get-a-repository)
- skills.sh 安装遥测与质量免责声明：[skills.sh Docs](https://www.skills.sh/docs)
- skills.sh installs 字段与目录 API：[skills.sh API Reference](https://www.skills.sh/docs/api)
- Agent skills 行为收益研究：[SWE-Skills-Bench 论文](https://arxiv.org/abs/2603.15401)、[官方仓库](https://github.com/GeniusHTX/SWE-Skills-Bench)
- 每个候选的固定源码、目录页、仓库 API 均已就近链接在表格中。
