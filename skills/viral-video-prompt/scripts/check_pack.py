#!/usr/bin/env python3
"""Mechanical gate for a viral-video prompt pack.

Zero dependencies (python3 stdlib only). Checks what a reader cannot verify by
skimming: that both variants exist for every model, that A and B are genuinely
different, that every prompt carries its settings table and stays inside the
model's real limits, that product attributes survive into every prompt, and
that the research file has sources rather than assertions.

Usage:
    python3 check_pack.py PACK_DIR [--limits LIMITS.json] [--json]

PACK_DIR is the timestamped pack directory (the one holding 00-brief.md).
--limits defaults to <script dir>/../references/models/limits.json.

Exit status 1 when any FAIL is present; WARN never fails the gate.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

PLACEHOLDERS = [
    r"\bTODO\b", r"\bTBD\b", r"\bXXX\b", r"<[a-z][^>\n]{0,60}>", r"\{\{[a-z_]+\}\}",
    r"lorem ipsum", r"\bplaceholder\b", r"待补充", r"此处省略", r"…$",
]
FENCE = re.compile(r"^\s*```")
HEADING = re.compile(r"^#{1,6}\s+(.*)$")
PROMPT_HEADING = re.compile(r"prompt|提示词", re.I)
NEGATIVE_HEADING = re.compile(r"negative|负向|反向", re.I)
SETTING_ROW = re.compile(r"^\s*\|\s*([^|]+?)\s*\|\s*(.+?)\s*\|\s*$")
REQUIRED_SETTINGS = ["model", "mode", "duration", "resolution", "audio", "prompt length"]
RESOLUTION_TOKEN = re.compile(r"\b\d{3,4}[pP]\b|\b[0-9]K\b|\bauto\b|\badaptive\b")
RATIO_TOKEN = re.compile(r"\b\d{1,2}:\d{1,2}\b|\bauto\b|\badaptive\b")
NOT_APPLICABLE = re.compile(r"n/?a|not settable|no field|follows the (?:input )?image|不适用", re.I)
TABLE_SEP = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*\|")
# A locator is anything a reader can go and open: a URL, a DOI, or a file the
# pack carries. A product photograph the user supplied is a primary source for
# product truth, and its path is a perfectly good locator.
LOCATOR = re.compile(
    r"https?://\S+"
    r"|doi:\s*10\.\d{4,}"
    r"|[\w./-]+\.(?:png|jpe?g|webp|heic|heif|gif|mp4|mov|pdf|md|txt|csv|json)\b",
    re.I,
)
NUMBERED_SOURCE = re.compile(r"^\s*(?:-\s*)?\[(\d{1,3})\]\s+\S")
CITATION = re.compile(r"\[(\d{1,3})\]")
DIFF_AXES_MIN = 4


@dataclass(frozen=True)
class Finding:
    level: str
    check: str
    message: str

    def line(self) -> str:
        return f"{self.level:<4} {self.check:<18} {self.message}"


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def strip_comments(text: str) -> str:
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)


def code_blocks(text: str) -> list[tuple[str, str]]:
    """Fenced blocks as (nearest preceding heading, body). The heading is what
    tells a prompt block apart from a negative-prompt block."""
    blocks: list[tuple[str, str]] = []
    current: list[str] | None = None
    heading = ""
    opened_under = ""
    for raw in text.splitlines():
        if FENCE.match(raw):
            if current is None:
                current, opened_under = [], heading
            else:
                blocks.append((opened_under, "\n".join(current)))
                current = None
            continue
        if current is None and (match := HEADING.match(raw)):
            heading = match.group(1).strip()
            continue
        if current is not None:
            current.append(raw)
    if current:
        blocks.append((opened_under, "\n".join(current)))
    return blocks


def prompt_block(blocks: list[tuple[str, str]]) -> str:
    """The block a user pastes into the model: the one under a Prompt heading,
    never the one under Negative prompt."""
    for heading, body in blocks:
        if NEGATIVE_HEADING.search(heading):
            continue
        if PROMPT_HEADING.search(heading):
            return body.strip()
    for heading, body in blocks:
        if not NEGATIVE_HEADING.search(heading):
            return body.strip()
    return ""


def outside_code(text: str) -> str:
    kept: list[str] = []
    inside = False
    for raw in text.splitlines():
        if FENCE.match(raw):
            inside = not inside
            continue
        if not inside:
            kept.append(raw)
    return "\n".join(kept)


def settings_table(text: str) -> dict[str, str]:
    table: dict[str, str] = {}
    for raw in outside_code(text).splitlines():
        match = SETTING_ROW.match(raw)
        if not match or TABLE_SEP.match(raw):
            continue
        key, value = match.group(1).strip().lower(), match.group(2).strip()
        if key in ("setting", "value") or set(key) <= {"-", ":", " "}:
            continue
        table.setdefault(key, value)
    return table


def load_limits(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def match_limits(limits: dict, model_key: str, settings: dict[str, str]) -> tuple[str | None, dict]:
    """Find the limits entry for a prompt file, by filename key then by the
    model/endpoint cell of its settings table."""
    if model_key in limits:
        return model_key, limits[model_key]
    declared = " ".join(settings.get(k, "") for k in ("model / endpoint", "model", "endpoint")).lower()
    for key, entry in limits.items():
        aliases = [key] + list(entry.get("aliases", []))
        if any(alias.lower() in declared for alias in aliases if alias):
            return key, entry
    return None, {}


def check_enum(name: str, model: str, settings: dict[str, str], entry: dict,
               setting_prefix: str, limits_key: str, token: re.Pattern[str]) -> list[Finding]:
    """Compare a settings cell against a documented enum. Case matters: MiniMax
    wants 768P while Wan and Seedance want 720p, and the wrong case is rejected."""
    allowed = entry.get(limits_key)
    if not allowed:
        return []
    cell = next((v for k, v in settings.items() if k.startswith(setting_prefix)), "")
    if not cell or NOT_APPLICABLE.search(cell):
        return []
    found = token.findall(cell)
    if not found:
        return []
    wrong = [f for f in found if f not in allowed]
    if not wrong:
        return []
    near = [a for a in allowed if any(f.lower() == str(a).lower() for f in wrong)]
    hint = f"; did you mean {near[0]!r}? case matters" if near else f"; allowed: {allowed}"
    return [Finding("FAIL", setting_prefix.replace(" ", "-"),
                    f"{name}: {setting_prefix} {wrong[0]!r} is not offered by {model}{hint}")]


def check_prompt_file(path: Path, limits: dict, product_terms: list[list[str]]) -> list[Finding]:
    findings: list[Finding] = []
    name = path.name
    text = strip_comments(read(path))
    if not text.strip():
        return [Finding("FAIL", "prompt-empty", f"{name}: file is empty")]

    prompt = prompt_block(code_blocks(text))
    if not prompt:
        findings.append(Finding("FAIL", "prompt-block", f"{name}: no fenced prompt block to copy"))

    settings = settings_table(text)
    missing = [key for key in REQUIRED_SETTINGS
               if not any(key in existing for existing in settings)]
    if missing:
        findings.append(Finding("FAIL", "settings", f"{name}: settings table missing {', '.join(missing)}"))

    model_key = name.rsplit("-", 1)[0]
    matched_key, entry = match_limits(limits, model_key, settings)
    if entry:
        max_chars = entry.get("max_prompt_chars")
        if isinstance(max_chars, int) and len(prompt) > max_chars:
            findings.append(Finding("FAIL", "prompt-length",
                                    f"{name}: prompt is {len(prompt)} chars, over the {matched_key} limit of {max_chars}"))
        durations = entry.get("durations")
        duration_cell = next((v for k, v in settings.items() if k.startswith("duration")), "")
        if durations and duration_cell:
            found = re.findall(r"\d+(?:\.\d+)?", duration_cell)
            allowed = {str(d) for d in durations}
            if found and not any(f in allowed for f in found):
                findings.append(Finding("FAIL", "duration",
                                        f"{name}: duration {duration_cell!r} is not one of {durations} for {matched_key}"))
        findings.extend(check_enum(name, matched_key, settings, entry, "resolution",
                                   "resolutions", RESOLUTION_TOKEN))
        findings.extend(check_enum(name, matched_key, settings, entry, "aspect ratio",
                                   "aspect_ratios", RATIO_TOKEN))
        if entry.get("negative_prompt") is False and re.search(r"^#+\s*negative prompt", text, re.I | re.M):
            findings.append(Finding("FAIL", "negative-prompt",
                                    f"{name}: {matched_key} has no negative-prompt field, but the file supplies one"))
        reasons = entry.get("forbidden_reasons", {})
        for forbidden in entry.get("forbidden_in_prompt", []):
            hit = re.search(forbidden, prompt, re.I)
            if hit:
                why = reasons.get(forbidden, f"not supported by {matched_key}")
                findings.append(Finding("WARN", "model-syntax",
                                        f"{name}: prompt contains {hit.group(0)!r} — {why}"))
    else:
        findings.append(Finding("WARN", "limits",
                                f"{name}: no limits entry matched; prompt length {len(prompt)} chars unchecked"))

    for pattern in PLACEHOLDERS:
        if re.search(pattern, prompt, re.I | re.M):
            findings.append(Finding("FAIL", "placeholder",
                                    f"{name}: prompt still holds placeholder text matching {pattern!r}"))
            break

    lowered = prompt.lower()
    absent = [spellings[0] for spellings in product_terms
              if not any(s.lower() in lowered for s in spellings)]
    if absent:
        findings.append(Finding("FAIL", "product-truth",
                                f"{name}: prompt drops product attribute(s): {', '.join(absent)}"))

    if not re.search(r"^#+\s*(why this works|为什么有效)", text, re.I | re.M):
        findings.append(Finding("WARN", "rationale", f"{name}: no 'Why this works' section"))
    if not re.search(r"^#+\s*(if the result is off|如果效果不对)", text, re.I | re.M):
        findings.append(Finding("WARN", "recovery", f"{name}: no 'If the result is off' section"))
    return findings


def difference_section(text: str) -> str:
    """Only the difference matrix, so a three-column table elsewhere in the
    concepts file cannot pad the count."""
    lines = text.splitlines()
    start = next((i for i, raw in enumerate(lines)
                  if (m := HEADING.match(raw)) and re.search(r"difference|差异", m.group(1), re.I)), None)
    if start is None:
        return text
    level = len(lines[start]) - len(lines[start].lstrip("#"))
    for i in range(start + 1, len(lines)):
        if (m := HEADING.match(lines[i])) and (len(lines[i]) - len(lines[i].lstrip("#"))) <= level:
            return "\n".join(lines[start:i])
    return "\n".join(lines[start:])


def check_difference_matrix(text: str) -> list[Finding]:
    """A pack may carry two concepts or more — the user decides the shape. The
    matrix is one axis column plus one column per concept, so accept any width
    of three or more and count an axis as differing when its concept cells are
    not all the same."""
    rows: list[list[str]] = []
    width = 0
    for raw in difference_section(text).splitlines():
        if not raw.strip().startswith("|") or TABLE_SEP.match(raw):
            continue
        cells = [c.strip() for c in raw.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue
        if cells[0].lower() in ("axis", "维度") or cells[1].lower().startswith("concept "):
            width = max(width, len(cells))
            continue
        rows.append(cells)
    if not rows:
        return [Finding("FAIL", "difference",
                        "02-concepts.md: no difference matrix found — expected one axis column "
                        "plus one column per concept")]
    width = width or max(len(r) for r in rows)
    rows = [r for r in rows if len(r) == width]
    if not rows:
        return [Finding("FAIL", "difference", "02-concepts.md: difference matrix rows disagree on width")]

    def filled(cell: str) -> bool:
        return bool(cell) and not re.fullmatch(r"[…\-\s]*", cell)

    differing = []
    for r in rows:
        vals = [c for c in r[1:] if filled(c)]
        if len(vals) == width - 1 and len({v.lower() for v in vals}) > 1:
            differing.append(r)
    if len(differing) < DIFF_AXES_MIN:
        n = width - 1
        return [Finding("FAIL", "difference",
                        f"02-concepts.md: only {len(differing)} axes differ across the "
                        f"{n} concepts; {DIFF_AXES_MIN} required")]
    return []


HOOK_TESTS = (
    ("generic-swap", r"generic[-\s]?swap"),
    ("competitor-frame", r"competitor[-\s]?frame"),
    ("glance", r"\bglance\b"),
    ("hook restatement", r"hook restatement|restatement"),
)
VERDICT = re.compile(r"\*\*(pass|fail)\*\*|(?<![A-Za-z])(pass|fail)(?![A-Za-z])", re.I)
NO_CHANGE = re.compile(
    r"no test failed|nothing (?:was )?(?:changed|escalated)|nothing changed|n/?a\b",
    re.I)


def logical_bullets(body: str) -> list[str]:
    """Join a markdown bullet with its continuation lines. Physical lines are an
    artefact of wrapping; a verdict and its reason are one statement."""
    out: list[str] = []
    for raw in body.splitlines():
        if re.match(r"\s*[-*+]\s|\s*\|", raw) or not out:
            out.append(raw.strip())
        elif raw.strip():
            out[-1] = out[-1] + " " + raw.strip()
        else:
            out.append("")
    return out


def check_hook_tests(text: str) -> list[Finding]:
    """The audit that produced this check found the four tests being run as
    documentation: a verdict recorded as a failure, then shipped unchanged. So
    the tests are enforced here rather than trusted.

    Two concepts, four verdicts each. A missing verdict is a FAIL because an
    unwritten test is an unrun test. A `fail` verdict is legal — a failure is
    allowed, that is the point of a gate — but only alongside an `On a fail`
    line that records what changed, and a line saying nothing changed does not
    count as recording it."""
    findings: list[Finding] = []
    parts = re.split(r"^##+\s+.*?\bConcept\s+([A-Z])\b.*$", text, flags=re.M | re.I)
    # split() yields [preamble, 'A', body, 'B', body, ...]
    bodies = {parts[i].upper(): parts[i + 1] for i in range(1, len(parts) - 1, 2)}
    if len(bodies) < 2:
        return [Finding("WARN", "hook-tests",
                        "02-concepts.md: found fewer than two 'Concept <letter>' headings, "
                        "so the four hook-test verdicts were not checked")]

    for letter in sorted(bodies):
        body = bodies[letter]
        failed: list[str] = []
        for name, pattern in HOOK_TESTS:
            named = [ln for ln in logical_bullets(body)
                     if re.search(pattern, ln, re.I) and re.search(r"test|restatement", ln, re.I)]
            if not named:
                findings.append(Finding("FAIL", "hook-tests",
                                        f"02-concepts.md: Concept {letter} has no {name} verdict; "
                                        "an unwritten test is an unrun test"))
                continue
            if name == "hook restatement":
                continue
            # A concept file discusses its own tests in prose as well as
            # recording them, so take the line that carries a verdict rather
            # than the first line that mentions the test.
            verdict = None
            for row in named:
                verdict = VERDICT.search(row)
                if verdict:
                    break
            if verdict is None and name == "glance":
                # A product film is not competing in a feed, so n/a is honest —
                # but only spelled out. A bare "n/a" is the quiet waiver the test
                # exists to prevent, so require a reason on the same line.
                na = next((r for r in named
                           if re.search(r"\bn/?a\b|not applicable", r, re.I) and len(r) > 120), None)
                if na:
                    continue
            if verdict is None:
                findings.append(Finding("FAIL", "hook-tests",
                                        f"02-concepts.md: Concept {letter}'s {name} line records no "
                                        "literal pass or fail"))
            elif (verdict.group(1) or verdict.group(2)).lower() == "fail":
                failed.append(name)

        for label, pattern in (("target metric", r"target metric"),
                               ("audience segment", r"audience segment"),
                               ("proof", r"\*\*the proof\*\*|^\s*[-*]\s*\*\*proof\*\*")):
            if not any(re.search(pattern, ln, re.I | re.M) for ln in logical_bullets(body)):
                findings.append(Finding("FAIL", "concept-decisions",
                                        f"02-concepts.md: Concept {letter} names no {label}; "
                                        "the metric selects the ending, the segment selects "
                                        "what must be shown, and the proof is what the clip settles"))

        # The count may be labelled "Change density" or simply stated in prose
        # under the change map. Either is a statement; only silence is not.
        density = next((ln for ln in logical_bullets(body)
                        if re.search(r"change density", ln, re.I)
                        or (re.search(r"largest gap", ln, re.I)
                            and re.search(r"\bchanges?\b", ln, re.I))), None)
        if density is None:
            findings.append(Finding("WARN", "change-density",
                                    f"02-concepts.md: Concept {letter} states no change density; "
                                    "a change map without a count is a film brief"))
        else:
            gap = re.search(r"largest gap\s*([0-9]+(?:\.[0-9]+)?)\s*s", density, re.I)
            count = re.search(r"([0-9]+)\s*changes", density, re.I)
            if gap and float(gap.group(1)) > 3.0:
                findings.append(Finding("FAIL", "change-density",
                                        f"02-concepts.md: Concept {letter}'s largest gap is "
                                        f"{gap.group(1)} s; nothing may hold longer than 3 s"))
            if count and int(count.group(1)) < 3:
                findings.append(Finding("FAIL", "change-density",
                                        f"02-concepts.md: Concept {letter} has {count.group(1)} "
                                        "changes; five seconds wants three and fifteen wants seven to nine"))

        on_fail = next((ln for ln in logical_bullets(body)
                        if re.search(r"on a fail", ln, re.I)), None)
        if failed and (on_fail is None or NO_CHANGE.search(on_fail)):
            findings.append(Finding("FAIL", "hook-tests",
                                    f"02-concepts.md: Concept {letter} failed {', '.join(failed)} "
                                    "and its 'On a fail' line records no redesign or escalation; "
                                    "recording a failure is not acting on it"))
    return findings


RUNG_SERVICE = {"3": "apify", "2": "brave", "1": "tavily"}


def check_ledger(pack: Path, research_text: str) -> list[Finding]:
    """A claimed degradation rung has to be backed by calls that actually
    happened. This is the check that catches a pack asserting it used a scraper
    it never called."""
    findings: list[Finding] = []
    path = pack / "requests" / "ledger.jsonl"
    entries: list[dict] = []
    if path.is_file():
        for line in read(path).splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                findings.append(Finding("WARN", "ledger", f"ledger.jsonl: unparseable line {line[:60]!r}"))
    elif research_text:
        findings.append(Finding("WARN", "ledger",
                                "no requests/ledger.jsonl: which external calls ran cannot be checked"))
        return findings

    services = {str(e.get("service", "")).lower() for e in entries}

    # An Apify line without its run id cannot be verified against the account,
    # which is the whole point of the ledger. Budget-check calls are exempt:
    # they start no run.
    for entry in entries:
        if str(entry.get("service", "")).lower() != "apify":
            continue
        op = str(entry.get("op", ""))
        if re.search(r"users/me|/limits|usage", op, re.I):
            continue
        if not entry.get("run_id"):
            findings.append(Finding("FAIL", "ledger",
                                    f"ledger.jsonl: apify line {op!r} has no run_id, so the run and its "
                                    "cost cannot be verified against the account"))

    unsaved = [str(e.get("op", "")) for e in entries
               if not e.get("saved")
               and str(e.get("service", "")).lower() in {"apify", "tavily", "brave"}
               and not re.search(r"users/me|/limits|usage", str(e.get("op", "")), re.I)]
    if unsaved:
        findings.append(Finding("WARN", "ledger",
                                f"{len(unsaved)} ledger line(s) name no saved response "
                                f"(first: {unsaved[0]!r}); the numbers they bought cannot be re-checked "
                                "without paying again"))

    for entry in entries:
        saved = entry.get("saved")
        if saved and not (path.parent / str(saved)).is_file():
            findings.append(Finding("FAIL", "ledger",
                                    f"ledger.jsonl: line names saved response {saved!r}, which is not in "
                                    "requests/ — paid data that is not on disk gets bought twice"))

    stamps = [str(e.get("ts", "")) for e in entries if e.get("ts")]
    if stamps and path.is_file():
        written = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
        for stamp in stamps:
            try:
                seen = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
            except ValueError:
                continue
            if seen > written + timedelta(minutes=2):
                findings.append(Finding("FAIL", "ledger",
                                        f"ledger.jsonl: entry timestamped {stamp} is later than the file's own "
                                        "last write, so it was not observed — take ts from `date -u` at call time"))
                break
    claimed = re.search(r"rung\s*([0-3])", research_text, re.I)
    if claimed and entries:
        rung = claimed.group(1)
        needed = RUNG_SERVICE.get(rung)
        if needed and needed not in services:
            findings.append(Finding("FAIL", "ledger",
                                    f"01-research.md claims rung {rung} but the ledger records no {needed} call; "
                                    f"services actually called: {sorted(s for s in services if s) or 'none'}"))
    return findings


def check_research(text: str) -> list[Finding]:
    findings: list[Finding] = []
    body = outside_code(strip_comments(text))
    entries = {int(m.group(1)) for line in body.splitlines() if (m := NUMBERED_SOURCE.match(line))}
    cited = {int(n) for n in CITATION.findall(body)}
    if not entries:
        findings.append(Finding("FAIL", "sources", "01-research.md: no numbered Sources entries"))
    dangling = sorted(cited - entries)
    if dangling:
        findings.append(Finding("FAIL", "sources",
                                f"01-research.md: citation(s) {dangling} have no Sources entry"))
    for line in body.splitlines():
        match = NUMBERED_SOURCE.match(line)
        if match and not LOCATOR.search(line):
            findings.append(Finding("WARN", "sources",
                                    f"01-research.md: source [{match.group(1)}] has no locator — "
                                    "give it a URL, a DOI, or the path of a file in the pack"))
    if not re.search(r"^\s*>\s*\*\*(reviewer note|审阅说明)", body, re.I | re.M):
        findings.append(Finding("WARN", "reviewer-note", "01-research.md: no reviewer note"))
    if not re.search(r"^#+.*(gap|缺口|未能验证)", body, re.I | re.M):
        findings.append(Finding("WARN", "gaps", "01-research.md: no gaps section"))
    return findings


def product_terms(brief_text: str) -> list[list[str]]:
    """Attributes the brief marked as must-appear, each returned as the set of
    spellings that satisfy it. Backticked terms on the 'Given attributes' line
    are the attributes; a `Must show` line adds the features the pack promised to
    put on screen; an optional 'Attribute equivalents' line supplies the other
    accepted spellings, so a Chinese attribute can be satisfied by its English
    rendering in an English prompt.

        - **Given attributes**: `藏青`, `10寸`, `午餐包`
        - **Must show**: `拉链`, `侧网袋`
        - **Attribute equivalents**: 藏青 = navy = deep blue; 10寸 = 10-inch = 25 cm
    """
    body = strip_comments(brief_text)
    terms: list[str] = []
    for line in body.splitlines():
        if re.search(r"(given attributes|给定属性|must show|必须出现)", line, re.I):
            terms.extend(re.findall(r"`([^`]+)`", line))
    terms = [t.strip() for t in terms
             if t.strip() and "<" not in t and ">" not in t and not t.endswith(".py")]

    equivalents: dict[str, list[str]] = {}
    for line in body.splitlines():
        if not re.search(r"(attribute equivalents|等价写法|同义)", line, re.I):
            continue
        for group in re.split(r"[;；]", line.split(":", 1)[-1]):
            spellings = [s.strip(" `*") for s in re.split(r"[=＝]", group) if s.strip(" `*")]
            if len(spellings) > 1:
                equivalents[spellings[0]] = spellings
    return [equivalents.get(t, [t]) for t in terms]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("pack")
    parser.add_argument("--limits", default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--lengths", action="store_true",
                        help="print each prompt's character count against its limit and exit, "
                             "so the settings table can be filled without a guess-and-retry loop")
    args = parser.parse_args()

    pack = Path(args.pack).expanduser()
    if not pack.is_dir():
        print(f"not a directory: {pack}", file=sys.stderr)
        return 2
    limits_path = Path(args.limits).expanduser() if args.limits else Path(__file__).resolve().parent.parent / "references" / "models" / "limits.json"
    limits = load_limits(limits_path)

    if args.lengths:
        for path in sorted((pack / "prompts").glob("*.md")):
            text = strip_comments(read(path))
            prompt = prompt_block(code_blocks(text))
            key, entry = match_limits(limits, path.stem.rsplit("-", 1)[0], settings_table(text))
            cap = entry.get("max_prompt_chars")
            print(f"{path.name:<24} {len(prompt):>5} chars"
                  + (f" of {cap} for {key}" if cap else f"  (no published cap for {key or '?'})"))
        return 0

    findings: list[Finding] = []
    brief = pack / "00-brief.md"
    research = pack / "01-research.md"
    concepts = pack / "02-concepts.md"
    prompts_dir = pack / "prompts"

    for required in (brief, research, concepts):
        if not required.is_file():
            findings.append(Finding("FAIL", "structure", f"missing {required.name}"))
    if not prompts_dir.is_dir():
        findings.append(Finding("FAIL", "structure", "missing prompts/ directory"))
    if not (pack / "README.md").is_file():
        findings.append(Finding("WARN", "structure", "no README.md: the pack does not explain itself"))

    terms = product_terms(read(brief))
    if not terms:
        findings.append(Finding("WARN", "product-truth",
                                "00-brief.md: no `backticked` attributes under 'Given attributes'; product-truth check skipped"))

    prompt_files = sorted(prompts_dir.glob("*.md")) if prompts_dir.is_dir() else []
    if not prompt_files:
        findings.append(Finding("FAIL", "structure", "prompts/ holds no .md files"))
    models: dict[str, set[str]] = {}
    for path in prompt_files:
        if path.name == "COMMON.md":
            continue  # the shared-notes file, by design; it is not a variant
        stem = path.stem
        # Two supported shapes. The pair shape is one file per model per variant,
        # `<model>-A.md`. The concept shape is one file per concept holding that
        # concept's segments for a single model, `<LETTER>-<slug>.md` — which is
        # what an assembled multi-segment video needs, because a 20-40 s video is
        # several generations and they belong in one file.
        concept_shape = re.match(r"^([A-Z])-(.+)$", stem)
        if concept_shape and not stem.rsplit("-", 1)[1].upper() in ("A", "B"):
            variant = concept_shape.group(1).upper()
            model = "concept-file"
        elif "-" in stem and stem.rsplit("-", 1)[1].upper() in ("A", "B"):
            model, variant = stem.rsplit("-", 1)
        else:
            findings.append(Finding("FAIL", "naming",
                                    f"{path.name}: expected <model>-A.md for a pair pack, "
                                    "or <LETTER>-<slug>.md for a concept-per-file pack"))
            continue
        models.setdefault(model, set()).add(variant.upper())
        findings.extend(check_prompt_file(path, limits, terms))
    for model, variants in sorted(models.items()):
        # At least a pair, and any further concepts must be a contiguous run from
        # A — the user decides how many bets a pack carries, but an orphan D with
        # no C is a missing file.
        expected = {chr(ord("A") + i) for i in range(len(variants))}
        if len(variants) < 2:
            findings.append(Finding("FAIL", "ab-pair",
                                    f"{model}: has {sorted(variants)}, needs at least A and B"))
        elif variants != expected:
            findings.append(Finding("FAIL", "ab-pair",
                                    f"{model}: has {sorted(variants)}, expected the contiguous run "
                                    f"{sorted(expected)} — a concept letter is missing"))

    if concepts.is_file():
        concepts_text = strip_comments(read(concepts))
        findings.extend(check_difference_matrix(concepts_text))
        findings.extend(check_hook_tests(concepts_text))
    if research.is_file():
        research_text = read(research)
        findings.extend(check_research(research_text))
        findings.extend(check_ledger(pack, research_text))

    fails = [f for f in findings if f.level == "FAIL"]
    warns = [f for f in findings if f.level == "WARN"]
    if args.json:
        print(json.dumps({"pack": str(pack), "fail": len(fails), "warn": len(warns),
                          "findings": [f.__dict__ for f in findings]}, ensure_ascii=False, indent=2))
    else:
        for finding in fails + warns:
            print(finding.line())
        variants = sum(len(v) for v in models.values())
        print(f"\n{len(models)} model(s), {variants} prompt file(s) · FAIL={len(fails)} WARN={len(warns)}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
