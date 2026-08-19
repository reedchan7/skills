#!/usr/bin/env python3
"""Deterministic contract tests for the feature skill pair."""

from __future__ import annotations

import importlib.util
import hashlib
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
EVAL_ROOT = ROOT / "evals" / "feature-dev"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def valid_delivery_plan(normative_digest: str) -> str:
    constraints = """- Use only the Python standard library.
- Preserve the email body."""
    candidate = "a" * 64
    return f"""# Plan — Feature 001 Export email

- SPEC: ./SPEC.md · version: 1 · normative digest: {normative_digest}
- Assurance: express
- Base revision: abc · Branch/worktree: fixture
- Candidate mode: local-content-manifest
- Authority: edit yes · commit no · branch no · push no · PR no · merge no · deploy no
- Created: 2026-01-01 · Current phase: 7

## Workflow gates
- [x] P1 Baseline and blast radius established
- [x] P2 PLAN validated and required gate approved/inherited
- [x] P3 All slices checkpointed
- [x] P4 Integration/requirement/sensitivity evidence closed
- [x] P5 Review closed with no real Critical/Important open
- [x] P6 Applicable exploratory charters closed
- [x] P7 Readiness report validated

## Candidate and unrelated-work inventory
| Path/state | SHA-256 / identity | Owner | Must remain unchanged? |
|---|---|---|---|
| Phase 4 frozen candidate | {candidate} | task | yes |

## Global constraints (verbatim from SPEC)
{constraints}

## Conventions inventory
- Affected tests: `python3 -m unittest -v`

## Baseline failure ledger
| Command | Exit | Test/check | Normalized fingerprint | Status/note |
|---|---:|---|---|---|
| unittest | 0 | all | clean | clean |

## Blast-radius coverage ledger
| Surface / consumer class | Causal path | Requirement/check | State | Limitation |
|---|---|---|---|---|
| email | function → mapping | AC-001/RC-001 | covered | fixture |

## Approved test migrations
| Existing test | Active requirement superseding old assertion | Narrow change |
|---|---|---|
| test_export_email_format | AC-001 | subject assertion only |

## Slices
- [x] **S1 — Export subject**
  - Covers: AC-001, RC-001
  - Files: exporter.py, test_exporter.py
  - Oracle order: subject, then body
  - Affected verify: unittest → pass
  - Rollback: restore manifest
  - Checkpoint: {candidate}
  - Evidence: unittest exit 0 on {candidate}

## Coverage matrix
| Active AC/RC/NFR | Slice(s) | Final Verify method |
|---|---|---|
| AC-001 | S1 | unittest |
| RC-001 | S1 | unittest |

## Deviations and amendments
| ID/date | Level | Expected / found / impact | Resolution and approval |
|---|---|---|---|
| none | code | none | none |

## Noticed, not touched
- None.

## Review log
| Round | Candidate digest | Independent? | Findings C/I/M | Fixed / disproved / open | Verdict |
|---|---|---|---|---|---|
| 1 | {candidate} | yes | 0/0/0 | 0/0/0 | pass |

## Delivery report
### Requirement evidence
| AC/RC/NFR | Verify method | Command/probe + result | Candidate | Time |
|---|---|---|---|---|
| AC-001 | test | unittest exit 0 pass | {candidate} | now |
| RC-001 | test | unittest exit 0 pass | {candidate} | now |

### Exploration
| Charter/oracle | Probe | Observation/evidence | Verdict |
|---|---|---|---|
| library | direct call | expected mapping | ok |

### State evidence
- Locally verified: candidate {candidate}; local gates pass.
"""


class FeatureSkillContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run(
            [sys.executable, str(EVAL_ROOT / "private" / "build_cases.py")],
            cwd=EVAL_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.spec_validator = load_module(
            "spec_validator",
            ROOT / "feature-design" / "scripts" / "validate_spec.py",
        )
        cls.plan_validator = load_module(
            "plan_validator",
            ROOT / "feature-implement" / "scripts" / "validate_plan.py",
        )
        cls.scorer = load_module(
            "feature_dev_scorer",
            EVAL_ROOT / "private" / "score_cases.py",
        )

    def test_packages_are_user_invoked_and_references_exist(self) -> None:
        for package in ("feature-design", "feature-implement"):
            skill = (ROOT / package / "SKILL.md").read_text()
            self.assertIn("disable-model-invocation: true", skill)
            for relative in set(
                re.findall(r"`((?:references|assets)/[^`]+\.md)`", skill)
            ):
                self.assertTrue((ROOT / package / relative).is_file(), relative)

    def test_requested_aliases_are_configured(self) -> None:
        linker = (ROOT / "scripts" / "link-skills.sh").read_text()
        self.assertIn("feature-design:new-feature", linker)
        self.assertNotIn("feature-design:feature-spec", linker)
        self.assertIn("feature-spec:feature-design", linker)

    def test_isolated_sync_installs_design_alias_and_implement(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            env = os.environ | {
                "HOME": str(home),
                "SKILLS_HUB_DIR": str(home / "hub"),
                "MATT_SKILLS_REPO": str(home / "no-matt"),
            }
            subprocess.run(
                [str(ROOT / "scripts" / "link-skills.sh")],
                cwd=ROOT,
                env=env,
                check=True,
                capture_output=True,
                text=True,
            )
            for name in (
                "feature-design",
                "new-feature",
                "feature-implement",
            ):
                skill = home / "hub" / name / "SKILL.md"
                self.assertTrue(skill.is_file(), str(skill))
                text = skill.read_text()
                self.assertIn(f"name: {name}\n", text)
                self.assertIn("disable-model-invocation: true", text)
            self.assertFalse(
                (home / "hub" / "feature-spec").exists(),
                "feature-spec must not install",
            )
            implement = (ROOT / "feature-implement" / "SKILL.md").read_text()
            self.assertIn("A SPEC path is optional", implement)
            self.assertIn("Discover below", implement)

    def test_every_fixture_spec_is_valid(self) -> None:
        for path in (EVAL_ROOT / "cases").glob("*/repo/docs/features/*/SPEC.md"):
            result = self.spec_validator.validate(path)
            self.assertTrue(result["valid"], (path, result["errors"]))
            self.assertEqual(
                result["normative_digest"],
                self.plan_validator.spec_normative_digest(path.read_text()),
                str(path),
            )

    def test_spec_validator_rejects_missing_verify(self) -> None:
        source = next(
            (EVAL_ROOT / "cases" / "migration" / "repo").glob(
                "docs/features/*/SPEC.md"
            )
        ).read_text()
        broken = source.replace("  Verify: test — `python3 -m unittest -v`\n", "", 1)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "SPEC.md"
            path.write_text(broken)
            result = self.spec_validator.validate(path)
        self.assertFalse(result["valid"])
        self.assertTrue(any("AC-001 has no Verify" in item for item in result["errors"]))

    def test_spec_validator_rejects_raw_template(self) -> None:
        template = ROOT / "feature-design" / "assets" / "spec.template.md"
        result = self.spec_validator.validate(template)
        self.assertFalse(result["valid"])
        self.assertTrue(
            any("template choices" in item for item in result["errors"]),
            result["errors"],
        )
        self.assertTrue(
            any("placeholder" in item for item in result["errors"]),
            result["errors"],
        )

    def test_approval_binds_normative_content_not_lifecycle_status(self) -> None:
        spec_path = next(
            (EVAL_ROOT / "cases" / "migration" / "repo").glob(
                "docs/features/*/SPEC.md"
            )
        )
        source = spec_path.read_text()
        original_digest = self.spec_validator.normative_digest(source)
        self.assertIsNotNone(original_digest)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "SPEC.md"
            path.write_text(source.replace("- Status: Approved", "- Status: In implementation"))
            state_result = self.spec_validator.validate(path)
            self.assertTrue(state_result["valid"], state_result["errors"])
            self.assertEqual(state_result["normative_digest"], original_digest)

            path.write_text(source.replace("- Spec version: 1", "- Spec version: 2"))
            version_result = self.spec_validator.validate(path)
            self.assertFalse(version_result["valid"])
            self.assertTrue(
                any("approval bound" in item for item in version_result["errors"]),
                version_result["errors"],
            )

            path.write_text(source.replace("CSV export complete", "ZIP export complete", 1))
            content_result = self.spec_validator.validate(path)
            self.assertFalse(content_result["valid"])
            self.assertTrue(
                any("approval bound" in item for item in content_result["errors"]),
                content_result["errors"],
            )

    def test_plan_validator_requires_bootstrap_slice_before_product_ac(self) -> None:
        repo = EVAL_ROOT / "cases" / "greenfield" / "repo"
        spec_path = next(repo.glob("docs/features/*/SPEC.md"))
        digest = self.spec_validator.normative_digest(spec_path.read_text())
        self.assertIsNotNone(digest)
        plan = f"""
# Plan — Feature 003 Hello CLI

- SPEC: ./SPEC.md · version: 1 · normative digest: {digest}
- Assurance: deep
- Base revision: empty-tree · Branch/worktree: fixture
- Candidate mode: local-content-manifest
- Authority: edit yes · commit no · branch no · push no · PR no · merge no · deploy no
- Created: 2026-01-01 · Current phase: 2

## Workflow gates
- [x] P1 Baseline and blast radius established
- [ ] P2 PLAN validated and required gate approved/inherited
- [ ] P3 All slices checkpointed
- [ ] P4 Integration/requirement/sensitivity evidence closed
- [ ] P5 Review closed with no real Critical/Important open
- [ ] P6 Applicable exploratory charters closed
- [ ] P7 Readiness report validated

## Candidate and unrelated-work inventory
| Path/state | SHA-256 / identity | Owner | Must remain unchanged? |
|---|---|---|---|
| HEAD | fixture | repository | yes |

## Global constraints (verbatim from SPEC)
- Python 3.12+.
- No third-party dependencies.

## Conventions inventory
- Affected tests: `python3 -m unittest -v`

## Baseline failure ledger
| Command | Exit | Test/check | Normalized fingerprint | Status/note |
|---|---:|---|---|---|
| none | 0 | none | empty | greenfield empty-tree |

## Blast-radius coverage ledger
| Surface / consumer class | Causal path | Requirement/check | State | Limitation |
|---|---|---|---|---|
| CLI | new process | AC-001 | covered | new |

## Approved test migrations
| Existing test | Active requirement superseding old assertion | Narrow change |
|---|---|---|
| none | none | none |

## Slices
- [ ] **S1 — Hello CLI**
  - Covers: AC-001, NFR-001
  - Files: hello.py
  - Oracle order: print hello
  - Affected verify: unittest
  - Rollback: delete files
  - Checkpoint: pending
  - Evidence: pending

## Coverage matrix
| Active AC/RC/NFR | Slice(s) | Final Verify method |
|---|---|---|
| AC-001 | S1 | test |
| NFR-001 | S1 | command |

## Deviations and amendments
| ID/date | Level | Expected / found / impact | Resolution and approval |
|---|---|---|---|
| none | none | none | none |

## Noticed, not touched
- None.

## Review log
"""
        with tempfile.TemporaryDirectory() as directory:
            plan_path = Path(directory) / "PLAN.md"
            plan_path.write_text(plan)
            result = self.plan_validator.validate(spec_path, plan_path, "plan")
        self.assertFalse(result["valid"])
        self.assertTrue(
            any("Bootstrap slice" in item for item in result["errors"]),
            result["errors"],
        )
        plan = plan.replace(
            "- [ ] **S1 — Hello CLI**\n  - Covers: AC-001, NFR-001",
            "- [ ] **S1 — Bootstrap toolchain**\n"
            "  - Covers: none — runner only\n"
            "  - Files: pyproject.toml, test_smoke.py\n"
            "  - Oracle order: smoke red then green\n"
            "  - Affected verify: unittest smoke\n"
            "  - Rollback: delete bootstrap files\n"
            "  - Checkpoint: pending\n"
            "  - Evidence: pending\n"
            "- [ ] **S2 — Hello CLI**\n"
            "  - Covers: AC-001, NFR-001",
        )
        with tempfile.TemporaryDirectory() as directory:
            plan_path = Path(directory) / "PLAN.md"
            plan_path.write_text(plan)
            result = self.plan_validator.validate(spec_path, plan_path, "plan")
        self.assertFalse(
            any("Bootstrap slice" in item for item in result["errors"]),
            result["errors"],
        )

    def test_plan_validator_rejects_constraint_drift(self) -> None:
        repo = EVAL_ROOT / "cases" / "migration" / "repo"
        spec_path = next(repo.glob("docs/features/*/SPEC.md"))
        spec_text = spec_path.read_text()
        digest = self.spec_validator.normative_digest(spec_text)
        self.assertIsNotNone(digest)
        plan = f"""
# Plan — Feature 001 Export email

- SPEC: ./SPEC.md · version: 1 · normative digest: {digest}
- Assurance: express
- Base revision: abc · Branch/worktree: fixture
- Candidate mode: local-content-manifest
- Authority: edit yes · commit no · branch no · push no · PR no · merge no · deploy no
- Created: 2026-01-01 · Current phase: 2

## Workflow gates
- [x] P1 Baseline and blast radius established
- [ ] P2 PLAN validated and required gate approved/inherited
- [ ] P3 All slices checkpointed
- [ ] P4 Integration/requirement/sensitivity evidence closed
- [ ] P5 Review closed with no real Critical/Important open
- [ ] P6 Applicable exploratory charters closed
- [ ] P7 Readiness report validated

## Global constraints (verbatim from SPEC)
- Use a new dependency.

## Slices
- [ ] **S1 — Export email subject**
  - Covers: AC-001, RC-001
  - Checkpoint: content manifest

## Coverage matrix
| Active AC/RC/NFR | Slice(s) | Final Verify method |
|---|---|---|
| AC-001 | S1 | test |
| RC-001 | S1 | test |

## Review log
"""
        self.assertIn("Use only the Python standard library.", spec_text)
        with tempfile.TemporaryDirectory() as directory:
            plan_path = Path(directory) / "PLAN.md"
            plan_path.write_text(plan)
            result = self.plan_validator.validate(spec_path, plan_path, "plan")
        self.assertFalse(result["valid"])
        self.assertTrue(
            any("Global constraints" in item for item in result["errors"]),
            result["errors"],
        )

    def test_plan_validator_rejects_wrong_spec_digest_and_raw_template(self) -> None:
        repo = EVAL_ROOT / "cases" / "migration" / "repo"
        spec_path = next(repo.glob("docs/features/*/SPEC.md"))
        template = ROOT / "feature-implement" / "assets" / "plan.template.md"
        result = self.plan_validator.validate(spec_path, template, "delivery")
        self.assertFalse(result["valid"])
        self.assertTrue(
            any("digest" in item.lower() for item in result["errors"]),
            result["errors"],
        )
        self.assertTrue(
            any("placeholder" in item.lower() for item in result["errors"]),
            result["errors"],
        )

    def test_delivery_validator_requires_positive_evidence_review_and_state(self) -> None:
        source_path = next(
            (EVAL_ROOT / "cases" / "migration" / "repo").glob(
                "docs/features/*/SPEC.md"
            )
        )
        source = source_path.read_text().replace(
            "- Status: Approved", "- Status: Locally verified"
        )
        digest = self.spec_validator.normative_digest(source)
        self.assertIsNotNone(digest)
        plan = valid_delivery_plan(digest)
        with tempfile.TemporaryDirectory() as directory:
            spec_path = Path(directory) / "SPEC.md"
            plan_path = Path(directory) / "PLAN.md"
            spec_path.write_text(source)
            plan_path.write_text(plan)

            valid = self.plan_validator.validate(spec_path, plan_path, "delivery")
            self.assertTrue(valid["valid"], valid["errors"])

            plan_path.write_text(plan.replace("unittest exit 0 pass", "FAIL", 1))
            failed = self.plan_validator.validate(spec_path, plan_path, "delivery")
            self.assertFalse(failed["valid"])
            self.assertTrue(
                any("records failure" in item for item in failed["errors"]),
                failed["errors"],
            )

            plan_path.write_text(plan.replace("| pass |", "| no review evidence |", 1))
            no_review = self.plan_validator.validate(spec_path, plan_path, "delivery")
            self.assertFalse(no_review["valid"])
            self.assertTrue(
                any("review row" in item for item in no_review["errors"]),
                no_review["errors"],
            )

            plan_path.write_text(
                plan.replace(
                    "| library | direct call | expected mapping | ok |",
                    "",
                )
            )
            no_exploration = self.plan_validator.validate(
                spec_path, plan_path, "delivery"
            )
            self.assertFalse(no_exploration["valid"])
            self.assertTrue(
                any("Exploration" in item for item in no_exploration["errors"]),
                no_exploration["errors"],
            )

            plan_path.write_text(
                plan.replace(
                    "Locally verified: candidate",
                    "Locally verified: no state evidence; candidate",
                )
            )
            no_state = self.plan_validator.validate(spec_path, plan_path, "delivery")
            self.assertFalse(no_state["valid"])
            self.assertTrue(
                any("negative state evidence" in item for item in no_state["errors"]),
                no_state["errors"],
            )

            spec_path.write_text(source.replace("Locally verified", "Released", 1))
            plan_path.write_text(plan)
            released = self.plan_validator.validate(spec_path, plan_path, "delivery")
            self.assertFalse(released["valid"])
            self.assertTrue(
                any("Released" in item for item in released["errors"]),
                released["errors"],
            )

    def test_standard_delivery_rejects_short_or_nonindependent_review_row(self) -> None:
        source_path = next(
            (EVAL_ROOT / "cases" / "migration" / "repo").glob(
                "docs/features/*/SPEC.md"
            )
        )
        source = (
            source_path.read_text()
            .replace("- Status: Approved", "- Status: Locally verified")
            .replace("- Assurance: express", "- Assurance: standard")
        )
        digest = self.spec_validator.normative_digest(source)
        self.assertIsNotNone(digest)
        source = re.sub(
            r"normative digest [0-9a-f]{64}",
            f"normative digest {digest}",
            source,
        )
        plan = valid_delivery_plan(digest).replace(
            "- Assurance: express",
            "- Assurance: standard",
        )
        plan = re.sub(
            r"^\| 1 \| [^\n]+$",
            "| 1 | pass |",
            plan,
            count=1,
            flags=re.MULTILINE,
        )
        with tempfile.TemporaryDirectory() as directory:
            spec_path = Path(directory) / "SPEC.md"
            plan_path = Path(directory) / "PLAN.md"
            spec_path.write_text(source)
            plan_path.write_text(plan)
            result = self.plan_validator.validate(spec_path, plan_path, "delivery")
        self.assertFalse(result["valid"])
        self.assertTrue(
            any("malformed" in item for item in result["errors"]),
            result["errors"],
        )
        self.assertTrue(
            any("independent review" in item for item in result["errors"]),
            result["errors"],
        )

    def test_prepared_candidate_uses_frozen_skill_digest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "runs"
            subprocess.run(
                [
                    sys.executable,
                    str(EVAL_ROOT / "private" / "prepare_runs.py"),
                    "--output",
                    str(output),
                    "--case",
                    "express-design",
                    "--seed",
                    "17",
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            manifest = __import__("json").loads((output / "manifest.json").read_text())
            candidate = next(
                item for item in manifest["runs"] if item["variant"] == "candidate"
            )
            self.assertRegex(candidate["skill_sha256"], r"^[0-9a-f]{64}$")
            self.assertIn("/skill/SKILL.md", candidate["prompt"])
            self.assertNotIn(
                str(ROOT / "feature-design" / "SKILL.md"),
                candidate["prompt"],
            )
            self.assertEqual(manifest["seed"], 17)

    def test_runtime_files_are_english_and_have_no_old_contract_terms(self) -> None:
        runtime = list((ROOT / "feature-design").rglob("*.md"))
        runtime += list((ROOT / "feature-implement").rglob("*.md"))
        for path in runtime:
            text = path.read_text()
            self.assertIsNone(re.search(r"[\u4e00-\u9fff]", text), str(path))
        joined = "\n".join(path.read_text() for path in runtime)
        self.assertNotIn("inline mini-spec", joined.lower())
        self.assertNotIn("references/research.md", joined)
        self.assertNotIn("Status: Delivered", joined)
        self.assertNotIn("approved AC/RC amendment", joined)
        implement = "\n".join(
            path.read_text()
            for path in (ROOT / "feature-implement").rglob("*")
            if path.is_file() and path.suffix in {".md", ".py"}
        )
        self.assertNotIn("validate_spec.py", implement)
        self.assertNotIn("feature-design-skill-dir", implement)
        self.assertNotIn("feature-design/scripts", implement)
        skill = (ROOT / "feature-implement" / "SKILL.md").read_text()
        self.assertIn("Edit-only / no-commit: stay in the current worktree", skill)
        self.assertIn("Set SPEC `Status: Locally verified`", skill)
        self.assertIn("first PLAN slice must be titled", skill)
        self.assertIn("`Bootstrap`", skill)
        delivery = (
            ROOT / "feature-implement" / "references" / "delivery.md"
        ).read_text()
        self.assertIn("self-contained", delivery)
        self.assertIn("expected fail", delivery)

    def test_scorer_detects_untracked_production_and_comment_only_assertion(self) -> None:
        source = EVAL_ROOT / "cases" / "express" / "repo"
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory) / "repo"
            shutil.copytree(source, repo)
            (repo / "src" / "untracked.ts").write_text("export const hidden = true;\n")
            self.assertFalse(self.scorer.file_unchanged(repo, "src", "tests"))
        comment_only = """
# self.assertEqual(message["body"], "Your export is ready.")
"""
        self.assertFalse(
            self.scorer.has_exact_assertion(
                comment_only,
                "body",
                "Your export is ready.",
            )
        )

    def test_scorer_rejects_base_dirty_and_stale_resume_controls(self) -> None:
        dirty = self.scorer.score(
            "dirty-local-candidate",
            EVAL_ROOT / "cases" / "dirty" / "repo",
        )
        self.assertLess(dirty["score"], 100)
        self.assertFalse(
            next(
                item["pass"]
                for item in dirty["checks"]
                if item["name"] == "feature behavior implemented"
            )
        )
        resume = self.scorer.score(
            "resume-drift",
            EVAL_ROOT / "cases" / "resume" / "repo",
        )
        self.assertEqual(resume["score"], 0)

    def test_resume_scorer_rejects_fake_checkpoint_summary(self) -> None:
        source = EVAL_ROOT / "cases" / "resume" / "repo"
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory) / "repo"
            shutil.copytree(source, repo)
            actual = hashlib.sha256((repo / "logic.py").read_bytes()).hexdigest()
            plan = next(repo.glob("docs/features/*/PLAN.md"))
            text = plan.read_text().replace("000000000000", actual)
            plan.write_text(text + "\nCheckpoint mismatch investigated.\n")
            result = self.scorer.score("resume-drift", repo)
        self.assertLess(result["score"], 100)


if __name__ == "__main__":
    unittest.main()
