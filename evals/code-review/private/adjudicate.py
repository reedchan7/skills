#!/usr/bin/env python3
"""Blind semantic adjudication for review submissions.

The deterministic scorer matches on location plus a bag-of-tokens concept
overlap, which has no polarity: a body that keeps the oracle's keywords while
concluding "this is correct" still matches. `scorer.py` catches the explicit
phrasings, but hedged text ("this may be intentional, though note X") slips
through and collects full credit.

This tool splits scoring into two tiers. It emits one packet per submitted
finding containing only the case diff and the finding text — never the oracle —
so a judge can answer two questions without knowing the expected answer:

    asserts_defect  does this text claim a defect exists, or describe/excuse
                    behavior without claiming it is wrong?
    mechanism       in one sentence, the failure mechanism it claims

Feed the collected verdicts back with `scorer.py --adjudication`.

    python3 private/adjudicate.py emit  submission.json --split sealed > packet.json
    python3 private/adjudicate.py stub  packet.json > verdicts.json
    python3 private/scorer.py submission.json --split sealed --adjudication verdicts.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]

JUDGE_PROMPT = """You are adjudicating one code-review finding. You are not
reviewing the code and you do not know whether a defect exists.

Read the diff and the finding text. Answer only:

1. asserts_defect — true when the text claims something is wrong with the
   changed code. False when it describes behavior, asks a question, excuses the
   code, hedges without committing, or concludes the code is acceptable.
   Hedged text that never commits to a defect is false.
2. mechanism — one sentence naming the failure mechanism the text claims, or
   null when asserts_defect is false.

Return only: {"asserts_defect": bool, "mechanism": string or null}
"""


def case_diff(split: str, case_id: str) -> str:
    repo = ROOT / "cases" / split / case_id / "repo"
    if not repo.is_dir():
        raise ValueError(f"case repository is missing: {repo}")
    return subprocess.run(
        ["git", "diff", "HEAD^", "HEAD"],
        cwd=repo,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    ).stdout


def emit(submission_path: Path, split: str) -> dict:
    submission = json.loads(submission_path.read_text())
    diffs: dict[str, str] = {}
    items = []
    for review in submission["reviews"]:
        case_id = review["case_id"]
        for index, finding in enumerate(review.get("findings", [])):
            if case_id not in diffs:
                diffs[case_id] = case_diff(split, case_id)
            items.append(
                {
                    "id": f"{case_id}#{index}",
                    "diff": diffs[case_id],
                    "finding": {
                        "title": finding["title"],
                        "body": finding["body"],
                        "file": finding["file"],
                        "line": finding["line"],
                    },
                }
            )
    return {"split": split, "prompt": JUDGE_PROMPT, "items": items}


def stub(packet_path: Path) -> dict:
    """An all-true verdict file, so the pipeline can be wired before a judge runs."""
    packet = json.loads(packet_path.read_text())
    return {item["id"]: {"asserts_defect": True, "mechanism": None} for item in packet["items"]}


def load_verdicts(path: Path) -> dict[str, bool]:
    raw = json.loads(path.read_text())
    verdicts = {}
    for key, value in raw.items():
        if isinstance(value, bool):
            verdicts[key] = value
        elif isinstance(value, dict) and isinstance(value.get("asserts_defect"), bool):
            verdicts[key] = value["asserts_defect"]
        else:
            raise ValueError(f"verdict for {key} needs a boolean asserts_defect")
    return verdicts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("emit", "stub"))
    parser.add_argument("path", type=Path)
    parser.add_argument("--split", choices=("calibration", "sealed"))
    args = parser.parse_args()
    try:
        if args.command == "emit":
            if not args.split:
                raise ValueError("emit needs --split")
            result = emit(args.path, args.split)
        else:
            result = stub(args.path)
    except (OSError, ValueError, KeyError, json.JSONDecodeError, subprocess.CalledProcessError) as error:
        print(f"adjudication failed: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
