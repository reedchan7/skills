#!/usr/bin/env python3
"""Self-check for skills/deep-research/scripts/renumber_citations.py."""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE.parents[2] / "skills" / "deep-research" / "scripts" / "renumber_citations.py"

LEDGER = """## Sources
- S3 | Vendor docs | https://example.com/docs | type: first-party-docs | tier: A | published: 2026-01 | accessed: 2026-09-02 | fetched | stance/notes: option defaults
- S7 | Filing 10-K | https://example.com/10k | type: filing | tier: A | published: 2026-02 | accessed: 2026-09-02 | fetched
- S12 | Blog post | https://example.org/post | type: expert-commentary | tier: B | published: 2025-11 | accessed: 2026-09-02 | fetched | note: critic's view
- S20 | Snippet only | https://example.net/x | type: community | tier: C | published: 2025 | accessed: 2026-09-02 | snippet-only
"""
DRAFT = "# T\n\n## Answer\nFact one [S12]. Fact two [S3][S12]. Fact three [S3, S7].\n\n## Sources\n[old] stale\n"


def load_module():
    spec = importlib.util.spec_from_file_location("renumber_citations", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules["renumber_citations"] = module
    spec.loader.exec_module(module)
    return module


class RenumberTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = load_module()

    def run_script(self, draft: str) -> tuple[int, str]:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "draft.md").write_text(draft, encoding="utf-8")
            (root / "ledger.md").write_text(LEDGER, encoding="utf-8")
            code = self.mod.main([str(root / "draft.md"), str(root / "ledger.md"), "-o", str(root / "report.md")])
            output = (root / "report.md").read_text(encoding="utf-8") if (root / "report.md").exists() else ""
            return code, output

    def test_numbers_follow_first_appearance_and_sources_are_generated(self) -> None:
        code, output = self.run_script(DRAFT)
        self.assertEqual(code, 0)
        self.assertIn("Fact one [1]. Fact two [2][1]. Fact three [2][3].", output)
        self.assertIn("[1] Blog post, 2025-11. https://example.org/post (accessed 2026-09-02) — contributed: critic's view", output)
        self.assertIn("[3] Filing 10-K, 2026-02. https://example.com/10k (accessed 2026-09-02)", output)
        self.assertNotIn("[old] stale", output)

    def test_refuses_unknown_or_weak_provenance(self) -> None:
        code, output = self.run_script("Claim [S20]. Other [S99].\n")
        self.assertEqual(code, 1)
        self.assertEqual(output, "")


if __name__ == "__main__":
    sys.exit(unittest.main(verbosity=2))
