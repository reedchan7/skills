#!/usr/bin/env python3
"""Turn ledger-id citations into gapless [n] markers and a generated Sources list.

Write the draft citing ledger ids — `[S12]`, `[S3][S12]`, or `[S3, S12]` — and
run this once at synthesis. Numbers are assigned in order of first appearance;
the Sources section is built from the ledger's S lines, so a URL can only be
cited if it was logged. Zero dependencies.

Usage:
    python3 renumber_citations.py DRAFT.md LEDGER.md [-o REPORT.md] [--contributed FILE]

`--contributed FILE` is an optional text file with lines `S12: one-line note`
appended to the matching Sources entry as "— contributed: …"; without it the
ledger line's trailing notes field is used when present.

Exit status 1 when the draft cites an id the ledger does not hold, or whose
provenance is model-knowledge or snippet-only.
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

DRAFT_CITE = re.compile(r"\[(S\d+(?:\s*[,;]\s*S\d+)*)\]")
S_LINE = re.compile(r"^\s*-\s*(S\d+)\s*\|\s*(.*)$")
SOURCES_HEADING = re.compile(r"^#{1,6}\s*(sources|references|参考文献|来源)\s*$", re.I | re.M)
FIELD = re.compile(r"^\s*(type|tier|published|accessed|stance/notes|notes|note)\s*:\s*(.*)$", re.I)
PROVENANCE = {"fetched", "digest", "snippet-only", "user-provided", "model-knowledge"}


@dataclass(frozen=True)
class Source:
    sid: str
    title: str
    locator: str
    published: str
    accessed: str
    provenance: str
    notes: str


def parse_ledger(text: str) -> dict[str, Source]:
    sources: dict[str, Source] = {}
    for line in text.splitlines():
        match = S_LINE.match(line)
        if not match:
            continue
        sid, rest = match.group(1), match.group(2)
        parts = [p.strip() for p in rest.split("|")]
        title = parts[0] if parts else ""
        locator = parts[1] if len(parts) > 1 else ""
        fields = {"published": "", "accessed": "", "notes": ""}
        provenance = ""
        for part in parts[2:]:
            lowered = part.lower()
            if lowered in PROVENANCE:
                provenance = lowered
                continue
            field = FIELD.match(part)
            if field:
                key = field.group(1).lower()
                key = "notes" if key.startswith(("stance", "note")) else key
                if key in fields:
                    fields[key] = field.group(2).strip()
        sources[sid] = Source(sid, title, locator, fields["published"], fields["accessed"], provenance, fields["notes"])
    return sources


def parse_contributed(path: Path | None) -> dict[str, str]:
    if path is None or not path.exists():
        return {}
    pairs = (line.split(":", 1) for line in path.read_text(encoding="utf-8").splitlines() if ":" in line)
    return {sid.strip(): note.strip() for sid, note in pairs}


def cited_ids_in_order(draft: str) -> list[str]:
    ordered: list[str] = []
    for match in DRAFT_CITE.finditer(draft):
        for sid in re.findall(r"S\d+", match.group(1)):
            if sid not in ordered:
                ordered.append(sid)
    return ordered


def renumber(draft: str, numbering: dict[str, int]) -> str:
    def replace(match: re.Match[str]) -> str:
        ids = re.findall(r"S\d+", match.group(1))
        return "".join(f"[{numbering[sid]}]" for sid in ids)

    return DRAFT_CITE.sub(replace, draft)


def strip_existing_sources(text: str) -> str:
    match = SOURCES_HEADING.search(text)
    return text[: match.start()].rstrip() + "\n" if match else text.rstrip() + "\n"


def sources_section(order: list[str], ledger: dict[str, Source], contributed: dict[str, str]) -> str:
    lines = ["## Sources", ""]
    for number, sid in enumerate(order, start=1):
        source = ledger[sid]
        published = f", {source.published}" if source.published else ""
        accessed = f" (accessed {source.accessed})" if source.accessed else ""
        note = contributed.get(sid) or source.notes
        contributed_text = f" — contributed: {note}" if note else ""
        lines.append(f"[{number}] {source.title}{published}. {source.locator}{accessed}{contributed_text}")
    return "\n".join(lines) + "\n"


def problems(order: list[str], ledger: dict[str, Source]) -> list[str]:
    missing = [sid for sid in order if sid not in ledger]
    weak = [sid for sid in order if sid in ledger and ledger[sid].provenance in {"model-knowledge", "snippet-only"}]
    no_locator = [sid for sid in order if sid in ledger and not ledger[sid].locator]
    return [
        *(f"cited but not in ledger: {sid}" for sid in missing),
        *(f"cited with provenance {ledger[sid].provenance}; open it or tag the sentence instead of citing: {sid}" for sid in weak),
        *(f"ledger line has no locator: {sid}" for sid in no_locator),
    ]


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("draft", type=Path)
    parser.add_argument("ledger", type=Path)
    parser.add_argument("-o", "--output", type=Path, default=None, help="default: report.md beside the draft")
    parser.add_argument("--contributed", type=Path, default=None)
    args = parser.parse_args(argv)

    draft = args.draft.read_text(encoding="utf-8")
    ledger = parse_ledger(args.ledger.read_text(encoding="utf-8"))
    order = cited_ids_in_order(draft)
    issues = problems(order, ledger)
    if issues:
        print("renumber_citations: refusing to write\n  " + "\n  ".join(issues), file=sys.stderr)
        return 1
    numbering = {sid: index for index, sid in enumerate(order, start=1)}
    body = strip_existing_sources(renumber(draft, numbering))
    output = args.output or args.draft.with_name("report.md")
    output.write_text(body + "\n" + sources_section(order, ledger, parse_contributed(args.contributed)), encoding="utf-8")
    print(f"renumber_citations: wrote {output} with {len(order)} sources")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
