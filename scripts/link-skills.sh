#!/usr/bin/env bash
# link-skills.sh — one script for the skill hub + every agent runtime.
#
# Usage:
#   ./scripts/link-skills.sh                 # smart full sync (recommended)
#   ./scripts/link-skills.sh <skill>         # one skill from this repo
#   ./scripts/link-skills.sh <skill> <as>    # install under a different local name
#   ./scripts/link-skills.sh <path> [as]     # install from any skill directory
#   ./scripts/link-skills.sh --unlink <name> # remove from hub + agents
#
# Full sync (no args):
#   1. Links personal skills in this repo (with local aliases)
#   2. If a Matt Pocock clone is found, links its skills (with Matt aliases)
#   3. Retires known renames
#   4. Never overwrites a hub name owned by another source
#   5. Sweeps broken hub symlinks
#
# Env: SKILLS_HUB_DIR, MATT_SKILLS_REPO
# macOS /bin/bash 3.2 compatible.

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HUB_DIR="${SKILLS_HUB_DIR:-$HOME/.agents/skills}"
MATT_REPO="${MATT_SKILLS_REPO:-$HOME/Workspaces/github/mattpocock/skills}"

AGENTS=(
	"$HOME/.claude/skills"
	"$HOME/.codex/skills"
	"$HOME/.grok/skills"
	"$HOME/.zcode/skills"
	"$HOME/.kimi-code/skills"
	"$HOME/.pi/agent/skills"
	"$HOME/.reasonix/skills"
	"$HOME/.gemini/skills"
	"$HOME/.gemini/antigravity-cli/skills"
	"$HOME/.gemini/antigravity-ide/skills"
	"$HOME/.dsh/skills"
)

# Per-source install-name overrides: "upstream:install-as"
PERSONAL_ALIASES="
code-review:code-review-pro
"
PERSONAL_EXTRA_ALIASES="
feature-design:new-feature
feature-design:feature-spec
"
MATT_ALIASES="
code-review:matt-code-review
"

# After new name exists, drop the old hub name: "old:new"
RETIRED="
writing-great-skills:writing-for-agents
code-review:code-review-pro
"

# ---------------------------------------------------------------------------

usage() {
	sed -n '2,18p' "$0" | sed 's/^# \{0,1\}//'
	exit 1
}

lookup_alias() {
	local table="$1" upstream="$2" line key val
	while IFS= read -r line; do
		[[ -z "${line// /}" ]] && continue
		key="${line%%:*}"
		val="${line#*:}"
		if [[ "$key" == "$upstream" ]]; then
			printf '%s\n' "$val"
			return 0
		fi
	done <<< "$table"
	printf '%s\n' "$upstream"
}

install_extra_aliases() {
	local source_path="$1" upstream="$2" source_root="$3"
	local line key install_as
	while IFS= read -r line; do
		[[ -z "${line// /}" ]] && continue
		key="${line%%:*}"
		install_as="${line#*:}"
		[[ "$key" == "$upstream" ]] || continue
		install_skill "$source_path" "$install_as" "$source_root" || true
	done <<< "$PERSONAL_EXTRA_ALIASES"
}

realpath_of() {
	python3 -c "import os,sys; print(os.path.realpath(sys.argv[1]))" "$1" 2>/dev/null
}

