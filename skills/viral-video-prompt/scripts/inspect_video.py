#!/usr/bin/env python3
"""Break a reference video into facts an agent can read: metadata, cut points,
one frame per beat, and a contact sheet. Requires ffmpeg and ffprobe on PATH;
no Python dependencies.

Usage:
    python3 inspect_video.py VIDEO --out DIR [--fps 1] [--scene 0.3] [--max-frames 24]

Writes into DIR:
    meta.json        duration, size, fps, audio presence, cut timestamps
    frame_XX.jpg     one frame per second (or per --fps), 360px wide
    sheet.jpg        contact sheet of up to 24 frames, read it first
    summary.md       the same facts as prose for the notes file

Exit 2 when ffmpeg/ffprobe are missing; exit 1 on a bad input path.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True, check=False)


def probe(video: Path) -> dict:
    out = run([
        "ffprobe", "-v", "error", "-show_entries",
        "stream=codec_type,width,height,r_frame_rate,duration,nb_frames",
        "-show_entries", "format=duration,size", "-of", "json", str(video),
    ])
    if out.returncode != 0:
        sys.exit(f"ffprobe failed: {out.stderr.strip()}")
    data = json.loads(out.stdout or "{}")
    video_stream = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), {})
    has_audio = any(s.get("codec_type") == "audio" for s in data.get("streams", []))
    fps_text = video_stream.get("r_frame_rate", "0/1")
    num, _, den = fps_text.partition("/")
    fps = round(float(num) / float(den or 1), 2) if den not in ("", "0") else float(num or 0)
    duration = float(data.get("format", {}).get("duration") or video_stream.get("duration") or 0)
    return {
        "duration_s": round(duration, 2),
        "width": video_stream.get("width"),
        "height": video_stream.get("height"),
        "fps": fps,
        "has_audio": has_audio,
        "size_bytes": int(data.get("format", {}).get("size") or 0),
    }


def scene_cuts(video: Path, threshold: float) -> list[float]:
    out = run([
        "ffmpeg", "-loglevel", "info", "-i", str(video), "-vf",
        f"select='gt(scene,{threshold})',showinfo", "-f", "null", "-",
    ])
    return [round(float(m), 2) for m in re.findall(r"pts_time:([0-9.]+)", out.stderr)]


def extract_frames(video: Path, out_dir: Path, fps: float, max_frames: int) -> list[str]:
    for old in out_dir.glob("frame_*.jpg"):
        old.unlink()
    run([
        "ffmpeg", "-loglevel", "error", "-y", "-i", str(video), "-vf",
        f"fps={fps},scale=360:-2", "-frames:v", str(max_frames),
        str(out_dir / "frame_%02d.jpg"),
    ])
    return sorted(p.name for p in out_dir.glob("frame_*.jpg"))


def contact_sheet(video: Path, out_dir: Path, duration: float, max_frames: int) -> str | None:
    cols = 6
    tiles = max(1, min(max_frames, cols * 4))
    fps = tiles / duration if duration > 0 else 1
    rows = max(1, -(-tiles // cols))
    out = run([
        "ffmpeg", "-loglevel", "error", "-y", "-i", str(video), "-vf",
        f"fps={fps:.4f},scale=240:-2,tile={cols}x{rows}", "-frames:v", "1",
        str(out_dir / "sheet.jpg"),
    ])
    return "sheet.jpg" if out.returncode == 0 and (out_dir / "sheet.jpg").exists() else None


def orientation(width: int | None, height: int | None) -> str:
    if not width or not height:
        return "unknown"
    ratio = width / height
    if ratio < 0.7:
        return "vertical (9:16-like)"
    if ratio > 1.4:
        return "horizontal (16:9-like)"
    return "square-ish"


def write_summary(out_dir: Path, meta: dict, cuts: list[float], frames: list[str], sheet: str | None) -> None:
    shots = len(cuts) + 1
    duration = meta["duration_s"] or 0
    avg_shot = round(duration / shots, 2) if shots else duration
    lines = [
        "# Reference video facts",
        "",
        f"- Duration: {duration}s · {meta['width']}x{meta['height']} · {orientation(meta['width'], meta['height'])} · {meta['fps']} fps · audio: {'yes' if meta['has_audio'] else 'no'}",
        f"- Detected cuts: {len(cuts)} → about {shots} shots, average shot {avg_shot}s",
        f"- Cut timestamps (s): {', '.join(str(c) for c in cuts) if cuts else 'none above threshold (single take or slow dissolves)'}",
        f"- Frames: {len(frames)} files (`frame_01.jpg` = first second); contact sheet: {sheet or 'not produced'}",
        "",
        "Read `sheet.jpg` first for the arc, then `frame_01.jpg` alone for the hook frame.",
        "Fill the Viral DNA card in references/viral-craft.md from what is seen, and mark",
        "anything inferred from audio as unverified unless the audio was transcribed.",
    ]
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("video")
    parser.add_argument("--out", required=True)
    parser.add_argument("--fps", type=float, default=1.0)
    parser.add_argument("--scene", type=float, default=0.3)
    parser.add_argument("--max-frames", type=int, default=24)
    args = parser.parse_args()

    if not (shutil.which("ffmpeg") and shutil.which("ffprobe")):
        print("ffmpeg/ffprobe not found; view the video another way (inspect-media skill, or ask the user for a frame grab)", file=sys.stderr)
        return 2
    video = Path(args.video).expanduser()
    if not video.is_file():
        print(f"not a file: {video}", file=sys.stderr)
        return 1
    out_dir = Path(args.out).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)

    meta = probe(video)
    cuts = scene_cuts(video, args.scene)
    frames = extract_frames(video, out_dir, args.fps, args.max_frames)
    sheet = contact_sheet(video, out_dir, meta["duration_s"], args.max_frames)
    (out_dir / "meta.json").write_text(json.dumps({**meta, "cuts_s": cuts, "frames": frames, "sheet": sheet}, indent=2), encoding="utf-8")
    write_summary(out_dir, meta, cuts, frames, sheet)
    print((out_dir / "summary.md").read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
