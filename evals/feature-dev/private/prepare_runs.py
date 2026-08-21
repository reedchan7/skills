#!/usr/bin/env python3
"""Prepare byte-identical candidate/control copies for local agent runs."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import random
import shutil


ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parents[1]
SKILLS_ROOT = REPO_ROOT / "skills"


def tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        digest.update(path.relative_to(root).as_posix().encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--case", action="append", dest="cases")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    if args.output.exists():
        if not args.force:
            raise SystemExit(f"refusing to overwrite {args.output}; pass --force")
        shutil.rmtree(args.output)
    args.output.mkdir(parents=True)

    manifest = json.loads((ROOT / "cases" / "manifest.json").read_text())
    selected = [
        case for case in manifest["cases"]
        if not args.cases or case["case_id"] in set(args.cases)
    ]
    skill_digests: dict[str, str] = {}
    for skill_name in ("feature-design", "feature-implement"):
        skill_digests[skill_name] = tree_digest(SKILLS_ROOT / skill_name)

    rng = random.Random(args.seed)
    work = [
        (case, variant)
        for case in selected
        for variant in ("candidate", "control")
    ]
    rng.shuffle(work)
    runs = []
    for index, (case, variant) in enumerate(work):
        source = ROOT / case["repo"]
        opaque = f"run-{index:02d}-{rng.getrandbits(48):012x}"
        run_root = args.output / opaque
        destination = run_root / "repo"
        shutil.copytree(source, destination)
        prompt = case["prompt"]
        skill_digest = None
        if variant == "candidate":
            frozen_skill = run_root / "skill"
            shutil.copytree(SKILLS_ROOT / case["skill"], frozen_skill)
            skill_path = frozen_skill / "SKILL.md"
            skill_digest = tree_digest(frozen_skill)
            if skill_digest != skill_digests[case["skill"]]:
                raise RuntimeError("frozen skill digest mismatch")
            prompt = (
                f"Read and follow {skill_path}. Load its references/assets/scripts "
                "only when the skill instructs you to. " + prompt
            )
        else:
            prompt = (
                "Complete the task using your normal engineering judgment. "
                "Do not read any feature-design or feature-implement skill files. "
                + prompt.replace("Use /feature-design to ", "")
                .replace("Use /feature-implement with ", "Implement ")
                .replace("Resume /feature-implement from ", "Resume from ")
            )
        runs.append(
            {
                "case_id": case["case_id"],
                "variant": variant,
                "repo": str(destination),
                "prompt": prompt,
                "skill_sha256": skill_digest,
            }
        )
    (args.output / "manifest.json").write_text(
        json.dumps(
            {"seed": args.seed, "skill_digests": skill_digests, "runs": runs},
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    print(json.dumps({"runs": len(runs), "output": str(args.output)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
