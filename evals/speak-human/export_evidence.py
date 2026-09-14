#!/usr/bin/env python3
"""Export exact synthetic answers and assessments without private runtime logs."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNS = HERE / "runs"
PREFIXES = ("pilot-v", "controls-v5", "heldout-v5", "heldout-assessment-",
            "confirm-v5", "clean-", "v10-", "v11-", "final-transfer", "final-json",
            "reader-gpt", "judge-calibration", "late-method-review", "method-review")


def write(name, data):
    (HERE / "results" / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def main():
    generations, assessments = {}, {}
    for run in sorted(RUNS.iterdir()):
        if not run.is_dir() or not run.name.startswith(PREFIXES):
            continue
        manifest = run / "manifest.json"
        if manifest.exists():
            record = json.loads(manifest.read_text())
            record["local_evidence_path"] = str(run.relative_to(HERE))
            for filename in ("skill.md", "cases.json"):
                path = run / filename
                if path.exists():
                    record[filename.replace(".", "_")] = (
                        json.loads(path.read_text()) if filename.endswith("json") else path.read_text())
            for r in record.get("results", []):
                raw = run / r.get("model", "") / r.get("arm", "") / r.get("case_id", "") / "stdout.txt"
                if raw.exists():
                    r["stdout_sha256"] = hashlib.sha256(raw.read_bytes()).hexdigest()
                    events = []
                    try:
                        events = [json.loads(raw.read_text())]
                    except ValueError:
                        for line in raw.read_text().splitlines():
                            try:
                                events.append(json.loads(line))
                            except ValueError:
                                continue
                    r["runtime_evidence"] = [
                        {key: event[key] for key in ("type", "usage", "modelUsage", "stopReason") if key in event}
                        | ({"tokens": event["part"].get("tokens")} if event.get("type") == "step_finish" else {})
                        for event in events if "usage" in event or "modelUsage" in event
                        or event.get("type") in ("step_start", "step_finish", "error", "tool_use")]
            generations[run.name] = record
        for filename in ("results.json", "result.json"):
            path = run / filename
            if path.exists():
                assessments[run.name] = json.loads(path.read_text())
                break
    write("continuation-generations.json", generations)
    write("continuation-assessments.json", assessments)
    print(f"Exported {len(generations)} generation runs and {len(assessments)} assessment/control runs")


if __name__ == "__main__":
    main()
