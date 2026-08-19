#!/usr/bin/env python3
"""Deterministically lint a generated feature SPEC."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys


STATUSES = {
    "Draft",
    "Approved",
    "In implementation",
    "Locally verified",
    "Ready for integration",
    "Integrated",
    "Released",
    "Declined",
}
ASSURANCE_LIMITS = {"express": 800, "standard": 2000, "deep": 4000}
REQUIRED_SECTIONS = {
    "Problem and evidence",
    "Outcome hypothesis",
    "Goals",
    "Non-goals",
    "Global constraints",
    "Acceptance criteria",
    "Regression contract",
    "Design decisions",
    "Testing decisions",
    "Assumptions",
    "Deferrals",
    "Limitations",
    "Decision log (append-only)",
}
PLACEHOLDER_RE = re.compile(r"<[^>\n]+>|\b(?:TBD|TKTK|\?\?\?)\b", re.IGNORECASE)
REQUIREMENT_RE = re.compile(r"^\s*-\s+\*\*((?:AC|RC|NFR)-\d{3})\*\*", re.MULTILINE)


def metadata(text: str, key: str) -> str | None:
    match = re.search(rf"^-\s+{re.escape(key)}:\s*(.+)$", text, re.MULTILINE)
    return match.group(1).strip() if match else None


def section_names(text: str) -> set[str]:
    return set(re.findall(r"^##\s+(.+?)\s*(?:\*\(.*\)\*)?\s*$", text, re.MULTILINE))


def requirement_blocks(text: str) -> list[tuple[str, str]]:
    blocks = []
    for title in (
        "Acceptance criteria",
        "Regression contract",
        "Non-functional requirements",
    ):
        section_match = re.search(
            rf"^##\s+{re.escape(title)}[^\n]*$\n(.*?)(?=^##\s+|\Z)",
            text,
            re.MULTILINE | re.DOTALL,
        )
        if not section_match:
            continue
        body = section_match.group(1)
        matches = list(REQUIREMENT_RE.finditer(body))
        for index, match in enumerate(matches):
            end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
            blocks.append((match.group(1), body[match.start() : end]))
    return blocks


def normative_digest(text: str) -> str | None:
    version_raw = metadata(text, "Spec version") or ""
    version_match = re.match(r"^(\d+)\b", version_raw)
    assurance = (metadata(text, "Assurance") or "").strip().lower()
    body_match = re.search(
        r"^## Problem and evidence\s*$\n(.*?)(?=^## Decision log \(append-only\)\s*$)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    if not version_match or assurance not in ASSURANCE_LIMITS or not body_match:
        return None
    body = "\n".join(line.rstrip() for line in body_match.group(1).strip().splitlines())
    payload = f"version:{version_match.group(1)}\nassurance:{assurance}\n{body}\n"
    return hashlib.sha256(payload.encode()).hexdigest()


def validate(path: Path) -> dict:
    text = path.read_text()
    errors: list[str] = []
    warnings: list[str] = []

    status_raw = metadata(text, "Status")
    status = status_raw.strip() if status_raw else None
    assurance_raw = metadata(text, "Assurance")
    assurance = assurance_raw.strip().lower() if assurance_raw else None
    version_raw = metadata(text, "Spec version")
    version_match = re.match(r"^(\d+)\b", version_raw or "")
    version = version_match.group(1) if version_match else None
    contract_digest = normative_digest(text)

    if status_raw and "|" in status_raw:
        errors.append("Status still contains template choices")
    if assurance_raw and "|" in assurance_raw:
        errors.append("Assurance still contains template choices")
    if status not in STATUSES:
        errors.append(f"invalid or missing Status: {status_raw!r}")
    if assurance not in ASSURANCE_LIMITS:
        errors.append(f"invalid or missing Assurance: {assurance_raw!r}")
    if not version:
        errors.append("Spec version must start with an integer")
    if not contract_digest:
        errors.append("cannot compute normative contract digest")

    missing = sorted(REQUIRED_SECTIONS - section_names(text))
    if missing:
        errors.append("missing sections: " + ", ".join(missing))

    placeholders = PLACEHOLDER_RE.findall(text)
    if placeholders:
        errors.append(f"SPEC contains {len(placeholders)} placeholder(s)")

    blocks = requirement_blocks(text)
    ids = [item[0] for item in blocks]
    duplicate_ids = sorted({item for item in ids if ids.count(item) > 1})
    if duplicate_ids:
        errors.append("duplicate requirement ids: " + ", ".join(duplicate_ids))
    if status not in {"Draft", "Declined"} and not any(item.startswith("AC-") for item in ids):
        errors.append("approved/active SPEC requires at least one AC")
    for requirement_id, block in blocks:
        if not re.search(r"^\s+Verify:\s+\S", block, re.MULTILINE):
            errors.append(f"{requirement_id} has no Verify method")

    regression_section = re.search(
        r"^## Regression contract\b(.*?)(?=^## |\Z)", text, re.MULTILINE | re.DOTALL
    )
    regression_text = regression_section.group(1) if regression_section else ""
    has_rc = any(item.startswith("RC-") for item in ids)
    if status != "Declined" and not has_rc and "No material RC known" not in regression_text:
        errors.append("Regression contract needs RC items or 'No material RC known'")

    if assurance == "deep" and status != "Declined":
        if not any(item.startswith("NFR-") for item in ids):
            errors.append("deep SPEC requires at least one active NFR")
        rollout = re.search(
            r"^## Rollout and rollback\b(.*?)(?=^## |\Z)", text, re.MULTILINE | re.DOTALL
        )
        if not rollout or len(rollout.group(1).strip()) < 40:
            errors.append("deep SPEC requires a substantive rollout/rollback section")

    if status in STATUSES - {"Draft", "Declined"} and version and contract_digest:
        approval = (
            f"Approved version {version} · normative digest {contract_digest} "
            "for implementation"
        )
        if approval not in text:
            errors.append(
                f"{status} SPEC lacks approval bound to current version/normative digest"
            )

    normative = text.split("## Decision log", 1)[0]
    word_count = len(re.findall(r"\b[\w'-]+\b", normative))
    if assurance in ASSURANCE_LIMITS and word_count > ASSURANCE_LIMITS[assurance]:
        errors.append(
            f"{assurance} SPEC has {word_count} normative words; "
            f"limit is {ASSURANCE_LIMITS[assurance]}"
        )

    if status in {"Locally verified", "Ready for integration", "Integrated", "Released"}:
        warnings.append("state evidence must also be validated against PLAN and Git/CI")

    return {
        "path": str(path),
        "status": status,
        "assurance": assurance,
        "version": version,
        "requirements": ids,
        "normative_digest": contract_digest,
        "word_count": word_count,
        "errors": errors,
        "warnings": warnings,
        "valid": not errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("spec", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        result = validate(args.spec)
    except OSError as error:
        print(f"SPEC validation failed: {error}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        for error in result["errors"]:
            print(f"ERROR: {error}")
        for warning in result["warnings"]:
            print(f"WARNING: {warning}")
        print(
            f"{'PASS' if result['valid'] else 'FAIL'}: "
            f"{len(result['requirements'])} requirements, "
            f"{result['word_count']} normative words"
        )
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
