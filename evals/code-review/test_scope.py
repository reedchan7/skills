#!/usr/bin/env python3
"""Behavioral tests for the read-only scope collector using disposable Git repos."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[2] / "skills/code-review/scripts/review_scope.py"


class ScopeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="review-scope-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.git("init", "-q")
        self.git("config", "user.name", "Scope Test")
        self.git("config", "user.email", "scope@example.invalid")
        self.git("config", "core.hooksPath", "/dev/null")
        self.write("app.txt", "original\n")
        self.commit("initial")

    def git(self, *args):
        return subprocess.check_output(["git", *args], cwd=self.repo).decode().strip()

    def write(self, name, content):
        path = self.repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)

    def commit(self, message):
        self.git("add", "-A")
        self.git("commit", "-qm", message)
        return self.git("rev-parse", "HEAD")

    def collect(self, *args, expected=0):
        run = subprocess.run([sys.executable, str(SCRIPT), "--repo", str(self.repo), *args], text=True, capture_output=True)
        self.assertEqual(run.returncode, expected, run.stderr or run.stdout)
        return json.loads(run.stderr if expected == 1 else run.stdout)

    def save(self, snapshot):
        path = self.root / "scope.json"
        path.write_text(json.dumps(snapshot))
        return str(path)

    def test_keeps_staged_revert_and_untracked_inventory(self):
        self.write("app.txt", "staged\n")
        self.git("add", "app.txt")
        self.write("app.txt", "original\n")
        self.write("new file\nname.txt", "new\n")
        scope = self.collect("--local")
        self.assertEqual(scope["changes"]["combined"], [])
        self.assertEqual(scope["changes"]["staged"], [{"path": "app.txt", "status": "M"}])
        self.assertEqual(scope["changes"]["unstaged"], [{"path": "app.txt", "status": "M"}])
        self.assertEqual(scope["changes"]["untracked"], ["new file\nname.txt"])

    def test_detects_content_drift_with_unchanged_status(self):
        self.write("app.txt", "first change\n")
        before = self.collect("--local")
        saved = self.save(before)
        self.write("app.txt", "other change\n")
        after = self.collect("--recheck", saved, expected=2)
        self.assertEqual(before["status_sha256"], after["current"]["status_sha256"])
        self.assertEqual(after["changed_paths"], ["app.txt"])

    def test_detects_index_drift_when_working_bytes_unchanged(self):
        self.write("app.txt", "staged one\n")
        self.git("add", "app.txt")
        self.write("app.txt", "working\n")
        before = self.collect("--local")
        saved = self.save(before)
        self.write("app.txt", "staged two\n")
        self.git("add", "app.txt")
        self.write("app.txt", "working\n")
        after = self.collect("--recheck", saved, expected=2)
        self.assertEqual(after["changed_paths"], [])
        self.assertIn("index_sha256", after["changed_fields"])

    def test_context_drift_in_ignored_file(self):
        self.write(".gitignore", "config.local\n")
        self.commit("ignore local config")
        self.write("config.local", "mode=one\n")
        saved = self.save(self.collect("--local", "--context-path", "config.local"))
        self.write("config.local", "mode=two\n")
        after = self.collect("--recheck", saved, expected=2)
        self.assertEqual(after["changed_paths"], ["config.local"])

    def test_rename_delete_mode_and_symlink(self):
        self.write("remove.txt", "remove\n")
        self.commit("extra file")
        self.git("mv", "app.txt", "renamed file.txt")
        (self.repo / "remove.txt").unlink()
        (self.repo / "renamed file.txt").chmod(0o755)
        (self.repo / "link").symlink_to("renamed file.txt")
        scope = self.collect("--local")
        self.assertEqual(scope["changes"]["staged"][0]["old_path"], "app.txt")
        self.assertEqual(scope["files"]["remove.txt"]["kind"], "missing")
        self.assertEqual(scope["files"]["renamed file.txt"]["mode"], 0o755)
        self.assertEqual(scope["files"]["link"]["kind"], "symlink")

    def test_exact_endpoints_differ_from_merge_base(self):
        original = self.git("rev-parse", "HEAD")
        self.write("app.txt", "left\n")
        left = self.commit("left change")
        self.git("checkout", "-q", "--detach", original)
        self.write("right.txt", "right\n")
        right = self.commit("right change")
        exact = self.collect("--base", left, "--head", right)
        branch = self.collect("--base", left, "--head", right, "--merge-base")
        self.assertEqual({r["path"] for r in exact["changes"]["committed"]}, {"app.txt", "right.txt"})
        self.assertEqual({r["path"] for r in branch["changes"]["committed"]}, {"right.txt"})
        self.assertEqual(branch["revisions"]["base"], original)

    def test_no_index_ref_or_working_mutations(self):
        self.write("app.txt", "changed\n")
        index = (self.repo / ".git/index").read_bytes()
        head = self.git("rev-parse", "HEAD")
        saved = self.save(self.collect("--local"))
        self.assertTrue(self.collect("--recheck", saved)["unchanged"])
        self.assertEqual((self.repo / ".git/index").read_bytes(), index)
        self.assertEqual(self.git("rev-parse", "HEAD"), head)
        self.assertEqual((self.repo / "app.txt").read_text(), "changed\n")

    def test_rejects_invalid_and_mixed_targets(self):
        self.assertIn("error", self.collect("--base", "unknown", "--head", "HEAD", expected=1))
        self.assertIn("error", self.collect("--local", "--merge-base", expected=1))
        self.assertIn("error", self.collect("--local", "--context-path", "../outside", expected=1))

    def test_does_not_follow_external_symlink(self):
        outside = self.root / "outside"
        outside.mkdir()
        (outside / "secret").write_text("not to be read")
        (self.repo / "external").symlink_to(outside, target_is_directory=True)
        scope = self.collect("--local")
        self.assertEqual(scope["files"]["external"]["kind"], "symlink")
        error = self.collect("--local", "--context-path", "external/secret", expected=1)
        self.assertIn("outside", error["error"])
        self.assertNotIn("not to be read", error["error"])

    def test_unborn_branch(self):
        fresh = self.root / "fresh"
        fresh.mkdir()
        self.repo = fresh
        self.git("init", "-q")
        self.write("first.txt", "first\n")
        self.git("add", "first.txt")
        scope = self.collect("--local")
        self.assertIsNone(scope["revisions"]["head"])
        self.assertEqual(scope["changes"]["staged"], [{"path": "first.txt", "status": "A"}])

    def add_submodule(self):
        origin = self.root / "nested-origin"
        origin.mkdir()
        subprocess.run(["git", "init", "-q", str(origin)], check=True)
        (origin / "value.txt").write_text("one\n")
        subprocess.run(["git", "add", "."], cwd=origin, check=True)
        subprocess.run(["git", "-c", "user.name=Scope Test", "-c", "user.email=scope@example.invalid", "-c", "core.hooksPath=/dev/null", "commit", "-qm", "initial"], cwd=origin, check=True)
        self.git("-c", "protocol.file.allow=always", "submodule", "add", "-q", str(origin), "nested")
        self.commit("add submodule")
        self.git("config", "diff.ignoreSubmodules", "all")
        return self.repo / "nested"

    def test_submodule_ignore_config_cannot_hide_local_limit(self):
        nested = self.add_submodule()
        (nested / "value.txt").write_text("two\n")
        scope = self.collect("--local")
        self.assertTrue(any(r["path"] == "nested" for r in scope["changes"]["unstaged"]))
        self.assertEqual(scope["files"]["nested"]["kind"], "directory")
        self.assertTrue(any("nested" in limit for limit in scope["limits"]))

    def test_submodule_ignore_config_cannot_hide_committed_gitlink(self):
        nested = self.add_submodule()
        base = self.git("rev-parse", "HEAD")
        (nested / "value.txt").write_text("two\n")
        subprocess.run(["git", "-c", "user.name=Scope Test", "-c", "user.email=scope@example.invalid", "-c", "core.hooksPath=/dev/null", "commit", "-qam", "change"], cwd=nested, check=True)
        self.git("add", "nested")
        self.git("commit", "-qm", "update gitlink")
        scope = self.collect("--base", base, "--head", "HEAD")
        self.assertEqual(scope["changes"]["committed"], [{"path": "nested", "status": "M"}])

    def test_unmerged_index_is_visible(self):
        initial = self.git("rev-parse", "HEAD")
        self.write("app.txt", "left\n")
        left = self.commit("left")
        self.git("checkout", "-q", "--detach", initial)
        self.write("app.txt", "right\n")
        self.commit("right")
        subprocess.run(["git", "merge", left], cwd=self.repo, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        scope = self.collect("--local")
        self.assertTrue(any(r["status"] == "U" for r in scope["changes"]["staged"]))


if __name__ == "__main__":
    unittest.main()
