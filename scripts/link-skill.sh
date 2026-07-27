#!/usr/bin/env bash
# link-skill.sh — install a skill from this repo into the shared hub and every
# agent runtime, optionally under a different (published) name.
#
# Usage:
#   scripts/link-skill.sh <source-skill> [install-as]
#
# - One argument:  install <source-skill> under its own name (pure symlink).
# - Two arguments: install <source-skill> under the name <install-as>. The source
#   repo is left untouched; the installed copy's `name:` field and H1 are rewritten
#   to <install-as>, while every other file (references/, assets/, ...) stays a
#   live symlink to the source. Re-run the script to refresh after source edits.
#
# Layout produced:
#   ~/.agents/skills/<install-as>[/SKILL.md, ...]   (the shared hub)
#   <each agent>/skills/<install-as>  ->  hub entry
#
# Idempotent: symlinks are refreshed; a generated SKILL.md is regenerated.
# A pre-existing real file/dir that is not a symlink is left untouched (warning).
#
# Agent runtimes covered: claude code, codex, grok build, zcode, kimi code,
# pi agent, reasonix.

set -euo pipefail

SOURCE_NAME="${1:-}"
INSTALL_NAME="${2:-$SOURCE_NAME}"

if [[ -z "$SOURCE_NAME" ]]; then
	echo "Usage: $0 <source-skill> [install-as]" >&2
	exit 1
fi

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE="$REPO_DIR/$SOURCE_NAME"
HUB_DIR="$HOME/.agents/skills"
HUB_ENTRY="$HUB_DIR/$INSTALL_NAME"

AGENTS=(
	"$HOME/.claude/skills"
	"$HOME/.codex/skills"
	"$HOME/.grok/skills"
	"$HOME/.zcode/skills"
	"$HOME/.kimi-code/skills"
	"$HOME/.pi/agent/skills"
	"$HOME/.reasonix/skills"
)

if [[ ! -f "$SOURCE/SKILL.md" ]]; then
	echo "✗ Source skill not found: $SOURCE/SKILL.md" >&2
	exit 1
fi

# Rewrite the skill's identity lines (frontmatter `name:` and the first H1) from
# the source name to the install name. Only these two lines change; everything
# else is passed through verbatim.
rewrite_skill_md() { # rewrite_skill_md <src-md> <out-md>
	local src="$1" out="$2"
	sed -E \
		-e "s/^name:[[:space:]]*${SOURCE_NAME}[[:space:]]*\$/name: ${INSTALL_NAME}/" \
		-e "s/^# ${SOURCE_NAME}\$/# ${INSTALL_NAME}/" \
		"$src" >"$out"
}

mkdir -p "$HUB_DIR"

if [[ "$INSTALL_NAME" == "$SOURCE_NAME" ]]; then
	# Plain install: symlink the whole source directory into the hub.
	if [[ -L "$HUB_ENTRY" ]]; then
		ln -sfn "$SOURCE" "$HUB_ENTRY"
		echo "  ↻ updated  hub/$INSTALL_NAME (symlink)"
	elif [[ -e "$HUB_ENTRY" ]]; then
		echo "  ✗ hub/$INSTALL_NAME exists and is not a symlink — skipped" >&2
		exit 1
	else
		ln -s "$SOURCE" "$HUB_ENTRY"
		echo "  ✓ created  hub/$INSTALL_NAME (symlink)"
	fi
else
	# Rename install: hub entry is a real dir; SKILL.md is rewritten to the install
	# name, every other entry is symlinked to the source so it stays live.
	if [[ -L "$HUB_ENTRY" ]]; then rm "$HUB_ENTRY"; fi
	if [[ -e "$HUB_ENTRY" && ! -d "$HUB_ENTRY" ]]; then
		echo "  ✗ hub/$INSTALL_NAME exists and is not a dir — skipped" >&2
		exit 1
	fi
	mkdir -p "$HUB_ENTRY"
	rewrite_skill_md "$SOURCE/SKILL.md" "$HUB_ENTRY/SKILL.md"
	echo "  ✓ wrote    hub/$INSTALL_NAME/SKILL.md (name: $INSTALL_NAME)"
	shopt -s nullglob dotglob
	for item in "$SOURCE"/*; do
		base="$(basename "$item")"
		[[ "$base" == "SKILL.md" ]] && continue
		ln -sfn "$item" "$HUB_ENTRY/$base"
		echo "  ↻ linked  hub/$INSTALL_NAME/$base"
	done
	shopt -u nullglob dotglob
fi

echo "  agents:"
for agent in "${AGENTS[@]}"; do
	mkdir -p "$agent"
	if [[ -L "$agent/$INSTALL_NAME" ]]; then
		ln -sfn "$HUB_ENTRY" "$agent/$INSTALL_NAME"
		echo "  ↻ updated  $(basename "$agent")/$INSTALL_NAME"
	elif [[ -e "$agent/$INSTALL_NAME" ]]; then
		echo "  ✗ $(basename "$agent")/$INSTALL_NAME exists (not a symlink) — skipped" >&2
	else
		ln -s "$HUB_ENTRY" "$agent/$INSTALL_NAME"
		echo "  ✓ created  $(basename "$agent")/$INSTALL_NAME"
	fi
done

echo "Done: $SOURCE_NAME → installed as $INSTALL_NAME"
