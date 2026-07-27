# Code Review Skill 候选调研与静态机制评测

> 调研快照：2026-07-24。本文评价的是 skill / plugin 的公开指令、流程设计与可复现实证，不能直接等同于真实缺陷召回率。安装量来自 [skills.sh](https://www.skills.sh/) 的匿名安装遥测；GitHub Star 是仓库级信号。二者都能说明传播度，无法单独证明 review 质量。

## 结论摘要

当前没有一个候选同时拿下规格一致性、差分历史、调用链、安全、性能、测试、证据、低误报与上下文效率。

- **Trail of Bits `differential-review`** 拥有最完整的历史、影响面、攻击路径和覆盖边界机制，是安全差分审查的最佳底座。
- **Anthropic Code Review plugin** 拥有最值得复用的误报控制：多个发现者独立工作，再为每条候选问题启动独立复核者，只发布高信号问题。
- **Superpowers `requesting-code-review` + `receiving-code-review`** 拥有最完整的生命周期：精准构造 review packet、隔离上下文、技术性处理反馈、逐项落地与再次审阅。
- **Matt `code-review`** 的“Standards / Spec 两轴隔离”最能防止“代码写得漂亮但做错需求”以及“满足需求但违背仓库约束”。
- **Addy `code-review-and-quality`** 是覆盖面最均衡的通用质量清单，依赖升级和结构性改进建议尤其成熟。
- **Ponytail review** 是最锋利、最省上下文的减法专项；它应处于正确性审查之后，不能承担通用 review。
- **OpenAI Codex 的 14 行 orchestrator** 证明编排器可以非常小：按 `code-review-*` 专项并行分发。它当前的“返回所有问题且数量不限”会放大噪声，适合借架构，不适合照搬聚合策略。

最强通用 skill 的方向很明确：**小型编排器 + 风险驱动的专项发现 + 调用链/历史上下文 + 逐条独立复核 + 根因去重 + 可执行 finding contract + 可量化 eval**。继续扩充单体 checklist 的边际收益已经很低。

## 调研方法与证据口径

本轮全文阅读了点名候选及其直接依赖资料：

- Matt：`SKILL.md` 与本机 alias。
- Addy：396 行 `SKILL.md`、行为 eval 定义和 fixture。
- Trail of Bits：`SKILL.md`、`methodology.md`、`adversarial.md`、`reporting.md`、`patterns.md`。
- Anthropic：plugin `README.md` 和完整 `/code-review` command。
- Superpowers：request skill、reviewer template、receive skill。
- Ponytail：完整 review skill。
- Jeffallan：主 skill 与六份 references。
- Everything Claude Code：security skill、reviewer agent、command。
- Hermes：主 skill 与 report template。
- OpenAI Codex：orchestrator、breaking changes、change size、context、testing 五个专项。
- Google Gemini CLI：仓库内 `.gemini/skills/code-reviewer/SKILL.md`。
- wshobson：完整 `code-review-excellence/SKILL.md`。

另外读取了 Agno 的 31 行 sample skill、style guide 和启发式脚本，用作低端基线。它定位为教学样例，脚本只做行长、尾随空格和简单命名启发式，未纳入正式排名。

评分只回答“指令是否明确要求这些机制”。评分锚点：

| 分值 | 含义 |
|---:|---|
| 0 | 明确在范围外或完全缺失 |
| 1 | 一句泛化提醒 |
| 2 | 有 checklist，无操作闭环 |
| 3 | 有明确步骤和输出要求 |
| 4 | 能产出可复查证据，并有失败处理 |
| 5 | 有强制门禁、独立复核或定量闭环 |

### 权重

| 维度 | 权重 | 评价重点 |
|---|---:|---|
| 流程完整性 | 10 | 输入、范围、阶段、失败与收尾是否明确 |
| 差分 / 历史 | 10 | merge-base、commit timeline、blame、回归历史 |
| 调用链 / 影响面 | 9 | caller、callee、入口、状态流、公共契约 |
| 正确性 / 规格 | 14 | 需求遗漏、错误实现、边界、并发、兼容性 |
| 安全 | 10 | trust boundary、auth、注入、数据损失、攻击可达性 |
| 性能 | 6 | 复杂度、I/O、查询、资源、热点路径 |
| 测试 | 9 | 测试意图、缺口、回归能力、实际运行证据 |
| 证据质量 | 10 | file:line、因果链、触发条件、可证伪性 |
| 误报控制 | 10 | 独立复核、置信度、去重、工具可发现项过滤 |
| 输出可执行性 | 7 | 严重级别、影响、最小修复、明确 verdict |
| 上下文效率 | 5 | progressive disclosure、并行隔离、避免重复清单 |

总分为各维度 `0–5` 分按权重折算后的静态机制覆盖分。专项 skill 的低总分不代表专项能力弱；例如 Ponytail 明确放弃安全与正确性，Trail of Bits 明确偏向安全。

## 采用度快照

| 候选 | skills.sh 安装量 | GitHub Star | 原始来源 | 本机原文 |
|---|---:|---:|---|---|
| Matt `code-review` | [166.2K](https://www.skills.sh/mattpocock/skills) | 185,344 | [SKILL.md](https://github.com/mattpocock/skills/blob/main/skills/engineering/code-review/SKILL.md) | `/Users/reedchan/Workspaces/github/mattpocock/skills/skills/engineering/code-review/SKILL.md` |
| Addy `code-review-and-quality` | [16.4K](https://www.skills.sh/addyosmani/agent-skills) | 80,099 | [SKILL.md](https://github.com/addyosmani/agent-skills/blob/main/skills/code-review-and-quality/SKILL.md) | `/Users/reedchan/Workspaces/github/addyosmani/agent-skills/skills/code-review-and-quality/SKILL.md` |
| Trail of Bits `differential-review` | [5.0K](https://www.skills.sh/trailofbits/skills) | 6,242 | [skill 目录](https://github.com/trailofbits/skills/tree/main/plugins/differential-review/skills/differential-review) | 本机未安装，读取线上原文 |
| Anthropic Code Review plugin | 无同口径独立数据 | 138,892 | [README](https://github.com/anthropics/claude-code/blob/main/plugins/code-review/README.md) · [command](https://github.com/anthropics/claude-code/blob/main/plugins/code-review/commands/code-review.md) | `/Users/reedchan/.claude/plugins/marketplaces/claude-plugins-official/plugins/code-review/` |
| wshobson `code-review-excellence` | [25.3K](https://www.skills.sh/wshobson/agents/code-review-excellence) | 38,190 | [SKILL.md](https://github.com/wshobson/agents/blob/main/plugins/developer-essentials/skills/code-review-excellence/SKILL.md) | 本机未安装，读取线上原文 |
| Ponytail review | [9.5K](https://www.skills.sh/dietrichgebert/ponytail/ponytail-review) | 88,603 | [SKILL.md](https://github.com/DietrichGebert/ponytail/blob/main/skills/ponytail-review/SKILL.md) | `/Users/reedchan/.codex/plugins/cache/ponytail/ponytail/4.8.4/skills/ponytail-review/SKILL.md` |
| Superpowers request / receive | [176.9K / 146.7K](https://www.skills.sh/obra/superpowers) | 260,224 | [request](https://github.com/obra/superpowers/tree/main/skills/requesting-code-review) · [receive](https://github.com/obra/superpowers/blob/main/skills/receiving-code-review/SKILL.md) | `/Users/reedchan/.codex/plugins/cache/superpowers-official/superpowers/6.1.1/skills/` |
| OpenAI Codex review suite | [orchestrator 412](https://www.skills.sh/openai/codex/code-review) | 101,079 | [skill 目录](https://github.com/openai/codex/tree/main/.codex/skills) | `/Users/reedchan/Workspaces/github/openai/codex/.codex/skills/code-review/SKILL.md` |
| Google Gemini CLI reviewer | [8.5K](https://www.skills.sh/google-gemini/gemini-cli/code-reviewer) | 106,146 | [SKILL.md](https://github.com/google-gemini/gemini-cli/blob/main/.gemini/skills/code-reviewer/SKILL.md) | 本机未安装，读取线上原文 |
| Jeffallan `code-reviewer` | [4.6K](https://www.skills.sh/jeffallan/claude-skills/code-reviewer) | 10,709 | [skill 目录](https://github.com/Jeffallan/claude-skills/tree/main/skills/code-reviewer) | 本机未安装，读取线上原文 |
| ECC security + reviewer | [security skill 1.5K](https://www.skills.sh/affaan-m/ecc/security-review) | 232,647 | [security skill](https://github.com/affaan-m/ECC/blob/main/skills/security-review/SKILL.md) · [reviewer](https://github.com/affaan-m/ECC/blob/main/agents/code-reviewer.md) | `/Users/reedchan/Workspaces/github/affaan-m/everything-claude-code/` |
| Hermes `github-code-review` | [247](https://www.skills.sh/nousresearch/hermes-agent/github-code-review) | 219,656 | [skill 目录](https://github.com/NousResearch/hermes-agent/tree/main/skills/github/github-code-review) | `/Users/reedchan/Workspaces/github/NousResearch/hermes-agent/skills/github/github-code-review/SKILL.md` |

仓库 Star 很容易被整个产品或 skill pack 放大。Anthropic、OpenAI、Gemini、ECC、Hermes 的 Star 不能归因给单个 review skill。skills.sh 安装量也只代表安装事件，不代表活跃使用、成功率或留存。

## 候选评分表

缩写：流=流程，史=差分/历史，链=调用链，正=正确性/规格，安=安全，性=性能，测=测试，证=证据，准=误报控制，行=可执行性，效=上下文效率。

| 排名 | 候选 | 流 | 史 | 链 | 正 | 安 | 性 | 测 | 证 | 准 | 行 | 效 | 加权总分 |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | Trail of Bits differential-review | 5 | 5 | 5 | 3.5 | 5 | 1.5 | 4 | 5 | 3.5 | 4.5 | 2.5 | **83.6** |
| 2 | Superpowers request + receive | 5 | 3.5 | 2 | 4 | 3 | 3 | 4.5 | 4 | 4 | 5 | 4.5 | **77.0** |
| 3 | Anthropic Code Review plugin | 5 | 4.5 | 1.5 | 3.5 | 2.5 | 1.5 | 1 | 4.5 | 5 | 4.5 | 4 | **69.4** |
| 4 | Addy code-review-and-quality | 4.5 | 2 | 2 | 4 | 3.5 | 3.5 | 4 | 3.5 | 3 | 4.5 | 2.5 | **68.0** |
| 5 | ECC security-review + reviewer | 3.5 | 2.5 | 2.5 | 3 | 4 | 3 | 3 | 3.5 | 4 | 4 | 2.5 | **65.0** |
| 6 | Jeffallan code-reviewer | 4.5 | 1.5 | 1 | 4 | 3 | 3 | 4 | 3 | 3 | 4 | 3.5 | **62.9** |
| 7 | Matt code-review | 4.5 | 3 | 1 | 4.5 | 1 | 1 | 1.5 | 4.5 | 3.5 | 3.5 | 4.5 | **60.7** |
| 8 | Hermes github-code-review | 4.5 | 3.5 | 2 | 3 | 1.5 | 3 | 3.5 | 3 | 2 | 4.5 | 2 | **59.2** |
| 9 | OpenAI Codex review suite | 4.5 | 2 | 3 | 3.5 | 1 | 1 | 4.5 | 4 | 1.5 | 3 | 4 | **58.7** |
| 10 | wshobson code-review-excellence | 4 | 1.5 | 1 | 3 | 3 | 3 | 3 | 2 | 3 | 3.5 | 2 | **53.1** |
| 11 | Google Gemini CLI reviewer | 4 | 2 | 1.5 | 3 | 2.5 | 2.5 | 3 | 2 | 2 | 3 | 4 | **52.7** |
| 12 | Ponytail review | 4 | 2.5 | 1.5 | 0 | 0 | 0 | 1 | 3 | 3 | 5 | 5 | **41.5** |

这张表的正确读法：Trail of Bits 赢在安全差分深度；Superpowers 赢在流程闭环；Anthropic 赢在 precision；Matt 赢在规格忠实度；Ponytail 赢在减法专项。一个通用 skill 要吸收各自峰值，不能把第一名原样改名后发布。

## 逐份分析

### 1. Anthropic 官方 Code Review plugin

**独特机制**

1. 先由轻量 agent 判断 PR 是否关闭、草稿、自动化、显然无须审查或已有 Claude 评论。
2. 独立收集与改动路径相关的 `CLAUDE.md`，再由单独 agent 总结 PR。
3. 五个 Sonnet agent 并行发现问题，分工互不重叠：`CLAUDE.md` 合规、只看 diff 的浅层 bug、`git blame` 与历史上下文、touch 过这些文件的历史 PR 评论、改动区域内的代码注释约束。
4. 对每个候选问题再启动独立 Haiku agent 按 0–100 rubric 打置信度，`< 80` 直接丢弃；随后重跑一次 eligibility 检查。
5. 默认只输出终端；用户显式传 `--comment` 才写 GitHub。inline comment 需要完整 SHA、准确行范围和 `confirmed: true`。

**优势**

- “独立发现 → 独立反驳 → 过滤”是所有候选中最强的低误报结构。
- 明确排除 pre-existing、lint 可发现项、审美建议和重复评论。
- standards agent 只能引用与文件路径作用域相符的 `CLAUDE.md`，证据边界清晰。
- 读写边界较稳健，默认不产生外部副作用。

**遗漏与上限**

- 当前 command 要求 bug agent 主要看 diff，且主动排除依赖特定输入或状态的问题。很多真实缺陷正好依赖边界输入、状态机、并发顺序、权限组合或调用方契约，这会牺牲召回率。
- 没有强制 caller / callee、入口可达性、状态流、schema、迁移或公共 API 兼容性分析。
- 一般测试缺口、性能问题和“泛化安全问题”被排除，除非 `CLAUDE.md` 明文要求。
- 五个 finder 里三个（历史、历史 PR 评论、代码注释）都是“读周边文本”，只有一个真正读 diff 找 bug，且它被要求不读额外上下文；正确性召回的实际预算比看起来小。
- 单一 Haiku 打分器决定去留，rubric 里 `50` 档明确包含“已验证为真但不重要”，会连同真实的低影响缺陷一起被 `>= 80` 阈值滤掉。
- 文档漂移方向与直觉相反：`commands/code-review.md` 才是 5 个 finder + `0–100` + `< 80` 丢弃的权威实现；`README.md` 仍写 “4 parallel agents” 和 “2x CLAUDE.md compliance agents”，落后于命令源码。引用该 plugin 的机制时以 command 为准。
- “已有 Claude 评论即跳过”若未比较最后审阅 SHA 与当前 head，可能错过后续提交。

**可复用精华**

- 每条 finding 由第二个 agent 尝试证伪。
- 默认高 precision；“需要更多上下文”放到非阻塞区，不能静默当成不存在。
- 外部写入必须显式授权；评论前核对唯一性、行号和 suggestion 完整性。

### 2. Trail of Bits `differential-review`

**独特机制**

- 先建立 baseline 的 invariant、trust boundary、校验模式、call graph 和 state flow。
- 按代码库规模选择 DEEP / FOCUSED / SURGICAL，再按 auth、crypto、外部调用、价值转移等风险分类。
- 对每个 diff region 比较 before / after，追溯被删除代码的 blame 和历史，搜索被重新引入的旧漏洞模式。
- 显式计算 blast radius，并将 risk × callers 组合成优先级矩阵。
- 高风险变更进入 attacker model、入口、前置条件、攻击步骤、可利用性和具体影响分析。
- 报告必须写明覆盖率、未覆盖范围和置信度。

**优势**

- 历史、调用链、影响面、攻击可达性和证据要求远强于通用 checklist。
- “删除了什么保护、它为何存在、谁能触发、影响哪些调用方”直接针对回归根因。
- 把无测试视为风险放大器，同时保持测试缺口与漏洞发现的因果区分。
- 对分析范围保持诚实，适合大型仓库的分层投入。

**遗漏与冗余**

- 偏安全和 Solidity；规格一致性、通用性能、产品行为、可维护性覆盖不足。
- `grep` 文本计数 caller 会把定义、注释、测试算进去，也会漏掉动态分派、反射、事件、路由注册和间接调用。真实实现应优先符号图，再用文本补漏。
- 以文件数判定代码库规模、以 caller 数固定分级过于粗糙；公共 API 的一个调用方也可能是高影响面。
- “新增函数没测试即升级为 HIGH”“refactor 先按 HIGH”容易造成严重度膨胀。
- baseline 阶段直接 `git checkout` 会改变当前工作树；审阅流程应坚持 `git show`、临时 worktree 或只读索引。
- 必须生成大型报告的规则上下文和时间成本较高。
- 示例中出现未经项目证据支撑的金额影响估算，容易把具体场景写成虚假精度。

**可复用精华**

- 固化 `risk × reachability × blast radius`。
- 删除 guard 时强制追历史；改共享函数时强制追 callers、入口和 invariant。
- finding 必须包含攻击者或用户的具体触发路径，影响不可只写“可能出问题”。

### 3. Matt `code-review`

**独特机制**

- 用户提供固定点，使用 `git diff <fixed-point>...HEAD` 对 merge-base 做三点差分。
- 自动从 commit message、用户路径、branch 相关 docs 中定位 spec。
- Standards 与 Spec 使用两个隔离 subagent 并行审阅，防止互相污染。
- Standards 在仓库规范之外带一组 Fowler smells；仓库明确规则优先。
- 聚合时保留两轴，不用一个轴的通过掩盖另一个轴的失败。

**优势**

- 对“实现了错误需求”和 scope creep 的敏感度最高。
- 固定比较点、commit list、spec 引用和 standards 引用让结果可追溯。
- 89 行主文件，机制密度高，上下文成本低。

**遗漏与冗余**

- 缺少通用 bug、安全、性能、测试、调用链和历史意图的专项发现。
- spec 缺失时一半流程停用；需要仓库预先配置 issue tracker。
- smell baseline 中 Primitive Obsession、Data Clumps、Duplicated Code 等规则若机械执行，会鼓励过早抽象，与 YAGNI 发生冲突。
- 聚合明确禁止重新排序和归并，无法消除两个 agent 的重复根因，也无法把高风险行为问题提到最前。
- 没有第二阶段独立复核；判断性 smell 可能直接进入最终报告。

**可复用精华**

- 比较点必须先解析、固定、确认 diff 非空。
- Spec 与 Standards 在发现阶段隔离；最终汇总仍应保留来源标签，同时按风险统一排序和去重。

### 4. Addy `code-review-and-quality`

**独特机制**

- correctness、readability、architecture、security、performance 五轴。
- 先读测试理解意图，再读实现；评论带 Critical / required / Nit / Optional / FYI。
- 对结构性问题必须给出 named remedy，例如合并重复分支、拆 orchestration 与业务逻辑、删除 pass-through wrapper。
- 包含 change sizing、文件体积、依赖升级、changelog、lockfile、transitive graph 等完整纪律。

**优势**

- 通用覆盖最均衡，适合作为所有变更的基础层。
- “整体 code health 变好即可批准”能约束完美主义。
- 依赖升级审查是其他通用候选普遍漏掉的高价值内容。
- 输出优先高杠杆 finding，反对用十个 nit 淹没一个结构问题。

**遗漏与冗余**

- 396 行集中在一个文件，重复 checklist、rationalization、red flag 和末尾 gate，上下文效率偏低。
- 没有明确 base / head、merge-base、blame、调用链、入口、状态流或兼容面流程。
- 没有独立复核、root-cause 去重和 finding 置信度协议。
- 约 100 / 300 / 1000 changed lines、约 1000 file lines 等启发式容易被机械执行。
- `See Also` 指向 `references/security-checklist.md` 和 `references/performance-checklist.md`，当前仓库实际只包含 `SKILL.md`，两个引用不存在。

**已有 eval 的真实含义**

当前仓库 eval 得到 `124 checks passed — 0 errors / warnings`，触发 rank-1 为 `86% (65/76)`。该 skill 自身只有一个行为样例：新增 user search endpoint，fixture 中存在非常明显的 SQL 拼接和日志输入问题。它证明触发、格式和基础安全规则可工作，仍不足以证明多语言真实 PR 的召回率、误报率或严重度校准。

**可复用精华**

- 五轴基础层、测试先行阅读、结构性 remedy、依赖/lockfile 专项。
- 主文件缩成编排契约，把安全、性能、依赖、迁移按风险按需加载。

### 5. Superpowers request + receive

**独特机制**

- reviewer 只得到精准构造的 description、requirements、base SHA、head SHA，不继承实现者的会话历史。
- reviewer template 明确只读，要求 plan alignment、quality、architecture、tests、production readiness 和 file:line 输出。
- review 在任务阶段、重大功能和 merge 前重复发生，避免缺陷层层堆积。
- receive skill 要求先读完、重述、结合代码库事实判断、技术性回应、逐项处理；外部反馈按建议而非命令看待。

**优势**

- 上下文隔离与 review packet 是高质量 subagent 编排的最佳范式。
- 覆盖“发现问题 → 判断反馈 → 落地 → 再跑测试”的完整后半程。
- 对 reviewer 误判、YAGNI、遗留兼容和架构冲突提供合理 pushback 路径。
- 当前安装量在候选中最高，流程已经广泛传播。

**遗漏与冗余**

- reviewer 本体仍是一个宽泛单 pass，没有历史、调用图、状态流或独立复核。
- 示例默认 `HEAD~1`，多 commit 任务可能漏掉前面的提交；base 应来自任务开始时固定的 SHA 或 merge-base。
- “每个任务都 review”对小改动可能成本过高，需按风险合并 checkpoint。
- 强制输出 strengths 和大量社交措辞会占用上下文；正向反馈只保留对后续维护有信息量的部分。
- receive skill 的语气规则很多，属于交互规范，不能替代 finding 的技术复核。

**可复用精华**

- 使用 immutable review packet：`base/head + intent/spec + changed files + tests + constraints`。
- 独立 reviewer 不继承作者推理；处理结果必须留下 accepted / rejected / needs-info 处置记录。

### 6. wshobson `code-review-excellence`

**独特机制与优势**

- 把 review 视作知识分享，按 context、high-level、line-by-line、decision 四阶段推进。
- 强调反馈针对代码、具体可执行、区分 blocking / important / nit / learning / praise。
- 提供 Python、TypeScript、React、security、test quality 示例，适合培训新 reviewer。

**遗漏与冗余**

- 主要是通用工程常识，没有规定如何取得 diff、固定 base、阅读 spec、追历史、追 callers 或运行测试。
- 没有 file:line 证据门禁、置信度、独立复核、去重或覆盖声明。
- 多处建议带栈无关的处方倾向，例如默认引入 Repository、cache、memo、Context，可能制造新复杂度。
- “2–3 分钟 / 5–10 分钟 / 10–20 分钟”以及固定 PR 行数无法成为 agent 可可靠执行的质量机制。
- 大段语言示例和人际沟通内容消耗上下文，模型本身已具备其中大部分知识。

**可复用精华**

- 保留严重度语气和“解释 why + 给出最小修复”；其余通用教程无需进入最终 skill 主文件。

### 7. Ponytail review

**独特机制**

- 只猎杀 over-engineering，使用 `delete / stdlib / native / yagni / shrink` 五个标签。
- 每条 finding 一行：位置、删除对象、替代方案；最后给出净可删除行数。
- 明确把 correctness、security、performance 交给普通 review。

**优势**

- 57 行，触发、边界、格式都极清晰。
- 输出直接对应删除或替换动作，几乎没有 review prose。
- 对 AI 常见的 wrapper、单实现抽象、新依赖和“未来可能需要”特别有效。

**遗漏与风险**

- 总分低源于主动放弃多数维度，不能作为通用 code review。
- “净减少行数”容易被游戏化；更短的代码可能降低可读性、类型安全或错误隔离。
- 没有明确要求在删除前追所有 caller、公共契约、行为测试和历史原因。
- email validator 示例把复杂问题压成 `"@" in email`，在具体 trust boundary 中可能给出过度简化信号。

**可复用精华**

- 作为最终独立 simplification pass；仅接受能证明行为不变、边界保护不减弱的减法 finding。
- 衡量“删除的概念、依赖、分支、状态”，不要把 LOC 当唯一质量指标。

### 8. OpenAI Codex repo-local review suite

**独特机制**

- orchestrator 只有 14 行：为每个 `code-review-*` skill 启动一个 subagent，并行返回 file:line finding。
- 当前专项覆盖 breaking changes、change size、model context 和 integration testing。
- 允许用户级 `code-review-*` 继续扩展，主编排器无需增长。

**优势**

- 模块化和 progressive disclosure 最干净；每个专项可独立演化。
- repo-specific context skill 能编码外部通用 skill 无法知道的强约束。
- integration-test-first 和外部接口 breaking-change pass 有实用价值。

**遗漏与风险**

- 这是 Codex 仓库的定制套件，缺少通用 correctness、security、performance、spec 与 history 专项。
- “每个 subagent 的每个问题全部返回，数量不限”与低误报目标直接冲突。
- 没有独立复核、重复根因合并、冲突处理或统一严重度。
- 固定 500 / 800 行阈值只能做提醒，不能替代 risk 和 dependency 分析。

**可复用精华**

- 复制其小型 orchestrator 架构；聚合端改成 validated-only、deduplicated、risk-ranked。

### 9. Google Gemini CLI `.gemini/skills/code-reviewer`

**独特机制与优势**

- 以很短的 skill 同时支持 local staged / unstaged 和 remote PR。
- remote path 会读 PR 描述与已有评论，运行项目 preflight，再按 correctness、maintainability、efficiency、security、tests 输出 verdict。
- 作为官方仓库自用 skill，触发和结构容易理解。

**遗漏与风险**

- remote path 直接 `gh pr checkout`，会改变当前 branch 和工作树；只读 review 不应这样做。
- 硬编码 `npm run preflight`，跨仓库不可移植。
- local path 对 substantial change 先询问是否跑 preflight，会打断可安全自动完成的只读工作。
- 没有固定 base、三点差分、commit history、call graph、spec、evidence contract、置信度或去重。
- pillars 是模型本来就知道的通用词，增益有限。

**可复用精华**

- 保留 target normalization；替换 checkout 为 `gh pr diff`、`git show` 或临时 worktree，并自动发现项目原生命令。

### 10. Jeffallan `code-reviewer`

**独特机制**

- 开始 review 前必须用一句话复述 PR intent，无法复述就暂停并澄清。
- spec compliance 先审阅 missing requirements、unnecessary additions、interpretation gaps，再进入 quality review。
- 六份 reference 按场景渐进加载，主 skill 保持相对精简。

**优势**

- intent checkpoint 和 spec-first 顺序很强，覆盖 scope creep。
- report template、反馈示例和 receive 流程完整，输出可执行性高。
- progressive disclosure 优于把全部教程塞进一个主文件。

**遗漏与冗余**

- allowed tools 只有 Read / Grep / Glob，主流程没有获得 diff、base/head、commit、CI 和运行测试的方法。
- 没有 history、caller/callee、状态流、独立复核或置信度。
- references 反复出现 N+1、magic number、early return、SQL injection 等通用样例，token 增益比偏低。
- spec 阶段发现不合规后要求停止 quality stage，可能让同一实现中的严重安全问题延后暴露。critical security scan 应始终先行。
- 强制 praise 会产生无决策价值的输出。

**可复用精华**

- intent sentence gate；spec gap / scope creep / interpretation 三分类。
- 主 skill 按风险加载专项 reference，避免一次性吞入全部 checklist。

### 11. Everything Claude Code security + reviewer

**独特机制与优势**

- reviewer agent 明确读取 staged / unstaged diff、完整文件、imports、dependencies 和 call sites。
- 只报告自评超过 80% 的问题，并合并同类项。
- security skill 对常见 Web 安全面、测试和部署前条目覆盖广。

**遗漏与风险**

- security skill 495 行、reviewer 237 行、command 40 行，合计 772 行，重复大量通用 checklist。
- 技术栈偏 TypeScript、Next.js、Supabase、Solana，难以称为通用。
- 多个绝对规则会制造误报：所有 token 一律禁止 localStorage、所有 cookie 一律 SameSite=Strict、所有 endpoint 一律限流、所有状态操作同时要求多种 CSRF 模式。
- CSP 示例同时允许 `unsafe-eval` 和 `unsafe-inline`，与“安全默认值”目标冲突。
- 上传校验只看浏览器 MIME 与扩展名，不足以建立文件内容信任。
- command 用函数 50 行、文件 800 行、深度 4 层等启发式直接标 HIGH 并阻断 commit，严重度容易失真。

**可复用精华**

- 显式阅读 surrounding code 与 call sites；保留 confidence filter 和同类项合并。
- 安全 pass 改成 trust boundary、attacker capability、source-to-sink、authorization invariant，避免硬编码框架处方。

### 12. Hermes `github-code-review`

**独特机制与优势**

- 支持 local pre-push、GitHub PR、`gh` 和 REST fallback。
- 对 inline comment 的 head SHA、left/right side、atomic formal review 有完整操作示例。
- 输出模板与 GitHub 操作链很完整。

**严重问题**

- setup 示例会从 `~/.git-credentials` 抽取 token；skill 不应读取或回显凭据材料。
- 指导直接 checkout PR，结束时 checkout main 并 `git branch -D pr-N`，会改变用户工作树并执行破坏性分支删除。
- PR workflow 默认发评论、approve 或 request changes，缺少显式外部写入授权门禁。
- broad text scan 查 secret 容易误报，也可能把敏感片段带入上下文。
- 480 行主文件把认证、REST 教程、review 方法和评论模板混在一起；缺少独立复核、history intent、call graph 和 spec。

**可复用精华**

- GitHub comment 的 line side、head SHA 和 atomic review 细节可以放进可选 adapter；必须保持默认只读，用户明确授权后才调用。

## 精华提炼矩阵

| 来源 | 必须吸收 | 必须修正或丢弃 |
|---|---|---|
| Anthropic | 独立发现、逐条反驳、重复过滤、默认不写外部 | diff-only、只收“所有输入都必错”的极窄 bug 定义 |
| Trail of Bits | baseline invariant、blame、blast radius、攻击可达性、覆盖边界 | 工作树 checkout、文本 caller 计数、Solidity 偏置、严重度膨胀 |
| Matt | merge-base、Spec / Standards 隔离、scope creep | 禁止去重和重排、缺少 correctness/security 专项 |
| Addy | 五轴基础层、tests-first、结构 remedy、dependency discipline | 396 行单体、失效 reference、固定 LOC 门槛 |
| Superpowers | 精准 review packet、上下文隔离、反馈处置闭环 | `HEAD~1` 默认、每个小任务强制高成本 review |
| Ponytail | delete / stdlib / native / YAGNI 最终专项 | LOC 唯一指标、脱离行为证据的删减 |
| OpenAI Codex | 14 行模块编排器、repo-local extension | unlimited findings、没有聚合复核 |
| Jeffallan | intent gate、spec gap 三分类、progressive references | 重复教程、spec fail 后完全跳过安全扫描 |
| ECC | surrounding code + call sites、置信度门槛 | 框架绝对规则、泛化安全处方、上下文膨胀 |
| Gemini | local / PR target normalization | `gh pr checkout`、硬编码 npm preflight |
| Hermes | GitHub inline adapter 的具体协议 | 凭据抓取、branch 删除、未经授权外部写入 |
| wshobson | 评论语气和严重度表达 | 大段模型已知教程、泛化 pattern 建议 |

## 最强通用 Code Review Skill 的建议骨架

### 1. Intake：固定审阅对象

- 支持 working tree、staged、branch、commit range、PR。
- 解析 immutable `base` / `head`，branch 默认用 merge-base 三点差分。
- diff 为空、ref 无效、PR head 漂移时尽早失败。
- 默认只读；禁止 checkout、stash、reset、branch delete、comment、approve、fix。

### 2. Intent 与规范

- 收集 task / issue / PR description / acceptance criteria / relevant repo instructions。
- 用一句话复述 intent；列出显式需求、边界和非目标。
- Standards 与 Spec 独立生成 finding，保留来源标签。

### 3. Risk map 与代码图

- 从 changed symbols 出发，追 callers、callees、entry points、state writes、external I/O、schema、migration、public API。
- 结构工具优先，文本搜索补漏；标注动态分派、反射和生成代码造成的盲区。
- 计算 blast radius 时结合调用方性质、数据敏感度、部署面和可逆性，不能只数文本命中。
- 删除 guard、auth、validation、retry、transaction、lock 时查 blame 和历史原因。

### 4. 并行专项发现

按风险选择，避免每次全开：

1. **Spec / behavior**：遗漏、scope creep、边界、错误路径、状态机、并发。
2. **Security / data loss**：trust boundary、authn/authz、source-to-sink、secrets、migration safety。
3. **Compatibility / integrations**：API、CLI、config、schema、serialization、rollout resume。
4. **Tests**：测试是否能在实现破坏时失败，是否覆盖触发条件和回归路径。
5. **Performance / resources**：N+1、复杂度、同步 I/O、无界操作、hot path。
6. **Simplicity**：canonical helper、stdlib/native、无用抽象、可删除概念。

每个 reviewer 接受有界 review packet，不继承作者会话历史。

### 5. Finding contract

每条候选 finding 至少包含：

```text
location: changed file + tight line range
claim: one falsifiable defect statement
introduced_by: exact diff hunk or commit
trigger: concrete input / state / call sequence
path: entry -> changed symbol -> effect
impact: observable wrong behavior or security consequence
evidence: code, spec, history, test, tool output
confidence: 0-100 with reasons
fix: smallest root-cause correction; omit if genuinely obvious
test: smallest regression case that would fail before the fix
```

缺少 trigger、path 或 observable impact 的泛化建议不能成为 blocking finding。

### 6. 独立复核与聚合

- 为每条候选 finding 启动独立 verifier，目标是反驳它：是否由本 diff 引入、是否可达、是否被现有 invariant 阻断、是否只属 lint、是否读错版本或项目规则。
- 把同一根因的多个症状合并，保留最清楚的入口和影响面。
- 严重度由 impact × likelihood × reachability × reversibility 决定，不能由类别或行数直接决定。
- 低于阈值的条目不进入 findings；证据不足但风险高的条目进入 `Needs investigation`，不伪装成已确认缺陷。
- finding 优先输出；正向反馈只保留能帮助维护者延续正确 invariant 的内容。

### 7. 收尾与反馈闭环

- 默认只返回 findings、scope、coverage limits 和 verdict。
- 用户明确授权后才发 GitHub 评论；评论前再次核对 head SHA、line side、重复项和 suggestion 完整性。
- 反馈处理记录 `accepted / rejected-with-evidence / needs-info / fixed`。
- 修复后对相关 finding 做定向复审，再做一次根因级全局复扫。

## 面向后续多轮评测的要求

静态评分只能用于挑机制。新 skill 要通过可重复 benchmark 证明增益：

### 数据集

- 至少覆盖 TypeScript、Python、Go、Rust、SQL / migration。
- bug 类别包含边界、并发、幂等、权限、数据损失、兼容性、N+1、资源泄漏、测试假阳性、过度工程。
- 每类同时放入 `buggy` 和相近但正确的 control，专门测误报。
- fixture 隐藏一部分根因信息，防止关键词命中取代代码理解。
- 加入多文件调用链、动态路由、共享 helper、删除历史 guard 和旧 bug 回归。

### 指标

- finding-level precision / recall / F1。
- blocking finding precision、严重度准确率、root-cause 去重率。
- file:line 和 causal-path 证据完整率。
- control PR 平均误报数。
- 可执行修复建议命中率。
- tokens、wall time、subagent 数量和成本。

### 对照与轮次

- 同一模型无 skill、各候选 skill、组合 skill 三组对照。
- 多模型、多随机种子；至少三轮，报告均值与离散度。
- 评分器看不到候选名称；确定性规则与人工复核分开统计。
- 公开 easy fixtures 只做回归；最终排名以隐藏集为准。
- 每轮后只针对明确失败模式调整 skill，再跑旧集防止退化。

### 通过门槛建议

- 相对最佳单一候选，隐藏集 recall 有显著提升。
- control PR 误报不增加，blocking precision 保持高位。
- 所有 Critical / High finding 都有可达路径和紧凑 file:line 证据。
- 调用链、历史回归、规格偏差、安全、性能、测试六类至少各有一组独立 hidden case。
- 上下文成本增长必须换来可测召回增益；无增益的长 reference 直接删除。

## 最终判断

建议以 **OpenAI 的小型 orchestrator** 作为形态，以 **Superpowers 的 review packet** 作为上下文协议，以 **Matt 的 Spec / Standards 隔离** 作为 intent 层，以 **Trail of Bits 的历史 / 调用链 / invariant / blast radius** 作为深度层，以 **Anthropic 的逐条独立复核** 作为 precision 层，以 **Addy 的通用五轴与依赖纪律** 作为覆盖层，最后追加 **Ponytail 的行为保真减法 pass**。

这个组合删掉了大量重复教程，只保留会改变 agent 行为、能留下证据、能被 benchmark 判定成败的机制。后续实现应维持一个短主 skill，把专项规则按风险渐进加载；新能力只有在 hidden eval 证明净增益后才进入默认流程。