resolves_under() {
	local hub="$1" root="$2" resolved
	[[ -e "$hub" || -L "$hub" ]] || return 1
	resolved="$(realpath_of "$hub")"
	case "$resolved" in
		"$root"|"$root"/*) return 0 ;;
		*) return 1 ;;
	esac
}

# Leave hub alone when it already belongs to a different source tree.
should_preserve() {
	local install_as="$1" source_root="$2"
	local hub="$HUB_DIR/$install_as"

	[[ -e "$hub" || -L "$hub" ]] || return 1

	# Alias rewrite dir we manage (real dir + rewritten name frontmatter).
	if [[ -d "$hub" && ! -L "$hub" && -f "$hub/SKILL.md" ]]; then
		if grep -q "^name:[[:space:]]*${install_as}[[:space:]]*$" "$hub/SKILL.md" 2>/dev/null; then
			return 1
		fi
	fi

	if resolves_under "$hub" "$source_root"; then
		return 1
	fi
	return 0
}

rewrite_skill_md() {
	local src="$1" out="$2" source_name="$3" install_name="$4"
	sed -E \
		-e "s/^name:[[:space:]]*${source_name}[[:space:]]*\$/name: ${install_name}/" \
		-e "s/^# ${source_name}\$/# ${install_name}/" \
		"$src" >"$out"
}

link_or_rewrite_agents() {
	local src_agents="$1" dst_agents="$2" source_name="$3" install_name="$4"
	local src_yaml="$src_agents/openai.yaml" item base display

	[[ -d "$src_agents" ]] || return 0

	if [[ "$install_name" == "$source_name" || ! -f "$src_yaml" ]]; then
		ln -sfn "$src_agents" "$dst_agents"
		return 0
	fi

	[[ -L "$dst_agents" ]] && rm "$dst_agents"
	mkdir -p "$dst_agents"
	display="$(python3 -c "import sys; print(sys.argv[1].replace('-', ' ').title())" "$install_name")"

	if grep -q '^[[:space:]]*display_name:' "$src_yaml"; then
		sed -E "s/^([[:space:]]*display_name:[[:space:]]*).*/\1\"${display}\"/" \
			"$src_yaml" >"$dst_agents/openai.yaml"
	else
		cp "$src_yaml" "$dst_agents/openai.yaml"
	fi

	shopt -s nullglob
	for item in "$src_agents"/*; do
		base="$(basename "$item")"
		[[ "$base" == "openai.yaml" ]] && continue
		ln -sfn "$item" "$dst_agents/$base"
	done
	shopt -u nullglob
}

link_agent_views() {
	local install_name="$1" hub_entry="$HUB_DIR/$install_name" agent
	local hub_real
	hub_real="$(realpath_of "$HUB_DIR")"
	for agent in "${AGENTS[@]}"; do
		mkdir -p "$agent"
		# An agent dir symlinked to the hub itself is already served by the
		# hub entry; writing through it would turn hub/<name> into a self-loop.
		if [[ -n "$hub_real" && "$(realpath_of "$agent")" == "$hub_real" ]]; then
			continue
		fi
		if [[ -L "$agent/$install_name" ]]; then
			ln -sfn "$hub_entry" "$agent/$install_name"
		elif [[ -e "$agent/$install_name" ]]; then
			echo "  · skip agent view $(basename "$agent")/$install_name (not a symlink)"
		else
			ln -s "$hub_entry" "$agent/$install_name"
		fi
	done
}

unlink_everywhere() {
	local install_name="$1"
	local hub_entry="$HUB_DIR/$install_name"
	local agent
	if [[ -L "$hub_entry" || -e "$hub_entry" ]]; then
		rm -rf "$hub_entry"
		echo "  ✓ removed hub/$install_name"
	fi
	for agent in "${AGENTS[@]}"; do
		if [[ -L "$agent/$install_name" ]]; then
			rm "$agent/$install_name"
		fi
	done
}

install_skill() {
	local source_path="$1"
	local install_name="${2:-}"
	local source_root="${3:-}"
	local source_name hub_entry item base

	[[ -f "$source_path/SKILL.md" ]] || {
		echo "✗ no SKILL.md in $source_path" >&2
		return 1
	}

	source_name="$(basename "$source_path")"
	install_name="${install_name:-$source_name}"
	[[ -n "$source_root" ]] || source_root="$(cd "$(dirname "$source_path")" && pwd)"

	if should_preserve "$install_name" "$source_root"; then
		echo "· preserve $install_name (owned by another source)"
		return 0
	fi

	hub_entry="$HUB_DIR/$install_name"
	mkdir -p "$HUB_DIR"

	if [[ "$install_name" == "$source_name" ]]; then
		if [[ -L "$hub_entry" ]]; then
			ln -sfn "$source_path" "$hub_entry"
			echo "  ↻ $install_name"
		elif [[ -e "$hub_entry" ]]; then
			echo "  · skip $install_name (hub entry not a symlink)"
			return 0
		else
			ln -s "$source_path" "$hub_entry"
			echo "  ✓ $install_name"
		fi
	else
		[[ -L "$hub_entry" ]] && rm "$hub_entry"
		if [[ -e "$hub_entry" && ! -d "$hub_entry" ]]; then
			echo "  · skip $install_name (hub entry not a dir)"
			return 0
		fi
		mkdir -p "$hub_entry"
		rewrite_skill_md "$source_path/SKILL.md" "$hub_entry/SKILL.md" "$source_name" "$install_name"
		echo "  ✓ $install_name  ←  $source_name"

		shopt -s nullglob
		for item in "$hub_entry"/*; do
			base="$(basename "$item")"
			[[ "$base" == "SKILL.md" ]] && continue
			if [[ ! -e "$source_path/$base" && ! -L "$source_path/$base" ]]; then
				if [[ "$base" == "agents" && -d "$item" && ! -L "$item" ]]; then
					continue
				fi
				rm -rf "$item"
			fi
		done
		for item in "$source_path"/*; do
			base="$(basename "$item")"
			[[ "$base" == "SKILL.md" ]] && continue
			if [[ "$base" == "agents" ]]; then
				link_or_rewrite_agents "$item" "$hub_entry/agents" "$source_name" "$install_name"
				continue
			fi
			ln -sfn "$item" "$hub_entry/$base"
		done
		shopt -u nullglob
	fi

	link_agent_views "$install_name"
}

find_skills_under() {
	find "$1" -name SKILL.md \
		-not -path '*/node_modules/*' \
		-not -path '*/deprecated/*' \
		-not -path '*/.git/*' \
		| sort \
		| while IFS= read -r md; do dirname "$md"; done
}

find_personal_skills() {
	local d
	for d in "$REPO_DIR"/*/; do
		[[ -f "${d}SKILL.md" ]] || continue
		printf '%s\n' "${d%/}"
	done | sort
}

