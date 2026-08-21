#!/usr/bin/env bash
# Usage: run.sh <brief-name> <baseline|skilled> [claude|grok] [model] [effort]
# Assembles the arm's prompt (auto-appends briefs/<brief>-fixture.html when
# present) and runs the generator. Prints the output path.
set -euo pipefail
DIR="$(cd "$(dirname "$0")/.." && pwd)"
SKILL="$(cd "$DIR/../.." && pwd)/tasteful-frontend"
BRIEF="$DIR/briefs/$1.txt"; ARM="$2"
CLI="${3:-claude}"; MODEL="${4:-claude-sonnet-5}"; EFFORT="${5:-medium}"
OUT="$DIR/runs/$(date +%F)-$1-$ARM-${CLI}.html"
PROMPT="$(mktemp)"
{
  if [ "$ARM" = skilled ]; then
    echo "You have been given a frontend design skill. Follow it exactly when executing the brief at the end."
    echo; echo "===== SKILL: tasteful-frontend ====="; cat "$SKILL/SKILL.md"
    echo; echo "===== REFERENCE: anti-slop.md ====="; cat "$SKILL/references/anti-slop.md"
    echo; echo "===== REFERENCE: values.md ====="; cat "$SKILL/references/values.md"
    echo; echo "===== BRIEF ====="
  fi
  cat "$BRIEF"
  [ -f "$DIR/briefs/$1-fixture.html" ] && cat "$DIR/briefs/$1-fixture.html"
} > "$PROMPT"
mkdir -p "$DIR/runs"
if [ "$CLI" = grok ]; then
  grok -m "$MODEL" --reasoning-effort "$EFFORT" --prompt-file "$PROMPT" > "$OUT"
else
  claude -p --model "$MODEL" --effort "$EFFORT" < "$PROMPT" > "$OUT"
fi
rm -f "$PROMPT"; echo "$OUT"
