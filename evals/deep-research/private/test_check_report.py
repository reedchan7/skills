#!/usr/bin/env python3
"""Self-check for skills/deep-research/scripts/check_report.py against fixtures."""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE.parents[2] / "skills" / "deep-research" / "scripts" / "check_report.py"
FIXTURES = HERE / "fixtures"


def load_module():
    spec = importlib.util.spec_from_file_location("check_report", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules["check_report"] = module
    spec.loader.exec_module(module)
    return module


class CheckReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = load_module()

    def findings(self, report: str, ledger: str | None = None, shape: str = "explain"):
        ledger_path = FIXTURES / ledger if ledger else None
        return self.mod.run(FIXTURES / report, ledger_path, shape)

    def checks(self, findings, level):
        return {f.check for f in findings if f.level == level}

    def test_compliant_report_has_no_fail(self) -> None:
        findings = self.findings("compliant-report.md", "compliant-ledger.md", "explain")
        self.assertEqual(self.checks(findings, "FAIL"), set(), [f.message for f in findings if f.level == "FAIL"])

    def test_ledger_url_normalisation_matches_tracking_params(self) -> None:
        findings = self.findings("compliant-report.md", "compliant-ledger.md")
        self.assertNotIn("ledger", self.checks(findings, "FAIL"))

    def test_defective_report_catches_each_planted_defect(self) -> None:
        findings = self.findings("defective-report.md", "compliant-ledger.md")
        fails = self.checks(findings, "FAIL")
        for expected in ("citations", "sources", "placeholders", "synthesis", "attribution", "ledger"):
            self.assertIn(expected, fails, f"missing FAIL for {expected}")
        messages = "\n".join(f.message for f in findings)
        self.assertIn("[2-9] Additional citations", messages)
        self.assertIn("never-opened", messages)
        self.assertIn("据统计", messages)
        self.assertIn("Studies show", messages)

    def test_uncited_numbers_and_missing_sections_are_warnings(self) -> None:
        findings = self.findings("defective-report.md")
        warns = self.checks(findings, "WARN")
        self.assertIn("numbers", warns)
        self.assertIn("sections", warns)
        self.assertIn("confidence", warns)

    def test_exit_code_reflects_fail(self) -> None:
        self.assertEqual(self.mod.main([str(FIXTURES / "defective-report.md")]), 1)
        self.assertEqual(self.mod.main([str(FIXTURES / "compliant-report.md"), "--ledger", str(FIXTURES / "compliant-ledger.md")]), 0)


if __name__ == "__main__":
    sys.exit(unittest.main(verbosity=2))
