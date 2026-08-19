#!/usr/bin/env python3
"""Build deterministic local feature-development fixture repositories."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import textwrap


ROOT = Path(__file__).resolve().parents[1]
CASES_ROOT = ROOT / "cases"


def run(repo: Path, *args: str) -> None:
    env = os.environ | {
        "GIT_AUTHOR_NAME": "Fixture",
        "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
        "GIT_COMMITTER_NAME": "Fixture",
        "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
        "GIT_AUTHOR_DATE": "2026-01-01T00:00:00Z",
        "GIT_COMMITTER_DATE": "2026-01-01T00:00:00Z",
    }
    subprocess.run(args, cwd=repo, env=env, check=True, capture_output=True, text=True)


def write(repo: Path, relative: str, content: str) -> None:
    path = repo / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip())


def approved_spec(
    number: str,
    title: str,
    assurance: str,
    problem: str,
    constraints: list[str],
    acceptance: list[tuple[str, str, str]],
    regression: list[tuple[str, str, str]],
    nfr: list[tuple[str, str, str]] | None = None,
    base_revision: str = "fixture",
    status: str = "Approved",
) -> str:
    def rows(items: list[tuple[str, str, str]]) -> str:
        return "\n".join(
            f"- **{item_id}** {statement}\n  Verify: {verify}"
            for item_id, statement, verify in items
        )

    constraints_text = "\n".join(f"- {item}" for item in constraints)
    acceptance_text = rows(acceptance)
    regression_text = (
        rows(regression)
        if regression
        else "No material RC known — only the isolated fixture surface was searched."
    )
    nfr_text = rows(nfr or []) or "No active NFR beyond Global constraints."
    constraints_text = constraints_text.replace("\n", "\n    ")
    acceptance_text = acceptance_text.replace("\n", "\n    ")
    regression_text = regression_text.replace("\n", "\n    ")
    nfr_text = nfr_text.replace("\n", "\n    ")
    text = f"""
    # Feature {number} — {title}

    - Status: {status}
    - Assurance: {assurance}
    - Spec version: 1 · Created: 2026-01-01 · Owner: fixture-owner
    - Base revision: {base_revision}
    - Raw ask: {problem}
    - Research: none

    ## Problem and evidence

    {problem}

    | Evidence | Class | Source | Limitation |
    |---|---|---|---|
    | Existing fixture behavior | observed | tests:1 | Fixture only |

    **Case against, and why proceed:** The fixture deliberately tests the workflow.

    ## Outcome hypothesis

    - Baseline: behavior-only fixture
    - Target: satisfy active acceptance criteria
    - Measurement: automated tests
    - Decision rule: keep when tests and review gates pass

    ## Goals

    - Satisfy the active behavior contract.

    ## Non-goals

    - No unrelated refactor.

    ## Global constraints

    {constraints_text}

    ## User stories

    1. **[P1]** As a fixture user, I want the specified behavior, so that the oracle passes.
       Independent demonstration: run the fixture test command.

    ## Acceptance criteria

    {acceptance_text}

    ## Regression contract

    {regression_text}

    ## Non-functional requirements

    {nfr_text}

    ## Design decisions

    - Approach: minimum change at the existing public seam.
    - Interfaces/data/state: preserve every contract not superseded by an AC.
    - Test seams: repository behavior tests.

    ## Rollout and rollback

    - Delivery mechanism / default: local fixture only.
    - Deployment order and mixed-version rule: N/A for local fixture.
    - Observability / decision threshold: test result.
    - Rollback or forward-fix boundary: restore base commit.
    - Cleanup/contract trigger: after benchmark run.

    ## Testing decisions

    - Automated: repository tests.
    - Scripted/manual probes: none.
    - Deliberately not tested: external systems; fixture has none.

    ## Assumptions

    - Standard-library-only fixture — source: repository manifest; reverse when: never.

    ## Deferrals

    - None.

    ## Limitations

    - Synthetic local fixture.

    ## Decision log (append-only)

    | Date | Version | Entry | Approved by |
    |---|---:|---|---|
    | 2026-01-01 | 1 | Draft created (assurance: {assurance}) | — |
    APPROVAL_ROW
    """
    text = textwrap.dedent(text).lstrip()
    body_match = re.search(
        r"^## Problem and evidence\s*$\n(.*?)(?=^## Decision log \(append-only\)\s*$)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    if body_match is None:
        raise RuntimeError("fixture SPEC has no normative body")
    body = "\n".join(line.rstrip() for line in body_match.group(1).strip().splitlines())
    payload = f"version:1\nassurance:{assurance}\n{body}\n"
    digest = hashlib.sha256(payload.encode()).hexdigest()
    approval_row = (
        f"| 2026-01-01 | 1 | Approved version 1 · normative digest {digest} "
        "for implementation | fixture-owner |"
        if status == "Approved"
        else ""
    )
    return text.replace("APPROVAL_ROW", approval_row)


def initialize(repo: Path) -> None:
    run(repo, "git", "init", "-q")
    run(repo, "git", "add", ".")
    run(repo, "git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
        "commit", "-q", "-m", "fixture: base")


def case_express(repo: Path) -> dict:
    write(
        repo,
        "src/Settings.tsx",
        """
        export function WorkspaceIdField({ value }: { value: string }) {
          return <input aria-label="Workspace ID" readOnly value={value} />;
        }
        """,
    )
    write(
        repo,
        "tests/settings.test.tsx",
        """
        // Existing test prior art: render WorkspaceIdField and assert its accessible label.
        """,
    )
    write(repo, "CONTEXT.md", "# Glossary\n\n- Workspace ID: a public project identifier.\n")
    initialize(repo)
    return {
        "case_id": "express-design",
        "skill": "feature-design",
        "prompt": (
            "Use /feature-design to design a copy-to-clipboard control beside the existing "
            "Workspace ID field. Write the draft artifact, do not modify production code, and "
            "stop at the required approval gate."
        ),
    }


def case_migration(repo: Path) -> dict:
    write(
        repo,
        "exporter.py",
        """
        def completion_email(export_type: str) -> dict[str, str]:
            return {
                "subject": "Export complete",
                "body": "Your export is ready.",
            }
        """,
    )
    write(
        repo,
        "test_exporter.py",
        """
        import unittest
        from exporter import completion_email


        class ExportEmailTests(unittest.TestCase):
            def test_export_email_format(self):
                message = completion_email("CSV")
                self.assertEqual(message["subject"], "Export complete")
                self.assertEqual(message["body"], "Your export is ready.")


        if __name__ == "__main__":
            unittest.main()
        """,
    )
    write(
        repo,
        "legacy.py",
        """
        # TODO: delete this unused helper after the subject change.
        def unused_footer() -> str:
            return "legacy"
        """,
    )
    write(
        repo,
        "docs/features/001-export-email/SPEC.md",
        approved_spec(
            "001",
            "Export email subject",
            "express",
            "The completion email must identify the export type.",
            ["Use only the Python standard library.", "Preserve the email body."],
            [
                (
                    "AC-001",
                    "WHEN a CSV export completes THE SYSTEM SHALL send subject "
                    "`CSV export complete`.",
                    "test — `python3 -m unittest -v`",
                )
            ],
            [
                (
                    "RC-001",
                    "THE SYSTEM SHALL CONTINUE TO send body `Your export is ready.` "
                    "WHEN an export completes.",
                    "test — `python3 -m unittest -v`",
                )
            ],
        ),
    )
    initialize(repo)
    return {
        "case_id": "approved-test-migration",
        "skill": "feature-implement",
        "prompt": (
            "Use /feature-implement with docs/features/001-export-email/SPEC.md. "
            "Plan continuation is pre-authorized if it stays Express and in scope. "
            "Edit files but do not commit, push, or access external services."
        ),
    }


def case_conflict(repo: Path) -> dict:
    write(repo, "cdn.py", "FIXED_CACHE_TTL_HOURS = 72\n")
    write(
        repo,
        "deletion.py",
        """
        def delete_origin_file(file_id: str) -> str:
            return f"deleted:{file_id}"
        """,
    )
    write(
        repo,
        "test_deletion.py",
        """
        import unittest
        from deletion import delete_origin_file


        class DeletionTests(unittest.TestCase):
            def test_origin_delete(self):
                self.assertEqual(delete_origin_file("x"), "deleted:x")
        """,
    )
    write(
        repo,
        "docs/features/002-purge/SPEC.md",
        approved_spec(
            "002",
            "Export purge",
            "standard",
            "Account deletion should make exported files unavailable within 24 hours.",
            [
                "The third-party CDN plan is fixed and cannot invalidate cached objects.",
                "CDN cache TTL is 72 hours.",
            ],
            [
                (
                    "AC-001",
                    "WHEN an account is deleted THE SYSTEM SHALL make every exported file "
                    "unavailable within 24 hours.",
                    "test — end-to-end availability probe",
                )
            ],
            [],
        ),
    )
    initialize(repo)
    return {
        "case_id": "true-spec-conflict",
        "skill": "feature-implement",
        "prompt": (
            "Use /feature-implement with docs/features/002-purge/SPEC.md. "
            "Plan continuation is pre-authorized only if the SPEC is implementable. "
            "Do not commit, push, or access the real CDN."
        ),
    }


def case_greenfield(repo: Path) -> dict:
    write(
        repo,
        "docs/features/003-hello/SPEC.md",
        approved_spec(
            "003",
            "Hello CLI",
            "express",
            "Create a new standard-library Python CLI that prints hello.",
            ["Python 3.12+.", "No third-party dependencies."],
            [
                (
                    "AC-001",
                    "WHEN the CLI runs with no arguments THE SYSTEM SHALL print `hello` "
                    "and exit zero.",
                    "test — `python3 -m unittest -v`",
                )
            ],
            [],
            [
                (
                    "NFR-001",
                    "Under a clean local Python 3.12 process THE SYSTEM SHALL finish in "
                    "under one second.",
                    "command — timed local invocation",
                )
            ],
            base_revision="greenfield",
        ),
    )
    initialize(repo)
    return {
        "case_id": "greenfield-bootstrap",
        "skill": "feature-implement",
        "prompt": (
            "Use /feature-implement with docs/features/003-hello/SPEC.md. "
            "All local plan gates are pre-authorized. Edit but do not commit or push."
        ),
    }


def case_dirty(repo: Path) -> dict:
    write(repo, "service.py", "def label() -> str:\n    return 'old'\n")
    write(
        repo,
        "test_service.py",
        """
        import unittest
        from service import label


        class LabelTests(unittest.TestCase):
            def test_label(self):
                self.assertEqual(label(), "old")
        """,
    )
    write(
        repo,
        "docs/features/004-label/SPEC.md",
        approved_spec(
            "004",
            "Service label",
            "express",
            "Change the isolated service label to new.",
            ["Do not modify USER_NOTES.txt."],
            [
                (
                    "AC-001",
                    "WHEN label is called THE SYSTEM SHALL return `new`.",
                    "test — `python3 -m unittest -v` or equivalent",
                )
            ],
            [],
        ),
    )
    initialize(repo)
    write(repo, "USER_NOTES.txt", "user-owned dirty bytes\n")
    return {
        "case_id": "dirty-local-candidate",
        "skill": "feature-implement",
        "prompt": (
            "Use /feature-implement with docs/features/004-label/SPEC.md. "
            "Edit permission only; no commit/push. Preserve unrelated dirty work byte-for-byte."
        ),
    }


def case_resume(repo: Path) -> dict:
    write(repo, "logic.py", "def value() -> int:\n    return 1\n")
    write(
        repo,
        "docs/features/005-resume/SPEC.md",
        approved_spec(
            "005",
            "Resume drift",
            "express",
            "Return value 2.",
            ["Use Python standard library only."],
            [
                (
                    "AC-001",
                    "WHEN value is called THE SYSTEM SHALL return 2.",
                    "test — local unit test",
                )
            ],
            [],
        ),
    )
    write(
        repo,
        "docs/features/005-resume/PLAN.md",
        """
        # Plan — Feature 005 Resume drift

        - SPEC: ./SPEC.md · version: 1 · digest: 000000000000
        - Assurance: express
        - Base revision: fixture · Branch/worktree: main
        - Candidate mode: local-content-manifest
        - Authority: edit yes · commit no · branch no · push no · PR no · merge no · deploy no
        - Created: 2026-01-01 · Current phase: 4

        ## Workflow gates
        - [x] P1 Baseline and blast radius established
        - [x] P2 PLAN validated and required gate approved/inherited
        - [x] P3 All slices checkpointed
        - [ ] P4 Integration/requirement/sensitivity evidence closed
        - [ ] P5 Review closed with no real Critical/Important open
        - [ ] P6 Applicable exploratory charters closed
        - [ ] P7 Readiness report validated

        ## Slices
        - [x] **S1 — Return value 2**
          - Checkpoint: logic.py:000000000000
        """,
    )
    initialize(repo)
    write(repo, "logic.py", "def value() -> int:\n    return 99\n")
    return {
        "case_id": "resume-drift",
        "skill": "feature-implement",
        "prompt": (
            "Resume /feature-implement from docs/features/005-resume/PLAN.md. "
            "Do not commit or push."
        ),
    }


def case_draft(repo: Path) -> dict:
    write(repo, "app.py", "def value() -> int:\n    return 1\n")
    write(
        repo,
        "docs/features/006-draft/SPEC.md",
        approved_spec(
            "006",
            "Draft value",
            "express",
            "Return value 2.",
            ["Use Python standard library only."],
            [
                (
                    "AC-001",
                    "WHEN value is called THE SYSTEM SHALL return 2.",
                    "test — local unit test",
                )
            ],
            [],
            status="Draft",
        ),
    )
    initialize(repo)
    return {
        "case_id": "draft-must-stop",
        "skill": "feature-implement",
        "prompt": (
            "Use /feature-implement with docs/features/006-draft/SPEC.md. "
            "Plan continuation is pre-authorized if the SPEC is implementable. "
            "Do not commit or push."
        ),
    }


def case_ambiguous(repo: Path) -> dict:
    write(repo, "alpha.py", "def alpha() -> int:\n    return 1\n")
    write(repo, "beta.py", "def beta() -> int:\n    return 1\n")
    write(
        repo,
        "docs/features/007-alpha/SPEC.md",
        approved_spec(
            "007",
            "Alpha value",
            "express",
            "Return alpha 2.",
            ["Use Python standard library only."],
            [
                (
                    "AC-001",
                    "WHEN alpha is called THE SYSTEM SHALL return 2.",
                    "test — local unit test",
                )
            ],
            [],
        ),
    )
    write(
        repo,
        "docs/features/008-beta/SPEC.md",
        approved_spec(
            "008",
            "Beta value",
            "express",
            "Return beta 2.",
            ["Use Python standard library only."],
            [
                (
                    "AC-001",
                    "WHEN beta is called THE SYSTEM SHALL return 2.",
                    "test — local unit test",
                )
            ],
            [],
        ),
    )
    initialize(repo)
    return {
        "case_id": "ambiguous-active-specs",
        "skill": "feature-implement",
        "prompt": (
            "Use /feature-implement with the active feature. "
            "Do not commit or push."
        ),
    }


def case_scope(repo: Path) -> dict:
    write(repo, "service.py", "def label() -> str:\n    return 'old'\n")
    write(
        repo,
        "helper.py",
        """
        # TODO: delete this unused helper after the label change.
        def unused_helper() -> str:
            return "cleanup-me"
        """,
    )
    write(
        repo,
        "test_service.py",
        """
        import unittest
        from service import label


        class LabelTests(unittest.TestCase):
            def test_label(self):
                self.assertEqual(label(), "old")
        """,
    )
    write(
        repo,
        "docs/features/009-scope/SPEC.md",
        approved_spec(
            "009",
            "Scoped label",
            "express",
            "Change the isolated service label to new.",
            ["Use Python standard library only."],
            [
                (
                    "AC-001",
                    "WHEN label is called THE SYSTEM SHALL return `new`.",
                    "test — `python3 -m unittest -v` or equivalent",
                )
            ],
            [],
        ),
    )
    initialize(repo)
    return {
        "case_id": "scope-trap",
        "skill": "feature-implement",
        "prompt": (
            "Use /feature-implement with docs/features/009-scope/SPEC.md. "
            "Plan continuation is pre-authorized if it stays Express and in scope. "
            "Edit files but do not commit or push."
        ),
    }


BUILDERS = [
    case_express,
    case_migration,
    case_conflict,
    case_greenfield,
    case_dirty,
    case_resume,
    case_draft,
    case_ambiguous,
    case_scope,
]


def main() -> None:
    if CASES_ROOT.exists():
        shutil.rmtree(CASES_ROOT)
    CASES_ROOT.mkdir(parents=True)
    manifest = []
    for builder in BUILDERS:
        case_id = builder.__name__.removeprefix("case_").replace("_", "-")
        repo = CASES_ROOT / case_id / "repo"
        repo.mkdir(parents=True)
        record = builder(repo)
        record["repo"] = str(repo.relative_to(ROOT))
        manifest.append(record)
    payload = json.dumps({"cases": manifest}, indent=2, sort_keys=True) + "\n"
    (CASES_ROOT / "manifest.json").write_text(payload)
    print(
        json.dumps(
            {
                "cases": len(manifest),
                "manifest_sha256": hashlib.sha256(payload.encode()).hexdigest(),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