sync_tree() {
	local label="$1" root="$2" skills_root="$3" alias_table="$4"
	local src upstream install_as n=0

	echo "== $label =="
	if [[ ! -d "$skills_root" ]]; then
		echo "· skip (not found)"
		return 0
	fi

	while IFS= read -r src; do
		[[ -z "$src" ]] && continue
		upstream="$(basename "$src")"
		install_as="$(lookup_alias "$alias_table" "$upstream")"
		install_skill "$src" "$install_as" "$root" || true
		n=$((n + 1))
	done < <(find_skills_under "$skills_root")

	echo "  ($n considered)"
}

retire_renames() {
	local line old new
	echo "== retire renames =="
	while IFS= read -r line; do
		[[ -z "${line// /}" ]] && continue
		old="${line%%:*}"
		new="${line#*:}"
		# Only drop old if new is present AND old is not an intentional third install.
		if [[ -e "$HUB_DIR/$new" || -L "$HUB_DIR/$new" ]]; then
			if [[ -e "$HUB_DIR/$old" || -L "$HUB_DIR/$old" ]]; then
				# Keep matt alias targets that share the old upstream name key only when
				# the old hub entry is a plain symlink to the retired path-less name.
				echo "→ drop $old  (now $new)"
				unlink_everywhere "$old"
			fi
		fi
	done <<< "$RETIRED"
}

