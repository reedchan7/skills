#!/usr/bin/env python3
"""Mechanical gate for a deep-research report.

Zero dependencies (python3 stdlib only). Checks what a reader cannot verify by
skimming: citation closure, placeholder text, vague attribution, uncited
numbers, evidence dumps, required sections, and (optionally) that every cited
source was actually opened and logged in the ledger.

Usage:
    python3 check_report.py REPORT.md [--ledger LEDGER.md] [--shape SHAPE] [--json]

Exit status 1 when any FAIL is present; WARN never fails the gate.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

CITE = re.compile(r"\[(\d{1,3})\]")
SOURCE_ENTRY = re.compile(r"^\s*(?:-\s*)?\[(\d{1,3})\]\s*(.+)$")
LOCATOR = re.compile(r"https?://\S+|doi:\s*10\.\d{4,}|arxiv:\s*\d{4}\.\d{4,}|isbn[:\s]*[\d-]{10,}|file:|/[\w./-]+\.(?:pdf|md|txt|html?)", re.I)
HEADING = re.compile(r"^#{1,6}\s+(.*)$")
SOURCES_HEADING = re.compile(r"^#{1,6}\s*(?:\d+[.)]?\s*)?(sources|references|bibliography|works cited|参考文献|来源|引用)\b", re.I)
BULLET = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
TABLE_ROW = re.compile(r"^\s*\|")
CODE_FENCE = re.compile(r"^\s*```")

PLACEHOLDERS = [
    r"\bTODO\b", r"\bTBD\b", r"\bXXX\b", r"\[citation needed\]", r"\[insert[^\]]*\]",
    r"content continues", r"due to length", r"\[sections?\s+\d", r"additional citations",
    r"\bplaceholder\b", r"lorem ipsum", r"\[\d{1,3}\s*[-–]\s*\d{1,3}\]", r"待补充", r"此处省略",
]
VAGUE_ATTRIBUTION = [
    r"\bstudies (?:show|suggest|indicate)\b", r"\bresearch (?:shows|suggests|indicates)\b",
    r"\bexperts? (?:say|believe|agree|argue)\b", r"\bit is (?:widely|generally|commonly) (?:known|accepted|believed)\b",
    r"\bmany (?:people|users|analysts|researchers) (?:say|believe|report)\b", r"\bsome (?:say|argue|believe)\b",
    r"\baccording to (?:reports|sources)\b", r"\bit has been (?:shown|reported|said)\b",
    r"研究表明", r"研究显示", r"专家(?:认为|指出|表示)", r"某专家", r"业内人士", r"众所周知", r"据报道", r"据统计",
    r"据了解", r"数据显示", r"有人认为", r"普遍认为",
]
NUMBER_CLAIM = re.compile(r"(?:\d+(?:[.,]\d+)*\s*(?:%|percent|million|billion|trillion|bn|k\b|x\b|×|倍|万|亿|美元|元|USD|EUR|GBP|¥|\$|€|£|[KMGT]B\b|ms\b|seconds?\b|minutes?\b|hours?\b|days?\b|weeks?\b)|(?:\$|€|£|¥)\s*\d+(?:[.,]\d+)*)", re.I)
REVIEWER_NOTE = re.compile(r"^\s*>\s*\*\*(?:reviewer note|审阅说明|审校说明)", re.I | re.M)
TABLE_SEPARATOR = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*\|", re.M)
EVIDENCE_DUMP = [r"\(score\s+\d+,", r"^\s*\{\s*\"claim\"", r"- Uncertainty:\s*(?:single-source|thin-evidence)"]

REQUIRED_SECTIONS = {
    "any": [
        (r"(answer|summary|executive|bottom line|verdict|recommendation|结论|摘要|回答|建议)", "an answer-first section (Answer / Summary / Verdict)"),
        (r"(limitation|gap|unknown|open question|caveat|what would change|局限|未知|待解|不确定)", "a limitations / gaps / open-questions section"),
        (r"(sources|references|bibliography|参考文献|来源)", "a Sources section"),
    ],
    "decide": [(r"(criteria|标准|评估维度)", "an explicit criteria section")],
    "verify": [(r"(verdict|rating|结论|判定)", "a verdict/rating section")],
    "compare": [("__table__", "at least one comparison table (header row plus a --- separator row)")],
}

CONFIDENCE_WORDS = re.compile(
    r"\b(high|moderate|medium|low)\s+confidence\b|confidence:?\s*(high|moderate|medium|low|unable to determine)\b|置信度"
    r"|\b(almost certainly|very likely|likely|roughly even|unlikely|very unlikely|almost no chance)\b",
    re.I,
)


@dataclass(frozen=True)
class Finding:
    level: str
    check: str
    message: str
    line: int | None = None


@dataclass
class Report:
    path: Path
    lines: list[str]
    body: list[tuple[int, str]] = field(default_factory=list)
    sources: dict[int, str] = field(default_factory=dict)
    malformed_sources: list[tuple[int, str]] = field(default_factory=list)
    sources_start: int | None = None


def load(path: Path) -> Report:
    lines = path.read_text(encoding="utf-8").splitlines()
    report = Report(path=path, lines=lines)
    in_code = False
    sources_start = None
    for idx, raw in enumerate(lines, start=1):
        if CODE_FENCE.match(raw):
            in_code = not in_code
            continue
        if in_code:
            continue
        if SOURCES_HEADING.match(raw):
            sources_start = idx
            continue
        if sources_start is not None:
            if HEADING.match(raw) and not SOURCE_ENTRY.match(raw):
                sources_start = None
                report.body.append((idx, raw))
                continue
            entry = SOURCE_ENTRY.match(raw)
            if entry:
                report.sources[int(entry.group(1))] = entry.group(2).strip()
            elif raw.strip():
                report.malformed_sources.append((idx, raw.strip()))
            continue
        report.body.append((idx, raw))
    report.sources_start = sources_start
    return report


def body_text(report: Report) -> str:
    return "\n".join(text for _, text in report.body)


def check_citation_closure(report: Report) -> list[Finding]:
    cited = {int(n) for _, text in report.body for n in CITE.findall(text)}
    findings: list[Finding] = []
    if not report.sources:
        findings.append(Finding("FAIL", "sources", "no Sources section with [n] entries found"))
        if cited:
            findings.append(Finding("FAIL", "citations", f"{len(cited)} citation markers but no bibliography"))
        return findings
    missing = sorted(cited - set(report.sources))
    unused = sorted(set(report.sources) - cited)
    if missing:
        findings.append(Finding("FAIL", "citations", f"cited but absent from Sources: {missing}"))
    if unused:
        findings.append(Finding("WARN", "citations", f"listed in Sources but never cited: {unused}"))
    if not cited:
        findings.append(Finding("FAIL", "citations", "body contains no [n] citation markers"))
    return findings


def check_source_entries(report: Report) -> list[Finding]:
    findings: list[Finding] = [
        Finding("FAIL", "sources", f"malformed Sources line (one numbered entry per line, no ranges): '{text[:80]}'", idx)
        for idx, text in report.malformed_sources
    ]
    for num, entry in sorted(report.sources.items()):
        if not LOCATOR.search(entry):
            findings.append(Finding("FAIL", "sources", f"[{num}] has no URL/DOI/arXiv/file locator: {entry[:80]}"))
        if re.search(r"\b(?:etc\.?|and (?:so on|others)|\.\.\.|…)\s*$", entry, re.I):
            findings.append(Finding("FAIL", "sources", f"[{num}] ends in an elision instead of a full entry"))
    return findings


def scan_patterns(report: Report, patterns: list[str], check: str, level: str, label: str) -> list[Finding]:
    compiled = [re.compile(p, re.I | re.M) for p in patterns]
    findings: list[Finding] = []
    for idx, text in report.body:
        for pattern in compiled:
            hit = pattern.search(text)
            if hit:
                findings.append(Finding(level, check, f"{label}: '{hit.group(0)}'", idx))
                break
    return findings


def check_vague_attribution(report: Report) -> list[Finding]:
    compiled = [re.compile(p, re.I) for p in VAGUE_ATTRIBUTION]
    findings: list[Finding] = []
    for idx, text in report.body:
        for sentence in split_sentences(text):
            if any(p.search(sentence) for p in compiled) and not CITE.search(sentence):
                findings.append(Finding("FAIL", "attribution", f"vague attribution without a citation: '{sentence.strip()[:100]}'", idx))
    return findings


def check_uncited_numbers(report: Report) -> list[Finding]:
    findings: list[Finding] = []
    for idx, text in report.body:
        if HEADING.match(text) or TABLE_ROW.match(text) or text.lstrip().startswith(">"):
            continue
        for sentence in split_sentences(text):
            if NUMBER_CLAIM.search(sentence) and not CITE.search(sentence):
                findings.append(Finding("WARN", "numbers", f"quantitative claim without a citation in the sentence: '{sentence.strip()[:100]}'", idx))
    return findings


def check_bullet_ratio(report: Report) -> list[Finding]:
    prose = [t for _, t in report.body if t.strip() and not HEADING.match(t) and not TABLE_ROW.match(t)]
    if len(prose) < 20:
        return []
    bullets = sum(1 for t in prose if BULLET.match(t))
    ratio = bullets / len(prose)
    if ratio > 0.5:
        return [Finding("WARN", "prose", f"{ratio:.0%} of body lines are bullets; findings should be argued in prose, bullets kept for true lists")]
    return []


def check_required_sections(report: Report, shape: str) -> list[Finding]:
    headings = [m.group(1) for _, t in report.body if (m := HEADING.match(t))]
    heading_text = "\n".join(headings) + ("\nsources" if report.sources else "")
    findings: list[Finding] = []
    for pattern, label in REQUIRED_SECTIONS["any"] + REQUIRED_SECTIONS.get(shape, []):
        present = TABLE_SEPARATOR.search(body_text(report)) if pattern == "__table__" else re.search(pattern, heading_text, re.I)
        if not present:
            findings.append(Finding("WARN", "sections", f"missing {label}"))
    if not REVIEWER_NOTE.search("\n".join(report.lines)):
        findings.append(Finding("WARN", "sections", "missing the reviewer note block (> **Reviewer note** — …) at the top"))
    return findings


def check_confidence_language(report: Report) -> list[Finding]:
    if CONFIDENCE_WORDS.search(body_text(report)):
        return []
    return [Finding("WARN", "confidence", "no confidence or likelihood language found; every judgment should carry one")]


def check_ledger(report: Report, ledger_path: Path) -> list[Finding]:
    if not ledger_path.exists():
        return [Finding("FAIL", "ledger", f"ledger not found: {ledger_path}")]
    ledger = ledger_path.read_text(encoding="utf-8")
    ledger_urls = {normalize_url(u) for u in re.findall(r"https?://\S+", ledger)}
    findings: list[Finding] = []
    for num, entry in sorted(report.sources.items()):
        for url in re.findall(r"https?://\S+", entry):
            if normalize_url(url) not in ledger_urls:
                findings.append(Finding("FAIL", "ledger", f"[{num}] cites {url} which was never logged in the ledger (cite only what you opened)"))
    if not re.search(r"accessed|访问", ledger, re.I):
        findings.append(Finding("WARN", "ledger", "ledger has no access dates; record when each source was opened"))
    return findings


def normalize_url(url: str) -> str:
    stripped = url.rstrip(").,;>]\"'")
    stripped = re.sub(r"[?&](?:utm_[a-z]+|ref|source|fbclid|gclid)=[^&#]*", "", stripped)
    stripped = re.sub(r"#.*$", "", stripped)
    stripped = re.sub(r"^https?://(?:www\.)?", "", stripped, flags=re.I)
    return stripped.rstrip("/").lower()


def split_sentences(text: str) -> list[str]:
    return [s for s in re.split(r"(?<=[.!?。！？])\s+|(?<=[。！？])", text) if s.strip()]


def run(report_path: Path, ledger_path: Path | None, shape: str) -> list[Finding]:
    report = load(report_path)
    findings = [
        *check_citation_closure(report),
        *check_source_entries(report),
        *scan_patterns(report, PLACEHOLDERS, "placeholders", "FAIL", "placeholder text"),
        *scan_patterns(report, EVIDENCE_DUMP, "synthesis", "FAIL", "raw evidence dumped instead of synthesized"),
        *check_vague_attribution(report),
        *check_uncited_numbers(report),
        *check_bullet_ratio(report),
        *check_required_sections(report, shape),
        *check_confidence_language(report),
    ]
    if ledger_path is not None:
        findings = [*findings, *check_ledger(report, ledger_path)]
    return findings


def render(findings: list[Finding], report_path: Path) -> str:
    fails = [f for f in findings if f.level == "FAIL"]
    warns = [f for f in findings if f.level == "WARN"]
    lines = [f"check_report: {report_path}  FAIL={len(fails)}  WARN={len(warns)}"]
    for finding in sorted(findings, key=lambda f: (f.level != "FAIL", f.line or 0)):
        where = f" (line {finding.line})" if finding.line else ""
        lines.append(f"  {finding.level} [{finding.check}]{where} {finding.message}")
    lines.append("  gate: " + ("FAILED — fix every FAIL before delivery" if fails else "passed (review WARNs by hand)"))
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("report", type=Path)
    parser.add_argument("--ledger", type=Path, default=None, help="ledger.md; every cited URL must appear in it")
    parser.add_argument("--shape", choices=["explain", "compare", "decide", "verify"], default="explain")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if not args.report.exists():
        print(f"check_report: report not found: {args.report}", file=sys.stderr)
        return 2
    findings = run(args.report, args.ledger, args.shape)
    if args.json:
        print(json.dumps([finding.__dict__ for finding in findings], ensure_ascii=False, indent=2))
    else:
        print(render(findings, args.report))
    return 1 if any(f.level == "FAIL" for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
