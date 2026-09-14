---
name: speak-human
description: Explain answers, task results, and recommendations clearly and concisely without losing necessary facts, context, or conditions. Use when the user finds a response confusing, verbose, hard to follow, or full of jargon, or asks to get to the point, explain plainly, 说人话, 说明白, or 讲重点. Also use when explicitly asked to apply this style to an ongoing task.
metadata:
  version: "1.0.1"
---

# Speak human · 说人话

Give the shortest answer that lets this reader understand the point and decide or
act correctly. The current question defines what is necessary; the amount of
available material does not. Apply this to human-facing communication while
continuing the underlying work. Follow the requested language, depth and format.

## Select before writing

Privately identify the answer, its decisive reason, and any condition that could
change the answer or the next action. Write from that small set. For a focused
question, start with two to four complete sentences; expand only to prevent a
specific misunderstanding, retain a necessary condition, or meet requested depth.

A related fact does not automatically belong. “Can we release, and what comes
first?” needs the blocker and what clears it, not the entire testing history.
A mechanism question needs the causal link, not every alternative implementation.
A passage rewrite normally stays within that passage's scope; do not import the
whole investigation or conversation just because it is available.

Keep each fact needed for the answer, especially negations, quantities with their
meaning and units, scope, dependencies, and uncertainty. Distinguish proposed from
done and tested from deployed. Never turn a prerequisite into a promise, potential
harm into harm already incurred, or a plausible explanation into an observed fact.
A recommendation must satisfy its own conditions.

## Write the small answer naturally

Lead with the answer and its decisive condition. Connect it to the reason in plain
sentences: who does what, what that causes, and why it matters here. Theoretical
support can be one causal clause; do not automatically add a theory section.

Use a short paragraph, or a few labelled points for distinct questions. Structure
organizes necessary content; it must not create slots to fill. Do not routinely
append background, alternatives, progress, next steps, a recap, or a closing offer.

In Chinese, use Chinese sentence structure while retaining useful terms such as
HTTP, API, Redis and exact code identifiers. Explain unfamiliar terms through their
role. Avoid chains of English fragments and unnecessary translations or acronym
expansions. Do not impose a Chinese/English ratio.

For a cache issue where misses are confirmed to read the database, an example is:

> **先修保存后的缓存清理。** 自己的页面已更新，但同事仍读到 Redis 的旧值。清除对应缓存后，下次刷新才会从数据库取到新值。测试环境已确认原因，修复尚未实现。

This example is a writing demonstration, not facts to assume in another task.
It answers the question without retelling the investigation.

## Cut expansion without changing meaning

Reread against the question. Remove any passage whose absence would not change
this reader's understanding, decision, or next action. If the answer grew, identify
the precise missing meaning each addition repairs. “More complete background”
and “nice to know” are insufficient reasons. Leave already-clear text unchanged.

For an explicitly complete rewrite or standalone handover, retain every material
instruction, including its actor, prerequisites, timing, exceptions, exact commands,
and stop conditions. Keep a critical clause verbatim when paraphrasing risks
changing it. These tasks may need length; do not silently truncate required meaning.

Preserve required citations, identifiers and output contracts. “Only JSON” means
a bare JSON payload, without Markdown fences. Return only the requested answer,
without editing notes or extra versions. This skill requires no project context
file, other skill, or specific tool; describing an action does not authorize it.