sweep_broken() {
	local entry name target n=0
	echo "== sweep broken =="
	for entry in "$HUB_DIR"/*; do
		[[ -L "$entry" ]] || continue
		if [[ ! -e "$entry" ]]; then
			name="$(basename "$entry")"
			target="$(readlink "$entry")"
			echo "→ broken $name → $target"
			unlink_everywhere "$name"
			n=$((n + 1))
		fi
	done
	echo "  ($n removed)"
}

full_sync() {
	echo "Hub: $HUB_DIR"
	echo

	# Personal first → preserve wins over later sources for the same install name.
	echo "== personal =="
	local src n=0 install_as
	while IFS= read -r src; do
		[[ -z "$src" ]] && continue
		install_as="$(lookup_alias "$PERSONAL_ALIASES" "$(basename "$src")")"
		install_skill "$src" "$install_as" "$REPO_DIR" || true
		install_extra_aliases "$src" "$(basename "$src")" "$REPO_DIR"
		n=$((n + 1))
	done < <(find_personal_skills)
	echo "  ($n considered)"
	echo

	if [[ -d "$MATT_REPO/skills" ]]; then
		sync_tree "mattpocock/skills" "$MATT_REPO" "$MATT_REPO/skills" "$MATT_ALIASES"
	else
		echo "== mattpocock/skills =="
		echo "· skip (set MATT_SKILLS_REPO if needed)"
	fi
	echo

	retire_renames
	echo
	sweep_broken
	echo
	echo "Done. Restart agent sessions to pick up changes."
}

resolve_skill_arg() {
	local arg="$1"
	if [[ -f "$arg/SKILL.md" ]]; then
		[[ "$arg" == /* ]] || arg="$(cd "$arg" && pwd)"
		printf '%s\n' "$arg"
		return 0
	fi
	if [[ -f "$REPO_DIR/$arg/SKILL.md" ]]; then
		printf '%s\n' "$REPO_DIR/$arg"
		return 0
	fi
	return 1
}

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
	usage
fi

if [[ "${1:-}" == "--unlink" ]]; then
	[[ -n "${2:-}" ]] || {
		echo "Usage: $0 --unlink <install-name>" >&2
		exit 1
	}
	unlink_everywhere "$2"
	echo "Done: unlinked $2"
	exit 0
fi

if [[ $# -eq 0 ]]; then
	full_sync
	exit 0
fi

SOURCE_ARG="$1"
REQUESTED_INSTALL_AS="${2:-}"
INSTALL_AS="$REQUESTED_INSTALL_AS"
if ! SOURCE_PATH="$(resolve_skill_arg "$SOURCE_ARG")"; then
	echo "✗ skill not found: $SOURCE_ARG" >&2
	exit 1
fi

SOURCE_ROOT="$REPO_DIR"
case "$SOURCE_PATH" in
	"$MATT_REPO"/*) SOURCE_ROOT="$MATT_REPO" ;;
	"$REPO_DIR"/*) SOURCE_ROOT="$REPO_DIR" ;;
esac

if [[ -z "$INSTALL_AS" ]]; then
	if [[ "$SOURCE_ROOT" == "$REPO_DIR" ]]; then
		INSTALL_AS="$(lookup_alias "$PERSONAL_ALIASES" "$(basename "$SOURCE_PATH")")"
	elif [[ "$SOURCE_ROOT" == "$MATT_REPO" ]]; then
		INSTALL_AS="$(lookup_alias "$MATT_ALIASES" "$(basename "$SOURCE_PATH")")"
	else
		INSTALL_AS="$(basename "$SOURCE_PATH")"
	fi
fi

install_skill "$SOURCE_PATH" "$INSTALL_AS" "$SOURCE_ROOT"
if [[ -z "$REQUESTED_INSTALL_AS" && "$SOURCE_ROOT" == "$REPO_DIR" ]]; then
	install_extra_aliases "$SOURCE_PATH" "$(basename "$SOURCE_PATH")" "$SOURCE_ROOT"
fi
echo "Done."
