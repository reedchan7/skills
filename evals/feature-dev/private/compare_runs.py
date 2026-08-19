#!/usr/bin/env python3
"""Score a prepared paired run directory and report candidate deltas."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys


def load_scorer():
    path = Path(__file__).with_name("score_cases.py")
    spec = importlib.util.spec_from_file_location("score_cases", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load scorer")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_root", type=Path)
    args = parser.parse_args()
    manifest = json.loads((args.run_root / "manifest.json").read_text())
    scorer = load_scorer()
    results = []
    for run in manifest["runs"]:
        result = scorer.score(run["case_id"], Path(run["repo"]))
        result["variant"] = run["variant"]
        result["skill_sha256"] = run["skill_sha256"]
        results.append(result)

    pairs = []
    for case_id in sorted({item["case_id"] for item in results}):
        candidate = next(
            item for item in results
            if item["case_id"] == case_id and item["variant"] == "candidate"
        )
        control = next(
            item for item in results
            if item["case_id"] == case_id and item["variant"] == "control"
        )
        pairs.append(
            {
                "case_id": case_id,
                "candidate": candidate["score"],
                "control": control["score"],
                "delta": round(candidate["score"] - control["score"], 1),
            }
        )

    output = {
        "seed": manifest["seed"],
        "skill_digests": manifest["skill_digests"],
        "pairs": pairs,
        "mean_candidate": round(sum(item["candidate"] for item in pairs) / len(pairs), 1),
        "mean_control": round(sum(item["control"] for item in pairs) / len(pairs), 1),
        "mean_delta": round(sum(item["delta"] for item in pairs) / len(pairs), 1),
        "runs": results,
    }
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0 if all(item["candidate"] == 100 for item in pairs) else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, StopIteration) as error:
        print(f"comparison failed: {error}", file=sys.stderr)
        raise SystemExit(2) from error
