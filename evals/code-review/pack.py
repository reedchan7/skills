#!/usr/bin/env python3
"""Create a deterministic, answer-free review archive."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import stat
import struct
import sys
import zipfile


ROOT = Path(__file__).resolve().parent
FIXED_TIME = (2024, 1, 1, 0, 0, 0)
SKIP_NAMES = {".DS_Store", "__pycache__"}


def load_manifest() -> dict:
    return json.loads((ROOT / "cases" / "manifest.json").read_text())


def safe_files(source: Path):
    if source.is_symlink():
        raise ValueError(f"symlinks are not allowed: {source}")
    if source.is_file():
        yield source, PurePosixPath(source.name)
        return
    if not source.is_dir():
        raise ValueError(f"skill path does not exist: {source}")
    for path in sorted(source.rglob("*")):
        relative = path.relative_to(source)
        if any(part in SKIP_NAMES or part == ".git" for part in relative.parts):
            continue
        if path.is_symlink():
            raise ValueError(f"symlinks are not allowed: {path}")
        if path.is_file() and path.suffix != ".pyc":
            yield path, PurePosixPath(*relative.parts)


def add_bytes(archive: zipfile.ZipFile, name: str, data: bytes, mode: int = 0o644):
    info = zipfile.ZipInfo(name, FIXED_TIME)
    info.create_system = 3
    info.external_attr = (stat.S_IFREG | mode) << 16
    info.compress_type = zipfile.ZIP_STORED
    archive.writestr(info, data)


def canonical_git_index(data: bytes) -> bytes:
    """Remove mutable stat fields and optional extensions from a v2/v3 index."""
    if len(data) < 32 or data[:4] != b"DIRC":
        raise ValueError("invalid Git index")
    if hashlib.sha1(data[:-20]).digest() != data[-20:]:
        raise ValueError("Git index checksum mismatch")
    version, count = struct.unpack(">II", data[4:12])
    if version not in (2, 3):
        raise ValueError(f"unsupported Git index version: {version}")
    body = bytearray(data[:-20])
    offset = 12
    for _ in range(count):
        start = offset
        if start + 62 > len(body):
            raise ValueError("truncated Git index entry")
        flags = struct.unpack(">H", body[start + 60 : start + 62])[0]
        path_start = start + 62 + (2 if version == 3 and flags & 0x4000 else 0)
        try:
            path_end = body.index(0, path_start)
        except ValueError as error:
            raise ValueError("unterminated Git index path") from error
        entry_size = path_end + 1 - start
        offset = path_end + 1 + (-entry_size % 8)
        body[start : start + 24] = bytes(24)
        body[start + 28 : start + 40] = bytes(12)
    canonical = bytes(body[:offset])
    return canonical + hashlib.sha1(canonical).digest()


def schema(case_ids: list[str]) -> dict:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "additionalProperties": False,
        "required": ["reviews"],
        "properties": {
            "reviews": {
                "type": "array",
                "minItems": len(case_ids),
                "maxItems": len(case_ids),
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["case_id", "findings"],
                    "properties": {
                        "case_id": {"type": "string", "enum": case_ids},
                        "findings": {
                            "type": "array",
                            "maxItems": 20,
                            "items": {
                                "type": "object",
                                "additionalProperties": False,
                                "required": [
                                    "title",
                                    "severity",
                                    "file",
                                    "line",
                                    "body",
                                    "evidence",
                                ],
                                "properties": {
                                    "title": {"type": "string", "minLength": 1},
                                    "severity": {
                                        "type": "string",
                                        "enum": ["critical", "high", "medium", "low"],
                                    },
                                    "file": {"type": "string", "minLength": 1},
                                    "line": {"type": "integer", "minimum": 1},
                                    "body": {"type": "string", "minLength": 1},
                                    "evidence": {
                                        "type": "array",
                                        "items": {"type": "string", "minLength": 1},
                                    },
                                    "category": {"type": "string", "minLength": 1},
                                },
                            },
                        },
                    },
                },
            }
        },
    }


def task_for(split: str, manifest: dict, has_skill: bool) -> dict:
    cases = [case for case in manifest["cases"] if case["split"] == split]
    case_ids = [case["case_id"] for case in cases]
    return {
        "task": "Review every proposed change and report only actionable findings.",
        "split": split,
        "instructions": [
            "Treat each cases/<case_id> directory as an independent Git repository.",
            "Review only HEAD^..HEAD, while reading any unchanged context needed to reason about it.",
            "A case may carry a spec field and a repository may carry its own instruction files "
            "and earlier commits; when present they are part of the review context.",
            "Do not modify repositories or infer that every case must contain a finding.",
            "Use paths relative to the case repository and line numbers from HEAD.",
            "Write finding titles and bodies in English.",
            "Explain both the failure mechanism and its concrete user or system impact.",
            "Each evidence entry must identify a causal location as path:line and may add a short note.",
            "Return only one JSON object matching output_schema, with every case_id exactly once.",
        ],
        "skill": "skill/" if has_skill else None,
        "cases": [
            {
                "case_id": case["case_id"],
                "title": case["title"],
                "repository": f"cases/{case['case_id']}",
                "base": "HEAD^",
                "change": "HEAD",
                "context": case["context"],
            }
            | ({"spec": case["spec"]} if case.get("spec") else {})
            for case in cases
        ],
        "output_schema": schema(case_ids),
    }


def package(split: str, output: Path, skill: Path | None) -> str:
    manifest = load_manifest()
    task = task_for(split, manifest, skill is not None)
    if output.exists():
        raise ValueError(f"refusing to overwrite existing output: {output}")
    resolved_output = output.resolve()
    if resolved_output == ROOT or ROOT in resolved_output.parents:
        raise ValueError("output must be outside the benchmark source tree")
    output.parent.mkdir(parents=True, exist_ok=True)

    # Never pack README.md: it is the custodian document and describes the clean
    # controls, the finding count, and the severity distribution.
    entries: list[tuple[str, bytes, int]] = [
        ("README.md", (ROOT / "CONTENDER.md").read_bytes(), 0o644),
        ("task.json", (json.dumps(task, indent=2, sort_keys=True) + "\n").encode(), 0o644),
    ]
    for case in task["cases"]:
        source = ROOT / "cases" / split / case["case_id"] / "repo"
        for path in sorted(source.rglob("*")):
            if path.is_symlink():
                raise ValueError(f"case contains a symlink: {path}")
            if path.is_file():
                relative = path.relative_to(source).as_posix()
                mode = 0o755 if path.stat().st_mode & 0o111 else 0o644
                data = path.read_bytes()
                if relative == ".git/index":
                    data = canonical_git_index(data)
                entries.append((f"cases/{case['case_id']}/{relative}", data, mode))
    if skill is not None:
        if skill.is_symlink():
            raise ValueError(f"symlinks are not allowed: {skill}")
        skill = skill.resolve()
        private_root = ROOT / "private"
        if skill == private_root or private_root in skill.parents or skill in private_root.parents:
            raise ValueError("benchmark private data cannot be packaged as a skill")
        for path, relative in safe_files(skill):
            target = "skill/SKILL.md" if skill.is_file() else f"skill/{relative.as_posix()}"
            mode = 0o755 if path.stat().st_mode & 0o111 else 0o644
            entries.append((target, path.read_bytes(), mode))

    names = [name for name, _, _ in entries]
    if len(names) != len(set(names)):
        raise ValueError("archive would contain duplicate paths")
    with zipfile.ZipFile(output, "x") as archive:
        for name, data, mode in sorted(entries):
            add_bytes(archive, name, data, mode)
    return hashlib.sha256(output.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", required=True, choices=("calibration", "sealed"))
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--skill", type=Path)
    args = parser.parse_args()
    try:
        digest = package(args.split, args.output, args.skill)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"packaging failed: {error}", file=sys.stderr)
        return 2
    print(json.dumps({"archive": str(args.output), "sha256": digest}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
