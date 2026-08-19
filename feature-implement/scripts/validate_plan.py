#!/usr/bin/env python3
"""Validate SPEC-to-PLAN traceability and PLAN state."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys


PLACEHOLDER_RE = re.compile(r"<[^>\n]+>|\b(?:TBD|TKTK|\?\?\?)\b", re.IGNORECASE)
REQUIREMENT_RE = re.compile(r"^\s*-\s+\*\*((?:AC|RC|NFR)-\d{3})\*\*", re.MULTILINE)
SLICE_RE = re.compile(r"^-\s+\[([ xX])\]\s+\*\*(S\d+)\s+—", re.MULTILINE)
SPEC_STATUSES = {
    "Draft",
    "Approved",
    "In implementation",
    "Locally verified",
    "Ready for integration",
    "Integrated",
    "Released",
    "Declined",
}
REQUIRED_SPEC_SECTIONS = {
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
REQUIRED_PLAN_SECTIONS = {
    "Workflow gates",
    "Candidate and unrelated-work inventory",
    "Global constraints (verbatim from SPEC)",
    "Conventions inventory",
    "Baseline failure ledger",
    "Blast-radius coverage ledger",
    "Approved test migrations",
    "Slices",
    "Coverage matrix",
    "Deviations and amendments",
    "Noticed, not touched",
    "Review log",
    "Delivery report",
}


def metadata(text: str, key: str) -> str | None:
    match = re.search(rf"^-\s+{re.escape(key)}:\s*(.+)$", text, re.MULTILINE)
    return match.group(1).strip() if match else None


def section(text: str, title: str) -> str:
    match = re.search(
        rf"^##\s+{re.escape(title)}\s*$\n(.*?)(?=^##\s+|\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    return match.group(1) if match else ""


def bullets(text: str) -> list[str]:
    return [
        re.sub(r"\s+", " ", item.strip())
        for item in re.findall(r"^-\s+(.+)$", text, re.MULTILINE)
        if not item.lstrip().startswith("[")
    ]

def section_names(text: str) -> set[str]:
    return set(re.findall(r"^##\s+(.+?)\s*(?:\*\(.*\)\*)?\s*$", text, re.MULTILINE))


def exact_block(text: str, title: str) -> str:
    return "\n".join(line.rstrip() for line in section(text, title).strip().splitlines())


def spec_normative_digest(text: str) -> str | None:
    version_raw = metadata(text, "Spec version") or ""
    version_match = re.match(r"^(\d+)\b", version_raw)
    assurance = (metadata(text, "Assurance") or "").strip().lower()
    body_match = re.search(
        r"^## Problem and evidence\s*$\n(.*?)(?=^## Decision log \(append-only\)\s*$)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    if not version_match or assurance not in {"express", "standard", "deep"} or not body_match:
        return None
    body = "\n".join(line.rstrip() for line in body_match.group(1).strip().splitlines())
    payload = f"version:{version_match.group(1)}\nassurance:{assurance}\n{body}\n"
    return hashlib.sha256(payload.encode()).hexdigest()


def spec_requirement_blocks(text: str) -> list[tuple[str, str]]:
    blocks = []
    for title in (
        "Acceptance criteria",
        "Regression contract",
        "Non-functional requirements",
    ):
        match = re.search(
            rf"^##\s+{re.escape(title)}[^\n]*$\n(.*?)(?=^##\s+|\Z)",
            text,
            re.MULTILINE | re.DOTALL,
        )
        if not match:
            continue
        body = match.group(1)
        requirements = list(REQUIREMENT_RE.finditer(body))
        for index, requirement in enumerate(requirements):
            end = (
                requirements[index + 1].start()
                if index + 1 < len(requirements)
                else len(body)
            )
            blocks.append(
                (requirement.group(1), body[requirement.start() : end])
            )
    return blocks


def table_rows(block: str) -> list[list[str]]:
    rows = []
    for line in block.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if not cells or all(re.fullmatch(r":?-+:?", cell) for cell in cells):
            continue
        rows.append(cells)
    return rows


def slice_blocks(text: str) -> list[tuple[str, str, str]]:
    matches = list(SLICE_RE.finditer(text))
    blocks = []
    coverage_start = text.find("\n## Coverage matrix")
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else coverage_start
        if end < 0:
            end = len(text)
        blocks.append((match.group(1), match.group(2), text[match.start() : end]))
    return blocks


def validate(spec_path: Path, plan_path: Path, stage: str) -> dict:
    spec = spec_path.read_text()
    plan = plan_path.read_text()
    errors: list[str] = []
    warnings: list[str] = []

    spec_status = (metadata(spec, "Status") or "").strip()
    spec_assurance = (metadata(spec, "Assurance") or "").strip().lower()
    plan_assurance = metadata(plan, "Assurance")
    if plan_assurance and "|" in plan_assurance:
        plan_assurance = plan_assurance.split("|", 1)[0].strip()
    if spec_status not in SPEC_STATUSES:
        errors.append(f"invalid SPEC Status: {spec_status!r}")
    if spec_status in {"Draft", "Declined"}:
        errors.append(f"feature implementation cannot use SPEC state {spec_status}")
    if spec_assurance not in {"express", "standard", "deep"}:
        errors.append(f"invalid SPEC Assurance: {spec_assurance!r}")
    missing_spec_sections = sorted(REQUIRED_SPEC_SECTIONS - section_names(spec))
    if missing_spec_sections:
        errors.append("missing SPEC sections: " + ", ".join(missing_spec_sections))
    spec_placeholders = PLACEHOLDER_RE.findall(spec)
    if spec_placeholders:
        errors.append(f"SPEC contains {len(spec_placeholders)} placeholder(s)")
    if spec_assurance != plan_assurance:
        errors.append(
            f"Assurance mismatch: SPEC={spec_assurance!r}, PLAN={plan_assurance!r}"
        )

    spec_version_raw = metadata(spec, "Spec version") or ""
    spec_version_match = re.match(r"^(\d+)", spec_version_raw)
    spec_version = spec_version_match.group(1) if spec_version_match else None
    plan_spec_line = metadata(plan, "SPEC") or ""
    if not spec_version or not re.search(rf"\bversion:\s*{re.escape(spec_version)}\b", plan_spec_line):
        errors.append("PLAN SPEC identity does not match current Spec version")
    digest_match = re.search(
        r"\bnormative digest:\s*([0-9a-fA-F]{64})\b", plan_spec_line
    )
    actual_digest = spec_normative_digest(spec)
    if not digest_match:
        errors.append("PLAN SPEC identity requires the full normative SHA-256 digest")
    elif not actual_digest or digest_match.group(1).lower() != actual_digest:
        errors.append("PLAN SPEC normative digest does not match current contract")
    if spec_version and actual_digest:
        approval = (
            f"Approved version {spec_version} · normative digest {actual_digest} "
            "for implementation"
        )
        if approval not in spec:
            errors.append("SPEC approval is not bound to current version/normative digest")

    current_phase = metadata(plan, "Created")
    phase_match = re.search(r"Current phase:\s*([1-7])", current_phase or "")
    if not phase_match:
        errors.append("PLAN needs Current phase 1..7")

    missing_sections = sorted(REQUIRED_PLAN_SECTIONS - section_names(plan))
    if missing_sections:
        errors.append("missing PLAN sections: " + ", ".join(missing_sections))

    spec_constraints = exact_block(spec, "Global constraints")
    plan_constraints = exact_block(plan, "Global constraints (verbatim from SPEC)")
    if spec_constraints != plan_constraints:
        errors.append("PLAN Global constraints are not a byte-equivalent block copy of SPEC")

    candidate_inventory = section(plan, "Candidate and unrelated-work inventory")
    inventory_rows = [
        line for line in candidate_inventory.splitlines()
        if line.lstrip().startswith("|") and not re.match(r"^\|\s*(?:---|Path/state)", line)
    ]
    if not inventory_rows:
        errors.append("candidate/unrelated-work inventory has no concrete row")

    requirement_blocks = spec_requirement_blocks(spec)
    active_ids = [requirement_id for requirement_id, _ in requirement_blocks]
    if len(active_ids) != len(set(active_ids)):
        errors.append("SPEC contains duplicate active requirement ids")
    if not any(item.startswith("AC-") for item in active_ids):
        errors.append("active SPEC requires at least one AC")
    for requirement_id, block in requirement_blocks:
        if not re.search(r"^\s+Verify:\s+\S", block, re.MULTILINE):
            errors.append(f"{requirement_id} has no adjacent Verify method")
    regression = section(spec, "Regression contract")
    if not any(item.startswith("RC-") for item in active_ids) and "No material RC known" not in regression:
        errors.append("SPEC Regression contract needs RC items or bounded no-RC evidence")
    if spec_assurance == "deep" and not any(item.startswith("NFR-") for item in active_ids):
        errors.append("deep SPEC requires at least one active NFR")
    coverage = section(plan, "Coverage matrix")
    missing_ids = [item for item in active_ids if not re.search(rf"\b{item}\b", coverage)]
    if missing_ids:
        errors.append("coverage matrix missing: " + ", ".join(missing_ids))

    slices = SLICE_RE.findall(plan)
    if not slices:
        errors.append("PLAN has no standard '- [ ] **S# — ...**' slice checkboxes")
    duplicate_slices = sorted({item for _, item in slices if [x[1] for x in slices].count(item) > 1})
    if duplicate_slices:
        errors.append("duplicate slice ids: " + ", ".join(duplicate_slices))
    for _, slice_id, block in slice_blocks(plan):
        for field in (
            "Covers:",
            "Files:",
            "Oracle order:",
            "Affected verify:",
            "Rollback:",
            "Checkpoint:",
            "Evidence:",
        ):
            if field not in block:
                errors.append(f"{slice_id} missing field {field}")

    slices_section = section(plan, "Slices")
    if re.search(
        r"greenfield|empty[ -]repo|empty-tree|empty tree",
        f"{spec}\n{plan}",
        re.IGNORECASE,
    ):
        bootstrap_at = re.search(r"bootstrap", slices_section, re.IGNORECASE)
        product_at = re.search(r"\bAC-\d{3}\b", slices_section)
        if bootstrap_at is None or (
            product_at is not None and bootstrap_at.start() > product_at.start()
        ):
            errors.append(
                "greenfield/bootstrap PLAN must name a Bootstrap slice before any product AC"
            )

    for gate in range(1, 8):
        if not re.search(rf"^-\s+\[[ xX]\]\s+P{gate}\b", plan, re.MULTILINE):
            errors.append(f"workflow gate P{gate} is missing")

    plan_scope = plan.split("## Review log", 1)[0] if stage == "plan" else plan
    placeholders = PLACEHOLDER_RE.findall(plan_scope)
    if placeholders:
        errors.append(f"{stage} validation found {len(placeholders)} placeholder(s)")

    if stage == "delivery":
        unchecked_slices = [item for mark, item in slices if mark == " "]
        if unchecked_slices:
            errors.append("unchecked slices at delivery: " + ", ".join(unchecked_slices))
        for gate in range(1, 8):
            if not re.search(rf"^-\s+\[[xX]\]\s+P{gate}\b", plan, re.MULTILINE):
                errors.append(f"workflow gate P{gate} is not complete")
        evidence = section(plan, "Delivery report")
        evidence_rows = {
            row[0]: row
            for row in table_rows(evidence)
            if row and re.fullmatch(r"(?:AC|RC|NFR)-\d{3}", row[0])
        }
        for requirement_id in active_ids:
            row = evidence_rows.get(requirement_id)
            if row is None:
                errors.append(f"delivery evidence missing row for {requirement_id}")
                continue
            joined = " ".join(row[1:]).lower()
            if re.search(r"\b(?:fail(?:ed)?|error|unverified|not run|missing|open)\b", joined):
                errors.append(f"delivery evidence for {requirement_id} records failure/open state")
            if not re.search(r"\b(?:pass(?:ed)?|exit\s+0|green|verified|ok)\b", joined):
                errors.append(f"delivery evidence for {requirement_id} has no positive result")
            if not re.search(r"\b[0-9a-f]{64}\b", joined):
                errors.append(f"delivery evidence for {requirement_id} lacks candidate digest")
        review = section(plan, "Review log")
        review_rows = [
            row for row in table_rows(review)
            if row and re.fullmatch(r"[1-3]", row[0])
        ]
        if not review_rows:
            errors.append("delivery PLAN has no concrete review round")
        else:
            latest_review = review_rows[-1]
            if len(latest_review) < 6:
                errors.append("delivery review row is malformed; expected six columns")
            review_text = " ".join(latest_review).lower()
            if re.search(r"no review|not reviewed|needs fixes|open critical|open important", review_text):
                errors.append("delivery review row is not a passing review")
            if spec_assurance in {"standard", "deep"}:
                if len(latest_review) < 3 or latest_review[2].lower() not in {
                    "yes",
                    "true",
                    "independent",
                }:
                    errors.append(f"{spec_assurance} delivery requires independent review")
        if not re.search(r"Phase 4 frozen candidate.*[0-9a-f]{64}", candidate_inventory):
            errors.append("delivery PLAN lacks a frozen candidate digest")
        if not re.search(r"^###\s+Exploration\s*$", plan, re.MULTILINE):
            errors.append("delivery PLAN has no Exploration evidence section")
        exploration_match = re.search(
            r"^###\s+Exploration\s*$\n(.*?)(?=^###\s+|\Z)",
            plan,
            re.MULTILINE | re.DOTALL,
        )
        exploration_rows = [
            row for row in table_rows(exploration_match.group(1) if exploration_match else "")
            if row and row[0] != "Charter/oracle"
        ]
        if not exploration_rows:
            errors.append("delivery PLAN has no concrete Exploration row")
        for row in exploration_rows:
            verdict = row[-1].lower()
            if not re.search(r"\b(?:ok|pass|n/a)\b", verdict):
                errors.append("Exploration row lacks an ok/pass/N/A verdict")
            if "n/a" in verdict and len(" ".join(row[:-1]).strip()) < 12:
                errors.append("Exploration N/A row lacks a concrete reason")
        if not re.search(r"^###\s+State evidence\s*$", plan, re.MULTILINE):
            errors.append("delivery PLAN has no state evidence section")
        valid_delivery_states = {
            "Locally verified",
            "Ready for integration",
            "Integrated",
            "Released",
        }
        if spec_status not in valid_delivery_states:
            errors.append(f"delivery validation cannot close SPEC state {spec_status!r}")
        state_evidence = re.search(
            r"^###\s+State evidence\s*$\n(.*?)(?=^###\s+|\Z)",
            plan,
            re.MULTILINE | re.DOTALL,
        )
        state_text = state_evidence.group(1) if state_evidence else ""
        if spec_status and spec_status not in state_text:
            errors.append(f"state evidence does not support SPEC status {spec_status}")
        if spec_status == "Locally verified":
            locally_match = re.search(
                r"Locally verified:\s*(.+)$", state_text, re.MULTILINE
            )
            locally_text = locally_match.group(1) if locally_match else ""
            if re.search(r"\b(?:no|missing|unavailable|not verified)\b", locally_text, re.IGNORECASE):
                errors.append("Locally verified records missing/negative state evidence")
            if not re.search(
                r"\b(?:pass|green|verified|closed|0/0/0)\b",
                locally_text,
                re.IGNORECASE,
            ):
                errors.append("Locally verified lacks a positive local-gate result")
            if not re.search(r"\b[0-9a-f]{64}\b", candidate_inventory):
                errors.append("Locally verified lacks an immutable candidate digest")
        if spec_status == "Ready for integration" and not re.search(
            r"\b(?:CI|PR)\b.*\b(?:pass|green|exit 0)\b", state_text, re.IGNORECASE
        ):
            errors.append("Ready for integration lacks passing CI/PR evidence")
        if spec_status == "Integrated" and "merge" not in state_text.lower():
            errors.append("Integrated lacks merge evidence")
        if spec_status == "Released" and not re.search(
            r"deploy.*(?:smoke|observability|health)", state_text, re.IGNORECASE
        ):
            errors.append("Released lacks deployment and post-deploy evidence")

    if metadata(spec, "Status") == "Released":
        warnings.append("Released still requires external deployment evidence review")

    return {
        "spec": str(spec_path),
        "plan": str(plan_path),
        "stage": stage,
        "spec_normative_digest": actual_digest,
        "active_requirements": active_ids,
        "slices": [item for _, item in slices],
        "errors": errors,
        "warnings": warnings,
        "valid": not errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("spec", type=Path)
    parser.add_argument("plan", type=Path)
    parser.add_argument("--stage", choices=("plan", "delivery"), default="plan")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        result = validate(args.spec, args.plan, args.stage)
    except OSError as error:
        print(f"PLAN validation failed: {error}", file=sys.stderr)
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
            f"{len(result['active_requirements'])} requirements, "
            f"{len(result['slices'])} slices"
        )
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
