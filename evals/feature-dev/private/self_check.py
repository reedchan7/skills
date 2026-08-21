#!/usr/bin/env python3
"""Self-check generated fixtures and the artifact validators."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=repo, text=True, capture_output=True, check=False)


def main() -> int:
    build = run(ROOT, sys.executable, str(ROOT / "private" / "build_cases.py"))
    if build.returncode:
        print(build.stdout)
        print(build.stderr, file=sys.stderr)
        return 1

    manifest = json.loads((ROOT / "cases" / "manifest.json").read_text())
    if len(manifest["cases"]) != 11:
        raise AssertionError("expected eleven cases")

    validate_spec = load_module(
        "validate_spec",
        REPO_ROOT / "skills" / "feature-design" / "scripts" / "validate_spec.py",
    )
    for case in manifest["cases"]:
        repo = ROOT / case["repo"]
        specs = list(repo.glob("docs/features/*/SPEC.md"))
        for path in specs:
            result = validate_spec.validate(path)
            if not result["valid"]:
                raise AssertionError(f"{case['case_id']} invalid SPEC: {result['errors']}")

        head = run(repo, "git", "rev-parse", "HEAD")
        if head.returncode:
            raise AssertionError(f"{case['case_id']} is not a Git repository")

    expected_dirty = {
        "dirty-local-candidate": "?? USER_NOTES.txt",
        "resume-drift": "M logic.py",
    }
    for case in manifest["cases"]:
        repo = ROOT / case["repo"]
        status = run(repo, "git", "status", "--short", "--untracked-files=all").stdout.strip()
        expected = expected_dirty.get(case["case_id"], "")
        if status != expected:
            raise AssertionError(
                f"{case['case_id']} status {status!r}, expected {expected!r}"
            )

    for directory in ("migration", "conflict", "holdout-existing-runner"):
        repo = ROOT / "cases" / directory / "repo"
        tests = run(repo, sys.executable, "-m", "unittest", "-v")
        if tests.returncode:
            raise AssertionError(f"{directory} base tests fail:\n{tests.stdout}\n{tests.stderr}")

    print(json.dumps({"cases": 11, "status": "PASS"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
