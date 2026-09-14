#!/usr/bin/env python3
"""Calibrate source checks using controlled good/bad answers before trusting a judge."""
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from assess import judge, pair_prompt, SCHEMA

HERE = Path(__file__).resolve().parent
fixtures = [
    {"id": "scope-and-order", "request": "交代当前状态和发布前要做的事。",
     "source": "本地测试通过，尚未发布。仅欧盟区受影响。先备份并确认可恢复，再迁移；任一步失败就停止。",
     "required": ["本地测试通过但未发布", "仅欧盟区", "先确认备份可恢复再迁移，失败停止"],
     "A": "本地测试已通过，尚未发布；这次只影响欧盟区。发布前先备份并确认能恢复，再进行迁移，任何一步失败都应停止。",
     "B": "生产已经上线，全区可用。迁移完成后做一次备份即可。", "bad": "B"},
    {"id": "fluent-invention", "request": "为什么页面还没显示结果？",
     "source": "HTTP 202 表示请求已接收。后台任务还在运行，具体完成时间未知。",
     "required": ["已接收请求，后台还在运行", "完成时间未知"],
     "A": "请求已接收，后台正在处理。五分钟内肯定完成。",
     "B": "HTTP 202 表示请求已经收下；后台任务仍在运行，暂时还不知道什么时候完成。", "bad": "A"},
    {"id": "equivalent-wording", "request": "说明异常和进展。",
     "source": "回归测试有一项失败，重跑通过，但原因未查明。修改尚未提交。",
     "required": ["一项失败后重跑通过，原因未查明", "修改未提交"],
     "A": "修改还没提交。回归测试中有一项先失败、重跑又通过，原因仍在排查。",
     "B": "这次修改尚未提交。回归测试有一项首次失败，单独重跑通过，不过失败原因还没查清。", "bad": None}
]
out = HERE / "runs" / "judge-calibration"
out.mkdir(parents=True, exist_ok=False)
results = []
with ThreadPoolExecutor(max_workers=3) as pool:
    fs = {pool.submit(judge, pair_prompt(f, {"A": f["A"], "B": f["B"]}), SCHEMA, out/f["id"]): f for f in fixtures}
    for future in as_completed(fs):
        f = fs[future]
        r = future.result()
        if r["status"] == "completed":
            flagged = set()
            for a in r["assessment"]["answers"]:
                if any(c["status"] != "present" for c in a["coverage"]) or any(x["material"] for x in a["unsupported"]):
                    flagged.add(a["label"])
            r["expected_flagged"] = [f["bad"]] if f["bad"] else []
            r["actual_flagged"] = sorted(flagged)
            r["passed"] = flagged == set(r["expected_flagged"])
        results.append(dict(r, id=f["id"]))
(out/"results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2))
print([(r["id"], r.get("passed")) for r in results])
