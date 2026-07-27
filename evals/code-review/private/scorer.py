#!/usr/bin/env python3
"""Private deterministic scorer for contextual review submissions."""

from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path, PurePosixPath
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
ORACLE_PATH = Path(__file__).with_name("oracle.json")
SEVERITY_WEIGHTS = {"critical": 5.0, "high": 3.0, "medium": 2.0, "low": 1.0}
EVIDENCE_PATTERN = re.compile(r"(?P<path>[A-Za-z0-9_.\-/]+):(?P<line>[0-9]+)")

# Concept coverage is a bag-of-tokens intersection with no polarity: a body that
# keeps the oracle's keywords while asserting the opposite conclusion still
# matches. These phrases catch the explicit form of that inversion. They are a
# guard, not a semantic judge — see adjudicate.py for the real check.
NO_DEFECT_PHRASES = (
    "no defect",
    "not a defect",
    "no bug",
    "not a bug",
    "no issue",
    "not an issue",
    "no vulnerability",
    "no actual problem",
    "no action is needed",
    "no action is required",
    "no action needed",
    "no action required",
    "no change is needed",
    "no change is required",
    "nothing to fix",
    "works as intended",
    "working as intended",
    "behaves correctly",
    "behaves as documented",
    "is safe and correct",
    "safe and correct",
    "correct and safe",
    "this is fine",
    "not a real finding",
)


def ratio(numerator: float, denominator: float) -> float:
    return round(numerator / denominator, 6) if denominator else 0.0


def metric(tp: float, fp: float, fn: float) -> dict[str, float]:
    precision = ratio(tp, tp + fp)
    recall = ratio(tp, tp + fn)
    f1 = ratio(2 * precision * recall, precision + recall)
    return {"precision": precision, "recall": recall, "f1": f1}


def normalized_text(value: str) -> str:
    return " ".join(re.findall(r"[a-z0-9_]+", value.lower()))


def normalized_path(value: str) -> str:
    value = value.replace("\\", "/")
    while value.startswith("./"):
        value = value[2:]
    return value


def phrase_hit(text_tokens: set[str], alternative: str) -> bool:
    tokens = set(normalized_text(alternative).split())
    if not tokens:
        return False
    required = 1.0 if len(tokens) <= 2 else 0.75
    return len(tokens & text_tokens) / len(tokens) >= required


def no_defect_phrases(candidate: dict) -> list[str]:
    """Explicit no-defect verdicts in a finding body, which cannot be a finding."""
    text = normalized_text(f"{candidate['title']} {candidate['body']}")
    padded = f" {text} "
    return [phrase for phrase in NO_DEFECT_PHRASES if f" {normalized_text(phrase)} " in padded]


def concept_coverage(candidate: dict, truth: dict) -> float:
    text_tokens = set(normalized_text(f"{candidate['title']} {candidate['body']}").split())
    groups = truth["concept_groups"]
    hits = sum(any(phrase_hit(text_tokens, alternative) for alternative in group) for group in groups)
    return hits / len(groups) if groups else 1.0


def parsed_evidence(candidate: dict) -> set[tuple[str, int]]:
    parsed = set()
    for entry in candidate["evidence"]:
        for match in EVIDENCE_PATTERN.finditer(entry):
            parsed.add((normalized_path(match.group("path")), int(match.group("line"))))
    return parsed


def close_line(line: int, start: int, end: int, tolerance: int = 3) -> bool:
    return start - tolerance <= line <= end + tolerance


def evidence_hits(candidate: dict, truth: dict) -> int:
    evidence = parsed_evidence(candidate)
    return sum(
        any(
            path == anchor["file"] and close_line(line, anchor["line_start"], anchor["line_end"])
            for path, line in evidence
        )
        for anchor in truth["causal_anchors"]
    )


def candidate_location(candidate: dict, truth: dict) -> tuple[str, float, float]:
    path = normalized_path(candidate["file"])
    line = candidate["line"]
    if path == truth["file"]:
        if close_line(line, truth["line_start"], truth["line_end"], 0):
            return "root", 0.38, 0.17
        if close_line(line, truth["line_start"], truth["line_end"], 3):
            return "root-near", 0.38, 0.13
        if close_line(line, truth["line_start"], truth["line_end"], 10):
            return "root-near", 0.38, 0.07
    for anchor in truth["causal_anchors"]:
        if path == anchor["file"] and close_line(line, anchor["line_start"], anchor["line_end"]):
            return "anchor", 0.28, 0.12
    return "none", 0.0, 0.0


