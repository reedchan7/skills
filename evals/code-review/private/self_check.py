#!/usr/bin/env python3
"""Exercise repository shape, packaging isolation, and scorer extremes."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "private"))

from pack import package  # noqa: E402
from scorer import score_submission  # noqa: E402


ORACLE = json.loads((ROOT / "private" / "oracle.json").read_text())
MANIFEST = json.loads((ROOT / "cases" / "manifest.json").read_text())


def reviews_for(split: str, mode: str) -> dict:
    reviews = []
    for case in ORACLE["cases"]:
        if case["split"] != split:
            continue
        findings = []
        if mode in {"perfect", "shallow"}:
            for truth in case["findings"]:
                phrases = [group[0] for group in truth["concept_groups"]]
                findings.append(
                    {
                        "title": phrases[0],
                        "severity": truth["severity"],
                        "file": truth["file"],
                        "line": truth["line_start"],
                        "body": phrases[0] if mode == "shallow" else "; ".join(phrases),
                        "evidence": [
                            f"{anchor['file']}:{anchor['line_start']}"
                            for anchor in truth["causal_anchors"]
                        ],
                        "category": truth["category"],
                    }
                )
        elif mode == "false-positive" and not case["findings"]:
            findings.append(
                {
                    "title": "Possible naming concern",
                    "severity": "low",
                    "file": "src/notes.txt",
                    "line": 1,
                    "body": "A generic speculative concern with no causal support.",
                    "evidence": [],
                }
            )
        reviews.append({"case_id": case["case_id"], "findings": findings})
    return {"reviews": reviews}


def assert_repositories() -> None:
    for case in ORACLE["cases"]:
        repo = ROOT / "cases" / case["split"] / case["case_id"] / "repo"
        commits = subprocess.run(
            ["git", "rev-list", "--count", "HEAD"],
            cwd=repo,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        ).stdout.strip()
        changed = subprocess.run(
            ["git", "diff", "--name-only", "HEAD^", "HEAD"],
            cwd=repo,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        ).stdout.splitlines()
        dirty = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        ).stdout
        subprocess.run(
            ["git", "fsck", "--full", "--strict"],
            cwd=repo,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        # HEAD^ is always the base and HEAD the change; earlier commits are optional
        # history that a reviewer is expected to consult.
        assert int(commits) >= 2, case["case_id"]
        assert len(changed) >= 2, case["case_id"]
        assert not dirty, case["case_id"]
        for finding in case["findings"]:
            assert len({anchor["file"] for anchor in finding["causal_anchors"]}) >= 2


def assert_scores() -> dict:
    summary = {}
    for split in ("calibration", "sealed"):
        split_cases = [case for case in ORACLE["cases"] if case["split"] == split]
        manifest_cases = [case for case in MANIFEST["cases"] if case["split"] == split]
        control_count = sum(not case["findings"] for case in split_cases)
        assert len(split_cases) == len(manifest_cases), split
        assert split_cases, split
        assert control_count >= 1, split
        assert control_count < len(split_cases), split

        perfect = score_submission(reviews_for(split, "perfect"), split, ORACLE)
        shallow = score_submission(reviews_for(split, "shallow"), split, ORACLE)
        empty = score_submission(reviews_for(split, "empty"), split, ORACLE)
        false_positive = score_submission(reviews_for(split, "false-positive"), split, ORACLE)
        assert perfect["score"] == 100.0
        assert perfect["counts"]["false_positives"] == 0
        assert perfect["counts"]["misses"] == 0
        assert perfect["critical_misses"]["count"] == 0
        assert shallow["score"] < 100.0
        assert shallow["causal_reasoning"]["overall_coverage"] < 1.0
        assert empty["score"] == 0.0
        assert empty["counts"]["matched"] == 0
        assert empty["counts"]["misses"] == empty["counts"]["truth"]
        assert false_positive["score"] == 0.0
        assert false_positive["counts"]["matched"] == 0
        assert false_positive["clean_controls"]["cases_with_false_positives"] == control_count
        assert false_positive["clean_controls"]["false_positive_findings"] == control_count
        assert false_positive["penalties"]["false_positive_findings"] > 0
        summary[split] = {
            "perfect": perfect["score"],
            "empty": empty["score"],
            "false_positive": false_positive["score"],
        }
    return summary


def assert_package() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        temp = Path(temporary)
        skill = temp / "candidate"
        skill.mkdir()
        (skill / "SKILL.md").write_text("# Candidate\n")
        first = temp / "first.zip"
        second = temp / "second.zip"
        calibration = temp / "calibration.zip"
        first_digest = package("sealed", first, skill)
        second_digest = package("sealed", second, skill)
        package("calibration", calibration, None)
        assert first_digest == second_digest
        assert hashlib.sha256(first.read_bytes()).digest() == hashlib.sha256(second.read_bytes()).digest()

        with zipfile.ZipFile(first) as archive:
            names = archive.namelist()
            assert names == sorted(names)
            assert "task.json" in names
            assert "README.md" in names
            assert "skill/SKILL.md" in names
            sealed_count = sum(case["split"] == "sealed" for case in MANIFEST["cases"])
            assert sum(name.endswith("/.git/HEAD") for name in names) == sealed_count
            forbidden = {"oracle.json", "scorer.py", "build_cases.py", "self_check.py"}
            assert not any("private" in Path(name).parts for name in names)
            assert not any(Path(name).name in forbidden for name in names)

            # The custodian README describes the clean controls, the finding count,
            # and the severity distribution. It must never reach a contender.
            packed_readme = archive.read("README.md")
            assert packed_readme == (ROOT / "CONTENDER.md").read_bytes()
            packed_text = packed_readme.decode().lower()
            for probe in ("control", "adjudicated", "custodian", "oracle", "calibration"):
                assert probe not in packed_text, probe
            task = json.loads(archive.read("task.json"))
            assert task["split"] == "sealed"
            assert len(task["cases"]) == sealed_count
            assert task["skill"] == "skill/"
            extracted = temp / "extracted"
            archive.extractall(extracted)

        extracted_repo = extracted / "cases" / task["cases"][0]["case_id"]
        extracted_status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=extracted_repo,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).stdout
        assert not extracted_status

        with zipfile.ZipFile(calibration) as archive:
            task = json.loads(archive.read("task.json"))
            assert task["split"] == "calibration"
            assert len(task["cases"]) == sum(
                case["split"] == "calibration" for case in MANIFEST["cases"]
            )
            assert task["skill"] is None
            assert not any(name.startswith("skill/") for name in archive.namelist())

        linked_skill = temp / "linked-skill"
        linked_skill.symlink_to(skill, target_is_directory=True)
        try:
            package("sealed", temp / "linked.zip", linked_skill)
        except ValueError:
            pass
        else:
            raise AssertionError("skill symlink was accepted")

        for number, forbidden_skill in enumerate((ROOT / "private", ROOT, ROOT.parent)):
            try:
                package("sealed", temp / f"private-{number}.zip", forbidden_skill)
            except ValueError:
                pass
            else:
                raise AssertionError("a path containing private data was accepted as a skill")


def assert_clean_controls() -> None:
    rotation = (ROOT / "cases" / "sealed" / "s-82f7" / "repo" / "src" / "token.ts").read_text()
    rotation_session = (
        ROOT / "cases" / "sealed" / "s-82f7" / "repo" / "src" / "session.ts"
    ).read_text()
    import_repository = (
        ROOT / "cases" / "sealed" / "s-91b3" / "repo" / "imports" / "repository.go"
    ).read_text()
    membership_migration = (
        ROOT
        / "cases"
        / "sealed"
        / "s-a6e8"
        / "repo"
        / "migrations"
        / "002_membership_roles.sql"
    ).read_text()
    assert "parts.length === 2" in rotation and "parts.length === 3" in rotation
    assert "emitLegacyTokens" in rotation_session and "signLegacy" in rotation_session
    assert "BeginTx" in import_repository and "import_outbox" in import_repository
    assert "DEFAULT 'member'" in membership_migration


def main() -> int:
    manifest = json.loads((ROOT / "cases" / "manifest.json").read_text())
    assert len(manifest["cases"]) == len(ORACLE["cases"])
    assert not ({"findings", "severity", "category", "language"} & set().union(
        *(case.keys() for case in manifest["cases"])
    ))
    assert_repositories()
    assert_clean_controls()
    score_summary = assert_scores()
    assert_package()
    languages = sorted({case["language"] for case in ORACLE["cases"]})
    categories = sorted(
        {finding["category"] for case in ORACLE["cases"] for finding in case["findings"]}
    )
    print(
        json.dumps(
            {
                "status": "ok",
                "cases": len(ORACLE["cases"]),
                "languages": languages,
                "categories": categories,
                "scores": score_summary,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
