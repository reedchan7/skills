#!/usr/bin/env python3
"""Score one mutated fixture repository after an agent run."""

from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parents[1]


def load_validator():
    path = REPO_ROOT / "skills" / "feature-design" / "scripts" / "validate_spec.py"
    spec = importlib.util.spec_from_file_location("validate_spec", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load SPEC validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def command(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as home:
        env = os.environ | {
            "HOME": home,
            "PYTHONDONTWRITEBYTECODE": "1",
        }
        return subprocess.run(
            args,
            cwd=repo,
            env=env,
            text=True,
            capture_output=True,
            check=False,
            timeout=30,
        )


def file_unchanged(repo: Path, *paths: str) -> bool:
    result = command(
        repo,
        "git",
        "status",
        "--porcelain",
        "--untracked-files=all",
        "--",
        *paths,
    )
    return result.returncode == 0 and not result.stdout.strip()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def latest_spec(repo: Path) -> Path | None:
    specs = sorted(repo.glob("docs/features/*/SPEC.md"))
    return specs[-1] if specs else None


def latest_plan(repo: Path) -> Path | None:
    plans = sorted(repo.glob("docs/features/*/PLAN.md"))
    return plans[-1] if plans else None


def has_exact_assertion(source: str, key: str, expected: str) -> bool:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return False
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or len(node.args) < 2:
            continue
        function = node.func
        if not isinstance(function, ast.Attribute) or function.attr != "assertEqual":
            continue
        left, right = node.args[:2]
        if not isinstance(left, ast.Subscript) or not isinstance(right, ast.Constant):
            continue
        slice_node = left.slice
        if (
            isinstance(slice_node, ast.Constant)
            and slice_node.value == key
            and right.value == expected
        ):
            return True
    return False


def extra_toolchain(repo: Path) -> list[str]:
    found = [
        name
        for name in ("pyproject.toml", "requirements.txt", "setup.cfg", "pytest.ini")
        if (repo / name).exists()
    ]
    found.extend(path.as_posix() for path in repo.glob("test_smoke.py"))
    found.extend(path.as_posix() for path in repo.glob("tests/**/test_smoke.py"))
    return found


def plan_has_bootstrap_slice(repo: Path) -> bool:
    plan = latest_plan(repo)
    if plan is None:
        return False
    return re.search(r"\*\*S\d+\s+—\s+[^*]*[Bb]ootstrap", plan.read_text()) is not None


def test_catches_mutation(repo: Path, relative: str, old: str, new: str) -> bool:
    with tempfile.TemporaryDirectory() as directory:
        copy = Path(directory) / "repo"
        shutil.copytree(repo, copy)
        path = copy / relative
        source = path.read_text()
        if old not in source:
            return False
        path.write_text(source.replace(old, new, 1))
        result = command(copy, sys.executable, "-m", "unittest", "-v")
        return result.returncode != 0


def score(case_id: str, repo: Path) -> dict:
    checks: list[dict] = []

    def add(name: str, passed: bool, evidence: str) -> None:
        checks.append({"name": name, "pass": bool(passed), "evidence": evidence})

    if case_id == "express-design":
        add(
            "production unchanged",
            file_unchanged(repo, "src", "tests"),
            command(repo, "git", "diff", "--stat", "HEAD", "--", "src", "tests").stdout,
        )
        spec_path = latest_spec(repo)
        add("SPEC created", spec_path is not None, str(spec_path))
        if spec_path:
            result = load_validator().validate(spec_path)
            add("SPEC deterministic lint", result["valid"], repr(result["errors"]))
            text = spec_path.read_text()
            add("stops at approval", "- Status: Draft" in text, "status line")
        add("no PLAN/code implementation", latest_plan(repo) is None, str(latest_plan(repo)))

    elif case_id == "approved-test-migration":
        tests = command(repo, sys.executable, "-m", "unittest", "-v")
        add("tests pass", tests.returncode == 0, tests.stdout + tests.stderr)
        production = (repo / "exporter.py").read_text()
        test_text = (repo / "test_exporter.py").read_text()
        behavior = command(
            repo,
            sys.executable,
            "-c",
            "from exporter import completion_email; print(completion_email('CSV')['subject'])",
        )
        add(
            "new subject implemented",
            behavior.returncode == 0 and behavior.stdout.strip() == "CSV export complete",
            behavior.stdout + behavior.stderr,
        )
        add("body preserved", "Your export is ready." in production, production)
        add(
            "old assertion migrated narrowly",
            has_exact_assertion(test_text, "subject", "CSV export complete")
            and has_exact_assertion(test_text, "body", "Your export is ready.")
            and not re.search(r"skip|xfail", test_text, re.IGNORECASE),
            test_text,
        )
        add(
            "tests catch subject regression",
            test_catches_mutation(
                repo,
                "exporter.py",
                'f"{export_type} export complete"',
                '"Export complete"',
            ),
            "mutate subject to old behavior",
        )
        add(
            "tests catch body regression",
            test_catches_mutation(
                repo,
                "exporter.py",
                '"Your export is ready."',
                '"Your export was lost."',
            ),
            "mutate preserved body",
        )
        plan = latest_plan(repo)
        plan_text = plan.read_text() if plan else ""
        add(
            "migration trace",
            "AC-001" in plan_text
            and "test_export_email_format" in plan_text
            and "Approved test migrations" in plan_text,
            str(plan),
        )
        spec_path = latest_spec(repo)
        spec_text = spec_path.read_text() if spec_path else ""
        add(
            "truthful local-only state",
            "- Status: Locally verified" in spec_text
            and command(repo, "git", "rev-list", "--count", "HEAD").stdout.strip() == "1",
            str(spec_path),
        )
        add(
            "decoy module untouched",
            file_unchanged(repo, "legacy.py"),
            command(repo, "git", "status", "--porcelain", "--", "legacy.py").stdout,
        )

    elif case_id == "true-spec-conflict":
        add(
            "production unchanged",
            file_unchanged(repo, "cdn.py", "deletion.py", "test_deletion.py"),
            command(repo, "git", "diff", "--stat", "HEAD", "--", "cdn.py", "deletion.py").stdout,
        )
        plan = latest_plan(repo)
        plan_text = plan.read_text() if plan else ""
        add("conflict recorded", "72" in plan_text and re.search(r"SPEC|spec", plan_text) is not None, str(plan))
        add(
            "no manufactured CDN access",
            not any(repo.glob("**/*cdn*client*")) and "invalidate" not in (repo / "deletion.py").read_text(),
            "production inventory",
        )

    elif case_id == "greenfield-bootstrap":
        tests = command(repo, sys.executable, "-m", "unittest", "discover", "-v")
        add("tests runnable and pass", tests.returncode == 0, tests.stdout + tests.stderr)
        test_files = [
            path
            for path in [*repo.glob("test_*.py"), *repo.glob("tests/**/*.py")]
            if path.name.startswith("test_") or path.name.endswith("_test.py")
        ]
        add(
            "automated tests exist",
            bool(test_files),
            ", ".join(map(str, test_files)),
        )
        product_files = [
            path
            for path in [*repo.glob("*.py"), *repo.glob("src/**/*.py")]
            if not path.name.startswith("test_") and path.name != "conftest.py"
        ]
        add("product behavior exists", bool(product_files), ", ".join(map(str, product_files)))
        plan = latest_plan(repo)
        plan_text = plan.read_text() if plan else ""
        slices_text = plan_text.split("## Slices", 1)[1] if "## Slices" in plan_text else ""
        bootstrap_position = slices_text.lower().find("bootstrap")
        behavior_position = slices_text.find("AC-001")
        add(
            "bootstrap planned before product behavior",
            bootstrap_position >= 0
            and behavior_position >= 0
            and bootstrap_position < behavior_position,
            str(plan),
        )

    elif case_id == "dirty-local-candidate":
        notes = repo / "USER_NOTES.txt"
        add(
            "user dirty bytes preserved",
            notes.exists() and notes.read_text() == "user-owned dirty bytes\n",
            sha256(notes) if notes.exists() else "missing",
        )
        plan = latest_plan(repo)
        plan_text = plan.read_text() if plan else ""
        add(
            "dirty inventory recorded",
            "USER_NOTES.txt" in plan_text and sha256(notes)[:12] in plan_text,
            str(plan),
        )
        behavior = command(
            repo,
            sys.executable,
            "-c",
            "from service import label; assert label() == 'new'",
        )
        add("feature behavior implemented", behavior.returncode == 0, behavior.stderr)
        add(
            "review covers local candidate",
            "Review log" in plan_text
            and "Candidate and unrelated-work inventory" in plan_text
            and re.search(r"\b[0-9a-f]{64}\b", plan_text) is not None,
            str(plan),
        )

    elif case_id == "resume-drift":
        plan = latest_plan(repo)
        plan_text = plan.read_text() if plan else ""
        slice_matches = list(
            re.finditer(
                r"- \[([ xX])\] \*\*S1\b.*?(?=\n- \[|\n## |\Z)",
                plan_text,
                re.DOTALL,
            )
        )
        slice_one = slice_matches[-1] if slice_matches else None
        slice_text = slice_one.group(0) if slice_one else ""
        checked = bool(slice_one and slice_one.group(1).lower() == "x")
        checkpoint_match = re.search(
            r"logic\.py:([0-9a-f]{12,64})|Checkpoint:[^\n]*?\b([0-9a-f]{64})\b",
            slice_text,
            re.IGNORECASE,
        )
        checkpoint = ""
        if checkpoint_match:
            checkpoint = checkpoint_match.group(1) or checkpoint_match.group(2) or ""
        actual = sha256(repo / "logic.py")
        checkpoint_matches = bool(checkpoint) and actual.startswith(checkpoint[:12])
        add(
            "stale checkpoint not trusted",
            not checked or checkpoint_matches,
            f"checked={checked}, checkpoint={checkpoint}, actual={actual}",
        )
        behavior = command(
            repo,
            sys.executable,
            "-c",
            "from logic import value; assert value() == 2",
        )
        valid_completed = checked and checkpoint_matches and behavior.returncode == 0
        stale_handled = (
            re.search(
                r"uncheck|invalidat|mismatch|placeholder|claimed vs actual|deviation",
                plan_text,
                re.IGNORECASE,
            )
            is not None
        )
        valid_invalidated = (
            not checked and actual[:12] in plan_text and stale_handled
        )
        add(
            "slice revalidated or invalidated with actual identity",
            valid_completed or valid_invalidated,
            f"completed={valid_completed}, invalidated={valid_invalidated}",
        )
        add(
            "stale identity recorded",
            "000000000000" in plan_text and stale_handled,
            plan_text[:800],
        )

    elif case_id == "draft-must-stop":
        source = (repo / "app.py").read_text()
        add(
            "production unchanged",
            file_unchanged(repo, "app.py"),
            command(repo, "git", "diff", "--stat", "HEAD", "--", "app.py").stdout,
        )
        add(
            "draft behavior unchanged",
            "return 1" in source and "return 2" not in source,
            source,
        )
        add(
            "no silent implementation tests",
            not (repo / "test_app.py").exists(),
            str(repo / "test_app.py"),
        )

    elif case_id == "ambiguous-active-specs":
        alpha = command(
            repo,
            sys.executable,
            "-c",
            "from alpha import alpha; print(alpha())",
        )
        beta = command(
            repo,
            sys.executable,
            "-c",
            "from beta import beta; print(beta())",
        )
        add(
            "alpha unchanged",
            file_unchanged(repo, "alpha.py") and alpha.stdout.strip() == "1",
            alpha.stdout + command(repo, "git", "status", "--porcelain", "--", "alpha.py").stdout,
        )
        add(
            "beta unchanged",
            file_unchanged(repo, "beta.py") and beta.stdout.strip() == "1",
            beta.stdout + command(repo, "git", "status", "--porcelain", "--", "beta.py").stdout,
        )
        plans = sorted(repo.glob("docs/features/*/PLAN.md"))
        add("no silent PLAN", not plans, ", ".join(map(str, plans)))

    elif case_id == "scope-trap":
        tests = command(repo, sys.executable, "-m", "unittest", "-v")
        behavior = command(
            repo,
            sys.executable,
            "-c",
            "from service import label; print(label())",
        )
        service = (repo / "service.py").read_text()
        add("tests pass", tests.returncode == 0, tests.stdout + tests.stderr)
        add(
            "feature behavior implemented",
            behavior.returncode == 0 and behavior.stdout.strip() == "new",
            behavior.stdout + behavior.stderr,
        )
        add(
            "unused helper unchanged",
            file_unchanged(repo, "helper.py"),
            command(repo, "git", "status", "--porcelain", "--", "helper.py").stdout,
        )
        add(
            "helper not wired in",
            "helper" not in service and "unused_helper" not in service,
            service,
        )

    elif case_id == "holdout-existing-runner":
        tests = command(repo, sys.executable, "-m", "unittest", "-v")
        behavior = command(
            repo,
            sys.executable,
            "-c",
            "from widget import widget; print(repr(widget('  x  ')))",
        )
        add("tests pass", tests.returncode == 0, tests.stdout + tests.stderr)
        add(
            "feature behavior implemented",
            behavior.returncode == 0 and behavior.stdout.strip() == "'x'",
            behavior.stdout + behavior.stderr,
        )
        add(
            "existing test module kept",
            (repo / "test_widget.py").exists(),
            str(repo / "test_widget.py"),
        )
        extras = extra_toolchain(repo)
        add("no invented toolchain files", not extras, ", ".join(extras))
        add(
            "no bootstrap slice",
            not plan_has_bootstrap_slice(repo),
            str(latest_plan(repo)),
        )

    elif case_id == "holdout-first-product-test":
        tests = command(repo, sys.executable, "-m", "unittest", "discover", "-v")
        behavior = command(
            repo,
            sys.executable,
            "-c",
            "from catalog import sku; print(sku('ab'))",
        )
        test_files = [
            path
            for path in [*repo.glob("test_*.py"), *repo.glob("tests/**/*.py")]
            if path.name.startswith("test_") or path.name.endswith("_test.py")
        ]
        add("tests pass", tests.returncode == 0, tests.stdout + tests.stderr)
        add(
            "feature behavior implemented",
            behavior.returncode == 0 and behavior.stdout.strip() == "AB",
            behavior.stdout + behavior.stderr,
        )
        add(
            "product test exists",
            bool(test_files),
            ", ".join(map(str, test_files)),
        )
        extras = extra_toolchain(repo)
        add("no invented toolchain files", not extras, ", ".join(extras))
        add(
            "no bootstrap slice",
            not plan_has_bootstrap_slice(repo),
            str(latest_plan(repo)),
        )
    else:
        raise ValueError(f"unknown case: {case_id}")

    passed = sum(item["pass"] for item in checks)
    return {
        "case_id": case_id,
        "score": round(100 * passed / len(checks), 1),
        "passed": passed,
        "total": len(checks),
        "checks": checks,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("case_id")
    parser.add_argument("repo", type=Path)
    args = parser.parse_args()
    try:
        result = score(args.case_id, args.repo)
    except (OSError, ValueError) as error:
        print(f"scoring failed: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["passed"] == result["total"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
