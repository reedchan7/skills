#!/usr/bin/env python3
"""Exercise check_pack.py against the fixture packs.

    python3 evals/viral-video-prompt/private/test_check_pack.py

The compliant pack must pass with zero FAIL. The defective pack must raise one
finding per planted defect: a defect the checker stops catching is a regression.
"""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures"
SKILL = HERE.parent.parent.parent / "skills" / "viral-video-prompt"
CHECKER = SKILL / "scripts" / "check_pack.py"

sys.path.insert(0, str(CHECKER.parent))
import check_pack  # noqa: E402


def run(pack: str) -> tuple[int, dict]:
    result = subprocess.run(
        [sys.executable, str(CHECKER), str(FIXTURES / pack),
         "--limits", str(FIXTURES / "limits.json"), "--json"],
        capture_output=True, text=True, check=False,
    )
    return result.returncode, json.loads(result.stdout or "{}")


class CompliantPack(unittest.TestCase):
    def test_passes_clean(self) -> None:
        code, report = run("good-pack")
        self.assertEqual(report["fail"], 0, f"unexpected FAILs: {report['findings']}")
        self.assertEqual(report["warn"], 0, f"unexpected WARNs: {report['findings']}")
        self.assertEqual(code, 0)


class DefectivePack(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.code, cls.report = run("bad-pack")
        cls.checks = {(f["level"], f["check"]) for f in cls.report["findings"]}

    def test_exit_status_signals_failure(self) -> None:
        self.assertEqual(self.code, 1)

    def test_catches_every_planted_defect(self) -> None:
        planted = [
            ("FAIL", "settings"),        # settings table missing a required row
            ("FAIL", "prompt-length"),   # prompt over the model's character limit
            ("FAIL", "duration"),        # duration outside the model's allowed set
            ("FAIL", "resolution"),      # right value, wrong capitalisation
            ("FAIL", "aspect-ratio"),    # ratio the model does not offer
            ("FAIL", "negative-prompt"), # negative prompt supplied to a model without the field
            ("FAIL", "placeholder"),     # TODO left in the prompt
            ("FAIL", "product-truth"),   # a given attribute dropped from the prompt
            ("FAIL", "ab-pair"),         # a model with A but no B
            ("FAIL", "difference"),      # A and B differ on fewer than four axes
            ("FAIL", "sources"),         # citation with no Sources entry
            ("FAIL", "ledger"),          # claims a rung the ledger does not back
            ("FAIL", "hook-tests"),      # a failed test shipped unchanged; two verdicts absent
            ("FAIL", "concept-decisions"), # no target metric, segment, or proof named
            ("FAIL", "change-density"), # a beat holding longer than three seconds
            ("WARN", "model-syntax"),    # reference syntax the model does not support
            ("WARN", "rationale"),       # no "Why this works"
            ("WARN", "recovery"),        # no "If the result is off"
            ("WARN", "reviewer-note"),   # research file has no reviewer note
            ("WARN", "gaps"),            # research file has no gaps section
            ("WARN", "structure"),       # pack has no README
        ]
        missed = [f"{level} {check}" for level, check in planted if (level, check) not in self.checks]
        self.assertEqual(missed, [], f"defects no longer caught: {missed}")

    def test_shipped_failure_is_named_as_such(self) -> None:
        messages = [f["message"] for f in self.report["findings"] if f["check"] == "hook-tests"]
        self.assertTrue(any("recording a failure is not acting on it" in m for m in messages),
                        f"a concept that failed a test and changed nothing must be called out: {messages}")

    def test_missing_verdicts_are_each_named(self) -> None:
        messages = [f["message"] for f in self.report["findings"] if f["check"] == "hook-tests"]
        for absent in ("generic-swap", "glance"):
            self.assertTrue(any(f"has no {absent} verdict" in m for m in messages),
                            f"an unwritten {absent} verdict must fail the gate: {messages}")

    def test_mechanism_hero_is_not_silently_accepted(self) -> None:
        messages = [f["message"] for f in self.report["findings"]
                    if f["check"] in ("change-density", "concept-decisions")]
        self.assertTrue(any("longer than 3 s" in m for m in messages),
                        f"a beat that holds past three seconds must fail: {messages}")

    def test_negative_block_is_not_read_as_the_prompt(self) -> None:
        length = next(f for f in self.report["findings"] if f["check"] == "prompt-length")
        self.assertIn("288 chars", length["message"],
                      "the checker must measure the Prompt block, not the Negative prompt block")


class HookTestVerdicts(unittest.TestCase):
    """The verdict has to come off the line that records it, not off the first
    line that mentions the test — a concept file discusses its own tests in
    prose, and the lunch pack of the 2026-09-04 real run tripped exactly this."""

    def test_prose_mention_does_not_mask_the_verdict(self) -> None:
        body = (
            "## Concept A - x\n"
            "- The prior draft **failed its own generic-swap test**, which is why this one exists.\n"
            "- **Generic-swap test**: **pass** - the sentence carries this product's dimensions.\n"
            "- **Competitor-frame test**: **pass** - a frame no rival can shoot - in frame one: **yes**\n"
            "- **Glance test**: **pass** - two touching objects, one shorter.\n"
            "- **Hook restatement**: In the first frame I see x; within three seconds y; ...\n"
            "- **On a fail**: no test failed.\n"
            "## Concept B - y\n"
            "- **Generic-swap test**: **pass** - x\n"
            "- **Competitor-frame test**: **pass** - y - in frame one: **yes**\n"
            "- **Glance test**: **pass** - z\n"
            "- **Hook restatement**: ...\n"
            "- **On a fail**: no test failed.\n"
        )
        found = [f for f in check_pack.check_hook_tests(body) if f.check == "hook-tests"]
        self.assertEqual([f.message for f in found], [],
                         "a prose mention of a failure must not be read as this concept's verdict")


class AttributeEquivalents(unittest.TestCase):
    """An English prompt satisfies a Chinese attribute through its declared
    equivalent, and an undeclared attribute still has to appear literally."""

    def terms(self, brief: str):
        return check_pack.product_terms(brief)

    def test_equivalents_are_grouped(self) -> None:
        groups = self.terms(
            "- **Given attributes**: `\u85cf\u9752`, `10\u5bf8`\n"
            "- **Attribute equivalents**: \u85cf\u9752 = navy = deep blue; 10\u5bf8 = 10-inch\n"
        )
        self.assertEqual(groups, [["\u85cf\u9752", "navy", "deep blue"], ["10\u5bf8", "10-inch"]])

    def test_attribute_without_equivalents_stands_alone(self) -> None:
        self.assertEqual(self.terms("- Given attributes: `navy`\n"), [["navy"]])

    def test_unfilled_template_yields_nothing(self) -> None:
        template = (SKILL / "assets" / "brief.template.md").read_text(encoding="utf-8")
        self.assertEqual(self.terms(template), [])


class LedgerIntegrity(unittest.TestCase):
    """The ledger is the pack's auditability guarantee, so the gate has to catch
    a ledger that cannot be verified. These are the two falsifications an
    independent audit of a real run found by hand."""

    def checks(self, entries, research="Degradation ladder: rung 3.", mtime_offset=0, persist=()):
        import json as _json, os, tempfile, time
        with tempfile.TemporaryDirectory() as d:
            pack = Path(d)
            (pack / "requests").mkdir()
            led = pack / "requests" / "ledger.jsonl"
            led.write_text("\n".join(_json.dumps(e) for e in entries) + "\n", encoding="utf-8")
            for name in persist:
                (pack / "requests" / name).write_text("[]", encoding="utf-8")
            if mtime_offset:
                now = time.time() + mtime_offset
                os.utime(led, (now, now))
            return {(f.level, f.check, f.message) for f in check_pack.check_ledger(pack, research)}

    def test_apify_line_without_run_id_fails(self) -> None:
        found = self.checks([
            {"ts": "2026-09-04T04:00:00Z", "service": "apify",
             "op": "clockworks/tiktok-scraper", "result": "10 items", "cost_usd": 0.038},
        ])
        self.assertTrue(any("no run_id" in m for _, _, m in found), found)

    def test_budget_check_is_exempt_from_run_id(self) -> None:
        found = self.checks([
            {"ts": "2026-09-04T04:00:00Z", "service": "apify",
             "op": "GET /v2/users/me/usage/monthly", "result": "used_usd=4.25"},
        ])
        self.assertFalse(any("no run_id" in m for _, _, m in found), found)

    def test_timestamp_after_the_files_own_write_fails(self) -> None:
        found = self.checks([
            {"ts": "2099-01-01T00:00:00Z", "service": "tavily", "op": "search", "result": "8 results"},
        ], research="rung 1.")
        self.assertTrue(any("not observed" in m for _, _, m in found), found)

    def test_named_saved_response_must_exist(self) -> None:
        found = self.checks([
            {"ts": "2026-09-04T04:00:00Z", "service": "tavily", "op": "search",
             "result": "8 results", "saved": "tavily_1.json"},
        ], research="rung 1.")
        self.assertTrue(any("bought twice" in m for _, _, m in found), found)

    def test_a_verifiable_ledger_passes(self) -> None:
        found = self.checks([
            {"ts": "2026-09-04T04:00:00Z", "service": "tavily", "op": "search",
             "result": "8 results", "saved": "tavily_1.json"},
            {"ts": "2026-09-04T04:05:00Z", "service": "apify", "op": "clockworks/tiktok-scraper",
             "run_id": "9fqf1CtjiffwfrpTZ", "result": "10 items", "cost_usd": 0.038,
             "saved": "tiktok_1.json"},
        ], persist=["tavily_1.json", "tiktok_1.json"])
        self.assertEqual(found, set())

    def test_unpersisted_paid_call_warns(self) -> None:
        found = self.checks([
            {"ts": "2026-09-04T04:05:00Z", "service": "apify", "op": "clockworks/tiktok-scraper",
             "run_id": "9fqf1CtjiffwfrpTZ", "result": "10 items", "cost_usd": 0.038},
        ])
        self.assertTrue(any("without paying again" in m for _, _, m in found), found)


if __name__ == "__main__":
    unittest.main(verbosity=2)