def pair_score(candidate: dict, truth: dict) -> dict | None:
    kind, file_score, line_score = candidate_location(candidate, truth)
    concepts = concept_coverage(candidate, truth)
    anchors = evidence_hits(candidate, truth)
    anchor_ratio = anchors / len(truth["causal_anchors"]) if truth["causal_anchors"] else 1.0
    score = file_score + line_score + 0.35 * concepts + 0.10 * anchor_ratio
    if kind == "none" or concepts < 0.5 or score < 0.55:
        return None
    return {
        "score": score,
        "location_kind": kind,
        "concept_coverage": concepts,
        "evidence_hits": anchors,
    }


def validate_submission(submission: object, cases: list[dict]) -> dict[str, list[dict]]:
    if not isinstance(submission, dict) or set(submission) != {"reviews"}:
        raise ValueError("submission must be an object containing only reviews")
    reviews = submission["reviews"]
    if not isinstance(reviews, list):
        raise ValueError("reviews must be an array")
    expected = {case["case_id"] for case in cases}
    by_case: dict[str, list[dict]] = {}
    for review in reviews:
        if not isinstance(review, dict) or set(review) != {"case_id", "findings"}:
            raise ValueError("each review must contain only case_id and findings")
        case_id = review["case_id"]
        if case_id not in expected or case_id in by_case:
            raise ValueError(f"unknown or duplicate case_id: {case_id}")
        findings = review["findings"]
        if not isinstance(findings, list) or len(findings) > 20:
            raise ValueError(f"findings must be an array of at most 20 items for {case_id}")
        cleaned = []
        for item in findings:
            required = {"title", "severity", "file", "line", "body", "evidence"}
            allowed = required | {"category"}
            if not isinstance(item, dict) or not required <= set(item) <= allowed:
                raise ValueError(f"invalid finding fields for {case_id}")
            if item["severity"] not in SEVERITY_WEIGHTS:
                raise ValueError(f"invalid severity for {case_id}")
            if not isinstance(item["title"], str) or not 1 <= len(item["title"]) <= 500:
                raise ValueError(f"invalid title for {case_id}")
            if not isinstance(item["body"], str) or not 1 <= len(item["body"]) <= 4000:
                raise ValueError(f"invalid body for {case_id}")
            if not isinstance(item["file"], str) or not item["file"]:
                raise ValueError(f"invalid file for {case_id}")
            path = PurePosixPath(normalized_path(item["file"]))
            if path.is_absolute() or ".." in path.parts:
                raise ValueError(f"file must be relative for {case_id}")
            if type(item["line"]) is not int or item["line"] < 1:
                raise ValueError(f"invalid line for {case_id}")
            if not isinstance(item["evidence"], list) or not all(
                isinstance(entry, str) and entry for entry in item["evidence"]
            ):
                raise ValueError(f"invalid evidence for {case_id}")
            if "category" in item and (not isinstance(item["category"], str) or not item["category"]):
                raise ValueError(f"invalid category for {case_id}")
            cleaned.append(item)
        by_case[case_id] = cleaned
    missing = expected - set(by_case)
    if missing:
        raise ValueError(f"missing case reviews: {', '.join(sorted(missing))}")
    return by_case


def grouping_results(
    cases: list[dict],
    matches: list[dict],
    missed: list[dict],
    false_positives: list[dict],
    field: str,
) -> dict:
    counts = defaultdict(lambda: {"truth": 0, "tp": 0, "fp": 0, "fn": 0})
    case_language = {case["case_id"]: case["language"] for case in cases}
    for case in cases:
        for truth in case["findings"]:
            counts[truth[field]]["truth"] += 1
    for match in matches:
        counts[match["truth"][field]]["tp"] += 1
    for item in missed:
        counts[item[field]]["fn"] += 1
    for item in false_positives:
        if field == "language":
            key = case_language[item["case_id"]]
        else:
            key = normalized_text(item["finding"].get("category", "unclassified")).replace(" ", "-")
        counts[key]["fp"] += 1
    return {
        key: values | metric(values["tp"], values["fp"], values["fn"])
        for key, values in sorted(counts.items())
    }


