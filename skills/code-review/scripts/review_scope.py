#!/usr/bin/env python3
"""Read-only Git review inventory and drift detection. Emits JSON to stdout."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys


def git(repo: Path, *args: str) -> bytes:
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0")
    result = subprocess.run(
        ["git", "--no-pager", "--literal-pathspecs", "-c", "core.fsmonitor=false", *args],
        cwd=repo, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if result.returncode:
        raise ValueError(result.stderr.decode(errors="replace").strip())
    return result.stdout


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def decode(data: bytes) -> str:
    return os.fsdecode(data)


def oid(repo: Path, ref: str) -> str:
    return git(repo, "rev-parse", "--verify", "--end-of-options", ref + "^{commit}").decode().strip()


def changes(repo: Path, *args: str) -> list[dict]:
    parts = git(repo, "diff", "--no-ext-diff", "--no-textconv", "--name-status", "-z", "--find-renames", "--ignore-submodules=none", *args, "--").split(b"\0")
    rows = []
    i = 0
    while i < len(parts) - 1:
        status = parts[i].decode("ascii")
        row = {"status": status, "path": decode(parts[i + 1])}
        i += 2
        if status.startswith(("R", "C")):
            row["old_path"] = row["path"]
            row["path"] = decode(parts[i])
            i += 1
        rows.append(row)
    return rows


def safe_path(repo: Path, relative: str) -> Path:
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts or not path.parts or path.parts[0] == ".git":
        raise ValueError(f"expected a repository-relative content path: {relative!r}")
    full = repo / path
    if not full.parent.resolve().is_relative_to(repo):
        raise ValueError(f"path traverses outside the repository: {relative!r}")
    return full


def file_state(repo: Path, relative: str) -> dict:
    path = safe_path(repo, relative)
    try:
        before = path.lstat()
    except FileNotFoundError:
        return {"kind": "missing"}
    mode = stat.S_IMODE(before.st_mode)
    if stat.S_ISLNK(before.st_mode):
        return {"kind": "symlink", "mode": mode, "sha256": digest(os.fsencode(os.readlink(path)))}
    if stat.S_ISDIR(before.st_mode):
        return {"kind": "directory", "limit": "inspect nested repository/submodule separately"}
    if not stat.S_ISREG(before.st_mode):
        return {"kind": "special", "limit": "content not read"}
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(chunk)
    after = path.lstat()
    if (before.st_ino, before.st_size, before.st_mtime_ns, before.st_mode) != (after.st_ino, after.st_size, after.st_mtime_ns, after.st_mode):
        raise ValueError(f"file changed while reading: {relative!r}; retry capture")
    return {"kind": "file", "mode": mode, "sha256": hasher.hexdigest()}


def local_markers(repo: Path) -> tuple[str | None, bytes, bytes]:
    try:
        head = oid(repo, "HEAD")
    except ValueError:
        if git(repo, "rev-parse", "--is-inside-work-tree").strip() != b"true":
            raise
        # An unborn branch is valid; other HEAD failures must remain visible.
        branch = git(repo, "symbolic-ref", "-q", "HEAD").decode().strip()
        refs = git(repo, "for-each-ref", "--format=%(refname)", branch).decode().splitlines()
        if branch in refs:
            raise
        head = None
    status = git(repo, "status", "--porcelain=v1", "-z", "--untracked-files=all", "--ignore-submodules=none")
    index = git(repo, "ls-files", "--stage", "-z")
    return head, status, index


def capture(repo: Path, target: dict, context: list[str]) -> dict:
    result = {"version": 1, "repo": str(repo), "target": target, "context_paths": sorted(set(context))}
    if target["mode"] == "committed":
        base, head = oid(repo, target["base"]), oid(repo, target["head"])
        comparison = git(repo, "merge-base", base, head).decode().strip() if target["merge_base"] else base
        result["revisions"] = {"requested_base": base, "base": comparison, "head": head}
        result["changes"] = {"committed": changes(repo, comparison, head)}
        result["limits"] = []
        if context:
            raise ValueError("--context-path is for local reviews; read committed context at the frozen OIDs")
        return result
    before = local_markers(repo)
    head, status_bytes, index_bytes = before
    staged_args = ["--cached", head] if head else ["--cached"]
    staged, unstaged = changes(repo, *staged_args), changes(repo)
    combined = changes(repo, head) if head else staged + unstaged
    untracked = [decode(p) for p in git(repo, "ls-files", "--others", "--exclude-standard", "-z").split(b"\0") if p]
    result["revisions"] = {"head": head}
    result["status_sha256"] = digest(status_bytes)
    result["index_sha256"] = digest(index_bytes)
    result["changes"] = {"staged": staged, "unstaged": unstaged, "combined": combined, "untracked": untracked}
    paths = set(untracked) | set(context)
    for row in staged + unstaged:
        paths.add(row["path"])
        if "old_path" in row:
            paths.add(row["old_path"])
    result["files"] = {p: file_state(repo, p) for p in sorted(paths)}
    result["limits"] = [f"{p}: {state['limit']}" for p, state in result["files"].items() if "limit" in state]
    if before != local_markers(repo):
        raise ValueError("HEAD, index, or inventory changed during capture; retry capture")
    return result


def compare(before: dict, after: dict) -> dict:
    old_files, new_files = before.get("files", {}), after.get("files", {})
    drifted_paths = [p for p in sorted(old_files.keys() | new_files.keys()) if old_files.get(p) != new_files.get(p)]
    fields = [key for key in sorted(before.keys() | after.keys()) if before.get(key) != after.get(key)]
    return {"unchanged": not fields, "changed_fields": fields, "changed_paths": drifted_paths, "current": after}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path)
    parser.add_argument("--local", action="store_true")
    parser.add_argument("--base")
    parser.add_argument("--head")
    parser.add_argument("--merge-base", action="store_true")
    parser.add_argument("--context-path", action="append", default=[])
    parser.add_argument("--recheck", type=Path)
    args = parser.parse_args()
    try:
        if args.recheck:
            if args.local or args.base or args.head or args.merge_base or args.context_path:
                raise ValueError("--recheck uses the saved target and context; do not combine target flags")
            before = json.loads(args.recheck.read_text())
            if before.get("version") != 1:
                raise ValueError("unsupported scope manifest version")
            repo = Path(before["repo"]).resolve()
            if args.repo and args.repo.resolve() != repo:
                raise ValueError("--repo differs from the saved scope")
            after = capture(repo, before["target"], before["context_paths"])
            output = compare(before, after)
            code = 0 if output["unchanged"] else 2
        else:
            repo = (args.repo or Path.cwd()).resolve()
            repo = Path(decode(git(repo, "rev-parse", "--show-toplevel")).rstrip("\n")).resolve()
            if args.local:
                if args.base or args.head or args.merge_base:
                    raise ValueError("--local cannot be combined with committed target flags")
                target = {"mode": "local"}
            else:
                if not args.base or not args.head:
                    raise ValueError("provide --local or both --base and --head")
                target = {"mode": "committed", "base": args.base, "head": args.head, "merge_base": args.merge_base}
            output = capture(repo, target, args.context_path)
            code = 0
        print(json.dumps(output, ensure_ascii=True, indent=2, sort_keys=True))
        return code
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=True), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
