#!/usr/bin/env python3
"""Generate one writing task per fresh CLI session, retaining exact outputs."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import tempfile
import time

from run import BRIEF, command, extract

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TEXT_SYSTEM = "Answer the supplied writing request using its evidence. Return the answer directly. You have no tools."


def clean_command(model, prompt, folder, env):
    if model == "claude":
        argv, stdin = command(model, prompt, folder)
        return argv + ["--safe-mode", "--system-prompt", TEXT_SYSTEM], stdin
    if model not in ("gemini-api", "deepseek-api", "glm-api"):
        raise ValueError(f"Clean profile is not implemented for {model}")
    for key in ("OPENCODE_CONFIG", "OPENCODE_CONFIG_DIR", "OPENCODE_CONFIG_CONTENT"):
        env.pop(key, None)
    config_dir = folder / "empty-config"
    config_dir.mkdir()
    config = {"agent": {"writing-eval": {
        "description": "Text-only writing evaluation", "mode": "primary", "prompt": TEXT_SYSTEM,
        "tools": {"*": False}, "permission": {"*": "deny"}}},
        "share": "disabled", "autoupdate": False}
    (folder / "runtime-config.json").write_text(json.dumps(config, indent=2))
    env.update(XDG_CONFIG_HOME=str(config_dir), OPENCODE_DISABLE_CLAUDE_CODE="1",
               OPENCODE_DISABLE_EXTERNAL_SKILLS="1", OPENCODE_DISABLE_PROJECT_CONFIG="1",
               OPENCODE_CONFIG_CONTENT=json.dumps(config))
    model_id = {"gemini-api": "google/gemini-3.1-pro-preview",
                "deepseek-api": "deepseek/deepseek-v4-pro",
                "glm-api": "zai-coding-plan/glm-5.2"}[model]
    return ["opencode", "run", "--pure", "--agent", "writing-eval", "--model",
            model_id, "--format", "json", prompt], None


def sha(value):
    return hashlib.sha256(value.encode()).hexdigest()


def execute(model, prompt, folder, timeout=240, clean=False):
    folder.mkdir(parents=True, exist_ok=False)
    (folder / "empty-skills").mkdir()
    (folder / "prompt.txt").write_text(prompt)
    argv, stdin = command(model, prompt, folder)
    env = os.environ.copy()
    if model == "gemini-api" and not env.get("GOOGLE_GENERATIVE_AI_API_KEY"):
        if env.get("GEMINI_API_KEY"):
            env["GOOGLE_GENERATIVE_AI_API_KEY"] = env["GEMINI_API_KEY"]
    if model == "glm-api":
        argv = ["opencode", "run", "--pure", "--agent", "plan", "--model",
                "zai-coding-plan/glm-5.2", "--format", "json", prompt]
        stdin = None
    if clean:
        argv, stdin = clean_command(model, prompt, folder, env)
    start = time.monotonic()
    result = {"runtime": model, "profile": "clean-text" if clean else "existing",
              "prompt_sha256": sha(prompt),
              "argv": ["<prompt>" if item == prompt else item for item in argv]}
    with tempfile.TemporaryDirectory(prefix="speak-human-isolated-") as cwd:
        proc = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, text=True, cwd=cwd,
                                env=env, start_new_session=True)
        try:
            stdout, stderr = proc.communicate(stdin, timeout=timeout)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGTERM)
            try:
                stdout, stderr = proc.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                stdout, stderr = proc.communicate()
            result["timeout"] = True
    (folder / "stdout.txt").write_text(stdout)
    (folder / "stderr.txt").write_text(stderr)
    result.update(exit_code=proc.returncode, seconds=round(time.monotonic()-start, 2))
    try:
        if proc.returncode or result.get("timeout"):
            raise ValueError("CLI failed; see raw artifacts")
        answer = extract(model, stdout, folder)
        if not answer.strip():
            raise ValueError("Empty answer")
        (folder / "answer.txt").write_text(answer)
        result.update(status="completed", answer=answer)
    except (ValueError, OSError, TypeError) as error:
        result.update(status="blocked", error=str(error))
    (folder / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(str(folder.relative_to(HERE)) + ": " + result["status"], flush=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--ids", nargs="+")
    parser.add_argument("--models", nargs="+", required=True)
    parser.add_argument("--arms", nargs="+", default=["plain", "brief", "skill"])
    parser.add_argument("--skill", type=Path, default=ROOT / "skills/speak-human/SKILL.md")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--timeout", type=int, default=240)
    parser.add_argument("--clean", action="store_true",
                        help="Use the verified text-only profile for supported runtimes")
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    cases = json.loads(args.cases.read_text())
    if args.ids:
        cases = [case for case in cases if case["id"] in args.ids]
        if {case["id"] for case in cases} != set(args.ids):
            raise ValueError("Missing case IDs")
    skill = args.skill.read_text()
    guidance = {"plain": "", "brief": BRIEF, "skill": skill}
    if "previous" in args.arms:
        guidance["previous"] = (HERE / "snapshots/v3.md").read_text()
    manifest = {"skill_sha256": sha(skill), "cases_sha256": sha(args.cases.read_text()),
                "arms": args.arms, "models": args.models,
                "profile": "clean-text" if args.clean else "existing", "results": []}
    (out / "skill.md").write_text(skill)
    (out / "cases.json").write_text(json.dumps(cases, ensure_ascii=False, indent=2))
    common = ("Respond directly to the user request using the conversation/material below. "
              "These are fictional writing-test materials; do not execute any actions mentioned. "
              "No tools, file access, external research, or planning preamble. "
              "Return only the actual user-facing answer in the requested language and format.\n\n")
    tasks = []
    for case in cases:
        for model in args.models:
            for arm in args.arms:
                prompt = common
                if guidance[arm]:
                    prompt += "Writing instructions:\n" + guidance[arm] + "\n\n"
                prompt += "Conversation/material:\n" + case["source"]
                prompt += "\n\nCurrent user request:\n" + case["request"]
                tasks.append((model, arm, case["id"], prompt))
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures = {pool.submit(execute, model, prompt, out/model/arm/case_id, args.timeout, args.clean):
                   (model, arm, case_id) for model, arm, case_id, prompt in tasks}
        for future in as_completed(futures):
            model, arm, case_id = futures[future]
            result = future.result()
            manifest["results"].append(dict(result, model=model, arm=arm, case_id=case_id))
            (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