def score_submission(
    submission: object,
    split: str,
    oracle: dict | None = None,
    allow_negated: bool = False,
    adjudication: dict | None = None,
) -> dict:
    if split not in {"calibration", "sealed"}:
        raise ValueError("split must be calibration or sealed")
    oracle = oracle or json.loads(ORACLE_PATH.read_text())
    cases = [case for case in oracle["cases"] if case["split"] == split]
    submitted = validate_submission(submission, cases)

    rejected: list[dict] = []
    if not allow_negated:
        for case_id, candidates in submitted.items():
            kept = []
            for index, candidate in enumerate(candidates):
                phrases = no_defect_phrases(candidate)
                verdict = (adjudication or {}).get(f"{case_id}#{index}")
                asserts_defect = True if verdict is None else bool(verdict)
                if phrases or not asserts_defect:
                    rejected.append(
                        {
                            "case_id": case_id,
                            "index": index,
                            "title": candidate["title"],
                            "reason": "no-defect phrase" if phrases else "adjudicated as no claim",
                            "phrases": phrases,
                            "finding": candidate,
                        }
                    )
                    continue
                kept.append(candidate)
            submitted[case_id] = kept

    matches = []
    missed = []
    false_positives = []
    duplicates = []
    for case in cases:
        candidates = submitted[case["case_id"]]
        truths = case["findings"]
        pairs = []
        for candidate_index, candidate in enumerate(candidates):
            for truth_index, truth in enumerate(truths):
                details = pair_score(candidate, truth)
                if details is not None:
                    pairs.append((details["score"], candidate_index, truth_index, details))
        used_candidates: set[int] = set()
        used_truths: set[int] = set()
        for _, candidate_index, truth_index, details in sorted(
            pairs, key=lambda item: (-item[0], item[1], item[2])
        ):
            if candidate_index in used_candidates or truth_index in used_truths:
                continue
            used_candidates.add(candidate_index)
            used_truths.add(truth_index)
            matches.append(
                {
                    "case_id": case["case_id"],
                    "finding": candidates[candidate_index],
                    "truth": truths[truth_index],
                    "details": details,
                }
            )
        missed.extend(truth for index, truth in enumerate(truths) if index not in used_truths)
        for index, finding in enumerate(candidates):
            if index in used_candidates:
                continue
            # One adjudicated finding can legitimately be reported as two related
            # findings. A candidate that would have paired with an already-matched
            # truth is a duplicate of one root cause, not an invented defect, and
            # must not be scored as a false positive.
            duplicate_of = next(
                (
                    truths[truth_index].get("finding_id")
                    for truth_index in sorted(used_truths)
                    if pair_score(finding, truths[truth_index]) is not None
                ),
                None,
            )
            if duplicate_of is not None:
                duplicates.append(
                    {
                        "case_id": case["case_id"],
                        "finding": finding,
                        "duplicate_of": duplicate_of,
                    }
                )
            else:
                false_positives.append({"case_id": case["case_id"], "finding": finding})

    # A submitted entry that asserts no defect still consumed a finding slot, so it
    # counts against precision instead of silently disappearing.
    false_positives.extend(
        {"case_id": item["case_id"], "finding": item["finding"]} for item in rejected
    )

    tp, fp, fn = len(matches), len(false_positives), len(missed)
    finding_metrics = metric(tp, fp, fn)
    truth_weight = sum(
        SEVERITY_WEIGHTS[truth["severity"]] for case in cases for truth in case["findings"]
    )
    matched_weight = sum(SEVERITY_WEIGHTS[item["truth"]["severity"]] for item in matches)
    fp_weight = sum(SEVERITY_WEIGHTS[item["finding"]["severity"]] for item in false_positives)
    weighted_metrics = metric(matched_weight, fp_weight, truth_weight - matched_weight)

    exact_severity = sum(
        item["finding"]["severity"] == item["truth"]["severity"] for item in matches
    )
    severity_accuracy = ratio(exact_severity, tp)
    confusion = defaultdict(int)
    for item in matches:
        confusion[f"{item['truth']['severity']}->{item['finding']['severity']}"] += 1

    root_exact = sum(item["details"]["location_kind"] == "root" for item in matches)
    causal_location = sum(item["details"]["location_kind"] != "none" for item in matches)
    total_anchors = sum(
        len(truth["causal_anchors"]) for case in cases for truth in case["findings"]
    )
    matched_anchors = sum(len(item["truth"]["causal_anchors"]) for item in matches)
    anchors_hit = sum(item["details"]["evidence_hits"] for item in matches)
    causal_overall = ratio(anchors_hit, total_anchors)
    concept_coverage = sum(item["details"]["concept_coverage"] for item in matches)
    causal_reasoning = ratio(concept_coverage, tp + fn)

    clean_cases = {case["case_id"] for case in cases if not case["findings"]}
    clean_fp_items = [item for item in false_positives if item["case_id"] in clean_cases]
    clean_cases_with_fp = {item["case_id"] for item in clean_fp_items}
    critical_misses = [item for item in missed if item["severity"] == "critical"]

    components = {
        "finding_f1": round(20 * finding_metrics["f1"], 4),
        "severity_weighted_f1": round(40 * weighted_metrics["f1"], 4),
        "severity_accuracy": round(10 * severity_accuracy, 4),
        "causal_localization": round(10 * ratio(causal_location, tp + fn), 4),
        "causal_evidence": round(10 * causal_overall, 4),
        "causal_reasoning": round(10 * causal_reasoning, 4),
    }
    fp_penalty = min(20.0, 1.5 * fp)
    clean_penalty = min(15.0, 4.0 * len(clean_cases_with_fp))
    critical_penalty = min(36.0, 12.0 * len(critical_misses))
    # Splitting one root cause costs far less than inventing a defect.
    duplicate_penalty = min(5.0, 0.5 * len(duplicates))
    penalties = {
        "false_positive_findings": fp_penalty,
        "clean_control_cases": clean_penalty,
        "critical_misses": critical_penalty,
        "duplicate_reports": duplicate_penalty,
        "total": fp_penalty + clean_penalty + critical_penalty + duplicate_penalty,
    }
    raw_score = sum(components.values())
    final_score = round(max(0.0, min(100.0, raw_score - penalties["total"])), 2)

    return {
        "score": final_score,
        "counts": {
            "truth": tp + fn,
            "submitted": tp + fp,
            "matched": tp,
            "false_positives": fp,
            "misses": fn,
        },
        "finding_metrics": finding_metrics,
        "severity_weighted_metrics": weighted_metrics
        | {"matched_weight": matched_weight, "truth_weight": truth_weight, "false_positive_weight": fp_weight},
        "severity": {
            "accuracy": severity_accuracy,
            "exact": exact_severity,
            "matched": tp,
            "confusion": dict(sorted(confusion.items())),
        },
        "localization": {
            "root_exact": root_exact,
            "root_exact_rate": ratio(root_exact, tp),
            "causal_location": causal_location,
            "causal_location_rate": ratio(causal_location, tp + fn),
        },
        "causal_evidence": {
            "anchors_hit": anchors_hit,
            "anchors_for_matches": matched_anchors,
            "anchors_total": total_anchors,
            "matched_coverage": ratio(anchors_hit, matched_anchors),
            "overall_coverage": causal_overall,
        },
        "causal_reasoning": {
            "concept_coverage_sum": round(concept_coverage, 6),
            "matched_coverage": ratio(concept_coverage, tp),
            "overall_coverage": causal_reasoning,
        },
        "per_category": grouping_results(cases, matches, missed, false_positives, "category"),
        "per_language": grouping_results(cases, matches, missed, false_positives, "language"),
        "clean_controls": {
            "cases": len(clean_cases),
            "cases_with_false_positives": len(clean_cases_with_fp),
            "false_positive_findings": len(clean_fp_items),
            "case_false_positive_rate": ratio(len(clean_cases_with_fp), len(clean_cases)),
        },
        "duplicates": {
            "count": len(duplicates),
            "items": [
                {
                    "case_id": item["case_id"],
                    "duplicate_of": item["duplicate_of"],
                    "title": item["finding"]["title"],
                }
                for item in duplicates
            ],
        },
        "polarity": {
            "rejected": len(rejected),
            "adjudicated": adjudication is not None,
            "items": [
                {key: item[key] for key in ("case_id", "index", "title", "reason", "phrases")}
                for item in rejected
            ],
        },
        "critical_misses": {
            "count": len(critical_misses),
            "finding_ids": sorted(item["finding_id"] for item in critical_misses),
        },
        "components": components | {"raw": round(raw_score, 4)},
        "penalties": penalties,
    }


def submission_template(split: str) -> dict:
    manifest = json.loads((ROOT / "cases" / "manifest.json").read_text())
    return {
        "reviews": [
            {"case_id": case["case_id"], "findings": []}
            for case in manifest["cases"]
            if case["split"] == split
        ]
    }


def compare_submissions(
    paths: list[Path],
    split: str,
    allow_negated: bool = False,
    adjudication: dict | None = None,
) -> dict:
    """Score a shared no-skill baseline (first path) against one or more candidates."""
    reports = []
    for path in paths:
        report = score_submission(
            json.loads(path.read_text()),
            split,
            allow_negated=allow_negated,
            adjudication=adjudication,
        )
        reports.append({"submission": str(path), "report": report})
    baseline = reports[0]

    def row(entry: dict) -> dict:
        report = entry["report"]
        return {
            "submission": entry["submission"],
            "score": report["score"],
            "precision": report["finding_metrics"]["precision"],
            "recall": report["finding_metrics"]["recall"],
            "f1": report["finding_metrics"]["f1"],
            "severity_accuracy": report["severity"]["accuracy"],
            "false_positives": report["counts"]["false_positives"],
            "critical_misses": report["critical_misses"]["count"],
            "control_false_positives": report["clean_controls"]["false_positive_findings"],
        }

    baseline_row = row(baseline)
    candidates = []
    for entry in reports[1:]:
        current = row(entry)
        candidates.append(
            current
            | {
                "score_delta": round(current["score"] - baseline_row["score"], 4),
                "recall_delta": round(current["recall"] - baseline_row["recall"], 6),
                "false_positive_delta": current["false_positives"] - baseline_row["false_positives"],
                "control_false_positive_delta": (
                    current["control_false_positives"] - baseline_row["control_false_positives"]
                ),
                "critical_miss_delta": current["critical_misses"] - baseline_row["critical_misses"],
            }
        )
    return {
        "split": split,
        "baseline": baseline_row,
        "candidates": candidates,
        "reports": reports,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("submission", type=Path, nargs="*")
    parser.add_argument("--split", required=True, choices=("calibration", "sealed"))
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--compare",
        action="store_true",
        help="first submission is the shared no-skill baseline, the rest are candidates",
    )
    parser.add_argument(
        "--template",
        action="store_true",
        help="print an empty submission skeleton for the split and exit",
    )
    parser.add_argument(
        "--adjudication",
        type=Path,
        help="verdict file from adjudicate.py; drops findings that assert no defect",
    )
    parser.add_argument(
        "--allow-negated-bodies",
        action="store_true",
        help="diagnostic only: disable the no-defect gate and score raw matches",
    )
    args = parser.parse_args()
    if args.template:
        print(json.dumps(submission_template(args.split), indent=2) + "\n", end="")
        return 0
    if not args.submission:
        print("scoring failed: no submission given", file=sys.stderr)
        return 2
    if args.compare and len(args.submission) < 2:
        print("scoring failed: --compare needs a baseline and at least one candidate", file=sys.stderr)
        return 2
    try:
        adjudication = None
        if args.adjudication:
            from adjudicate import load_verdicts

            adjudication = load_verdicts(args.adjudication)
        if args.compare:
            report = compare_submissions(
                args.submission, args.split, args.allow_negated_bodies, adjudication
            )
        else:
            submission = json.loads(args.submission[0].read_text())
            report = score_submission(
                submission,
                args.split,
                allow_negated=args.allow_negated_bodies,
                adjudication=adjudication,
            )
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"scoring failed: {error}", file=sys.stderr)
        return 2
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        if args.output.exists():
            print(f"scoring failed: refusing to overwrite {args.output}", file=sys.stderr)
            return 2
        args.output.write_text(rendered)
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
